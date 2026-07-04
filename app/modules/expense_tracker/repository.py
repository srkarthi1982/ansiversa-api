from sqlalchemy import update
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import select

from app.modules.expense_tracker.models import (
    ExpenseTrackerCategory,
    ExpenseTrackerExpense,
    ExpenseTrackerHistory,
)


def get_expense(db: Session, expense_id: int) -> ExpenseTrackerExpense | None:
    return db.get(ExpenseTrackerExpense, expense_id)


def get_category(db: Session, category_id: int) -> ExpenseTrackerCategory | None:
    return db.get(ExpenseTrackerCategory, category_id)


def list_expenses(db: Session, owner_id: str) -> list[ExpenseTrackerExpense]:
    return list(
        db.execute(
            select(ExpenseTrackerExpense)
            .options(joinedload(ExpenseTrackerExpense.category))
            .where(ExpenseTrackerExpense.owner_id == owner_id)
            .order_by(ExpenseTrackerExpense.expense_date.desc(), ExpenseTrackerExpense.updated_at.desc())
        )
        .scalars()
        .all()
    )


def list_categories(db: Session, owner_id: str) -> list[ExpenseTrackerCategory]:
    return list(
        db.execute(
            select(ExpenseTrackerCategory)
            .where(ExpenseTrackerCategory.owner_id == owner_id)
            .order_by(ExpenseTrackerCategory.is_archived.asc(), ExpenseTrackerCategory.name.asc())
        )
        .scalars()
        .all()
    )


def list_history(db: Session, owner_id: str) -> list[ExpenseTrackerHistory]:
    return list(
        db.execute(
            select(ExpenseTrackerHistory)
            .where(ExpenseTrackerHistory.owner_id == owner_id)
            .order_by(ExpenseTrackerHistory.created_at.desc())
            .limit(100)
        )
        .scalars()
        .all()
    )


def add(db: Session, record: object) -> None:
    db.add(record)


def delete_record(db: Session, record: object) -> None:
    db.delete(record)


def detach_expense_history(db: Session, owner_id: str, expense_id: int) -> None:
    db.execute(
        update(ExpenseTrackerHistory)
        .where(ExpenseTrackerHistory.owner_id == owner_id, ExpenseTrackerHistory.expense_id == expense_id)
        .values(expense_id=None)
    )


def detach_category_from_expenses(db: Session, owner_id: str, category_id: int) -> None:
    db.execute(
        update(ExpenseTrackerExpense)
        .where(ExpenseTrackerExpense.owner_id == owner_id, ExpenseTrackerExpense.category_id == category_id)
        .values(category_id=None)
    )


def detach_category_history(db: Session, owner_id: str, category_id: int) -> None:
    db.execute(
        update(ExpenseTrackerHistory)
        .where(ExpenseTrackerHistory.owner_id == owner_id, ExpenseTrackerHistory.category_id == category_id)
        .values(category_id=None)
    )


def record_history(
    db: Session,
    *,
    owner_id: str,
    action_type: str,
    expense_id: int | None = None,
    category_id: int | None = None,
    title: str | None = None,
    amount: float | None = None,
    currency: str | None = None,
    notes: str | None = None,
) -> ExpenseTrackerHistory:
    history = ExpenseTrackerHistory(
        owner_id=owner_id,
        expense_id=expense_id,
        category_id=category_id,
        action_type=action_type,
        title=title,
        amount=amount,
        currency=currency,
        notes=notes,
    )
    add(db, history)
    return history

