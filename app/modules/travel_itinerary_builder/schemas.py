from datetime import date, datetime, time
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

ItineraryStatus = Literal["draft", "planned", "active", "completed", "cancelled"]


def clean(value):
    if isinstance(value, str):
        value = " ".join(value.strip().split())
        return value or None
    return value


class CategoryWrite(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    color: str | None = Field(None, max_length=40)
    sort_order: int = Field(0, alias="sortOrder", ge=0, le=10000)
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("name", "color", mode="before")
    @classmethod
    def tidy(cls, value):
        return clean(value)


class TravelCategoryCreate(CategoryWrite):
    pass


class TravelCategoryUpdate(CategoryWrite):
    pass


class TravelCategoryResponse(CategoryWrite):
    id: str
    activity_count: int = Field(serialization_alias="activityCount")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")
    model_config = ConfigDict(populate_by_name=True)


class TravelCategoryList(BaseModel):
    items: list[TravelCategoryResponse]
    total: int
    page: int
    page_size: int = Field(serialization_alias="pageSize")
    pages: int


class ItineraryWrite(BaseModel):
    name: str = Field(min_length=1, max_length=180)
    destination: str = Field(min_length=1, max_length=180)
    start_date: date = Field(alias="startDate")
    end_date: date = Field(alias="endDate")
    status: ItineraryStatus = "draft"
    purpose: str | None = Field(None, max_length=80)
    notes: str | None = Field(None, max_length=5000)
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("name", "destination", "purpose", "notes", mode="before")
    @classmethod
    def tidy(cls, value):
        return clean(value)

    @model_validator(mode="after")
    def validate_dates(self):
        if self.end_date < self.start_date:
            raise ValueError("End date cannot be before start date.")
        return self


class ItineraryCreate(ItineraryWrite):
    pass


class ItineraryUpdate(ItineraryWrite):
    pass


class ItinerarySummary(BaseModel):
    id: str
    name: str
    destination: str
    start_date: date = Field(serialization_alias="startDate")
    end_date: date = Field(serialization_alias="endDate")
    status: ItineraryStatus
    purpose: str | None
    day_count: int = Field(serialization_alias="dayCount")
    activity_count: int = Field(serialization_alias="activityCount")
    next_activity: str | None = Field(serialization_alias="nextActivity")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")
    model_config = ConfigDict(populate_by_name=True)


class ItineraryDayWrite(BaseModel):
    day_date: date = Field(alias="dayDate")
    title: str | None = Field(None, max_length=160)
    notes: str | None = Field(None, max_length=5000)
    sort_order: int = Field(0, alias="sortOrder", ge=0, le=10000)
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("title", "notes", mode="before")
    @classmethod
    def tidy(cls, value):
        return clean(value)


class ItineraryDayCreate(ItineraryDayWrite):
    pass


class ItineraryDayUpdate(ItineraryDayWrite):
    pass


class ActivityWrite(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    category_id: str | None = Field(None, alias="categoryId")
    start_time: time | None = Field(None, alias="startTime")
    end_time: time | None = Field(None, alias="endTime")
    location: str | None = Field(None, max_length=240)
    booking_reference: str | None = Field(None, alias="bookingReference", max_length=160)
    notes: str | None = Field(None, max_length=5000)
    sort_order: int = Field(0, alias="sortOrder", ge=0, le=10000)
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("title", "location", "booking_reference", "notes", mode="before")
    @classmethod
    def tidy(cls, value):
        return clean(value)

    @model_validator(mode="after")
    def validate_times(self):
        if self.start_time and self.end_time and self.end_time <= self.start_time:
            raise ValueError("End time must be after start time.")
        return self


class ActivityCreate(ActivityWrite):
    pass


class ActivityUpdate(ActivityWrite):
    pass


class ActivityResponse(BaseModel):
    id: str
    category_id: str | None = Field(serialization_alias="categoryId")
    category_name: str | None = Field(serialization_alias="categoryName")
    category_color: str | None = Field(serialization_alias="categoryColor")
    title: str
    start_time: time | None = Field(serialization_alias="startTime")
    end_time: time | None = Field(serialization_alias="endTime")
    location: str | None
    booking_reference: str | None = Field(serialization_alias="bookingReference")
    notes: str | None
    sort_order: int = Field(serialization_alias="sortOrder")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")
    model_config = ConfigDict(populate_by_name=True)


class ItineraryDayResponse(BaseModel):
    id: str
    day_date: date = Field(serialization_alias="dayDate")
    title: str | None
    notes: str | None
    sort_order: int = Field(serialization_alias="sortOrder")
    activity_count: int = Field(serialization_alias="activityCount")
    activities: list[ActivityResponse] = []
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")
    model_config = ConfigDict(populate_by_name=True)


class ItineraryDetail(ItinerarySummary):
    notes: str | None
    days: list[ItineraryDayResponse] = []


class ItineraryList(BaseModel):
    items: list[ItinerarySummary]
    total: int
    page: int
    page_size: int = Field(serialization_alias="pageSize")
    pages: int


class TravelDashboard(BaseModel):
    draft: int
    planned: int
    active: int
    completed: int
    cancelled: int
    upcoming: int
    total_itineraries: int = Field(serialization_alias="totalItineraries")
    total_days: int = Field(serialization_alias="totalDays")
    total_activities: int = Field(serialization_alias="totalActivities")
    recent: list[ItinerarySummary]
    model_config = ConfigDict(populate_by_name=True)

