from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.modules.auth.schemas import UserResponse


class DashboardAppResponse(BaseModel):
    id: str
    key: str
    slug: str
    name: str
    description: str
    status: str
    launch_status: str = Field(serialization_alias="launchStatus")
    visibility: str
    pricing_gate: str = Field(serialization_alias="pricingGate")
    website_url: str | None = Field(default=None, serialization_alias="websiteUrl")
    logo_key: str | None = Field(default=None, serialization_alias="logoKey")

    model_config = ConfigDict(from_attributes=True)


class RecentAppResponse(BaseModel):
    app: DashboardAppResponse
    last_activity_at: datetime | None = Field(
        default=None,
        serialization_alias="lastActivityAt",
    )


class DashboardItemResponse(BaseModel):
    id: str
    app: DashboardAppResponse
    last_activity_at: datetime | None = Field(
        default=None,
        serialization_alias="lastActivityAt",
    )
    summary_version: int = Field(serialization_alias="summaryVersion")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")
    summary: dict[str, Any]


class DashboardSummaryResponse(BaseModel):
    user: UserResponse
    favorites_count: int = Field(serialization_alias="favoritesCount")
    unread_notifications_count: int = Field(
        serialization_alias="unreadNotificationsCount",
    )
    recent_apps: list[RecentAppResponse] = Field(serialization_alias="recentApps")
    dashboard_items: list[DashboardItemResponse] = Field(
        serialization_alias="dashboardItems",
    )
