from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

DurationUnit = Literal["years", "months"]
RepaymentFrequency = Literal["monthly"]
CurrencyCode = Literal["AED", "USD", "EUR", "GBP", "INR", "SAR"]


def _normalize_text(value: object) -> object:
    if isinstance(value, str):
        normalized = value.strip()
        return normalized or None
    return value


def _currency(value: str | None) -> str:
    if not value:
        return "USD"
    return value.strip().upper()


class EmiLoanCalculationRequest(BaseModel):
    loan_amount: Decimal = Field(alias="loanAmount", gt=0, le=Decimal("1000000000"))
    annual_interest_rate: Decimal = Field(alias="annualInterestRate", ge=0, le=Decimal("100"))
    duration_value: int = Field(alias="durationValue", gt=0, le=600)
    duration_unit: DurationUnit = Field(default="years", alias="durationUnit")
    repayment_frequency: RepaymentFrequency = Field(default="monthly", alias="repaymentFrequency")
    start_date: str | None = Field(default=None, alias="startDate", max_length=40)
    processing_fee: Decimal = Field(default=Decimal("0"), alias="processingFee", ge=0, le=Decimal("100000000"))
    extra_payment: Decimal = Field(default=Decimal("0"), alias="extraPayment", ge=0, le=Decimal("100000000"))
    currency_code: CurrencyCode = Field(default="USD", alias="currencyCode")

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)

    @field_validator("currency_code", mode="before")
    @classmethod
    def normalize_currency(cls, value: str | None) -> str:
        return _currency(value)


class EmiLoanScenarioCreateRequest(EmiLoanCalculationRequest):
    name: str = Field(min_length=1, max_length=180)


class EmiLoanScenarioUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=180)
    loan_amount: Decimal | None = Field(default=None, alias="loanAmount", gt=0, le=Decimal("1000000000"))
    annual_interest_rate: Decimal | None = Field(default=None, alias="annualInterestRate", ge=0, le=Decimal("100"))
    duration_value: int | None = Field(default=None, alias="durationValue", gt=0, le=600)
    duration_unit: DurationUnit | None = Field(default=None, alias="durationUnit")
    repayment_frequency: RepaymentFrequency | None = Field(default=None, alias="repaymentFrequency")
    start_date: str | None = Field(default=None, alias="startDate", max_length=40)
    processing_fee: Decimal | None = Field(default=None, alias="processingFee", ge=0, le=Decimal("100000000"))
    extra_payment: Decimal | None = Field(default=None, alias="extraPayment", ge=0, le=Decimal("100000000"))
    currency_code: CurrencyCode | None = Field(default=None, alias="currencyCode")

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)

    @field_validator("currency_code", mode="before")
    @classmethod
    def normalize_currency(cls, value: str | None) -> str | None:
        return _currency(value) if value is not None else None


class EmiLoanInstallmentResponse(BaseModel):
    installment_number: int = Field(serialization_alias="installmentNumber")
    payment_date: str | None = Field(serialization_alias="paymentDate")
    opening_balance: Decimal = Field(serialization_alias="openingBalance")
    scheduled_emi: Decimal = Field(serialization_alias="scheduledEmi")
    extra_payment: Decimal = Field(serialization_alias="extraPayment")
    principal_component: Decimal = Field(serialization_alias="principalComponent")
    interest_component: Decimal = Field(serialization_alias="interestComponent")
    closing_balance: Decimal = Field(serialization_alias="closingBalance")


class EmiLoanCalculationResponse(BaseModel):
    regular_emi: Decimal = Field(serialization_alias="regularEmi")
    total_principal: Decimal = Field(serialization_alias="totalPrincipal")
    total_interest: Decimal = Field(serialization_alias="totalInterest")
    total_repayment: Decimal = Field(serialization_alias="totalRepayment")
    processing_fee: Decimal = Field(serialization_alias="processingFee")
    overall_loan_cost: Decimal = Field(serialization_alias="overallLoanCost")
    installment_count: int = Field(serialization_alias="installmentCount")
    estimated_payoff_date: str | None = Field(serialization_alias="estimatedPayoffDate")
    interest_to_principal_ratio: Decimal = Field(serialization_alias="interestToPrincipalRatio")
    savings_from_extra_payment: Decimal = Field(serialization_alias="savingsFromExtraPayment")
    schedule: list[EmiLoanInstallmentResponse]


class EmiLoanScenarioSummaryResponse(BaseModel):
    id: str
    name: str
    loan_amount: Decimal = Field(serialization_alias="loanAmount")
    annual_interest_rate: Decimal = Field(serialization_alias="annualInterestRate")
    duration_value: int = Field(serialization_alias="durationValue")
    duration_unit: DurationUnit = Field(serialization_alias="durationUnit")
    repayment_frequency: RepaymentFrequency = Field(serialization_alias="repaymentFrequency")
    start_date: str | None = Field(serialization_alias="startDate")
    processing_fee: Decimal = Field(serialization_alias="processingFee")
    extra_payment: Decimal = Field(serialization_alias="extraPayment")
    currency_code: CurrencyCode = Field(serialization_alias="currencyCode")
    calculated_emi: Decimal = Field(serialization_alias="calculatedEmi")
    total_interest: Decimal = Field(serialization_alias="totalInterest")
    total_repayment: Decimal = Field(serialization_alias="totalRepayment")
    overall_loan_cost: Decimal = Field(serialization_alias="overallLoanCost")
    estimated_payoff_date: str | None = Field(serialization_alias="estimatedPayoffDate")
    installment_count: int = Field(serialization_alias="installmentCount")
    interest_to_principal_ratio: Decimal = Field(serialization_alias="interestToPrincipalRatio")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class EmiLoanScenarioDetailResponse(EmiLoanScenarioSummaryResponse):
    calculation: EmiLoanCalculationResponse


class EmiLoanDashboardResponse(BaseModel):
    scenarios: list[EmiLoanScenarioSummaryResponse]
    total_scenarios: int = Field(serialization_alias="totalScenarios")
    active_scenarios: int = Field(serialization_alias="activeScenarios")
    aggregate_principal: Decimal = Field(serialization_alias="aggregatePrincipal")
    aggregate_projected_interest: Decimal = Field(serialization_alias="aggregateProjectedInterest")
    highest_emi: Decimal = Field(serialization_alias="highestEmi")
    lowest_emi: Decimal = Field(serialization_alias="lowestEmi")
    highest_total_interest: Decimal = Field(serialization_alias="highestTotalInterest")
