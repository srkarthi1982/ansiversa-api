from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

ActivityType = Literal["navigation", "created", "updated", "completed", "deleted", "archived", "restored", "favorited", "unfavorited", "notification", "assistant", "account", "system"]
ActivitySource = Literal["platform", "app", "assistant", "notification", "account"]


class ActivitySourceAppResponse(BaseModel):
    slug: str
    name: str


class ActivityActionResponse(BaseModel):
    label: str
    route: str


class UniversalActivityItemResponse(BaseModel):
    id: str
    type: ActivityType
    title: str
    description: str | None
    source: ActivitySource
    created_at: datetime = Field(serialization_alias="createdAt")
    source_app: ActivitySourceAppResponse | None = Field(default=None, serialization_alias="sourceApp")
    action: ActivityActionResponse | None = None


class UniversalActivityListResponse(BaseModel):
    items: list[UniversalActivityItemResponse]
    page: int
    page_size: int = Field(serialization_alias="pageSize")
    total: int


class UniversalActivitySummaryResponse(BaseModel):
    items: list[UniversalActivityItemResponse]


class AppNavigationActivityRequest(BaseModel):
    app_slug: str = Field(validation_alias="appSlug", min_length=1, max_length=120)
    model_config = ConfigDict(populate_by_name=True)


class PlatformActivityRequest(BaseModel):
    event: Literal["assistant_used", "notification_action_opened"]
