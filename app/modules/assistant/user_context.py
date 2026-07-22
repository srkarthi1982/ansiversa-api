from __future__ import annotations

import logging
import re
from collections import Counter
from dataclasses import dataclass, field
from time import perf_counter
from typing import Literal

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.modules.activity.service import list_activity
from app.modules.apps.models import AppCatalogItem
from app.modules.assistant.schemas import AssistantClientContext
from app.modules.auth.models import User, UserPreference
from app.modules.favorites.service import list_user_favorites
from app.modules.notifications.service import list_user_notifications


LOGGER = logging.getLogger(__name__)

PlatformUserContextProfile = Literal["minimal", "personalization", "attention", "tool_execution"]
MAX_CONTEXT_APPS = 5
MAX_RECENT_INPUT = 10
MAX_ACTIVITY_ITEMS = 10
MAX_NOTIFICATION_ITEMS = 20
_UNSAFE_ROUTE_CHARS = re.compile(r"[\\\x00?#]")


@dataclass(frozen=True)
class UserContextApp:
    slug: str
    name: str
    route: str
    category: str | None = None
    source: Literal["backend", "frontend_validated"] = "backend"


@dataclass(frozen=True)
class UserActivityContext:
    recent_activity_count: int
    last_activity_at: str | None = None
    recent_apps: tuple[str, ...] = ()
    recent_activity_types: tuple[str, ...] = ()


@dataclass(frozen=True)
class UserNotificationContext:
    unread_count: int
    has_unread: bool
    types: dict[str, int] = field(default_factory=dict)


@dataclass(frozen=True)
class AssistantPreferenceContext:
    notifications_enabled: bool | None = None
    reminder_notifications_enabled: bool | None = None
    system_notifications_enabled: bool | None = None
    contextual_assistance_enabled: bool | None = None
    user_data_assistance_enabled: bool | None = None


@dataclass(frozen=True)
class PlatformUserContext:
    profile: PlatformUserContextProfile
    is_authenticated: bool
    user_reference: str | None = None
    current_route: str | None = None
    current_app_slug: str | None = None
    favorite_apps: tuple[UserContextApp, ...] = ()
    recent_apps: tuple[UserContextApp, ...] = ()
    activity_summary: UserActivityContext | None = None
    notification_summary: UserNotificationContext | None = None
    assistant_preferences: AssistantPreferenceContext | None = None
    backend_owned_sources: tuple[str, ...] = ()
    frontend_validated_sources: tuple[str, ...] = ()
    unavailable_sources: tuple[str, ...] = ()

    def to_openai_context(self) -> dict[str, object]:
        context: dict[str, object] = {
            "isAuthenticated": self.is_authenticated,
        }
        if self.current_route:
            context["currentRoute"] = self.current_route
        if self.current_app_slug:
            context["currentAppSlug"] = self.current_app_slug
        if self.favorite_apps:
            context["favoriteApps"] = [app.name for app in self.favorite_apps]
        if self.recent_apps:
            context["recentApps"] = [app.name for app in self.recent_apps]
        if self.activity_summary:
            context["activitySummary"] = {
                "recentActivityCount": self.activity_summary.recent_activity_count,
                "lastActivityAt": self.activity_summary.last_activity_at,
                "recentApps": list(self.activity_summary.recent_apps),
                "recentActivityTypes": list(self.activity_summary.recent_activity_types),
            }
        if self.notification_summary:
            context["notificationSummary"] = {
                "unreadCount": self.notification_summary.unread_count,
                "hasUnread": self.notification_summary.has_unread,
                "types": self.notification_summary.types,
            }
        if self.assistant_preferences:
            context["assistantPreferences"] = {
                "notificationsEnabled": self.assistant_preferences.notifications_enabled,
                "reminderNotificationsEnabled": self.assistant_preferences.reminder_notifications_enabled,
                "systemNotificationsEnabled": self.assistant_preferences.system_notifications_enabled,
                "contextualAssistanceEnabled": self.assistant_preferences.contextual_assistance_enabled,
                "userDataAssistanceEnabled": self.assistant_preferences.user_data_assistance_enabled,
            }
        return context


def build_platform_user_context(
    db: Session,
    *,
    user: User | None,
    client_context: AssistantClientContext | None,
    allowed_routes: frozenset[str],
    profile: PlatformUserContextProfile,
) -> PlatformUserContext:
    start = perf_counter()
    unavailable_sources: list[str] = []
    backend_sources: list[str] = []
    frontend_sources: list[str] = []
    current_route = _validated_current_route(client_context.current_route if client_context else None, allowed_routes)
    current_app_slug = _resolve_current_app_slug(db, current_route)

    favorite_apps: tuple[UserContextApp, ...] = ()
    recent_apps: tuple[UserContextApp, ...] = ()
    activity_summary: UserActivityContext | None = None
    notification_summary: UserNotificationContext | None = None
    assistant_preferences: AssistantPreferenceContext | None = None

    if user and profile in {"personalization", "attention"}:
        try:
            favorite_apps = _favorite_apps(db, user, allowed_routes)
            backend_sources.append("favorites")
        except Exception:
            LOGGER.exception("Astra user context favorites source unavailable.")
            unavailable_sources.append("favorites")

    if profile in {"personalization", "attention"}:
        try:
            recent_apps = _recent_apps(db, client_context, allowed_routes)
            if recent_apps:
                frontend_sources.append("recent_apps")
        except Exception:
            LOGGER.exception("Astra user context recent-app source unavailable.")
            unavailable_sources.append("recent_apps")

    if user and profile in {"personalization", "attention"}:
        try:
            activity_summary = _activity_summary(db, user)
            backend_sources.append("activity")
        except Exception:
            LOGGER.exception("Astra user context activity source unavailable.")
            unavailable_sources.append("activity")

    if user and profile == "attention":
        try:
            notification_summary = _notification_summary(db, user)
            assistant_preferences = _assistant_preferences(db, user)
            backend_sources.extend(("notifications", "preferences"))
        except Exception:
            LOGGER.exception("Astra user context notification source unavailable.")
            unavailable_sources.append("notifications")

    if user and profile == "tool_execution":
        backend_sources.append("authenticated_user")

    LOGGER.info(
        "Astra user context metadata: %s",
        {
            "profile": profile,
            "authenticated": bool(user),
            "backendSources": backend_sources,
            "frontendValidatedSources": frontend_sources,
            "unavailableSources": unavailable_sources,
            "favoriteCount": len(favorite_apps),
            "recentAppCount": len(recent_apps),
            "hasActivitySummary": activity_summary is not None,
            "hasNotificationSummary": notification_summary is not None,
            "durationMs": int((perf_counter() - start) * 1000),
        },
    )
    return PlatformUserContext(
        profile=profile,
        is_authenticated=user is not None,
        user_reference=user.id if user and profile == "tool_execution" else None,
        current_route=current_route,
        current_app_slug=current_app_slug,
        favorite_apps=favorite_apps,
        recent_apps=recent_apps,
        activity_summary=activity_summary,
        notification_summary=notification_summary,
        assistant_preferences=assistant_preferences,
        backend_owned_sources=tuple(backend_sources),
        frontend_validated_sources=tuple(frontend_sources),
        unavailable_sources=tuple(unavailable_sources),
    )


def _validated_current_route(route: str | None, allowed_routes: frozenset[str]) -> str | None:
    if not route or not route.startswith("/") or route.startswith("//"):
        return None
    if _UNSAFE_ROUTE_CHARS.search(route):
        return None
    segments = [segment for segment in route.split("/") if segment]
    if any(segment in {".", ".."} for segment in segments):
        return None
    if route in allowed_routes:
        return route
    slug = segments[0] if segments else ""
    if f"/{slug}" in allowed_routes:
        return route
    if any(allowed_route.startswith(f"/{slug}/") for allowed_route in allowed_routes):
        return route
    return None


def _resolve_current_app_slug(db: Session, route: str | None) -> str | None:
    if not route:
        return None
    segments = [segment for segment in route.split("/") if segment]
    if not segments:
        return None
    app = _catalog_app_by_slug(db, segments[0])
    return app.slug if app else None


def _favorite_apps(db: Session, user: User, allowed_routes: frozenset[str]) -> tuple[UserContextApp, ...]:
    apps: list[UserContextApp] = []
    for favorite in list_user_favorites(db, user)[:MAX_CONTEXT_APPS]:
        app = favorite.app
        if not _is_visible_app(app):
            continue
        apps.append(_context_app(app, allowed_routes, source="backend"))
    return tuple(apps[:MAX_CONTEXT_APPS])


def _recent_apps(
    db: Session,
    client_context: AssistantClientContext | None,
    allowed_routes: frozenset[str],
) -> tuple[UserContextApp, ...]:
    if client_context is None:
        return ()
    slugs: list[str] = []
    for raw_slug in client_context.recent_app_keys[:MAX_RECENT_INPUT]:
        slug = _normalize_slug(raw_slug)
        if slug and slug not in slugs:
            slugs.append(slug)
        if len(slugs) == MAX_CONTEXT_APPS:
            break
    if not slugs:
        return ()
    apps_by_slug = {
        app.slug: app
        for app in db.execute(
            select(AppCatalogItem)
            .options(joinedload(AppCatalogItem.category))
            .where(
                AppCatalogItem.slug.in_(slugs),
                AppCatalogItem.status == "active",
                AppCatalogItem.visibility == "public",
            )
        )
        .scalars()
        .all()
    }
    return tuple(
        _context_app(apps_by_slug[slug], allowed_routes, source="frontend_validated")
        for slug in slugs
        if slug in apps_by_slug
    )


def _activity_summary(db: Session, user: User) -> UserActivityContext:
    items, total = list_activity(db, user, page=1, page_size=MAX_ACTIVITY_ITEMS)
    recent_app_slugs: list[str] = []
    recent_types: list[str] = []
    for item in items:
        if item.source_app and item.source_app.slug not in recent_app_slugs:
            recent_app_slugs.append(item.source_app.slug)
        if item.activity_type not in recent_types:
            recent_types.append(item.activity_type)
    last_activity_at = items[0].created_at.isoformat() if items else None
    return UserActivityContext(
        recent_activity_count=min(total, MAX_ACTIVITY_ITEMS),
        last_activity_at=last_activity_at,
        recent_apps=tuple(recent_app_slugs[:MAX_CONTEXT_APPS]),
        recent_activity_types=tuple(recent_types[:MAX_CONTEXT_APPS]),
    )


def _notification_summary(db: Session, user: User) -> UserNotificationContext:
    items, _, unread_count = list_user_notifications(
        db,
        user,
        page=1,
        page_size=MAX_NOTIFICATION_ITEMS,
        unread_only=True,
        notification_type=None,
    )
    type_counts = Counter(str(item.type) for item in items if not item.is_read)
    return UserNotificationContext(
        unread_count=unread_count,
        has_unread=unread_count > 0,
        types=dict(sorted(type_counts.items())),
    )


def _assistant_preferences(db: Session, user: User) -> AssistantPreferenceContext:
    preferences = db.get(UserPreference, user.id)
    if preferences is None:
        return AssistantPreferenceContext(
            contextual_assistance_enabled=None,
            user_data_assistance_enabled=None,
        )
    return AssistantPreferenceContext(
        notifications_enabled=preferences.notifications_enabled,
        reminder_notifications_enabled=preferences.reminder_notifications_enabled,
        system_notifications_enabled=preferences.system_notifications_enabled,
        contextual_assistance_enabled=None,
        user_data_assistance_enabled=None,
    )


def _catalog_app_by_slug(db: Session, slug: str) -> AppCatalogItem | None:
    return db.execute(
        select(AppCatalogItem)
        .options(joinedload(AppCatalogItem.category))
        .where(
            AppCatalogItem.slug == slug,
            AppCatalogItem.status == "active",
            AppCatalogItem.visibility == "public",
        )
    ).scalar_one_or_none()


def _context_app(
    app: AppCatalogItem,
    allowed_routes: frozenset[str],
    *,
    source: Literal["backend", "frontend_validated"],
) -> UserContextApp:
    route = _approved_app_route(app.slug, allowed_routes)
    return UserContextApp(
        slug=app.slug,
        name=app.name,
        route=route,
        category=app.category.name if app.category else None,
        source=source,
    )


def _approved_app_route(slug: str, allowed_routes: frozenset[str]) -> str:
    direct_route = f"/{slug}"
    if direct_route in allowed_routes:
        return direct_route
    prefix = f"/{slug}/"
    for route in sorted(allowed_routes):
        if route.startswith(prefix):
            return route
    return direct_route


def _normalize_slug(value: str | None) -> str | None:
    if not value:
        return None
    slug = value.strip().lower()
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{1,118}[a-z0-9]", slug):
        return None
    return slug


def _is_visible_app(app: AppCatalogItem | None) -> bool:
    return bool(
        app
        and app.visibility == "public"
        and app.status == "active"
        and app.launch_status == "live"
    )
