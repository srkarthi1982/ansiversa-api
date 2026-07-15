from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.modules.home_maintenance_planner.models import MaintenanceArea, MaintenanceCategory, MaintenanceTask, MaintenanceTaskCompletion


def add(db: Session, item):
    db.add(item)
    return item


def delete_record(db: Session, item) -> None:
    db.delete(item)


def list_areas(db: Session, owner_id: str) -> list[MaintenanceArea]:
    return list(db.scalars(select(MaintenanceArea).where(MaintenanceArea.owner_id == owner_id).order_by(MaintenanceArea.sort_order, MaintenanceArea.name)))


def get_area(db: Session, item_id: str) -> MaintenanceArea | None:
    return db.get(MaintenanceArea, item_id)


def list_categories(db: Session, owner_id: str) -> list[MaintenanceCategory]:
    return list(db.scalars(select(MaintenanceCategory).where(MaintenanceCategory.owner_id == owner_id).order_by(MaintenanceCategory.sort_order, MaintenanceCategory.name)))


def get_category(db: Session, item_id: str) -> MaintenanceCategory | None:
    return db.get(MaintenanceCategory, item_id)


def list_tasks(db: Session, owner_id: str) -> list[MaintenanceTask]:
    result = db.execute(select(MaintenanceTask).options(joinedload(MaintenanceTask.area), joinedload(MaintenanceTask.category), joinedload(MaintenanceTask.completions)).where(MaintenanceTask.owner_id == owner_id).order_by(MaintenanceTask.due_date, MaintenanceTask.title))
    return list(result.unique().scalars())


def get_task(db: Session, task_id: str) -> MaintenanceTask | None:
    result = db.execute(select(MaintenanceTask).options(joinedload(MaintenanceTask.area), joinedload(MaintenanceTask.category), joinedload(MaintenanceTask.completions)).where(MaintenanceTask.id == task_id))
    return result.unique().scalars().first()


def count_tasks_for_area(db: Session, owner_id: str, area_id: str) -> int:
    return db.scalar(select(func.count()).select_from(MaintenanceTask).where(MaintenanceTask.owner_id == owner_id, MaintenanceTask.area_id == area_id)) or 0


def count_tasks_for_category(db: Session, owner_id: str, category_id: str) -> int:
    return db.scalar(select(func.count()).select_from(MaintenanceTask).where(MaintenanceTask.owner_id == owner_id, MaintenanceTask.category_id == category_id)) or 0


def task_counts_by_area(db: Session, owner_id: str) -> dict[str, int]:
    rows = db.execute(select(MaintenanceTask.area_id, func.count()).where(MaintenanceTask.owner_id == owner_id).group_by(MaintenanceTask.area_id))
    return {row[0]: row[1] for row in rows}


def task_counts_by_category(db: Session, owner_id: str) -> dict[str, int]:
    rows = db.execute(select(MaintenanceTask.category_id, func.count()).where(MaintenanceTask.owner_id == owner_id).group_by(MaintenanceTask.category_id))
    return {row[0]: row[1] for row in rows}


def list_completions(db: Session, owner_id: str) -> list[MaintenanceTaskCompletion]:
    return list(db.scalars(select(MaintenanceTaskCompletion).where(MaintenanceTaskCompletion.owner_id == owner_id).order_by(MaintenanceTaskCompletion.completed_at.desc())))

