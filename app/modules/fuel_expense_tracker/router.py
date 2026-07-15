from datetime import date
from fastapi import APIRouter, Query, Response, status
from app.modules.fuel_expense_tracker import service
from app.modules.fuel_expense_tracker.dependencies import CurrentFuelExpenseUser, FuelExpenseDB
from app.modules.fuel_expense_tracker.schemas import ArchiveFilter, DashboardResponse, EntryCreateRequest, EntryListResponse, EntryResponse, EntrySort, EntryUpdateRequest, InsightsResponse, VehicleCreateRequest, VehicleResponse, VehicleUpdateRequest

router = APIRouter()


@router.get("/dashboard", response_model=DashboardResponse, operation_id="getFuelExpenseTrackerDashboard")
def get_dashboard(db: FuelExpenseDB, current_user: CurrentFuelExpenseUser):
    return service.get_dashboard(db, current_user)


@router.get("/insights", response_model=InsightsResponse, operation_id="getFuelExpenseTrackerInsights")
def get_insights(db: FuelExpenseDB, current_user: CurrentFuelExpenseUser):
    return service.get_insights(db, current_user)


@router.get("/vehicles", response_model=list[VehicleResponse], operation_id="listFuelExpenseTrackerVehicles")
def list_vehicles(db: FuelExpenseDB, current_user: CurrentFuelExpenseUser, archive_filter: ArchiveFilter = Query(default="active", alias="archiveFilter")):
    return service.list_vehicles(db, current_user, archive_filter)


@router.post("/vehicles", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED, operation_id="createFuelExpenseTrackerVehicle")
def create_vehicle(payload: VehicleCreateRequest, db: FuelExpenseDB, current_user: CurrentFuelExpenseUser):
    return service.create_vehicle(db, current_user, payload)


@router.put("/vehicles/{vehicle_id}", response_model=VehicleResponse, operation_id="updateFuelExpenseTrackerVehicle")
def update_vehicle(vehicle_id: str, payload: VehicleUpdateRequest, db: FuelExpenseDB, current_user: CurrentFuelExpenseUser):
    return service.update_vehicle(db, current_user, vehicle_id, payload)


@router.post("/vehicles/{vehicle_id}/archive", response_model=VehicleResponse, operation_id="archiveFuelExpenseTrackerVehicle")
def archive_vehicle(vehicle_id: str, db: FuelExpenseDB, current_user: CurrentFuelExpenseUser):
    return service.set_vehicle_archived(db, current_user, vehicle_id, True)


@router.post("/vehicles/{vehicle_id}/restore", response_model=VehicleResponse, operation_id="restoreFuelExpenseTrackerVehicle")
def restore_vehicle(vehicle_id: str, db: FuelExpenseDB, current_user: CurrentFuelExpenseUser):
    return service.set_vehicle_archived(db, current_user, vehicle_id, False)


@router.delete("/vehicles/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="deleteFuelExpenseTrackerVehicle")
def delete_vehicle(vehicle_id: str, db: FuelExpenseDB, current_user: CurrentFuelExpenseUser):
    service.delete_vehicle(db, current_user, vehicle_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/entries", response_model=EntryListResponse, operation_id="listFuelExpenseTrackerEntries")
def list_entries(db: FuelExpenseDB, current_user: CurrentFuelExpenseUser, q: str | None = Query(default=None), vehicle_id: str | None = Query(default=None, alias="vehicleId"), date_from: date | None = Query(default=None, alias="dateFrom"), date_to: date | None = Query(default=None, alias="dateTo"), station: str | None = None, sort_by: EntrySort = Query(default="date", alias="sortBy"), page: int = Query(default=1, ge=1), page_size: int = Query(default=25, alias="pageSize", ge=1, le=100)):
    return service.list_entries(db, current_user, q, vehicle_id, date_from, date_to, station, sort_by, page, page_size)


@router.post("/entries", response_model=EntryResponse, status_code=status.HTTP_201_CREATED, operation_id="createFuelExpenseTrackerEntry")
def create_entry(payload: EntryCreateRequest, db: FuelExpenseDB, current_user: CurrentFuelExpenseUser):
    return service.create_entry(db, current_user, payload)


@router.get("/entries/{entry_id}", response_model=EntryResponse, operation_id="getFuelExpenseTrackerEntry")
def get_entry(entry_id: str, db: FuelExpenseDB, current_user: CurrentFuelExpenseUser):
    return service.get_entry(db, current_user, entry_id)


@router.put("/entries/{entry_id}", response_model=EntryResponse, operation_id="updateFuelExpenseTrackerEntry")
def update_entry(entry_id: str, payload: EntryUpdateRequest, db: FuelExpenseDB, current_user: CurrentFuelExpenseUser):
    return service.update_entry(db, current_user, entry_id, payload)


@router.delete("/entries/{entry_id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="deleteFuelExpenseTrackerEntry")
def delete_entry(entry_id: str, db: FuelExpenseDB, current_user: CurrentFuelExpenseUser):
    service.delete_entry(db, current_user, entry_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
