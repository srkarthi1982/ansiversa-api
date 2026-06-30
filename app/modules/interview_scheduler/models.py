from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.interview_scheduler.db import InterviewSchedulerBase


class InterviewSchedule(InterviewSchedulerBase):
    __tablename__ = "InterviewSchedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    platform_id: Mapped[str | None] = mapped_column("platformId", String(120), nullable=True)
    candidate_name: Mapped[str] = mapped_column("candidateName", String(180), nullable=False)
    role_title: Mapped[str] = mapped_column("roleTitle", String(180), nullable=False)
    company_name: Mapped[str | None] = mapped_column("companyName", String(180), nullable=True)
    interview_stage: Mapped[str | None] = mapped_column("interviewStage", String(120), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="planned", server_default="planned", nullable=False)
    priority: Mapped[str] = mapped_column(String(40), default="medium", server_default="medium", nullable=False)
    target_date: Mapped[str | None] = mapped_column("targetDate", String(40), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    rounds: Mapped[list["InterviewRound"]] = relationship(back_populates="schedule", cascade="all, delete-orphan")
    calendar_events: Mapped[list["InterviewCalendarEvent"]] = relationship(back_populates="schedule", cascade="all, delete-orphan")
    history: Mapped[list["InterviewHistory"]] = relationship(back_populates="schedule", cascade="all, delete-orphan")


class InterviewRound(InterviewSchedulerBase):
    __tablename__ = "InterviewRounds"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    platform_id: Mapped[str | None] = mapped_column("platformId", String(120), nullable=True)
    schedule_id: Mapped[int] = mapped_column("scheduleId", Integer, ForeignKey("InterviewSchedules.id"), index=True, nullable=False)
    round_name: Mapped[str] = mapped_column("roundName", String(180), nullable=False)
    interviewer_name: Mapped[str | None] = mapped_column("interviewerName", String(180), nullable=True)
    interview_type: Mapped[str | None] = mapped_column("interviewType", String(120), nullable=True)
    sequence: Mapped[int] = mapped_column(Integer, default=1, server_default="1", nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="planned", server_default="planned", nullable=False)
    scheduled_at: Mapped[str | None] = mapped_column("scheduledAt", String(40), nullable=True)
    location: Mapped[str | None] = mapped_column(String(240), nullable=True)
    preparation_notes: Mapped[str | None] = mapped_column("preparationNotes", Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    schedule: Mapped[InterviewSchedule] = relationship(back_populates="rounds")
    calendar_events: Mapped[list["InterviewCalendarEvent"]] = relationship(back_populates="round", cascade="all, delete-orphan")


class InterviewCalendarEvent(InterviewSchedulerBase):
    __tablename__ = "InterviewCalendarEvents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    platform_id: Mapped[str | None] = mapped_column("platformId", String(120), nullable=True)
    schedule_id: Mapped[int] = mapped_column("scheduleId", Integer, ForeignKey("InterviewSchedules.id"), index=True, nullable=False)
    round_id: Mapped[int | None] = mapped_column("roundId", Integer, ForeignKey("InterviewRounds.id"), index=True, nullable=True)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    event_type: Mapped[str] = mapped_column("eventType", String(80), default="interview", server_default="interview", nullable=False)
    starts_at: Mapped[str] = mapped_column("startsAt", String(40), nullable=False)
    ends_at: Mapped[str | None] = mapped_column("endsAt", String(40), nullable=True)
    reminder_minutes: Mapped[int | None] = mapped_column("reminderMinutes", Integer, nullable=True)
    location: Mapped[str | None] = mapped_column(String(240), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    schedule: Mapped[InterviewSchedule] = relationship(back_populates="calendar_events")
    round: Mapped[InterviewRound | None] = relationship(back_populates="calendar_events")


class InterviewHistory(InterviewSchedulerBase):
    __tablename__ = "InterviewHistory"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    platform_id: Mapped[str | None] = mapped_column("platformId", String(120), nullable=True)
    schedule_id: Mapped[int] = mapped_column("scheduleId", Integer, ForeignKey("InterviewSchedules.id"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    outcome: Mapped[str | None] = mapped_column(String(120), nullable=True)
    completed_at: Mapped[str | None] = mapped_column("completedAt", String(40), nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    next_steps: Mapped[str | None] = mapped_column("nextSteps", Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    schedule: Mapped[InterviewSchedule] = relationship(back_populates="history")
