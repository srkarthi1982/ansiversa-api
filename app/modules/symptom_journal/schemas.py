from datetime import date, datetime, time
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator

ArchiveFilter = Literal["active", "archived", "all"]
EntrySort = Literal["date", "severity", "category", "title", "created", "updated"]
SeverityFilter = Literal["all", "mild", "moderate", "severe"]


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


class EntryCreateRequest(BaseModel):
    category_id: str | None = Field(default=None, alias="categoryId", max_length=36)
    entry_date: date = Field(alias="entryDate")
    entry_time: time | None = Field(default=None, alias="entryTime")
    symptom_title: str = Field(alias="symptomTitle", min_length=1, max_length=180)
    severity: int = Field(ge=1, le=10)
    duration: str | None = Field(default=None, max_length=120)
    body_location: str | None = Field(default=None, alias="bodyLocation", max_length=180)
    mood: str | None = Field(default=None, max_length=120)
    temperature: Decimal | None = Field(default=None, ge=30, le=45, max_digits=5, decimal_places=2)
    triggers: str | None = Field(default=None, max_length=5000)
    relief_methods: str | None = Field(default=None, alias="reliefMethods", max_length=5000)
    follow_up_notes: str | None = Field(default=None, alias="followUpNotes", max_length=5000)
    notes: str | None = Field(default=None, max_length=5000)
    archived: bool = False
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("symptom_title", "duration", "body_location", "mood", "triggers", "relief_methods", "follow_up_notes", "notes", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class EntryUpdateRequest(EntryCreateRequest):
    pass


class CategoryResponse(BaseModel):
    id: str
    name: str
    description: str | None
    sort_order: int = Field(serialization_alias="sortOrder")
    is_system: bool = Field(serialization_alias="isSystem")
    entry_count: int = Field(serialization_alias="entryCount")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class EntrySummaryResponse(BaseModel):
    id: str
    category_id: str | None = Field(serialization_alias="categoryId")
    category_name: str | None = Field(serialization_alias="categoryName")
    entry_date: date = Field(serialization_alias="entryDate")
    entry_time: time | None = Field(serialization_alias="entryTime")
    symptom_title: str = Field(serialization_alias="symptomTitle")
    severity: int
    severity_label: str = Field(serialization_alias="severityLabel")
    duration: str | None
    body_location: str | None = Field(serialization_alias="bodyLocation")
    mood: str | None
    temperature: Decimal | None
    archived: bool
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class EntryDetailResponse(EntrySummaryResponse):
    triggers: str | None
    relief_methods: str | None = Field(serialization_alias="reliefMethods")
    follow_up_notes: str | None = Field(serialization_alias="followUpNotes")
    notes: str | None


class EntryListResponse(BaseModel):
    items: list[EntrySummaryResponse]
    total: int
    page: int
    page_size: int = Field(serialization_alias="pageSize")


class CountItem(BaseModel):
    label: str
    count: int


class RecurringSymptomItem(BaseModel):
    title: str
    count: int
    average_severity: float = Field(serialization_alias="averageSeverity")


class DashboardResponse(BaseModel):
    total_entries: int = Field(serialization_alias="totalEntries")
    today_entries: int = Field(serialization_alias="todayEntries")
    weekly_entries: int = Field(serialization_alias="weeklyEntries")
    monthly_entries: int = Field(serialization_alias="monthlyEntries")
    archived_entries: int = Field(serialization_alias="archivedEntries")
    most_common_category: str | None = Field(serialization_alias="mostCommonCategory")
    average_severity: float = Field(serialization_alias="averageSeverity")


class InsightsResponse(DashboardResponse):
    categories: list[CategoryResponse]
    entries_by_category: list[CountItem] = Field(serialization_alias="entriesByCategory")
    entries_by_body_location: list[CountItem] = Field(serialization_alias="entriesByBodyLocation")
    entries_by_mood: list[CountItem] = Field(serialization_alias="entriesByMood")
    entries_by_severity: list[CountItem] = Field(serialization_alias="entriesBySeverity")
    recurring_symptoms: list[RecurringSymptomItem] = Field(serialization_alias="recurringSymptoms")
    recently_added_entries: list[EntrySummaryResponse] = Field(serialization_alias="recentlyAddedEntries")
