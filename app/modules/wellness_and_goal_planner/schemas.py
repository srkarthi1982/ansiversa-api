from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

GoalStatus = Literal["active", "paused", "completed", "archived"]
GoalPriority = Literal["low", "medium", "high"]
ReflectionMood = Literal["great", "good", "steady", "low", "stressed"]


def _normalize_text(value: object) -> object:
    if isinstance(value, str):
        normalized = value.strip()
        return normalized or None
    return value


class WellnessAreaCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=2000)
    color: str = Field(default="#2f6f73", min_length=3, max_length=40)
    icon: str | None = Field(default=None, max_length=60)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class WellnessAreaUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=2000)
    color: str | None = Field(default=None, min_length=3, max_length=40)
    icon: str | None = Field(default=None, max_length=60)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class WellnessGoalCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    area_id: str | None = Field(default=None, alias="areaId")
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


class WellnessGoalUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    area_id: str | None = Field(default=None, alias="areaId")
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


class WellnessReflectionCreateRequest(BaseModel):
    reflection_date: str = Field(alias="reflectionDate", min_length=1, max_length=40)
    goal_id: str | None = Field(default=None, alias="goalId")
    reflection: str = Field(min_length=1, max_length=4000)
    mood: ReflectionMood = "steady"
    notes: str | None = Field(default=None, max_length=3000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class WellnessReflectionUpdateRequest(BaseModel):
    reflection_date: str | None = Field(default=None, alias="reflectionDate", min_length=1, max_length=40)
    goal_id: str | None = Field(default=None, alias="goalId")
    reflection: str | None = Field(default=None, min_length=1, max_length=4000)
    mood: ReflectionMood | None = None
    notes: str | None = Field(default=None, max_length=3000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class WellnessAreaSummaryResponse(BaseModel):
    id: str
    name: str
    description_preview: str | None = Field(serialization_alias="descriptionPreview")
    color: str
    icon: str | None
    goal_count: int = Field(serialization_alias="goalCount")
    active_goal_count: int = Field(serialization_alias="activeGoalCount")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class WellnessAreaDetailResponse(WellnessAreaSummaryResponse):
    description: str | None


class WellnessGoalSummaryResponse(BaseModel):
    id: str
    title: str
    area_id: str | None = Field(serialization_alias="areaId")
    area_name: str | None = Field(serialization_alias="areaName")
    area_color: str | None = Field(serialization_alias="areaColor")
    description_preview: str | None = Field(serialization_alias="descriptionPreview")
    target_date: str | None = Field(serialization_alias="targetDate")
    status: GoalStatus
    priority: GoalPriority
    progress: int
    reflection_count: int = Field(serialization_alias="reflectionCount")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class WellnessGoalDetailResponse(WellnessGoalSummaryResponse):
    description: str | None


class WellnessReflectionSummaryResponse(BaseModel):
    id: str
    goal_id: str | None = Field(serialization_alias="goalId")
    goal_title: str | None = Field(serialization_alias="goalTitle")
    reflection_date: str = Field(serialization_alias="reflectionDate")
    reflection_preview: str = Field(serialization_alias="reflectionPreview")
    mood: ReflectionMood
    notes_preview: str | None = Field(serialization_alias="notesPreview")
    created_at: datetime = Field(serialization_alias="createdAt")


class WellnessReflectionDetailResponse(WellnessReflectionSummaryResponse):
    reflection: str
    notes: str | None


class WellnessDashboardResponse(BaseModel):
    areas: list[WellnessAreaSummaryResponse]
    goals: list[WellnessGoalSummaryResponse]
    reflections: list[WellnessReflectionSummaryResponse]
    active_goal_count: int = Field(serialization_alias="activeGoalCount")
    completed_goal_count: int = Field(serialization_alias="completedGoalCount")
    wellness_area_count: int = Field(serialization_alias="wellnessAreaCount")
    reflections_this_month: int = Field(serialization_alias="reflectionsThisMonth")
    average_progress: int = Field(serialization_alias="averageProgress")
    recent_reflections: list[WellnessReflectionSummaryResponse] = Field(serialization_alias="recentReflections")
