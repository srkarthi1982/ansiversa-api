from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.wellness_and_goal_planner.db import WellnessAndGoalPlannerBase


def _uuid() -> str:
    return str(uuid4())


class WellnessArea(WellnessAndGoalPlannerBase):
    __tablename__ = "WellnessAreas"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    icon: Mapped[str | None] = mapped_column(String(60), nullable=True)
    sort_order: Mapped[int | None] = mapped_column("sortOrder", Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    goals: Mapped[list["WellnessGoal"]] = relationship(back_populates="area")


class WellnessGoal(WellnessAndGoalPlannerBase):
    __tablename__ = "WellnessGoals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    area_id: Mapped[str | None] = mapped_column("areaId", String(36), ForeignKey("WellnessAreas.id"), index=True, nullable=True)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    target_date: Mapped[str | None] = mapped_column("targetDate", String(40), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="active", server_default="active", nullable=False)
    priority: Mapped[str] = mapped_column(String(40), default="medium", server_default="medium", nullable=False)
    progress: Mapped[int] = mapped_column("progressPercent", Integer, default=0, server_default="0", nullable=False)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    area: Mapped[WellnessArea | None] = relationship(back_populates="goals")
    reflections: Mapped[list["WellnessReflection"]] = relationship(back_populates="goal")


class WellnessReflection(WellnessAndGoalPlannerBase):
    __tablename__ = "WellnessReflections"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    area_id: Mapped[str | None] = mapped_column("areaId", String(36), ForeignKey("WellnessAreas.id"), index=True, nullable=True)
    goal_id: Mapped[str | None] = mapped_column("goalId", String(36), ForeignKey("WellnessGoals.id"), index=True, nullable=True)
    reflection_date: Mapped[str] = mapped_column("entryDate", String(40), nullable=False)
    reflection_text: Mapped[str | None] = mapped_column("reflection", Text, nullable=True)
    mood: Mapped[str] = mapped_column(String(40), default="steady", server_default="steady", nullable=False)
    energy_level: Mapped[int | None] = mapped_column("energyLevel", Integer, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)

    goal: Mapped[WellnessGoal | None] = relationship(back_populates="reflections")
