from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

RecordStatus = Literal["active", "inactive"]
TaskPriority = Literal["low", "medium", "high", "urgent"]
TaskRecurring = Literal["none", "daily", "weekly", "monthly"]
TaskStatus = Literal["pending", "inProgress", "completed", "reopened", "archived"]


def _normalize_text(value: object) -> object:
    if isinstance(value, str):
        normalized = value.strip()
        return normalized or None
    return value


class MemberCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=140)
    color: str | None = Field(default=None, max_length=40)
    avatar: str | None = Field(default=None, max_length=80)
    status: RecordStatus = "active"

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class MemberUpdateRequest(MemberCreateRequest):
    name: str | None = Field(default=None, min_length=1, max_length=140)
    status: RecordStatus | None = None


class CategoryCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=140)
    color: str | None = Field(default=None, max_length=40)
    description: str | None = Field(default=None, max_length=2000)
    status: RecordStatus = "active"

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class CategoryUpdateRequest(CategoryCreateRequest):
    name: str | None = Field(default=None, min_length=1, max_length=140)
    status: RecordStatus | None = None


class TaskCreateRequest(BaseModel):
    member_id: str | None = Field(default=None, alias="memberId", max_length=36)
    category_id: str | None = Field(default=None, alias="categoryId", max_length=36)
    title: str = Field(min_length=1, max_length=180)
    description: str | None = Field(default=None, max_length=4000)
    priority: TaskPriority = "medium"
    due_date: str | None = Field(default=None, alias="dueDate", max_length=40)
    recurring: TaskRecurring = "none"
    status: TaskStatus = "pending"
    notes: str | None = Field(default=None, max_length=4000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class TaskUpdateRequest(TaskCreateRequest):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    priority: TaskPriority | None = None
    recurring: TaskRecurring | None = None
    status: TaskStatus | None = None


class TaskDuplicateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    due_date: str | None = Field(default=None, alias="dueDate", max_length=40)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class MemberSummaryResponse(BaseModel):
    id: str
    name: str
    color: str | None
    avatar: str | None
    status: RecordStatus
    task_count: int = Field(serialization_alias="taskCount")
    pending_count: int = Field(serialization_alias="pendingCount")
    completed_count: int = Field(serialization_alias="completedCount")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class CategorySummaryResponse(BaseModel):
    id: str
    name: str
    color: str | None
    description_preview: str | None = Field(serialization_alias="descriptionPreview")
    status: RecordStatus
    task_count: int = Field(serialization_alias="taskCount")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class TaskSummaryResponse(BaseModel):
    id: str
    member_id: str | None = Field(serialization_alias="memberId")
    member_name: str | None = Field(serialization_alias="memberName")
    category_id: str | None = Field(serialization_alias="categoryId")
    category_name: str | None = Field(serialization_alias="categoryName")
    title: str
    description_preview: str | None = Field(serialization_alias="descriptionPreview")
    priority: TaskPriority
    due_date: str | None = Field(serialization_alias="dueDate")
    recurring: TaskRecurring
    status: TaskStatus
    notes_preview: str | None = Field(serialization_alias="notesPreview")
    completed_at: str | None = Field(serialization_alias="completedAt")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class MemberDetailResponse(MemberSummaryResponse):
    pass


class CategoryDetailResponse(CategorySummaryResponse):
    description: str | None


class TaskDetailResponse(TaskSummaryResponse):
    description: str | None
    notes: str | None


class CalendarDayResponse(BaseModel):
    date: str
    tasks: list[TaskSummaryResponse]


class WorkloadResponse(BaseModel):
    member_id: str | None = Field(serialization_alias="memberId")
    member_name: str = Field(serialization_alias="memberName")
    pending_count: int = Field(serialization_alias="pendingCount")
    completed_count: int = Field(serialization_alias="completedCount")


class CategoryDistributionResponse(BaseModel):
    category_id: str | None = Field(serialization_alias="categoryId")
    category_name: str = Field(serialization_alias="categoryName")
    task_count: int = Field(serialization_alias="taskCount")


class FamilyTaskPlannerDashboardResponse(BaseModel):
    tasks: list[TaskSummaryResponse]
    members: list[MemberSummaryResponse]
    categories: list[CategorySummaryResponse]
    task_count: int = Field(serialization_alias="taskCount")
    pending_count: int = Field(serialization_alias="pendingCount")
    completed_count: int = Field(serialization_alias="completedCount")
    overdue_count: int = Field(serialization_alias="overdueCount")
    due_today: list[TaskSummaryResponse] = Field(serialization_alias="dueToday")
    upcoming_tasks: list[TaskSummaryResponse] = Field(serialization_alias="upcomingTasks")
    recently_completed: list[TaskSummaryResponse] = Field(serialization_alias="recentlyCompleted")
    workload: list[WorkloadResponse]
    calendar: list[CalendarDayResponse]
    completed_this_week: int = Field(serialization_alias="completedThisWeek")
    completion_rate: int = Field(serialization_alias="completionRate")
    most_active_member: str | None = Field(serialization_alias="mostActiveMember")
    category_distribution: list[CategoryDistributionResponse] = Field(serialization_alias="categoryDistribution")
