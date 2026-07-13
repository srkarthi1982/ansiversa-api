from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

SubscriptionStatus = Literal["active", "trial", "paused", "cancelled", "expired"]
BillingFrequency = Literal["weekly", "monthly", "quarterly", "semiannual", "annual", "custom"]
RenewalStatus = Literal["recorded", "skipped", "cancelled"]


def _normalize_text(value: object) -> object:
    if isinstance(value, str):
        normalized = value.strip()
        return normalized or None
    return value


def _currency(value: str | None) -> str:
    if not value:
        return "USD"
    return value.strip().upper()


class SubscriptionManagerCategoryCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    color: str | None = Field(default=None, max_length=40)
    notes: str | None = Field(default=None, max_length=5000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class SubscriptionManagerCategoryUpdateRequest(SubscriptionManagerCategoryCreateRequest):
    name: str | None = Field(default=None, min_length=1, max_length=120)


class SubscriptionManagerSubscriptionCreateRequest(BaseModel):
    category_id: str = Field(alias="categoryId", max_length=36)
    name: str = Field(min_length=1, max_length=180)
    provider: str = Field(min_length=1, max_length=180)
    billing_amount: float = Field(alias="billingAmount", gt=0)
    currency_code: str = Field(default="USD", alias="currencyCode", min_length=3, max_length=3)
    billing_frequency: BillingFrequency = Field(default="monthly", alias="billingFrequency")
    start_date: str | None = Field(default=None, alias="startDate", max_length=40)
    next_billing_date: str = Field(alias="nextBillingDate", min_length=1, max_length=40)
    trial_end_date: str | None = Field(default=None, alias="trialEndDate", max_length=40)
    payment_method: str | None = Field(default=None, alias="paymentMethod", max_length=120)
    status: SubscriptionStatus = "active"
    auto_renew: bool = Field(default=True, alias="autoRenew")
    cancellation_notice_days: int = Field(default=0, alias="cancellationNoticeDays", ge=0, le=365)
    website: str | None = Field(default=None, max_length=500)
    reference: str | None = Field(default=None, max_length=180)
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

    @model_validator(mode="after")
    def validate_dates(self) -> "SubscriptionManagerSubscriptionCreateRequest":
        if self.start_date and self.trial_end_date and self.trial_end_date < self.start_date:
            raise ValueError("trialEndDate must not be before startDate.")
        if self.start_date and self.next_billing_date < self.start_date:
            raise ValueError("nextBillingDate must not be before startDate.")
        return self


class SubscriptionManagerSubscriptionUpdateRequest(BaseModel):
    category_id: str | None = Field(default=None, alias="categoryId", max_length=36)
    name: str | None = Field(default=None, min_length=1, max_length=180)
    provider: str | None = Field(default=None, min_length=1, max_length=180)
    billing_amount: float | None = Field(default=None, alias="billingAmount", gt=0)
    currency_code: str | None = Field(default=None, alias="currencyCode", min_length=3, max_length=3)
    billing_frequency: BillingFrequency | None = Field(default=None, alias="billingFrequency")
    start_date: str | None = Field(default=None, alias="startDate", max_length=40)
    next_billing_date: str | None = Field(default=None, alias="nextBillingDate", max_length=40)
    trial_end_date: str | None = Field(default=None, alias="trialEndDate", max_length=40)
    payment_method: str | None = Field(default=None, alias="paymentMethod", max_length=120)
    status: SubscriptionStatus | None = None
    auto_renew: bool | None = Field(default=None, alias="autoRenew")
    cancellation_notice_days: int | None = Field(default=None, alias="cancellationNoticeDays", ge=0, le=365)
    website: str | None = Field(default=None, max_length=500)
    reference: str | None = Field(default=None, max_length=180)
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


class SubscriptionManagerRenewalCreateRequest(BaseModel):
    subscription_id: str = Field(alias="subscriptionId", max_length=36)
    renewal_date: str = Field(alias="renewalDate", min_length=1, max_length=40)
    amount: float = Field(gt=0)
    currency_code: str = Field(default="USD", alias="currencyCode", min_length=3, max_length=3)
    status: RenewalStatus = "recorded"
    next_billing_date: str | None = Field(default=None, alias="nextBillingDate", max_length=40)
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


class SubscriptionManagerRenewalUpdateRequest(BaseModel):
    renewal_date: str | None = Field(default=None, alias="renewalDate", min_length=1, max_length=40)
    amount: float | None = Field(default=None, gt=0)
    currency_code: str | None = Field(default=None, alias="currencyCode", min_length=3, max_length=3)
    status: RenewalStatus | None = None
    next_billing_date: str | None = Field(default=None, alias="nextBillingDate", max_length=40)
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


class SubscriptionManagerSubscriptionActionRequest(BaseModel):
    next_billing_date: str | None = Field(default=None, alias="nextBillingDate", max_length=40)
    notes: str | None = Field(default=None, max_length=5000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class SubscriptionManagerCategorySummaryResponse(BaseModel):
    id: str
    name: str
    color: str | None
    notes_preview: str | None = Field(serialization_alias="notesPreview")
    subscription_count: int = Field(serialization_alias="subscriptionCount")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class SubscriptionManagerCategoryDetailResponse(SubscriptionManagerCategorySummaryResponse):
    notes: str | None


class SubscriptionManagerSubscriptionSummaryResponse(BaseModel):
    id: str
    category_id: str = Field(serialization_alias="categoryId")
    category_name: str = Field(serialization_alias="categoryName")
    name: str
    provider: str
    billing_amount: float = Field(serialization_alias="billingAmount")
    currency_code: str = Field(serialization_alias="currencyCode")
    billing_frequency: BillingFrequency = Field(serialization_alias="billingFrequency")
    start_date: str | None = Field(serialization_alias="startDate")
    next_billing_date: str = Field(serialization_alias="nextBillingDate")
    trial_end_date: str | None = Field(serialization_alias="trialEndDate")
    payment_method: str | None = Field(serialization_alias="paymentMethod")
    status: SubscriptionStatus
    auto_renew: bool = Field(serialization_alias="autoRenew")
    cancellation_notice_days: int = Field(serialization_alias="cancellationNoticeDays")
    website: str | None
    reference: str | None
    notes_preview: str | None = Field(serialization_alias="notesPreview")
    renewal_state: str = Field(serialization_alias="renewalState")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class SubscriptionManagerSubscriptionDetailResponse(SubscriptionManagerSubscriptionSummaryResponse):
    notes: str | None


class SubscriptionManagerRenewalSummaryResponse(BaseModel):
    id: str
    subscription_id: str = Field(serialization_alias="subscriptionId")
    subscription_name: str = Field(serialization_alias="subscriptionName")
    provider: str
    category_id: str = Field(serialization_alias="categoryId")
    category_name: str = Field(serialization_alias="categoryName")
    renewal_date: str = Field(serialization_alias="renewalDate")
    amount: float
    currency_code: str = Field(serialization_alias="currencyCode")
    status: RenewalStatus
    next_billing_date: str | None = Field(serialization_alias="nextBillingDate")
    notes_preview: str | None = Field(serialization_alias="notesPreview")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class SubscriptionManagerRenewalDetailResponse(SubscriptionManagerRenewalSummaryResponse):
    notes: str | None


class SubscriptionManagerCurrencyTotalResponse(BaseModel):
    currency_code: str = Field(serialization_alias="currencyCode")
    monthly_amount: float = Field(serialization_alias="monthlyAmount")
    annual_amount: float = Field(serialization_alias="annualAmount")
    subscription_count: int = Field(serialization_alias="subscriptionCount")


class SubscriptionManagerBreakdownResponse(BaseModel):
    label: str
    currency_code: str = Field(serialization_alias="currencyCode")
    amount: float
    count: int


class SubscriptionManagerTimelineResponse(BaseModel):
    month: str
    currency_code: str = Field(serialization_alias="currencyCode")
    amount: float
    count: int


class SubscriptionManagerDashboardResponse(BaseModel):
    categories: list[SubscriptionManagerCategorySummaryResponse]
    subscriptions: list[SubscriptionManagerSubscriptionSummaryResponse]
    renewals: list[SubscriptionManagerRenewalSummaryResponse]
    total_active: int = Field(serialization_alias="totalActive")
    trial_count: int = Field(serialization_alias="trialCount")
    upcoming_renewals: int = Field(serialization_alias="upcomingRenewals")
    overdue_renewals: int = Field(serialization_alias="overdueRenewals")
    currency_totals: list[SubscriptionManagerCurrencyTotalResponse] = Field(serialization_alias="currencyTotals")
    spending_by_category: list[SubscriptionManagerBreakdownResponse] = Field(serialization_alias="spendingByCategory")
    spending_by_frequency: list[SubscriptionManagerBreakdownResponse] = Field(serialization_alias="spendingByFrequency")
    monthly_activity: list[SubscriptionManagerTimelineResponse] = Field(serialization_alias="monthlyActivity")
    recent_activity: list[SubscriptionManagerRenewalSummaryResponse] = Field(serialization_alias="recentActivity")
