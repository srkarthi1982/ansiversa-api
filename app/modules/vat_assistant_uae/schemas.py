from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

RegistrationStatus = Literal["draft", "active", "suspended", "cancelled", "needs_review"]
RegistrationType = Literal["standard", "voluntary", "group", "exempt_review", "other"]
FilingStatus = Literal["draft", "ready_for_review", "filed_externally", "payment_pending", "refund_expected", "overdue", "closed"]
TransactionType = Literal["sale", "purchase", "import", "export", "reverse_charge", "adjustment", "other"]


def _normalize_text(value: object) -> object:
    if isinstance(value, str):
        normalized = value.strip()
        return normalized or None
    return value


def _currency(value: str | None) -> str:
    if not value:
        return "AED"
    return value.strip().upper()


class VatRegistrationCreateRequest(BaseModel):
    business_name: str = Field(alias="businessName", min_length=1, max_length=180)
    trn: str | None = Field(default=None, max_length=30)
    registration_type: RegistrationType = Field(default="standard", alias="registrationType")
    registration_date: str | None = Field(default=None, alias="registrationDate", max_length=40)
    vat_period: str | None = Field(default=None, alias="vatPeriod", max_length=80)
    status: RegistrationStatus = "draft"
    country: str = Field(default="United Arab Emirates", max_length=80)
    notes: str | None = Field(default=None, max_length=5000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class VatRegistrationUpdateRequest(VatRegistrationCreateRequest):
    business_name: str | None = Field(default=None, alias="businessName", min_length=1, max_length=180)
    registration_type: RegistrationType | None = Field(default=None, alias="registrationType")
    status: RegistrationStatus | None = None
    country: str | None = Field(default=None, max_length=80)


class VatReturnCreateRequest(BaseModel):
    registration_id: str = Field(alias="registrationId", max_length=36)
    vat_period: str = Field(alias="vatPeriod", min_length=1, max_length=80)
    filing_due_date: str | None = Field(default=None, alias="filingDueDate", max_length=40)
    output_vat: float = Field(default=0, alias="outputVAT", ge=0)
    input_vat: float = Field(default=0, alias="inputVAT", ge=0)
    payable_vat: float = Field(default=0, alias="payableVAT", ge=0)
    refund_amount: float = Field(default=0, alias="refundAmount", ge=0)
    filing_status: FilingStatus = Field(default="draft", alias="filingStatus")
    submission_date: str | None = Field(default=None, alias="submissionDate", max_length=40)
    currency_code: str = Field(default="AED", alias="currencyCode", min_length=3, max_length=3)
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


class VatReturnUpdateRequest(BaseModel):
    vat_period: str | None = Field(default=None, alias="vatPeriod", min_length=1, max_length=80)
    filing_due_date: str | None = Field(default=None, alias="filingDueDate", max_length=40)
    output_vat: float | None = Field(default=None, alias="outputVAT", ge=0)
    input_vat: float | None = Field(default=None, alias="inputVAT", ge=0)
    payable_vat: float | None = Field(default=None, alias="payableVAT", ge=0)
    refund_amount: float | None = Field(default=None, alias="refundAmount", ge=0)
    filing_status: FilingStatus | None = Field(default=None, alias="filingStatus")
    submission_date: str | None = Field(default=None, alias="submissionDate", max_length=40)
    currency_code: str | None = Field(default=None, alias="currencyCode", min_length=3, max_length=3)
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


class VatTransactionCreateRequest(BaseModel):
    registration_id: str = Field(alias="registrationId", max_length=36)
    return_id: str | None = Field(default=None, alias="returnId", max_length=36)
    transaction_date: str | None = Field(default=None, alias="date", max_length=40)
    invoice_number: str | None = Field(default=None, alias="invoiceNumber", max_length=120)
    counterparty: str = Field(min_length=1, max_length=180)
    transaction_type: TransactionType = Field(default="sale", alias="transactionType")
    taxable_amount: float = Field(default=0, alias="taxableAmount", ge=0)
    vat_rate: float = Field(default=5, alias="vatRate", ge=0, le=100)
    vat_amount: float = Field(default=0, alias="vatAmount", ge=0)
    currency_code: str = Field(default="AED", alias="currencyCode", min_length=3, max_length=3)
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


class VatTransactionUpdateRequest(BaseModel):
    return_id: str | None = Field(default=None, alias="returnId", max_length=36)
    transaction_date: str | None = Field(default=None, alias="date", max_length=40)
    invoice_number: str | None = Field(default=None, alias="invoiceNumber", max_length=120)
    counterparty: str | None = Field(default=None, min_length=1, max_length=180)
    transaction_type: TransactionType | None = Field(default=None, alias="transactionType")
    taxable_amount: float | None = Field(default=None, alias="taxableAmount", ge=0)
    vat_rate: float | None = Field(default=None, alias="vatRate", ge=0, le=100)
    vat_amount: float | None = Field(default=None, alias="vatAmount", ge=0)
    currency_code: str | None = Field(default=None, alias="currencyCode", min_length=3, max_length=3)
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


class VatMoneyResponse(BaseModel):
    currency_code: str = Field(serialization_alias="currencyCode")
    amount: float


class VatRegistrationSummaryResponse(BaseModel):
    id: str
    business_name: str = Field(serialization_alias="businessName")
    trn: str | None
    registration_type: RegistrationType = Field(serialization_alias="registrationType")
    registration_date: str | None = Field(serialization_alias="registrationDate")
    vat_period: str | None = Field(serialization_alias="vatPeriod")
    status: RegistrationStatus
    country: str
    return_count: int = Field(serialization_alias="returnCount")
    transaction_count: int = Field(serialization_alias="transactionCount")
    notes_preview: str | None = Field(serialization_alias="notesPreview")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class VatRegistrationDetailResponse(VatRegistrationSummaryResponse):
    notes: str | None


class VatReturnSummaryResponse(BaseModel):
    id: str
    registration_id: str = Field(serialization_alias="registrationId")
    business_name: str = Field(serialization_alias="businessName")
    vat_period: str = Field(serialization_alias="vatPeriod")
    filing_due_date: str | None = Field(serialization_alias="filingDueDate")
    output_vat: float = Field(serialization_alias="outputVAT")
    input_vat: float = Field(serialization_alias="inputVAT")
    payable_vat: float = Field(serialization_alias="payableVAT")
    refund_amount: float = Field(serialization_alias="refundAmount")
    filing_status: FilingStatus = Field(serialization_alias="filingStatus")
    submission_date: str | None = Field(serialization_alias="submissionDate")
    currency_code: str = Field(serialization_alias="currencyCode")
    notes_preview: str | None = Field(serialization_alias="notesPreview")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class VatReturnDetailResponse(VatReturnSummaryResponse):
    notes: str | None


class VatTransactionSummaryResponse(BaseModel):
    id: str
    registration_id: str = Field(serialization_alias="registrationId")
    business_name: str = Field(serialization_alias="businessName")
    return_id: str | None = Field(serialization_alias="returnId")
    return_period: str | None = Field(serialization_alias="returnPeriod")
    transaction_date: str | None = Field(serialization_alias="date")
    invoice_number: str | None = Field(serialization_alias="invoiceNumber")
    counterparty: str
    transaction_type: TransactionType = Field(serialization_alias="transactionType")
    taxable_amount: float = Field(serialization_alias="taxableAmount")
    vat_rate: float = Field(serialization_alias="vatRate")
    vat_amount: float = Field(serialization_alias="vatAmount")
    currency_code: str = Field(serialization_alias="currencyCode")
    notes_preview: str | None = Field(serialization_alias="notesPreview")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class VatTransactionDetailResponse(VatTransactionSummaryResponse):
    notes: str | None


class VatBreakdownResponse(BaseModel):
    label: str
    amount: float
    count: int


class VatPeriodSummaryResponse(BaseModel):
    vat_period: str = Field(serialization_alias="vatPeriod")
    output_vat: float = Field(serialization_alias="outputVAT")
    input_vat: float = Field(serialization_alias="inputVAT")
    net_vat_payable: float = Field(serialization_alias="netVATPayable")
    return_count: int = Field(serialization_alias="returnCount")


class VatDashboardResponse(BaseModel):
    registrations: list[VatRegistrationSummaryResponse]
    returns: list[VatReturnSummaryResponse]
    transactions: list[VatTransactionSummaryResponse]
    total_registrations: int = Field(serialization_alias="totalRegistrations")
    active_registrations: int = Field(serialization_alias="activeRegistrations")
    filed_returns: int = Field(serialization_alias="filedReturns")
    pending_returns: int = Field(serialization_alias="pendingReturns")
    total_output_vat_by_currency: list[VatMoneyResponse] = Field(serialization_alias="totalOutputVATByCurrency")
    total_input_vat_by_currency: list[VatMoneyResponse] = Field(serialization_alias="totalInputVATByCurrency")
    net_vat_payable_by_currency: list[VatMoneyResponse] = Field(serialization_alias="netVATPayableByCurrency")
    vat_by_period: list[VatPeriodSummaryResponse] = Field(serialization_alias="vatByPeriod")
    vat_by_rate: list[VatBreakdownResponse] = Field(serialization_alias="vatByRate")
    recent_activity: list[VatTransactionSummaryResponse] = Field(serialization_alias="recentActivity")
    disclaimer: str
