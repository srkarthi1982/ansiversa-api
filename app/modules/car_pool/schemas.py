from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

RideStatus = Literal["open", "full", "completed", "cancelled"]
RideRecurrence = Literal["one_time", "weekdays", "weekly", "custom"]
RideVisibility = Literal["private", "shared"]
PassengerStatus = Literal["joined", "left", "completed", "cancelled"]
RequestStatus = Literal["pending", "approved", "rejected"]


def _normalize_text(value: object) -> object:
    if isinstance(value, str):
        normalized = value.strip()
        return normalized or None
    return value


def _currency(value: str | None) -> str:
    if not value:
        return "USD"
    return value.strip().upper()


class CarPoolRideCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    origin: str = Field(min_length=1, max_length=180)
    destination: str = Field(min_length=1, max_length=180)
    departure_at: str = Field(alias="departureAt", min_length=1, max_length=40)
    return_at: str | None = Field(default=None, alias="returnAt", max_length=40)
    meeting_point: str | None = Field(default=None, alias="meetingPoint", max_length=220)
    vehicle_label: str | None = Field(default=None, alias="vehicleLabel", max_length=160)
    driver_name: str | None = Field(default=None, alias="driverName", max_length=120)
    seats_offered: int = Field(default=1, alias="seatsOffered", ge=1, le=12)
    seats_filled: int = Field(default=0, alias="seatsFilled", ge=0, le=12)
    price_per_seat: float | None = Field(default=None, alias="pricePerSeat", ge=0)
    currency_code: str = Field(default="USD", alias="currencyCode", min_length=3, max_length=3)
    recurrence: RideRecurrence = "one_time"
    status: RideStatus = "open"
    visibility: RideVisibility = "private"
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
    def validate_seats(self) -> "CarPoolRideCreateRequest":
        if self.seats_filled is not None and self.seats_offered is not None and self.seats_filled > self.seats_offered:
            raise ValueError("Seats filled cannot exceed seats offered.")
        return self


class CarPoolRideUpdateRequest(CarPoolRideCreateRequest):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    origin: str | None = Field(default=None, min_length=1, max_length=180)
    destination: str | None = Field(default=None, min_length=1, max_length=180)
    departure_at: str | None = Field(default=None, alias="departureAt", min_length=1, max_length=40)
    seats_offered: int | None = Field(default=None, alias="seatsOffered", ge=1, le=12)
    seats_filled: int | None = Field(default=None, alias="seatsFilled", ge=0, le=12)
    currency_code: str | None = Field(default=None, alias="currencyCode", min_length=3, max_length=3)
    recurrence: RideRecurrence | None = None
    status: RideStatus | None = None
    visibility: RideVisibility | None = None


class CarPoolRideDuplicateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=180)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class CarPoolPassengerJoinRequest(BaseModel):
    ride_id: str = Field(alias="rideId", max_length=36)
    passenger_name: str = Field(alias="passengerName", min_length=1, max_length=120)
    seats: int = Field(default=1, ge=1, le=12)
    contact_note: str | None = Field(default=None, alias="contactNote", max_length=220)
    joined_at: str = Field(alias="joinedAt", min_length=1, max_length=40)
    notes: str | None = Field(default=None, max_length=5000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class CarPoolPassengerUpdateRequest(BaseModel):
    passenger_name: str | None = Field(default=None, alias="passengerName", min_length=1, max_length=120)
    seats: int | None = Field(default=None, ge=1, le=12)
    contact_note: str | None = Field(default=None, alias="contactNote", max_length=220)
    joined_at: str | None = Field(default=None, alias="joinedAt", min_length=1, max_length=40)
    status: PassengerStatus | None = None
    notes: str | None = Field(default=None, max_length=5000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class CarPoolRequestCreateRequest(BaseModel):
    ride_id: str = Field(alias="rideId", max_length=36)
    requester_name: str = Field(alias="requesterName", min_length=1, max_length=120)
    seats_requested: int = Field(default=1, alias="seatsRequested", ge=1, le=12)
    pickup_note: str | None = Field(default=None, alias="pickupNote", max_length=220)
    message: str | None = Field(default=None, max_length=5000)
    requested_at: str = Field(alias="requestedAt", min_length=1, max_length=40)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class CarPoolRequestUpdateRequest(BaseModel):
    requester_name: str | None = Field(default=None, alias="requesterName", min_length=1, max_length=120)
    seats_requested: int | None = Field(default=None, alias="seatsRequested", ge=1, le=12)
    pickup_note: str | None = Field(default=None, alias="pickupNote", max_length=220)
    message: str | None = Field(default=None, max_length=5000)
    requested_at: str | None = Field(default=None, alias="requestedAt", min_length=1, max_length=40)
    status: RequestStatus | None = None
    response_note: str | None = Field(default=None, alias="responseNote", max_length=500)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class CarPoolRequestDecisionRequest(BaseModel):
    response_note: str | None = Field(default=None, alias="responseNote", max_length=500)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class CarPoolRideSummaryResponse(BaseModel):
    id: str
    title: str
    origin: str
    destination: str
    departure_at: str = Field(serialization_alias="departureAt")
    return_at: str | None = Field(serialization_alias="returnAt")
    meeting_point: str | None = Field(serialization_alias="meetingPoint")
    vehicle_label: str | None = Field(serialization_alias="vehicleLabel")
    seats_offered: int = Field(serialization_alias="seatsOffered")
    seats_filled: int = Field(serialization_alias="seatsFilled")
    available_seats: int = Field(serialization_alias="availableSeats")
    price_per_seat: float | None = Field(serialization_alias="pricePerSeat")
    currency_code: str = Field(serialization_alias="currencyCode")
    recurrence: RideRecurrence
    status: RideStatus
    visibility: RideVisibility
    notes_preview: str | None = Field(serialization_alias="notesPreview")
    passenger_count: int = Field(serialization_alias="passengerCount")
    request_count: int = Field(serialization_alias="requestCount")
    pending_request_count: int = Field(serialization_alias="pendingRequestCount")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class CarPoolRideDetailResponse(CarPoolRideSummaryResponse):
    driver_name: str | None = Field(serialization_alias="driverName")
    notes: str | None


class CarPoolPassengerSummaryResponse(BaseModel):
    id: str
    ride_id: str = Field(serialization_alias="rideId")
    ride_title: str = Field(serialization_alias="rideTitle")
    origin: str
    destination: str
    departure_at: str = Field(serialization_alias="departureAt")
    passenger_name: str = Field(serialization_alias="passengerName")
    seats: int
    contact_note: str | None = Field(serialization_alias="contactNote")
    joined_at: str = Field(serialization_alias="joinedAt")
    status: PassengerStatus
    notes_preview: str | None = Field(serialization_alias="notesPreview")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class CarPoolPassengerDetailResponse(CarPoolPassengerSummaryResponse):
    notes: str | None


class CarPoolRequestSummaryResponse(BaseModel):
    id: str
    ride_id: str = Field(serialization_alias="rideId")
    ride_title: str = Field(serialization_alias="rideTitle")
    origin: str
    destination: str
    departure_at: str = Field(serialization_alias="departureAt")
    requester_name: str = Field(serialization_alias="requesterName")
    seats_requested: int = Field(serialization_alias="seatsRequested")
    pickup_note: str | None = Field(serialization_alias="pickupNote")
    message_preview: str | None = Field(serialization_alias="messagePreview")
    requested_at: str = Field(serialization_alias="requestedAt")
    status: RequestStatus
    response_note: str | None = Field(serialization_alias="responseNote")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class CarPoolRequestDetailResponse(CarPoolRequestSummaryResponse):
    message: str | None


class CarPoolWeeklyActivityResponse(BaseModel):
    week: str
    ride_count: int = Field(serialization_alias="rideCount")
    trip_count: int = Field(serialization_alias="tripCount")
    request_count: int = Field(serialization_alias="requestCount")


class CarPoolDashboardResponse(BaseModel):
    rides: list[CarPoolRideSummaryResponse]
    passengers: list[CarPoolPassengerSummaryResponse]
    requests: list[CarPoolRequestSummaryResponse]
    total_rides: int = Field(serialization_alias="totalRides")
    seats_offered: int = Field(serialization_alias="seatsOffered")
    seats_filled: int = Field(serialization_alias="seatsFilled")
    trips_completed: int = Field(serialization_alias="tripsCompleted")
    cancellation_rate: float = Field(serialization_alias="cancellationRate")
    pending_requests: int = Field(serialization_alias="pendingRequests")
    approved_requests: int = Field(serialization_alias="approvedRequests")
    rejected_requests: int = Field(serialization_alias="rejectedRequests")
    upcoming_trips: list[CarPoolPassengerSummaryResponse] = Field(serialization_alias="upcomingTrips")
    past_trips: list[CarPoolPassengerSummaryResponse] = Field(serialization_alias="pastTrips")
    recently_updated_rides: list[CarPoolRideSummaryResponse] = Field(serialization_alias="recentlyUpdatedRides")
    weekly_activity: list[CarPoolWeeklyActivityResponse] = Field(serialization_alias="weeklyActivity")
