import json
from typing import Any

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session, joinedload

from app.modules.auth.models import User
from app.modules.apps.models import AppCatalogItem, Category
from app.modules.dashboard.models import Dashboard
from app.modules.dashboard.schemas import PlatformDashboardSummaryResponse
from app.modules.favorites.models import Favorite
from app.modules.notifications.models import Notification


def parse_summary_json(value: str | None) -> dict[str, Any]:
    if not value:
        return {}

    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        return {}

    if not isinstance(parsed, dict):
        return {}

    return parsed


def count_user_favorites(db: Session, user: User) -> int:
    statement = select(func.count(Favorite.id)).where(Favorite.user_id == user.id)

    return int(db.execute(statement).scalar_one())


def count_unread_notifications(db: Session, user: User) -> int:
    statement = select(func.count(Notification.id)).where(
        Notification.user_id == user.id,
        Notification.is_read.is_(False),
    )

    return int(db.execute(statement).scalar_one())


def list_user_dashboard_items(db: Session, user: User) -> list[Dashboard]:
    statement = (
        select(Dashboard)
        .options(joinedload(Dashboard.app))
        .where(Dashboard.user_id == user.id)
        .order_by(
            Dashboard.last_activity_at.desc().nullslast(),
            Dashboard.updated_at.desc(),
        )
    )

    return list(db.execute(statement).scalars().all())


def get_platform_dashboard_summary(db: Session) -> PlatformDashboardSummaryResponse:
    active_apps_statement = select(
        func.count(AppCatalogItem.id).label("total_apps"),
        func.sum(
            case((AppCatalogItem.launch_status == "live", 1), else_=0),
        ).label("live_apps"),
        func.sum(
            case((AppCatalogItem.launch_status == "comingSoon", 1), else_=0),
        ).label("coming_soon_apps"),
    ).where(AppCatalogItem.status == "active")
    active_apps_row = db.execute(active_apps_statement).one()

    total_apps = int(active_apps_row.total_apps or 0)
    live_apps = int(active_apps_row.live_apps or 0)
    coming_soon_apps = int(active_apps_row.coming_soon_apps or 0)

    categories_statement = select(func.count(Category.id)).where(
        Category.status == "active",
    )
    categories = int(db.execute(categories_statement).scalar_one())
    progress_percent = round((live_apps / total_apps) * 100) if total_apps else 0

    return PlatformDashboardSummaryResponse(
        total_apps=total_apps,
        live_apps=live_apps,
        coming_soon_apps=coming_soon_apps,
        categories=categories,
        progress_percent=progress_percent,
    )
