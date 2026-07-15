from fastapi import APIRouter, Query, Response, status
from app.modules.doctor_visit_tracker import service
from app.modules.doctor_visit_tracker.dependencies import CurrentDoctorVisitUser, DoctorVisitDB
from app.modules.doctor_visit_tracker.schemas import ArchiveFilter, DashboardResponse, InsightsResponse, SpecialtyCreateRequest, SpecialtyResponse, SpecialtyUpdateRequest, TimeFilter, VisitCreateRequest, VisitDetailResponse, VisitSort, VisitSummaryResponse, VisitUpdateRequest

router = APIRouter()

@router.get('/dashboard', response_model=DashboardResponse, operation_id='getDoctorVisitTrackerDashboard')
def get_dashboard(db: DoctorVisitDB, current_user: CurrentDoctorVisitUser): return service.get_dashboard(db, current_user)

@router.get('/insights', response_model=InsightsResponse, operation_id='getDoctorVisitTrackerInsights')
def get_insights(db: DoctorVisitDB, current_user: CurrentDoctorVisitUser): return service.get_insights(db, current_user)

@router.get('/specialties', response_model=list[SpecialtyResponse], operation_id='listDoctorVisitTrackerSpecialties')
def list_specialties(db: DoctorVisitDB, current_user: CurrentDoctorVisitUser): return service.list_specialties(db, current_user)

@router.post('/specialties', response_model=SpecialtyResponse, status_code=status.HTTP_201_CREATED, operation_id='createDoctorVisitTrackerSpecialty')
def create_specialty(payload: SpecialtyCreateRequest, db: DoctorVisitDB, current_user: CurrentDoctorVisitUser): return service.create_specialty(db, current_user, payload)

@router.put('/specialties/{specialty_id}', response_model=SpecialtyResponse, operation_id='updateDoctorVisitTrackerSpecialty')
def update_specialty(specialty_id: str, payload: SpecialtyUpdateRequest, db: DoctorVisitDB, current_user: CurrentDoctorVisitUser): return service.update_specialty(db, current_user, specialty_id, payload)

@router.delete('/specialties/{specialty_id}', status_code=status.HTTP_204_NO_CONTENT, operation_id='deleteDoctorVisitTrackerSpecialty')
def delete_specialty(specialty_id: str, db: DoctorVisitDB, current_user: CurrentDoctorVisitUser): service.delete_specialty(db, current_user, specialty_id); return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.get('/visits', response_model=list[VisitSummaryResponse], operation_id='listDoctorVisitTrackerVisits')
def list_visits(db: DoctorVisitDB, current_user: CurrentDoctorVisitUser, q: str | None = Query(default=None), archive_filter: ArchiveFilter = Query(default='active', alias='archiveFilter'), specialty_id: str | None = Query(default=None, alias='specialtyId'), status_filter: str | None = Query(default=None, alias='statusFilter'), time_filter: TimeFilter = Query(default='all', alias='timeFilter'), sort_by: VisitSort = Query(default='date', alias='sortBy')):
    return service.list_visits(db, current_user, q, archive_filter, specialty_id, status_filter, time_filter, sort_by)

@router.post('/visits', response_model=VisitDetailResponse, status_code=status.HTTP_201_CREATED, operation_id='createDoctorVisitTrackerVisit')
def create_visit(payload: VisitCreateRequest, db: DoctorVisitDB, current_user: CurrentDoctorVisitUser): return service.create_visit(db, current_user, payload)

@router.get('/visits/{visit_id}', response_model=VisitDetailResponse, operation_id='getDoctorVisitTrackerVisit')
def get_visit(visit_id: str, db: DoctorVisitDB, current_user: CurrentDoctorVisitUser): return service.get_visit(db, current_user, visit_id)

@router.put('/visits/{visit_id}', response_model=VisitDetailResponse, operation_id='updateDoctorVisitTrackerVisit')
def update_visit(visit_id: str, payload: VisitUpdateRequest, db: DoctorVisitDB, current_user: CurrentDoctorVisitUser): return service.update_visit(db, current_user, visit_id, payload)

@router.post('/visits/{visit_id}/archive', response_model=VisitDetailResponse, operation_id='archiveDoctorVisitTrackerVisit')
def archive_visit(visit_id: str, db: DoctorVisitDB, current_user: CurrentDoctorVisitUser): return service.set_visit_archived(db, current_user, visit_id, True)

@router.post('/visits/{visit_id}/restore', response_model=VisitDetailResponse, operation_id='restoreDoctorVisitTrackerVisit')
def restore_visit(visit_id: str, db: DoctorVisitDB, current_user: CurrentDoctorVisitUser): return service.set_visit_archived(db, current_user, visit_id, False)

@router.delete('/visits/{visit_id}', status_code=status.HTTP_204_NO_CONTENT, operation_id='deleteDoctorVisitTrackerVisit')
def delete_visit(visit_id: str, db: DoctorVisitDB, current_user: CurrentDoctorVisitUser): service.delete_visit(db, current_user, visit_id); return Response(status_code=status.HTTP_204_NO_CONTENT)
