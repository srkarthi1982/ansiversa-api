from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

VehicleStatus = Literal["active", "inactive", "sold"]
FuelType = Literal["gasoline", "diesel", "hybrid", "electric", "other"]
ServiceCategory = Literal["oil_change", "tire_rotation", "inspection", "insurance", "registration", "repair", "general"]
ReminderType = Literal["oil_change", "tire_rotation", "inspection", "insurance_renewal", "registration_renewal", "service"]
ReminderPriority = Literal["low", "normal", "high"]
ReminderStatus = Literal["upcoming", "overdue", "completed", "dismissed"]


def _normalize_text(value: object) -> object:
    if isinstance(value, str):
        normalized = value.strip()
        return normalized or None
    return value


def _currency(value: str | None) -> str:
    if not value:
        return "USD"
    return value.strip().upper()


class VehicleMaintenanceVehicleCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=180)
    make: str | None = Field(default=None, max_length=120)
    model: str | None = Field(default=None, max_length=120)
    year: int | None = Field(default=None, ge=1900, le=2100)
    plate_number: str | None = Field(default=None, alias="plateNumber", max_length=60)
    vin: str | None = Field(default=None, max_length=80)
    odometer: int = Field(default=0, ge=0, le=2_000_000)
    fuel_type: FuelType = Field(default="gasoline", alias="fuelType")
    status: VehicleStatus = "active"
    notes: str | None = Field(default=None, max_length=5000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class VehicleMaintenanceVehicleUpdateRequest(VehicleMaintenanceVehicleCreateRequest):
    name: str | None = Field(default=None, min_length=1, max_length=180)
    odometer: int | None = Field(default=None, ge=0, le=2_000_000)
    fuel_type: FuelType | None = Field(default=None, alias="fuelType")
    status: VehicleStatus | None = None


class VehicleMaintenanceVehicleDuplicateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=180)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class VehicleMaintenanceRecordCreateRequest(BaseModel):
    vehicle_id: str = Field(alias="vehicleId", max_length=36)
    title: str = Field(min_length=1, max_length=180)
    service_date: str = Field(alias="serviceDate", min_length=1, max_length=40)
    category: ServiceCategory = "general"
    odometer: int = Field(default=0, ge=0, le=2_000_000)
    cost: float = Field(default=0, ge=0)
    currency_code: str = Field(default="USD", alias="currencyCode", min_length=3, max_length=3)
    provider: str | None = Field(default=None, max_length=160)
    next_due_date: str | None = Field(default=None, alias="nextDueDate", max_length=40)
    next_due_odometer: int | None = Field(default=None, alias="nextDueOdometer", ge=0, le=2_000_000)
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


class VehicleMaintenanceRecordUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    service_date: str | None = Field(default=None, alias="serviceDate", min_length=1, max_length=40)
    category: ServiceCategory | None = None
    odometer: int | None = Field(default=None, ge=0, le=2_000_000)
    cost: float | None = Field(default=None, ge=0)
    currency_code: str | None = Field(default=None, alias="currencyCode", min_length=3, max_length=3)
    provider: str | None = Field(default=None, max_length=160)
    next_due_date: str | None = Field(default=None, alias="nextDueDate", max_length=40)
    next_due_odometer: int | None = Field(default=None, alias="nextDueOdometer", ge=0, le=2_000_000)
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


class VehicleMaintenanceReminderCreateRequest(BaseModel):
    vehicle_id: str = Field(alias="vehicleId", max_length=36)
    title: str = Field(min_length=1, max_length=180)
    reminder_type: ReminderType = Field(default="service", alias="reminderType")
    due_date: str = Field(alias="dueDate", min_length=1, max_length=40)
    due_odometer: int | None = Field(default=None, alias="dueOdometer", ge=0, le=2_000_000)
    priority: ReminderPriority = "normal"
    status: ReminderStatus = "upcoming"
    completed_at: str | None = Field(default=None, alias="completedAt", max_length=40)
    notes: str | None = Field(default=None, max_length=5000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class VehicleMaintenanceReminderUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    reminder_type: ReminderType | None = Field(default=None, alias="reminderType")
    due_date: str | None = Field(default=None, alias="dueDate", min_length=1, max_length=40)
    due_odometer: int | None = Field(default=None, alias="dueOdometer", ge=0, le=2_000_000)
    priority: ReminderPriority | None = None
    status: ReminderStatus | None = None
    completed_at: str | None = Field(default=None, alias="completedAt", max_length=40)
    notes: str | None = Field(default=None, max_length=5000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class VehicleMaintenanceVehicleSummaryResponse(BaseModel):
    id: str
    name: str
    make: str | None
    model: str | None
    year: int | None
    plate_number: str | None = Field(serialization_alias="plateNumber")
    odometer: int
    fuel_type: FuelType = Field(serialization_alias="fuelType")
    status: VehicleStatus
    notes_preview: str | None = Field(serialization_alias="notesPreview")
    record_count: int = Field(serialization_alias="recordCount")
    reminder_count: int = Field(serialization_alias="reminderCount")
    upcoming_reminder_count: int = Field(serialization_alias="upcomingReminderCount")
    overdue_reminder_count: int = Field(serialization_alias="overdueReminderCount")
    total_cost: float = Field(serialization_alias="totalCost")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class VehicleMaintenanceVehicleDetailResponse(VehicleMaintenanceVehicleSummaryResponse):
    vin: str | None
    notes: str | None


class VehicleMaintenanceRecordSummaryResponse(BaseModel):
    id: str
    vehicle_id: str = Field(serialization_alias="vehicleId")
    vehicle_name: str = Field(serialization_alias="vehicleName")
    title: str
    service_date: str = Field(serialization_alias="serviceDate")
    category: ServiceCategory
    odometer: int
    cost: float
    currency_code: str = Field(serialization_alias="currencyCode")
    provider: str | None
    next_due_date: str | None = Field(serialization_alias="nextDueDate")
    next_due_odometer: int | None = Field(serialization_alias="nextDueOdometer")
    notes_preview: str | None = Field(serialization_alias="notesPreview")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class VehicleMaintenanceRecordDetailResponse(VehicleMaintenanceRecordSummaryResponse):
    notes: str | None


class VehicleMaintenanceReminderSummaryResponse(BaseModel):
    id: str
    vehicle_id: str = Field(serialization_alias="vehicleId")
    vehicle_name: str = Field(serialization_alias="vehicleName")
    title: str
    reminder_type: ReminderType = Field(serialization_alias="reminderType")
    due_date: str = Field(serialization_alias="dueDate")
    due_odometer: int | None = Field(serialization_alias="dueOdometer")
    priority: ReminderPriority
    status: ReminderStatus
    completed_at: str | None = Field(serialization_alias="completedAt")
    notes_preview: str | None = Field(serialization_alias="notesPreview")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class VehicleMaintenanceReminderDetailResponse(VehicleMaintenanceReminderSummaryResponse):
    notes: str | None


class VehicleMaintenanceMonthlyActivityResponse(BaseModel):
    month: str
    record_count: int = Field(serialization_alias="recordCount")
    reminder_count: int = Field(serialization_alias="reminderCount")
    cost: float


class VehicleMaintenanceServiceFrequencyResponse(BaseModel):
    category: ServiceCategory
    count: int


class VehicleMaintenanceDashboardResponse(BaseModel):
    vehicles: list[VehicleMaintenanceVehicleSummaryResponse]
    records: list[VehicleMaintenanceRecordSummaryResponse]
    reminders: list[VehicleMaintenanceReminderSummaryResponse]
    total_vehicles: int = Field(serialization_alias="totalVehicles")
    total_records: int = Field(serialization_alias="totalRecords")
    total_cost: float = Field(serialization_alias="totalCost")
    upcoming_reminders: int = Field(serialization_alias="upcomingReminders")
    overdue_reminders: int = Field(serialization_alias="overdueReminders")
    service_frequency: list[VehicleMaintenanceServiceFrequencyResponse] = Field(serialization_alias="serviceFrequency")
    monthly_activity: list[VehicleMaintenanceMonthlyActivityResponse] = Field(serialization_alias="monthlyActivity")
