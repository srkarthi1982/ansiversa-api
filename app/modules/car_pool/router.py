from fastapi import APIRouter, Response, status

from app.modules.car_pool import service
from app.modules.car_pool.dependencies import CarPoolDB, CurrentCarPoolUser
from app.modules.car_pool.schemas import (
    CarPoolDashboardResponse,
    CarPoolPassengerDetailResponse,
    CarPoolPassengerJoinRequest,
    CarPoolPassengerSummaryResponse,
    CarPoolPassengerUpdateRequest,
    CarPoolRequestCreateRequest,
    CarPoolRequestDecisionRequest,
    CarPoolRequestDetailResponse,
    CarPoolRequestSummaryResponse,
    CarPoolRequestUpdateRequest,
    CarPoolRideCreateRequest,
    CarPoolRideDetailResponse,
    CarPoolRideDuplicateRequest,
    CarPoolRideSummaryResponse,
    CarPoolRideUpdateRequest,
)

router = APIRouter()


@router.get("/dashboard", response_model=CarPoolDashboardResponse, operation_id="getCarPoolDashboard")
def get_dashboard(db: CarPoolDB, current_user: CurrentCarPoolUser):
    return service.get_dashboard(db, current_user)


@router.get("/rides", response_model=list[CarPoolRideSummaryResponse], operation_id="listCarPoolRides")
def list_rides(db: CarPoolDB, current_user: CurrentCarPoolUser):
    return service.list_rides(db, current_user)


@router.post("/rides", response_model=CarPoolRideDetailResponse, status_code=status.HTTP_201_CREATED, operation_id="createCarPoolRide")
def create_ride(payload: CarPoolRideCreateRequest, db: CarPoolDB, current_user: CurrentCarPoolUser):
    return service.create_ride(db, current_user, payload)


@router.get("/rides/{ride_id}", response_model=CarPoolRideDetailResponse, operation_id="getCarPoolRide")
def get_ride(ride_id: str, db: CarPoolDB, current_user: CurrentCarPoolUser):
    return service.get_ride(db, current_user, ride_id)


@router.put("/rides/{ride_id}", response_model=CarPoolRideDetailResponse, operation_id="updateCarPoolRide")
def update_ride(ride_id: str, payload: CarPoolRideUpdateRequest, db: CarPoolDB, current_user: CurrentCarPoolUser):
    return service.update_ride(db, current_user, ride_id, payload)


@router.post("/rides/{ride_id}/duplicate", response_model=CarPoolRideDetailResponse, status_code=status.HTTP_201_CREATED, operation_id="duplicateCarPoolRide")
def duplicate_ride(ride_id: str, payload: CarPoolRideDuplicateRequest, db: CarPoolDB, current_user: CurrentCarPoolUser):
    return service.duplicate_ride(db, current_user, ride_id, payload)


@router.delete("/rides/{ride_id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="deleteCarPoolRide")
def delete_ride(ride_id: str, db: CarPoolDB, current_user: CurrentCarPoolUser):
    service.delete_ride(db, current_user, ride_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/passengers", response_model=list[CarPoolPassengerSummaryResponse], operation_id="listCarPoolPassengers")
def list_passengers(db: CarPoolDB, current_user: CurrentCarPoolUser):
    return service.list_passengers(db, current_user)


@router.post("/passengers", response_model=CarPoolPassengerDetailResponse, status_code=status.HTTP_201_CREATED, operation_id="joinCarPoolRide")
def join_ride(payload: CarPoolPassengerJoinRequest, db: CarPoolDB, current_user: CurrentCarPoolUser):
    return service.join_ride(db, current_user, payload)


@router.get("/passengers/{passenger_id}", response_model=CarPoolPassengerDetailResponse, operation_id="getCarPoolPassenger")
def get_passenger(passenger_id: str, db: CarPoolDB, current_user: CurrentCarPoolUser):
    return service.get_passenger(db, current_user, passenger_id)


@router.put("/passengers/{passenger_id}", response_model=CarPoolPassengerDetailResponse, operation_id="updateCarPoolPassenger")
def update_passenger(passenger_id: str, payload: CarPoolPassengerUpdateRequest, db: CarPoolDB, current_user: CurrentCarPoolUser):
    return service.update_passenger(db, current_user, passenger_id, payload)


@router.post("/passengers/{passenger_id}/leave", response_model=CarPoolPassengerDetailResponse, operation_id="leaveCarPoolTrip")
def leave_trip(passenger_id: str, db: CarPoolDB, current_user: CurrentCarPoolUser):
    return service.leave_trip(db, current_user, passenger_id)


@router.delete("/passengers/{passenger_id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="deleteCarPoolPassenger")
def delete_passenger(passenger_id: str, db: CarPoolDB, current_user: CurrentCarPoolUser):
    service.delete_passenger(db, current_user, passenger_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/requests", response_model=list[CarPoolRequestSummaryResponse], operation_id="listCarPoolRequests")
def list_requests(db: CarPoolDB, current_user: CurrentCarPoolUser):
    return service.list_requests(db, current_user)


@router.post("/requests", response_model=CarPoolRequestDetailResponse, status_code=status.HTTP_201_CREATED, operation_id="createCarPoolRequest")
def create_request(payload: CarPoolRequestCreateRequest, db: CarPoolDB, current_user: CurrentCarPoolUser):
    return service.create_request(db, current_user, payload)


@router.get("/requests/{request_id}", response_model=CarPoolRequestDetailResponse, operation_id="getCarPoolRequest")
def get_request(request_id: str, db: CarPoolDB, current_user: CurrentCarPoolUser):
    return service.get_request(db, current_user, request_id)


@router.put("/requests/{request_id}", response_model=CarPoolRequestDetailResponse, operation_id="updateCarPoolRequest")
def update_request(request_id: str, payload: CarPoolRequestUpdateRequest, db: CarPoolDB, current_user: CurrentCarPoolUser):
    return service.update_request(db, current_user, request_id, payload)


@router.post("/requests/{request_id}/approve", response_model=CarPoolRequestDetailResponse, operation_id="approveCarPoolRequest")
def approve_request(request_id: str, payload: CarPoolRequestDecisionRequest, db: CarPoolDB, current_user: CurrentCarPoolUser):
    return service.approve_request(db, current_user, request_id, payload)


@router.post("/requests/{request_id}/reject", response_model=CarPoolRequestDetailResponse, operation_id="rejectCarPoolRequest")
def reject_request(request_id: str, payload: CarPoolRequestDecisionRequest, db: CarPoolDB, current_user: CurrentCarPoolUser):
    return service.reject_request(db, current_user, request_id, payload)


@router.delete("/requests/{request_id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="deleteCarPoolRequest")
def delete_request(request_id: str, db: CarPoolDB, current_user: CurrentCarPoolUser):
    service.delete_request(db, current_user, request_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
