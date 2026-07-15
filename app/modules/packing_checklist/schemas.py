from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

ChecklistStatus = Literal["planning", "packing", "ready", "completed"]
ChecklistSort = Literal["updated", "startDate", "title", "progress"]
ArchiveFilter = Literal["active", "archived", "all"]
ItemPriority = Literal["low", "normal", "high"]
PackedFilter = Literal["all", "packed", "remaining"]


def _normalize_text(value: object) -> object:
    if isinstance(value, str):
        normalized = " ".join(value.strip().split())
        return normalized or None
    return value


class PackingCategoryCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    sort_order: int = Field(default=0, alias="sortOrder", ge=0, le=999)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("name", mode="before")
    @classmethod
    def normalize_name(cls, value: object) -> object:
        return _normalize_text(value)


class PackingCategoryUpdateRequest(PackingCategoryCreateRequest):
    pass


class PackingCategoryResponse(BaseModel):
    id: str
    name: str
    sort_order: int = Field(serialization_alias="sortOrder")
    is_system: bool = Field(serialization_alias="isSystem")
    item_count: int = Field(serialization_alias="itemCount")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class PackingChecklistCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    destination: str | None = Field(default=None, max_length=180)
    trip_type: str = Field(default="Travel", alias="tripType", min_length=1, max_length=80)
    start_date: date | None = Field(default=None, alias="startDate")
    end_date: date | None = Field(default=None, alias="endDate")
    status: ChecklistStatus = "planning"
    notes: str | None = Field(default=None, max_length=5000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("title", "destination", "trip_type", "notes", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)

    @model_validator(mode="after")
    def validate_dates(self) -> "PackingChecklistCreateRequest":
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValueError("endDate must be on or after startDate.")
        return self


class PackingChecklistUpdateRequest(PackingChecklistCreateRequest):
    pass


class PackingItemCreateRequest(BaseModel):
    item_name: str = Field(alias="itemName", min_length=1, max_length=180)
    category_id: str = Field(alias="categoryId", min_length=1, max_length=36)
    quantity: int = Field(default=1, ge=1, le=999)
    packed: bool = False
    priority: ItemPriority = "normal"
    notes: str | None = Field(default=None, max_length=2000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("item_name", "notes", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class PackingItemUpdateRequest(PackingItemCreateRequest):
    pass


class PackingItemResponse(BaseModel):
    id: str
    checklist_id: str = Field(serialization_alias="checklistId")
    category_id: str = Field(serialization_alias="categoryId")
    category_name: str = Field(serialization_alias="categoryName")
    item_name: str = Field(serialization_alias="itemName")
    quantity: int
    packed: bool
    priority: ItemPriority
    notes: str | None
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class PackingChecklistSummaryResponse(BaseModel):
    id: str
    title: str
    destination: str | None
    trip_type: str = Field(serialization_alias="tripType")
    start_date: date | None = Field(serialization_alias="startDate")
    end_date: date | None = Field(serialization_alias="endDate")
    status: ChecklistStatus
    archived: bool
    notes_preview: str | None = Field(serialization_alias="notesPreview")
    total_items: int = Field(serialization_alias="totalItems")
    packed_items: int = Field(serialization_alias="packedItems")
    remaining_items: int = Field(serialization_alias="remainingItems")
    high_priority_remaining: int = Field(serialization_alias="highPriorityRemaining")
    completion_percentage: int = Field(serialization_alias="completionPercentage")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class PackingChecklistDetailResponse(PackingChecklistSummaryResponse):
    notes: str | None
    items: list[PackingItemResponse]


class PackingCountItem(BaseModel):
    label: str
    count: int


class PackingChecklistDashboardResponse(BaseModel):
    total_checklists: int = Field(serialization_alias="totalChecklists")
    active_checklists: int = Field(serialization_alias="activeChecklists")
    archived_checklists: int = Field(serialization_alias="archivedChecklists")
    total_items: int = Field(serialization_alias="totalItems")
    packed_items: int = Field(serialization_alias="packedItems")
    remaining_items: int = Field(serialization_alias="remainingItems")
    high_priority_remaining: int = Field(serialization_alias="highPriorityRemaining")
    average_completion: int = Field(serialization_alias="averageCompletion")


class PackingChecklistInsightsResponse(PackingChecklistDashboardResponse):
    categories: list[PackingCategoryResponse]
    status_distribution: list[PackingCountItem] = Field(serialization_alias="statusDistribution")
    trip_type_distribution: list[PackingCountItem] = Field(serialization_alias="tripTypeDistribution")
    category_distribution: list[PackingCountItem] = Field(serialization_alias="categoryDistribution")
    upcoming_checklists: list[PackingChecklistSummaryResponse] = Field(serialization_alias="upcomingChecklists")
    recently_updated: list[PackingChecklistSummaryResponse] = Field(serialization_alias="recentlyUpdated")
