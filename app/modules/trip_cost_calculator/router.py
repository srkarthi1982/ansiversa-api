from fastapi import APIRouter, Response, status

from app.modules.trip_cost_calculator import service
from app.modules.trip_cost_calculator.dependencies import CurrentTripCostUser, TripCostDB
from app.modules.trip_cost_calculator.schemas import (
    TripCostDashboardResponse,
    TripCostExpenseCreateRequest,
    TripCostExpenseDetailResponse,
    TripCostExpenseSummaryResponse,
    TripCostExpenseUpdateRequest,
    TripCostTripCreateRequest,
    TripCostTripDetailResponse,
    TripCostTripSummaryResponse,
    TripCostTripUpdateRequest,
)

router = APIRouter()


@router.get("/dashboard", response_model=TripCostDashboardResponse, operation_id="getTripCostDashboard")
def get_dashboard(db: TripCostDB, current_user: CurrentTripCostUser):
    return service.get_dashboard(db, current_user)


@router.get("/trips", response_model=list[TripCostTripSummaryResponse], operation_id="listTripCostTrips")
def list_trips(db: TripCostDB, current_user: CurrentTripCostUser):
    return service.list_trips(db, current_user)


@router.post("/trips", response_model=TripCostTripDetailResponse, status_code=status.HTTP_201_CREATED, operation_id="createTripCostTrip")
def create_trip(payload: TripCostTripCreateRequest, db: TripCostDB, current_user: CurrentTripCostUser):
    return service.create_trip(db, current_user, payload)


@router.get("/trips/{trip_id}", response_model=TripCostTripDetailResponse, operation_id="getTripCostTrip")
def get_trip(trip_id: str, db: TripCostDB, current_user: CurrentTripCostUser):
    return service.get_trip(db, current_user, trip_id)


@router.put("/trips/{trip_id}", response_model=TripCostTripDetailResponse, operation_id="updateTripCostTrip")
def update_trip(trip_id: str, payload: TripCostTripUpdateRequest, db: TripCostDB, current_user: CurrentTripCostUser):
    return service.update_trip(db, current_user, trip_id, payload)


@router.post("/trips/{trip_id}/duplicate", response_model=TripCostTripDetailResponse, status_code=status.HTTP_201_CREATED, operation_id="duplicateTripCostTrip")
def duplicate_trip(trip_id: str, db: TripCostDB, current_user: CurrentTripCostUser):
    return service.duplicate_trip(db, current_user, trip_id)


@router.delete("/trips/{trip_id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="deleteTripCostTrip")
def delete_trip(trip_id: str, db: TripCostDB, current_user: CurrentTripCostUser):
    service.delete_trip(db, current_user, trip_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/expenses", response_model=list[TripCostExpenseSummaryResponse], operation_id="listTripCostExpenses")
def list_expenses(db: TripCostDB, current_user: CurrentTripCostUser):
    return service.list_expenses(db, current_user)


@router.post("/expenses", response_model=TripCostExpenseDetailResponse, status_code=status.HTTP_201_CREATED, operation_id="createTripCostExpense")
def create_expense(payload: TripCostExpenseCreateRequest, db: TripCostDB, current_user: CurrentTripCostUser):
    return service.create_expense(db, current_user, payload)


@router.get("/expenses/{expense_id}", response_model=TripCostExpenseDetailResponse, operation_id="getTripCostExpense")
def get_expense(expense_id: str, db: TripCostDB, current_user: CurrentTripCostUser):
    return service.get_expense(db, current_user, expense_id)


@router.put("/expenses/{expense_id}", response_model=TripCostExpenseDetailResponse, operation_id="updateTripCostExpense")
def update_expense(expense_id: str, payload: TripCostExpenseUpdateRequest, db: TripCostDB, current_user: CurrentTripCostUser):
    return service.update_expense(db, current_user, expense_id, payload)


@router.delete("/expenses/{expense_id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="deleteTripCostExpense")
def delete_expense(expense_id: str, db: TripCostDB, current_user: CurrentTripCostUser):
    service.delete_expense(db, current_user, expense_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
