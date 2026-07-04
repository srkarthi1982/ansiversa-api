from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.expense_tracker import repository
from app.modules.expense_tracker.models import ExpenseTrackerCategory, ExpenseTrackerExpense
from app.modules.expense_tracker.schemas import (
    ExpenseTrackerCategoryCreateRequest,
    ExpenseTrackerCategoryDetailResponse,
    ExpenseTrackerCategorySummaryResponse,
    ExpenseTrackerCategoryTotalResponse,
    ExpenseTrackerCategoryUpdateRequest,
    ExpenseTrackerDashboardResponse,
    ExpenseTrackerExpenseCreateRequest,
    ExpenseTrackerExpenseDetailResponse,
    ExpenseTrackerExpenseSummaryResponse,
    ExpenseTrackerExpenseUpdateRequest,
    ExpenseTrackerHistoryResponse,
)

PREVIEW_LENGTH = 220


def _preview(value: str | None) -> str | None:
    if not value:
        return None
    if len(value) <= PREVIEW_LENGTH:
        return value
    return f"{value[:PREVIEW_LENGTH].rstrip()}..."


def _rounded(value: float) -> float:
    return round(value, 2)


def _not_found(detail: str) -> None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def _get_owned_expense(db: Session, user: User, expense_id: int) -> ExpenseTrackerExpense:
    expense = repository.get_expense(db, expense_id)
    if not expense or expense.owner_id != user.id:
        _not_found("Expense was not found.")
    return expense


def _get_owned_category(db: Session, user: User, category_id: int) -> ExpenseTrackerCategory:
    category = repository.get_category(db, category_id)
    if not category or category.owner_id != user.id:
        _not_found("Category was not found.")
    return category


def _validate_category(db: Session, user: User, category_id: int | None) -> None:
    if category_id is None:
        return
    _get_owned_category(db, user, category_id)


def _category_summary_response(category: ExpenseTrackerCategory) -> ExpenseTrackerCategorySummaryResponse:
    return ExpenseTrackerCategorySummaryResponse(
        id=category.id,
        name=category.name,
        color=category.color,
        is_archived=category.is_archived,
        notes_preview=_preview(category.notes),
        created_at=category.created_at,
        updated_at=category.updated_at,
    )


def _category_detail_response(category: ExpenseTrackerCategory) -> ExpenseTrackerCategoryDetailResponse:
    summary = _category_summary_response(category)
    return ExpenseTrackerCategoryDetailResponse(**summary.model_dump(), notes=category.notes)


def _expense_summary_response(expense: ExpenseTrackerExpense) -> ExpenseTrackerExpenseSummaryResponse:
    return ExpenseTrackerExpenseSummaryResponse(
        id=expense.id,
        title=expense.title,
        amount=_rounded(expense.amount),
        currency=expense.currency,
        expense_date=expense.expense_date,
        payment_method=expense.payment_method,
        category_id=expense.category_id,
        category_name=expense.category.name if expense.category else None,
        category_color=expense.category.color if expense.category else None,
        merchant=expense.merchant,
        notes_preview=_preview(expense.notes),
        created_at=expense.created_at,
        updated_at=expense.updated_at,
    )


def _expense_detail_response(expense: ExpenseTrackerExpense) -> ExpenseTrackerExpenseDetailResponse:
    summary = _expense_summary_response(expense)
    return ExpenseTrackerExpenseDetailResponse(**summary.model_dump(), notes=expense.notes)


def _history_response(history: object) -> ExpenseTrackerHistoryResponse:
    return ExpenseTrackerHistoryResponse(
        id=history.id,
        expense_id=history.expense_id,
        category_id=history.category_id,
        action_type=history.action_type,
        title=history.title,
        amount=_rounded(history.amount) if history.amount is not None else None,
        currency=history.currency,
        notes=history.notes,
        created_at=history.created_at,
    )


def list_expenses(db: Session, user: User) -> list[ExpenseTrackerExpenseSummaryResponse]:
    return [_expense_summary_response(expense) for expense in repository.list_expenses(db, user.id)]


def create_expense(
    db: Session,
    user: User,
    payload: ExpenseTrackerExpenseCreateRequest,
) -> ExpenseTrackerExpenseDetailResponse:
    data = payload.model_dump()
    _validate_category(db, user, data.get("category_id"))
    expense = ExpenseTrackerExpense(owner_id=user.id, **data)
    repository.add(db, expense)
    db.flush()
    repository.record_history(
        db,
        owner_id=user.id,
        expense_id=expense.id,
        category_id=expense.category_id,
        action_type="expense-created",
        title=expense.title,
        amount=expense.amount,
        currency=expense.currency,
    )
    db.commit()
    db.refresh(expense)
    return _expense_detail_response(expense)


def get_expense(db: Session, user: User, expense_id: int) -> ExpenseTrackerExpenseDetailResponse:
    return _expense_detail_response(_get_owned_expense(db, user, expense_id))


def update_expense(
    db: Session,
    user: User,
    expense_id: int,
    payload: ExpenseTrackerExpenseUpdateRequest,
) -> ExpenseTrackerExpenseDetailResponse:
    expense = _get_owned_expense(db, user, expense_id)
    data = payload.model_dump(exclude_unset=True)
    if "category_id" in data:
        _validate_category(db, user, data["category_id"])
    for field, value in data.items():
        setattr(expense, field, value)
    repository.record_history(
        db,
        owner_id=user.id,
        expense_id=expense.id,
        category_id=expense.category_id,
        action_type="expense-updated",
        title=expense.title,
        amount=expense.amount,
        currency=expense.currency,
    )
    db.commit()
    db.refresh(expense)
    return _expense_detail_response(expense)


def delete_expense(db: Session, user: User, expense_id: int) -> None:
    expense = _get_owned_expense(db, user, expense_id)
    repository.record_history(
        db,
        owner_id=user.id,
        expense_id=None,
        category_id=expense.category_id,
        action_type="expense-deleted",
        title=expense.title,
        amount=expense.amount,
        currency=expense.currency,
    )
    repository.detach_expense_history(db, user.id, expense.id)
    repository.delete_record(db, expense)
    db.commit()


def duplicate_expense(db: Session, user: User, expense_id: int) -> ExpenseTrackerExpenseDetailResponse:
    expense = _get_owned_expense(db, user, expense_id)
    duplicate = ExpenseTrackerExpense(
        owner_id=user.id,
        category_id=expense.category_id,
        title=expense.title,
        amount=expense.amount,
        currency=expense.currency,
        expense_date=expense.expense_date,
        payment_method=expense.payment_method,
        merchant=expense.merchant,
        notes=expense.notes,
    )
    repository.add(db, duplicate)
    db.flush()
    repository.record_history(
        db,
        owner_id=user.id,
        expense_id=duplicate.id,
        category_id=duplicate.category_id,
        action_type="expense-duplicated",
        title=duplicate.title,
        amount=duplicate.amount,
        currency=duplicate.currency,
    )
    db.commit()
    db.refresh(duplicate)
    return _expense_detail_response(duplicate)


def list_categories(db: Session, user: User) -> list[ExpenseTrackerCategorySummaryResponse]:
    return [_category_summary_response(category) for category in repository.list_categories(db, user.id)]


def create_category(
    db: Session,
    user: User,
    payload: ExpenseTrackerCategoryCreateRequest,
) -> ExpenseTrackerCategoryDetailResponse:
    category = ExpenseTrackerCategory(owner_id=user.id, **payload.model_dump())
    repository.add(db, category)
    db.flush()
    repository.record_history(
        db,
        owner_id=user.id,
        category_id=category.id,
        action_type="category-created",
        title=category.name,
    )
    db.commit()
    db.refresh(category)
    return _category_detail_response(category)


def get_category(db: Session, user: User, category_id: int) -> ExpenseTrackerCategoryDetailResponse:
    return _category_detail_response(_get_owned_category(db, user, category_id))


def update_category(
    db: Session,
    user: User,
    category_id: int,
    payload: ExpenseTrackerCategoryUpdateRequest,
) -> ExpenseTrackerCategoryDetailResponse:
    category = _get_owned_category(db, user, category_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(category, field, value)
    repository.record_history(
        db,
        owner_id=user.id,
        category_id=category.id,
        action_type="category-updated",
        title=category.name,
    )
    db.commit()
    db.refresh(category)
    return _category_detail_response(category)


def delete_category(db: Session, user: User, category_id: int) -> None:
    category = _get_owned_category(db, user, category_id)
    repository.record_history(
        db,
        owner_id=user.id,
        category_id=None,
        action_type="category-deleted",
        title=category.name,
    )
    repository.detach_category_from_expenses(db, user.id, category.id)
    repository.detach_category_history(db, user.id, category.id)
    repository.delete_record(db, category)
    db.commit()


def list_history(db: Session, user: User) -> list[ExpenseTrackerHistoryResponse]:
    return [_history_response(history) for history in repository.list_history(db, user.id)]


def get_dashboard(db: Session, user: User) -> ExpenseTrackerDashboardResponse:
    expenses = list_expenses(db, user)
    categories = list_categories(db, user)
    history = list_history(db, user)
    current_month = date.today().isoformat()[:7]
    total_amount = _rounded(sum(expense.amount for expense in expenses))
    monthly_total = _rounded(sum(expense.amount for expense in expenses if expense.expense_date.startswith(current_month)))
    highest_expense = max(expenses, key=lambda expense: expense.amount, default=None)
    average_expense = _rounded(total_amount / len(expenses)) if expenses else 0
    totals: dict[tuple[int | None, str, str | None, str], ExpenseTrackerCategoryTotalResponse] = {}

    for expense in expenses:
        category_name = expense.category_name or ""
        key = (expense.category_id, category_name, expense.category_color, expense.currency)
        current = totals.get(key)
        if current is None:
            totals[key] = ExpenseTrackerCategoryTotalResponse(
                category_id=expense.category_id,
                category_name=category_name,
                category_color=expense.category_color,
                currency=expense.currency,
                total_amount=expense.amount,
                expense_count=1,
            )
            continue
        current.total_amount = _rounded(current.total_amount + expense.amount)
        current.expense_count += 1

    category_totals = sorted(totals.values(), key=lambda item: item.total_amount, reverse=True)

    return ExpenseTrackerDashboardResponse(
        expenses=expenses,
        categories=categories,
        history=history,
        total_expenses=len(expenses),
        total_amount=total_amount,
        monthly_total=monthly_total,
        highest_expense=highest_expense,
        recent_expenses=expenses[:5],
        average_expense=average_expense,
        category_totals=category_totals,
    )
