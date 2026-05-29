import json
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.modules.auth.models import User
from app.modules.dashboard.models import Dashboard
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
