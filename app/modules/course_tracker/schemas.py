from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

CourseStatus = Literal["active", "paused", "completed"]
ModuleStatus = Literal["notStarted", "inProgress", "completed"]


def _normalize_text(value: object) -> object:
    if isinstance(value, str):
        normalized = value.strip()
        return normalized or None

    return value


class CourseCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    provider: str = Field(min_length=1, max_length=120)
    category: str | None = Field(default=None, max_length=120)
    goal: str = Field(min_length=1, max_length=2000)
    start_date: date = Field(alias="startDate")
    target_date: date | None = Field(default=None, alias="targetDate")

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("title", "provider", "category", "goal", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)

    @model_validator(mode="after")
    def validate_dates(self) -> "CourseCreateRequest":
        if self.target_date is not None and self.target_date < self.start_date:
            raise ValueError("targetDate must be on or after startDate.")

        return self


class CourseUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    provider: str | None = Field(default=None, min_length=1, max_length=120)
    category: str | None = Field(default=None, max_length=120)
    goal: str | None = Field(default=None, min_length=1, max_length=2000)
    start_date: date | None = Field(default=None, alias="startDate")
    target_date: date | None = Field(default=None, alias="targetDate")
    status: CourseStatus | None = None

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("title", "provider", "category", "goal", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class CourseModuleCreateRequest(BaseModel):
    course_id: int = Field(alias="courseId", gt=0)
    title: str = Field(min_length=1, max_length=180)
    notes: str | None = Field(default=None, max_length=2000)
    sequence: int = Field(default=1, gt=0, le=1000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("title", "notes", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class CourseModuleUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    notes: str | None = Field(default=None, max_length=2000)
    sequence: int | None = Field(default=None, gt=0, le=1000)
    status: ModuleStatus | None = None

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("title", "notes", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class CourseProgressLogCreateRequest(BaseModel):
    course_id: int = Field(alias="courseId", gt=0)
    module_id: int | None = Field(default=None, alias="moduleId", gt=0)
    progress_date: date = Field(alias="progressDate")
    minutes: int = Field(gt=0, le=1440)
    summary: str = Field(min_length=1, max_length=240)
    reflection: str | None = Field(default=None, max_length=2000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("summary", "reflection", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class CourseResponse(BaseModel):
    id: int
    title: str
    provider: str
    category: str | None
    goal: str
    start_date: date = Field(serialization_alias="startDate")
    target_date: date | None = Field(serialization_alias="targetDate")
    status: CourseStatus
    module_count: int = Field(serialization_alias="moduleCount")
    completed_module_count: int = Field(serialization_alias="completedModuleCount")
    total_minutes: int = Field(serialization_alias="totalMinutes")
    completion_rate: int = Field(serialization_alias="completionRate")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class CourseListResponse(BaseModel):
    items: list[CourseResponse]


class CourseModuleResponse(BaseModel):
    id: int
    course_id: int = Field(serialization_alias="courseId")
    course_title: str = Field(serialization_alias="courseTitle")
    title: str
    notes: str | None
    sequence: int
    status: ModuleStatus
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class CourseModuleListResponse(BaseModel):
    items: list[CourseModuleResponse]


class CourseProgressLogResponse(BaseModel):
    id: int
    course_id: int = Field(serialization_alias="courseId")
    course_title: str = Field(serialization_alias="courseTitle")
    module_id: int | None = Field(serialization_alias="moduleId")
    module_title: str | None = Field(serialization_alias="moduleTitle")
    progress_date: date = Field(serialization_alias="progressDate")
    minutes: int
    summary: str
    reflection: str | None
    created_at: datetime = Field(serialization_alias="createdAt")

    model_config = ConfigDict(from_attributes=True)


class CourseProgressLogListResponse(BaseModel):
    items: list[CourseProgressLogResponse]


class CourseTrackerReviewResponse(BaseModel):
    active_course_count: int = Field(serialization_alias="activeCourseCount")
    completed_course_count: int = Field(serialization_alias="completedCourseCount")
    total_module_count: int = Field(serialization_alias="totalModuleCount")
    completed_module_count: int = Field(serialization_alias="completedModuleCount")
    total_minutes: int = Field(serialization_alias="totalMinutes")
    completion_rate: int = Field(serialization_alias="completionRate")
    recent_logs: list[CourseProgressLogResponse] = Field(serialization_alias="recentLogs")


class CourseTrackerDashboardResponse(BaseModel):
    courses: list[CourseResponse]
    modules: list[CourseModuleResponse]
    progress_logs: list[CourseProgressLogResponse] = Field(serialization_alias="progressLogs")
    review: CourseTrackerReviewResponse
