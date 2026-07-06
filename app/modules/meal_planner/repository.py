from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import Select, select

from app.modules.meal_planner.models import MealPlan, MealPlanEntry, Recipe


def get_recipe(db: Session, recipe_id: str) -> Recipe | None:
    return db.get(Recipe, recipe_id)


def get_meal_plan(db: Session, plan_id: str) -> MealPlan | None:
    return db.get(MealPlan, plan_id)


def get_meal_plan_entry(db: Session, entry_id: str) -> MealPlanEntry | None:
    return db.get(MealPlanEntry, entry_id)


def _paginate(statement: Select[tuple[object]], page: int, page_size: int) -> Select[tuple[object]]:
    return statement.offset((page - 1) * page_size).limit(page_size)


def _recipe_search(statement: Select[tuple[Recipe]], query: str | None) -> Select[tuple[Recipe]]:
    if not query:
        return statement
    pattern = f"%{query.strip()}%"
    return statement.where(
        or_(
            Recipe.title.ilike(pattern),
            Recipe.category.ilike(pattern),
            Recipe.ingredients.ilike(pattern),
            Recipe.notes.ilike(pattern),
        )
    )


def _plan_search(statement: Select[tuple[MealPlan]], query: str | None) -> Select[tuple[MealPlan]]:
    if not query:
        return statement
    pattern = f"%{query.strip()}%"
    return statement.where(or_(MealPlan.title.ilike(pattern), MealPlan.notes.ilike(pattern)))


def _entry_search(statement: Select[tuple[MealPlanEntry]], query: str | None) -> Select[tuple[MealPlanEntry]]:
    if not query:
        return statement
    pattern = f"%{query.strip()}%"
    return statement.where(or_(MealPlanEntry.title.ilike(pattern), MealPlanEntry.notes.ilike(pattern)))


def list_recipes(
    db: Session,
    owner_id: str,
    *,
    query: str | None = None,
    category: str | None = None,
    sort: str = "updatedAt",
    direction: str = "desc",
    page: int = 1,
    page_size: int = 100,
) -> tuple[list[Recipe], int]:
    statement = select(Recipe).options(joinedload(Recipe.entries)).where(Recipe.owner_id == owner_id)
    if category:
        statement = statement.where(Recipe.category == category)
    statement = _recipe_search(statement, query)
    total = db.scalar(select(func.count()).select_from(statement.order_by(None).subquery())) or 0
    sort_column = Recipe.title if sort == "title" else Recipe.updated_at
    statement = statement.order_by(sort_column.asc() if direction == "asc" else sort_column.desc(), Recipe.title.asc())
    return list(db.execute(_paginate(statement, page, page_size)).unique().scalars().all()), total


def count_recipes(db: Session, owner_id: str) -> int:
    return db.scalar(select(func.count()).select_from(Recipe).where(Recipe.owner_id == owner_id)) or 0


def list_meal_plans(
    db: Session,
    owner_id: str,
    *,
    query: str | None = None,
    status: str | None = None,
    sort: str = "weekStartDate",
    direction: str = "desc",
    page: int = 1,
    page_size: int = 100,
) -> tuple[list[MealPlan], int]:
    statement = select(MealPlan).options(joinedload(MealPlan.entries)).where(MealPlan.owner_id == owner_id)
    if status:
        statement = statement.where(MealPlan.status == status)
    statement = _plan_search(statement, query)
    total = db.scalar(select(func.count()).select_from(statement.order_by(None).subquery())) or 0
    sort_column = MealPlan.title if sort == "title" else MealPlan.updated_at if sort == "updatedAt" else MealPlan.week_start_date
    statement = statement.order_by(sort_column.asc() if direction == "asc" else sort_column.desc(), MealPlan.title.asc())
    return list(db.execute(_paginate(statement, page, page_size)).unique().scalars().all()), total


def count_meal_plans(db: Session, owner_id: str, *, status: str | None = None) -> int:
    statement = select(func.count()).select_from(MealPlan).where(MealPlan.owner_id == owner_id)
    if status:
        statement = statement.where(MealPlan.status == status)
    return db.scalar(statement) or 0


def list_meal_plan_entries(
    db: Session,
    owner_id: str,
    *,
    query: str | None = None,
    plan_id: str | None = None,
    meal_type: str | None = None,
    week_start: str | None = None,
    sort: str = "entryDate",
    direction: str = "asc",
    page: int = 1,
    page_size: int = 100,
) -> tuple[list[MealPlanEntry], int]:
    statement = (
        select(MealPlanEntry)
        .options(joinedload(MealPlanEntry.plan), joinedload(MealPlanEntry.recipe))
        .where(MealPlanEntry.owner_id == owner_id)
    )
    if plan_id:
        statement = statement.where(MealPlanEntry.plan_id == plan_id)
    if meal_type:
        statement = statement.where(MealPlanEntry.meal_type == meal_type)
    if week_start:
        statement = statement.where(MealPlanEntry.entry_date >= week_start)
    statement = _entry_search(statement, query)
    total = db.scalar(select(func.count()).select_from(statement.order_by(None).subquery())) or 0
    sort_column = MealPlanEntry.updated_at if sort == "updatedAt" else MealPlanEntry.entry_date
    statement = statement.order_by(
        sort_column.asc() if direction == "asc" else sort_column.desc(),
        MealPlanEntry.meal_type.asc(),
        MealPlanEntry.sort_order.asc(),
    )
    return list(db.execute(_paginate(statement, page, page_size)).scalars().all()), total


def count_meal_plan_entries(
    db: Session,
    owner_id: str,
    *,
    entry_date_from: str | None = None,
    entry_date_before: str | None = None,
) -> int:
    statement = select(func.count()).select_from(MealPlanEntry).where(MealPlanEntry.owner_id == owner_id)
    if entry_date_from:
        statement = statement.where(MealPlanEntry.entry_date >= entry_date_from)
    if entry_date_before:
        statement = statement.where(MealPlanEntry.entry_date < entry_date_before)
    return db.scalar(statement) or 0


def add(db: Session, record: object) -> None:
    db.add(record)


def delete_record(db: Session, record: object) -> None:
    db.delete(record)
