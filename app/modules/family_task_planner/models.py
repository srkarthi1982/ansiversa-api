from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.family_task_planner.db import FamilyTaskPlannerBase


def _uuid() -> str:
    return str(uuid4())


class FamilyTaskMember(FamilyTaskPlannerBase):
    __tablename__ = "FamilyTaskMembers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(140), nullable=False)
    color: Mapped[str | None] = mapped_column(String(40), nullable=True)
    avatar: Mapped[str | None] = mapped_column(String(80), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="active", server_default="active", nullable=False)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    tasks: Mapped[list["FamilyTask"]] = relationship(back_populates="member")


class FamilyTaskCategory(FamilyTaskPlannerBase):
    __tablename__ = "FamilyTaskCategories"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(140), nullable=False)
    color: Mapped[str | None] = mapped_column(String(40), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="active", server_default="active", nullable=False)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    tasks: Mapped[list["FamilyTask"]] = relationship(back_populates="category")


class FamilyTask(FamilyTaskPlannerBase):
    __tablename__ = "FamilyTasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    member_id: Mapped[str | None] = mapped_column("memberId", String(36), ForeignKey("FamilyTaskMembers.id"), index=True, nullable=True)
    category_id: Mapped[str | None] = mapped_column("categoryId", String(36), ForeignKey("FamilyTaskCategories.id"), index=True, nullable=True)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    priority: Mapped[str] = mapped_column(String(40), default="medium", server_default="medium", nullable=False)
    due_date: Mapped[str | None] = mapped_column("dueDate", String(40), nullable=True)
    recurring: Mapped[str] = mapped_column(String(40), default="none", server_default="none", nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="pending", server_default="pending", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    completed_at: Mapped[str | None] = mapped_column("completedAt", String(40), nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    member: Mapped[FamilyTaskMember | None] = relationship(back_populates="tasks")
    category: Mapped[FamilyTaskCategory | None] = relationship(back_populates="tasks")
