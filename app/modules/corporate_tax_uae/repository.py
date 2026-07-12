from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import select

from app.modules.corporate_tax_uae.models import CorporateTaxAdjustment, CorporateTaxObligation, CorporateTaxPeriod


def get_period(db: Session, period_id: str) -> CorporateTaxPeriod | None:
    return db.get(CorporateTaxPeriod, period_id)


def get_adjustment(db: Session, adjustment_id: str) -> CorporateTaxAdjustment | None:
    return db.get(CorporateTaxAdjustment, adjustment_id)


def get_obligation(db: Session, obligation_id: str) -> CorporateTaxObligation | None:
    return db.get(CorporateTaxObligation, obligation_id)


def list_periods(db: Session, owner_id: str) -> list[CorporateTaxPeriod]:
    return list(
        db.execute(
            select(CorporateTaxPeriod)
            .options(joinedload(CorporateTaxPeriod.adjustments), joinedload(CorporateTaxPeriod.obligations))
            .where(CorporateTaxPeriod.owner_id == owner_id)
            .order_by(CorporateTaxPeriod.financial_year_end.desc(), CorporateTaxPeriod.updated_at.desc())
        )
        .unique()
        .scalars()
        .all()
    )


def list_adjustments(db: Session, owner_id: str) -> list[CorporateTaxAdjustment]:
    return list(
        db.execute(
            select(CorporateTaxAdjustment)
            .options(joinedload(CorporateTaxAdjustment.period))
            .where(CorporateTaxAdjustment.owner_id == owner_id)
            .order_by(CorporateTaxAdjustment.updated_at.desc())
        )
        .unique()
        .scalars()
        .all()
    )


def list_obligations(db: Session, owner_id: str) -> list[CorporateTaxObligation]:
    return list(
        db.execute(
            select(CorporateTaxObligation)
            .options(joinedload(CorporateTaxObligation.period))
            .where(CorporateTaxObligation.owner_id == owner_id)
            .order_by(CorporateTaxObligation.due_date.asc(), CorporateTaxObligation.updated_at.desc())
        )
        .unique()
        .scalars()
        .all()
    )


def add(db: Session, record: object) -> None:
    db.add(record)


def delete_record(db: Session, record: object) -> None:
    db.delete(record)
