from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.project_tracker.db import ProjectTrackerBase


class ProjectTrackerProject(ProjectTrackerBase):
    __tablename__ = "ProjectTrackerProjects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    platform_id: Mapped[str | None] = mapped_column("platformId", String(120), nullable=True)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    owner_name: Mapped[str | None] = mapped_column("ownerName", String(120), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="planning", server_default="planning", nullable=False)
    priority: Mapped[str] = mapped_column(String(40), default="medium", server_default="medium", nullable=False)
    due_date: Mapped[str | None] = mapped_column("dueDate", String(40), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    tasks: Mapped[list["ProjectTrackerTask"]] = relationship(back_populates="project", cascade="all, delete-orphan")


class ProjectTrackerTask(ProjectTrackerBase):
    __tablename__ = "ProjectTrackerTasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    platform_id: Mapped[str | None] = mapped_column("platformId", String(120), nullable=True)
    project_id: Mapped[int] = mapped_column("projectId", Integer, ForeignKey("ProjectTrackerProjects.id"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="todo", server_default="todo", nullable=False)
    priority: Mapped[str] = mapped_column(String(40), default="medium", server_default="medium", nullable=False)
    due_date: Mapped[str | None] = mapped_column("dueDate", String(40), nullable=True)
    estimate_hours: Mapped[float | None] = mapped_column("estimateHours", Float, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    project: Mapped[ProjectTrackerProject] = relationship(back_populates="tasks")
