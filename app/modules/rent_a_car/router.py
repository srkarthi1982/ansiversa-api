from fastapi import APIRouter, Response, status

from app.modules.rent_a_car import service
from app.modules.rent_a_car.dependencies import CurrentRentACarUser, RentACarDB
from app.modules.rent_a_car.schemas import (
    RentACarBookingCreateRequest,
    RentACarBookingDetailResponse,
    RentACarBookingSummaryResponse,
    RentACarBookingUpdateRequest,
    RentACarDashboardResponse,
    RentACarSearchCreateRequest,
    RentACarSearchDetailResponse,
    RentACarSearchDuplicateRequest,
    RentACarSearchSummaryResponse,
    RentACarSearchUpdateRequest,
    RentACarVehicleOptionCreateRequest,
    RentACarVehicleOptionDetailResponse,
    RentACarVehicleOptionDuplicateRequest,
    RentACarVehicleOptionSummaryResponse,
    RentACarVehicleOptionUpdateRequest,
)

router = APIRouter()


@router.get("/dashboard", response_model=RentACarDashboardResponse, operation_id="getRentACarDashboard")
def get_dashboard(db: RentACarDB, current_user: CurrentRentACarUser):
    return service.get_dashboard(db, current_user)


@router.get("/searches", response_model=list[RentACarSearchSummaryResponse], operation_id="listRentACarSearches")
def list_searches(db: RentACarDB, current_user: CurrentRentACarUser):
    return service.list_searches(db, current_user)


@router.post("/searches", response_model=RentACarSearchDetailResponse, status_code=status.HTTP_201_CREATED, operation_id="createRentACarSearch")
def create_search(payload: RentACarSearchCreateRequest, db: RentACarDB, current_user: CurrentRentACarUser):
    return service.create_search(db, current_user, payload)


@router.get("/searches/{search_id}", response_model=RentACarSearchDetailResponse, operation_id="getRentACarSearch")
def get_search(search_id: str, db: RentACarDB, current_user: CurrentRentACarUser):
    return service.get_search(db, current_user, search_id)


@router.put("/searches/{search_id}", response_model=RentACarSearchDetailResponse, operation_id="updateRentACarSearch")
def update_search(search_id: str, payload: RentACarSearchUpdateRequest, db: RentACarDB, current_user: CurrentRentACarUser):
    return service.update_search(db, current_user, search_id, payload)


@router.post("/searches/{search_id}/duplicate", response_model=RentACarSearchDetailResponse, status_code=status.HTTP_201_CREATED, operation_id="duplicateRentACarSearch")
def duplicate_search(search_id: str, payload: RentACarSearchDuplicateRequest, db: RentACarDB, current_user: CurrentRentACarUser):
    return service.duplicate_search(db, current_user, search_id, payload)


@router.delete("/searches/{search_id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="deleteRentACarSearch")
def delete_search(search_id: str, db: RentACarDB, current_user: CurrentRentACarUser):
    service.delete_search(db, current_user, search_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/vehicle-options", response_model=list[RentACarVehicleOptionSummaryResponse], operation_id="listRentACarVehicleOptions")
def list_vehicle_options(db: RentACarDB, current_user: CurrentRentACarUser):
    return service.list_vehicle_options(db, current_user)


@router.post("/vehicle-options", response_model=RentACarVehicleOptionDetailResponse, status_code=status.HTTP_201_CREATED, operation_id="createRentACarVehicleOption")
def create_vehicle_option(payload: RentACarVehicleOptionCreateRequest, db: RentACarDB, current_user: CurrentRentACarUser):
    return service.create_vehicle_option(db, current_user, payload)


@router.get("/vehicle-options/{option_id}", response_model=RentACarVehicleOptionDetailResponse, operation_id="getRentACarVehicleOption")
def get_vehicle_option(option_id: str, db: RentACarDB, current_user: CurrentRentACarUser):
    return service.get_vehicle_option(db, current_user, option_id)


@router.put("/vehicle-options/{option_id}", response_model=RentACarVehicleOptionDetailResponse, operation_id="updateRentACarVehicleOption")
def update_vehicle_option(option_id: str, payload: RentACarVehicleOptionUpdateRequest, db: RentACarDB, current_user: CurrentRentACarUser):
    return service.update_vehicle_option(db, current_user, option_id, payload)


@router.post("/vehicle-options/{option_id}/duplicate", response_model=RentACarVehicleOptionDetailResponse, status_code=status.HTTP_201_CREATED, operation_id="duplicateRentACarVehicleOption")
def duplicate_vehicle_option(option_id: str, payload: RentACarVehicleOptionDuplicateRequest, db: RentACarDB, current_user: CurrentRentACarUser):
    return service.duplicate_vehicle_option(db, current_user, option_id, payload)


@router.post("/vehicle-options/{option_id}/preferred", response_model=RentACarVehicleOptionDetailResponse, operation_id="markRentACarVehicleOptionPreferred")
def mark_vehicle_option_preferred(option_id: str, db: RentACarDB, current_user: CurrentRentACarUser):
    return service.mark_vehicle_option_preferred(db, current_user, option_id)


@router.post("/vehicle-options/{option_id}/unpreferred", response_model=RentACarVehicleOptionDetailResponse, operation_id="unmarkRentACarVehicleOptionPreferred")
def unmark_vehicle_option_preferred(option_id: str, db: RentACarDB, current_user: CurrentRentACarUser):
    return service.unmark_vehicle_option_preferred(db, current_user, option_id)


@router.delete("/vehicle-options/{option_id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="deleteRentACarVehicleOption")
def delete_vehicle_option(option_id: str, db: RentACarDB, current_user: CurrentRentACarUser):
    service.delete_vehicle_option(db, current_user, option_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/bookings", response_model=list[RentACarBookingSummaryResponse], operation_id="listRentACarBookings")
def list_bookings(db: RentACarDB, current_user: CurrentRentACarUser):
    return service.list_bookings(db, current_user)


@router.post("/bookings", response_model=RentACarBookingDetailResponse, status_code=status.HTTP_201_CREATED, operation_id="createRentACarBooking")
def create_booking(payload: RentACarBookingCreateRequest, db: RentACarDB, current_user: CurrentRentACarUser):
    return service.create_booking(db, current_user, payload)


@router.get("/bookings/{booking_id}", response_model=RentACarBookingDetailResponse, operation_id="getRentACarBooking")
def get_booking(booking_id: str, db: RentACarDB, current_user: CurrentRentACarUser):
    return service.get_booking(db, current_user, booking_id)


@router.put("/bookings/{booking_id}", response_model=RentACarBookingDetailResponse, operation_id="updateRentACarBooking")
def update_booking(booking_id: str, payload: RentACarBookingUpdateRequest, db: RentACarDB, current_user: CurrentRentACarUser):
    return service.update_booking(db, current_user, booking_id, payload)


@router.delete("/bookings/{booking_id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="deleteRentACarBooking")
def delete_booking(booking_id: str, db: RentACarDB, current_user: CurrentRentACarUser):
    service.delete_booking(db, current_user, booking_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
