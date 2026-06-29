from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

GoalStatus = Literal["active", "paused", "completed", "archived"]
RoadmapStatus = Literal["planned", "inProgress", "completed", "archived"]
MilestoneStatus = Literal["todo", "inProgress", "done", "blocked"]
ReviewActionType = Literal["created", "updated", "reviewed", "completed", "paused", "archived"]


def _normalize_text(value: object) -> object:
    if isinstance(value, str):
        normalized = value.strip()
        return normalized or None

    return value


class CareerGoalCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    target_role: str | None = Field(default=None, alias="targetRole", max_length=180)
    time_horizon: str = Field(default="12 months", alias="timeHorizon", min_length=1, max_length=80)
    status: GoalStatus = "active"
    notes: str | None = Field(default=None, max_length=3000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("title", "target_role", "time_horizon", "notes", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class CareerGoalUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    target_role: str | None = Field(default=None, alias="targetRole", max_length=180)
    time_horizon: str | None = Field(default=None, alias="timeHorizon", min_length=1, max_length=80)
    status: GoalStatus | None = None
    notes: str | None = Field(default=None, max_length=3000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("title", "target_role", "time_horizon", "notes", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class CareerRoadmapCreateRequest(BaseModel):
    goal_id: int = Field(alias="goalId", gt=0)
    title: str = Field(min_length=1, max_length=180)
    focus_area: str = Field(default="skills", alias="focusArea", min_length=1, max_length=120)
    status: RoadmapStatus = "planned"
    summary: str | None = Field(default=None, max_length=5000)
    sort_order: int = Field(default=0, alias="sortOrder", ge=0, le=999)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("title", "focus_area", "summary", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class CareerRoadmapUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    focus_area: str | None = Field(default=None, alias="focusArea", min_length=1, max_length=120)
    status: RoadmapStatus | None = None
    summary: str | None = Field(default=None, max_length=5000)
    sort_order: int | None = Field(default=None, alias="sortOrder", ge=0, le=999)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("title", "focus_area", "summary", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class CareerMilestoneCreateRequest(BaseModel):
    roadmap_id: int = Field(alias="roadmapId", gt=0)
    title: str = Field(min_length=1, max_length=180)
    due_date: str | None = Field(default=None, alias="dueDate", max_length=40)
    status: MilestoneStatus = "todo"
    success_metric: str | None = Field(default=None, alias="successMetric", max_length=240)
    notes: str | None = Field(default=None, max_length=3000)
    sort_order: int = Field(default=0, alias="sortOrder", ge=0, le=999)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("title", "due_date", "success_metric", "notes", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class CareerMilestoneUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    due_date: str | None = Field(default=None, alias="dueDate", max_length=40)
    status: MilestoneStatus | None = None
    success_metric: str | None = Field(default=None, alias="successMetric", max_length=240)
    notes: str | None = Field(default=None, max_length=3000)
    sort_order: int | None = Field(default=None, alias="sortOrder", ge=0, le=999)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("title", "due_date", "success_metric", "notes", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class CareerReviewHistoryCreateRequest(BaseModel):
    goal_id: int | None = Field(default=None, alias="goalId", gt=0)
    title: str = Field(min_length=1, max_length=180)
    action_type: ReviewActionType = Field(default="reviewed", alias="actionType")
    notes: str | None = Field(default=None, max_length=5000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("title", "notes", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class CareerGoalSummaryResponse(BaseModel):
    id: int
    title: str
    target_role: str | None = Field(serialization_alias="targetRole")
    time_horizon: str = Field(serialization_alias="timeHorizon")
    status: GoalStatus
    roadmap_count: int = Field(serialization_alias="roadmapCount")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class CareerGoalDetailResponse(CareerGoalSummaryResponse):
    notes: str | None


class CareerRoadmapSummaryResponse(BaseModel):
    id: int
    goal_id: int = Field(serialization_alias="goalId")
    goal_title: str = Field(serialization_alias="goalTitle")
    title: str
    focus_area: str = Field(serialization_alias="focusArea")
    status: RoadmapStatus
    milestone_count: int = Field(serialization_alias="milestoneCount")
    sort_order: int = Field(serialization_alias="sortOrder")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class CareerRoadmapDetailResponse(CareerRoadmapSummaryResponse):
    summary: str | None


class CareerMilestoneSummaryResponse(BaseModel):
    id: int
    roadmap_id: int = Field(serialization_alias="roadmapId")
    roadmap_title: str = Field(serialization_alias="roadmapTitle")
    title: str
    due_date: str | None = Field(serialization_alias="dueDate")
    status: MilestoneStatus
    success_metric: str | None = Field(serialization_alias="successMetric")
    sort_order: int = Field(serialization_alias="sortOrder")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class CareerMilestoneDetailResponse(CareerMilestoneSummaryResponse):
    notes: str | None


class CareerReviewHistorySummaryResponse(BaseModel):
    id: int
    goal_id: int | None = Field(serialization_alias="goalId")
    goal_title: str | None = Field(serialization_alias="goalTitle")
    title: str
    action_type: ReviewActionType = Field(serialization_alias="actionType")
    notes_preview: str | None = Field(serialization_alias="notesPreview")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class CareerDashboardResponse(BaseModel):
    goals: list[CareerGoalSummaryResponse]
    roadmaps: list[CareerRoadmapSummaryResponse]
    milestones: list[CareerMilestoneSummaryResponse]
    review_history: list[CareerReviewHistorySummaryResponse] = Field(serialization_alias="reviewHistory")
    active_goal_count: int = Field(serialization_alias="activeGoalCount")
    in_progress_roadmap_count: int = Field(serialization_alias="inProgressRoadmapCount")
    done_milestone_count: int = Field(serialization_alias="doneMilestoneCount")

    model_config = ConfigDict(from_attributes=True)
