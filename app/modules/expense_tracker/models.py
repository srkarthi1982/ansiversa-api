from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.expense_tracker.db import ExpenseTrackerBase


class ExpenseTrackerCategory(ExpenseTrackerBase):
    __tablename__ = "ExpenseTrackerCategories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    color: Mapped[str] = mapped_column(String(40), default="#2f6f73", server_default="#2f6f73", nullable=False)
    is_archived: Mapped[bool] = mapped_column("isArchived", Boolean, default=False, server_default="0", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    expenses: Mapped[list["ExpenseTrackerExpense"]] = relationship(back_populates="category")


class ExpenseTrackerExpense(ExpenseTrackerBase):
    __tablename__ = "ExpenseTrackerExpenses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    category_id: Mapped[int | None] = mapped_column("categoryId", Integer, ForeignKey("ExpenseTrackerCategories.id"), index=True, nullable=True)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(8), default="AED", server_default="AED", nullable=False)
    expense_date: Mapped[str] = mapped_column("expenseDate", String(40), nullable=False)
    payment_method: Mapped[str] = mapped_column("paymentMethod", String(40), default="card", server_default="card", nullable=False)
    merchant: Mapped[str | None] = mapped_column(String(160), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    category: Mapped[ExpenseTrackerCategory | None] = relationship(back_populates="expenses")
    history: Mapped[list["ExpenseTrackerHistory"]] = relationship(back_populates="expense")


class ExpenseTrackerHistory(ExpenseTrackerBase):
    __tablename__ = "ExpenseTrackerHistory"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    expense_id: Mapped[int | None] = mapped_column("expenseId", Integer, ForeignKey("ExpenseTrackerExpenses.id"), index=True, nullable=True)
    category_id: Mapped[int | None] = mapped_column("categoryId", Integer, ForeignKey("ExpenseTrackerCategories.id"), index=True, nullable=True)
    action_type: Mapped[str] = mapped_column("actionType", String(40), nullable=False)
    title: Mapped[str | None] = mapped_column(String(180), nullable=True)
    amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    currency: Mapped[str | None] = mapped_column(String(8), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)

    expense: Mapped[ExpenseTrackerExpense | None] = relationship(back_populates="history")

