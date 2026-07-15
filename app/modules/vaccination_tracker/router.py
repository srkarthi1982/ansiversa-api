from datetime import date
from fastapi import APIRouter, Query, Response, status
from app.modules.vaccination_tracker import service
from app.modules.vaccination_tracker.dependencies import CurrentVaccinationUser, VaccinationDB
from app.modules.vaccination_tracker.schemas import ArchiveFilter, DashboardResponse, DueFilter, InsightsResponse, ProfileCreateRequest, ProfileResponse, ProfileUpdateRequest, RecordCreateRequest, RecordDetailResponse, RecordListResponse, RecordSort, RecordUpdateRequest, VaccineTypeCreateRequest, VaccineTypeResponse, VaccineTypeUpdateRequest

router = APIRouter()

@router.get('/dashboard', response_model=DashboardResponse, operation_id='getVaccinationTrackerDashboard')
def get_dashboard(db: VaccinationDB, current_user: CurrentVaccinationUser): return service.get_dashboard(db, current_user)

@router.get('/insights', response_model=InsightsResponse, operation_id='getVaccinationTrackerInsights')
def get_insights(db: VaccinationDB, current_user: CurrentVaccinationUser): return service.get_insights(db, current_user)

@router.get('/profiles', response_model=list[ProfileResponse], operation_id='listVaccinationTrackerProfiles')
def list_profiles(db: VaccinationDB, current_user: CurrentVaccinationUser): return service.list_profiles(db, current_user)

@router.post('/profiles', response_model=ProfileResponse, status_code=status.HTTP_201_CREATED, operation_id='createVaccinationTrackerProfile')
def create_profile(payload: ProfileCreateRequest, db: VaccinationDB, current_user: CurrentVaccinationUser): return service.create_profile(db, current_user, payload)

@router.put('/profiles/{profile_id}', response_model=ProfileResponse, operation_id='updateVaccinationTrackerProfile')
def update_profile(profile_id: str, payload: ProfileUpdateRequest, db: VaccinationDB, current_user: CurrentVaccinationUser): return service.update_profile(db, current_user, profile_id, payload)

@router.post('/profiles/{profile_id}/archive', response_model=ProfileResponse, operation_id='archiveVaccinationTrackerProfile')
def archive_profile(profile_id: str, db: VaccinationDB, current_user: CurrentVaccinationUser): return service.set_profile_archived(db, current_user, profile_id, True)

@router.post('/profiles/{profile_id}/restore', response_model=ProfileResponse, operation_id='restoreVaccinationTrackerProfile')
def restore_profile(profile_id: str, db: VaccinationDB, current_user: CurrentVaccinationUser): return service.set_profile_archived(db, current_user, profile_id, False)

@router.delete('/profiles/{profile_id}', status_code=status.HTTP_204_NO_CONTENT, operation_id='deleteVaccinationTrackerProfile')
def delete_profile(profile_id: str, db: VaccinationDB, current_user: CurrentVaccinationUser): service.delete_profile(db, current_user, profile_id); return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.get('/vaccines', response_model=list[VaccineTypeResponse], operation_id='listVaccinationTrackerVaccineTypes')
def list_vaccine_types(db: VaccinationDB, current_user: CurrentVaccinationUser): return service.list_vaccine_types(db, current_user)

@router.post('/vaccines', response_model=VaccineTypeResponse, status_code=status.HTTP_201_CREATED, operation_id='createVaccinationTrackerVaccineType')
def create_vaccine_type(payload: VaccineTypeCreateRequest, db: VaccinationDB, current_user: CurrentVaccinationUser): return service.create_vaccine_type(db, current_user, payload)

@router.put('/vaccines/{vaccine_type_id}', response_model=VaccineTypeResponse, operation_id='updateVaccinationTrackerVaccineType')
def update_vaccine_type(vaccine_type_id: str, payload: VaccineTypeUpdateRequest, db: VaccinationDB, current_user: CurrentVaccinationUser): return service.update_vaccine_type(db, current_user, vaccine_type_id, payload)

@router.delete('/vaccines/{vaccine_type_id}', status_code=status.HTTP_204_NO_CONTENT, operation_id='deleteVaccinationTrackerVaccineType')
def delete_vaccine_type(vaccine_type_id: str, db: VaccinationDB, current_user: CurrentVaccinationUser): service.delete_vaccine_type(db, current_user, vaccine_type_id); return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.get('/records', response_model=RecordListResponse, operation_id='listVaccinationTrackerRecords')
def list_records(db: VaccinationDB, current_user: CurrentVaccinationUser, q: str | None = Query(default=None), archive_filter: ArchiveFilter = Query(default='active', alias='archiveFilter'), profile_id: str | None = Query(default=None, alias='profileId'), vaccine_type_id: str | None = Query(default=None, alias='vaccineTypeId'), status_filter: str | None = Query(default=None, alias='statusFilter'), due_filter: DueFilter = Query(default='all', alias='dueFilter'), date_from: date | None = Query(default=None, alias='dateFrom'), date_to: date | None = Query(default=None, alias='dateTo'), sort_by: RecordSort = Query(default='due', alias='sortBy'), page: int = Query(default=1, ge=1), page_size: int = Query(default=25, alias='pageSize', ge=1, le=100)):
    return service.list_records(db, current_user, q, archive_filter, profile_id, vaccine_type_id, status_filter, due_filter, date_from, date_to, sort_by, page, page_size)

@router.post('/records', response_model=RecordDetailResponse, status_code=status.HTTP_201_CREATED, operation_id='createVaccinationTrackerRecord')
def create_record(payload: RecordCreateRequest, db: VaccinationDB, current_user: CurrentVaccinationUser): return service.create_record(db, current_user, payload)

@router.get('/records/{record_id}', response_model=RecordDetailResponse, operation_id='getVaccinationTrackerRecord')
def get_record(record_id: str, db: VaccinationDB, current_user: CurrentVaccinationUser): return service.get_record(db, current_user, record_id)

@router.put('/records/{record_id}', response_model=RecordDetailResponse, operation_id='updateVaccinationTrackerRecord')
def update_record(record_id: str, payload: RecordUpdateRequest, db: VaccinationDB, current_user: CurrentVaccinationUser): return service.update_record(db, current_user, record_id, payload)

@router.post('/records/{record_id}/archive', response_model=RecordDetailResponse, operation_id='archiveVaccinationTrackerRecord')
def archive_record(record_id: str, db: VaccinationDB, current_user: CurrentVaccinationUser): return service.set_record_archived(db, current_user, record_id, True)

@router.post('/records/{record_id}/restore', response_model=RecordDetailResponse, operation_id='restoreVaccinationTrackerRecord')
def restore_record(record_id: str, db: VaccinationDB, current_user: CurrentVaccinationUser): return service.set_record_archived(db, current_user, record_id, False)

@router.delete('/records/{record_id}', status_code=status.HTTP_204_NO_CONTENT, operation_id='deleteVaccinationTrackerRecord')
def delete_record(record_id: str, db: VaccinationDB, current_user: CurrentVaccinationUser): service.delete_record(db, current_user, record_id); return Response(status_code=status.HTTP_204_NO_CONTENT)
