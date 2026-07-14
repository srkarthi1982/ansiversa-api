from sqlalchemy import asc, desc, func, select
from sqlalchemy.orm import Session, selectinload

from app.modules.digital_document_vault.models import VaultCategory, VaultDocument


def add(db: Session, record: object) -> None:
    db.add(record)


def delete_record(db: Session, record: object) -> None:
    db.delete(record)


def get_category(db: Session, category_id: str) -> VaultCategory | None:
    return db.get(VaultCategory, category_id)


def list_categories(db: Session, owner_id: str) -> list[VaultCategory]:
    statement = select(VaultCategory).where(VaultCategory.owner_id == owner_id).order_by(asc(VaultCategory.name))
    return list(db.execute(statement).scalars().all())


def count_documents_for_category(db: Session, owner_id: str, category_id: str) -> int:
    statement = select(func.count(VaultDocument.id)).where(
        VaultDocument.owner_id == owner_id,
        VaultDocument.category_id == category_id,
    )
    return int(db.execute(statement).scalar_one())


def document_counts_by_category(db: Session, owner_id: str) -> dict[str, int]:
    statement = (
        select(VaultDocument.category_id, func.count(VaultDocument.id))
        .where(VaultDocument.owner_id == owner_id)
        .group_by(VaultDocument.category_id)
    )
    return {str(category_id): int(count) for category_id, count in db.execute(statement).all()}


def get_document(db: Session, document_id: str) -> VaultDocument | None:
    statement = select(VaultDocument).options(selectinload(VaultDocument.category)).where(VaultDocument.id == document_id)
    return db.execute(statement).scalars().first()


def list_documents(db: Session, owner_id: str) -> list[VaultDocument]:
    statement = (
        select(VaultDocument)
        .options(selectinload(VaultDocument.category))
        .where(VaultDocument.owner_id == owner_id)
        .order_by(desc(VaultDocument.uploaded_at), asc(VaultDocument.title))
    )
    return list(db.execute(statement).scalars().all())
