from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

ParkingType = Literal["street", "mall", "office", "airport", "other"]
PaymentMethod = Literal["cash", "card", "mobile_wallet", "company_card", "other"]


def _normalize_text(value: object) -> object:
    if isinstance(value, str):
        normalized = value.strip()
        return normalized or None
    return value


def _currency(value: str | None) -> str:
    if not value:
        return "USD"
    return value.strip().upper()


class ParkingExpenseLocationCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=180)
    city: str | None = Field(default=None, max_length=120)
    area: str | None = Field(default=None, max_length=120)
    parking_type: ParkingType = Field(default="other", alias="parkingType")
    default_hourly_rate: float | None = Field(default=None, alias="defaultHourlyRate", ge=0)
    notes: str | None = Field(default=None, max_length=5000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class ParkingExpenseLocationUpdateRequest(ParkingExpenseLocationCreateRequest):
    name: str | None = Field(default=None, min_length=1, max_length=180)
    parking_type: ParkingType | None = Field(default=None, alias="parkingType")


class ParkingExpenseEntryCreateRequest(BaseModel):
    location_id: str = Field(alias="locationId", max_length=36)
    parked_at: str = Field(alias="date", min_length=1, max_length=40)
    start_time: str | None = Field(default=None, alias="startTime", max_length=20)
    end_time: str | None = Field(default=None, alias="endTime", max_length=20)
    duration_minutes: int = Field(default=0, alias="durationMinutes", ge=0, le=100_000)
    amount: float = Field(default=0, ge=0)
    currency_code: str = Field(default="USD", alias="currencyCode", min_length=3, max_length=3)
    payment_method: PaymentMethod = Field(default="card", alias="paymentMethod")
    vehicle: str | None = Field(default=None, max_length=120)
    purpose: str | None = Field(default=None, max_length=180)
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


class ParkingExpenseEntryUpdateRequest(BaseModel):
    parked_at: str | None = Field(default=None, alias="date", min_length=1, max_length=40)
    start_time: str | None = Field(default=None, alias="startTime", max_length=20)
    end_time: str | None = Field(default=None, alias="endTime", max_length=20)
    duration_minutes: int | None = Field(default=None, alias="durationMinutes", ge=0, le=100_000)
    amount: float | None = Field(default=None, ge=0)
    currency_code: str | None = Field(default=None, alias="currencyCode", min_length=3, max_length=3)
    payment_method: PaymentMethod | None = Field(default=None, alias="paymentMethod")
    vehicle: str | None = Field(default=None, max_length=120)
    purpose: str | None = Field(default=None, max_length=180)
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


class ParkingExpenseLocationSummaryResponse(BaseModel):
    id: str
    name: str
    city: str | None
    area: str | None
    parking_type: ParkingType = Field(serialization_alias="parkingType")
    default_hourly_rate: float | None = Field(serialization_alias="defaultHourlyRate")
    notes_preview: str | None = Field(serialization_alias="notesPreview")
    expense_count: int = Field(serialization_alias="expenseCount")
    total_amount: float = Field(serialization_alias="totalAmount")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class ParkingExpenseLocationDetailResponse(ParkingExpenseLocationSummaryResponse):
    notes: str | None


class ParkingExpenseEntrySummaryResponse(BaseModel):
    id: str
    location_id: str = Field(serialization_alias="locationId")
    location_name: str = Field(serialization_alias="locationName")
    parked_at: str = Field(serialization_alias="date")
    start_time: str | None = Field(serialization_alias="startTime")
    end_time: str | None = Field(serialization_alias="endTime")
    duration_minutes: int = Field(serialization_alias="durationMinutes")
    amount: float
    currency_code: str = Field(serialization_alias="currencyCode")
    payment_method: PaymentMethod = Field(serialization_alias="paymentMethod")
    vehicle: str | None
    purpose: str | None
    notes_preview: str | None = Field(serialization_alias="notesPreview")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class ParkingExpenseEntryDetailResponse(ParkingExpenseEntrySummaryResponse):
    notes: str | None


class ParkingExpenseMonthlySpendingResponse(BaseModel):
    month: str
    amount: float
    sessions: int


class ParkingExpenseBreakdownResponse(BaseModel):
    label: str
    amount: float
    sessions: int


class ParkingExpenseDashboardResponse(BaseModel):
    locations: list[ParkingExpenseLocationSummaryResponse]
    expenses: list[ParkingExpenseEntrySummaryResponse]
    total_expenses: float = Field(serialization_alias="totalExpenses")
    this_month: float = Field(serialization_alias="thisMonth")
    average_per_visit: float = Field(serialization_alias="averagePerVisit")
    total_sessions: int = Field(serialization_alias="totalSessions")
    monthly_spending: list[ParkingExpenseMonthlySpendingResponse] = Field(serialization_alias="monthlySpending")
    spending_by_payment_method: list[ParkingExpenseBreakdownResponse] = Field(serialization_alias="spendingByPaymentMethod")
    spending_by_location: list[ParkingExpenseBreakdownResponse] = Field(serialization_alias="spendingByLocation")
