from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

ActivityType = Literal["strength", "cardio", "mobility", "sport", "other"]
ActivityIntensity = Literal["light", "moderate", "hard"]
ActivityStatus = Literal["active", "archived"]
DistanceUnit = Literal["km", "mi"]
SortDirection = Literal["asc", "desc"]


def _normalize_text(value: object) -> object:
    if isinstance(value, str):
        normalized = value.strip()
        return normalized or None
    return value


class ActivityCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    activity_type: ActivityType = Field(default="other", alias="activityType")
    default_duration_minutes: int | None = Field(default=None, alias="defaultDurationMinutes", ge=1, le=1440)
    intensity: ActivityIntensity = "moderate"
    status: ActivityStatus = "active"
    notes: str | None = Field(default=None, max_length=4000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class ActivityUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    activity_type: ActivityType | None = Field(default=None, alias="activityType")
    default_duration_minutes: int | None = Field(default=None, alias="defaultDurationMinutes", ge=1, le=1440)
    intensity: ActivityIntensity | None = None
    status: ActivityStatus | None = None
    notes: str | None = Field(default=None, max_length=4000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class LogCreateRequest(BaseModel):
    activity_id: str = Field(alias="activityId", min_length=1, max_length=36)
    log_date: str = Field(alias="logDate", min_length=1, max_length=40)
    duration_minutes: int = Field(alias="durationMinutes", ge=1, le=1440)
    intensity: ActivityIntensity = "moderate"
    effort: int | None = Field(default=None, ge=1, le=10)
    distance_value: float | None = Field(default=None, alias="distanceValue", ge=0, le=1000000)
    distance_unit: DistanceUnit | None = Field(default=None, alias="distanceUnit")
    notes: str | None = Field(default=None, max_length=4000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class LogUpdateRequest(BaseModel):
    log_date: str | None = Field(default=None, alias="logDate", min_length=1, max_length=40)
    duration_minutes: int | None = Field(default=None, alias="durationMinutes", ge=1, le=1440)
    intensity: ActivityIntensity | None = None
    effort: int | None = Field(default=None, ge=1, le=10)
    distance_value: float | None = Field(default=None, alias="distanceValue", ge=0, le=1000000)
    distance_unit: DistanceUnit | None = Field(default=None, alias="distanceUnit")
    notes: str | None = Field(default=None, max_length=4000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class ActivitySummaryResponse(BaseModel):
    id: str
    title: str
    activity_type: ActivityType = Field(serialization_alias="activityType")
    default_duration_minutes: int | None = Field(serialization_alias="defaultDurationMinutes")
    intensity: ActivityIntensity
    status: ActivityStatus
    notes_preview: str | None = Field(serialization_alias="notesPreview")
    log_count: int = Field(serialization_alias="logCount")
    total_minutes: int = Field(serialization_alias="totalMinutes")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class ActivityDetailResponse(ActivitySummaryResponse):
    notes: str | None
    logs: list["LogSummaryResponse"]


class LogSummaryResponse(BaseModel):
    id: str
    activity_id: str = Field(serialization_alias="activityId")
    activity_title: str = Field(serialization_alias="activityTitle")
    activity_type: ActivityType = Field(serialization_alias="activityType")
    log_date: str = Field(serialization_alias="logDate")
    duration_minutes: int = Field(serialization_alias="durationMinutes")
    intensity: ActivityIntensity
    effort: int | None
    distance_value: float | None = Field(serialization_alias="distanceValue")
    distance_unit: DistanceUnit | None = Field(serialization_alias="distanceUnit")
    notes_preview: str | None = Field(serialization_alias="notesPreview")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class LogDetailResponse(LogSummaryResponse):
    notes: str | None


class FitnessTrackerDashboardResponse(BaseModel):
    activities: list[ActivitySummaryResponse]
    logs: list[LogSummaryResponse]
    activity_count: int = Field(serialization_alias="activityCount")
    active_activity_count: int = Field(serialization_alias="activeActivityCount")
    log_count: int = Field(serialization_alias="logCount")
    total_minutes: int = Field(serialization_alias="totalMinutes")
    recent_logs: list[LogSummaryResponse] = Field(serialization_alias="recentLogs")
    weekly_minutes: int = Field(serialization_alias="weeklyMinutes")


class PaginatedActivityResponse(BaseModel):
    items: list[ActivitySummaryResponse]
    page: int
    page_size: int = Field(serialization_alias="pageSize")
    total: int


class PaginatedLogResponse(BaseModel):
    items: list[LogSummaryResponse]
    page: int
    page_size: int = Field(serialization_alias="pageSize")
    total: int
