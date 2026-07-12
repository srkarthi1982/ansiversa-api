from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import select

from app.modules.vat_assistant_uae.models import VatRegistration, VatReturn, VatTransaction


def get_registration(db: Session, registration_id: str) -> VatRegistration | None:
    return db.get(VatRegistration, registration_id)


def get_return(db: Session, return_id: str) -> VatReturn | None:
    return db.get(VatReturn, return_id)


def get_transaction(db: Session, transaction_id: str) -> VatTransaction | None:
    return db.get(VatTransaction, transaction_id)


def list_registrations(db: Session, owner_id: str) -> list[VatRegistration]:
    return list(
        db.execute(
            select(VatRegistration)
            .options(joinedload(VatRegistration.returns), joinedload(VatRegistration.transactions))
            .where(VatRegistration.owner_id == owner_id)
            .order_by(VatRegistration.updated_at.desc())
        )
        .unique()
        .scalars()
        .all()
    )


def list_returns(db: Session, owner_id: str) -> list[VatReturn]:
    return list(
        db.execute(
            select(VatReturn)
            .options(joinedload(VatReturn.registration))
            .where(VatReturn.owner_id == owner_id)
            .order_by(VatReturn.filing_due_date.asc(), VatReturn.updated_at.desc())
        )
        .unique()
        .scalars()
        .all()
    )


def list_transactions(db: Session, owner_id: str) -> list[VatTransaction]:
    return list(
        db.execute(
            select(VatTransaction)
            .options(joinedload(VatTransaction.registration), joinedload(VatTransaction.vat_return))
            .where(VatTransaction.owner_id == owner_id)
            .order_by(VatTransaction.transaction_date.desc(), VatTransaction.updated_at.desc())
        )
        .unique()
        .scalars()
        .all()
    )


def add(db: Session, record: object) -> None:
    db.add(record)


def delete_record(db: Session, record: object) -> None:
    db.delete(record)
