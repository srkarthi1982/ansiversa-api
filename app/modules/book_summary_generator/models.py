from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.book_summary_generator.db import BookSummaryGeneratorBase


class BookCollection(BookSummaryGeneratorBase):
    __tablename__ = "BookCollections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    platform_id: Mapped[str | None] = mapped_column("platformId", String(120), nullable=True)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    author: Mapped[str | None] = mapped_column(String(180), nullable=True)
    category: Mapped[str | None] = mapped_column(String(120), nullable=True)
    source_type: Mapped[str] = mapped_column("sourceType", String(40), default="manual", server_default="manual", nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="draft", server_default="draft", nullable=False)
    source_text: Mapped[str | None] = mapped_column("sourceText", Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    summaries: Mapped[list["BookSummary"]] = relationship(back_populates="book", cascade="all, delete-orphan")


class BookSummary(BookSummaryGeneratorBase):
    __tablename__ = "BookSummaries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    platform_id: Mapped[str | None] = mapped_column("platformId", String(120), nullable=True)
    book_id: Mapped[int] = mapped_column("bookId", Integer, ForeignKey("BookCollections.id"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    summary_type: Mapped[str] = mapped_column("summaryType", String(60), default="chapter", server_default="chapter", nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="draft", server_default="draft", nullable=False)
    summary_text: Mapped[str | None] = mapped_column("summaryText", Text, nullable=True)
    key_points: Mapped[str | None] = mapped_column("keyPoints", Text, nullable=True)
    action_items: Mapped[str | None] = mapped_column("actionItems", Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    book: Mapped[BookCollection] = relationship(back_populates="summaries")
    notes: Mapped[list["SummaryNote"]] = relationship(back_populates="summary", cascade="all, delete-orphan")
    history: Mapped[list["SummaryHistory"]] = relationship(back_populates="summary", cascade="all, delete-orphan")


class SummaryNote(BookSummaryGeneratorBase):
    __tablename__ = "SummaryNotes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    platform_id: Mapped[str | None] = mapped_column("platformId", String(120), nullable=True)
    summary_id: Mapped[int] = mapped_column("summaryId", Integer, ForeignKey("BookSummaries.id"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    note_type: Mapped[str] = mapped_column("noteType", String(60), default="note", server_default="note", nullable=False)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    highlight: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    summary: Mapped[BookSummary] = relationship(back_populates="notes")


class SummaryHistory(BookSummaryGeneratorBase):
    __tablename__ = "SummaryHistory"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    platform_id: Mapped[str | None] = mapped_column("platformId", String(120), nullable=True)
    summary_id: Mapped[int] = mapped_column("summaryId", Integer, ForeignKey("BookSummaries.id"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    event_type: Mapped[str | None] = mapped_column("eventType", String(80), nullable=True)
    occurred_at: Mapped[str | None] = mapped_column("occurredAt", String(40), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    revision_notes: Mapped[str | None] = mapped_column("revisionNotes", Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    summary: Mapped[BookSummary] = relationship(back_populates="history")
