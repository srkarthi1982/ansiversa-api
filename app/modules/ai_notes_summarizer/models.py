from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.ai_notes_summarizer.db import AiNotesSummarizerBase


class NotesDocument(AiNotesSummarizerBase):
    __tablename__ = "NotesDocuments"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    owner_id: Mapped[str] = mapped_column(
        "ownerId",
        String(36),
        index=True,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    source_type: Mapped[str] = mapped_column(
        "sourceType",
        String(40),
        default="paste",
        server_default="paste",
        nullable=False,
    )
    source_meta: Mapped[str | None] = mapped_column("sourceMeta", Text, nullable=True)
    tags: Mapped[str | None] = mapped_column(Text, nullable=True)
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

    summaries: Mapped[list["NoteSummary"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
    )
    jobs: Mapped[list["SummaryJob"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
    )


class NoteSummary(AiNotesSummarizerBase):
    __tablename__ = "NoteSummaries"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    document_id: Mapped[int] = mapped_column(
        "documentId",
        Integer,
        ForeignKey("NotesDocuments.id"),
        index=True,
        nullable=False,
    )
    owner_id: Mapped[str] = mapped_column(
        "ownerId",
        String(36),
        index=True,
        nullable=False,
    )
    summary_type: Mapped[str] = mapped_column(
        "summaryType",
        String(40),
        default="standard",
        server_default="standard",
        nullable=False,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    original_length: Mapped[int | None] = mapped_column(
        "originalLength",
        Integer,
        nullable=True,
    )
    summary_length: Mapped[int | None] = mapped_column(
        "summaryLength",
        Integer,
        nullable=True,
    )
    meta: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        "createdAt",
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    document: Mapped[NotesDocument] = relationship(back_populates="summaries")


class SummaryJob(AiNotesSummarizerBase):
    __tablename__ = "SummaryJobs"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    document_id: Mapped[int | None] = mapped_column(
        "documentId",
        Integer,
        ForeignKey("NotesDocuments.id"),
        index=True,
        nullable=True,
    )
    owner_id: Mapped[str] = mapped_column(
        "ownerId",
        String(36),
        index=True,
        nullable=False,
    )
    job_type: Mapped[str] = mapped_column("jobType", String(80), nullable=False)
    input: Mapped[str | None] = mapped_column(Text, nullable=True)
    output: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        "createdAt",
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    document: Mapped[NotesDocument] = relationship(back_populates="jobs")
