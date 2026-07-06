from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

MealPlanStatus = Literal["draft", "active", "completed", "archived"]
MealType = Literal["breakfast", "lunch", "dinner", "snack"]
SortDirection = Literal["asc", "desc"]


def _normalize_text(value: object) -> object:
    if isinstance(value, str):
        normalized = value.strip()
        return normalized or None
    return value


class RecipeCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    category: str | None = Field(default=None, max_length=80)
    prep_minutes: int | None = Field(default=None, alias="prepMinutes", ge=0, le=1440)
    cook_minutes: int | None = Field(default=None, alias="cookMinutes", ge=0, le=1440)
    servings: int | None = Field(default=None, ge=1, le=100)
    ingredients: str | None = Field(default=None, max_length=8000)
    instructions: str | None = Field(default=None, max_length=8000)
    notes: str | None = Field(default=None, max_length=4000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class RecipeUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    category: str | None = Field(default=None, max_length=80)
    prep_minutes: int | None = Field(default=None, alias="prepMinutes", ge=0, le=1440)
    cook_minutes: int | None = Field(default=None, alias="cookMinutes", ge=0, le=1440)
    servings: int | None = Field(default=None, ge=1, le=100)
    ingredients: str | None = Field(default=None, max_length=8000)
    instructions: str | None = Field(default=None, max_length=8000)
    notes: str | None = Field(default=None, max_length=4000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class MealPlanCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    week_start_date: str = Field(alias="weekStartDate", min_length=1, max_length=40)
    status: MealPlanStatus = "draft"
    notes: str | None = Field(default=None, max_length=4000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class MealPlanUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    week_start_date: str | None = Field(default=None, alias="weekStartDate", min_length=1, max_length=40)
    status: MealPlanStatus | None = None
    notes: str | None = Field(default=None, max_length=4000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class MealPlanEntryCreateRequest(BaseModel):
    plan_id: str = Field(alias="mealPlanId", min_length=1, max_length=36)
    recipe_id: str | None = Field(default=None, alias="recipeId", max_length=36)
    entry_date: str = Field(alias="entryDate", min_length=1, max_length=40)
    meal_type: MealType = Field(default="dinner", alias="mealType")
    title: str | None = Field(default=None, max_length=180)
    notes: str | None = Field(default=None, max_length=4000)
    sort_order: int = Field(default=0, alias="sortOrder", ge=0, le=10000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class MealPlanEntryUpdateRequest(BaseModel):
    recipe_id: str | None = Field(default=None, alias="recipeId", max_length=36)
    entry_date: str | None = Field(default=None, alias="entryDate", min_length=1, max_length=40)
    meal_type: MealType | None = Field(default=None, alias="mealType")
    title: str | None = Field(default=None, max_length=180)
    notes: str | None = Field(default=None, max_length=4000)
    sort_order: int | None = Field(default=None, alias="sortOrder", ge=0, le=10000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class RecipeSummaryResponse(BaseModel):
    id: str
    title: str
    category: str | None
    prep_minutes: int | None = Field(serialization_alias="prepMinutes")
    cook_minutes: int | None = Field(serialization_alias="cookMinutes")
    servings: int | None
    ingredients_preview: str | None = Field(serialization_alias="ingredientsPreview")
    notes_preview: str | None = Field(serialization_alias="notesPreview")
    entry_count: int = Field(serialization_alias="entryCount")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class RecipeDetailResponse(RecipeSummaryResponse):
    ingredients: str | None
    instructions: str | None
    notes: str | None


class MealPlanEntrySummaryResponse(BaseModel):
    id: str
    plan_id: str = Field(serialization_alias="mealPlanId")
    plan_title: str = Field(serialization_alias="mealPlanTitle")
    recipe_id: str | None = Field(serialization_alias="recipeId")
    recipe_title: str | None = Field(serialization_alias="recipeTitle")
    entry_date: str = Field(serialization_alias="entryDate")
    meal_type: MealType = Field(serialization_alias="mealType")
    title: str | None
    display_title: str = Field(serialization_alias="displayTitle")
    notes_preview: str | None = Field(serialization_alias="notesPreview")
    sort_order: int = Field(serialization_alias="sortOrder")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class MealPlanEntryDetailResponse(MealPlanEntrySummaryResponse):
    notes: str | None


class MealPlanSummaryResponse(BaseModel):
    id: str
    title: str
    week_start_date: str = Field(serialization_alias="weekStartDate")
    status: MealPlanStatus
    notes_preview: str | None = Field(serialization_alias="notesPreview")
    entry_count: int = Field(serialization_alias="entryCount")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class MealPlanDetailResponse(MealPlanSummaryResponse):
    notes: str | None
    entries: list[MealPlanEntrySummaryResponse]


class MealPlannerDashboardResponse(BaseModel):
    recipes: list[RecipeSummaryResponse]
    meal_plans: list[MealPlanSummaryResponse] = Field(serialization_alias="mealPlans")
    entries: list[MealPlanEntrySummaryResponse]
    recipe_count: int = Field(serialization_alias="recipeCount")
    active_plan_count: int = Field(serialization_alias="activePlanCount")
    planned_meal_count: int = Field(serialization_alias="plannedMealCount")
    this_week_entry_count: int = Field(serialization_alias="thisWeekEntryCount")
    recent_entries: list[MealPlanEntrySummaryResponse] = Field(serialization_alias="recentEntries")


class PaginatedRecipeResponse(BaseModel):
    items: list[RecipeSummaryResponse]
    page: int
    page_size: int = Field(serialization_alias="pageSize")
    total: int


class PaginatedMealPlanResponse(BaseModel):
    items: list[MealPlanSummaryResponse]
    page: int
    page_size: int = Field(serialization_alias="pageSize")
    total: int


class PaginatedMealPlanEntryResponse(BaseModel):
    items: list[MealPlanEntrySummaryResponse]
    page: int
    page_size: int = Field(serialization_alias="pageSize")
    total: int
