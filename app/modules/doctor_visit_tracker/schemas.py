from datetime import date, datetime, time
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator

ArchiveFilter = Literal['active', 'archived', 'all']
VisitStatus = Literal['scheduled', 'completed', 'cancelled', 'missed']
VisitSort = Literal['date', 'doctor', 'specialty', 'status', 'created', 'cost']
TimeFilter = Literal['all', 'upcoming', 'past', 'today', 'month', 'follow_up']

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

class SpecialtyCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    sort_order: int = Field(default=0, alias='sortOrder', ge=0, le=999)
    model_config = ConfigDict(extra='forbid', populate_by_name=True)
    @field_validator('name', mode='before')
    @classmethod
    def normalize_name(cls, value: object) -> object:
        return _normalize_text(value)

class SpecialtyUpdateRequest(SpecialtyCreateRequest):
    pass

class SpecialtyResponse(BaseModel):
    id: str
    name: str
    sort_order: int = Field(serialization_alias='sortOrder')
    is_system: bool = Field(serialization_alias='isSystem')
    visit_count: int = Field(serialization_alias='visitCount')
    created_at: datetime = Field(serialization_alias='createdAt')
    updated_at: datetime = Field(serialization_alias='updatedAt')

class VisitCreateRequest(BaseModel):
    visit_title: str = Field(alias='visitTitle', min_length=1, max_length=180)
    doctor_name: str = Field(alias='doctorName', min_length=1, max_length=180)
    specialty_id: str = Field(alias='specialtyId', min_length=1, max_length=36)
    clinic_name: str | None = Field(default=None, alias='clinicName', max_length=180)
    visit_date: date = Field(alias='visitDate')
    visit_time: time | None = Field(default=None, alias='visitTime')
    status: VisitStatus = 'scheduled'
    reason: str | None = Field(default=None, max_length=5000)
    diagnosis_notes: str | None = Field(default=None, alias='diagnosisNotes', max_length=5000)
    medications: str | None = Field(default=None, max_length=5000)
    follow_up_date: date | None = Field(default=None, alias='followUpDate')
    visit_cost: Decimal | None = Field(default=None, alias='visitCost', ge=0, max_digits=12, decimal_places=2)
    currency: str = Field(default='USD', min_length=3, max_length=3)
    insurance_notes: str | None = Field(default=None, alias='insuranceNotes', max_length=5000)
    personal_notes: str | None = Field(default=None, alias='personalNotes', max_length=5000)
    archived: bool = False
    model_config = ConfigDict(extra='forbid', populate_by_name=True)
    @field_validator('visit_title', 'doctor_name', 'clinic_name', 'reason', 'diagnosis_notes', 'medications', 'insurance_notes', 'personal_notes', mode='before')
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)
    @field_validator('currency', mode='before')
    @classmethod
    def normalize_currency(cls, value: object) -> object:
        return _normalize_currency(value)

class VisitUpdateRequest(VisitCreateRequest):
    pass

class VisitSummaryResponse(BaseModel):
    id: str
    visit_title: str = Field(serialization_alias='visitTitle')
    doctor_name: str = Field(serialization_alias='doctorName')
    specialty_id: str = Field(serialization_alias='specialtyId')
    specialty_name: str = Field(serialization_alias='specialtyName')
    clinic_name: str | None = Field(serialization_alias='clinicName')
    visit_date: date = Field(serialization_alias='visitDate')
    visit_time: time | None = Field(serialization_alias='visitTime')
    status: str
    follow_up_date: date | None = Field(serialization_alias='followUpDate')
    visit_cost: Decimal | None = Field(serialization_alias='visitCost')
    currency: str
    archived: bool
    days_until_visit: int = Field(serialization_alias='daysUntilVisit')
    created_at: datetime = Field(serialization_alias='createdAt')
    updated_at: datetime = Field(serialization_alias='updatedAt')

class VisitDetailResponse(VisitSummaryResponse):
    reason: str | None
    diagnosis_notes: str | None = Field(serialization_alias='diagnosisNotes')
    medications: str | None
    insurance_notes: str | None = Field(serialization_alias='insuranceNotes')
    personal_notes: str | None = Field(serialization_alias='personalNotes')

class CountItem(BaseModel):
    label: str
    count: int

class DashboardResponse(BaseModel):
    total_visits: int = Field(serialization_alias='totalVisits')
    upcoming_appointments: int = Field(serialization_alias='upcomingAppointments')
    completed_visits: int = Field(serialization_alias='completedVisits')
    missed_appointments: int = Field(serialization_alias='missedAppointments')
    scheduled_today: int = Field(serialization_alias='scheduledToday')
    upcoming_follow_ups: int = Field(serialization_alias='upcomingFollowUps')
    archived_visits: int = Field(serialization_alias='archivedVisits')
    total_cost: Decimal = Field(serialization_alias='totalCost')

class InsightsResponse(DashboardResponse):
    specialties: list[SpecialtyResponse]
    visits_by_specialty: list[CountItem] = Field(serialization_alias='visitsBySpecialty')
    visits_by_month: list[CountItem] = Field(serialization_alias='visitsByMonth')
    visits_by_status: list[CountItem] = Field(serialization_alias='visitsByStatus')
    recent_visits: list[VisitSummaryResponse] = Field(serialization_alias='recentVisits')
    upcoming_follow_up_visits: list[VisitSummaryResponse] = Field(serialization_alias='upcomingFollowUpVisits')
    upcoming_appointments_list: list[VisitSummaryResponse] = Field(serialization_alias='upcomingAppointmentsList')
