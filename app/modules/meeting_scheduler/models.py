from datetime import date, datetime, time
from uuid import uuid4

from sqlalchemy import Date, DateTime, ForeignKey, Index, Integer, String, Text, Time, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.meeting_scheduler.db import MeetingSchedulerBase


def _uuid() -> str:
    return str(uuid4())


class Meeting(MeetingSchedulerBase):
    __tablename__ = "Meetings"
    __table_args__ = (Index("ix_meetings_user_date", "userId", "meetingDate"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    meeting_date: Mapped[date] = mapped_column("meetingDate", Date, index=True, nullable=False)
    start_time: Mapped[time] = mapped_column("startTime", Time, nullable=False)
    end_time: Mapped[time] = mapped_column("endTime", Time, nullable=False)
    timezone: Mapped[str] = mapped_column(String(80), nullable=False)
    location: Mapped[str | None] = mapped_column(String(300))
    meeting_type: Mapped[str] = mapped_column("meetingType", String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), index=True, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    participants: Mapped[list["MeetingParticipant"]] = relationship(back_populates="meeting", cascade="all, delete-orphan")
    agenda_items: Mapped[list["MeetingAgendaItem"]] = relationship(back_populates="meeting", cascade="all, delete-orphan")


class MeetingParticipant(MeetingSchedulerBase):
    __tablename__ = "MeetingParticipants"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    meeting_id: Mapped[str] = mapped_column("meetingId", String(36), ForeignKey("Meetings.id", ondelete="CASCADE"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    email: Mapped[str | None] = mapped_column(String(254))
    role: Mapped[str | None] = mapped_column(String(120))
    response_status: Mapped[str] = mapped_column("responseStatus", String(20), index=True, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    meeting: Mapped[Meeting] = relationship(back_populates="participants")


class MeetingAgendaItem(MeetingSchedulerBase):
    __tablename__ = "MeetingAgendaItems"
    __table_args__ = (Index("ix_meeting_agenda_order", "meetingId", "sortOrder"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    meeting_id: Mapped[str] = mapped_column("meetingId", String(36), ForeignKey("Meetings.id", ondelete="CASCADE"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    duration_minutes: Mapped[int] = mapped_column("durationMinutes", Integer, nullable=False)
    sort_order: Mapped[int] = mapped_column("sortOrder", Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    meeting: Mapped[Meeting] = relationship(back_populates="agenda_items")
