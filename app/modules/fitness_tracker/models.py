from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.fitness_tracker.db import FitnessTrackerBase


def _uuid() -> str:
    return str(uuid4())


class FitnessActivity(FitnessTrackerBase):
    __tablename__ = "FitnessActivities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    activity_type: Mapped[str] = mapped_column("activityType", String(40), index=True, nullable=False)
    default_duration_minutes: Mapped[int | None] = mapped_column("defaultDurationMinutes", Integer, nullable=True)
    intensity: Mapped[str] = mapped_column(String(40), default="moderate", server_default="moderate", nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="active", server_default="active", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    logs: Mapped[list["FitnessLog"]] = relationship(back_populates="activity", cascade="all, delete-orphan")


class FitnessLog(FitnessTrackerBase):
    __tablename__ = "FitnessLogs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    activity_id: Mapped[str] = mapped_column("activityId", String(36), ForeignKey("FitnessActivities.id"), index=True, nullable=False)
    log_date: Mapped[str] = mapped_column("logDate", String(40), index=True, nullable=False)
    duration_minutes: Mapped[int] = mapped_column("durationMinutes", Integer, nullable=False)
    intensity: Mapped[str] = mapped_column(String(40), default="moderate", server_default="moderate", nullable=False)
    effort: Mapped[int | None] = mapped_column(Integer, nullable=True)
    distance_value: Mapped[float | None] = mapped_column("distanceValue", Float, nullable=True)
    distance_unit: Mapped[str | None] = mapped_column("distanceUnit", String(20), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    activity: Mapped[FitnessActivity] = relationship(back_populates="logs")
