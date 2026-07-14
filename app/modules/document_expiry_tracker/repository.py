from sqlalchemy import asc, desc, select
from sqlalchemy.orm import Session

from app.modules.document_expiry_tracker.models import DocumentRecord


def get_document(db: Session, document_id: str) -> DocumentRecord | None:
    return db.get(DocumentRecord, document_id)


def list_documents(db: Session, owner_id: str, include_archived: bool = False) -> list[DocumentRecord]:
    statement = select(DocumentRecord).where(DocumentRecord.owner_id == owner_id)
    if not include_archived:
        statement = statement.where(DocumentRecord.archived.is_(False))
    return list(
        db.execute(statement.order_by(asc(DocumentRecord.expiry_date), desc(DocumentRecord.updated_at)))
        .scalars()
        .all()
    )


def add(db: Session, record: object) -> None:
    db.add(record)


def delete_record(db: Session, record: object) -> None:
    db.delete(record)
