from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.household_expense_splitter.db import HouseholdExpenseSplitterBase


def _uuid() -> str:
    return str(uuid4())


class HouseholdMember(HouseholdExpenseSplitterBase):
    __tablename__ = "Members"
    __table_args__ = (UniqueConstraint("userId", "name", name="uq_household_members_owner_name"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, index=True, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    paid_expenses: Mapped[list["HouseholdExpense"]] = relationship(back_populates="paid_by_member", foreign_keys="HouseholdExpense.paid_by_member_id")


class HouseholdExpense(HouseholdExpenseSplitterBase):
    __tablename__ = "Expenses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    category: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    paid_by_member_id: Mapped[str] = mapped_column("paidByMemberId", String(36), ForeignKey("Members.id"), index=True, nullable=False)
    split_method: Mapped[str] = mapped_column("splitMethod", String(20), index=True, nullable=False)
    expense_date: Mapped[str] = mapped_column("expenseDate", String(40), index=True, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    archived: Mapped[bool] = mapped_column(Boolean, index=True, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    paid_by_member: Mapped[HouseholdMember] = relationship(foreign_keys=[paid_by_member_id], back_populates="paid_expenses")
    participants: Mapped[list["ExpenseParticipant"]] = relationship(back_populates="expense", cascade="all, delete-orphan")


class ExpenseParticipant(HouseholdExpenseSplitterBase):
    __tablename__ = "ExpenseParticipants"
    __table_args__ = (UniqueConstraint("expenseId", "memberId", name="uq_expense_participants_expense_member"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    expense_id: Mapped[str] = mapped_column("expenseId", String(36), ForeignKey("Expenses.id"), index=True, nullable=False)
    member_id: Mapped[str] = mapped_column("memberId", String(36), ForeignKey("Members.id"), index=True, nullable=False)
    share_amount: Mapped[float] = mapped_column("shareAmount", Numeric(12, 2), nullable=False)

    expense: Mapped[HouseholdExpense] = relationship(back_populates="participants")
    member: Mapped[HouseholdMember] = relationship()


class HouseholdSettlement(HouseholdExpenseSplitterBase):
    __tablename__ = "Settlements"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    from_member_id: Mapped[str] = mapped_column("fromMemberId", String(36), ForeignKey("Members.id"), index=True, nullable=False)
    to_member_id: Mapped[str] = mapped_column("toMemberId", String(36), ForeignKey("Members.id"), index=True, nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    settlement_date: Mapped[str] = mapped_column("settlementDate", String(40), index=True, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    from_member: Mapped[HouseholdMember] = relationship(foreign_keys=[from_member_id])
    to_member: Mapped[HouseholdMember] = relationship(foreign_keys=[to_member_id])
