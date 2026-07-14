from sqlalchemy import asc, desc, func, select
from sqlalchemy.orm import Session, selectinload

from app.modules.home_inventory_manager.models import InventoryCategory, InventoryItem


def add(db: Session, record: object) -> None:
    db.add(record)


def delete_record(db: Session, record: object) -> None:
    db.delete(record)


def get_category(db: Session, category_id: str) -> InventoryCategory | None:
    return db.get(InventoryCategory, category_id)


def list_categories(db: Session, owner_id: str) -> list[InventoryCategory]:
    statement = select(InventoryCategory).where(InventoryCategory.owner_id == owner_id).order_by(asc(InventoryCategory.name))
    return list(db.execute(statement).scalars().all())


def count_items_for_category(db: Session, owner_id: str, category_id: str) -> int:
    statement = select(func.count(InventoryItem.id)).where(
        InventoryItem.owner_id == owner_id,
        InventoryItem.category_id == category_id,
    )
    return int(db.execute(statement).scalar_one())


def item_counts_by_category(db: Session, owner_id: str) -> dict[str, int]:
    statement = (
        select(InventoryItem.category_id, func.count(InventoryItem.id))
        .where(InventoryItem.owner_id == owner_id)
        .group_by(InventoryItem.category_id)
    )
    return {str(category_id): int(count) for category_id, count in db.execute(statement).all()}


def get_item(db: Session, item_id: str) -> InventoryItem | None:
    statement = select(InventoryItem).options(selectinload(InventoryItem.category)).where(InventoryItem.id == item_id)
    return db.execute(statement).scalars().first()


def list_items(db: Session, owner_id: str) -> list[InventoryItem]:
    statement = (
        select(InventoryItem)
        .options(selectinload(InventoryItem.category))
        .where(InventoryItem.owner_id == owner_id)
        .order_by(desc(InventoryItem.updated_at), asc(InventoryItem.title))
    )
    return list(db.execute(statement).scalars().all())
