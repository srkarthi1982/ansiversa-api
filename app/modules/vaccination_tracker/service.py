from __future__ import annotations
from collections import Counter
from datetime import date, timedelta
from decimal import Decimal
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.modules.auth.models import User
from app.modules.vaccination_tracker import repository
from app.modules.vaccination_tracker.models import VaccinationProfile, VaccinationRecord, VaccineType
from app.modules.vaccination_tracker.schemas import ArchiveFilter, CountItem, DashboardResponse, DueFilter, InsightsResponse, ProfileCreateRequest, ProfileResponse, ProfileUpdateRequest, RecordCreateRequest, RecordDetailResponse, RecordListResponse, RecordSort, RecordSummaryResponse, RecordUpdateRequest, VaccineTypeCreateRequest, VaccineTypeResponse, VaccineTypeUpdateRequest

DEFAULT_VACCINES = [('Influenza', 'Seasonal flu', 10), ('COVID-19', 'COVID-19', 20), ('Hepatitis A', 'Hepatitis A', 30), ('Hepatitis B', 'Hepatitis B', 40), ('Tetanus', 'Tetanus', 50), ('Diphtheria', 'Diphtheria', 60), ('Pertussis', 'Pertussis', 70), ('MMR', 'Measles, mumps, rubella', 80), ('Polio', 'Polio', 90), ('Varicella', 'Chickenpox', 100), ('HPV', 'Human papillomavirus', 110), ('Pneumococcal', 'Pneumococcal disease', 120), ('Meningococcal', 'Meningococcal disease', 130), ('Rabies', 'Rabies', 140), ('Typhoid', 'Typhoid', 150), ('Yellow fever', 'Yellow fever', 160), ('Other', None, 170)]

def _today() -> date:
    return date.today()

def _not_found(resource: str) -> None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'{resource} was not found.')

def _commit_or_conflict(db: Session, message: str) -> None:
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=message) from exc

def _decimal(value) -> Decimal:
    if value is None:
        return Decimal('0.00')
    return Decimal(str(value)).quantize(Decimal('0.01'))

def _derived_status(item: VaccinationRecord, today: date | None = None) -> str:
    current = today or _today()
    if item.archived:
        return 'archived'
    if item.status == 'completed':
        return 'completed'
    if item.status in {'skipped', 'cancelled'}:
        return item.status
    if item.next_due_date:
        if item.next_due_date < current:
            return 'overdue'
        if item.next_due_date == current:
            return 'due_today'
        if item.next_due_date <= current + timedelta(days=7):
            return 'due_soon'
    return 'scheduled'

def _completion_percent(item: VaccinationRecord) -> float:
    if item.total_doses and item.total_doses > 0:
        completed = item.dose_number if item.status == 'completed' else max(item.dose_number - 1, 0)
        return float(min(100, round(completed / item.total_doses * 100, 1)))
    return 100.0 if item.status == 'completed' else 0.0

def _series_complete(item: VaccinationRecord) -> bool:
    return bool(item.total_doses and item.status == 'completed' and item.dose_number >= item.total_doses)

def ensure_default_vaccine_types(db: Session, user: User) -> None:
    existing = {item.name.lower() for item in repository.list_vaccine_types(db, user.id)}
    created = False
    for name, purpose, order in DEFAULT_VACCINES:
        if name.lower() not in existing:
            repository.add(db, VaccineType(owner_id=user.id, name=name, disease_or_purpose=purpose, sort_order=order, is_system=True)); created = True
    if created:
        _commit_or_conflict(db, 'Unable to prepare vaccine types.')

def _get_owned_profile(db: Session, user: User, profile_id: str) -> VaccinationProfile:
    item = repository.get_profile(db, profile_id)
    if not item or item.owner_id != user.id:
        _not_found('Vaccination profile')
    return item

def _get_owned_vaccine_type(db: Session, user: User, vaccine_type_id: str) -> VaccineType:
    item = repository.get_vaccine_type(db, vaccine_type_id)
    if not item or item.owner_id != user.id:
        _not_found('Vaccine type')
    return item

def _get_owned_record(db: Session, user: User, record_id: str) -> VaccinationRecord:
    item = repository.get_record(db, record_id)
    if not item or item.owner_id != user.id:
        _not_found('Vaccination record')
    return item

def _profile_response(item: VaccinationProfile, count: int = 0) -> ProfileResponse:
    return ProfileResponse(id=item.id, full_name=item.full_name, date_of_birth=item.date_of_birth, relationship=item.relationship, nickname=item.nickname, notes=item.notes, archived=item.archived, record_count=count, created_at=item.created_at, updated_at=item.updated_at)

def _vaccine_response(item: VaccineType, count: int = 0) -> VaccineTypeResponse:
    return VaccineTypeResponse(id=item.id, name=item.name, disease_or_purpose=item.disease_or_purpose, description=item.description, sort_order=item.sort_order, is_system=item.is_system, record_count=count, created_at=item.created_at, updated_at=item.updated_at)

def _record_summary(item: VaccinationRecord, current: date | None = None) -> RecordSummaryResponse:
    return RecordSummaryResponse(id=item.id, profile_id=item.profile_id, profile_name=item.profile.full_name, vaccine_type_id=item.vaccine_type_id, vaccine_type_name=item.vaccine_type.name if item.vaccine_type else None, vaccine_name=item.vaccine_name, disease_or_purpose=item.disease_or_purpose, dose_number=item.dose_number, total_doses=item.total_doses, completion_percent=_completion_percent(item), series_complete=_series_complete(item), vaccination_date=item.vaccination_date, next_due_date=item.next_due_date, status=item.status, derived_status=_derived_status(item, current), clinic_or_provider=item.clinic_or_provider, cost=item.cost, currency=item.currency, archived=item.archived, created_at=item.created_at, updated_at=item.updated_at)

def _record_detail(item: VaccinationRecord) -> RecordDetailResponse:
    return RecordDetailResponse(**_record_summary(item).model_dump(), professional_name=item.professional_name, country_or_location=item.country_or_location, manufacturer=item.manufacturer, batch_number=item.batch_number, certificate_reference=item.certificate_reference, notes=item.notes)

def list_profiles(db: Session, user: User) -> list[ProfileResponse]:
    counts = repository.record_counts_by_profile(db, user.id)
    return [_profile_response(item, counts.get(item.id, 0)) for item in repository.list_profiles(db, user.id)]

def create_profile(db: Session, user: User, payload: ProfileCreateRequest) -> ProfileResponse:
    item = VaccinationProfile(owner_id=user.id, full_name=payload.full_name, date_of_birth=payload.date_of_birth, relationship=payload.relationship, nickname=payload.nickname, notes=payload.notes, archived=payload.archived)
    repository.add(db, item); _commit_or_conflict(db, 'Unable to create vaccination profile.'); db.refresh(item); return _profile_response(item)

def update_profile(db: Session, user: User, profile_id: str, payload: ProfileUpdateRequest) -> ProfileResponse:
    item = _get_owned_profile(db, user, profile_id)
    item.full_name = payload.full_name; item.date_of_birth = payload.date_of_birth; item.relationship = payload.relationship; item.nickname = payload.nickname; item.notes = payload.notes; item.archived = payload.archived
    _commit_or_conflict(db, 'Unable to update vaccination profile.'); db.refresh(item); return _profile_response(item, repository.count_records_for_profile(db, user.id, item.id))

def set_profile_archived(db: Session, user: User, profile_id: str, archived: bool) -> ProfileResponse:
    item = _get_owned_profile(db, user, profile_id); item.archived = archived; db.commit(); db.refresh(item); return _profile_response(item, repository.count_records_for_profile(db, user.id, item.id))

def delete_profile(db: Session, user: User, profile_id: str) -> None:
    item = _get_owned_profile(db, user, profile_id)
    if repository.count_records_for_profile(db, user.id, item.id) > 0:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Profile has vaccination records. Delete or reassign records first.')
    repository.delete_record(db, item); db.commit()

def list_vaccine_types(db: Session, user: User) -> list[VaccineTypeResponse]:
    ensure_default_vaccine_types(db, user); counts = repository.record_counts_by_vaccine_type(db, user.id)
    return [_vaccine_response(item, counts.get(item.id, 0)) for item in repository.list_vaccine_types(db, user.id)]

def create_vaccine_type(db: Session, user: User, payload: VaccineTypeCreateRequest) -> VaccineTypeResponse:
    item = VaccineType(owner_id=user.id, name=payload.name, disease_or_purpose=payload.disease_or_purpose, description=payload.description, sort_order=payload.sort_order)
    repository.add(db, item); _commit_or_conflict(db, 'A vaccine type with this name already exists.'); db.refresh(item); return _vaccine_response(item)

def update_vaccine_type(db: Session, user: User, vaccine_type_id: str, payload: VaccineTypeUpdateRequest) -> VaccineTypeResponse:
    item = _get_owned_vaccine_type(db, user, vaccine_type_id)
    item.name = payload.name; item.disease_or_purpose = payload.disease_or_purpose; item.description = payload.description; item.sort_order = payload.sort_order
    _commit_or_conflict(db, 'A vaccine type with this name already exists.'); db.refresh(item); return _vaccine_response(item, repository.count_records_for_vaccine_type(db, user.id, item.id))

def delete_vaccine_type(db: Session, user: User, vaccine_type_id: str) -> None:
    item = _get_owned_vaccine_type(db, user, vaccine_type_id)
    if repository.count_records_for_vaccine_type(db, user.id, item.id) > 0:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Vaccine type has records. Reassign or delete records first.')
    repository.delete_record(db, item); db.commit()

def _validate_record_refs(db: Session, user: User, payload: RecordCreateRequest | RecordUpdateRequest) -> None:
    _get_owned_profile(db, user, payload.profile_id)
    if payload.vaccine_type_id:
        _get_owned_vaccine_type(db, user, payload.vaccine_type_id)

def _check_duplicate(db: Session, user: User, payload: RecordCreateRequest | RecordUpdateRequest, current_id: str | None = None) -> None:
    key_name = payload.vaccine_name.strip().lower()
    for item in repository.list_records(db, user.id):
        if current_id and item.id == current_id:
            continue
        if item.profile_id == payload.profile_id and item.vaccine_name.lower() == key_name and item.dose_number == payload.dose_number:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='A record for this profile, vaccine, and dose number already exists.')

def _apply_record_payload(item: VaccinationRecord, payload: RecordCreateRequest | RecordUpdateRequest) -> None:
    item.profile_id = payload.profile_id; item.vaccine_type_id = payload.vaccine_type_id; item.vaccine_name = payload.vaccine_name; item.disease_or_purpose = payload.disease_or_purpose; item.dose_number = payload.dose_number; item.total_doses = payload.total_doses; item.vaccination_date = payload.vaccination_date; item.next_due_date = payload.next_due_date; item.status = payload.status; item.clinic_or_provider = payload.clinic_or_provider; item.professional_name = payload.professional_name; item.country_or_location = payload.country_or_location; item.manufacturer = payload.manufacturer; item.batch_number = payload.batch_number; item.certificate_reference = payload.certificate_reference; item.cost = payload.cost; item.currency = payload.currency; item.notes = payload.notes; item.archived = payload.archived

def list_records(db: Session, user: User, query: str | None = None, archive_filter: ArchiveFilter = 'active', profile_id: str | None = None, vaccine_type_id: str | None = None, status_filter: str | None = None, due_filter: DueFilter = 'all', date_from: date | None = None, date_to: date | None = None, sort_by: RecordSort = 'due', page: int = 1, page_size: int = 25) -> RecordListResponse:
    ensure_default_vaccine_types(db, user); current = _today(); term = (query or '').strip().lower(); result = []
    for item in repository.list_records(db, user.id):
        derived = _derived_status(item, current)
        record_date = item.vaccination_date or item.next_due_date
        if archive_filter == 'active' and item.archived: continue
        if archive_filter == 'archived' and not item.archived: continue
        if profile_id and item.profile_id != profile_id: continue
        if vaccine_type_id and item.vaccine_type_id != vaccine_type_id: continue
        if status_filter and item.status != status_filter and derived != status_filter: continue
        if date_from and (not record_date or record_date < date_from): continue
        if date_to and (not record_date or record_date > date_to): continue
        if due_filter == 'upcoming' and derived not in {'scheduled', 'due_soon', 'due_today'}: continue
        if due_filter == 'today' and derived != 'due_today': continue
        if due_filter == 'week' and not (item.next_due_date and current <= item.next_due_date <= current + timedelta(days=7)): continue
        if due_filter == 'overdue' and derived != 'overdue': continue
        if due_filter == 'completed' and item.status != 'completed': continue
        haystack = [item.profile.full_name, item.vaccine_name, item.disease_or_purpose or '', item.clinic_or_provider or '', item.professional_name or '', item.country_or_location or '', item.manufacturer or '', item.batch_number or '', item.certificate_reference or '', item.notes or '']
        if term and not any(term in value.lower() for value in haystack): continue
        result.append(item)
    if sort_by == 'profile': result.sort(key=lambda item: (item.profile.full_name.lower(), item.vaccine_name.lower()))
    elif sort_by == 'vaccine': result.sort(key=lambda item: (item.vaccine_name.lower(), item.dose_number))
    elif sort_by == 'status': result.sort(key=lambda item: (_derived_status(item, current), item.next_due_date or date.max))
    elif sort_by == 'created': result.sort(key=lambda item: item.created_at, reverse=True)
    elif sort_by == 'cost': result.sort(key=lambda item: _decimal(item.cost), reverse=True)
    elif sort_by == 'date': result.sort(key=lambda item: (item.vaccination_date or date.max, item.created_at), reverse=True)
    else: result.sort(key=lambda item: (item.next_due_date or date.max, item.vaccine_name.lower()))
    total = len(result); start = (page - 1) * page_size
    return RecordListResponse(items=[_record_summary(item, current) for item in result[start:start + page_size]], total=total, page=page, page_size=page_size)

def create_record(db: Session, user: User, payload: RecordCreateRequest) -> RecordDetailResponse:
    _validate_record_refs(db, user, payload); _check_duplicate(db, user, payload)
    item = VaccinationRecord(owner_id=user.id, profile_id=payload.profile_id, vaccine_name=payload.vaccine_name, dose_number=payload.dose_number)
    _apply_record_payload(item, payload); repository.add(db, item); _commit_or_conflict(db, 'Unable to create vaccination record.'); db.refresh(item); return _record_detail(_get_owned_record(db, user, item.id))

def get_record(db: Session, user: User, record_id: str) -> RecordDetailResponse:
    return _record_detail(_get_owned_record(db, user, record_id))

def update_record(db: Session, user: User, record_id: str, payload: RecordUpdateRequest) -> RecordDetailResponse:
    item = _get_owned_record(db, user, record_id); _validate_record_refs(db, user, payload); _check_duplicate(db, user, payload, item.id); _apply_record_payload(item, payload); _commit_or_conflict(db, 'Unable to update vaccination record.'); return _record_detail(_get_owned_record(db, user, item.id))

def set_record_archived(db: Session, user: User, record_id: str, archived: bool) -> RecordDetailResponse:
    item = _get_owned_record(db, user, record_id); item.archived = archived; db.commit(); return _record_detail(_get_owned_record(db, user, item.id))

def delete_record(db: Session, user: User, record_id: str) -> None:
    item = _get_owned_record(db, user, record_id); repository.delete_record(db, item); db.commit()

def get_dashboard(db: Session, user: User) -> DashboardResponse:
    ensure_default_vaccine_types(db, user); current = _today(); profiles = [p for p in repository.list_profiles(db, user.id) if not p.archived]; records = repository.list_records(db, user.id); active = [r for r in records if not r.archived]; derived = [_derived_status(r, current) for r in active]
    return DashboardResponse(total_profiles=len(profiles), total_records=len(active), completed_doses=sum(1 for r in active if r.status == 'completed'), upcoming_doses=sum(1 for d in derived if d in {'scheduled', 'due_soon', 'due_today'}), due_today=derived.count('due_today'), due_this_week=sum(1 for r in active if r.next_due_date and current <= r.next_due_date <= current + timedelta(days=7)), overdue_doses=derived.count('overdue'), completed_series=sum(1 for r in active if _series_complete(r)), archived_records=sum(1 for r in records if r.archived))

def get_insights(db: Session, user: User) -> InsightsResponse:
    current = _today(); records = [r for r in repository.list_records(db, user.id) if not r.archived]; dashboard = get_dashboard(db, user); by_vaccine = Counter(r.vaccine_name for r in records); by_profile = Counter(r.profile.full_name for r in records); by_status = Counter(_derived_status(r, current).replace('_', ' ').title() for r in records); by_year = Counter(str((r.vaccination_date or r.next_due_date or r.created_at.date()).year) for r in records)
    recent_added = sorted(records, key=lambda r: r.created_at, reverse=True)[:8]
    recent_completed = sorted([r for r in records if r.status == 'completed'], key=lambda r: r.vaccination_date or r.created_at.date(), reverse=True)[:8]
    return InsightsResponse(**dashboard.model_dump(), profiles=list_profiles(db, user), vaccine_types=list_vaccine_types(db, user), records_by_vaccine=[CountItem(label=k, count=v) for k, v in by_vaccine.most_common()], records_by_profile=[CountItem(label=k, count=v) for k, v in by_profile.most_common()], records_by_status=[CountItem(label=k, count=v) for k, v in by_status.most_common()], records_by_year=[CountItem(label=k, count=v) for k, v in sorted(by_year.items(), reverse=True)], recently_added_records=[_record_summary(r, current) for r in recent_added], recently_completed_records=[_record_summary(r, current) for r in recent_completed])
