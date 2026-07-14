from sqlalchemy import asc, desc, func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.modules.household_expense_splitter.models import ExpenseParticipant, HouseholdExpense, HouseholdMember, HouseholdSettlement


def add(db: Session, record: object) -> None:
    db.add(record)


def delete_record(db: Session, record: object) -> None:
    db.delete(record)


def get_member(db: Session, member_id: str) -> HouseholdMember | None:
    return db.get(HouseholdMember, member_id)


def list_members(db: Session, owner_id: str) -> list[HouseholdMember]:
    return list(db.execute(select(HouseholdMember).where(HouseholdMember.owner_id == owner_id).order_by(asc(HouseholdMember.name))).scalars().all())


def member_link_count(db: Session, owner_id: str, member_id: str) -> int:
    expenses = db.execute(select(func.count(HouseholdExpense.id)).where(HouseholdExpense.owner_id == owner_id, HouseholdExpense.paid_by_member_id == member_id)).scalar_one()
    participants = db.execute(select(func.count(ExpenseParticipant.id)).join(HouseholdExpense).where(HouseholdExpense.owner_id == owner_id, ExpenseParticipant.member_id == member_id)).scalar_one()
    settlements = db.execute(
        select(func.count(HouseholdSettlement.id)).where(
            HouseholdSettlement.owner_id == owner_id,
            or_(HouseholdSettlement.from_member_id == member_id, HouseholdSettlement.to_member_id == member_id),
        )
    ).scalar_one()
    return int(expenses) + int(participants) + int(settlements)


def get_expense(db: Session, expense_id: str) -> HouseholdExpense | None:
    statement = (
        select(HouseholdExpense)
        .options(selectinload(HouseholdExpense.paid_by_member), selectinload(HouseholdExpense.participants).selectinload(ExpenseParticipant.member))
        .where(HouseholdExpense.id == expense_id)
    )
    return db.execute(statement).scalars().first()


def list_expenses(db: Session, owner_id: str) -> list[HouseholdExpense]:
    statement = (
        select(HouseholdExpense)
        .options(selectinload(HouseholdExpense.paid_by_member), selectinload(HouseholdExpense.participants).selectinload(ExpenseParticipant.member))
        .where(HouseholdExpense.owner_id == owner_id)
        .order_by(desc(HouseholdExpense.expense_date), desc(HouseholdExpense.created_at))
    )
    return list(db.execute(statement).scalars().all())


def get_settlement(db: Session, settlement_id: str) -> HouseholdSettlement | None:
    statement = (
        select(HouseholdSettlement)
        .options(selectinload(HouseholdSettlement.from_member), selectinload(HouseholdSettlement.to_member))
        .where(HouseholdSettlement.id == settlement_id)
    )
    return db.execute(statement).scalars().first()


def list_settlements(db: Session, owner_id: str) -> list[HouseholdSettlement]:
    statement = (
        select(HouseholdSettlement)
        .options(selectinload(HouseholdSettlement.from_member), selectinload(HouseholdSettlement.to_member))
        .where(HouseholdSettlement.owner_id == owner_id)
        .order_by(desc(HouseholdSettlement.settlement_date), desc(HouseholdSettlement.created_at))
    )
    return list(db.execute(statement).scalars().all())
