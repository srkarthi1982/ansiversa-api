from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import select

from app.modules.parking_expense_tracker.models import ParkingExpenseEntry, ParkingExpenseLocation


def get_location(db: Session, location_id: str) -> ParkingExpenseLocation | None:
    return db.get(ParkingExpenseLocation, location_id)


def get_expense(db: Session, expense_id: str) -> ParkingExpenseEntry | None:
    return db.get(ParkingExpenseEntry, expense_id)


def list_locations(db: Session, owner_id: str) -> list[ParkingExpenseLocation]:
    return list(
        db.execute(
            select(ParkingExpenseLocation)
            .options(joinedload(ParkingExpenseLocation.expenses))
            .where(ParkingExpenseLocation.owner_id == owner_id)
            .order_by(ParkingExpenseLocation.updated_at.desc())
        )
        .unique()
        .scalars()
        .all()
    )


def list_expenses(db: Session, owner_id: str) -> list[ParkingExpenseEntry]:
    return list(
        db.execute(
            select(ParkingExpenseEntry)
            .options(joinedload(ParkingExpenseEntry.location))
            .where(ParkingExpenseEntry.owner_id == owner_id)
            .order_by(ParkingExpenseEntry.parked_at.desc(), ParkingExpenseEntry.updated_at.desc())
        )
        .unique()
        .scalars()
        .all()
    )


def add(db: Session, record: object) -> None:
    db.add(record)


def delete_record(db: Session, record: object) -> None:
    db.delete(record)
