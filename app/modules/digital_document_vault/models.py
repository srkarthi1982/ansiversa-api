from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, LargeBinary, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.digital_document_vault.db import DigitalDocumentVaultBase


def _uuid() -> str:
    return str(uuid4())


class VaultCategory(DigitalDocumentVaultBase):
    __tablename__ = "Categories"
    __table_args__ = (UniqueConstraint("userId", "name", name="uq_vault_categories_owner_name"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    documents: Mapped[list["VaultDocument"]] = relationship(back_populates="category")


class VaultDocument(DigitalDocumentVaultBase):
    __tablename__ = "Documents"
    __table_args__ = (UniqueConstraint("userId", "storedFileName", name="uq_vault_documents_owner_stored_file"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    category_id: Mapped[str] = mapped_column("categoryId", String(36), ForeignKey("Categories.id"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    document_type: Mapped[str] = mapped_column("documentType", String(80), index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    tags: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_name: Mapped[str] = mapped_column("fileName", String(255), nullable=False)
    stored_file_name: Mapped[str] = mapped_column("storedFileName", String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column("mimeType", String(120), nullable=False)
    file_size: Mapped[int] = mapped_column("fileSize", Integer, nullable=False)
    file_blob: Mapped[bytes] = mapped_column("fileBlob", LargeBinary, nullable=False)
    issue_date: Mapped[str | None] = mapped_column("issueDate", String(40), nullable=True)
    expiry_date: Mapped[str | None] = mapped_column("expiryDate", String(40), index=True, nullable=True)
    uploaded_at: Mapped[datetime] = mapped_column("uploadedAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    category: Mapped[VaultCategory] = relationship(back_populates="documents")
