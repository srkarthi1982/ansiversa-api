from datetime import date, datetime
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

ArchiveFilter = Literal['active', 'archived', 'all']
RecordStatus = Literal['scheduled', 'completed', 'skipped', 'cancelled']
RecordSort = Literal['date', 'due', 'profile', 'vaccine', 'status', 'created', 'cost']
DueFilter = Literal['all', 'upcoming', 'today', 'week', 'overdue', 'completed']


def _normalize_text(value: object) -> object:
    if isinstance(value, str):
        normalized = ' '.join(value.strip().split())
        return normalized or None
    return value


def _normalize_currency(value: object) -> object:
    if isinstance(value, str):
        normalized = value.strip().upper()
        return normalized or 'USD'
    return value

class ProfileCreateRequest(BaseModel):
    full_name: str = Field(alias='fullName', min_length=1, max_length=180)
    date_of_birth: date | None = Field(default=None, alias='dateOfBirth')
    relationship: str | None = Field(default=None, max_length=80)
    nickname: str | None = Field(default=None, max_length=120)
    notes: str | None = Field(default=None, max_length=5000)
    archived: bool = False
    model_config = ConfigDict(extra='forbid', populate_by_name=True)
    @field_validator('full_name', 'relationship', 'nickname', 'notes', mode='before')
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)

class ProfileUpdateRequest(ProfileCreateRequest):
    pass

class VaccineTypeCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    disease_or_purpose: str | None = Field(default=None, alias='diseaseOrPurpose', max_length=180)
    description: str | None = Field(default=None, max_length=3000)
    sort_order: int = Field(default=0, alias='sortOrder', ge=0, le=999)
    model_config = ConfigDict(extra='forbid', populate_by_name=True)
    @field_validator('name', 'disease_or_purpose', 'description', mode='before')
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)

class VaccineTypeUpdateRequest(VaccineTypeCreateRequest):
    pass

class RecordCreateRequest(BaseModel):
    profile_id: str = Field(alias='profileId', min_length=1, max_length=36)
    vaccine_type_id: str | None = Field(default=None, alias='vaccineTypeId', max_length=36)
    vaccine_name: str = Field(alias='vaccineName', min_length=1, max_length=180)
    disease_or_purpose: str | None = Field(default=None, alias='diseaseOrPurpose', max_length=180)
    dose_number: int = Field(default=1, alias='doseNumber', ge=1, le=99)
    total_doses: int | None = Field(default=None, alias='totalDoses', ge=1, le=99)
    vaccination_date: date | None = Field(default=None, alias='vaccinationDate')
    next_due_date: date | None = Field(default=None, alias='nextDueDate')
    status: RecordStatus = 'scheduled'
    clinic_or_provider: str | None = Field(default=None, alias='clinicOrProvider', max_length=180)
    professional_name: str | None = Field(default=None, alias='professionalName', max_length=180)
    country_or_location: str | None = Field(default=None, alias='countryOrLocation', max_length=180)
    manufacturer: str | None = Field(default=None, max_length=180)
    batch_number: str | None = Field(default=None, alias='batchNumber', max_length=120)
    certificate_reference: str | None = Field(default=None, alias='certificateReference', max_length=180)
    cost: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    currency: str = Field(default='USD', min_length=3, max_length=3)
    notes: str | None = Field(default=None, max_length=5000)
    archived: bool = False
    model_config = ConfigDict(extra='forbid', populate_by_name=True)

    @field_validator('vaccine_name', 'disease_or_purpose', 'clinic_or_provider', 'professional_name', 'country_or_location', 'manufacturer', 'batch_number', 'certificate_reference', 'notes', mode='before')
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)

    @field_validator('currency', mode='before')
    @classmethod
    def normalize_currency(cls, value: object) -> object:
        return _normalize_currency(value)

    @model_validator(mode='after')
    def validate_doses_and_dates(self):
        if self.total_doses is not None and self.dose_number > self.total_doses:
            raise ValueError('doseNumber cannot be greater than totalDoses.')
        if self.status == 'completed' and self.vaccination_date is None:
            raise ValueError('vaccinationDate is required for completed records.')
        return self

class RecordUpdateRequest(RecordCreateRequest):
    pass

class ProfileResponse(BaseModel):
    id: str
    full_name: str = Field(serialization_alias='fullName')
    date_of_birth: date | None = Field(serialization_alias='dateOfBirth')
    relationship: str | None
    nickname: str | None
    notes: str | None
    archived: bool
    record_count: int = Field(serialization_alias='recordCount')
    created_at: datetime = Field(serialization_alias='createdAt')
    updated_at: datetime = Field(serialization_alias='updatedAt')

class VaccineTypeResponse(BaseModel):
    id: str
    name: str
    disease_or_purpose: str | None = Field(serialization_alias='diseaseOrPurpose')
    description: str | None
    sort_order: int = Field(serialization_alias='sortOrder')
    is_system: bool = Field(serialization_alias='isSystem')
    record_count: int = Field(serialization_alias='recordCount')
    created_at: datetime = Field(serialization_alias='createdAt')
    updated_at: datetime = Field(serialization_alias='updatedAt')

class RecordSummaryResponse(BaseModel):
    id: str
    profile_id: str = Field(serialization_alias='profileId')
    profile_name: str = Field(serialization_alias='profileName')
    vaccine_type_id: str | None = Field(serialization_alias='vaccineTypeId')
    vaccine_type_name: str | None = Field(serialization_alias='vaccineTypeName')
    vaccine_name: str = Field(serialization_alias='vaccineName')
    disease_or_purpose: str | None = Field(serialization_alias='diseaseOrPurpose')
    dose_number: int = Field(serialization_alias='doseNumber')
    total_doses: int | None = Field(serialization_alias='totalDoses')
    completion_percent: float = Field(serialization_alias='completionPercent')
    series_complete: bool = Field(serialization_alias='seriesComplete')
    vaccination_date: date | None = Field(serialization_alias='vaccinationDate')
    next_due_date: date | None = Field(serialization_alias='nextDueDate')
    status: str
    derived_status: str = Field(serialization_alias='derivedStatus')
    clinic_or_provider: str | None = Field(serialization_alias='clinicOrProvider')
    cost: Decimal | None
    currency: str
    archived: bool
    created_at: datetime = Field(serialization_alias='createdAt')
    updated_at: datetime = Field(serialization_alias='updatedAt')

class RecordDetailResponse(RecordSummaryResponse):
    professional_name: str | None = Field(serialization_alias='professionalName')
    country_or_location: str | None = Field(serialization_alias='countryOrLocation')
    manufacturer: str | None
    batch_number: str | None = Field(serialization_alias='batchNumber')
    certificate_reference: str | None = Field(serialization_alias='certificateReference')
    notes: str | None

class RecordListResponse(BaseModel):
    items: list[RecordSummaryResponse]
    total: int
    page: int
    page_size: int = Field(serialization_alias='pageSize')

class CountItem(BaseModel):
    label: str
    count: int

class DashboardResponse(BaseModel):
    total_profiles: int = Field(serialization_alias='totalProfiles')
    total_records: int = Field(serialization_alias='totalRecords')
    completed_doses: int = Field(serialization_alias='completedDoses')
    upcoming_doses: int = Field(serialization_alias='upcomingDoses')
    due_today: int = Field(serialization_alias='dueToday')
    due_this_week: int = Field(serialization_alias='dueThisWeek')
    overdue_doses: int = Field(serialization_alias='overdueDoses')
    completed_series: int = Field(serialization_alias='completedSeries')
    archived_records: int = Field(serialization_alias='archivedRecords')

class InsightsResponse(DashboardResponse):
    profiles: list[ProfileResponse]
    vaccine_types: list[VaccineTypeResponse] = Field(serialization_alias='vaccineTypes')
    records_by_vaccine: list[CountItem] = Field(serialization_alias='recordsByVaccine')
    records_by_profile: list[CountItem] = Field(serialization_alias='recordsByProfile')
    records_by_status: list[CountItem] = Field(serialization_alias='recordsByStatus')
    records_by_year: list[CountItem] = Field(serialization_alias='recordsByYear')
    recently_added_records: list[RecordSummaryResponse] = Field(serialization_alias='recentlyAddedRecords')
    recently_completed_records: list[RecordSummaryResponse] = Field(serialization_alias='recentlyCompletedRecords')
