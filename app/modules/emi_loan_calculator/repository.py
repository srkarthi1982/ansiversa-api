from sqlalchemy.orm import Session
from sqlalchemy.sql import select

from app.modules.emi_loan_calculator.models import LoanScenario


def get_scenario(db: Session, scenario_id: str) -> LoanScenario | None:
    return db.get(LoanScenario, scenario_id)


def list_scenarios(db: Session, owner_id: str) -> list[LoanScenario]:
    return list(
        db.execute(
            select(LoanScenario)
            .where(LoanScenario.owner_id == owner_id)
            .order_by(LoanScenario.updated_at.desc(), LoanScenario.created_at.desc())
        )
        .scalars()
        .all()
    )


def add(db: Session, record: object) -> None:
    db.add(record)


def delete_record(db: Session, record: object) -> None:
    db.delete(record)
