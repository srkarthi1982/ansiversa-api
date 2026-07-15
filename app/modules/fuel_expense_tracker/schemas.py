from datetime import date, datetime
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

ArchiveFilter = Literal["active", "archived", "all"]
EntrySort = Literal["date", "cost", "quantity", "vehicle", "station", "created"]
OdometerUnit = Literal["km", "mi"]
FuelUnit = Literal["L", "gal"]


def _normalize_text(value: object) -> object:
    if isinstance(value, str):
        normalized = " ".join(value.strip().split())
        return normalized or None
    return value


def _normalize_currency(value: object) -> object:
    if isinstance(value, str):
        normalized = value.strip().upper()
        return normalized or "USD"
    return value


class VehicleCreateRequest(BaseModel):
    vehicle_name: str = Field(alias="vehicleName", min_length=1, max_length=160)
    manufacturer: str | None = Field(default=None, max_length=120)
    model: str | None = Field(default=None, max_length=120)
    year: int | None = Field(default=None, ge=1900, le=2100)
    fuel_type: str | None = Field(default=None, alias="fuelType", max_length=80)
    registration_nickname: str | None = Field(default=None, alias="registrationNickname", max_length=120)
    odometer_unit: OdometerUnit = Field(default="km", alias="odometerUnit")
    notes: str | None = Field(default=None, max_length=5000)
    archived: bool = False
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("vehicle_name", "manufacturer", "model", "fuel_type", "registration_nickname", "notes", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class VehicleUpdateRequest(VehicleCreateRequest):
    pass


class EntryCreateRequest(BaseModel):
    vehicle_id: str = Field(alias="vehicleId", min_length=1, max_length=36)
    purchase_date: date = Field(alias="purchaseDate")
    odometer: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=1)
    fuel_quantity: Decimal = Field(alias="fuelQuantity", gt=0, max_digits=12, decimal_places=3)
    fuel_unit: FuelUnit = Field(default="L", alias="fuelUnit")
    total_cost: Decimal = Field(alias="totalCost", ge=0, max_digits=12, decimal_places=2)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    unit_price: Decimal | None = Field(default=None, alias="unitPrice", ge=0, max_digits=12, decimal_places=4)
    station_name: str | None = Field(default=None, alias="stationName", max_length=180)
    payment_method: str | None = Field(default=None, alias="paymentMethod", max_length=120)
    full_tank: bool = Field(default=False, alias="fullTank")
    notes: str | None = Field(default=None, max_length=5000)
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("station_name", "payment_method", "notes", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)

    @field_validator("currency", mode="before")
    @classmethod
    def normalize_currency(cls, value: object) -> object:
        return _normalize_currency(value)

    @model_validator(mode="after")
    def derive_unit_price(self):
        if self.unit_price is None:
            self.unit_price = (self.total_cost / self.fuel_quantity).quantize(Decimal("0.0001"))
        return self


class EntryUpdateRequest(EntryCreateRequest):
    pass


class VehicleResponse(BaseModel):
    id: str
    vehicle_name: str = Field(serialization_alias="vehicleName")
    manufacturer: str | None
    model: str | None
    year: int | None
    fuel_type: str | None = Field(serialization_alias="fuelType")
    registration_nickname: str | None = Field(serialization_alias="registrationNickname")
    odometer_unit: str = Field(serialization_alias="odometerUnit")
    notes: str | None
    archived: bool
    entry_count: int = Field(serialization_alias="entryCount")
    total_cost: Decimal = Field(serialization_alias="totalCost")
    total_fuel: Decimal = Field(serialization_alias="totalFuel")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class EntryResponse(BaseModel):
    id: str
    vehicle_id: str = Field(serialization_alias="vehicleId")
    vehicle_name: str = Field(serialization_alias="vehicleName")
    purchase_date: date = Field(serialization_alias="purchaseDate")
    odometer: Decimal | None
    fuel_quantity: Decimal = Field(serialization_alias="fuelQuantity")
    fuel_unit: str = Field(serialization_alias="fuelUnit")
    total_cost: Decimal = Field(serialization_alias="totalCost")
    currency: str
    unit_price: Decimal = Field(serialization_alias="unitPrice")
    station_name: str | None = Field(serialization_alias="stationName")
    payment_method: str | None = Field(serialization_alias="paymentMethod")
    full_tank: bool = Field(serialization_alias="fullTank")
    fuel_economy: Decimal | None = Field(serialization_alias="fuelEconomy")
    notes: str | None
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class EntryListResponse(BaseModel):
    items: list[EntryResponse]
    total: int
    page: int
    page_size: int = Field(serialization_alias="pageSize")


class CountItem(BaseModel):
    label: str
    count: int


class MoneyItem(BaseModel):
    label: str
    amount: Decimal


class DashboardResponse(BaseModel):
    total_cost: Decimal = Field(serialization_alias="totalCost")
    monthly_cost: Decimal = Field(serialization_alias="monthlyCost")
    total_fuel: Decimal = Field(serialization_alias="totalFuel")
    average_fuel_price: Decimal = Field(serialization_alias="averageFuelPrice")
    average_fuel_economy: Decimal | None = Field(serialization_alias="averageFuelEconomy")
    total_entries: int = Field(serialization_alias="totalEntries")
    total_vehicles: int = Field(serialization_alias="totalVehicles")


class InsightsResponse(DashboardResponse):
    vehicles: list[VehicleResponse]
    recent_entries: list[EntryResponse] = Field(serialization_alias="recentEntries")
    cost_by_month: list[MoneyItem] = Field(serialization_alias="costByMonth")
    cost_by_vehicle: list[MoneyItem] = Field(serialization_alias="costByVehicle")
    purchases_by_station: list[CountItem] = Field(serialization_alias="purchasesByStation")
    highest_expense: EntryResponse | None = Field(serialization_alias="highestExpense")
    lowest_expense: EntryResponse | None = Field(serialization_alias="lowestExpense")
