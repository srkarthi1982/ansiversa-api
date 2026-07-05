from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

GoalStatus = Literal["active", "paused", "completed", "archived"]
GoalPriority = Literal["low", "medium", "high"]
MilestoneStatus = Literal["pending", "inProgress", "completed"]
CheckInMood = Literal["great", "good", "steady", "low", "blocked"]


def _normalize_text(value: object) -> object:
    if isinstance(value, str):
        normalized = value.strip()
        return normalized or None
    return value


class GoalCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    category: str | None = Field(default=None, max_length=80)
    description: str | None = Field(default=None, max_length=4000)
    target_date: str | None = Field(default=None, alias="targetDate", max_length=40)
    status: GoalStatus = "active"
    priority: GoalPriority = "medium"
    progress: int = Field(default=0, ge=0, le=100)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class GoalUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    category: str | None = Field(default=None, max_length=80)
    description: str | None = Field(default=None, max_length=4000)
    target_date: str | None = Field(default=None, alias="targetDate", max_length=40)
    status: GoalStatus | None = None
    priority: GoalPriority | None = None
    progress: int | None = Field(default=None, ge=0, le=100)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class GoalDuplicateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=180)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class MilestoneCreateRequest(BaseModel):
    goal_id: str = Field(alias="goalId", min_length=1, max_length=36)
    title: str = Field(min_length=1, max_length=180)
    target_date: str | None = Field(default=None, alias="targetDate", max_length=40)
    status: MilestoneStatus = "pending"
    sort_order: int = Field(default=0, alias="sortOrder", ge=0, le=10000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class MilestoneUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    target_date: str | None = Field(default=None, alias="targetDate", max_length=40)
    status: MilestoneStatus | None = None
    sort_order: int | None = Field(default=None, alias="sortOrder", ge=0, le=10000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class CheckInCreateRequest(BaseModel):
    goal_id: str = Field(alias="goalId", min_length=1, max_length=36)
    check_in_date: str = Field(alias="checkInDate", min_length=1, max_length=40)
    progress: int = Field(ge=0, le=100)
    note: str | None = Field(default=None, max_length=4000)
    mood: CheckInMood = "steady"

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class CheckInUpdateRequest(BaseModel):
    check_in_date: str | None = Field(default=None, alias="checkInDate", min_length=1, max_length=40)
    progress: int | None = Field(default=None, ge=0, le=100)
    note: str | None = Field(default=None, max_length=4000)
    mood: CheckInMood | None = None

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class GoalSummaryResponse(BaseModel):
    id: str
    title: str
    category: str | None
    description_preview: str | None = Field(serialization_alias="descriptionPreview")
    target_date: str | None = Field(serialization_alias="targetDate")
    status: GoalStatus
    priority: GoalPriority
    progress: int
    milestone_count: int = Field(serialization_alias="milestoneCount")
    completed_milestone_count: int = Field(serialization_alias="completedMilestoneCount")
    check_in_count: int = Field(serialization_alias="checkInCount")
    last_check_in_date: str | None = Field(serialization_alias="lastCheckInDate")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class MilestoneSummaryResponse(BaseModel):
    id: str
    goal_id: str = Field(serialization_alias="goalId")
    goal_title: str = Field(serialization_alias="goalTitle")
    title: str
    target_date: str | None = Field(serialization_alias="targetDate")
    status: MilestoneStatus
    sort_order: int = Field(serialization_alias="sortOrder")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class CheckInSummaryResponse(BaseModel):
    id: str
    goal_id: str = Field(serialization_alias="goalId")
    goal_title: str = Field(serialization_alias="goalTitle")
    check_in_date: str = Field(serialization_alias="checkInDate")
    progress: int
    mood: CheckInMood
    note_preview: str | None = Field(serialization_alias="notePreview")
    created_at: datetime = Field(serialization_alias="createdAt")


class GoalDetailResponse(GoalSummaryResponse):
    description: str | None
    milestones: list[MilestoneSummaryResponse]
    check_ins: list[CheckInSummaryResponse] = Field(serialization_alias="checkIns")


class MilestoneDetailResponse(MilestoneSummaryResponse):
    pass


class CheckInDetailResponse(CheckInSummaryResponse):
    note: str | None


class GoalTrackerDashboardResponse(BaseModel):
    goals: list[GoalSummaryResponse]
    milestones: list[MilestoneSummaryResponse]
    check_ins: list[CheckInSummaryResponse] = Field(serialization_alias="checkIns")
    active_goal_count: int = Field(serialization_alias="activeGoalCount")
    completed_goal_count: int = Field(serialization_alias="completedGoalCount")
    paused_goal_count: int = Field(serialization_alias="pausedGoalCount")
    average_progress: int = Field(serialization_alias="averageProgress")
    check_ins_this_month: int = Field(serialization_alias="checkInsThisMonth")
    high_priority_goal_count: int = Field(serialization_alias="highPriorityGoalCount")
    recent_check_ins: list[CheckInSummaryResponse] = Field(serialization_alias="recentCheckIns")
