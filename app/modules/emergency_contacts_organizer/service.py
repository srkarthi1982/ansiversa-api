from __future__ import annotations

from collections import Counter

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.emergency_contacts_organizer import repository
from app.modules.emergency_contacts_organizer.models import EmergencyContact, EmergencyContactCategory
from app.modules.emergency_contacts_organizer.schemas import (
    ContactSort,
    EmergencyContactCategoryCreateRequest,
    EmergencyContactCategoryResponse,
    EmergencyContactCategoryUpdateRequest,
    EmergencyContactCountItem,
    EmergencyContactCreateRequest,
    EmergencyContactDashboardResponse,
    EmergencyContactDetailResponse,
    EmergencyContactInsightsResponse,
    EmergencyContactSummaryResponse,
    EmergencyContactUpdateRequest,
    FavouriteFilter,
)

DEFAULT_CATEGORIES = [
    ("Family", "Family members and close household contacts", 10),
    ("Medical", "Doctors, clinics, pharmacies, and medical support", 20),
    ("Police", "Local police or non-emergency police contact numbers", 30),
    ("Fire and rescue", "Fire, civil defense, and rescue contacts", 40),
    ("Workplace", "Employer, manager, or workplace emergency contacts", 50),
    ("School", "School, nursery, or student support contacts", 60),
    ("Roadside assistance", "Vehicle and roadside support contacts", 70),
    ("Insurance", "Insurance provider or claim assistance contacts", 80),
    ("Other", "Other important contacts", 90),
]


def _not_found(resource: str) -> None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{resource} was not found.")


def _commit_or_conflict(db: Session, message: str) -> None:
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=message) from exc


def _preview(value: str | None) -> str | None:
    if not value:
        return None
    normalized = " ".join(value.split())
    return normalized if len(normalized) <= 140 else f"{normalized[:137]}..."


def ensure_default_categories(db: Session, user: User) -> None:
    existing_names = {category.name.lower() for category in repository.list_categories(db, user.id)}
    created = False
    for name, description, sort_order in DEFAULT_CATEGORIES:
        if name.lower() in existing_names:
            continue
        repository.add(
            db,
            EmergencyContactCategory(
                owner_id=user.id,
                name=name,
                description=description,
                sort_order=sort_order,
                is_system=True,
            ),
        )
        created = True
    if created:
        _commit_or_conflict(db, "Unable to prepare default categories.")


def _get_owned_category(db: Session, user: User, category_id: str) -> EmergencyContactCategory:
    category = repository.get_category(db, category_id)
    if not category or category.owner_id != user.id:
        _not_found("Category")
    return category


def _get_owned_contact(db: Session, user: User, contact_id: str) -> EmergencyContact:
    contact = repository.get_contact(db, contact_id)
    if not contact or contact.owner_id != user.id:
        _not_found("Contact")
    return contact


def _category_response(category: EmergencyContactCategory, contact_count: int = 0) -> EmergencyContactCategoryResponse:
    return EmergencyContactCategoryResponse(
        id=category.id,
        name=category.name,
        description=category.description,
        sort_order=category.sort_order,
        is_system=category.is_system,
        contact_count=contact_count,
        created_at=category.created_at,
        updated_at=category.updated_at,
    )


def _contact_summary(contact: EmergencyContact) -> EmergencyContactSummaryResponse:
    return EmergencyContactSummaryResponse(
        id=contact.id,
        full_name=contact.full_name,
        category_id=contact.category_id,
        category_name=contact.category.name,
        relationship=contact.relationship,
        primary_phone=contact.primary_phone,
        alternate_phone=contact.alternate_phone,
        email=contact.email,
        country_or_region=contact.country_or_region,
        priority=contact.priority,
        is_favourite=contact.is_favourite,
        is_primary=contact.is_primary,
        notes_preview=_preview(contact.notes),
        created_at=contact.created_at,
        updated_at=contact.updated_at,
    )


def _contact_detail(contact: EmergencyContact) -> EmergencyContactDetailResponse:
    return EmergencyContactDetailResponse(**_contact_summary(contact).model_dump(), address=contact.address, notes=contact.notes)


def _apply_contact_payload(contact: EmergencyContact, payload: EmergencyContactCreateRequest | EmergencyContactUpdateRequest) -> None:
    contact.full_name = payload.full_name
    contact.category_id = payload.category_id
    contact.relationship = payload.relationship
    contact.primary_phone = payload.primary_phone
    contact.alternate_phone = payload.alternate_phone
    contact.email = str(payload.email) if payload.email else None
    contact.country_or_region = payload.country_or_region
    contact.address = payload.address
    contact.notes = payload.notes
    contact.priority = payload.priority
    contact.is_favourite = payload.is_favourite
    contact.is_primary = payload.is_primary


def list_categories(db: Session, user: User) -> list[EmergencyContactCategoryResponse]:
    ensure_default_categories(db, user)
    counts = repository.contact_counts_by_category(db, user.id)
    return [_category_response(category, counts.get(category.id, 0)) for category in repository.list_categories(db, user.id)]


def create_category(db: Session, user: User, payload: EmergencyContactCategoryCreateRequest) -> EmergencyContactCategoryResponse:
    category = EmergencyContactCategory(owner_id=user.id, name=payload.name, description=payload.description, sort_order=payload.sort_order)
    repository.add(db, category)
    _commit_or_conflict(db, "A category with this name already exists.")
    db.refresh(category)
    return _category_response(category, 0)


def update_category(db: Session, user: User, category_id: str, payload: EmergencyContactCategoryUpdateRequest) -> EmergencyContactCategoryResponse:
    category = _get_owned_category(db, user, category_id)
    category.name = payload.name
    category.description = payload.description
    category.sort_order = payload.sort_order
    _commit_or_conflict(db, "A category with this name already exists.")
    db.refresh(category)
    return _category_response(category, repository.count_contacts_for_category(db, user.id, category.id))


def delete_category(db: Session, user: User, category_id: str) -> None:
    category = _get_owned_category(db, user, category_id)
    if repository.count_contacts_for_category(db, user.id, category.id) > 0:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Category has contacts. Reassign or delete contacts first.")
    repository.delete_record(db, category)
    db.commit()


def _filter_contacts(
    contacts: list[EmergencyContact],
    query: str | None,
    category_id: str | None,
    favourite_filter: FavouriteFilter,
) -> list[EmergencyContact]:
    term = (query or "").strip().lower()
    category_filter = (category_id or "").strip()
    filtered: list[EmergencyContact] = []
    for contact in contacts:
        haystack = [
            contact.full_name,
            contact.relationship,
            contact.category.name,
            contact.primary_phone,
            contact.alternate_phone or "",
            contact.email or "",
            contact.country_or_region or "",
            contact.address or "",
            contact.notes or "",
        ]
        if term and not any(term in value.lower() for value in haystack):
            continue
        if category_filter and contact.category_id != category_filter:
            continue
        if favourite_filter == "favourites" and not contact.is_favourite:
            continue
        if favourite_filter == "primary" and not contact.is_primary:
            continue
        filtered.append(contact)
    return filtered


def _sort_contacts(contacts: list[EmergencyContact], sort_by: ContactSort) -> list[EmergencyContact]:
    if sort_by == "name":
        return sorted(contacts, key=lambda contact: (contact.full_name.lower(), contact.relationship.lower()))
    if sort_by == "updated":
        return sorted(contacts, key=lambda contact: contact.updated_at, reverse=True)
    return sorted(
        contacts,
        key=lambda contact: (
            not contact.is_favourite,
            not contact.is_primary,
            contact.priority,
            contact.full_name.lower(),
        ),
    )


def list_contacts(
    db: Session,
    user: User,
    query: str | None = None,
    category_id: str | None = None,
    favourite_filter: FavouriteFilter = "all",
    sort_by: ContactSort = "priority",
) -> list[EmergencyContactSummaryResponse]:
    ensure_default_categories(db, user)
    contacts = repository.list_contacts(db, user.id)
    filtered = _filter_contacts(contacts, query, category_id, favourite_filter)
    return [_contact_summary(contact) for contact in _sort_contacts(filtered, sort_by)]


def create_contact(db: Session, user: User, payload: EmergencyContactCreateRequest) -> EmergencyContactDetailResponse:
    category = _get_owned_category(db, user, payload.category_id)
    contact = EmergencyContact(owner_id=user.id, category_id=category.id, full_name=payload.full_name, relationship=payload.relationship, primary_phone=payload.primary_phone)
    _apply_contact_payload(contact, payload)
    repository.add(db, contact)
    _commit_or_conflict(db, "Unable to create contact.")
    db.refresh(contact)
    contact.category = category
    return _contact_detail(contact)


def get_contact(db: Session, user: User, contact_id: str) -> EmergencyContactDetailResponse:
    return _contact_detail(_get_owned_contact(db, user, contact_id))


def update_contact(db: Session, user: User, contact_id: str, payload: EmergencyContactUpdateRequest) -> EmergencyContactDetailResponse:
    contact = _get_owned_contact(db, user, contact_id)
    category = _get_owned_category(db, user, payload.category_id)
    _apply_contact_payload(contact, payload)
    _commit_or_conflict(db, "Unable to update contact.")
    db.refresh(contact)
    contact.category = category
    return _contact_detail(contact)


def set_contact_favourite(db: Session, user: User, contact_id: str, is_favourite: bool) -> EmergencyContactDetailResponse:
    contact = _get_owned_contact(db, user, contact_id)
    contact.is_favourite = is_favourite
    db.commit()
    db.refresh(contact)
    return _contact_detail(contact)


def set_contact_primary(db: Session, user: User, contact_id: str, is_primary: bool) -> EmergencyContactDetailResponse:
    contact = _get_owned_contact(db, user, contact_id)
    contact.is_primary = is_primary
    db.commit()
    db.refresh(contact)
    return _contact_detail(contact)


def delete_contact(db: Session, user: User, contact_id: str) -> None:
    contact = _get_owned_contact(db, user, contact_id)
    repository.delete_record(db, contact)
    db.commit()


def get_dashboard(db: Session, user: User) -> EmergencyContactDashboardResponse:
    ensure_default_categories(db, user)
    contacts = repository.list_contacts(db, user.id)
    return EmergencyContactDashboardResponse(
        total_contacts=len(contacts),
        favourite_contacts=len([contact for contact in contacts if contact.is_favourite]),
        primary_contacts=len([contact for contact in contacts if contact.is_primary]),
        missing_phone_contacts=len([contact for contact in contacts if not contact.primary_phone]),
        missing_email_contacts=len([contact for contact in contacts if not contact.email]),
    )


def get_insights(db: Session, user: User) -> EmergencyContactInsightsResponse:
    contacts = repository.list_contacts(db, user.id)
    dashboard = get_dashboard(db, user)
    category_counts = Counter(contact.category.name for contact in contacts)
    relationship_counts = Counter(contact.relationship for contact in contacts)
    country_counts = Counter(contact.country_or_region or "Not set" for contact in contacts)
    favourites = [contact for contact in contacts if contact.is_favourite][:8]
    recent = sorted(contacts, key=lambda contact: contact.created_at, reverse=True)[:8]

    return EmergencyContactInsightsResponse(
        **dashboard.model_dump(),
        categories=list_categories(db, user),
        category_distribution=[EmergencyContactCountItem(label=label, count=count) for label, count in category_counts.most_common(10)],
        relationship_distribution=[EmergencyContactCountItem(label=label, count=count) for label, count in relationship_counts.most_common(10)],
        country_distribution=[EmergencyContactCountItem(label=label, count=count) for label, count in country_counts.most_common(10)],
        favourite_contacts_list=[_contact_summary(contact) for contact in favourites],
        recent_contacts=[_contact_summary(contact) for contact in recent],
    )
