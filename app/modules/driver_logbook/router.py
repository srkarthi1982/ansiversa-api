from datetime import date
from fastapi import APIRouter, Query, Response, status
from app.modules.driver_logbook import service
from app.modules.driver_logbook.dependencies import CurrentDriverLogbookUser, DriverLogbookDB
from app.modules.driver_logbook.schemas import ArchiveFilter, DashboardResponse, InsightsResponse, TripCreateRequest, TripListResponse, TripPurpose, TripResponse, TripSort, TripUpdateRequest, VehicleCreateRequest, VehicleResponse, VehicleUpdateRequest

router = APIRouter()


@router.get("/dashboard", response_model=DashboardResponse, operation_id="getDriverLogbookDashboard")
def get_dashboard(db: DriverLogbookDB, current_user: CurrentDriverLogbookUser):
    return service.get_dashboard(db, current_user)


@router.get("/insights", response_model=InsightsResponse, operation_id="getDriverLogbookInsights")
def get_insights(db: DriverLogbookDB, current_user: CurrentDriverLogbookUser):
    return service.get_insights(db, current_user)


@router.get("/vehicles", response_model=list[VehicleResponse], operation_id="listDriverLogbookVehicles")
def list_vehicles(db: DriverLogbookDB, current_user: CurrentDriverLogbookUser, archive_filter: ArchiveFilter = Query(default="active", alias="archiveFilter")):
    return service.list_vehicles(db, current_user, archive_filter)


@router.post("/vehicles", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED, operation_id="createDriverLogbookVehicle")
def create_vehicle(payload: VehicleCreateRequest, db: DriverLogbookDB, current_user: CurrentDriverLogbookUser):
    return service.create_vehicle(db, current_user, payload)


@router.put("/vehicles/{vehicle_id}", response_model=VehicleResponse, operation_id="updateDriverLogbookVehicle")
def update_vehicle(vehicle_id: str, payload: VehicleUpdateRequest, db: DriverLogbookDB, current_user: CurrentDriverLogbookUser):
    return service.update_vehicle(db, current_user, vehicle_id, payload)


@router.post("/vehicles/{vehicle_id}/archive", response_model=VehicleResponse, operation_id="archiveDriverLogbookVehicle")
def archive_vehicle(vehicle_id: str, db: DriverLogbookDB, current_user: CurrentDriverLogbookUser):
    return service.set_vehicle_archived(db, current_user, vehicle_id, True)


@router.post("/vehicles/{vehicle_id}/restore", response_model=VehicleResponse, operation_id="restoreDriverLogbookVehicle")
def restore_vehicle(vehicle_id: str, db: DriverLogbookDB, current_user: CurrentDriverLogbookUser):
    return service.set_vehicle_archived(db, current_user, vehicle_id, False)


@router.delete("/vehicles/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="deleteDriverLogbookVehicle")
def delete_vehicle(vehicle_id: str, db: DriverLogbookDB, current_user: CurrentDriverLogbookUser):
    service.delete_vehicle(db, current_user, vehicle_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/trips", response_model=TripListResponse, operation_id="listDriverLogbookTrips")
def list_trips(db: DriverLogbookDB, current_user: CurrentDriverLogbookUser, q: str | None = Query(default=None), vehicle_id: str | None = Query(default=None, alias="vehicleId"), date_from: date | None = Query(default=None, alias="dateFrom"), date_to: date | None = Query(default=None, alias="dateTo"), purpose: TripPurpose | None = None, archive_filter: ArchiveFilter = Query(default="active", alias="archiveFilter"), sort_by: TripSort = Query(default="date", alias="sortBy"), page: int = Query(default=1, ge=1), page_size: int = Query(default=25, alias="pageSize", ge=1, le=100)):
    return service.list_trips(db, current_user, q, vehicle_id, date_from, date_to, purpose, archive_filter, sort_by, page, page_size)


@router.post("/trips", response_model=TripResponse, status_code=status.HTTP_201_CREATED, operation_id="createDriverLogbookTrip")
def create_trip(payload: TripCreateRequest, db: DriverLogbookDB, current_user: CurrentDriverLogbookUser):
    return service.create_trip(db, current_user, payload)


@router.get("/trips/{trip_id}", response_model=TripResponse, operation_id="getDriverLogbookTrip")
def get_trip(trip_id: str, db: DriverLogbookDB, current_user: CurrentDriverLogbookUser):
    return service.get_trip(db, current_user, trip_id)


@router.put("/trips/{trip_id}", response_model=TripResponse, operation_id="updateDriverLogbookTrip")
def update_trip(trip_id: str, payload: TripUpdateRequest, db: DriverLogbookDB, current_user: CurrentDriverLogbookUser):
    return service.update_trip(db, current_user, trip_id, payload)


@router.post("/trips/{trip_id}/archive", response_model=TripResponse, operation_id="archiveDriverLogbookTrip")
def archive_trip(trip_id: str, db: DriverLogbookDB, current_user: CurrentDriverLogbookUser):
    return service.set_trip_archived(db, current_user, trip_id, True)


@router.post("/trips/{trip_id}/restore", response_model=TripResponse, operation_id="restoreDriverLogbookTrip")
def restore_trip(trip_id: str, db: DriverLogbookDB, current_user: CurrentDriverLogbookUser):
    return service.set_trip_archived(db, current_user, trip_id, False)


@router.delete("/trips/{trip_id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="deleteDriverLogbookTrip")
def delete_trip(trip_id: str, db: DriverLogbookDB, current_user: CurrentDriverLogbookUser):
    service.delete_trip(db, current_user, trip_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
