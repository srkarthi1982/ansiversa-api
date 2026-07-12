from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

PeriodStatus = Literal["draft", "in_review", "ready_for_adviser_review", "filed_externally", "closed"]
EntityType = Literal["mainland_company", "free_zone_person", "natural_person_business", "non_resident", "other"]
AdjustmentCategory = Literal[
    "non_deductible_expense",
    "exempt_income",
    "relief_or_election",
    "interest_limitation",
    "related_party_adjustment",
    "tax_loss",
    "foreign_tax_credit",
    "transitional_adjustment",
    "other",
]
AdjustmentDirection = Literal["increase_taxable_income", "decrease_taxable_income"]
TreatmentStatus = Literal["draft", "needs_professional_review", "confirmed_externally"]
ObligationType = Literal[
    "registration_review",
    "return_preparation",
    "filing_deadline",
    "payment_deadline",
    "record_retention",
    "transfer_pricing_documentation",
    "adviser_review",
    "supporting_document_collection",
    "other",
]
ObligationPriority = Literal["low", "medium", "high"]
ObligationStatus = Literal["upcoming", "in_progress", "completed_externally", "overdue", "not_applicable"]


def _normalize_text(value: object) -> object:
    if isinstance(value, str):
        normalized = value.strip()
        return normalized or None
    return value


def _currency(value: str | None) -> str:
    if not value:
        return "AED"
    return value.strip().upper()


class CorporateTaxPeriodCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=180)
    financial_year_start: str | None = Field(default=None, alias="financialYearStart", max_length=40)
    financial_year_end: str | None = Field(default=None, alias="financialYearEnd", max_length=40)
    filing_due_date: str | None = Field(default=None, alias="filingDueDate", max_length=40)
    entity_name: str = Field(alias="entityName", min_length=1, max_length=180)
    trade_licence_number: str | None = Field(default=None, alias="tradeLicenceNumber", max_length=120)
    tax_registration_number: str | None = Field(default=None, alias="taxRegistrationNumber", max_length=120)
    entity_type: EntityType = Field(default="mainland_company", alias="entityType")
    revenue: float = Field(default=0, ge=0)
    accounting_profit: float = Field(default=0, alias="accountingProfit")
    taxable_income_estimate: float | None = Field(default=None, alias="taxableIncomeEstimate")
    currency_code: str = Field(default="AED", alias="currencyCode", min_length=3, max_length=3)
    status: PeriodStatus = "draft"
    tax_rate_percent: float = Field(default=9, alias="taxRatePercent", ge=0, le=100)
    tax_threshold: float = Field(default=375000, alias="taxThreshold", ge=0)
    assumption_effective_date: str | None = Field(default=None, alias="assumptionEffectiveDate", max_length=40)
    assumption_reference_note: str | None = Field(default=None, alias="assumptionReferenceNote", max_length=500)
    notes: str | None = Field(default=None, max_length=5000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)

    @field_validator("currency_code", mode="before")
    @classmethod
    def normalize_currency(cls, value: str | None) -> str:
        return _currency(value)


class CorporateTaxPeriodUpdateRequest(CorporateTaxPeriodCreateRequest):
    name: str | None = Field(default=None, min_length=1, max_length=180)
    entity_name: str | None = Field(default=None, alias="entityName", min_length=1, max_length=180)
    revenue: float | None = Field(default=None, ge=0)
    accounting_profit: float | None = Field(default=None, alias="accountingProfit")
    currency_code: str | None = Field(default=None, alias="currencyCode", min_length=3, max_length=3)
    tax_rate_percent: float | None = Field(default=None, alias="taxRatePercent", ge=0, le=100)
    tax_threshold: float | None = Field(default=None, alias="taxThreshold", ge=0)

    @field_validator("currency_code", mode="before")
    @classmethod
    def normalize_optional_currency(cls, value: str | None) -> str | None:
        return _currency(value) if value is not None else None


class CorporateTaxAdjustmentCreateRequest(BaseModel):
    period_id: str = Field(alias="periodId", max_length=36)
    title: str = Field(min_length=1, max_length=180)
    category: AdjustmentCategory = "other"
    direction: AdjustmentDirection = "increase_taxable_income"
    amount: float = Field(default=0, ge=0)
    currency_code: str = Field(default="AED", alias="currencyCode", min_length=3, max_length=3)
    reference: str | None = Field(default=None, max_length=180)
    explanation: str | None = Field(default=None, max_length=5000)
    supporting_document_note: str | None = Field(default=None, alias="supportingDocumentNote", max_length=500)
    treatment_status: TreatmentStatus = Field(default="draft", alias="treatmentStatus")
    notes: str | None = Field(default=None, max_length=5000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)

    @field_validator("currency_code", mode="before")
    @classmethod
    def normalize_currency(cls, value: str | None) -> str:
        return _currency(value)


class CorporateTaxAdjustmentUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    category: AdjustmentCategory | None = None
    direction: AdjustmentDirection | None = None
    amount: float | None = Field(default=None, ge=0)
    currency_code: str | None = Field(default=None, alias="currencyCode", min_length=3, max_length=3)
    reference: str | None = Field(default=None, max_length=180)
    explanation: str | None = Field(default=None, max_length=5000)
    supporting_document_note: str | None = Field(default=None, alias="supportingDocumentNote", max_length=500)
    treatment_status: TreatmentStatus | None = Field(default=None, alias="treatmentStatus")
    notes: str | None = Field(default=None, max_length=5000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)

    @field_validator("currency_code", mode="before")
    @classmethod
    def normalize_currency(cls, value: str | None) -> str | None:
        return _currency(value) if value is not None else None


class CorporateTaxObligationCreateRequest(BaseModel):
    period_id: str = Field(alias="periodId", max_length=36)
    title: str = Field(min_length=1, max_length=180)
    obligation_type: ObligationType = Field(default="other", alias="type")
    due_date: str | None = Field(default=None, alias="dueDate", max_length=40)
    priority: ObligationPriority = "medium"
    status: ObligationStatus = "upcoming"
    responsible_person: str | None = Field(default=None, alias="responsiblePerson", max_length=140)
    external_reference: str | None = Field(default=None, alias="externalReference", max_length=180)
    completion_date: str | None = Field(default=None, alias="completionDate", max_length=40)
    notes: str | None = Field(default=None, max_length=5000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class CorporateTaxObligationUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    obligation_type: ObligationType | None = Field(default=None, alias="type")
    due_date: str | None = Field(default=None, alias="dueDate", max_length=40)
    priority: ObligationPriority | None = None
    status: ObligationStatus | None = None
    responsible_person: str | None = Field(default=None, alias="responsiblePerson", max_length=140)
    external_reference: str | None = Field(default=None, alias="externalReference", max_length=180)
    completion_date: str | None = Field(default=None, alias="completionDate", max_length=40)
    notes: str | None = Field(default=None, max_length=5000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class CorporateTaxMoneyResponse(BaseModel):
    currency_code: str = Field(serialization_alias="currencyCode")
    amount: float


class CorporateTaxAssumptionResponse(BaseModel):
    tax_rate_percent: float = Field(serialization_alias="taxRatePercent")
    tax_threshold: float = Field(serialization_alias="taxThreshold")
    currency_code: str = Field(serialization_alias="currencyCode")
    effective_date: str | None = Field(serialization_alias="effectiveDate")
    reference_note: str | None = Field(serialization_alias="referenceNote")
    basis: str


class CorporateTaxPeriodSummaryResponse(BaseModel):
    id: str
    name: str
    financial_year_start: str | None = Field(serialization_alias="financialYearStart")
    financial_year_end: str | None = Field(serialization_alias="financialYearEnd")
    filing_due_date: str | None = Field(serialization_alias="filingDueDate")
    entity_name: str = Field(serialization_alias="entityName")
    entity_type: EntityType = Field(serialization_alias="entityType")
    revenue: float
    accounting_profit: float = Field(serialization_alias="accountingProfit")
    taxable_income_estimate: float | None = Field(serialization_alias="taxableIncomeEstimate")
    calculated_taxable_income_estimate: float = Field(serialization_alias="calculatedTaxableIncomeEstimate")
    indicative_tax_estimate: float = Field(serialization_alias="indicativeTaxEstimate")
    currency_code: str = Field(serialization_alias="currencyCode")
    status: PeriodStatus
    adjustment_count: int = Field(serialization_alias="adjustmentCount")
    obligation_count: int = Field(serialization_alias="obligationCount")
    net_adjustment: float = Field(serialization_alias="netAdjustment")
    notes_preview: str | None = Field(serialization_alias="notesPreview")
    assumption: CorporateTaxAssumptionResponse
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class CorporateTaxPeriodDetailResponse(CorporateTaxPeriodSummaryResponse):
    trade_licence_number: str | None = Field(serialization_alias="tradeLicenceNumber")
    tax_registration_number: str | None = Field(serialization_alias="taxRegistrationNumber")
    notes: str | None


class CorporateTaxAdjustmentSummaryResponse(BaseModel):
    id: str
    period_id: str = Field(serialization_alias="periodId")
    period_name: str = Field(serialization_alias="periodName")
    title: str
    category: AdjustmentCategory
    direction: AdjustmentDirection
    amount: float
    signed_amount: float = Field(serialization_alias="signedAmount")
    currency_code: str = Field(serialization_alias="currencyCode")
    reference: str | None
    supporting_document_note: str | None = Field(serialization_alias="supportingDocumentNote")
    treatment_status: TreatmentStatus = Field(serialization_alias="treatmentStatus")
    explanation_preview: str | None = Field(serialization_alias="explanationPreview")
    notes_preview: str | None = Field(serialization_alias="notesPreview")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class CorporateTaxAdjustmentDetailResponse(CorporateTaxAdjustmentSummaryResponse):
    explanation: str | None
    notes: str | None


class CorporateTaxObligationSummaryResponse(BaseModel):
    id: str
    period_id: str = Field(serialization_alias="periodId")
    period_name: str = Field(serialization_alias="periodName")
    title: str
    obligation_type: ObligationType = Field(serialization_alias="type")
    due_date: str | None = Field(serialization_alias="dueDate")
    priority: ObligationPriority
    status: ObligationStatus
    responsible_person: str | None = Field(serialization_alias="responsiblePerson")
    external_reference: str | None = Field(serialization_alias="externalReference")
    completion_date: str | None = Field(serialization_alias="completionDate")
    notes_preview: str | None = Field(serialization_alias="notesPreview")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class CorporateTaxObligationDetailResponse(CorporateTaxObligationSummaryResponse):
    notes: str | None


class CorporateTaxBreakdownResponse(BaseModel):
    label: str
    amount: float
    count: int


class CorporateTaxPeriodComparisonResponse(BaseModel):
    period_id: str = Field(serialization_alias="periodId")
    period_name: str = Field(serialization_alias="periodName")
    currency_code: str = Field(serialization_alias="currencyCode")
    accounting_profit: float = Field(serialization_alias="accountingProfit")
    net_adjustment: float = Field(serialization_alias="netAdjustment")
    calculated_taxable_income_estimate: float = Field(serialization_alias="calculatedTaxableIncomeEstimate")
    indicative_tax_estimate: float = Field(serialization_alias="indicativeTaxEstimate")


class CorporateTaxDashboardResponse(BaseModel):
    periods: list[CorporateTaxPeriodSummaryResponse]
    adjustments: list[CorporateTaxAdjustmentSummaryResponse]
    obligations: list[CorporateTaxObligationSummaryResponse]
    total_periods: int = Field(serialization_alias="totalPeriods")
    draft_periods: int = Field(serialization_alias="draftPeriods")
    upcoming_filings: int = Field(serialization_alias="upcomingFilings")
    accounting_profit_by_currency: list[CorporateTaxMoneyResponse] = Field(serialization_alias="accountingProfitByCurrency")
    net_adjustments_by_currency: list[CorporateTaxMoneyResponse] = Field(serialization_alias="netAdjustmentsByCurrency")
    estimated_taxable_income_by_currency: list[CorporateTaxMoneyResponse] = Field(serialization_alias="estimatedTaxableIncomeByCurrency")
    indicative_tax_estimate_by_currency: list[CorporateTaxMoneyResponse] = Field(serialization_alias="indicativeTaxEstimateByCurrency")
    upcoming_obligations: int = Field(serialization_alias="upcomingObligations")
    overdue_obligations: int = Field(serialization_alias="overdueObligations")
    completed_obligations: int = Field(serialization_alias="completedObligations")
    adjustment_breakdown_by_category: list[CorporateTaxBreakdownResponse] = Field(serialization_alias="adjustmentBreakdownByCategory")
    period_comparison: list[CorporateTaxPeriodComparisonResponse] = Field(serialization_alias="periodComparison")
    recent_activity: list[CorporateTaxAdjustmentSummaryResponse] = Field(serialization_alias="recentActivity")
    disclaimer: str
