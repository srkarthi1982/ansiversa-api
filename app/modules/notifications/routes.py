from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_parent_db
from app.modules.auth.models import User
from app.modules.auth.service import get_current_user
from app.modules.notifications.schemas import (
    MarkAllReadResponse,
    MarkReadResponse,
    NotificationListResponse,
    NotificationResponse,
    UnreadCountResponse,
)
from app.modules.notifications.service import (
    get_unread_count,
    list_user_notifications,
    mark_all_notifications_read,
    mark_notification_read,
)

router = APIRouter()


@router.get("/notifications", response_model=NotificationListResponse)
def list_notifications(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_parent_db)],
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> NotificationListResponse:
    notifications = list_user_notifications(db, current_user, limit=limit)

    return NotificationListResponse(
        items=[
            NotificationResponse.model_validate(notification)
            for notification in notifications
        ],
        total=len(notifications),
    )


@router.get("/notifications/unread-count", response_model=UnreadCountResponse)
def read_unread_count(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_parent_db)],
) -> UnreadCountResponse:
    return UnreadCountResponse(count=get_unread_count(db, current_user))


@router.patch("/notifications/{notification_id}", response_model=MarkReadResponse)
def mark_read(
    notification_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_parent_db)],
) -> MarkReadResponse:
    notification = mark_notification_read(db, current_user, notification_id)

    return MarkReadResponse(
        ok=True,
        notification=NotificationResponse.model_validate(notification),
    )


@router.post("/notifications/mark-all-read", response_model=MarkAllReadResponse)
def mark_all_read(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_parent_db)],
) -> MarkAllReadResponse:
    updated = mark_all_notifications_read(db, current_user)

    return MarkAllReadResponse(ok=True, updated=updated)
