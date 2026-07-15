from datetime import date, datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator

GuideSort = Literal["display", "title", "category", "reviewed", "viewed"]


def _normalize_text(value: object) -> object:
    if isinstance(value, str):
        normalized = " ".join(value.strip().split())
        return normalized or None
    return value


class CategoryCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=3000)
    sort_order: int = Field(default=0, alias="sortOrder", ge=0, le=999)
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("name", "description", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class CategoryUpdateRequest(CategoryCreateRequest):
    pass


class GuideCreateRequest(BaseModel):
    category_id: str = Field(alias="categoryId", min_length=1, max_length=36)
    title: str = Field(min_length=1, max_length=180)
    summary: str = Field(min_length=1, max_length=1000)
    overview: str = Field(min_length=1, max_length=5000)
    first_aid_steps: str = Field(alias="firstAidSteps", min_length=1, max_length=8000)
    avoid_actions: str = Field(alias="avoidActions", min_length=1, max_length=5000)
    emergency_warning: str = Field(alias="emergencyWarning", min_length=1, max_length=5000)
    prevention: str | None = Field(default=None, max_length=5000)
    related_topics: str | None = Field(default=None, alias="relatedTopics", max_length=3000)
    display_order: int = Field(default=0, alias="displayOrder", ge=0, le=999)
    last_reviewed: date | None = Field(default=None, alias="lastReviewed")
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("title", "summary", "overview", "first_aid_steps", "avoid_actions", "emergency_warning", "prevention", "related_topics", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class GuideUpdateRequest(GuideCreateRequest):
    pass


class CategoryResponse(BaseModel):
    id: str
    name: str
    description: str | None
    sort_order: int = Field(serialization_alias="sortOrder")
    is_system: bool = Field(serialization_alias="isSystem")
    guide_count: int = Field(serialization_alias="guideCount")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class GuideSummaryResponse(BaseModel):
    id: str
    category_id: str = Field(serialization_alias="categoryId")
    category_name: str = Field(serialization_alias="categoryName")
    title: str
    summary: str
    emergency_warning: str = Field(serialization_alias="emergencyWarning")
    display_order: int = Field(serialization_alias="displayOrder")
    last_reviewed: date | None = Field(serialization_alias="lastReviewed")
    is_bookmarked: bool = Field(serialization_alias="isBookmarked")
    view_count: int = Field(serialization_alias="viewCount")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class GuideDetailResponse(GuideSummaryResponse):
    overview: str
    first_aid_steps: str = Field(serialization_alias="firstAidSteps")
    avoid_actions: str = Field(serialization_alias="avoidActions")
    prevention: str | None
    related_topics: str | None = Field(serialization_alias="relatedTopics")


class GuideListResponse(BaseModel):
    items: list[GuideSummaryResponse]
    total: int
    page: int
    page_size: int = Field(serialization_alias="pageSize")


class CountItem(BaseModel):
    label: str
    count: int


class DashboardResponse(BaseModel):
    total_guides: int = Field(serialization_alias="totalGuides")
    total_categories: int = Field(serialization_alias="totalCategories")
    favourite_guides: int = Field(serialization_alias="favouriteGuides")
    recently_viewed: int = Field(serialization_alias="recentlyViewed")
    total_history: int = Field(serialization_alias="totalHistory")


class InsightsResponse(DashboardResponse):
    categories: list[CategoryResponse]
    favourite_topics: list[GuideSummaryResponse] = Field(serialization_alias="favouriteTopics")
    recently_viewed_topics: list[GuideSummaryResponse] = Field(serialization_alias="recentlyViewedTopics")
    most_viewed_topics: list[GuideSummaryResponse] = Field(serialization_alias="mostViewedTopics")
    guides_by_category: list[CountItem] = Field(serialization_alias="guidesByCategory")
