from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

SearchStatus = Literal["planning", "comparing", "booked", "completed", "cancelled"]
TransmissionPreference = Literal["any", "automatic", "manual"]
VehicleTransmission = Literal["automatic", "manual"]
AvailabilityStatus = Literal["available", "unconfirmed", "unavailable"]
BookingStatus = Literal["confirmed", "completed", "cancelled"]


def _normalize_text(value: object) -> object:
    if isinstance(value, str):
        normalized = value.strip()
        return normalized or None
    return value


def _currency(value: str | None) -> str:
    if not value:
        return "USD"
    return value.strip().upper()


class RentACarSearchCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    pickup_location: str = Field(alias="pickupLocation", min_length=1, max_length=180)
    dropoff_location: str = Field(alias="dropoffLocation", min_length=1, max_length=180)
    pickup_at: str = Field(alias="pickupAt", min_length=1, max_length=40)
    return_at: str = Field(alias="returnAt", min_length=1, max_length=40)
    driver_age_group: str = Field(default="30-64", alias="driverAgeGroup", max_length=60)
    vehicle_type: str = Field(default="any", alias="vehicleType", max_length=80)
    transmission: TransmissionPreference = "any"
    passengers: int = Field(default=1, ge=1, le=20)
    luggage: int = Field(default=0, ge=0, le=20)
    budget: float | None = Field(default=None, ge=0)
    currency_code: str = Field(default="USD", alias="currencyCode", min_length=3, max_length=3)
    notes: str | None = Field(default=None, max_length=5000)
    status: SearchStatus = "planning"

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
    def validate_date_order(self) -> "RentACarSearchCreateRequest":
        if self.pickup_at and self.return_at and self.return_at <= self.pickup_at:
            raise ValueError("Return date and time must be after pickup date and time.")
        return self


class RentACarSearchUpdateRequest(RentACarSearchCreateRequest):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    pickup_location: str | None = Field(default=None, alias="pickupLocation", min_length=1, max_length=180)
    dropoff_location: str | None = Field(default=None, alias="dropoffLocation", min_length=1, max_length=180)
    pickup_at: str | None = Field(default=None, alias="pickupAt", min_length=1, max_length=40)
    return_at: str | None = Field(default=None, alias="returnAt", min_length=1, max_length=40)
    driver_age_group: str | None = Field(default=None, alias="driverAgeGroup", max_length=60)
    vehicle_type: str | None = Field(default=None, alias="vehicleType", max_length=80)
    transmission: TransmissionPreference | None = None
    passengers: int | None = Field(default=None, ge=1, le=20)
    luggage: int | None = Field(default=None, ge=0, le=20)
    currency_code: str | None = Field(default=None, alias="currencyCode", min_length=3, max_length=3)
    status: SearchStatus | None = None


class RentACarSearchDuplicateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=180)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class RentACarVehicleOptionCreateRequest(BaseModel):
    search_id: str = Field(alias="searchId", max_length=36)
    provider_name: str = Field(alias="providerName", min_length=1, max_length=160)
    vehicle_name: str = Field(alias="vehicleName", min_length=1, max_length=180)
    vehicle_class: str = Field(alias="vehicleClass", min_length=1, max_length=80)
    transmission: VehicleTransmission = "automatic"
    fuel_policy: str | None = Field(default=None, alias="fuelPolicy", max_length=160)
    seats: int = Field(default=4, ge=1, le=20)
    luggage_capacity: int = Field(default=1, alias="luggageCapacity", ge=0, le=20)
    daily_base_rate: float = Field(default=0, alias="dailyBaseRate", ge=0)
    rental_days: int = Field(default=1, alias="rentalDays", ge=1, le=365)
    taxes_and_fees: float = Field(default=0, alias="taxesAndFees", ge=0)
    deposit: float | None = Field(default=None, ge=0)
    addon_estimate: float = Field(default=0, alias="addonEstimate", ge=0)
    mileage_policy: str | None = Field(default=None, alias="mileagePolicy", max_length=180)
    cancellation_terms: str | None = Field(default=None, alias="cancellationTerms", max_length=220)
    pickup_method: str | None = Field(default=None, alias="pickupMethod", max_length=160)
    reference_url: str | None = Field(default=None, alias="referenceUrl", max_length=600)
    last_checked: str | None = Field(default=None, alias="lastChecked", max_length=40)
    notes: str | None = Field(default=None, max_length=5000)
    is_preferred: bool = Field(default=False, alias="isPreferred")
    availability_status: AvailabilityStatus = Field(default="unconfirmed", alias="availabilityStatus")

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class RentACarVehicleOptionUpdateRequest(BaseModel):
    provider_name: str | None = Field(default=None, alias="providerName", min_length=1, max_length=160)
    vehicle_name: str | None = Field(default=None, alias="vehicleName", min_length=1, max_length=180)
    vehicle_class: str | None = Field(default=None, alias="vehicleClass", min_length=1, max_length=80)
    transmission: VehicleTransmission | None = None
    fuel_policy: str | None = Field(default=None, alias="fuelPolicy", max_length=160)
    seats: int | None = Field(default=None, ge=1, le=20)
    luggage_capacity: int | None = Field(default=None, alias="luggageCapacity", ge=0, le=20)
    daily_base_rate: float | None = Field(default=None, alias="dailyBaseRate", ge=0)
    rental_days: int | None = Field(default=None, alias="rentalDays", ge=1, le=365)
    taxes_and_fees: float | None = Field(default=None, alias="taxesAndFees", ge=0)
    deposit: float | None = Field(default=None, ge=0)
    addon_estimate: float | None = Field(default=None, alias="addonEstimate", ge=0)
    mileage_policy: str | None = Field(default=None, alias="mileagePolicy", max_length=180)
    cancellation_terms: str | None = Field(default=None, alias="cancellationTerms", max_length=220)
    pickup_method: str | None = Field(default=None, alias="pickupMethod", max_length=160)
    reference_url: str | None = Field(default=None, alias="referenceUrl", max_length=600)
    last_checked: str | None = Field(default=None, alias="lastChecked", max_length=40)
    notes: str | None = Field(default=None, max_length=5000)
    is_preferred: bool | None = Field(default=None, alias="isPreferred")
    availability_status: AvailabilityStatus | None = Field(default=None, alias="availabilityStatus")

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class RentACarVehicleOptionDuplicateRequest(BaseModel):
    vehicle_name: str | None = Field(default=None, alias="vehicleName", min_length=1, max_length=180)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class RentACarBookingCreateRequest(BaseModel):
    search_id: str = Field(alias="searchId", max_length=36)
    vehicle_option_id: str | None = Field(default=None, alias="vehicleOptionId", max_length=36)
    booking_reference: str = Field(alias="bookingReference", min_length=1, max_length=160)
    provider_name: str = Field(alias="providerName", min_length=1, max_length=160)
    pickup_instructions: str | None = Field(default=None, alias="pickupInstructions", max_length=5000)
    dropoff_instructions: str | None = Field(default=None, alias="dropoffInstructions", max_length=5000)
    confirmed_total: float = Field(default=0, alias="confirmedTotal", ge=0)
    currency_code: str = Field(default="USD", alias="currencyCode", min_length=3, max_length=3)
    deposit_amount: float | None = Field(default=None, alias="depositAmount", ge=0)
    contact_information: str | None = Field(default=None, alias="contactInformation", max_length=220)
    booking_date: str = Field(alias="bookingDate", min_length=1, max_length=40)
    cancellation_deadline: str | None = Field(default=None, alias="cancellationDeadline", max_length=40)
    status: BookingStatus = "confirmed"
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


class RentACarBookingUpdateRequest(BaseModel):
    booking_reference: str | None = Field(default=None, alias="bookingReference", min_length=1, max_length=160)
    provider_name: str | None = Field(default=None, alias="providerName", min_length=1, max_length=160)
    pickup_instructions: str | None = Field(default=None, alias="pickupInstructions", max_length=5000)
    dropoff_instructions: str | None = Field(default=None, alias="dropoffInstructions", max_length=5000)
    confirmed_total: float | None = Field(default=None, alias="confirmedTotal", ge=0)
    currency_code: str | None = Field(default=None, alias="currencyCode", min_length=3, max_length=3)
    deposit_amount: float | None = Field(default=None, alias="depositAmount", ge=0)
    contact_information: str | None = Field(default=None, alias="contactInformation", max_length=220)
    booking_date: str | None = Field(default=None, alias="bookingDate", min_length=1, max_length=40)
    cancellation_deadline: str | None = Field(default=None, alias="cancellationDeadline", max_length=40)
    status: BookingStatus | None = None
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


class RentACarSearchSummaryResponse(BaseModel):
    id: str
    title: str
    pickup_location: str = Field(serialization_alias="pickupLocation")
    dropoff_location: str = Field(serialization_alias="dropoffLocation")
    pickup_at: str = Field(serialization_alias="pickupAt")
    return_at: str = Field(serialization_alias="returnAt")
    vehicle_type: str = Field(serialization_alias="vehicleType")
    transmission: TransmissionPreference
    passengers: int
    luggage: int
    budget: float | None
    currency_code: str = Field(serialization_alias="currencyCode")
    notes_preview: str | None = Field(serialization_alias="notesPreview")
    status: SearchStatus
    option_count: int = Field(serialization_alias="optionCount")
    booking_count: int = Field(serialization_alias="bookingCount")
    preferred_option_id: str | None = Field(serialization_alias="preferredOptionId")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class RentACarSearchDetailResponse(RentACarSearchSummaryResponse):
    driver_age_group: str = Field(serialization_alias="driverAgeGroup")
    notes: str | None


class RentACarVehicleOptionSummaryResponse(BaseModel):
    id: str
    search_id: str = Field(serialization_alias="searchId")
    search_title: str = Field(serialization_alias="searchTitle")
    provider_name: str = Field(serialization_alias="providerName")
    vehicle_name: str = Field(serialization_alias="vehicleName")
    vehicle_class: str = Field(serialization_alias="vehicleClass")
    transmission: VehicleTransmission
    seats: int
    luggage_capacity: int = Field(serialization_alias="luggageCapacity")
    daily_base_rate: float = Field(serialization_alias="dailyBaseRate")
    rental_days: int = Field(serialization_alias="rentalDays")
    taxes_and_fees: float = Field(serialization_alias="taxesAndFees")
    deposit: float | None
    addon_estimate: float = Field(serialization_alias="addonEstimate")
    estimated_total: float = Field(serialization_alias="estimatedTotal")
    notes_preview: str | None = Field(serialization_alias="notesPreview")
    is_preferred: bool = Field(serialization_alias="isPreferred")
    availability_status: AvailabilityStatus = Field(serialization_alias="availabilityStatus")
    last_checked: str | None = Field(serialization_alias="lastChecked")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class RentACarVehicleOptionDetailResponse(RentACarVehicleOptionSummaryResponse):
    fuel_policy: str | None = Field(serialization_alias="fuelPolicy")
    mileage_policy: str | None = Field(serialization_alias="mileagePolicy")
    cancellation_terms: str | None = Field(serialization_alias="cancellationTerms")
    pickup_method: str | None = Field(serialization_alias="pickupMethod")
    reference_url: str | None = Field(serialization_alias="referenceUrl")
    notes: str | None


class RentACarBookingSummaryResponse(BaseModel):
    id: str
    search_id: str = Field(serialization_alias="searchId")
    search_title: str = Field(serialization_alias="searchTitle")
    vehicle_option_id: str | None = Field(serialization_alias="vehicleOptionId")
    vehicle_name: str | None = Field(serialization_alias="vehicleName")
    booking_reference: str = Field(serialization_alias="bookingReference")
    provider_name: str = Field(serialization_alias="providerName")
    confirmed_total: float = Field(serialization_alias="confirmedTotal")
    currency_code: str = Field(serialization_alias="currencyCode")
    deposit_amount: float | None = Field(serialization_alias="depositAmount")
    booking_date: str = Field(serialization_alias="bookingDate")
    cancellation_deadline: str | None = Field(serialization_alias="cancellationDeadline")
    status: BookingStatus
    notes_preview: str | None = Field(serialization_alias="notesPreview")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class RentACarBookingDetailResponse(RentACarBookingSummaryResponse):
    pickup_instructions: str | None = Field(serialization_alias="pickupInstructions")
    dropoff_instructions: str | None = Field(serialization_alias="dropoffInstructions")
    contact_information: str | None = Field(serialization_alias="contactInformation")
    notes: str | None


class RentACarProviderDistributionResponse(BaseModel):
    provider_name: str = Field(serialization_alias="providerName")
    option_count: int = Field(serialization_alias="optionCount")


class RentACarClassDistributionResponse(BaseModel):
    vehicle_class: str = Field(serialization_alias="vehicleClass")
    option_count: int = Field(serialization_alias="optionCount")


class RentACarDashboardResponse(BaseModel):
    searches: list[RentACarSearchSummaryResponse]
    vehicle_options: list[RentACarVehicleOptionSummaryResponse] = Field(serialization_alias="vehicleOptions")
    bookings: list[RentACarBookingSummaryResponse]
    total_searches: int = Field(serialization_alias="totalSearches")
    comparing_searches: int = Field(serialization_alias="comparingSearches")
    confirmed_bookings: int = Field(serialization_alias="confirmedBookings")
    upcoming_bookings: int = Field(serialization_alias="upcomingBookings")
    completed_bookings: int = Field(serialization_alias="completedBookings")
    average_estimated_daily_rate: float = Field(serialization_alias="averageEstimatedDailyRate")
    estimated_total_spend: float = Field(serialization_alias="estimatedTotalSpend")
    most_used_class: str | None = Field(serialization_alias="mostUsedClass")
    most_used_provider: str | None = Field(serialization_alias="mostUsedProvider")
    recently_updated_searches: list[RentACarSearchSummaryResponse] = Field(serialization_alias="recentlyUpdatedSearches")
    upcoming_cancellation_deadlines: list[RentACarBookingSummaryResponse] = Field(serialization_alias="upcomingCancellationDeadlines")
    provider_distribution: list[RentACarProviderDistributionResponse] = Field(serialization_alias="providerDistribution")
    class_distribution: list[RentACarClassDistributionResponse] = Field(serialization_alias="classDistribution")
