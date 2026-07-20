import json
from datetime import datetime, timezone
from typing import Any, cast, get_args

from fastapi import HTTPException, status
from pydantic import TypeAdapter, ValidationError
from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.modules.apps.models import AppCatalogItem
from app.modules.auth.models import User, UserPreference
from app.modules.notifications.models import Notification
from app.modules.notifications.schemas import (
    NotificationActionResponse,
    NotificationPreferencesUpdateRequest,
    NotificationResponse,
    NotificationSourceAppResponse,
    NotificationType,
)

NOTIFICATION_TYPES = frozenset(get_args(NotificationType))
_type_adapter = TypeAdapter(NotificationType)


def _validate_type(value: str) -> NotificationType:
    try:
        return _type_adapter.validate_python(value)
    except ValidationError as exc:
        raise ValueError("Unsupported notification type.") from exc


def _normalize_internal_route(route: str | None, source_slug: str | None) -> str | None:
    if not route or not route.startswith("/") or route.startswith("//"):
        return None
    if any(character in route for character in ("\\", "\x00", "?", "#")):
        return None
    segments = [segment for segment in route.split("/") if segment]
    if any(segment in {".", ".."} for segment in segments):
        return None
    platform_routes = {
        "/", "/about", "/apps", "/contact", "/dashboard", "/faq", "/pricing",
        "/privacy", "/profile", "/settings", "/subscription", "/terms",
    }
    if route in platform_routes:
        return route
    if source_slug and (route == f"/{source_slug}" or route.startswith(f"/{source_slug}/")):
        return route
    return None


def _metadata(notification: Notification) -> dict[str, Any]:
    if not notification.metadata_json:
        return {}
    try:
        value = json.loads(notification.metadata_json)
    except (TypeError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def serialize_notification(db: Session, notification: Notification) -> NotificationResponse:
    metadata = _metadata(notification)
    source_slug = metadata.get("sourceAppSlug")
    source = None
    if isinstance(source_slug, str):
        app = db.execute(
            select(AppCatalogItem).where(
                AppCatalogItem.slug == source_slug,
                AppCatalogItem.status == "active",
                AppCatalogItem.visibility == "public",
            )
        ).scalar_one_or_none()
        if app:
            source = NotificationSourceAppResponse(slug=app.slug, name=app.name)

    action = None
    route = _normalize_internal_route(metadata.get("actionRoute"), source.slug if source else None)
    label = metadata.get("actionLabel")
    if route and isinstance(label, str) and label.strip():
        action = NotificationActionResponse(label=label.strip()[:120], route=route)

    notification_type = notification.type if notification.type in NOTIFICATION_TYPES else "info"
    return NotificationResponse(
        id=notification.id,
        title=notification.title,
        message=notification.message,
        type=cast(NotificationType, notification_type),
        is_read=notification.is_read,
        created_at=notification.created_at,
        read_at=notification.read_at,
        source_app=source,
        action=action,
    )


def list_user_notifications(db: Session, user: User, *, page: int, page_size: int,
                            unread_only: bool, notification_type: NotificationType | None
                            ) -> tuple[list[Notification], int, int]:
    conditions = [Notification.user_id == user.id]
    if unread_only:
        conditions.append(Notification.is_read.is_(False))
    if notification_type:
        conditions.append(Notification.type == notification_type)
    total = int(db.execute(select(func.count(Notification.id)).where(*conditions)).scalar_one())
    items = list(db.execute(
        select(Notification).where(*conditions)
        .order_by(Notification.created_at.desc(), Notification.id.desc())
        .offset((page - 1) * page_size).limit(page_size)
    ).scalars().all())
    return items, total, get_unread_count(db, user)


def get_unread_count(db: Session, user: User) -> int:
    return int(db.execute(select(func.count(Notification.id)).where(
        Notification.user_id == user.id, Notification.is_read.is_(False)
    )).scalar_one())


def mark_notification_read(db: Session, user: User, notification_id: str) -> Notification:
    notification = db.execute(select(Notification).where(
        Notification.id == notification_id, Notification.user_id == user.id
    )).scalar_one_or_none()
    if notification is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found.")
    if not notification.is_read:
        notification.is_read = True
        notification.read_at = datetime.now(timezone.utc)
        db.add(notification); db.commit(); db.refresh(notification)
    return notification


def mark_all_notifications_read(db: Session, user: User) -> int:
    result = db.execute(update(Notification).where(
        Notification.user_id == user.id, Notification.is_read.is_(False)
    ).values(is_read=True, read_at=datetime.now(timezone.utc)))
    db.commit()
    return int(result.rowcount or 0)


def get_notification_preferences(db: Session, user: User) -> UserPreference:
    preferences = db.get(UserPreference, user.id)
    if preferences is None:
        preferences = UserPreference(user_id=user.id)
        db.add(preferences); db.commit(); db.refresh(preferences)
    return preferences


def update_notification_preferences(db: Session, user: User,
        payload: NotificationPreferencesUpdateRequest) -> UserPreference:
    preferences = get_notification_preferences(db, user)
    preferences.notifications_enabled = payload.notifications_enabled
    preferences.reminder_notifications_enabled = payload.reminder_notifications_enabled
    preferences.system_notifications_enabled = payload.system_notifications_enabled
    preferences.updated_at = datetime.now(timezone.utc)
    db.commit(); db.refresh(preferences)
    return preferences


def create_notification(db: Session, *, user_id: str, type: NotificationType, title: str,
                        message: str | None = None, source_app_slug: str | None = None,
                        action_route: str | None = None, action_label: str | None = None,
                        metadata: dict[str, Any] | None = None) -> Notification:
    _validate_type(type)
    if db.get(User, user_id) is None:
        raise ValueError("Notification owner does not exist.")
    source = None
    if source_app_slug:
        source = db.execute(select(AppCatalogItem).where(
            AppCatalogItem.slug == source_app_slug,
            AppCatalogItem.status == "active",
            AppCatalogItem.visibility == "public",
        )).scalar_one_or_none()
        if source is None:
            raise ValueError("Notification source app is not approved.")
    safe_route = _normalize_internal_route(action_route, source.slug if source else None)
    if action_route and safe_route is None:
        raise ValueError("Notification action route is not approved.")
    safe_metadata = {key: value for key, value in (metadata or {}).items()
                     if key not in {"sourceAppSlug", "actionRoute", "actionLabel"}}
    if source: safe_metadata["sourceAppSlug"] = source.slug
    if safe_route:
        safe_metadata["actionRoute"] = safe_route
        safe_metadata["actionLabel"] = (action_label or "Open").strip()[:120]
    notification = Notification(user_id=user_id, type=type, title=title.strip()[:255],
        message=message, metadata_json=json.dumps(safe_metadata, separators=(",", ":")))
    db.add(notification); db.commit(); db.refresh(notification)
    return notification
