from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.course_tracker.db import CourseTrackerBase


class Course(CourseTrackerBase):
    __tablename__ = "Courses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column(
        "ownerId",
        String(36),
        index=True,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    provider: Mapped[str] = mapped_column(String(120), nullable=False)
    category: Mapped[str | None] = mapped_column(String(120), nullable=True)
    goal: Mapped[str] = mapped_column(Text, nullable=False)
    start_date: Mapped[date] = mapped_column("startDate", Date(), nullable=False)
    target_date: Mapped[date | None] = mapped_column("targetDate", Date(), nullable=True)
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

    modules: Mapped[list["CourseModule"]] = relationship(
        back_populates="course",
        cascade="all, delete-orphan",
    )
    progress_logs: Mapped[list["CourseProgressLog"]] = relationship(
        back_populates="course",
        cascade="all, delete-orphan",
    )


class CourseModule(CourseTrackerBase):
    __tablename__ = "CourseModules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    course_id: Mapped[int] = mapped_column(
        "courseId",
        Integer,
        ForeignKey("Courses.id"),
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
    sequence: Mapped[int] = mapped_column(Integer, default=1, server_default="1", nullable=False)
    status: Mapped[str] = mapped_column(
        String(40),
        default="notStarted",
        server_default="notStarted",
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

    course: Mapped[Course] = relationship(back_populates="modules")
    progress_logs: Mapped[list["CourseProgressLog"]] = relationship(back_populates="module")


class CourseProgressLog(CourseTrackerBase):
    __tablename__ = "CourseProgressLogs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    course_id: Mapped[int] = mapped_column(
        "courseId",
        Integer,
        ForeignKey("Courses.id"),
        index=True,
        nullable=False,
    )
    module_id: Mapped[int | None] = mapped_column(
        "moduleId",
        Integer,
        ForeignKey("CourseModules.id"),
        index=True,
        nullable=True,
    )
    owner_id: Mapped[str] = mapped_column(
        "ownerId",
        String(36),
        index=True,
        nullable=False,
    )
    progress_date: Mapped[date] = mapped_column("progressDate", Date(), nullable=False)
    minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    summary: Mapped[str] = mapped_column(String(240), nullable=False)
    reflection: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        "createdAt",
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    course: Mapped[Course] = relationship(back_populates="progress_logs")
    module: Mapped[CourseModule | None] = relationship(back_populates="progress_logs")
