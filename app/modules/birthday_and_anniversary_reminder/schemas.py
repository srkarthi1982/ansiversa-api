from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

ArchiveFilter = Literal["active", "archived", "all"]
ReminderSort = Literal["upcoming", "name", "type", "created"]
FavouriteFilter = Literal["all", "favourites"]
TimeFilter = Literal["all", "today", "week", "month", "next30", "missed", "acknowledged"]


def _normalize_text(value: object) -> object:
    if isinstance(value, str):
        normalized = " ".join(value.strip().split())
        return normalized or None
    return value


def _normalize_phone(value: object) -> object:
    if isinstance(value, str):
        normalized = value.strip()
        return normalized or None
    return value


def _validate_phone(value: str | None) -> str | None:
    if value is None:
        return None
    allowed = set("0123456789+()-. xX")
    if sum(1 for character in value if character.isdigit()) < 3 or any(character not in allowed for character in value):
        raise ValueError("phone must be a valid phone value.")
    return value


class ReminderTypeCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    sort_order: int = Field(default=0, alias="sortOrder", ge=0, le=999)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("name", mode="before")
    @classmethod
    def normalize_name(cls, value: object) -> object:
        return _normalize_text(value)


class ReminderTypeUpdateRequest(ReminderTypeCreateRequest):
    pass


class ReminderTypeResponse(BaseModel):
    id: str
    name: str
    sort_order: int = Field(serialization_alias="sortOrder")
    is_system: bool = Field(serialization_alias="isSystem")
    reminder_count: int = Field(serialization_alias="reminderCount")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class ReminderCreateRequest(BaseModel):
    person_name: str = Field(alias="personName", min_length=1, max_length=180)
    reminder_type_id: str = Field(alias="reminderTypeId", min_length=1, max_length=36)
    relationship: str | None = Field(default=None, max_length=120)
    event_date: date = Field(alias="eventDate")
    phone: str | None = Field(default=None, max_length=60)
    email: EmailStr | None = Field(default=None, max_length=180)
    gift_ideas: str | None = Field(default=None, alias="giftIdeas", max_length=4000)
    notes: str | None = Field(default=None, max_length=5000)
    favourite: bool = False
    archived: bool = False

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("person_name", "relationship", "gift_ideas", "notes", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)

    @field_validator("phone", mode="before")
    @classmethod
    def normalize_phone(cls, value: object) -> object:
        return _normalize_phone(value)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str | None) -> str | None:
        return _validate_phone(value)


class ReminderUpdateRequest(ReminderCreateRequest):
    pass


class ReminderSummaryResponse(BaseModel):
    id: str
    person_name: str = Field(serialization_alias="personName")
    reminder_type_id: str = Field(serialization_alias="reminderTypeId")
    reminder_type_name: str = Field(serialization_alias="reminderTypeName")
    relationship: str | None
    event_date: date = Field(serialization_alias="eventDate")
    next_occurrence: date = Field(serialization_alias="nextOccurrence")
    days_remaining: int = Field(serialization_alias="daysRemaining")
    phone: str | None
    email: str | None
    favourite: bool
    archived: bool
    acknowledged_this_year: bool = Field(serialization_alias="acknowledgedThisYear")
    missed_this_year: bool = Field(serialization_alias="missedThisYear")
    gift_preview: str | None = Field(serialization_alias="giftPreview")
    notes_preview: str | None = Field(serialization_alias="notesPreview")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class ReminderDetailResponse(ReminderSummaryResponse):
    gift_ideas: str | None = Field(serialization_alias="giftIdeas")
    notes: str | None


class CountItem(BaseModel):
    label: str
    count: int


class DashboardResponse(BaseModel):
    total_reminders: int = Field(serialization_alias="totalReminders")
    birthdays: int
    anniversaries: int
    today: int
    this_week: int = Field(serialization_alias="thisWeek")
    this_month: int = Field(serialization_alias="thisMonth")
    next_30_days: int = Field(serialization_alias="next30Days")
    missed_this_year: int = Field(serialization_alias="missedThisYear")
    acknowledged_this_year: int = Field(serialization_alias="acknowledgedThisYear")
    favourites: int


class InsightsResponse(DashboardResponse):
    types: list[ReminderTypeResponse]
    monthly_distribution: list[CountItem] = Field(serialization_alias="monthlyDistribution")
    type_distribution: list[CountItem] = Field(serialization_alias="typeDistribution")
    favourite_reminders: list[ReminderSummaryResponse] = Field(serialization_alias="favouriteReminders")
    recently_added: list[ReminderSummaryResponse] = Field(serialization_alias="recentlyAdded")
    upcoming_next_30: list[ReminderSummaryResponse] = Field(serialization_alias="upcomingNext30")
