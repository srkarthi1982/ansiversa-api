from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.speech_writer.db import SpeechWriterBase


class SpeechProject(SpeechWriterBase):
    __tablename__ = "SpeechProjects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    platform_id: Mapped[str | None] = mapped_column("platformId", String(120), nullable=True)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    occasion: Mapped[str | None] = mapped_column(String(120), nullable=True)
    event_date: Mapped[str | None] = mapped_column("eventDate", String(40), nullable=True)
    audience: Mapped[str | None] = mapped_column(String(180), nullable=True)
    tone: Mapped[str | None] = mapped_column(String(80), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="draft", server_default="draft", nullable=False)
    purpose: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    speeches: Mapped[list["Speech"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    templates: Mapped[list["SpeechTemplate"]] = relationship(back_populates="project", cascade="all, delete-orphan")


class Speech(SpeechWriterBase):
    __tablename__ = "Speeches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    platform_id: Mapped[str | None] = mapped_column("platformId", String(120), nullable=True)
    project_id: Mapped[int] = mapped_column("projectId", Integer, ForeignKey("SpeechProjects.id"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    speaker_name: Mapped[str | None] = mapped_column("speakerName", String(140), nullable=True)
    occasion: Mapped[str | None] = mapped_column(String(120), nullable=True)
    duration_minutes: Mapped[int | None] = mapped_column("durationMinutes", Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="draft", server_default="draft", nullable=False)
    key_message: Mapped[str | None] = mapped_column("keyMessage", Text, nullable=True)
    speech_text: Mapped[str | None] = mapped_column("speechText", Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    project: Mapped[SpeechProject] = relationship(back_populates="speeches")
    history: Mapped[list["SpeechHistory"]] = relationship(back_populates="speech", cascade="all, delete-orphan")


class SpeechTemplate(SpeechWriterBase):
    __tablename__ = "SpeechTemplates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    platform_id: Mapped[str | None] = mapped_column("platformId", String(120), nullable=True)
    project_id: Mapped[int] = mapped_column("projectId", Integer, ForeignKey("SpeechProjects.id"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    occasion: Mapped[str | None] = mapped_column(String(120), nullable=True)
    tone: Mapped[str | None] = mapped_column(String(80), nullable=True)
    template_text: Mapped[str | None] = mapped_column("templateText", Text, nullable=True)
    usage_notes: Mapped[str | None] = mapped_column("usageNotes", Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    project: Mapped[SpeechProject] = relationship(back_populates="templates")


class SpeechHistory(SpeechWriterBase):
    __tablename__ = "SpeechHistory"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    platform_id: Mapped[str | None] = mapped_column("platformId", String(120), nullable=True)
    speech_id: Mapped[int] = mapped_column("speechId", Integer, ForeignKey("Speeches.id"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    event_type: Mapped[str | None] = mapped_column("eventType", String(80), nullable=True)
    occurred_at: Mapped[str | None] = mapped_column("occurredAt", String(40), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    revision_notes: Mapped[str | None] = mapped_column("revisionNotes", Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    speech: Mapped[Speech] = relationship(back_populates="history")
