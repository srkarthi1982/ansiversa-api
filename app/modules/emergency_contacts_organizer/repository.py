from sqlalchemy import asc, desc, func, select
from sqlalchemy.orm import Session, selectinload

from app.modules.emergency_contacts_organizer.models import EmergencyContact, EmergencyContactCategory


def add(db: Session, record: object) -> None:
    db.add(record)


def delete_record(db: Session, record: object) -> None:
    db.delete(record)


def get_category(db: Session, category_id: str) -> EmergencyContactCategory | None:
    return db.get(EmergencyContactCategory, category_id)


def list_categories(db: Session, owner_id: str) -> list[EmergencyContactCategory]:
    statement = (
        select(EmergencyContactCategory)
        .where(EmergencyContactCategory.owner_id == owner_id)
        .order_by(asc(EmergencyContactCategory.sort_order), asc(EmergencyContactCategory.name))
    )
    return list(db.execute(statement).scalars().all())


def count_contacts_for_category(db: Session, owner_id: str, category_id: str) -> int:
    statement = select(func.count(EmergencyContact.id)).where(
        EmergencyContact.owner_id == owner_id,
        EmergencyContact.category_id == category_id,
    )
    return int(db.execute(statement).scalar_one())


def contact_counts_by_category(db: Session, owner_id: str) -> dict[str, int]:
    statement = (
        select(EmergencyContact.category_id, func.count(EmergencyContact.id))
        .where(EmergencyContact.owner_id == owner_id)
        .group_by(EmergencyContact.category_id)
    )
    return {str(category_id): int(count) for category_id, count in db.execute(statement).all()}


def get_contact(db: Session, contact_id: str) -> EmergencyContact | None:
    statement = select(EmergencyContact).options(selectinload(EmergencyContact.category)).where(EmergencyContact.id == contact_id)
    return db.execute(statement).scalars().first()


def list_contacts(db: Session, owner_id: str) -> list[EmergencyContact]:
    statement = (
        select(EmergencyContact)
        .options(selectinload(EmergencyContact.category))
        .where(EmergencyContact.owner_id == owner_id)
        .order_by(desc(EmergencyContact.is_favourite), desc(EmergencyContact.is_primary), asc(EmergencyContact.priority), asc(EmergencyContact.full_name))
    )
    return list(db.execute(statement).scalars().all())
