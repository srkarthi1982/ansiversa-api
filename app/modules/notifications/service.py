from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.notifications.models import Notification


def list_user_notifications(
    db: Session,
    user: User,
    limit: int = 50,
) -> list[Notification]:
    statement = (
        select(Notification)
        .where(Notification.user_id == user.id)
        .order_by(Notification.created_at.desc())
        .limit(limit)
    )

    return list(db.execute(statement).scalars().all())


def get_unread_count(db: Session, user: User) -> int:
    statement = select(func.count(Notification.id)).where(
        Notification.user_id == user.id,
        Notification.is_read.is_(False),
    )

    return int(db.execute(statement).scalar_one())


def mark_notification_read(
    db: Session,
    user: User,
    notification_id: str,
) -> Notification:
    notification = db.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == user.id,
        )
    ).scalar_one_or_none()

    if notification is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found.",
        )

    if not notification.is_read:
        notification.is_read = True
        notification.read_at = datetime.now(timezone.utc)
        db.add(notification)
        db.commit()
        db.refresh(notification)

    return notification


def mark_all_notifications_read(db: Session, user: User) -> int:
    now = datetime.now(timezone.utc)
    statement = (
        update(Notification)
        .where(Notification.user_id == user.id, Notification.is_read.is_(False))
        .values(is_read=True, read_at=now)
    )

    result = db.execute(statement)
    db.commit()

    return int(result.rowcount or 0)
