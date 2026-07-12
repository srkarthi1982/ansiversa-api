from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import select

from app.modules.trip_cost_calculator.models import TripCostExpense, TripCostTrip


def get_trip(db: Session, trip_id: str) -> TripCostTrip | None:
    return db.get(TripCostTrip, trip_id)


def get_expense(db: Session, expense_id: str) -> TripCostExpense | None:
    return db.get(TripCostExpense, expense_id)


def list_trips(db: Session, owner_id: str) -> list[TripCostTrip]:
    return list(
        db.execute(
            select(TripCostTrip)
            .options(joinedload(TripCostTrip.expenses))
            .where(TripCostTrip.owner_id == owner_id)
            .order_by(TripCostTrip.updated_at.desc())
        )
        .unique()
        .scalars()
        .all()
    )


def list_expenses(db: Session, owner_id: str) -> list[TripCostExpense]:
    return list(
        db.execute(
            select(TripCostExpense)
            .options(joinedload(TripCostExpense.trip))
            .where(TripCostExpense.owner_id == owner_id)
            .order_by(TripCostExpense.expense_date.desc(), TripCostExpense.updated_at.desc())
        )
        .unique()
        .scalars()
        .all()
    )


def add(db: Session, record: object) -> None:
    db.add(record)


def delete_record(db: Session, record: object) -> None:
    db.delete(record)
