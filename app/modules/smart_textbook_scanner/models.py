from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.smart_textbook_scanner.db import SmartTextbookScannerBase


class TextbookScan(SmartTextbookScannerBase):
    __tablename__ = "TextbookScans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    subject: Mapped[str] = mapped_column(String(120), nullable=False)
    source: Mapped[str | None] = mapped_column(String(180), nullable=True)
    goal: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        String(40),
        default="scanning",
        server_default="scanning",
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

    pages: Mapped[list["TextbookPage"]] = relationship(
        back_populates="scan",
        cascade="all, delete-orphan",
    )
    notes: Mapped[list["ExtractedNote"]] = relationship(
        back_populates="scan",
        cascade="all, delete-orphan",
    )


class TextbookPage(SmartTextbookScannerBase):
    __tablename__ = "TextbookPages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    scan_id: Mapped[int] = mapped_column(
        "scanId",
        Integer,
        ForeignKey("TextbookScans.id"),
        index=True,
        nullable=False,
    )
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    page_number: Mapped[int] = mapped_column("pageNumber", Integer, nullable=False)
    title: Mapped[str | None] = mapped_column(String(180), nullable=True)
    page_text: Mapped[str] = mapped_column("pageText", Text, nullable=False)
    status: Mapped[str] = mapped_column(
        String(40),
        default="captured",
        server_default="captured",
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

    scan: Mapped[TextbookScan] = relationship(back_populates="pages")
    notes: Mapped[list["ExtractedNote"]] = relationship(back_populates="page")


class ExtractedNote(SmartTextbookScannerBase):
    __tablename__ = "ExtractedNotes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    scan_id: Mapped[int] = mapped_column(
        "scanId",
        Integer,
        ForeignKey("TextbookScans.id"),
        index=True,
        nullable=False,
    )
    page_id: Mapped[int] = mapped_column(
        "pageId",
        Integer,
        ForeignKey("TextbookPages.id"),
        index=True,
        nullable=False,
    )
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    heading: Mapped[str] = mapped_column(String(180), nullable=False)
    key_points: Mapped[str] = mapped_column("keyPoints", Text, nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    note_type: Mapped[str] = mapped_column(
        "noteType",
        String(40),
        default="keyPoints",
        server_default="keyPoints",
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        "createdAt",
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    scan: Mapped[TextbookScan] = relationship(back_populates="notes")
    page: Mapped[TextbookPage] = relationship(back_populates="notes")
