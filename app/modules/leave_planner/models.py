from datetime import date, datetime
from uuid import uuid4
from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Index, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.modules.leave_planner.db import LeavePlannerBase

def _uuid(): return str(uuid4())

class LeaveType(LeavePlannerBase):
    __tablename__ = "LeaveTypes"
    __table_args__ = (UniqueConstraint("userId", "name", name="uq_leave_types_user_name"), Index("ix_leave_types_user_active", "userId", "isActive"))
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    code: Mapped[str | None] = mapped_column(String(30))
    description: Mapped[str | None] = mapped_column(Text)
    annual_allowance_days: Mapped[float] = mapped_column("annualAllowanceDays", Float, nullable=False, default=0)
    carry_forward_days: Mapped[float] = mapped_column("carryForwardDays", Float, nullable=False, default=0)
    color_key: Mapped[str] = mapped_column("colorKey", String(30), nullable=False, default="blue")
    is_active: Mapped[bool] = mapped_column("isActive", Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    entries: Mapped[list["LeaveEntry"]] = relationship(back_populates="leave_type")

class LeaveEntry(LeavePlannerBase):
    __tablename__ = "LeaveEntries"
    __table_args__ = (Index("ix_leave_entries_user_dates", "userId", "startDate", "endDate"), Index("ix_leave_entries_user_status", "userId", "status"), Index("ix_leave_entries_user_type", "userId", "leaveTypeId"))
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    leave_type_id: Mapped[str] = mapped_column("leaveTypeId", String(36), ForeignKey("LeaveTypes.id"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    start_date: Mapped[date] = mapped_column("startDate", Date, index=True, nullable=False)
    end_date: Mapped[date] = mapped_column("endDate", Date, index=True, nullable=False)
    duration_days: Mapped[float] = mapped_column("durationDays", Float, nullable=False)
    day_type: Mapped[str] = mapped_column("dayType", String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), index=True, nullable=False)
    reason: Mapped[str | None] = mapped_column(String(500))
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    leave_type: Mapped[LeaveType] = relationship(back_populates="entries")
