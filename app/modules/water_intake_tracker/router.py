from datetime import date
from fastapi import APIRouter, Query, Response, status
from app.modules.water_intake_tracker import service
from app.modules.water_intake_tracker.dependencies import CurrentWaterIntakeUser, WaterIntakeDB
from app.modules.water_intake_tracker.schemas import DashboardResponse, DaySummary, EntryCreateRequest, EntryDetailResponse, EntryListResponse, EntrySort, EntryUpdateRequest, GoalRequest, GoalResponse, InsightsResponse, SummaryRange

router = APIRouter()

@router.get('/dashboard', response_model=DashboardResponse, operation_id='getWaterIntakeTrackerDashboard')
def get_dashboard(db: WaterIntakeDB, current_user: CurrentWaterIntakeUser):
    return service.get_dashboard(db, current_user)

@router.get('/insights', response_model=InsightsResponse, operation_id='getWaterIntakeTrackerInsights')
def get_insights(db: WaterIntakeDB, current_user: CurrentWaterIntakeUser):
    return service.get_insights(db, current_user)

@router.get('/goal', response_model=GoalResponse, operation_id='getWaterIntakeTrackerGoal')
def get_goal(db: WaterIntakeDB, current_user: CurrentWaterIntakeUser):
    return service.get_goal(db, current_user)

@router.put('/goal', response_model=GoalResponse, operation_id='updateWaterIntakeTrackerGoal')
def update_goal(payload: GoalRequest, db: WaterIntakeDB, current_user: CurrentWaterIntakeUser):
    return service.update_goal(db, current_user, payload)

@router.get('/drink-types', response_model=list[str], operation_id='listWaterIntakeTrackerDrinkTypes')
def list_drink_types(db: WaterIntakeDB, current_user: CurrentWaterIntakeUser):
    return service.list_drink_types(db, current_user)

@router.get('/entries', response_model=EntryListResponse, operation_id='listWaterIntakeTrackerEntries')
def list_entries(db: WaterIntakeDB, current_user: CurrentWaterIntakeUser, q: str | None = Query(default=None), date_from: date | None = Query(default=None, alias='dateFrom'), date_to: date | None = Query(default=None, alias='dateTo'), drink_type: str | None = Query(default=None, alias='drinkType'), sort_by: EntrySort = Query(default='date', alias='sortBy'), page: int = Query(default=1, ge=1), page_size: int = Query(default=25, alias='pageSize', ge=1, le=100)):
    return service.list_entries(db, current_user, q, date_from, date_to, drink_type, sort_by, page, page_size)

@router.post('/entries', response_model=EntryDetailResponse, status_code=status.HTTP_201_CREATED, operation_id='createWaterIntakeTrackerEntry')
def create_entry(payload: EntryCreateRequest, db: WaterIntakeDB, current_user: CurrentWaterIntakeUser):
    return service.create_entry(db, current_user, payload)

@router.get('/entries/{entry_id}', response_model=EntryDetailResponse, operation_id='getWaterIntakeTrackerEntry')
def get_entry(entry_id: str, db: WaterIntakeDB, current_user: CurrentWaterIntakeUser):
    return service.get_entry(db, current_user, entry_id)

@router.put('/entries/{entry_id}', response_model=EntryDetailResponse, operation_id='updateWaterIntakeTrackerEntry')
def update_entry(entry_id: str, payload: EntryUpdateRequest, db: WaterIntakeDB, current_user: CurrentWaterIntakeUser):
    return service.update_entry(db, current_user, entry_id, payload)

@router.delete('/entries/{entry_id}', status_code=status.HTTP_204_NO_CONTENT, operation_id='deleteWaterIntakeTrackerEntry')
def delete_entry(entry_id: str, db: WaterIntakeDB, current_user: CurrentWaterIntakeUser):
    service.delete_entry(db, current_user, entry_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.get('/summary/{range_name}', response_model=list[DaySummary], operation_id='getWaterIntakeTrackerSummary')
def get_summary(range_name: SummaryRange, db: WaterIntakeDB, current_user: CurrentWaterIntakeUser):
    return service.get_summary(db, current_user, range_name)
