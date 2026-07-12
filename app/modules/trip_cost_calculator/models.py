from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.trip_cost_calculator.db import TripCostBase


def _uuid() -> str:
    return str(uuid4())


class TripCostTrip(TripCostBase):
    __tablename__ = "TripCostTrips"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    start_location: Mapped[str | None] = mapped_column("startLocation", String(180), nullable=True)
    destination: Mapped[str] = mapped_column(String(180), nullable=False)
    start_date: Mapped[str | None] = mapped_column("startDate", String(40), nullable=True)
    end_date: Mapped[str | None] = mapped_column("endDate", String(40), nullable=True)
    travelers: Mapped[int] = mapped_column(Integer, default=1, server_default="1", nullable=False)
    vehicle: Mapped[str | None] = mapped_column(String(120), nullable=True)
    distance: Mapped[float] = mapped_column(Float, default=0, server_default="0", nullable=False)
    currency_code: Mapped[str] = mapped_column("currencyCode", String(3), default="USD", server_default="USD", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    expenses: Mapped[list["TripCostExpense"]] = relationship(back_populates="trip", cascade="all, delete-orphan")


class TripCostExpense(TripCostBase):
    __tablename__ = "TripCostExpenses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    trip_id: Mapped[str] = mapped_column("tripId", String(36), ForeignKey("TripCostTrips.id"), index=True, nullable=False)
    category: Mapped[str] = mapped_column(String(40), default="miscellaneous", server_default="miscellaneous", nullable=False)
    description: Mapped[str] = mapped_column(String(220), nullable=False)
    amount: Mapped[float] = mapped_column(Float, default=0, server_default="0", nullable=False)
    currency_code: Mapped[str] = mapped_column("currencyCode", String(3), default="USD", server_default="USD", nullable=False)
    expense_date: Mapped[str] = mapped_column("date", String(40), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    trip: Mapped[TripCostTrip] = relationship(back_populates="expenses")
