from sqlalchemy import asc, desc, func, select
from sqlalchemy.orm import Session, selectinload

from app.modules.birthday_and_anniversary_reminder.models import ReminderAcknowledgement, ReminderContact, ReminderType


def add(db: Session, record: object) -> None:
    db.add(record)


def delete_record(db: Session, record: object) -> None:
    db.delete(record)


def get_type(db: Session, type_id: str) -> ReminderType | None:
    return db.get(ReminderType, type_id)


def list_types(db: Session, owner_id: str) -> list[ReminderType]:
    statement = select(ReminderType).where(ReminderType.owner_id == owner_id).order_by(asc(ReminderType.sort_order), asc(ReminderType.name))
    return list(db.execute(statement).scalars().all())


def reminder_counts_by_type(db: Session, owner_id: str) -> dict[str, int]:
    statement = select(ReminderContact.reminder_type_id, func.count(ReminderContact.id)).where(ReminderContact.owner_id == owner_id).group_by(ReminderContact.reminder_type_id)
    return {str(type_id): int(count) for type_id, count in db.execute(statement).all()}


def count_reminders_for_type(db: Session, owner_id: str, type_id: str) -> int:
    statement = select(func.count(ReminderContact.id)).where(ReminderContact.owner_id == owner_id, ReminderContact.reminder_type_id == type_id)
    return int(db.execute(statement).scalar_one())


def get_reminder(db: Session, reminder_id: str) -> ReminderContact | None:
    statement = (
        select(ReminderContact)
        .options(selectinload(ReminderContact.reminder_type), selectinload(ReminderContact.acknowledgements))
        .where(ReminderContact.id == reminder_id)
    )
    return db.execute(statement).scalars().first()


def list_reminders(db: Session, owner_id: str) -> list[ReminderContact]:
    statement = (
        select(ReminderContact)
        .options(selectinload(ReminderContact.reminder_type), selectinload(ReminderContact.acknowledgements))
        .where(ReminderContact.owner_id == owner_id)
        .order_by(desc(ReminderContact.favourite), asc(ReminderContact.event_date), asc(ReminderContact.person_name))
    )
    return list(db.execute(statement).scalars().all())


def get_acknowledgement(db: Session, owner_id: str, reminder_id: str, year: int) -> ReminderAcknowledgement | None:
    statement = select(ReminderAcknowledgement).where(
        ReminderAcknowledgement.owner_id == owner_id,
        ReminderAcknowledgement.reminder_contact_id == reminder_id,
        ReminderAcknowledgement.acknowledgement_year == year,
    )
    return db.execute(statement).scalars().first()
