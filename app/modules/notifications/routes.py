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
    NotificationPreferencesResponse,
    NotificationPreferencesUpdateRequest,
    NotificationType,
    UnreadCountResponse,
)
from app.modules.notifications.service import (
    get_notification_preferences,
    get_unread_count,
    list_user_notifications,
    mark_all_notifications_read,
    mark_notification_read,
    serialize_notification,
    update_notification_preferences,
)

router = APIRouter()


@router.get("/notifications", response_model=NotificationListResponse)
def list_notifications(current_user: Annotated[User, Depends(get_current_user)],
        db: Annotated[Session, Depends(get_parent_db)],
        page: Annotated[int, Query(ge=1)] = 1,
        page_size: Annotated[int, Query(alias="pageSize", ge=1, le=100)] = 20,
        unread_only: Annotated[bool, Query(alias="unreadOnly")] = False,
        type: NotificationType | None = None) -> NotificationListResponse:
    items, total, unread_count = list_user_notifications(db, current_user, page=page,
        page_size=page_size, unread_only=unread_only, notification_type=type)
    return NotificationListResponse(items=[serialize_notification(db, item) for item in items],
        total=total, unread_count=unread_count, page=page, page_size=page_size)


@router.get("/notifications/unread-count", response_model=UnreadCountResponse)
def read_unread_count(current_user: Annotated[User, Depends(get_current_user)],
        db: Annotated[Session, Depends(get_parent_db)]) -> UnreadCountResponse:
    return UnreadCountResponse(count=get_unread_count(db, current_user))


@router.patch("/notifications/{notification_id}/read", response_model=MarkReadResponse)
def mark_read(notification_id: str, current_user: Annotated[User, Depends(get_current_user)],
        db: Annotated[Session, Depends(get_parent_db)]) -> MarkReadResponse:
    notification = mark_notification_read(db, current_user, notification_id)
    return MarkReadResponse(ok=True, notification=serialize_notification(db, notification))


@router.patch("/notifications/read-all", response_model=MarkAllReadResponse)
def mark_all_read(current_user: Annotated[User, Depends(get_current_user)],
        db: Annotated[Session, Depends(get_parent_db)]) -> MarkAllReadResponse:
    return MarkAllReadResponse(ok=True, updated=mark_all_notifications_read(db, current_user))


@router.get("/notifications/preferences", response_model=NotificationPreferencesResponse)
def read_preferences(current_user: Annotated[User, Depends(get_current_user)],
        db: Annotated[Session, Depends(get_parent_db)]) -> NotificationPreferencesResponse:
    return NotificationPreferencesResponse.model_validate(get_notification_preferences(db, current_user))


@router.patch("/notifications/preferences", response_model=NotificationPreferencesResponse)
def patch_preferences(payload: NotificationPreferencesUpdateRequest,
        current_user: Annotated[User, Depends(get_current_user)],
        db: Annotated[Session, Depends(get_parent_db)]) -> NotificationPreferencesResponse:
    return NotificationPreferencesResponse.model_validate(
        update_notification_preferences(db, current_user, payload))
