import re
from datetime import datetime, timedelta, timezone
from typing import cast, get_args

from sqlalchemy import delete, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, joinedload

from app.core.database import ParentSessionLocal
from app.modules.activity.models import ActivityTimelineEntry
from app.modules.activity.schemas import ActivityActionResponse, ActivitySource, ActivitySourceAppResponse, ActivityType, UniversalActivityItemResponse
from app.modules.apps.models import AppCatalogItem
from app.modules.auth.models import User

ACTIVITY_TYPES = frozenset(get_args(ActivityType))
ACTIVITY_SOURCES = frozenset(get_args(ActivitySource))
RETENTION_LIMIT = 1000
NAVIGATION_COOLDOWN = timedelta(minutes=30)
_control_characters = re.compile(r"[\x00-\x1f\x7f]+")


def _clean_text(value: str | None, limit: int) -> str | None:
    if value is None:
        return None
    cleaned = " ".join(_control_characters.sub(" ", value).split()).strip()
    return cleaned[:limit] or None


def _safe_route(route: str | None, source_slug: str | None) -> str | None:
    if not route or not route.startswith("/") or route.startswith("//") or any(value in route for value in ("\\", "?", "#", "\x00")):
        return None
    segments = [segment for segment in route.split("/") if segment]
    if any(segment in {".", ".."} for segment in segments):
        return None
    platform = {"/", "/about", "/activity", "/apps", "/contact", "/dashboard", "/faq", "/pricing", "/privacy", "/profile", "/settings", "/subscription", "/terms"}
    if route in platform:
        return route
    if source_slug and (route == f"/{source_slug}" or route.startswith(f"/{source_slug}/")):
        return route
    return None


def _approved_app(db: Session, slug: str | None) -> AppCatalogItem | None:
    if not slug:
        return None
    return db.execute(select(AppCatalogItem).where(AppCatalogItem.slug == slug, AppCatalogItem.status == "active", AppCatalogItem.visibility == "public")).scalar_one_or_none()


def record_activity(db: Session, *, user_id: str, activity_type: ActivityType, title: str,
        description: str | None = None, source: ActivitySource = "platform",
        source_app_slug: str | None = None, action_route: str | None = None,
        action_label: str | None = None, entity_type: str | None = None,
        entity_id: str | None = None, deduplication_window: timedelta | None = None) -> ActivityTimelineEntry:
    if activity_type not in ACTIVITY_TYPES: raise ValueError("Unsupported activity type.")
    if source not in ACTIVITY_SOURCES: raise ValueError("Unsupported activity source.")
    if db.get(User, user_id) is None: raise ValueError("Activity owner does not exist.")
    app = _approved_app(db, source_app_slug)
    if source_app_slug and app is None: raise ValueError("Activity source app is not approved.")
    route = _safe_route(action_route, app.slug if app else None)
    if action_route and route is None: raise ValueError("Activity action route is not approved.")
    safe_title = _clean_text(title, 160)
    if not safe_title: raise ValueError("Activity title is required.")
    safe_entity_type = _clean_text(entity_type, 80)
    safe_entity_id = _clean_text(entity_id, 120)
    if deduplication_window:
        existing = db.execute(select(ActivityTimelineEntry).where(
            ActivityTimelineEntry.user_id == user_id,
            ActivityTimelineEntry.activity_type == activity_type,
            ActivityTimelineEntry.source_app_id == (app.id if app else None),
            ActivityTimelineEntry.entity_type == safe_entity_type,
            ActivityTimelineEntry.entity_id == safe_entity_id,
            ActivityTimelineEntry.created_at >= datetime.now(timezone.utc) - deduplication_window,
        ).order_by(ActivityTimelineEntry.created_at.desc()).limit(1)).scalar_one_or_none()
        if existing: return existing
    entry = ActivityTimelineEntry(user_id=user_id, activity_type=activity_type,
        title=safe_title, description=_clean_text(description, 300), source=source,
        source_app_id=app.id if app else None, action_route=route,
        action_label=_clean_text(action_label, 120) if route else None,
        entity_type=safe_entity_type, entity_id=safe_entity_id)
    db.add(entry); db.commit(); db.refresh(entry)
    excess_ids = list(db.execute(select(ActivityTimelineEntry.id).where(
        ActivityTimelineEntry.user_id == user_id).order_by(
        ActivityTimelineEntry.created_at.desc(), ActivityTimelineEntry.id.desc()
    ).offset(RETENTION_LIMIT)).scalars().all())
    if excess_ids:
        db.execute(delete(ActivityTimelineEntry).where(ActivityTimelineEntry.id.in_(excess_ids))); db.commit()
    return entry


def record_activity_safely(**kwargs: object) -> None:
    try:
        with ParentSessionLocal() as db:
            record_activity(db, **kwargs)  # type: ignore[arg-type]
    except (SQLAlchemyError, ValueError, RuntimeError):
        return


def record_app_navigation(db: Session, user: User, app_slug: str) -> ActivityTimelineEntry:
    app = _approved_app(db, app_slug)
    if app is None: raise ValueError("Activity source app is not approved.")
    return record_activity(db, user_id=user.id, activity_type="navigation",
        title=f"Opened {app.name}", source="app", source_app_slug=app.slug,
        action_route=f"/{app.slug}", action_label=f"Open {app.name}",
        entity_type="app", entity_id=app.id, deduplication_window=NAVIGATION_COOLDOWN)


def serialize_activity(entry: ActivityTimelineEntry) -> UniversalActivityItemResponse:
    app = entry.source_app
    action = None
    route = _safe_route(entry.action_route, app.slug if app else None)
    if route and entry.action_label:
        action = ActivityActionResponse(label=entry.action_label, route=route)
    return UniversalActivityItemResponse(id=entry.id, type=cast(ActivityType, entry.activity_type),
        title=entry.title, description=entry.description, source=cast(ActivitySource, entry.source),
        created_at=entry.created_at,
        source_app=ActivitySourceAppResponse(slug=app.slug, name=app.name) if app else None,
        action=action)


def list_activity(db: Session, user: User, *, page: int, page_size: int,
        activity_type: ActivityType | None = None, app_slug: str | None = None
        ) -> tuple[list[ActivityTimelineEntry], int]:
    conditions = [ActivityTimelineEntry.user_id == user.id]
    if activity_type: conditions.append(ActivityTimelineEntry.activity_type == activity_type)
    if app_slug:
        app = _approved_app(db, app_slug)
        if app is None: return [], 0
        conditions.append(ActivityTimelineEntry.source_app_id == app.id)
    total = int(db.execute(select(func.count(ActivityTimelineEntry.id)).where(*conditions)).scalar_one())
    items = list(db.execute(select(ActivityTimelineEntry).options(joinedload(ActivityTimelineEntry.source_app))
        .where(*conditions).order_by(ActivityTimelineEntry.created_at.desc(), ActivityTimelineEntry.id.desc())
        .offset((page - 1) * page_size).limit(page_size)).scalars().all())
    return items, total
