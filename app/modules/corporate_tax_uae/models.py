from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.corporate_tax_uae.db import CorporateTaxBase


def _uuid() -> str:
    return str(uuid4())


class CorporateTaxPeriod(CorporateTaxBase):
    __tablename__ = "CorporateTaxPeriods"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    financial_year_start: Mapped[str | None] = mapped_column("financialYearStart", String(40), nullable=True)
    financial_year_end: Mapped[str | None] = mapped_column("financialYearEnd", String(40), nullable=True)
    filing_due_date: Mapped[str | None] = mapped_column("filingDueDate", String(40), nullable=True)
    entity_name: Mapped[str] = mapped_column("entityName", String(180), nullable=False)
    trade_licence_number: Mapped[str | None] = mapped_column("tradeLicenceNumber", String(120), nullable=True)
    tax_registration_number: Mapped[str | None] = mapped_column("taxRegistrationNumber", String(120), nullable=True)
    entity_type: Mapped[str] = mapped_column("entityType", String(80), default="mainland_company", server_default="mainland_company", nullable=False)
    revenue: Mapped[float] = mapped_column(Float, default=0, server_default="0", nullable=False)
    accounting_profit: Mapped[float] = mapped_column("accountingProfit", Float, default=0, server_default="0", nullable=False)
    taxable_income_estimate: Mapped[float | None] = mapped_column("taxableIncomeEstimate", Float, nullable=True)
    currency_code: Mapped[str] = mapped_column("currencyCode", String(3), default="AED", server_default="AED", nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="draft", server_default="draft", nullable=False)
    tax_rate_percent: Mapped[float] = mapped_column("taxRatePercent", Float, default=9, server_default="9", nullable=False)
    tax_threshold: Mapped[float] = mapped_column("taxThreshold", Float, default=375000, server_default="375000", nullable=False)
    assumption_effective_date: Mapped[str | None] = mapped_column("assumptionEffectiveDate", String(40), nullable=True)
    assumption_reference_note: Mapped[str | None] = mapped_column("assumptionReferenceNote", String(500), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    adjustments: Mapped[list["CorporateTaxAdjustment"]] = relationship(back_populates="period", cascade="all, delete-orphan")
    obligations: Mapped[list["CorporateTaxObligation"]] = relationship(back_populates="period", cascade="all, delete-orphan")


class CorporateTaxAdjustment(CorporateTaxBase):
    __tablename__ = "CorporateTaxAdjustments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    period_id: Mapped[str] = mapped_column("periodId", String(36), ForeignKey("CorporateTaxPeriods.id"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    category: Mapped[str] = mapped_column(String(60), default="other", server_default="other", nullable=False)
    direction: Mapped[str] = mapped_column(String(40), default="increase_taxable_income", server_default="increase_taxable_income", nullable=False)
    amount: Mapped[float] = mapped_column(Float, default=0, server_default="0", nullable=False)
    currency_code: Mapped[str] = mapped_column("currencyCode", String(3), default="AED", server_default="AED", nullable=False)
    reference: Mapped[str | None] = mapped_column(String(180), nullable=True)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    supporting_document_note: Mapped[str | None] = mapped_column("supportingDocumentNote", String(500), nullable=True)
    treatment_status: Mapped[str] = mapped_column("treatmentStatus", String(40), default="draft", server_default="draft", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    period: Mapped[CorporateTaxPeriod] = relationship(back_populates="adjustments")


class CorporateTaxObligation(CorporateTaxBase):
    __tablename__ = "CorporateTaxObligations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    period_id: Mapped[str] = mapped_column("periodId", String(36), ForeignKey("CorporateTaxPeriods.id"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    obligation_type: Mapped[str] = mapped_column("type", String(60), default="other", server_default="other", nullable=False)
    due_date: Mapped[str | None] = mapped_column("dueDate", String(40), nullable=True)
    priority: Mapped[str] = mapped_column(String(20), default="medium", server_default="medium", nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="upcoming", server_default="upcoming", nullable=False)
    responsible_person: Mapped[str | None] = mapped_column("responsiblePerson", String(140), nullable=True)
    external_reference: Mapped[str | None] = mapped_column("externalReference", String(180), nullable=True)
    completion_date: Mapped[str | None] = mapped_column("completionDate", String(40), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    period: Mapped[CorporateTaxPeriod] = relationship(back_populates="obligations")
