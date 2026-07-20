from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

NotificationType = Literal[
    "info", "reminder", "due_soon", "overdue", "success", "warning", "system"
]


class NotificationSourceAppResponse(BaseModel):
    slug: str
    name: str


class NotificationActionResponse(BaseModel):
    label: str
    route: str


class NotificationResponse(BaseModel):
    id: str
    title: str
    message: str | None
    type: NotificationType
    is_read: bool = Field(serialization_alias="isRead")
    created_at: datetime = Field(serialization_alias="createdAt")
    read_at: datetime | None = Field(default=None, serialization_alias="readAt")
    source_app: NotificationSourceAppResponse | None = Field(
        default=None, serialization_alias="sourceApp"
    )
    action: NotificationActionResponse | None = None

    model_config = ConfigDict(from_attributes=True)


class NotificationListResponse(BaseModel):
    items: list[NotificationResponse]
    total: int
    unread_count: int = Field(serialization_alias="unreadCount")
    page: int
    page_size: int = Field(serialization_alias="pageSize")


class UnreadCountResponse(BaseModel):
    count: int


class MarkReadResponse(BaseModel):
    ok: bool
    notification: NotificationResponse


class MarkAllReadResponse(BaseModel):
    ok: bool
    updated: int


class NotificationPreferencesResponse(BaseModel):
    notifications_enabled: bool = Field(serialization_alias="notificationsEnabled")
    reminder_notifications_enabled: bool = Field(
        serialization_alias="reminderNotificationsEnabled"
    )
    system_notifications_enabled: bool = Field(
        serialization_alias="systemNotificationsEnabled"
    )

    model_config = ConfigDict(from_attributes=True)


class NotificationPreferencesUpdateRequest(BaseModel):
    notifications_enabled: bool = Field(validation_alias="notificationsEnabled")
    reminder_notifications_enabled: bool = Field(
        validation_alias="reminderNotificationsEnabled"
    )
    system_notifications_enabled: bool = Field(
        validation_alias="systemNotificationsEnabled"
    )

    model_config = ConfigDict(populate_by_name=True)
