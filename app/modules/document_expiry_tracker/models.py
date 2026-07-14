from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.document_expiry_tracker.db import DocumentExpiryBase


def _uuid() -> str:
    return str(uuid4())


class DocumentRecord(DocumentExpiryBase):
    __tablename__ = "Documents"
    __table_args__ = (
        UniqueConstraint("userId", "title", "documentType", name="uq_documents_owner_title_type"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    document_type: Mapped[str] = mapped_column("documentType", String(80), index=True, nullable=False)
    document_number: Mapped[str | None] = mapped_column("documentNumber", String(120), nullable=True)
    issuing_authority: Mapped[str | None] = mapped_column("issuingAuthority", String(180), nullable=True)
    country: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    issue_date: Mapped[str | None] = mapped_column("issueDate", String(40), nullable=True)
    expiry_date: Mapped[str | None] = mapped_column("expiryDate", String(40), index=True, nullable=True)
    renewal_reminder_days: Mapped[int] = mapped_column("renewalReminderDays", Integer, default=30, server_default="30", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    tags: Mapped[str | None] = mapped_column(Text, nullable=True)
    archived: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0", index=True, nullable=False)
    renewal_count: Mapped[int] = mapped_column("renewalCount", Integer, default=0, server_default="0", nullable=False)
    last_renewed_at: Mapped[str | None] = mapped_column("lastRenewedAt", String(40), nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
