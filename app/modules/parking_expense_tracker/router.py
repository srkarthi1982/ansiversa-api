from fastapi import APIRouter, Response, status

from app.modules.parking_expense_tracker import service
from app.modules.parking_expense_tracker.dependencies import CurrentParkingExpenseUser, ParkingExpenseDB
from app.modules.parking_expense_tracker.schemas import (
    ParkingExpenseDashboardResponse,
    ParkingExpenseEntryCreateRequest,
    ParkingExpenseEntryDetailResponse,
    ParkingExpenseEntrySummaryResponse,
    ParkingExpenseEntryUpdateRequest,
    ParkingExpenseLocationCreateRequest,
    ParkingExpenseLocationDetailResponse,
    ParkingExpenseLocationSummaryResponse,
    ParkingExpenseLocationUpdateRequest,
)

router = APIRouter()


@router.get("/dashboard", response_model=ParkingExpenseDashboardResponse, operation_id="getParkingExpenseDashboard")
def get_dashboard(db: ParkingExpenseDB, current_user: CurrentParkingExpenseUser):
    return service.get_dashboard(db, current_user)


@router.get("/locations", response_model=list[ParkingExpenseLocationSummaryResponse], operation_id="listParkingExpenseLocations")
def list_locations(db: ParkingExpenseDB, current_user: CurrentParkingExpenseUser):
    return service.list_locations(db, current_user)


@router.post("/locations", response_model=ParkingExpenseLocationDetailResponse, status_code=status.HTTP_201_CREATED, operation_id="createParkingExpenseLocation")
def create_location(payload: ParkingExpenseLocationCreateRequest, db: ParkingExpenseDB, current_user: CurrentParkingExpenseUser):
    return service.create_location(db, current_user, payload)


@router.get("/locations/{location_id}", response_model=ParkingExpenseLocationDetailResponse, operation_id="getParkingExpenseLocation")
def get_location(location_id: str, db: ParkingExpenseDB, current_user: CurrentParkingExpenseUser):
    return service.get_location(db, current_user, location_id)


@router.put("/locations/{location_id}", response_model=ParkingExpenseLocationDetailResponse, operation_id="updateParkingExpenseLocation")
def update_location(location_id: str, payload: ParkingExpenseLocationUpdateRequest, db: ParkingExpenseDB, current_user: CurrentParkingExpenseUser):
    return service.update_location(db, current_user, location_id, payload)


@router.delete("/locations/{location_id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="deleteParkingExpenseLocation")
def delete_location(location_id: str, db: ParkingExpenseDB, current_user: CurrentParkingExpenseUser):
    service.delete_location(db, current_user, location_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/expenses", response_model=list[ParkingExpenseEntrySummaryResponse], operation_id="listParkingExpenseEntries")
def list_expenses(db: ParkingExpenseDB, current_user: CurrentParkingExpenseUser):
    return service.list_expenses(db, current_user)


@router.post("/expenses", response_model=ParkingExpenseEntryDetailResponse, status_code=status.HTTP_201_CREATED, operation_id="createParkingExpenseEntry")
def create_expense(payload: ParkingExpenseEntryCreateRequest, db: ParkingExpenseDB, current_user: CurrentParkingExpenseUser):
    return service.create_expense(db, current_user, payload)


@router.get("/expenses/{expense_id}", response_model=ParkingExpenseEntryDetailResponse, operation_id="getParkingExpenseEntry")
def get_expense(expense_id: str, db: ParkingExpenseDB, current_user: CurrentParkingExpenseUser):
    return service.get_expense(db, current_user, expense_id)


@router.put("/expenses/{expense_id}", response_model=ParkingExpenseEntryDetailResponse, operation_id="updateParkingExpenseEntry")
def update_expense(expense_id: str, payload: ParkingExpenseEntryUpdateRequest, db: ParkingExpenseDB, current_user: CurrentParkingExpenseUser):
    return service.update_expense(db, current_user, expense_id, payload)


@router.delete("/expenses/{expense_id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="deleteParkingExpenseEntry")
def delete_expense(expense_id: str, db: ParkingExpenseDB, current_user: CurrentParkingExpenseUser):
    service.delete_expense(db, current_user, expense_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
