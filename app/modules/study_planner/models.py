from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.study_planner.db import StudyPlannerBase


class StudyPlan(StudyPlannerBase):
    __tablename__ = "StudyPlans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column(
        "ownerId",
        String(36),
        index=True,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    subject: Mapped[str] = mapped_column(String(120), nullable=False)
    goal: Mapped[str] = mapped_column(Text, nullable=False)
    start_date: Mapped[date] = mapped_column("startDate", Date(), nullable=False)
    target_date: Mapped[date] = mapped_column("targetDate", Date(), nullable=False)
    status: Mapped[str] = mapped_column(
        String(40),
        default="active",
        server_default="active",
        nullable=False,
    )
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

    tasks: Mapped[list["StudyPlanTask"]] = relationship(
        back_populates="plan",
        cascade="all, delete-orphan",
    )
    logs: Mapped[list["StudyLog"]] = relationship(
        back_populates="plan",
        cascade="all, delete-orphan",
    )


class StudyPlanTask(StudyPlannerBase):
    __tablename__ = "StudyPlanTasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    plan_id: Mapped[int] = mapped_column(
        "planId",
        Integer,
        ForeignKey("StudyPlans.id"),
        index=True,
        nullable=False,
    )
    owner_id: Mapped[str] = mapped_column(
        "ownerId",
        String(36),
        index=True,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    due_date: Mapped[date | None] = mapped_column("dueDate", Date(), nullable=True)
    priority: Mapped[str] = mapped_column(
        String(20),
        default="medium",
        server_default="medium",
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(40),
        default="pending",
        server_default="pending",
        nullable=False,
    )
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

    plan: Mapped[StudyPlan] = relationship(back_populates="tasks")
    logs: Mapped[list["StudyLog"]] = relationship(back_populates="task")


class StudyLog(StudyPlannerBase):
    __tablename__ = "StudyLogs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    plan_id: Mapped[int] = mapped_column(
        "planId",
        Integer,
        ForeignKey("StudyPlans.id"),
        index=True,
        nullable=False,
    )
    task_id: Mapped[int | None] = mapped_column(
        "taskId",
        Integer,
        ForeignKey("StudyPlanTasks.id"),
        index=True,
        nullable=True,
    )
    owner_id: Mapped[str] = mapped_column(
        "ownerId",
        String(36),
        index=True,
        nullable=False,
    )
    study_date: Mapped[date] = mapped_column("studyDate", Date(), nullable=False)
    minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    focus: Mapped[str] = mapped_column(String(180), nullable=False)
    reflection: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        "createdAt",
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    plan: Mapped[StudyPlan] = relationship(back_populates="logs")
    task: Mapped[StudyPlanTask | None] = relationship(back_populates="logs")
