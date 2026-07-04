from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

ProjectStatus = Literal["planning", "active", "on-hold", "completed"]
ProjectPriority = Literal["low", "medium", "high", "urgent"]
TaskStatus = Literal["todo", "doing", "blocked", "done"]


def _normalize_text(value: object) -> object:
    if isinstance(value, str):
        normalized = value.strip()
        return normalized or None
    return value


class ProjectTrackerProjectCreateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    title: str = Field(min_length=1, max_length=180)
    owner_name: str | None = Field(default=None, alias="ownerName", max_length=120)
    status: ProjectStatus = "planning"
    priority: ProjectPriority = "medium"
    due_date: str | None = Field(default=None, alias="dueDate", max_length=40)
    notes: str | None = Field(default=None, max_length=4000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class ProjectTrackerProjectUpdateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    title: str | None = Field(default=None, min_length=1, max_length=180)
    owner_name: str | None = Field(default=None, alias="ownerName", max_length=120)
    status: ProjectStatus | None = None
    priority: ProjectPriority | None = None
    due_date: str | None = Field(default=None, alias="dueDate", max_length=40)
    notes: str | None = Field(default=None, max_length=4000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class ProjectTrackerTaskCreateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    project_id: int = Field(alias="projectId", gt=0)
    title: str = Field(min_length=1, max_length=180)
    status: TaskStatus = "todo"
    priority: ProjectPriority = "medium"
    due_date: str | None = Field(default=None, alias="dueDate", max_length=40)
    estimate_hours: float | None = Field(default=None, alias="estimateHours", ge=0)
    notes: str | None = Field(default=None, max_length=4000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class ProjectTrackerTaskUpdateRequest(BaseModel):
    platform_id: str | None = Field(default=None, alias="platformId", max_length=120)
    title: str | None = Field(default=None, min_length=1, max_length=180)
    status: TaskStatus | None = None
    priority: ProjectPriority | None = None
    due_date: str | None = Field(default=None, alias="dueDate", max_length=40)
    estimate_hours: float | None = Field(default=None, alias="estimateHours", ge=0)
    notes: str | None = Field(default=None, max_length=4000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class ProjectTrackerProjectSummaryResponse(BaseModel):
    id: int
    platform_id: str | None = Field(serialization_alias="platformId")
    title: str
    owner_name: str | None = Field(serialization_alias="ownerName")
    status: ProjectStatus
    priority: ProjectPriority
    due_date: str | None = Field(serialization_alias="dueDate")
    notes_preview: str | None = Field(serialization_alias="notesPreview")
    task_count: int = Field(serialization_alias="taskCount")
    completed_task_count: int = Field(serialization_alias="completedTaskCount")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class ProjectTrackerProjectDetailResponse(ProjectTrackerProjectSummaryResponse):
    notes: str | None


class ProjectTrackerTaskSummaryResponse(BaseModel):
    id: int
    platform_id: str | None = Field(serialization_alias="platformId")
    project_id: int = Field(serialization_alias="projectId")
    project_title: str = Field(serialization_alias="projectTitle")
    title: str
    status: TaskStatus
    priority: ProjectPriority
    due_date: str | None = Field(serialization_alias="dueDate")
    estimate_hours: float | None = Field(serialization_alias="estimateHours")
    notes_preview: str | None = Field(serialization_alias="notesPreview")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class ProjectTrackerTaskDetailResponse(ProjectTrackerTaskSummaryResponse):
    notes: str | None


class ProjectTrackerDashboardResponse(BaseModel):
    projects: list[ProjectTrackerProjectSummaryResponse]
    tasks: list[ProjectTrackerTaskSummaryResponse]
    total_projects: int = Field(serialization_alias="totalProjects")
    active_projects: int = Field(serialization_alias="activeProjects")
    completed_projects: int = Field(serialization_alias="completedProjects")
    total_tasks: int = Field(serialization_alias="totalTasks")
    completed_tasks: int = Field(serialization_alias="completedTasks")
    blocked_tasks: int = Field(serialization_alias="blockedTasks")
    overdue_tasks: int = Field(serialization_alias="overdueTasks")
    upcoming_tasks: list[ProjectTrackerTaskSummaryResponse] = Field(serialization_alias="upcomingTasks")
