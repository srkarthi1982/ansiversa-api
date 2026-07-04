from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.task_prioritizer.db import TaskPrioritizerBase


class TaskPrioritizerTask(TaskPrioritizerBase):
    __tablename__ = "TaskPrioritizerTasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    platform_id: Mapped[str | None] = mapped_column("platformId", String(120), nullable=True)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    category: Mapped[str] = mapped_column(String(40), default="work", server_default="work", nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="inbox", server_default="inbox", nullable=False)
    due_date: Mapped[str | None] = mapped_column("dueDate", String(40), nullable=True)
    effort: Mapped[int] = mapped_column(Integer, default=3, server_default="3", nullable=False)
    impact: Mapped[int] = mapped_column(Integer, default=3, server_default="3", nullable=False)
    urgency: Mapped[int] = mapped_column(Integer, default=3, server_default="3", nullable=False)
    priority_score: Mapped[float] = mapped_column("priorityScore", Float, default=0, server_default="0", nullable=False)
    priority_label: Mapped[str] = mapped_column("priorityLabel", String(40), default="medium", server_default="medium", nullable=False)
    manual_override: Mapped[bool] = mapped_column("manualOverride", Boolean, default=False, server_default="0", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    priorities: Mapped[list["TaskPrioritizerTaskPriority"]] = relationship(back_populates="task", cascade="all, delete-orphan")
    history: Mapped[list["TaskPrioritizerPriorityHistory"]] = relationship(back_populates="task", cascade="all, delete-orphan")


class TaskPrioritizerTaskPriority(TaskPrioritizerBase):
    __tablename__ = "TaskPrioritizerTaskPriorities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    task_id: Mapped[int] = mapped_column("taskId", Integer, ForeignKey("TaskPrioritizerTasks.id"), index=True, nullable=False)
    priority_score: Mapped[float] = mapped_column("priorityScore", Float, nullable=False)
    priority_label: Mapped[str] = mapped_column("priorityLabel", String(40), nullable=False)
    source: Mapped[str] = mapped_column(String(40), default="system", server_default="system", nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)

    task: Mapped[TaskPrioritizerTask] = relationship(back_populates="priorities")


class TaskPrioritizerPriorityRule(TaskPrioritizerBase):
    __tablename__ = "TaskPrioritizerPriorityRules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    category: Mapped[str | None] = mapped_column(String(40), nullable=True)
    impact_weight: Mapped[float] = mapped_column("impactWeight", Float, default=2, server_default="2", nullable=False)
    urgency_weight: Mapped[float] = mapped_column("urgencyWeight", Float, default=2, server_default="2", nullable=False)
    effort_weight: Mapped[float] = mapped_column("effortWeight", Float, default=1, server_default="1", nullable=False)
    due_date_weight: Mapped[float] = mapped_column("dueDateWeight", Float, default=2, server_default="2", nullable=False)
    is_enabled: Mapped[bool] = mapped_column("isEnabled", Boolean, default=True, server_default="1", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class TaskPrioritizerPriorityHistory(TaskPrioritizerBase):
    __tablename__ = "TaskPrioritizerPriorityHistory"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    task_id: Mapped[int | None] = mapped_column("taskId", Integer, ForeignKey("TaskPrioritizerTasks.id"), index=True, nullable=True)
    action_type: Mapped[str] = mapped_column("actionType", String(40), nullable=False)
    previous_priority: Mapped[str | None] = mapped_column("previousPriority", String(40), nullable=True)
    new_priority: Mapped[str | None] = mapped_column("newPriority", String(40), nullable=True)
    priority_score: Mapped[float | None] = mapped_column("priorityScore", Float, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)

    task: Mapped[TaskPrioritizerTask | None] = relationship(back_populates="history")
