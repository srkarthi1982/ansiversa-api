from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class NotificationResponse(BaseModel):
    id: str
    title: str
    message: str | None
    type: str
    is_read: bool = Field(serialization_alias="isRead")
    created_at: datetime = Field(serialization_alias="createdAt")
    read_at: datetime | None = Field(default=None, serialization_alias="readAt")
    metadata_json: str | None = Field(default=None, serialization_alias="metadataJson")

    model_config = ConfigDict(from_attributes=True)


class NotificationListResponse(BaseModel):
    items: list[NotificationResponse]
    total: int


class UnreadCountResponse(BaseModel):
    count: int


class MarkReadResponse(BaseModel):
    ok: bool
    notification: NotificationResponse


class MarkAllReadResponse(BaseModel):
    ok: bool
    updated: int
