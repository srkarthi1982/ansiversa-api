from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

PaymentMethod = Literal["cash", "card", "bank-transfer", "wallet", "other"]
HistoryAction = Literal[
    "expense-created",
    "expense-updated",
    "expense-deleted",
    "expense-duplicated",
    "category-created",
    "category-updated",
    "category-deleted",
]


def _normalize_text(value: object) -> object:
    if isinstance(value, str):
        normalized = value.strip()
        return normalized or None
    return value


class ExpenseTrackerExpenseCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    amount: float = Field(gt=0, le=1_000_000_000)
    currency: str = Field(default="AED", min_length=2, max_length=8)
    expense_date: str = Field(alias="expenseDate", min_length=1, max_length=40)
    payment_method: PaymentMethod = Field(default="card", alias="paymentMethod")
    category_id: int | None = Field(default=None, alias="categoryId")
    merchant: str | None = Field(default=None, max_length=160)
    notes: str | None = Field(default=None, max_length=4000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class ExpenseTrackerExpenseUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    amount: float | None = Field(default=None, gt=0, le=1_000_000_000)
    currency: str | None = Field(default=None, min_length=2, max_length=8)
    expense_date: str | None = Field(default=None, alias="expenseDate", min_length=1, max_length=40)
    payment_method: PaymentMethod | None = Field(default=None, alias="paymentMethod")
    category_id: int | None = Field(default=None, alias="categoryId")
    merchant: str | None = Field(default=None, max_length=160)
    notes: str | None = Field(default=None, max_length=4000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class ExpenseTrackerCategoryCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    color: str = Field(default="#2f6f73", min_length=3, max_length=40)
    notes: str | None = Field(default=None, max_length=2000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class ExpenseTrackerCategoryUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    color: str | None = Field(default=None, min_length=3, max_length=40)
    is_archived: bool | None = Field(default=None, alias="isArchived")
    notes: str | None = Field(default=None, max_length=2000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class ExpenseTrackerCategorySummaryResponse(BaseModel):
    id: int
    name: str
    color: str
    is_archived: bool = Field(serialization_alias="isArchived")
    notes_preview: str | None = Field(serialization_alias="notesPreview")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class ExpenseTrackerCategoryDetailResponse(ExpenseTrackerCategorySummaryResponse):
    notes: str | None


class ExpenseTrackerExpenseSummaryResponse(BaseModel):
    id: int
    title: str
    amount: float
    currency: str
    expense_date: str = Field(serialization_alias="expenseDate")
    payment_method: PaymentMethod = Field(serialization_alias="paymentMethod")
    category_id: int | None = Field(serialization_alias="categoryId")
    category_name: str | None = Field(serialization_alias="categoryName")
    category_color: str | None = Field(serialization_alias="categoryColor")
    merchant: str | None
    notes_preview: str | None = Field(serialization_alias="notesPreview")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class ExpenseTrackerExpenseDetailResponse(ExpenseTrackerExpenseSummaryResponse):
    notes: str | None


class ExpenseTrackerHistoryResponse(BaseModel):
    id: int
    expense_id: int | None = Field(serialization_alias="expenseId")
    category_id: int | None = Field(serialization_alias="categoryId")
    action_type: HistoryAction = Field(serialization_alias="actionType")
    title: str | None
    amount: float | None
    currency: str | None
    notes: str | None
    created_at: datetime = Field(serialization_alias="createdAt")


class ExpenseTrackerCategoryTotalResponse(BaseModel):
    category_id: int | None = Field(serialization_alias="categoryId")
    category_name: str = Field(serialization_alias="categoryName")
    category_color: str | None = Field(serialization_alias="categoryColor")
    currency: str
    total_amount: float = Field(serialization_alias="totalAmount")
    expense_count: int = Field(serialization_alias="expenseCount")


class ExpenseTrackerDashboardResponse(BaseModel):
    expenses: list[ExpenseTrackerExpenseSummaryResponse]
    categories: list[ExpenseTrackerCategorySummaryResponse]
    history: list[ExpenseTrackerHistoryResponse]
    total_expenses: int = Field(serialization_alias="totalExpenses")
    total_amount: float = Field(serialization_alias="totalAmount")
    monthly_total: float = Field(serialization_alias="monthlyTotal")
    highest_expense: ExpenseTrackerExpenseSummaryResponse | None = Field(serialization_alias="highestExpense")
    recent_expenses: list[ExpenseTrackerExpenseSummaryResponse] = Field(serialization_alias="recentExpenses")
    average_expense: float = Field(serialization_alias="averageExpense")
    category_totals: list[ExpenseTrackerCategoryTotalResponse] = Field(serialization_alias="categoryTotals")

