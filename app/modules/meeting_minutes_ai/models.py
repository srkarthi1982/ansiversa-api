from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.meeting_minutes_ai.db import MeetingMinutesAiBase


class MeetingRecord(MeetingMinutesAiBase):
    __tablename__ = "MeetingMinutesMeetings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    meeting_date: Mapped[date | None] = mapped_column("meetingDate", Date(), nullable=True)
    participants: Mapped[str | None] = mapped_column(Text, nullable=True)
    context: Mapped[str | None] = mapped_column(Text, nullable=True)
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

    notes: Mapped[list["MeetingNote"]] = relationship(
        back_populates="meeting",
        cascade="all, delete-orphan",
    )
    action_items: Mapped[list["MeetingActionItem"]] = relationship(
        back_populates="meeting",
        cascade="all, delete-orphan",
    )
    summaries: Mapped[list["MeetingSummary"]] = relationship(
        back_populates="meeting",
        cascade="all, delete-orphan",
    )


class MeetingNote(MeetingMinutesAiBase):
    __tablename__ = "MeetingMinutesNotes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    meeting_id: Mapped[int] = mapped_column(
        "meetingId",
        Integer,
        ForeignKey("MeetingMinutesMeetings.id"),
        index=True,
        nullable=False,
    )
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    note_type: Mapped[str] = mapped_column(
        "noteType",
        String(40),
        default="notes",
        server_default="notes",
        nullable=False,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
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

    meeting: Mapped[MeetingRecord] = relationship(back_populates="notes")


class MeetingActionItem(MeetingMinutesAiBase):
    __tablename__ = "MeetingMinutesActionItems"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    meeting_id: Mapped[int] = mapped_column(
        "meetingId",
        Integer,
        ForeignKey("MeetingMinutesMeetings.id"),
        index=True,
        nullable=False,
    )
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    owner_name: Mapped[str | None] = mapped_column("ownerName", String(140), nullable=True)
    due_date: Mapped[date | None] = mapped_column("dueDate", Date(), nullable=True)
    status: Mapped[str] = mapped_column(
        String(40),
        default="open",
        server_default="open",
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

    meeting: Mapped[MeetingRecord] = relationship(back_populates="action_items")


class MeetingSummary(MeetingMinutesAiBase):
    __tablename__ = "MeetingMinutesSummaries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    meeting_id: Mapped[int] = mapped_column(
        "meetingId",
        Integer,
        ForeignKey("MeetingMinutesMeetings.id"),
        index=True,
        nullable=False,
    )
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    summary_text: Mapped[str] = mapped_column("summaryText", Text, nullable=False)
    decisions: Mapped[str | None] = mapped_column(Text, nullable=True)
    risks: Mapped[str | None] = mapped_column(Text, nullable=True)
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

    meeting: Mapped[MeetingRecord] = relationship(back_populates="summaries")
