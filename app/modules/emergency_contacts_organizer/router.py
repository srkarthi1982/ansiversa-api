from fastapi import APIRouter, Query, Response, status

from app.modules.emergency_contacts_organizer import service
from app.modules.emergency_contacts_organizer.dependencies import CurrentEmergencyContactsOrganizerUser, EmergencyContactsOrganizerDB
from app.modules.emergency_contacts_organizer.schemas import (
    ContactSort,
    EmergencyContactCategoryCreateRequest,
    EmergencyContactCategoryResponse,
    EmergencyContactCategoryUpdateRequest,
    EmergencyContactCreateRequest,
    EmergencyContactDashboardResponse,
    EmergencyContactDetailResponse,
    EmergencyContactInsightsResponse,
    EmergencyContactSummaryResponse,
    EmergencyContactUpdateRequest,
    FavouriteFilter,
)

router = APIRouter()


@router.get("/dashboard", response_model=EmergencyContactDashboardResponse, operation_id="getEmergencyContactsOrganizerDashboard")
def get_dashboard(db: EmergencyContactsOrganizerDB, current_user: CurrentEmergencyContactsOrganizerUser):
    return service.get_dashboard(db, current_user)


@router.get("/insights", response_model=EmergencyContactInsightsResponse, operation_id="getEmergencyContactsOrganizerInsights")
def get_insights(db: EmergencyContactsOrganizerDB, current_user: CurrentEmergencyContactsOrganizerUser):
    return service.get_insights(db, current_user)


@router.get("/categories", response_model=list[EmergencyContactCategoryResponse], operation_id="listEmergencyContactsOrganizerCategories")
def list_categories(db: EmergencyContactsOrganizerDB, current_user: CurrentEmergencyContactsOrganizerUser):
    return service.list_categories(db, current_user)


@router.post("/categories", response_model=EmergencyContactCategoryResponse, status_code=status.HTTP_201_CREATED, operation_id="createEmergencyContactsOrganizerCategory")
def create_category(payload: EmergencyContactCategoryCreateRequest, db: EmergencyContactsOrganizerDB, current_user: CurrentEmergencyContactsOrganizerUser):
    return service.create_category(db, current_user, payload)


@router.put("/categories/{category_id}", response_model=EmergencyContactCategoryResponse, operation_id="updateEmergencyContactsOrganizerCategory")
def update_category(category_id: str, payload: EmergencyContactCategoryUpdateRequest, db: EmergencyContactsOrganizerDB, current_user: CurrentEmergencyContactsOrganizerUser):
    return service.update_category(db, current_user, category_id, payload)


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="deleteEmergencyContactsOrganizerCategory")
def delete_category(category_id: str, db: EmergencyContactsOrganizerDB, current_user: CurrentEmergencyContactsOrganizerUser):
    service.delete_category(db, current_user, category_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/contacts", response_model=list[EmergencyContactSummaryResponse], operation_id="listEmergencyContactsOrganizerContacts")
def list_contacts(
    db: EmergencyContactsOrganizerDB,
    current_user: CurrentEmergencyContactsOrganizerUser,
    q: str | None = Query(default=None),
    category_id: str | None = Query(default=None, alias="categoryId"),
    favourite_filter: FavouriteFilter = Query(default="all", alias="favouriteFilter"),
    sort_by: ContactSort = Query(default="priority", alias="sortBy"),
):
    return service.list_contacts(db, current_user, q, category_id, favourite_filter, sort_by)


@router.post("/contacts", response_model=EmergencyContactDetailResponse, status_code=status.HTTP_201_CREATED, operation_id="createEmergencyContactsOrganizerContact")
def create_contact(payload: EmergencyContactCreateRequest, db: EmergencyContactsOrganizerDB, current_user: CurrentEmergencyContactsOrganizerUser):
    return service.create_contact(db, current_user, payload)


@router.get("/contacts/{contact_id}", response_model=EmergencyContactDetailResponse, operation_id="getEmergencyContactsOrganizerContact")
def get_contact(contact_id: str, db: EmergencyContactsOrganizerDB, current_user: CurrentEmergencyContactsOrganizerUser):
    return service.get_contact(db, current_user, contact_id)


@router.put("/contacts/{contact_id}", response_model=EmergencyContactDetailResponse, operation_id="updateEmergencyContactsOrganizerContact")
def update_contact(contact_id: str, payload: EmergencyContactUpdateRequest, db: EmergencyContactsOrganizerDB, current_user: CurrentEmergencyContactsOrganizerUser):
    return service.update_contact(db, current_user, contact_id, payload)


@router.post("/contacts/{contact_id}/favourite", response_model=EmergencyContactDetailResponse, operation_id="favouriteEmergencyContactsOrganizerContact")
def favourite_contact(contact_id: str, db: EmergencyContactsOrganizerDB, current_user: CurrentEmergencyContactsOrganizerUser):
    return service.set_contact_favourite(db, current_user, contact_id, True)


@router.post("/contacts/{contact_id}/unfavourite", response_model=EmergencyContactDetailResponse, operation_id="unfavouriteEmergencyContactsOrganizerContact")
def unfavourite_contact(contact_id: str, db: EmergencyContactsOrganizerDB, current_user: CurrentEmergencyContactsOrganizerUser):
    return service.set_contact_favourite(db, current_user, contact_id, False)


@router.post("/contacts/{contact_id}/primary", response_model=EmergencyContactDetailResponse, operation_id="primaryEmergencyContactsOrganizerContact")
def mark_primary_contact(contact_id: str, db: EmergencyContactsOrganizerDB, current_user: CurrentEmergencyContactsOrganizerUser):
    return service.set_contact_primary(db, current_user, contact_id, True)


@router.post("/contacts/{contact_id}/unprimary", response_model=EmergencyContactDetailResponse, operation_id="unprimaryEmergencyContactsOrganizerContact")
def unmark_primary_contact(contact_id: str, db: EmergencyContactsOrganizerDB, current_user: CurrentEmergencyContactsOrganizerUser):
    return service.set_contact_primary(db, current_user, contact_id, False)


@router.delete("/contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="deleteEmergencyContactsOrganizerContact")
def delete_contact(contact_id: str, db: EmergencyContactsOrganizerDB, current_user: CurrentEmergencyContactsOrganizerUser):
    service.delete_contact(db, current_user, contact_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
