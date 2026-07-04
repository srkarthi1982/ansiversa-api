from fastapi import APIRouter, Response, status

from app.modules.expense_tracker import service
from app.modules.expense_tracker.dependencies import CurrentExpenseTrackerUser, ExpenseTrackerDB
from app.modules.expense_tracker.schemas import (
    ExpenseTrackerCategoryCreateRequest,
    ExpenseTrackerCategoryDetailResponse,
    ExpenseTrackerCategorySummaryResponse,
    ExpenseTrackerCategoryUpdateRequest,
    ExpenseTrackerDashboardResponse,
    ExpenseTrackerExpenseCreateRequest,
    ExpenseTrackerExpenseDetailResponse,
    ExpenseTrackerExpenseSummaryResponse,
    ExpenseTrackerExpenseUpdateRequest,
    ExpenseTrackerHistoryResponse,
)

router = APIRouter()


@router.get("/dashboard", response_model=ExpenseTrackerDashboardResponse)
def get_dashboard(db: ExpenseTrackerDB, current_user: CurrentExpenseTrackerUser):
    return service.get_dashboard(db, current_user)


@router.get("/expenses", response_model=list[ExpenseTrackerExpenseSummaryResponse])
def list_expenses(db: ExpenseTrackerDB, current_user: CurrentExpenseTrackerUser):
    return service.list_expenses(db, current_user)


@router.post("/expenses", response_model=ExpenseTrackerExpenseDetailResponse, status_code=status.HTTP_201_CREATED)
def create_expense(
    payload: ExpenseTrackerExpenseCreateRequest,
    db: ExpenseTrackerDB,
    current_user: CurrentExpenseTrackerUser,
):
    return service.create_expense(db, current_user, payload)


@router.get("/expenses/{expense_id}", response_model=ExpenseTrackerExpenseDetailResponse)
def get_expense(expense_id: int, db: ExpenseTrackerDB, current_user: CurrentExpenseTrackerUser):
    return service.get_expense(db, current_user, expense_id)


@router.put("/expenses/{expense_id}", response_model=ExpenseTrackerExpenseDetailResponse)
def update_expense(
    expense_id: int,
    payload: ExpenseTrackerExpenseUpdateRequest,
    db: ExpenseTrackerDB,
    current_user: CurrentExpenseTrackerUser,
):
    return service.update_expense(db, current_user, expense_id, payload)


@router.delete("/expenses/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(expense_id: int, db: ExpenseTrackerDB, current_user: CurrentExpenseTrackerUser):
    service.delete_expense(db, current_user, expense_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/expenses/{expense_id}/duplicate", response_model=ExpenseTrackerExpenseDetailResponse)
def duplicate_expense(expense_id: int, db: ExpenseTrackerDB, current_user: CurrentExpenseTrackerUser):
    return service.duplicate_expense(db, current_user, expense_id)


@router.get("/categories", response_model=list[ExpenseTrackerCategorySummaryResponse])
def list_categories(db: ExpenseTrackerDB, current_user: CurrentExpenseTrackerUser):
    return service.list_categories(db, current_user)


@router.post("/categories", response_model=ExpenseTrackerCategoryDetailResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    payload: ExpenseTrackerCategoryCreateRequest,
    db: ExpenseTrackerDB,
    current_user: CurrentExpenseTrackerUser,
):
    return service.create_category(db, current_user, payload)


@router.get("/categories/{category_id}", response_model=ExpenseTrackerCategoryDetailResponse)
def get_category(category_id: int, db: ExpenseTrackerDB, current_user: CurrentExpenseTrackerUser):
    return service.get_category(db, current_user, category_id)


@router.put("/categories/{category_id}", response_model=ExpenseTrackerCategoryDetailResponse)
def update_category(
    category_id: int,
    payload: ExpenseTrackerCategoryUpdateRequest,
    db: ExpenseTrackerDB,
    current_user: CurrentExpenseTrackerUser,
):
    return service.update_category(db, current_user, category_id, payload)


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, db: ExpenseTrackerDB, current_user: CurrentExpenseTrackerUser):
    service.delete_category(db, current_user, category_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/history", response_model=list[ExpenseTrackerHistoryResponse])
def list_history(db: ExpenseTrackerDB, current_user: CurrentExpenseTrackerUser):
    return service.list_history(db, current_user)

