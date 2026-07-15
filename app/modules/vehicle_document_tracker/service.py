from __future__ import annotations
from collections import Counter
from datetime import date, timedelta
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.modules.auth.models import User
from app.modules.vehicle_document_tracker import repository
from app.modules.vehicle_document_tracker.models import VehicleDocument, VehicleDocumentType, VehicleDocumentVehicle
from app.modules.vehicle_document_tracker.schemas import ArchiveFilter, CountItem, DashboardResponse, DocumentCreateRequest, DocumentListResponse, DocumentResponse, DocumentSort, DocumentTypeCreateRequest, DocumentTypeResponse, DocumentTypeUpdateRequest, DocumentUpdateRequest, InsightsResponse, VehicleCreateRequest, VehicleResponse, VehicleUpdateRequest

DEFAULT_TYPES = [
    ("Vehicle Registration", 10),
    ("Insurance", 20),
    ("Driving Licence Reference", 30),
    ("Emissions Certificate", 40),
    ("Roadworthiness Inspection", 50),
    ("Warranty", 60),
    ("Service Contract", 70),
    ("Other", 80),
]


def _commit(db: Session, message: str) -> None:
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=message) from exc


def ensure_seed_types(db: Session, user: User) -> None:
    existing = {item.name for item in repository.list_types(db, user.id)}
    created = False
    for name, order in DEFAULT_TYPES:
        if name not in existing:
            repository.add(db, VehicleDocumentType(owner_id="system", name=name, sort_order=order, is_system=True))
            created = True
    if created:
        _commit(db, "Unable to prepare default document types.")


def _not_found(resource: str) -> None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{resource} was not found.")


def _vehicle(db: Session, user: User, vehicle_id: str) -> VehicleDocumentVehicle:
    item = repository.get_vehicle(db, vehicle_id)
    if not item or item.owner_id != user.id:
        _not_found("Vehicle")
    return item


def _type(db: Session, user: User, type_id: str) -> VehicleDocumentType:
    ensure_seed_types(db, user)
    item = repository.get_type(db, type_id)
    if not item or (item.owner_id != user.id and not item.is_system):
        _not_found("Document type")
    return item


def _document(db: Session, user: User, document_id: str) -> VehicleDocument:
    item = repository.get_document(db, document_id)
    if not item or item.owner_id != user.id:
        _not_found("Vehicle document")
    return item


def _computed_status(item: VehicleDocument, today: date | None = None) -> str:
    today = today or date.today()
    if item.archived:
        return "archived"
    if item.expiry_date and item.expiry_date < today:
        return "expired"
    if item.reminder_date and item.reminder_date <= today:
        return "renewal_due"
    return item.status


def _days_until_expiry(item: VehicleDocument, today: date | None = None) -> int | None:
    if not item.expiry_date:
        return None
    return (item.expiry_date - (today or date.today())).days


def _document_response(item: VehicleDocument) -> DocumentResponse:
    return DocumentResponse(id=item.id, vehicle_id=item.vehicle_id, vehicle_name=item.vehicle.vehicle_name, document_type_id=item.document_type_id, document_type_name=item.document_type.name, document_number=item.document_number, issue_date=item.issue_date, expiry_date=item.expiry_date, reminder_date=item.reminder_date, issuing_authority=item.issuing_authority, status=item.status, computed_status=_computed_status(item), days_until_expiry=_days_until_expiry(item), archived=item.archived, notes=item.notes, created_at=item.created_at, updated_at=item.updated_at)


def _vehicle_response(item: VehicleDocumentVehicle, docs: list[VehicleDocument]) -> VehicleResponse:
    related = [doc for doc in docs if doc.vehicle_id == item.id and not doc.archived]
    return VehicleResponse(id=item.id, vehicle_name=item.vehicle_name, manufacturer=item.manufacturer, model=item.model, year=item.year, registration_nickname=item.registration_nickname, registration_number=item.registration_number, notes=item.notes, archived=item.archived, document_count=len(related), expired_count=sum(1 for doc in related if _computed_status(doc) == "expired"), upcoming_count=sum(1 for doc in related if doc.expiry_date and 0 <= _days_until_expiry(doc) <= 30), created_at=item.created_at, updated_at=item.updated_at)


def _type_response(item: VehicleDocumentType, docs: list[VehicleDocument], user: User) -> DocumentTypeResponse:
    count = sum(1 for doc in docs if doc.document_type_id == item.id and not doc.archived)
    return DocumentTypeResponse(id=item.id, name=item.name, sort_order=item.sort_order, is_system=item.is_system, document_count=count, created_at=item.created_at, updated_at=item.updated_at)


def list_vehicles(db: Session, user: User, archive_filter: ArchiveFilter = "active") -> list[VehicleResponse]:
    vehicles = repository.list_vehicles(db, user.id)
    if archive_filter == "active":
        vehicles = [item for item in vehicles if not item.archived]
    elif archive_filter == "archived":
        vehicles = [item for item in vehicles if item.archived]
    docs = repository.list_documents(db, user.id)
    return [_vehicle_response(item, docs) for item in vehicles]


def create_vehicle(db: Session, user: User, payload: VehicleCreateRequest) -> VehicleResponse:
    item = VehicleDocumentVehicle(owner_id=user.id, vehicle_name=payload.vehicle_name, manufacturer=payload.manufacturer, model=payload.model, year=payload.year, registration_nickname=payload.registration_nickname, registration_number=payload.registration_number, notes=payload.notes, archived=payload.archived)
    repository.add(db, item)
    db.commit()
    db.refresh(item)
    return _vehicle_response(item, repository.list_documents(db, user.id))


def update_vehicle(db: Session, user: User, vehicle_id: str, payload: VehicleUpdateRequest) -> VehicleResponse:
    item = _vehicle(db, user, vehicle_id)
    item.vehicle_name = payload.vehicle_name
    item.manufacturer = payload.manufacturer
    item.model = payload.model
    item.year = payload.year
    item.registration_nickname = payload.registration_nickname
    item.registration_number = payload.registration_number
    item.notes = payload.notes
    item.archived = payload.archived
    db.commit()
    db.refresh(item)
    return _vehicle_response(item, repository.list_documents(db, user.id))


def set_vehicle_archived(db: Session, user: User, vehicle_id: str, archived: bool) -> VehicleResponse:
    item = _vehicle(db, user, vehicle_id)
    item.archived = archived
    db.commit()
    db.refresh(item)
    return _vehicle_response(item, repository.list_documents(db, user.id))


def delete_vehicle(db: Session, user: User, vehicle_id: str) -> None:
    item = _vehicle(db, user, vehicle_id)
    if repository.count_documents_for_vehicle(db, user.id, vehicle_id):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Delete linked documents before deleting this vehicle.")
    repository.delete(db, item)
    db.commit()


def list_document_types(db: Session, user: User) -> list[DocumentTypeResponse]:
    ensure_seed_types(db, user)
    docs = repository.list_documents(db, user.id)
    return [_type_response(item, docs, user) for item in repository.list_types(db, user.id)]


def create_document_type(db: Session, user: User, payload: DocumentTypeCreateRequest) -> DocumentTypeResponse:
    item = VehicleDocumentType(owner_id=user.id, name=payload.name, sort_order=payload.sort_order, is_system=False)
    repository.add(db, item)
    _commit(db, "A document type with this name already exists.")
    db.refresh(item)
    return _type_response(item, repository.list_documents(db, user.id), user)


def update_document_type(db: Session, user: User, type_id: str, payload: DocumentTypeUpdateRequest) -> DocumentTypeResponse:
    item = _type(db, user, type_id)
    if item.is_system:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="System document types cannot be edited.")
    item.name = payload.name
    item.sort_order = payload.sort_order
    _commit(db, "A document type with this name already exists.")
    db.refresh(item)
    return _type_response(item, repository.list_documents(db, user.id), user)


def delete_document_type(db: Session, user: User, type_id: str) -> None:
    item = _type(db, user, type_id)
    if item.is_system:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="System document types cannot be deleted.")
    if repository.count_documents_for_type(db, user.id, type_id):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Delete linked documents before deleting this type.")
    repository.delete(db, item)
    db.commit()


def _apply_document(item: VehicleDocument, payload: DocumentCreateRequest | DocumentUpdateRequest) -> None:
    item.vehicle_id = payload.vehicle_id
    item.document_type_id = payload.document_type_id
    item.document_number = payload.document_number
    item.issue_date = payload.issue_date
    item.expiry_date = payload.expiry_date
    item.reminder_date = payload.reminder_date
    item.issuing_authority = payload.issuing_authority
    item.status = payload.status
    item.notes = payload.notes
    item.archived = payload.archived


def create_document(db: Session, user: User, payload: DocumentCreateRequest) -> DocumentResponse:
    vehicle = _vehicle(db, user, payload.vehicle_id)
    doc_type = _type(db, user, payload.document_type_id)
    item = VehicleDocument(owner_id=user.id, vehicle_id=vehicle.id, document_type_id=doc_type.id, status=payload.status)
    _apply_document(item, payload)
    repository.add(db, item)
    db.commit()
    return _document_response(repository.get_document(db, item.id))


def get_document(db: Session, user: User, document_id: str) -> DocumentResponse:
    return _document_response(_document(db, user, document_id))


def update_document(db: Session, user: User, document_id: str, payload: DocumentUpdateRequest) -> DocumentResponse:
    item = _document(db, user, document_id)
    _vehicle(db, user, payload.vehicle_id)
    _type(db, user, payload.document_type_id)
    _apply_document(item, payload)
    db.commit()
    return get_document(db, user, document_id)


def set_document_archived(db: Session, user: User, document_id: str, archived: bool) -> DocumentResponse:
    item = _document(db, user, document_id)
    item.archived = archived
    item.status = "archived" if archived else "active"
    db.commit()
    return get_document(db, user, document_id)


def delete_document(db: Session, user: User, document_id: str) -> None:
    repository.delete(db, _document(db, user, document_id))
    db.commit()


def _filtered_documents(db: Session, user: User, q: str | None, vehicle_id: str | None, document_type_id: str | None, status_filter: str | None, expiry_from: date | None, expiry_to: date | None, archive_filter: ArchiveFilter, sort_by: DocumentSort) -> list[VehicleDocument]:
    docs = repository.list_documents(db, user.id)
    if archive_filter == "active":
        docs = [item for item in docs if not item.archived]
    elif archive_filter == "archived":
        docs = [item for item in docs if item.archived]
    if vehicle_id:
        docs = [item for item in docs if item.vehicle_id == vehicle_id]
    if document_type_id:
        docs = [item for item in docs if item.document_type_id == document_type_id]
    if status_filter:
        docs = [item for item in docs if _computed_status(item) == status_filter or item.status == status_filter]
    if expiry_from:
        docs = [item for item in docs if item.expiry_date and item.expiry_date >= expiry_from]
    if expiry_to:
        docs = [item for item in docs if item.expiry_date and item.expiry_date <= expiry_to]
    if q:
        needle = q.lower()
        docs = [item for item in docs if needle in " ".join([item.vehicle.vehicle_name, item.document_type.name, item.document_number or "", item.issuing_authority or "", item.notes or "", item.status]).lower()]
    if sort_by == "reminder":
        docs.sort(key=lambda item: (item.reminder_date or date.max, item.expiry_date or date.max))
    elif sort_by == "updated":
        docs.sort(key=lambda item: item.updated_at, reverse=True)
    elif sort_by == "vehicle":
        docs.sort(key=lambda item: (item.vehicle.vehicle_name, item.expiry_date or date.max))
    elif sort_by == "type":
        docs.sort(key=lambda item: (item.document_type.name, item.expiry_date or date.max))
    elif sort_by == "status":
        docs.sort(key=lambda item: (_computed_status(item), item.expiry_date or date.max))
    else:
        docs.sort(key=lambda item: (item.expiry_date or date.max, item.updated_at))
    return docs


def list_documents(db: Session, user: User, q: str | None, vehicle_id: str | None, document_type_id: str | None, status_filter: str | None, expiry_from: date | None, expiry_to: date | None, archive_filter: ArchiveFilter, sort_by: DocumentSort, page: int, page_size: int) -> DocumentListResponse:
    ensure_seed_types(db, user)
    docs = _filtered_documents(db, user, q, vehicle_id, document_type_id, status_filter, expiry_from, expiry_to, archive_filter, sort_by)
    start = (page - 1) * page_size
    return DocumentListResponse(items=[_document_response(item) for item in docs[start:start + page_size]], total=len(docs), page=page, page_size=page_size)


def get_dashboard(db: Session, user: User) -> DashboardResponse:
    docs = [doc for doc in repository.list_documents(db, user.id) if not doc.archived]
    vehicles = [vehicle for vehicle in repository.list_vehicles(db, user.id) if not vehicle.archived]
    today = date.today()
    week_end = today + timedelta(days=7)
    return DashboardResponse(total_vehicles=len(vehicles), total_documents=len(docs), expiring_today=sum(1 for doc in docs if doc.expiry_date == today), expiring_this_week=sum(1 for doc in docs if doc.expiry_date and today <= doc.expiry_date <= week_end), expired_documents=sum(1 for doc in docs if _computed_status(doc, today) == "expired"), upcoming_renewals=sum(1 for doc in docs if doc.reminder_date and doc.reminder_date <= week_end and (not doc.expiry_date or doc.expiry_date >= today)))


def get_insights(db: Session, user: User) -> InsightsResponse:
    ensure_seed_types(db, user)
    docs = [doc for doc in repository.list_documents(db, user.id) if not doc.archived]
    dashboard = get_dashboard(db, user)
    today = date.today()
    by_type = Counter(doc.document_type.name for doc in docs)
    by_vehicle = Counter(doc.vehicle.vehicle_name for doc in docs)
    by_status = Counter(_computed_status(doc, today) for doc in docs)
    recent = sorted(docs, key=lambda item: item.updated_at, reverse=True)[:8]
    upcoming = sorted([doc for doc in docs if doc.expiry_date and doc.expiry_date >= today], key=lambda item: item.expiry_date)[:8]
    expired = sorted([doc for doc in docs if _computed_status(doc, today) == "expired"], key=lambda item: item.expiry_date or date.min)[:8]
    return InsightsResponse(**dashboard.model_dump(), vehicles=list_vehicles(db, user, "all"), document_types=list_document_types(db, user), recent_documents=[_document_response(doc) for doc in recent], upcoming_documents=[_document_response(doc) for doc in upcoming], expired_document_items=[_document_response(doc) for doc in expired], documents_by_type=[CountItem(label=k, count=v) for k, v in by_type.most_common()], documents_by_vehicle=[CountItem(label=k, count=v) for k, v in by_vehicle.most_common()], documents_by_status=[CountItem(label=k, count=v) for k, v in by_status.most_common()])
