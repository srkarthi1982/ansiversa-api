from datetime import date, datetime
from uuid import uuid4

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship as orm_relationship

from app.modules.home_maintenance_planner.db import HomeMaintenanceBase


def _uuid() -> str:
    return str(uuid4())


class MaintenanceArea(HomeMaintenanceBase):
    __tablename__ = "MaintenanceAreas"
    __table_args__ = (UniqueConstraint("userId", "name", name="uq_maintenance_areas_owner_name"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column("sortOrder", Integer, nullable=False, default=0)
    is_system: Mapped[bool] = mapped_column("isSystem", Boolean, index=True, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    tasks: Mapped[list["MaintenanceTask"]] = orm_relationship(back_populates="area")


class MaintenanceCategory(HomeMaintenanceBase):
    __tablename__ = "MaintenanceCategories"
    __table_args__ = (UniqueConstraint("userId", "name", name="uq_maintenance_categories_owner_name"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column("sortOrder", Integer, nullable=False, default=0)
    is_system: Mapped[bool] = mapped_column("isSystem", Boolean, index=True, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    tasks: Mapped[list["MaintenanceTask"]] = orm_relationship(back_populates="category")


class MaintenanceTask(HomeMaintenanceBase):
    __tablename__ = "MaintenanceTasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    area_id: Mapped[str] = mapped_column("areaId", String(36), ForeignKey("MaintenanceAreas.id"), index=True, nullable=False)
    category_id: Mapped[str] = mapped_column("categoryId", String(36), ForeignKey("MaintenanceCategories.id"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    due_date: Mapped[date] = mapped_column("dueDate", Date, index=True, nullable=False)
    recurrence_type: Mapped[str] = mapped_column("recurrenceType", String(40), index=True, nullable=False, default="one_time")
    recurrence_interval: Mapped[int | None] = mapped_column("recurrenceInterval", Integer, nullable=True)
    priority: Mapped[str] = mapped_column(String(20), index=True, nullable=False, default="medium")
    estimated_cost: Mapped[float | None] = mapped_column("estimatedCost", Numeric(12, 2), nullable=True)
    actual_cost: Mapped[float | None] = mapped_column("actualCost", Numeric(12, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    provider_name: Mapped[str | None] = mapped_column("providerName", String(180), nullable=True)
    provider_phone: Mapped[str | None] = mapped_column("providerPhone", String(60), nullable=True)
    provider_email: Mapped[str | None] = mapped_column("providerEmail", String(180), nullable=True)
    reference_number: Mapped[str | None] = mapped_column("referenceNumber", String(120), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    completion_notes: Mapped[str | None] = mapped_column("completionNotes", Text, nullable=True)
    reminder_lead_days: Mapped[int] = mapped_column("reminderLeadDays", Integer, nullable=False, default=3)
    completed_at: Mapped[datetime | None] = mapped_column("completedAt", DateTime(timezone=True), nullable=True)
    archived: Mapped[bool] = mapped_column(Boolean, index=True, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    area: Mapped[MaintenanceArea] = orm_relationship(back_populates="tasks")
    category: Mapped[MaintenanceCategory] = orm_relationship(back_populates="tasks")
    completions: Mapped[list["MaintenanceTaskCompletion"]] = orm_relationship(back_populates="task", cascade="all, delete-orphan")


class MaintenanceTaskCompletion(HomeMaintenanceBase):
    __tablename__ = "MaintenanceTaskCompletions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    task_id: Mapped[str] = mapped_column("taskId", String(36), ForeignKey("MaintenanceTasks.id", ondelete="CASCADE"), index=True, nullable=False)
    completed_due_date: Mapped[date] = mapped_column("completedDueDate", Date, index=True, nullable=False)
    completed_at: Mapped[datetime] = mapped_column("completedAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    actual_cost: Mapped[float | None] = mapped_column("actualCost", Numeric(12, 2), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    task: Mapped[MaintenanceTask] = orm_relationship(back_populates="completions")

