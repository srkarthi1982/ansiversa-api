from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import select

from app.modules.health_report_organizer.models import (
    HealthReport,
    HealthReportAttachment,
    HealthReportCategory,
    HealthReportFacility,
    HealthReportNote,
)


def get_category(db: Session, category_id: str) -> HealthReportCategory | None:
    return db.get(HealthReportCategory, category_id)


def get_facility(db: Session, facility_id: str) -> HealthReportFacility | None:
    return db.get(HealthReportFacility, facility_id)


def get_report(db: Session, report_id: str) -> HealthReport | None:
    return db.get(HealthReport, report_id)


def get_attachment(db: Session, attachment_id: str) -> HealthReportAttachment | None:
    return db.get(HealthReportAttachment, attachment_id)


def get_note(db: Session, note_id: str) -> HealthReportNote | None:
    return db.get(HealthReportNote, note_id)


def list_categories(db: Session, owner_id: str) -> list[HealthReportCategory]:
    return list(
        db.execute(
            select(HealthReportCategory)
            .options(joinedload(HealthReportCategory.reports))
            .where(HealthReportCategory.owner_id == owner_id)
            .order_by(HealthReportCategory.updated_at.desc(), HealthReportCategory.name.asc())
        )
        .unique()
        .scalars()
        .all()
    )


def list_facilities(db: Session, owner_id: str) -> list[HealthReportFacility]:
    return list(
        db.execute(
            select(HealthReportFacility)
            .options(joinedload(HealthReportFacility.reports))
            .where(HealthReportFacility.owner_id == owner_id)
            .order_by(HealthReportFacility.updated_at.desc(), HealthReportFacility.name.asc())
        )
        .unique()
        .scalars()
        .all()
    )


def list_reports(db: Session, owner_id: str) -> list[HealthReport]:
    return list(
        db.execute(
            select(HealthReport)
            .options(
                joinedload(HealthReport.category),
                joinedload(HealthReport.facility),
                joinedload(HealthReport.attachments),
                joinedload(HealthReport.notes),
            )
            .where(HealthReport.owner_id == owner_id)
            .order_by(HealthReport.report_date.desc(), HealthReport.updated_at.desc())
        )
        .unique()
        .scalars()
        .all()
    )


def list_attachments(db: Session, owner_id: str) -> list[HealthReportAttachment]:
    return list(
        db.execute(
            select(HealthReportAttachment)
            .options(joinedload(HealthReportAttachment.report))
            .where(HealthReportAttachment.owner_id == owner_id)
            .order_by(HealthReportAttachment.updated_at.desc(), HealthReportAttachment.file_name.asc())
        )
        .scalars()
        .all()
    )


def list_notes(db: Session, owner_id: str) -> list[HealthReportNote]:
    return list(
        db.execute(
            select(HealthReportNote)
            .options(joinedload(HealthReportNote.report))
            .where(HealthReportNote.owner_id == owner_id)
            .order_by(HealthReportNote.note_date.desc(), HealthReportNote.updated_at.desc())
        )
        .scalars()
        .all()
    )


def add(db: Session, record: object) -> None:
    db.add(record)


def delete_record(db: Session, record: object) -> None:
    db.delete(record)
