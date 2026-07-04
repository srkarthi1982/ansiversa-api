from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

TaskStatus = Literal["inbox", "next", "in-progress", "waiting", "done"]
TaskCategory = Literal["work", "personal", "finance", "health", "learning", "other"]
PriorityLabel = Literal["low", "medium", "high", "urgent"]
PrioritySource = Literal["system", "manual"]
HistoryAction = Literal["created", "updated", "deleted", "duplicated", "priority-assigned", "recalculated", "status-change"]


def _normalize_text(value: object) -> object:
    if isinstance(value, str):
        normalized = value.strip()
        return normalized or None
    return value


class TaskPrioritizerTaskCreateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    title: str = Field(min_length=1, max_length=180)
    category: TaskCategory = "work"
    status: TaskStatus = "inbox"
    due_date: str | None = Field(default=None, alias="dueDate", max_length=40)
    effort: int = Field(default=3, ge=1, le=5)
    impact: int = Field(default=3, ge=1, le=5)
    urgency: int = Field(default=3, ge=1, le=5)
    priority_label: PriorityLabel = Field(default="medium", alias="priorityLabel")
    manual_override: bool = Field(default=False, alias="manualOverride")
    notes: str | None = Field(default=None, max_length=4000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class TaskPrioritizerTaskUpdateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    title: str | None = Field(default=None, min_length=1, max_length=180)
    category: TaskCategory | None = None
    status: TaskStatus | None = None
    due_date: str | None = Field(default=None, alias="dueDate", max_length=40)
    effort: int | None = Field(default=None, ge=1, le=5)
    impact: int | None = Field(default=None, ge=1, le=5)
    urgency: int | None = Field(default=None, ge=1, le=5)
    priority_label: PriorityLabel | None = Field(default=None, alias="priorityLabel")
    manual_override: bool | None = Field(default=None, alias="manualOverride")
    notes: str | None = Field(default=None, max_length=4000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class TaskPrioritizerPriorityAssignRequest(BaseModel):
    priority_label: PriorityLabel = Field(alias="priorityLabel")
    priority_score: float | None = Field(default=None, alias="priorityScore", ge=0)
    reason: str | None = Field(default=None, max_length=1000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class TaskPrioritizerRuleCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    category: TaskCategory | None = None
    impact_weight: float = Field(default=2, alias="impactWeight", ge=0, le=10)
    urgency_weight: float = Field(default=2, alias="urgencyWeight", ge=0, le=10)
    effort_weight: float = Field(default=1, alias="effortWeight", ge=0, le=10)
    due_date_weight: float = Field(default=2, alias="dueDateWeight", ge=0, le=10)
    is_enabled: bool = Field(default=True, alias="isEnabled")
    notes: str | None = Field(default=None, max_length=2000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class TaskPrioritizerRuleUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=160)
    category: TaskCategory | None = None
    impact_weight: float | None = Field(default=None, alias="impactWeight", ge=0, le=10)
    urgency_weight: float | None = Field(default=None, alias="urgencyWeight", ge=0, le=10)
    effort_weight: float | None = Field(default=None, alias="effortWeight", ge=0, le=10)
    due_date_weight: float | None = Field(default=None, alias="dueDateWeight", ge=0, le=10)
    is_enabled: bool | None = Field(default=None, alias="isEnabled")
    notes: str | None = Field(default=None, max_length=2000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class TaskPrioritizerTaskSummaryResponse(BaseModel):
    id: int
    platform_id: str | None = Field(serialization_alias="platformId")
    title: str
    category: TaskCategory
    status: TaskStatus
    due_date: str | None = Field(serialization_alias="dueDate")
    effort: int
    impact: int
    urgency: int
    priority_score: float = Field(serialization_alias="priorityScore")
    priority_label: PriorityLabel = Field(serialization_alias="priorityLabel")
    manual_override: bool = Field(serialization_alias="manualOverride")
    notes_preview: str | None = Field(serialization_alias="notesPreview")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class TaskPrioritizerTaskDetailResponse(TaskPrioritizerTaskSummaryResponse):
    notes: str | None


class TaskPrioritizerPriorityResponse(BaseModel):
    id: int
    task_id: int = Field(serialization_alias="taskId")
    priority_score: float = Field(serialization_alias="priorityScore")
    priority_label: PriorityLabel = Field(serialization_alias="priorityLabel")
    source: PrioritySource
    reason: str | None
    created_at: datetime = Field(serialization_alias="createdAt")

    model_config = ConfigDict(from_attributes=True)


class TaskPrioritizerRuleResponse(BaseModel):
    id: int
    title: str
    category: TaskCategory | None
    impact_weight: float = Field(serialization_alias="impactWeight")
    urgency_weight: float = Field(serialization_alias="urgencyWeight")
    effort_weight: float = Field(serialization_alias="effortWeight")
    due_date_weight: float = Field(serialization_alias="dueDateWeight")
    is_enabled: bool = Field(serialization_alias="isEnabled")
    notes: str | None
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class TaskPrioritizerHistoryResponse(BaseModel):
    id: int
    task_id: int | None = Field(serialization_alias="taskId")
    task_title: str | None = Field(serialization_alias="taskTitle")
    action_type: HistoryAction = Field(serialization_alias="actionType")
    previous_priority: str | None = Field(serialization_alias="previousPriority")
    new_priority: str | None = Field(serialization_alias="newPriority")
    priority_score: float | None = Field(serialization_alias="priorityScore")
    notes: str | None
    created_at: datetime = Field(serialization_alias="createdAt")


class TaskPrioritizerDashboardResponse(BaseModel):
    tasks: list[TaskPrioritizerTaskSummaryResponse]
    rules: list[TaskPrioritizerRuleResponse]
    history: list[TaskPrioritizerHistoryResponse]
    total_tasks: int = Field(serialization_alias="totalTasks")
    open_tasks: int = Field(serialization_alias="openTasks")
    urgent_tasks: int = Field(serialization_alias="urgentTasks")
    overdue_tasks: int = Field(serialization_alias="overdueTasks")
    manual_overrides: int = Field(serialization_alias="manualOverrides")
    average_priority_score: float = Field(serialization_alias="averagePriorityScore")
    top_tasks: list[TaskPrioritizerTaskSummaryResponse] = Field(serialization_alias="topTasks")
