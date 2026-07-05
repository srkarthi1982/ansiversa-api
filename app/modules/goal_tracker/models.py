from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.goal_tracker.db import GoalTrackerBase


def _uuid() -> str:
    return str(uuid4())


class GoalTrackerGoal(GoalTrackerBase):
    __tablename__ = "GoalTrackerGoals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    category: Mapped[str | None] = mapped_column(String(80), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    target_date: Mapped[str | None] = mapped_column("targetDate", String(40), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="active", server_default="active", nullable=False)
    priority: Mapped[str] = mapped_column(String(40), default="medium", server_default="medium", nullable=False)
    progress: Mapped[int] = mapped_column("progressPercent", Integer, default=0, server_default="0", nullable=False)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    milestones: Mapped[list["GoalTrackerMilestone"]] = relationship(back_populates="goal", cascade="all, delete-orphan")
    check_ins: Mapped[list["GoalTrackerCheckIn"]] = relationship(back_populates="goal", cascade="all, delete-orphan")


class GoalTrackerMilestone(GoalTrackerBase):
    __tablename__ = "GoalTrackerMilestones"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    goal_id: Mapped[str] = mapped_column("goalId", String(36), ForeignKey("GoalTrackerGoals.id"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    target_date: Mapped[str | None] = mapped_column("targetDate", String(40), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="pending", server_default="pending", nullable=False)
    sort_order: Mapped[int] = mapped_column("sortOrder", Integer, default=0, server_default="0", nullable=False)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    goal: Mapped[GoalTrackerGoal] = relationship(back_populates="milestones")


class GoalTrackerCheckIn(GoalTrackerBase):
    __tablename__ = "GoalTrackerCheckIns"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    goal_id: Mapped[str] = mapped_column("goalId", String(36), ForeignKey("GoalTrackerGoals.id"), index=True, nullable=False)
    check_in_date: Mapped[str] = mapped_column("checkInDate", String(40), nullable=False)
    progress: Mapped[int] = mapped_column("progressPercent", Integer, nullable=False)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    mood: Mapped[str] = mapped_column(String(40), default="steady", server_default="steady", nullable=False)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)

    goal: Mapped[GoalTrackerGoal] = relationship(back_populates="check_ins")
