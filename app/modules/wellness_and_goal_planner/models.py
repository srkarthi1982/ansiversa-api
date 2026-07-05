from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.wellness_and_goal_planner.db import WellnessAndGoalPlannerBase


class WellnessArea(WellnessAndGoalPlannerBase):
    __tablename__ = "WellnessAreas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    color: Mapped[str] = mapped_column(String(40), default="#2f6f73", server_default="#2f6f73", nullable=False)
    icon: Mapped[str | None] = mapped_column(String(60), nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    goals: Mapped[list["WellnessGoal"]] = relationship(back_populates="area")


class WellnessGoal(WellnessAndGoalPlannerBase):
    __tablename__ = "WellnessGoals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    area_id: Mapped[int | None] = mapped_column("areaId", Integer, ForeignKey("WellnessAreas.id"), index=True, nullable=True)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    target_date: Mapped[str | None] = mapped_column("targetDate", String(40), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="active", server_default="active", nullable=False)
    priority: Mapped[str] = mapped_column(String(40), default="medium", server_default="medium", nullable=False)
    progress: Mapped[int] = mapped_column(Integer, default=0, server_default="0", nullable=False)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    area: Mapped[WellnessArea | None] = relationship(back_populates="goals")
    reflections: Mapped[list["WellnessReflection"]] = relationship(back_populates="goal")


class WellnessReflection(WellnessAndGoalPlannerBase):
    __tablename__ = "WellnessReflections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    goal_id: Mapped[int | None] = mapped_column("goalId", Integer, ForeignKey("WellnessGoals.id"), index=True, nullable=True)
    reflection_date: Mapped[str] = mapped_column("reflectionDate", String(40), nullable=False)
    reflection: Mapped[str] = mapped_column(Text, nullable=False)
    mood: Mapped[str] = mapped_column(String(40), default="steady", server_default="steady", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    goal: Mapped[WellnessGoal | None] = relationship(back_populates="reflections")
