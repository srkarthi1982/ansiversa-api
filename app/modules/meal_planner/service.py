from datetime import date, timedelta

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.meal_planner import repository
from app.modules.meal_planner.models import MealPlan, MealPlanEntry, Recipe
from app.modules.meal_planner.schemas import (
    MealPlanCreateRequest,
    MealPlanDetailResponse,
    MealPlanEntryCreateRequest,
    MealPlanEntryDetailResponse,
    MealPlanEntrySummaryResponse,
    MealPlannerDashboardResponse,
    MealPlanSummaryResponse,
    MealPlanUpdateRequest,
    MealPlanEntryUpdateRequest,
    PaginatedMealPlanEntryResponse,
    PaginatedMealPlanResponse,
    PaginatedRecipeResponse,
    RecipeCreateRequest,
    RecipeDetailResponse,
    RecipeSummaryResponse,
    RecipeUpdateRequest,
)

PREVIEW_LENGTH = 220


def _preview(value: str | None) -> str | None:
    if not value:
        return None
    if len(value) <= PREVIEW_LENGTH:
        return value
    return f"{value[:PREVIEW_LENGTH].rstrip()}..."


def _not_found(detail: str) -> None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def _get_owned_recipe(db: Session, user: User, recipe_id: str) -> Recipe:
    recipe = repository.get_recipe(db, recipe_id)
    if not recipe or recipe.owner_id != user.id:
        _not_found("Recipe was not found.")
    return recipe


def _get_owned_meal_plan(db: Session, user: User, plan_id: str) -> MealPlan:
    plan = repository.get_meal_plan(db, plan_id)
    if not plan or plan.owner_id != user.id:
        _not_found("Meal plan was not found.")
    return plan


def _get_owned_entry(db: Session, user: User, entry_id: str) -> MealPlanEntry:
    entry = repository.get_meal_plan_entry(db, entry_id)
    if not entry or entry.owner_id != user.id:
        _not_found("Meal plan entry was not found.")
    return entry


def _recipe_summary_response(recipe: Recipe) -> RecipeSummaryResponse:
    return RecipeSummaryResponse(
        id=recipe.id,
        title=recipe.title,
        category=recipe.category,
        prep_minutes=recipe.prep_minutes,
        cook_minutes=recipe.cook_minutes,
        servings=recipe.servings,
        ingredients_preview=_preview(recipe.ingredients),
        notes_preview=_preview(recipe.notes),
        entry_count=len(recipe.entries),
        created_at=recipe.created_at,
        updated_at=recipe.updated_at,
    )


def _recipe_detail_response(recipe: Recipe) -> RecipeDetailResponse:
    return RecipeDetailResponse(
        **_recipe_summary_response(recipe).model_dump(),
        ingredients=recipe.ingredients,
        instructions=recipe.instructions,
        notes=recipe.notes,
    )


def _entry_display_title(entry: MealPlanEntry) -> str:
    if entry.title:
        return entry.title
    if entry.recipe:
        return entry.recipe.title
    return "Untitled meal"


def _entry_summary_response(entry: MealPlanEntry) -> MealPlanEntrySummaryResponse:
    return MealPlanEntrySummaryResponse(
        id=entry.id,
        plan_id=entry.plan_id,
        plan_title=entry.plan.title,
        recipe_id=entry.recipe_id,
        recipe_title=entry.recipe.title if entry.recipe else None,
        entry_date=entry.entry_date,
        meal_type=entry.meal_type,
        title=entry.title,
        display_title=_entry_display_title(entry),
        notes_preview=_preview(entry.notes),
        sort_order=entry.sort_order,
        created_at=entry.created_at,
        updated_at=entry.updated_at,
    )


def _entry_detail_response(entry: MealPlanEntry) -> MealPlanEntryDetailResponse:
    return MealPlanEntryDetailResponse(**_entry_summary_response(entry).model_dump(), notes=entry.notes)


def _plan_summary_response(plan: MealPlan) -> MealPlanSummaryResponse:
    return MealPlanSummaryResponse(
        id=plan.id,
        title=plan.title,
        week_start_date=plan.week_start_date,
        status=plan.status,
        notes_preview=_preview(plan.notes),
        entry_count=len(plan.entries),
        created_at=plan.created_at,
        updated_at=plan.updated_at,
    )


def _plan_detail_response(plan: MealPlan) -> MealPlanDetailResponse:
    entries = sorted(plan.entries, key=lambda item: (item.entry_date, item.meal_type, item.sort_order))
    return MealPlanDetailResponse(
        **_plan_summary_response(plan).model_dump(),
        notes=plan.notes,
        entries=[_entry_summary_response(entry) for entry in entries],
    )


def _current_week_range() -> tuple[str, str]:
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    return monday.isoformat(), (monday + timedelta(days=7)).isoformat()


def _validate_entry_meal(data: dict[str, object]) -> None:
    recipe_id = data.get("recipe_id")
    title = data.get("title")
    if recipe_id or (isinstance(title, str) and title.strip()):
        return
    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="Meal plan entry requires a recipeId or custom title.",
    )


def list_recipes(
    db: Session,
    user: User,
    *,
    query: str | None,
    category: str | None,
    sort: str,
    direction: str,
    page: int,
    page_size: int,
) -> PaginatedRecipeResponse:
    recipes, total = repository.list_recipes(
        db,
        user.id,
        query=query,
        category=category,
        sort=sort,
        direction=direction,
        page=page,
        page_size=page_size,
    )
    return PaginatedRecipeResponse(
        items=[_recipe_summary_response(recipe) for recipe in recipes],
        page=page,
        page_size=page_size,
        total=total,
    )


def create_recipe(db: Session, user: User, payload: RecipeCreateRequest) -> RecipeDetailResponse:
    recipe = Recipe(owner_id=user.id, **payload.model_dump())
    repository.add(db, recipe)
    db.commit()
    db.refresh(recipe)
    return _recipe_detail_response(recipe)


def get_recipe(db: Session, user: User, recipe_id: str) -> RecipeDetailResponse:
    return _recipe_detail_response(_get_owned_recipe(db, user, recipe_id))


def update_recipe(db: Session, user: User, recipe_id: str, payload: RecipeUpdateRequest) -> RecipeDetailResponse:
    recipe = _get_owned_recipe(db, user, recipe_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(recipe, field, value)
    db.commit()
    db.refresh(recipe)
    return _recipe_detail_response(recipe)


def delete_recipe(db: Session, user: User, recipe_id: str) -> None:
    recipe = _get_owned_recipe(db, user, recipe_id)
    for entry in recipe.entries:
        entry.recipe_id = None
    repository.delete_record(db, recipe)
    db.commit()


def list_meal_plans(
    db: Session,
    user: User,
    *,
    query: str | None,
    plan_status: str | None,
    sort: str,
    direction: str,
    page: int,
    page_size: int,
) -> PaginatedMealPlanResponse:
    plans, total = repository.list_meal_plans(
        db,
        user.id,
        query=query,
        status=plan_status,
        sort=sort,
        direction=direction,
        page=page,
        page_size=page_size,
    )
    return PaginatedMealPlanResponse(
        items=[_plan_summary_response(plan) for plan in plans],
        page=page,
        page_size=page_size,
        total=total,
    )


def create_meal_plan(db: Session, user: User, payload: MealPlanCreateRequest) -> MealPlanDetailResponse:
    plan = MealPlan(owner_id=user.id, **payload.model_dump())
    repository.add(db, plan)
    db.commit()
    db.refresh(plan)
    return _plan_detail_response(plan)


def get_meal_plan(db: Session, user: User, plan_id: str) -> MealPlanDetailResponse:
    return _plan_detail_response(_get_owned_meal_plan(db, user, plan_id))


def update_meal_plan(db: Session, user: User, plan_id: str, payload: MealPlanUpdateRequest) -> MealPlanDetailResponse:
    plan = _get_owned_meal_plan(db, user, plan_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(plan, field, value)
    db.commit()
    db.refresh(plan)
    return _plan_detail_response(plan)


def delete_meal_plan(db: Session, user: User, plan_id: str) -> None:
    plan = _get_owned_meal_plan(db, user, plan_id)
    repository.delete_record(db, plan)
    db.commit()


def list_entries(
    db: Session,
    user: User,
    *,
    query: str | None,
    plan_id: str | None,
    meal_type: str | None,
    week_start: str | None,
    sort: str,
    direction: str,
    page: int,
    page_size: int,
) -> PaginatedMealPlanEntryResponse:
    if plan_id:
        _get_owned_meal_plan(db, user, plan_id)
    entries, total = repository.list_meal_plan_entries(
        db,
        user.id,
        query=query,
        plan_id=plan_id,
        meal_type=meal_type,
        week_start=week_start,
        sort=sort,
        direction=direction,
        page=page,
        page_size=page_size,
    )
    return PaginatedMealPlanEntryResponse(
        items=[_entry_summary_response(entry) for entry in entries],
        page=page,
        page_size=page_size,
        total=total,
    )


def create_entry(db: Session, user: User, payload: MealPlanEntryCreateRequest) -> MealPlanEntryDetailResponse:
    data = payload.model_dump()
    _validate_entry_meal(data)
    _get_owned_meal_plan(db, user, data["plan_id"])
    if data.get("recipe_id"):
        _get_owned_recipe(db, user, data["recipe_id"])
    entry = MealPlanEntry(owner_id=user.id, **data)
    repository.add(db, entry)
    db.commit()
    db.refresh(entry)
    return _entry_detail_response(entry)


def get_entry(db: Session, user: User, entry_id: str) -> MealPlanEntryDetailResponse:
    return _entry_detail_response(_get_owned_entry(db, user, entry_id))


def update_entry(
    db: Session,
    user: User,
    entry_id: str,
    payload: MealPlanEntryUpdateRequest,
) -> MealPlanEntryDetailResponse:
    entry = _get_owned_entry(db, user, entry_id)
    data = payload.model_dump(exclude_unset=True)
    next_data = {"recipe_id": entry.recipe_id, "title": entry.title, **data}
    _validate_entry_meal(next_data)
    if data.get("recipe_id"):
        _get_owned_recipe(db, user, data["recipe_id"])
    for field, value in data.items():
        setattr(entry, field, value)
    db.commit()
    db.refresh(entry)
    return _entry_detail_response(entry)


def delete_entry(db: Session, user: User, entry_id: str) -> None:
    entry = _get_owned_entry(db, user, entry_id)
    repository.delete_record(db, entry)
    db.commit()


def get_dashboard(db: Session, user: User) -> MealPlannerDashboardResponse:
    recipes, _ = repository.list_recipes(db, user.id, page_size=200)
    plans, _ = repository.list_meal_plans(db, user.id, page_size=100)
    entries, _ = repository.list_meal_plan_entries(db, user.id, page_size=200)
    recent_entries, _ = repository.list_meal_plan_entries(db, user.id, sort="updatedAt", direction="desc", page_size=5)
    week_start, week_end = _current_week_range()
    return MealPlannerDashboardResponse(
        recipes=[_recipe_summary_response(recipe) for recipe in recipes],
        meal_plans=[_plan_summary_response(plan) for plan in plans],
        entries=[_entry_summary_response(entry) for entry in entries],
        recipe_count=repository.count_recipes(db, user.id),
        active_plan_count=repository.count_meal_plans(db, user.id, status="active"),
        planned_meal_count=repository.count_meal_plan_entries(db, user.id),
        this_week_entry_count=repository.count_meal_plan_entries(
            db,
            user.id,
            entry_date_from=week_start,
            entry_date_before=week_end,
        ),
        recent_entries=[_entry_summary_response(entry) for entry in recent_entries],
    )
