from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.parking_expense_tracker.db import ParkingExpenseBase


def _uuid() -> str:
    return str(uuid4())


class ParkingExpenseLocation(ParkingExpenseBase):
    __tablename__ = "ParkingExpenseLocations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    city: Mapped[str | None] = mapped_column(String(120), nullable=True)
    area: Mapped[str | None] = mapped_column(String(120), nullable=True)
    parking_type: Mapped[str] = mapped_column("parkingType", String(40), default="other", server_default="other", nullable=False)
    default_hourly_rate: Mapped[float | None] = mapped_column("defaultHourlyRate", Float, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    expenses: Mapped[list["ParkingExpenseEntry"]] = relationship(back_populates="location", cascade="all, delete-orphan")


class ParkingExpenseEntry(ParkingExpenseBase):
    __tablename__ = "ParkingExpenseEntries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    location_id: Mapped[str] = mapped_column("locationId", String(36), ForeignKey("ParkingExpenseLocations.id"), index=True, nullable=False)
    parked_at: Mapped[str] = mapped_column("date", String(40), nullable=False)
    start_time: Mapped[str | None] = mapped_column("startTime", String(20), nullable=True)
    end_time: Mapped[str | None] = mapped_column("endTime", String(20), nullable=True)
    duration_minutes: Mapped[int] = mapped_column("durationMinutes", Integer, default=0, server_default="0", nullable=False)
    amount: Mapped[float] = mapped_column(Float, default=0, server_default="0", nullable=False)
    currency_code: Mapped[str] = mapped_column("currencyCode", String(3), default="USD", server_default="USD", nullable=False)
    payment_method: Mapped[str] = mapped_column("paymentMethod", String(40), default="card", server_default="card", nullable=False)
    vehicle: Mapped[str | None] = mapped_column(String(120), nullable=True)
    purpose: Mapped[str | None] = mapped_column(String(180), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    location: Mapped[ParkingExpenseLocation] = relationship(back_populates="expenses")
