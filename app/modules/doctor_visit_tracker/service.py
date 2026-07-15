from __future__ import annotations
import calendar
from collections import Counter
from datetime import date
from decimal import Decimal
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.modules.auth.models import User
from app.modules.doctor_visit_tracker import repository
from app.modules.doctor_visit_tracker.models import DoctorSpecialty, DoctorVisit
from app.modules.doctor_visit_tracker.schemas import ArchiveFilter, CountItem, DashboardResponse, InsightsResponse, SpecialtyCreateRequest, SpecialtyResponse, SpecialtyUpdateRequest, TimeFilter, VisitCreateRequest, VisitDetailResponse, VisitSort, VisitSummaryResponse, VisitUpdateRequest

DEFAULT_SPECIALTIES = [('General Physician', 10), ('Pediatrician', 20), ('Cardiologist', 30), ('Dermatologist', 40), ('Dentist', 50), ('ENT', 60), ('Neurologist', 70), ('Orthopedic', 80), ('Ophthalmologist', 90), ('Gynecologist', 100), ('Psychiatrist', 110), ('Urologist', 120), ('Other', 130)]

def _today() -> date:
    return date.today()

def _not_found(resource: str) -> None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'{resource} was not found.')

def _commit_or_conflict(db: Session, message: str) -> None:
    try: db.commit()
    except IntegrityError as exc:
        db.rollback(); raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=message) from exc

def _decimal(value) -> Decimal:
    if value is None: return Decimal('0.00')
    return Decimal(str(value)).quantize(Decimal('0.01'))

def _time_sort(value) -> str:
    return value.isoformat() if value else '00:00'

def ensure_default_specialties(db: Session, user: User) -> None:
    existing = {item.name.lower() for item in repository.list_specialties(db, user.id)}
    created = False
    for name, sort_order in DEFAULT_SPECIALTIES:
        if name.lower() not in existing:
            repository.add(db, DoctorSpecialty(owner_id=user.id, name=name, sort_order=sort_order, is_system=True)); created = True
    if created: _commit_or_conflict(db, 'Unable to prepare doctor specialties.')

def _get_owned_specialty(db: Session, user: User, specialty_id: str) -> DoctorSpecialty:
    item = repository.get_specialty(db, specialty_id)
    if not item or item.owner_id != user.id: _not_found('Doctor specialty')
    return item

def _get_owned_visit(db: Session, user: User, visit_id: str) -> DoctorVisit:
    item = repository.get_visit(db, visit_id)
    if not item or item.owner_id != user.id: _not_found('Doctor visit')
    return item

def _specialty_response(item: DoctorSpecialty, visit_count: int = 0) -> SpecialtyResponse:
    return SpecialtyResponse(id=item.id, name=item.name, sort_order=item.sort_order, is_system=item.is_system, visit_count=visit_count, created_at=item.created_at, updated_at=item.updated_at)

def _visit_summary(item: DoctorVisit, current: date | None = None) -> VisitSummaryResponse:
    today = current or _today()
    return VisitSummaryResponse(id=item.id, visit_title=item.visit_title, doctor_name=item.doctor_name, specialty_id=item.specialty_id, specialty_name=item.specialty.name, clinic_name=item.clinic_name, visit_date=item.visit_date, visit_time=item.visit_time, status=item.status, follow_up_date=item.follow_up_date, visit_cost=item.visit_cost, currency=item.currency, archived=item.archived, days_until_visit=(item.visit_date - today).days, created_at=item.created_at, updated_at=item.updated_at)

def _visit_detail(item: DoctorVisit) -> VisitDetailResponse:
    return VisitDetailResponse(**_visit_summary(item).model_dump(), reason=item.reason, diagnosis_notes=item.diagnosis_notes, medications=item.medications, insurance_notes=item.insurance_notes, personal_notes=item.personal_notes)

def list_specialties(db: Session, user: User) -> list[SpecialtyResponse]:
    ensure_default_specialties(db, user); counts = repository.visit_counts_by_specialty(db, user.id)
    return [_specialty_response(item, counts.get(item.id, 0)) for item in repository.list_specialties(db, user.id)]

def create_specialty(db: Session, user: User, payload: SpecialtyCreateRequest) -> SpecialtyResponse:
    item = DoctorSpecialty(owner_id=user.id, name=payload.name, sort_order=payload.sort_order)
    repository.add(db, item); _commit_or_conflict(db, 'A specialty with this name already exists.'); db.refresh(item); return _specialty_response(item)

def update_specialty(db: Session, user: User, specialty_id: str, payload: SpecialtyUpdateRequest) -> SpecialtyResponse:
    item = _get_owned_specialty(db, user, specialty_id); item.name = payload.name; item.sort_order = payload.sort_order
    _commit_or_conflict(db, 'A specialty with this name already exists.'); db.refresh(item); return _specialty_response(item, repository.count_visits_for_specialty(db, user.id, item.id))

def delete_specialty(db: Session, user: User, specialty_id: str) -> None:
    item = _get_owned_specialty(db, user, specialty_id)
    if repository.count_visits_for_specialty(db, user.id, item.id) > 0: raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Specialty has visits. Reassign or delete visits first.')
    repository.delete_record(db, item); db.commit()

def _apply_visit_payload(item: DoctorVisit, payload: VisitCreateRequest | VisitUpdateRequest) -> None:
    item.visit_title = payload.visit_title; item.doctor_name = payload.doctor_name; item.specialty_id = payload.specialty_id; item.clinic_name = payload.clinic_name; item.visit_date = payload.visit_date; item.visit_time = payload.visit_time; item.status = payload.status; item.reason = payload.reason; item.diagnosis_notes = payload.diagnosis_notes; item.medications = payload.medications; item.follow_up_date = payload.follow_up_date; item.visit_cost = payload.visit_cost; item.currency = payload.currency; item.insurance_notes = payload.insurance_notes; item.personal_notes = payload.personal_notes; item.archived = payload.archived

def list_visits(db: Session, user: User, query: str | None = None, archive_filter: ArchiveFilter = 'active', specialty_id: str | None = None, status_filter: str | None = None, time_filter: TimeFilter = 'all', sort_by: VisitSort = 'date') -> list[VisitSummaryResponse]:
    ensure_default_specialties(db, user); visits = repository.list_visits(db, user.id); today = _today(); term = (query or '').strip().lower(); result = []
    for item in visits:
        if archive_filter == 'active' and item.archived: continue
        if archive_filter == 'archived' and not item.archived: continue
        if specialty_id and item.specialty_id != specialty_id: continue
        if status_filter and item.status != status_filter: continue
        if term and not any(term in value.lower() for value in [item.visit_title, item.doctor_name, item.clinic_name or '', item.specialty.name, item.reason or '', item.diagnosis_notes or '', item.medications or '', item.insurance_notes or '', item.personal_notes or '']): continue
        if time_filter == 'upcoming' and item.visit_date < today: continue
        if time_filter == 'past' and item.visit_date >= today: continue
        if time_filter == 'today' and item.visit_date != today: continue
        if time_filter == 'month' and not (item.visit_date.year == today.year and item.visit_date.month == today.month): continue
        if time_filter == 'follow_up' and item.follow_up_date is None: continue
        result.append(item)
    if sort_by == 'doctor': result.sort(key=lambda item: item.doctor_name.lower())
    elif sort_by == 'specialty': result.sort(key=lambda item: (item.specialty.name, item.visit_date))
    elif sort_by == 'status': result.sort(key=lambda item: (item.status, item.visit_date))
    elif sort_by == 'created': result.sort(key=lambda item: item.created_at, reverse=True)
    elif sort_by == 'cost': result.sort(key=lambda item: _decimal(item.visit_cost), reverse=True)
    else: result.sort(key=lambda item: (item.visit_date, _time_sort(item.visit_time), item.doctor_name.lower()))
    return [_visit_summary(item, today) for item in result]

def create_visit(db: Session, user: User, payload: VisitCreateRequest) -> VisitDetailResponse:
    _get_owned_specialty(db, user, payload.specialty_id); item = DoctorVisit(owner_id=user.id, specialty_id=payload.specialty_id, visit_title=payload.visit_title, doctor_name=payload.doctor_name, visit_date=payload.visit_date)
    _apply_visit_payload(item, payload); repository.add(db, item); _commit_or_conflict(db, 'Unable to create doctor visit.'); db.refresh(item); return _visit_detail(_get_owned_visit(db, user, item.id))

def get_visit(db: Session, user: User, visit_id: str) -> VisitDetailResponse:
    return _visit_detail(_get_owned_visit(db, user, visit_id))

def update_visit(db: Session, user: User, visit_id: str, payload: VisitUpdateRequest) -> VisitDetailResponse:
    item = _get_owned_visit(db, user, visit_id); _get_owned_specialty(db, user, payload.specialty_id); _apply_visit_payload(item, payload); _commit_or_conflict(db, 'Unable to update doctor visit.'); return _visit_detail(_get_owned_visit(db, user, item.id))

def set_visit_archived(db: Session, user: User, visit_id: str, archived: bool) -> VisitDetailResponse:
    item = _get_owned_visit(db, user, visit_id); item.archived = archived; db.commit(); return _visit_detail(_get_owned_visit(db, user, item.id))

def delete_visit(db: Session, user: User, visit_id: str) -> None:
    item = _get_owned_visit(db, user, visit_id); repository.delete_record(db, item); db.commit()

def get_dashboard(db: Session, user: User) -> DashboardResponse:
    ensure_default_specialties(db, user); today = _today(); visits = repository.list_visits(db, user.id); active = [item for item in visits if not item.archived]
    return DashboardResponse(total_visits=len(active), upcoming_appointments=sum(1 for item in active if item.visit_date >= today and item.status == 'scheduled'), completed_visits=sum(1 for item in active if item.status == 'completed'), missed_appointments=sum(1 for item in active if item.status == 'missed'), scheduled_today=sum(1 for item in active if item.visit_date == today), upcoming_follow_ups=sum(1 for item in active if item.follow_up_date and item.follow_up_date >= today), archived_visits=sum(1 for item in visits if item.archived), total_cost=sum((_decimal(item.visit_cost) for item in active), Decimal('0.00')))

def get_insights(db: Session, user: User) -> InsightsResponse:
    today = _today(); visits = [item for item in repository.list_visits(db, user.id) if not item.archived]; dashboard = get_dashboard(db, user)
    by_specialty = Counter(item.specialty.name for item in visits); by_month = Counter(calendar.month_name[item.visit_date.month] for item in visits); by_status = Counter(item.status for item in visits)
    recent = sorted(visits, key=lambda item: item.visit_date, reverse=True)[:8]
    followups = sorted([item for item in visits if item.follow_up_date and item.follow_up_date >= today], key=lambda item: item.follow_up_date or today)[:8]
    upcoming = sorted([item for item in visits if item.visit_date >= today and item.status == 'scheduled'], key=lambda item: item.visit_date)[:8]
    return InsightsResponse(**dashboard.model_dump(), specialties=list_specialties(db, user), visits_by_specialty=[CountItem(label=k, count=v) for k, v in by_specialty.most_common()], visits_by_month=[CountItem(label=k, count=v) for k, v in by_month.items()], visits_by_status=[CountItem(label=k.title(), count=v) for k, v in by_status.most_common()], recent_visits=[_visit_summary(item, today) for item in recent], upcoming_follow_up_visits=[_visit_summary(item, today) for item in followups], upcoming_appointments_list=[_visit_summary(item, today) for item in upcoming])
