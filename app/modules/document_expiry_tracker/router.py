from fastapi import APIRouter, Query, Response, status

from app.modules.document_expiry_tracker import service
from app.modules.document_expiry_tracker.dependencies import CurrentDocumentExpiryUser, DocumentExpiryDB
from app.modules.document_expiry_tracker.schemas import (
    DocumentExpiryDashboardResponse,
    DocumentExpiryDocumentCreateRequest,
    DocumentExpiryDocumentDetailResponse,
    DocumentExpiryDocumentSummaryResponse,
    DocumentExpiryDocumentUpdateRequest,
    DocumentExpiryRenewRequest,
    DocumentSort,
    DocumentStatus,
    ExpiryPeriod,
)

router = APIRouter()


@router.get("/dashboard", response_model=DocumentExpiryDashboardResponse, operation_id="getDocumentExpiryTrackerDashboard")
def get_dashboard(db: DocumentExpiryDB, current_user: CurrentDocumentExpiryUser):
    return service.get_dashboard(db, current_user)


@router.get("/documents", response_model=list[DocumentExpiryDocumentSummaryResponse], operation_id="listDocumentExpiryTrackerDocuments")
def list_documents(
    db: DocumentExpiryDB,
    current_user: CurrentDocumentExpiryUser,
    q: str | None = Query(default=None),
    document_type: str | None = Query(default=None, alias="documentType"),
    document_status: DocumentStatus | None = Query(default=None, alias="status"),
    country: str | None = Query(default=None),
    tag: str | None = Query(default=None),
    expiry_period: ExpiryPeriod = Query(default="all", alias="expiryPeriod"),
    sort_by: DocumentSort = Query(default="expiryDate", alias="sortBy"),
    include_archived: bool = Query(default=False, alias="includeArchived"),
):
    return service.list_documents(db, current_user, q, document_type, document_status, country, tag, expiry_period, sort_by, include_archived)


@router.post("/documents", response_model=DocumentExpiryDocumentDetailResponse, status_code=status.HTTP_201_CREATED, operation_id="createDocumentExpiryTrackerDocument")
def create_document(payload: DocumentExpiryDocumentCreateRequest, db: DocumentExpiryDB, current_user: CurrentDocumentExpiryUser):
    return service.create_document(db, current_user, payload)


@router.get("/documents/{document_id}", response_model=DocumentExpiryDocumentDetailResponse, operation_id="getDocumentExpiryTrackerDocument")
def get_document(document_id: str, db: DocumentExpiryDB, current_user: CurrentDocumentExpiryUser):
    return service.get_document(db, current_user, document_id)


@router.put("/documents/{document_id}", response_model=DocumentExpiryDocumentDetailResponse, operation_id="updateDocumentExpiryTrackerDocument")
def update_document(document_id: str, payload: DocumentExpiryDocumentUpdateRequest, db: DocumentExpiryDB, current_user: CurrentDocumentExpiryUser):
    return service.update_document(db, current_user, document_id, payload)


@router.post("/documents/{document_id}/archive", response_model=DocumentExpiryDocumentDetailResponse, operation_id="archiveDocumentExpiryTrackerDocument")
def archive_document(document_id: str, db: DocumentExpiryDB, current_user: CurrentDocumentExpiryUser):
    return service.archive_document(db, current_user, document_id)


@router.post("/documents/{document_id}/restore", response_model=DocumentExpiryDocumentDetailResponse, operation_id="restoreDocumentExpiryTrackerDocument")
def restore_document(document_id: str, db: DocumentExpiryDB, current_user: CurrentDocumentExpiryUser):
    return service.restore_document(db, current_user, document_id)


@router.post("/documents/{document_id}/renew", response_model=DocumentExpiryDocumentDetailResponse, operation_id="renewDocumentExpiryTrackerDocument")
def renew_document(document_id: str, payload: DocumentExpiryRenewRequest, db: DocumentExpiryDB, current_user: CurrentDocumentExpiryUser):
    return service.renew_document(db, current_user, document_id, payload)


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="deleteDocumentExpiryTrackerDocument")
def delete_document(document_id: str, db: DocumentExpiryDB, current_user: CurrentDocumentExpiryUser):
    service.delete_document(db, current_user, document_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
