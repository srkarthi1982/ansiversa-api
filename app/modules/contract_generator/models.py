from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.contract_generator.db import ContractBase


class ContractProject(ContractBase):
    __tablename__ = "ContractProjects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    counterparty_name: Mapped[str | None] = mapped_column("counterpartyName", String(180), nullable=True)
    contract_type: Mapped[str] = mapped_column("contractType", String(80), default="service", server_default="service", nullable=False)
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

    documents: Mapped[list["ContractDocument"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )
    history_items: Mapped[list["ContractHistoryItem"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )


class ContractDocument(ContractBase):
    __tablename__ = "ContractDocuments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(
        "projectId",
        Integer,
        ForeignKey("ContractProjects.id"),
        index=True,
        nullable=False,
    )
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="draft", server_default="draft", nullable=False)
    contract_type: Mapped[str] = mapped_column("contractType", String(80), default="service", server_default="service", nullable=False)
    effective_date: Mapped[str | None] = mapped_column("effectiveDate", String(40), nullable=True)
    expiry_date: Mapped[str | None] = mapped_column("expiryDate", String(40), nullable=True)
    jurisdiction: Mapped[str | None] = mapped_column(String(120), nullable=True)
    parties: Mapped[str | None] = mapped_column(Text, nullable=True)
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
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

    project: Mapped[ContractProject] = relationship(back_populates="documents")
    clauses: Mapped[list["ContractClause"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
    )
    history_items: Mapped[list["ContractHistoryItem"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
    )


class ContractClause(ContractBase):
    __tablename__ = "ContractClauses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    document_id: Mapped[int] = mapped_column(
        "documentId",
        Integer,
        ForeignKey("ContractDocuments.id"),
        index=True,
        nullable=False,
    )
    owner_id: Mapped[str] = mapped_column("ownerId", String(36), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    category: Mapped[str] = mapped_column(String(80), default="general", server_default="general", nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
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

    document: Mapped[ContractDocument] = relationship(back_populates="clauses")


class ContractHistoryItem(ContractBase):
    __tablename__ = "ContractHistory"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int | None] = mapped_column(
        "projectId",
        Integer,
        ForeignKey("ContractProjects.id"),
        index=True,
        nullable=True,
    )
    document_id: Mapped[int | None] = mapped_column(
        "documentId",
        Integer,
        ForeignKey("ContractDocuments.id"),
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

    project: Mapped[ContractProject | None] = relationship(back_populates="history_items")
    document: Mapped[ContractDocument | None] = relationship(back_populates="history_items")
