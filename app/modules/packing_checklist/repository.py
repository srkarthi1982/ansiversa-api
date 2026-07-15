from sqlalchemy import asc, desc, func, select
from sqlalchemy.orm import Session, selectinload

from app.modules.packing_checklist.models import PackingCategory, PackingItem, PackingTripChecklist


def add(db: Session, record: object) -> None:
    db.add(record)


def delete_record(db: Session, record: object) -> None:
    db.delete(record)


def get_category(db: Session, category_id: str) -> PackingCategory | None:
    return db.get(PackingCategory, category_id)


def list_categories(db: Session, owner_id: str) -> list[PackingCategory]:
    statement = (
        select(PackingCategory)
        .where(PackingCategory.owner_id == owner_id)
        .order_by(asc(PackingCategory.sort_order), asc(PackingCategory.name))
    )
    return list(db.execute(statement).scalars().all())


def item_counts_by_category(db: Session, owner_id: str) -> dict[str, int]:
    statement = (
        select(PackingItem.category_id, func.count(PackingItem.id))
        .where(PackingItem.owner_id == owner_id)
        .group_by(PackingItem.category_id)
    )
    return {str(category_id): int(count) for category_id, count in db.execute(statement).all()}


def count_items_for_category(db: Session, owner_id: str, category_id: str) -> int:
    statement = select(func.count(PackingItem.id)).where(PackingItem.owner_id == owner_id, PackingItem.category_id == category_id)
    return int(db.execute(statement).scalar_one())


def get_checklist(db: Session, checklist_id: str) -> PackingTripChecklist | None:
    statement = (
        select(PackingTripChecklist)
        .options(selectinload(PackingTripChecklist.items).selectinload(PackingItem.category))
        .where(PackingTripChecklist.id == checklist_id)
    )
    return db.execute(statement).scalars().first()


def list_checklists(db: Session, owner_id: str) -> list[PackingTripChecklist]:
    statement = (
        select(PackingTripChecklist)
        .options(selectinload(PackingTripChecklist.items).selectinload(PackingItem.category))
        .where(PackingTripChecklist.owner_id == owner_id)
        .order_by(desc(PackingTripChecklist.updated_at), asc(PackingTripChecklist.title))
    )
    return list(db.execute(statement).scalars().all())


def get_item(db: Session, item_id: str) -> PackingItem | None:
    statement = select(PackingItem).options(selectinload(PackingItem.category), selectinload(PackingItem.checklist)).where(PackingItem.id == item_id)
    return db.execute(statement).scalars().first()
