from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.vat_assistant_uae.db import VatAssistantBase


def _uuid() -> str:
    return str(uuid4())


class VatRegistration(VatAssistantBase):
    __tablename__ = "VATRegistrations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    business_name: Mapped[str] = mapped_column("businessName", String(180), nullable=False)
    trn: Mapped[str | None] = mapped_column(String(30), nullable=True)
    registration_type: Mapped[str] = mapped_column("registrationType", String(60), default="standard", server_default="standard", nullable=False)
    registration_date: Mapped[str | None] = mapped_column("registrationDate", String(40), nullable=True)
    vat_period: Mapped[str | None] = mapped_column("vatPeriod", String(80), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="draft", server_default="draft", nullable=False)
    country: Mapped[str] = mapped_column(String(80), default="United Arab Emirates", server_default="United Arab Emirates", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    returns: Mapped[list["VatReturn"]] = relationship(back_populates="registration", cascade="all, delete-orphan")
    transactions: Mapped[list["VatTransaction"]] = relationship(back_populates="registration", cascade="all, delete-orphan")


class VatReturn(VatAssistantBase):
    __tablename__ = "VATReturns"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    registration_id: Mapped[str] = mapped_column("registrationId", String(36), ForeignKey("VATRegistrations.id"), index=True, nullable=False)
    vat_period: Mapped[str] = mapped_column("vatPeriod", String(80), nullable=False)
    filing_due_date: Mapped[str | None] = mapped_column("filingDueDate", String(40), nullable=True)
    output_vat: Mapped[float] = mapped_column("outputVAT", Float, default=0, server_default="0", nullable=False)
    input_vat: Mapped[float] = mapped_column("inputVAT", Float, default=0, server_default="0", nullable=False)
    payable_vat: Mapped[float] = mapped_column("payableVAT", Float, default=0, server_default="0", nullable=False)
    refund_amount: Mapped[float] = mapped_column("refundAmount", Float, default=0, server_default="0", nullable=False)
    filing_status: Mapped[str] = mapped_column("filingStatus", String(40), default="draft", server_default="draft", nullable=False)
    submission_date: Mapped[str | None] = mapped_column("submissionDate", String(40), nullable=True)
    currency_code: Mapped[str] = mapped_column("currencyCode", String(3), default="AED", server_default="AED", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    registration: Mapped[VatRegistration] = relationship(back_populates="returns")


class VatTransaction(VatAssistantBase):
    __tablename__ = "VATTransactions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    registration_id: Mapped[str] = mapped_column("registrationId", String(36), ForeignKey("VATRegistrations.id"), index=True, nullable=False)
    return_id: Mapped[str | None] = mapped_column("returnId", String(36), ForeignKey("VATReturns.id"), index=True, nullable=True)
    transaction_date: Mapped[str | None] = mapped_column("date", String(40), nullable=True)
    invoice_number: Mapped[str | None] = mapped_column("invoiceNumber", String(120), nullable=True)
    counterparty: Mapped[str] = mapped_column("counterparty", String(180), nullable=False)
    transaction_type: Mapped[str] = mapped_column("transactionType", String(40), default="sale", server_default="sale", nullable=False)
    taxable_amount: Mapped[float] = mapped_column("taxableAmount", Float, default=0, server_default="0", nullable=False)
    vat_rate: Mapped[float] = mapped_column("vatRate", Float, default=5, server_default="5", nullable=False)
    vat_amount: Mapped[float] = mapped_column("vatAmount", Float, default=0, server_default="0", nullable=False)
    currency_code: Mapped[str] = mapped_column("currencyCode", String(3), default="AED", server_default="AED", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    registration: Mapped[VatRegistration] = relationship(back_populates="transactions")
    vat_return: Mapped[VatReturn | None] = relationship()
