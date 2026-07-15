from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload
from app.modules.symptom_journal.models import SymptomCategory, SymptomEntry


def add(db: Session, item):
    db.add(item)
    return item


def delete(db: Session, item) -> None:
    db.delete(item)


def list_categories(db: Session, owner_id: str) -> list[SymptomCategory]:
    return list(db.scalars(select(SymptomCategory).where(SymptomCategory.owner_id == owner_id).order_by(SymptomCategory.sort_order, SymptomCategory.name)))


def get_category(db: Session, item_id: str) -> SymptomCategory | None:
    return db.get(SymptomCategory, item_id)


def list_entries(db: Session, owner_id: str) -> list[SymptomEntry]:
    result = db.execute(select(SymptomEntry).options(joinedload(SymptomEntry.category)).where(SymptomEntry.owner_id == owner_id).order_by(SymptomEntry.entry_date.desc(), SymptomEntry.created_at.desc()))
    return list(result.unique().scalars())


def get_entry(db: Session, item_id: str) -> SymptomEntry | None:
    result = db.execute(select(SymptomEntry).options(joinedload(SymptomEntry.category)).where(SymptomEntry.id == item_id))
    return result.unique().scalars().first()


def entry_counts_by_category(db: Session, owner_id: str) -> dict[str, int]:
    rows = db.execute(select(SymptomEntry.category_id, func.count()).where(SymptomEntry.owner_id == owner_id, SymptomEntry.category_id.is_not(None)).group_by(SymptomEntry.category_id))
    return {row[0]: row[1] for row in rows}


def count_entries_for_category(db: Session, owner_id: str, category_id: str) -> int:
    return db.scalar(select(func.count()).select_from(SymptomEntry).where(SymptomEntry.owner_id == owner_id, SymptomEntry.category_id == category_id)) or 0
