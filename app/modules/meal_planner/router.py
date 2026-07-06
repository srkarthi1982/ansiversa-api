from typing import Literal

from fastapi import APIRouter, Query, Response, status

from app.modules.meal_planner import service
from app.modules.meal_planner.dependencies import CurrentMealPlannerUser, MealPlannerDB
from app.modules.meal_planner.schemas import (
    MealPlanCreateRequest,
    MealPlanDetailResponse,
    MealPlanEntryCreateRequest,
    MealPlanEntryDetailResponse,
    MealPlanEntryUpdateRequest,
    MealPlannerDashboardResponse,
    MealPlanUpdateRequest,
    PaginatedMealPlanEntryResponse,
    PaginatedMealPlanResponse,
    PaginatedRecipeResponse,
    RecipeCreateRequest,
    RecipeDetailResponse,
    RecipeUpdateRequest,
)

router = APIRouter()


@router.get("/dashboard", response_model=MealPlannerDashboardResponse)
def get_dashboard(db: MealPlannerDB, current_user: CurrentMealPlannerUser):
    return service.get_dashboard(db, current_user)


@router.get("/recipes", response_model=PaginatedRecipeResponse)
def list_recipes(
    db: MealPlannerDB,
    current_user: CurrentMealPlannerUser,
    q: str | None = Query(default=None, max_length=120),
    category: str | None = Query(default=None, max_length=80),
    sort: Literal["title", "updatedAt"] = "updatedAt",
    direction: Literal["asc", "desc"] = "desc",
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=100, alias="pageSize", ge=1, le=200),
):
    return service.list_recipes(
        db,
        current_user,
        query=q,
        category=category,
        sort=sort,
        direction=direction,
        page=page,
        page_size=page_size,
    )


@router.post("/recipes", response_model=RecipeDetailResponse, status_code=status.HTTP_201_CREATED)
def create_recipe(payload: RecipeCreateRequest, db: MealPlannerDB, current_user: CurrentMealPlannerUser):
    return service.create_recipe(db, current_user, payload)


@router.get("/recipes/{recipe_id}", response_model=RecipeDetailResponse)
def get_recipe(recipe_id: str, db: MealPlannerDB, current_user: CurrentMealPlannerUser):
    return service.get_recipe(db, current_user, recipe_id)


@router.put("/recipes/{recipe_id}", response_model=RecipeDetailResponse)
def update_recipe(
    recipe_id: str,
    payload: RecipeUpdateRequest,
    db: MealPlannerDB,
    current_user: CurrentMealPlannerUser,
):
    return service.update_recipe(db, current_user, recipe_id, payload)


@router.delete("/recipes/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recipe(recipe_id: str, db: MealPlannerDB, current_user: CurrentMealPlannerUser):
    service.delete_recipe(db, current_user, recipe_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/meal-plans", response_model=PaginatedMealPlanResponse)
def list_meal_plans(
    db: MealPlannerDB,
    current_user: CurrentMealPlannerUser,
    q: str | None = Query(default=None, max_length=120),
    plan_status: str | None = Query(default=None, alias="status", max_length=40),
    sort: Literal["title", "weekStartDate", "updatedAt"] = "weekStartDate",
    direction: Literal["asc", "desc"] = "desc",
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=100, alias="pageSize", ge=1, le=200),
):
    return service.list_meal_plans(
        db,
        current_user,
        query=q,
        plan_status=plan_status,
        sort=sort,
        direction=direction,
        page=page,
        page_size=page_size,
    )


@router.post("/meal-plans", response_model=MealPlanDetailResponse, status_code=status.HTTP_201_CREATED)
def create_meal_plan(payload: MealPlanCreateRequest, db: MealPlannerDB, current_user: CurrentMealPlannerUser):
    return service.create_meal_plan(db, current_user, payload)


@router.get("/meal-plans/{plan_id}", response_model=MealPlanDetailResponse)
def get_meal_plan(plan_id: str, db: MealPlannerDB, current_user: CurrentMealPlannerUser):
    return service.get_meal_plan(db, current_user, plan_id)


@router.put("/meal-plans/{plan_id}", response_model=MealPlanDetailResponse)
def update_meal_plan(
    plan_id: str,
    payload: MealPlanUpdateRequest,
    db: MealPlannerDB,
    current_user: CurrentMealPlannerUser,
):
    return service.update_meal_plan(db, current_user, plan_id, payload)


@router.delete("/meal-plans/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_meal_plan(plan_id: str, db: MealPlannerDB, current_user: CurrentMealPlannerUser):
    service.delete_meal_plan(db, current_user, plan_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/entries", response_model=PaginatedMealPlanEntryResponse)
def list_entries(
    db: MealPlannerDB,
    current_user: CurrentMealPlannerUser,
    q: str | None = Query(default=None, max_length=120),
    plan_id: str | None = Query(default=None, alias="mealPlanId", max_length=36),
    meal_type: str | None = Query(default=None, alias="mealType", max_length=40),
    week_start: str | None = Query(default=None, alias="weekStart", max_length=40),
    sort: Literal["entryDate", "updatedAt"] = "entryDate",
    direction: Literal["asc", "desc"] = "asc",
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=100, alias="pageSize", ge=1, le=200),
):
    return service.list_entries(
        db,
        current_user,
        query=q,
        plan_id=plan_id,
        meal_type=meal_type,
        week_start=week_start,
        sort=sort,
        direction=direction,
        page=page,
        page_size=page_size,
    )


@router.post("/entries", response_model=MealPlanEntryDetailResponse, status_code=status.HTTP_201_CREATED)
def create_entry(payload: MealPlanEntryCreateRequest, db: MealPlannerDB, current_user: CurrentMealPlannerUser):
    return service.create_entry(db, current_user, payload)


@router.get("/entries/{entry_id}", response_model=MealPlanEntryDetailResponse)
def get_entry(entry_id: str, db: MealPlannerDB, current_user: CurrentMealPlannerUser):
    return service.get_entry(db, current_user, entry_id)


@router.put("/entries/{entry_id}", response_model=MealPlanEntryDetailResponse)
def update_entry(
    entry_id: str,
    payload: MealPlanEntryUpdateRequest,
    db: MealPlannerDB,
    current_user: CurrentMealPlannerUser,
):
    return service.update_entry(db, current_user, entry_id, payload)


@router.delete("/entries/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_entry(entry_id: str, db: MealPlannerDB, current_user: CurrentMealPlannerUser):
    service.delete_entry(db, current_user, entry_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
