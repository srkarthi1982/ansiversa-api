from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

PlanStatus = Literal["active", "paused", "completed"]
TaskPriority = Literal["low", "medium", "high"]
TaskStatus = Literal["pending", "inProgress", "completed"]


def _normalize_text(value: object) -> object:
    if isinstance(value, str):
        normalized = value.strip()
        return normalized or None

    return value


class StudyPlanCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    subject: str = Field(min_length=1, max_length=120)
    goal: str = Field(min_length=1, max_length=2000)
    start_date: date = Field(alias="startDate")
    target_date: date = Field(alias="targetDate")

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("title", "subject", "goal", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)

    @model_validator(mode="after")
    def validate_dates(self) -> "StudyPlanCreateRequest":
        if self.target_date < self.start_date:
            raise ValueError("targetDate must be on or after startDate.")

        return self


class StudyPlanUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    subject: str | None = Field(default=None, min_length=1, max_length=120)
    goal: str | None = Field(default=None, min_length=1, max_length=2000)
    start_date: date | None = Field(default=None, alias="startDate")
    target_date: date | None = Field(default=None, alias="targetDate")
    status: PlanStatus | None = None

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("title", "subject", "goal", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class StudyPlanTaskCreateRequest(BaseModel):
    plan_id: int = Field(alias="planId", gt=0)
    title: str = Field(min_length=1, max_length=180)
    notes: str | None = Field(default=None, max_length=2000)
    due_date: date | None = Field(default=None, alias="dueDate")
    priority: TaskPriority = "medium"

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("title", "notes", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class StudyPlanTaskUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    notes: str | None = Field(default=None, max_length=2000)
    due_date: date | None = Field(default=None, alias="dueDate")
    priority: TaskPriority | None = None
    status: TaskStatus | None = None

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("title", "notes", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class StudyLogCreateRequest(BaseModel):
    plan_id: int = Field(alias="planId", gt=0)
    task_id: int | None = Field(default=None, alias="taskId", gt=0)
    study_date: date = Field(alias="studyDate")
    minutes: int = Field(gt=0, le=1440)
    focus: str = Field(min_length=1, max_length=180)
    reflection: str | None = Field(default=None, max_length=2000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("focus", "reflection", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class StudyPlanResponse(BaseModel):
    id: int
    title: str
    subject: str
    goal: str
    start_date: date = Field(serialization_alias="startDate")
    target_date: date = Field(serialization_alias="targetDate")
    status: PlanStatus
    task_count: int = Field(serialization_alias="taskCount")
    completed_task_count: int = Field(serialization_alias="completedTaskCount")
    total_minutes: int = Field(serialization_alias="totalMinutes")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class StudyPlanListResponse(BaseModel):
    items: list[StudyPlanResponse]


class StudyPlanTaskResponse(BaseModel):
    id: int
    plan_id: int = Field(serialization_alias="planId")
    plan_title: str = Field(serialization_alias="planTitle")
    title: str
    notes: str | None
    due_date: date | None = Field(serialization_alias="dueDate")
    priority: TaskPriority
    status: TaskStatus
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class StudyPlanTaskListResponse(BaseModel):
    items: list[StudyPlanTaskResponse]


class StudyLogResponse(BaseModel):
    id: int
    plan_id: int = Field(serialization_alias="planId")
    plan_title: str = Field(serialization_alias="planTitle")
    task_id: int | None = Field(serialization_alias="taskId")
    task_title: str | None = Field(serialization_alias="taskTitle")
    study_date: date = Field(serialization_alias="studyDate")
    minutes: int
    focus: str
    reflection: str | None
    created_at: datetime = Field(serialization_alias="createdAt")

    model_config = ConfigDict(from_attributes=True)


class StudyLogListResponse(BaseModel):
    items: list[StudyLogResponse]


class StudyPlannerReviewResponse(BaseModel):
    active_plan_count: int = Field(serialization_alias="activePlanCount")
    completed_plan_count: int = Field(serialization_alias="completedPlanCount")
    total_task_count: int = Field(serialization_alias="totalTaskCount")
    completed_task_count: int = Field(serialization_alias="completedTaskCount")
    total_minutes: int = Field(serialization_alias="totalMinutes")
    completion_rate: int = Field(serialization_alias="completionRate")
    recent_logs: list[StudyLogResponse] = Field(serialization_alias="recentLogs")


class StudyPlannerDashboardResponse(BaseModel):
    plans: list[StudyPlanResponse]
    tasks: list[StudyPlanTaskResponse]
    logs: list[StudyLogResponse]
    review: StudyPlannerReviewResponse
