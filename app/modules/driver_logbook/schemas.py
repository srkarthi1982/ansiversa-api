from datetime import date, datetime, time
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

ArchiveFilter = Literal["active", "archived", "all"]
TripSort = Literal["date", "distance", "duration", "vehicle", "purpose", "created"]
OdometerUnit = Literal["km", "mi"]
TripPurpose = Literal["personal", "work", "business", "school", "shopping", "medical", "vacation", "other"]


def _normalize_text(value: object) -> object:
    if isinstance(value, str):
        normalized = " ".join(value.strip().split())
        return normalized or None
    return value


class VehicleCreateRequest(BaseModel):
    vehicle_name: str = Field(alias="vehicleName", min_length=1, max_length=160)
    manufacturer: str | None = Field(default=None, max_length=120)
    model: str | None = Field(default=None, max_length=120)
    year: int | None = Field(default=None, ge=1900, le=2100)
    registration_nickname: str | None = Field(default=None, alias="registrationNickname", max_length=120)
    odometer_unit: OdometerUnit = Field(default="km", alias="odometerUnit")
    notes: str | None = Field(default=None, max_length=5000)
    archived: bool = False
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("vehicle_name", "manufacturer", "model", "registration_nickname", "notes", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class VehicleUpdateRequest(VehicleCreateRequest):
    pass


class TripCreateRequest(BaseModel):
    vehicle_id: str = Field(alias="vehicleId", min_length=1, max_length=36)
    trip_date: date = Field(alias="tripDate")
    start_time: time | None = Field(default=None, alias="startTime")
    end_time: time | None = Field(default=None, alias="endTime")
    start_odometer: Decimal | None = Field(default=None, alias="startOdometer", ge=0, max_digits=12, decimal_places=1)
    end_odometer: Decimal | None = Field(default=None, alias="endOdometer", ge=0, max_digits=12, decimal_places=1)
    distance: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=1)
    purpose: TripPurpose = "personal"
    start_location: str | None = Field(default=None, alias="startLocation", max_length=180)
    destination: str | None = Field(default=None, max_length=180)
    archived: bool = False
    notes: str | None = Field(default=None, max_length=5000)
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("start_location", "destination", "notes", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)

    @model_validator(mode="after")
    def validate_trip(self):
        if self.start_time and self.end_time and self.end_time < self.start_time:
            raise ValueError("End time cannot be before start time.")
        if self.start_odometer is not None and self.end_odometer is not None:
            if self.end_odometer < self.start_odometer:
                raise ValueError("End odometer cannot be lower than start odometer.")
            calculated = (self.end_odometer - self.start_odometer).quantize(Decimal("0.1"))
            self.distance = calculated
        if self.distance is None:
            self.distance = Decimal("0.0")
        return self


class TripUpdateRequest(TripCreateRequest):
    pass


class VehicleResponse(BaseModel):
    id: str
    vehicle_name: str = Field(serialization_alias="vehicleName")
    manufacturer: str | None
    model: str | None
    year: int | None
    registration_nickname: str | None = Field(serialization_alias="registrationNickname")
    odometer_unit: str = Field(serialization_alias="odometerUnit")
    notes: str | None
    archived: bool
    trip_count: int = Field(serialization_alias="tripCount")
    total_distance: Decimal = Field(serialization_alias="totalDistance")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class TripResponse(BaseModel):
    id: str
    vehicle_id: str = Field(serialization_alias="vehicleId")
    vehicle_name: str = Field(serialization_alias="vehicleName")
    trip_date: date = Field(serialization_alias="tripDate")
    start_time: time | None = Field(serialization_alias="startTime")
    end_time: time | None = Field(serialization_alias="endTime")
    start_odometer: Decimal | None = Field(serialization_alias="startOdometer")
    end_odometer: Decimal | None = Field(serialization_alias="endOdometer")
    distance: Decimal
    purpose: str
    start_location: str | None = Field(serialization_alias="startLocation")
    destination: str | None
    duration_minutes: int | None = Field(serialization_alias="durationMinutes")
    archived: bool
    notes: str | None
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class TripListResponse(BaseModel):
    items: list[TripResponse]
    total: int
    page: int
    page_size: int = Field(serialization_alias="pageSize")


class CountItem(BaseModel):
    label: str
    count: int


class DistanceItem(BaseModel):
    label: str
    distance: Decimal


class DashboardResponse(BaseModel):
    total_trips: int = Field(serialization_alias="totalTrips")
    total_distance: Decimal = Field(serialization_alias="totalDistance")
    monthly_distance: Decimal = Field(serialization_alias="monthlyDistance")
    driving_minutes: int = Field(serialization_alias="drivingMinutes")
    average_trip_distance: Decimal = Field(serialization_alias="averageTripDistance")
    total_vehicles: int = Field(serialization_alias="totalVehicles")


class InsightsResponse(DashboardResponse):
    vehicles: list[VehicleResponse]
    recent_trips: list[TripResponse] = Field(serialization_alias="recentTrips")
    distance_by_month: list[DistanceItem] = Field(serialization_alias="distanceByMonth")
    distance_by_vehicle: list[DistanceItem] = Field(serialization_alias="distanceByVehicle")
    distance_by_purpose: list[DistanceItem] = Field(serialization_alias="distanceByPurpose")
    trips_by_purpose: list[CountItem] = Field(serialization_alias="tripsByPurpose")
    longest_trip: TripResponse | None = Field(serialization_alias="longestTrip")
