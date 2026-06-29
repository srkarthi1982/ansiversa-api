from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.invoice_receipt_maker.db import InvoiceReceiptBase


class InvoiceReceiptProject(InvoiceReceiptBase):
    __tablename__ = "InvoiceReceiptProjects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    business_name: Mapped[str] = mapped_column("businessName", String(180), nullable=False)
    client_name: Mapped[str | None] = mapped_column("clientName", String(180), nullable=True)
    currency: Mapped[str] = mapped_column(String(12), default="AED", server_default="AED", nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="active", server_default="active", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
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

    documents: Mapped[list["InvoiceReceiptDocument"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )
    history_items: Mapped[list["InvoiceReceiptHistoryItem"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )


class InvoiceReceiptDocument(InvoiceReceiptBase):
    __tablename__ = "InvoiceReceiptDocuments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(
        "projectId",
        Integer,
        ForeignKey("InvoiceReceiptProjects.id"),
        index=True,
        nullable=False,
    )
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    document_type: Mapped[str] = mapped_column("documentType", String(40), nullable=False)
    document_number: Mapped[str] = mapped_column("documentNumber", String(80), nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    client_name: Mapped[str] = mapped_column("clientName", String(180), nullable=False)
    issue_date: Mapped[str | None] = mapped_column("issueDate", String(40), nullable=True)
    due_date: Mapped[str | None] = mapped_column("dueDate", String(40), nullable=True)
    paid_date: Mapped[str | None] = mapped_column("paidDate", String(40), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="draft", server_default="draft", nullable=False)
    subtotal: Mapped[float] = mapped_column(Numeric(12, 2), default=0, server_default="0", nullable=False)
    tax_total: Mapped[float] = mapped_column("taxTotal", Numeric(12, 2), default=0, server_default="0", nullable=False)
    total: Mapped[float] = mapped_column(Numeric(12, 2), default=0, server_default="0", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    terms: Mapped[str | None] = mapped_column(Text, nullable=True)
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

    project: Mapped[InvoiceReceiptProject] = relationship(back_populates="documents")
    items: Mapped[list["InvoiceReceiptItem"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
    )
    history_items: Mapped[list["InvoiceReceiptHistoryItem"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
    )


class InvoiceReceiptItem(InvoiceReceiptBase):
    __tablename__ = "InvoiceReceiptItems"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    document_id: Mapped[int] = mapped_column(
        "documentId",
        Integer,
        ForeignKey("InvoiceReceiptDocuments.id"),
        index=True,
        nullable=False,
    )
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    quantity: Mapped[float] = mapped_column(Numeric(10, 2), default=1, server_default="1", nullable=False)
    unit_price: Mapped[float] = mapped_column("unitPrice", Numeric(12, 2), default=0, server_default="0", nullable=False)
    tax_rate: Mapped[float] = mapped_column("taxRate", Numeric(5, 2), default=0, server_default="0", nullable=False)
    line_total: Mapped[float] = mapped_column("lineTotal", Numeric(12, 2), default=0, server_default="0", nullable=False)
    sort_order: Mapped[int] = mapped_column("sortOrder", Integer, default=0, server_default="0", nullable=False)
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

    document: Mapped[InvoiceReceiptDocument] = relationship(back_populates="items")


class InvoiceReceiptHistoryItem(InvoiceReceiptBase):
    __tablename__ = "InvoiceReceiptHistory"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int | None] = mapped_column(
        "projectId",
        Integer,
        ForeignKey("InvoiceReceiptProjects.id"),
        index=True,
        nullable=True,
    )
    document_id: Mapped[int | None] = mapped_column(
        "documentId",
        Integer,
        ForeignKey("InvoiceReceiptDocuments.id"),
        index=True,
        nullable=True,
    )
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    action_type: Mapped[str] = mapped_column("actionType", String(60), default="updated", server_default="updated", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
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

    project: Mapped[InvoiceReceiptProject | None] = relationship(back_populates="history_items")
    document: Mapped[InvoiceReceiptDocument | None] = relationship(back_populates="history_items")
