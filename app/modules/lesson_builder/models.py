from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.lesson_builder.db import LessonBuilderBase


class LessonPlan(LessonBuilderBase):
    __tablename__ = "LessonPlans"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    user_id: Mapped[str] = mapped_column(
        "userId",
        String(36),
        index=True,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    subject: Mapped[str] = mapped_column(String(140), nullable=False)
    audience: Mapped[str] = mapped_column(String(140), nullable=False)
    duration_minutes: Mapped[int] = mapped_column(
        "durationMinutes",
        Integer,
        nullable=False,
    )
    objective: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        String(40),
        default="draft",
        server_default="draft",
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
    published_at: Mapped[datetime | None] = mapped_column(
        "publishedAt",
        DateTime(timezone=True),
        nullable=True,
    )

    sections: Mapped[list["LessonSection"]] = relationship(
        back_populates="lesson",
        cascade="all, delete-orphan",
    )


class LessonSection(LessonBuilderBase):
    __tablename__ = "LessonSections"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    lesson_id: Mapped[str] = mapped_column(
        "lessonId",
        String(36),
        ForeignKey("LessonPlans.id"),
        index=True,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    section_type: Mapped[str] = mapped_column(
        "sectionType",
        String(60),
        nullable=False,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
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

    lesson: Mapped[LessonPlan] = relationship(back_populates="sections")
