from datetime import date, datetime, time
from decimal import Decimal
from uuid import uuid4
from sqlalchemy import Date, DateTime, Integer, Numeric, String, Text, Time, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column
from app.modules.water_intake_tracker.db import WaterIntakeBase

def _uuid() -> str:
    return str(uuid4())

class WaterGoal(WaterIntakeBase):
    __tablename__ = 'WaterGoals'
    __table_args__ = (UniqueConstraint('userId', name='uq_water_goals_user_id'),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column('userId', String(36), index=True, nullable=False)
    daily_goal: Mapped[Decimal] = mapped_column('dailyGoal', Numeric(12, 2), nullable=False, default=Decimal('2000.00'))
    preferred_unit: Mapped[str] = mapped_column('preferredUnit', String(2), nullable=False, default='ml')
    created_at: Mapped[datetime] = mapped_column('createdAt', DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column('updatedAt', DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

class WaterEntry(WaterIntakeBase):
    __tablename__ = 'WaterEntries'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column('userId', String(36), index=True, nullable=False)
    entry_date: Mapped[date] = mapped_column('entryDate', Date, index=True, nullable=False)
    entry_time: Mapped[time] = mapped_column('entryTime', Time, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    unit: Mapped[str] = mapped_column(String(2), nullable=False, default='ml')
    drink_type: Mapped[str] = mapped_column('drinkType', String(80), index=True, nullable=False, default='Water')
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column('createdAt', DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column('updatedAt', DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
