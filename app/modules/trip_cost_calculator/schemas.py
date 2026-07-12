from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

TripCostCategory = Literal["fuel", "parking", "toll", "accommodation", "food", "transport", "tickets", "shopping", "miscellaneous"]


def _normalize_text(value: object) -> object:
    if isinstance(value, str):
        normalized = value.strip()
        return normalized or None
    return value


def _currency(value: str | None) -> str:
    if not value:
        return "USD"
    return value.strip().upper()


class TripCostTripCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=180)
    start_location: str | None = Field(default=None, alias="startLocation", max_length=180)
    destination: str = Field(min_length=1, max_length=180)
    start_date: str | None = Field(default=None, alias="startDate", max_length=40)
    end_date: str | None = Field(default=None, alias="endDate", max_length=40)
    travelers: int = Field(default=1, ge=1, le=1000)
    vehicle: str | None = Field(default=None, max_length=120)
    distance: float = Field(default=0, ge=0)
    currency_code: str = Field(default="USD", alias="currencyCode", min_length=3, max_length=3)
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


class TripCostTripUpdateRequest(TripCostTripCreateRequest):
    name: str | None = Field(default=None, min_length=1, max_length=180)
    destination: str | None = Field(default=None, min_length=1, max_length=180)
    travelers: int | None = Field(default=None, ge=1, le=1000)
    distance: float | None = Field(default=None, ge=0)
    currency_code: str | None = Field(default=None, alias="currencyCode", min_length=3, max_length=3)

    @field_validator("currency_code", mode="before")
    @classmethod
    def normalize_optional_currency(cls, value: str | None) -> str | None:
        return _currency(value) if value is not None else None


class TripCostExpenseCreateRequest(BaseModel):
    trip_id: str = Field(alias="tripId", max_length=36)
    category: TripCostCategory = "miscellaneous"
    description: str = Field(min_length=1, max_length=220)
    amount: float = Field(default=0, ge=0)
    currency_code: str = Field(default="USD", alias="currencyCode", min_length=3, max_length=3)
    expense_date: str = Field(alias="date", min_length=1, max_length=40)
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


class TripCostExpenseUpdateRequest(BaseModel):
    category: TripCostCategory | None = None
    description: str | None = Field(default=None, min_length=1, max_length=220)
    amount: float | None = Field(default=None, ge=0)
    currency_code: str | None = Field(default=None, alias="currencyCode", min_length=3, max_length=3)
    expense_date: str | None = Field(default=None, alias="date", min_length=1, max_length=40)
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


class TripCostTripSummaryResponse(BaseModel):
    id: str
    name: str
    start_location: str | None = Field(serialization_alias="startLocation")
    destination: str
    start_date: str | None = Field(serialization_alias="startDate")
    end_date: str | None = Field(serialization_alias="endDate")
    travelers: int
    vehicle: str | None
    distance: float
    currency_code: str = Field(serialization_alias="currencyCode")
    notes_preview: str | None = Field(serialization_alias="notesPreview")
    expense_count: int = Field(serialization_alias="expenseCount")
    total_cost: float = Field(serialization_alias="totalCost")
    cost_per_traveler: float = Field(serialization_alias="costPerTraveler")
    cost_per_kilometer: float = Field(serialization_alias="costPerKilometer")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class TripCostTripDetailResponse(TripCostTripSummaryResponse):
    notes: str | None


class TripCostExpenseSummaryResponse(BaseModel):
    id: str
    trip_id: str = Field(serialization_alias="tripId")
    trip_name: str = Field(serialization_alias="tripName")
    category: TripCostCategory
    description: str
    amount: float
    currency_code: str = Field(serialization_alias="currencyCode")
    expense_date: str = Field(serialization_alias="date")
    notes_preview: str | None = Field(serialization_alias="notesPreview")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class TripCostExpenseDetailResponse(TripCostExpenseSummaryResponse):
    notes: str | None


class TripCostBreakdownResponse(BaseModel):
    label: str
    amount: float
    count: int


class TripCostMonthlyResponse(BaseModel):
    month: str
    amount: float
    count: int


class TripCostComparisonResponse(BaseModel):
    trip_id: str = Field(serialization_alias="tripId")
    trip_name: str = Field(serialization_alias="tripName")
    total_cost: float = Field(serialization_alias="totalCost")
    cost_per_traveler: float = Field(serialization_alias="costPerTraveler")
    cost_per_kilometer: float = Field(serialization_alias="costPerKilometer")
    category_breakdown: list[TripCostBreakdownResponse] = Field(serialization_alias="categoryBreakdown")
    highest_expense_category: str | None = Field(serialization_alias="highestExpenseCategory")
    lowest_expense_category: str | None = Field(serialization_alias="lowestExpenseCategory")


class TripCostDashboardResponse(BaseModel):
    trips: list[TripCostTripSummaryResponse]
    expenses: list[TripCostExpenseSummaryResponse]
    comparisons: list[TripCostComparisonResponse]
    total_trips: int = Field(serialization_alias="totalTrips")
    total_expenses: float = Field(serialization_alias="totalExpenses")
    average_trip_cost: float = Field(serialization_alias="averageTripCost")
    average_cost_per_traveler: float = Field(serialization_alias="averageCostPerTraveler")
    cost_by_category: list[TripCostBreakdownResponse] = Field(serialization_alias="costByCategory")
    monthly_spending: list[TripCostMonthlyResponse] = Field(serialization_alias="monthlySpending")
    recent_activity: list[TripCostExpenseSummaryResponse] = Field(serialization_alias="recentActivity")
