from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.career_planner.db import CareerPlannerBase


class CareerGoal(CareerPlannerBase):
    __tablename__ = "CareerGoals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    target_role: Mapped[str | None] = mapped_column("targetRole", String(180), nullable=True)
    time_horizon: Mapped[str] = mapped_column("timeHorizon", String(80), default="12 months", server_default="12 months", nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="active", server_default="active", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        "createdAt",
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        "updatedAt",
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    roadmaps: Mapped[list["CareerRoadmap"]] = relationship(
        back_populates="goal",
        cascade="all, delete-orphan",
    )
    review_history: Mapped[list["CareerReviewHistoryItem"]] = relationship(
        back_populates="goal",
        cascade="all, delete-orphan",
    )


class CareerRoadmap(CareerPlannerBase):
    __tablename__ = "CareerRoadmaps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    goal_id: Mapped[int] = mapped_column(
        "goalId",
        Integer,
        ForeignKey("CareerGoals.id"),
        index=True,
        nullable=False,
    )
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    focus_area: Mapped[str] = mapped_column("focusArea", String(120), default="skills", server_default="skills", nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="planned", server_default="planned", nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column("sortOrder", Integer, default=0, server_default="0", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        "createdAt",
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        "updatedAt",
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    goal: Mapped[CareerGoal] = relationship(back_populates="roadmaps")
    milestones: Mapped[list["CareerMilestone"]] = relationship(
        back_populates="roadmap",
        cascade="all, delete-orphan",
    )


class CareerMilestone(CareerPlannerBase):
    __tablename__ = "CareerMilestones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    roadmap_id: Mapped[int] = mapped_column(
        "roadmapId",
        Integer,
        ForeignKey("CareerRoadmaps.id"),
        index=True,
        nullable=False,
    )
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    due_date: Mapped[str | None] = mapped_column("dueDate", String(40), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="todo", server_default="todo", nullable=False)
    success_metric: Mapped[str | None] = mapped_column("successMetric", String(240), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column("sortOrder", Integer, default=0, server_default="0", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        "createdAt",
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        "updatedAt",
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    roadmap: Mapped[CareerRoadmap] = relationship(back_populates="milestones")


class CareerReviewHistoryItem(CareerPlannerBase):
    __tablename__ = "CareerReviewHistory"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    goal_id: Mapped[int | None] = mapped_column(
        "goalId",
        Integer,
        ForeignKey("CareerGoals.id"),
        index=True,
        nullable=True,
    )
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    action_type: Mapped[str] = mapped_column("actionType", String(60), default="reviewed", server_default="reviewed", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        "createdAt",
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        "updatedAt",
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    goal: Mapped[CareerGoal | None] = relationship(back_populates="review_history")
