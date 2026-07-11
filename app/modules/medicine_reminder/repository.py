from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import select

from app.modules.medicine_reminder.models import (
    MedicineReminderDoseLog,
    MedicineReminderMedicine,
    MedicineReminderNote,
    MedicineReminderSchedule,
)


def get_medicine(db: Session, medicine_id: str) -> MedicineReminderMedicine | None:
    return db.get(MedicineReminderMedicine, medicine_id)


def get_schedule(db: Session, schedule_id: str) -> MedicineReminderSchedule | None:
    return db.get(MedicineReminderSchedule, schedule_id)


def get_dose_log(db: Session, dose_log_id: str) -> MedicineReminderDoseLog | None:
    return db.get(MedicineReminderDoseLog, dose_log_id)


def get_note(db: Session, note_id: str) -> MedicineReminderNote | None:
    return db.get(MedicineReminderNote, note_id)


def list_medicines(db: Session, owner_id: str) -> list[MedicineReminderMedicine]:
    return list(
        db.execute(
            select(MedicineReminderMedicine)
            .options(
                joinedload(MedicineReminderMedicine.schedules),
                joinedload(MedicineReminderMedicine.dose_logs),
                joinedload(MedicineReminderMedicine.notes),
            )
            .where(MedicineReminderMedicine.owner_id == owner_id)
            .order_by(MedicineReminderMedicine.updated_at.desc(), MedicineReminderMedicine.name.asc())
        )
        .unique()
        .scalars()
        .all()
    )


def list_schedules(db: Session, owner_id: str) -> list[MedicineReminderSchedule]:
    return list(
        db.execute(
            select(MedicineReminderSchedule)
            .options(joinedload(MedicineReminderSchedule.medicine))
            .where(MedicineReminderSchedule.owner_id == owner_id)
            .order_by(MedicineReminderSchedule.time_of_day.asc(), MedicineReminderSchedule.updated_at.desc())
        )
        .scalars()
        .all()
    )


def list_dose_logs(db: Session, owner_id: str) -> list[MedicineReminderDoseLog]:
    return list(
        db.execute(
            select(MedicineReminderDoseLog)
            .options(joinedload(MedicineReminderDoseLog.medicine), joinedload(MedicineReminderDoseLog.schedule))
            .where(MedicineReminderDoseLog.owner_id == owner_id)
            .order_by(MedicineReminderDoseLog.scheduled_for.desc(), MedicineReminderDoseLog.created_at.desc())
        )
        .scalars()
        .all()
    )


def list_notes(db: Session, owner_id: str) -> list[MedicineReminderNote]:
    return list(
        db.execute(
            select(MedicineReminderNote)
            .options(joinedload(MedicineReminderNote.medicine))
            .where(MedicineReminderNote.owner_id == owner_id)
            .order_by(MedicineReminderNote.note_date.desc(), MedicineReminderNote.updated_at.desc())
        )
        .scalars()
        .all()
    )


def add(db: Session, record: object) -> None:
    db.add(record)


def delete_record(db: Session, record: object) -> None:
    db.delete(record)
