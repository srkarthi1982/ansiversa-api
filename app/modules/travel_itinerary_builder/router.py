from datetime import date

from fastapi import APIRouter, Query, Response

from . import service as service
from .dependencies import CurrentUser, DB
from .schemas import (
    ActivityCreate,
    ActivityUpdate,
    ItineraryCreate,
    ItineraryDayCreate,
    ItineraryDayUpdate,
    ItineraryDetail,
    ItineraryList,
    ItineraryStatus,
    ItineraryUpdate,
    TravelCategoryCreate,
    TravelCategoryList,
    TravelCategoryResponse,
    TravelCategoryUpdate,
    TravelDashboard,
)

router = APIRouter()


@router.get("/dashboard", response_model=TravelDashboard, operation_id="getTravelItineraryBuilderDashboard")
def dashboard(db: DB, current_user: CurrentUser):
    return service.dashboard(db, current_user)


@router.get("/itineraries", response_model=ItineraryList, operation_id="listTravelItineraries")
def list_itineraries(
    db: DB,
    current_user: CurrentUser,
    q: str | None = None,
    status: ItineraryStatus | None = None,
    destination: str | None = None,
    starts_from: date | None = Query(None, alias="startsFrom"),
    starts_to: date | None = Query(None, alias="startsTo"),
    page: int = Query(1, ge=1),
    page_size: int = Query(12, alias="pageSize", ge=1, le=100),
):
    return service.list_itineraries(db, current_user, q, status, destination, starts_from, starts_to, page, page_size)


@router.post("/itineraries", response_model=ItineraryDetail, status_code=201, operation_id="createTravelItinerary")
def create_itinerary(payload: ItineraryCreate, db: DB, current_user: CurrentUser):
    return service.save_itinerary(db, current_user, payload)


@router.get("/itineraries/{itinerary_id}", response_model=ItineraryDetail, operation_id="getTravelItinerary")
def get_itinerary(itinerary_id: str, db: DB, current_user: CurrentUser):
    return service.get_itinerary(db, current_user, itinerary_id)


@router.put("/itineraries/{itinerary_id}", response_model=ItineraryDetail, operation_id="updateTravelItinerary")
def update_itinerary(itinerary_id: str, payload: ItineraryUpdate, db: DB, current_user: CurrentUser):
    return service.save_itinerary(db, current_user, payload, itinerary_id)


@router.delete("/itineraries/{itinerary_id}", status_code=204, operation_id="deleteTravelItinerary")
def delete_itinerary(itinerary_id: str, db: DB, current_user: CurrentUser):
    service.delete_itinerary(db, current_user, itinerary_id)
    return Response(status_code=204)


@router.post("/itineraries/{itinerary_id}/days", response_model=ItineraryDetail, status_code=201, operation_id="createTravelItineraryDay")
def create_day(itinerary_id: str, payload: ItineraryDayCreate, db: DB, current_user: CurrentUser):
    return service.save_day(db, current_user, itinerary_id, payload)


@router.put("/itineraries/{itinerary_id}/days/{day_id}", response_model=ItineraryDetail, operation_id="updateTravelItineraryDay")
def update_day(itinerary_id: str, day_id: str, payload: ItineraryDayUpdate, db: DB, current_user: CurrentUser):
    return service.save_day(db, current_user, itinerary_id, payload, day_id)


@router.delete("/itineraries/{itinerary_id}/days/{day_id}", status_code=204, operation_id="deleteTravelItineraryDay")
def delete_day(itinerary_id: str, day_id: str, db: DB, current_user: CurrentUser):
    service.delete_day(db, current_user, itinerary_id, day_id)
    return Response(status_code=204)


@router.post("/itineraries/{itinerary_id}/days/{day_id}/activities", response_model=ItineraryDetail, status_code=201, operation_id="createTravelActivity")
def create_activity(itinerary_id: str, day_id: str, payload: ActivityCreate, db: DB, current_user: CurrentUser):
    return service.save_activity(db, current_user, itinerary_id, day_id, payload)


@router.put("/itineraries/{itinerary_id}/days/{day_id}/activities/{activity_id}", response_model=ItineraryDetail, operation_id="updateTravelActivity")
def update_activity(itinerary_id: str, day_id: str, activity_id: str, payload: ActivityUpdate, db: DB, current_user: CurrentUser):
    return service.save_activity(db, current_user, itinerary_id, day_id, payload, activity_id)


@router.delete("/itineraries/{itinerary_id}/days/{day_id}/activities/{activity_id}", response_model=ItineraryDetail, operation_id="deleteTravelActivity")
def delete_activity(itinerary_id: str, day_id: str, activity_id: str, db: DB, current_user: CurrentUser):
    return service.delete_activity(db, current_user, itinerary_id, day_id, activity_id)


@router.get("/categories", response_model=TravelCategoryList, operation_id="listTravelActivityCategories")
def list_categories(
    db: DB,
    current_user: CurrentUser,
    q: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, alias="pageSize", ge=1, le=100),
):
    return service.list_categories(db, current_user, q, page, page_size)


@router.post("/categories", response_model=TravelCategoryResponse, status_code=201, operation_id="createTravelActivityCategory")
def create_category(payload: TravelCategoryCreate, db: DB, current_user: CurrentUser):
    return service.save_category(db, current_user, payload)


@router.put("/categories/{category_id}", response_model=TravelCategoryResponse, operation_id="updateTravelActivityCategory")
def update_category(category_id: str, payload: TravelCategoryUpdate, db: DB, current_user: CurrentUser):
    return service.save_category(db, current_user, payload, category_id)


@router.delete("/categories/{category_id}", status_code=204, operation_id="deleteTravelActivityCategory")
def delete_category(category_id: str, db: DB, current_user: CurrentUser):
    service.delete_category(db, current_user, category_id)
    return Response(status_code=204)

