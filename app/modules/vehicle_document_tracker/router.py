from datetime import date
from fastapi import APIRouter, Query, Response, status
from app.modules.vehicle_document_tracker import service
from app.modules.vehicle_document_tracker.dependencies import CurrentVehicleDocumentTrackerUser, VehicleDocumentTrackerDB
from app.modules.vehicle_document_tracker.schemas import ArchiveFilter, DashboardResponse, DocumentCreateRequest, DocumentListResponse, DocumentResponse, DocumentSort, DocumentTypeCreateRequest, DocumentTypeResponse, DocumentTypeUpdateRequest, DocumentUpdateRequest, InsightsResponse, VehicleCreateRequest, VehicleResponse, VehicleUpdateRequest

router = APIRouter()


@router.get("/dashboard", response_model=DashboardResponse, operation_id="getVehicleDocumentTrackerDashboard")
def get_dashboard(db: VehicleDocumentTrackerDB, current_user: CurrentVehicleDocumentTrackerUser):
    return service.get_dashboard(db, current_user)


@router.get("/insights", response_model=InsightsResponse, operation_id="getVehicleDocumentTrackerInsights")
def get_insights(db: VehicleDocumentTrackerDB, current_user: CurrentVehicleDocumentTrackerUser):
    return service.get_insights(db, current_user)


@router.get("/vehicles", response_model=list[VehicleResponse], operation_id="listVehicleDocumentTrackerVehicles")
def list_vehicles(db: VehicleDocumentTrackerDB, current_user: CurrentVehicleDocumentTrackerUser, archive_filter: ArchiveFilter = Query(default="active", alias="archiveFilter")):
    return service.list_vehicles(db, current_user, archive_filter)


@router.post("/vehicles", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED, operation_id="createVehicleDocumentTrackerVehicle")
def create_vehicle(payload: VehicleCreateRequest, db: VehicleDocumentTrackerDB, current_user: CurrentVehicleDocumentTrackerUser):
    return service.create_vehicle(db, current_user, payload)


@router.put("/vehicles/{vehicle_id}", response_model=VehicleResponse, operation_id="updateVehicleDocumentTrackerVehicle")
def update_vehicle(vehicle_id: str, payload: VehicleUpdateRequest, db: VehicleDocumentTrackerDB, current_user: CurrentVehicleDocumentTrackerUser):
    return service.update_vehicle(db, current_user, vehicle_id, payload)


@router.post("/vehicles/{vehicle_id}/archive", response_model=VehicleResponse, operation_id="archiveVehicleDocumentTrackerVehicle")
def archive_vehicle(vehicle_id: str, db: VehicleDocumentTrackerDB, current_user: CurrentVehicleDocumentTrackerUser):
    return service.set_vehicle_archived(db, current_user, vehicle_id, True)


@router.post("/vehicles/{vehicle_id}/restore", response_model=VehicleResponse, operation_id="restoreVehicleDocumentTrackerVehicle")
def restore_vehicle(vehicle_id: str, db: VehicleDocumentTrackerDB, current_user: CurrentVehicleDocumentTrackerUser):
    return service.set_vehicle_archived(db, current_user, vehicle_id, False)


@router.delete("/vehicles/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="deleteVehicleDocumentTrackerVehicle")
def delete_vehicle(vehicle_id: str, db: VehicleDocumentTrackerDB, current_user: CurrentVehicleDocumentTrackerUser):
    service.delete_vehicle(db, current_user, vehicle_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/document-types", response_model=list[DocumentTypeResponse], operation_id="listVehicleDocumentTrackerDocumentTypes")
def list_document_types(db: VehicleDocumentTrackerDB, current_user: CurrentVehicleDocumentTrackerUser):
    return service.list_document_types(db, current_user)


@router.post("/document-types", response_model=DocumentTypeResponse, status_code=status.HTTP_201_CREATED, operation_id="createVehicleDocumentTrackerDocumentType")
def create_document_type(payload: DocumentTypeCreateRequest, db: VehicleDocumentTrackerDB, current_user: CurrentVehicleDocumentTrackerUser):
    return service.create_document_type(db, current_user, payload)


@router.put("/document-types/{type_id}", response_model=DocumentTypeResponse, operation_id="updateVehicleDocumentTrackerDocumentType")
def update_document_type(type_id: str, payload: DocumentTypeUpdateRequest, db: VehicleDocumentTrackerDB, current_user: CurrentVehicleDocumentTrackerUser):
    return service.update_document_type(db, current_user, type_id, payload)


@router.delete("/document-types/{type_id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="deleteVehicleDocumentTrackerDocumentType")
def delete_document_type(type_id: str, db: VehicleDocumentTrackerDB, current_user: CurrentVehicleDocumentTrackerUser):
    service.delete_document_type(db, current_user, type_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/documents", response_model=DocumentListResponse, operation_id="listVehicleDocumentTrackerDocuments")
def list_documents(db: VehicleDocumentTrackerDB, current_user: CurrentVehicleDocumentTrackerUser, q: str | None = None, vehicle_id: str | None = Query(default=None, alias="vehicleId"), document_type_id: str | None = Query(default=None, alias="documentTypeId"), status_filter: str | None = Query(default=None, alias="status"), expiry_from: date | None = Query(default=None, alias="expiryFrom"), expiry_to: date | None = Query(default=None, alias="expiryTo"), archive_filter: ArchiveFilter = Query(default="active", alias="archiveFilter"), sort_by: DocumentSort = Query(default="expiry", alias="sortBy"), page: int = Query(default=1, ge=1), page_size: int = Query(default=25, alias="pageSize", ge=1, le=100)):
    return service.list_documents(db, current_user, q, vehicle_id, document_type_id, status_filter, expiry_from, expiry_to, archive_filter, sort_by, page, page_size)


@router.post("/documents", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED, operation_id="createVehicleDocumentTrackerDocument")
def create_document(payload: DocumentCreateRequest, db: VehicleDocumentTrackerDB, current_user: CurrentVehicleDocumentTrackerUser):
    return service.create_document(db, current_user, payload)


@router.get("/documents/{document_id}", response_model=DocumentResponse, operation_id="getVehicleDocumentTrackerDocument")
def get_document(document_id: str, db: VehicleDocumentTrackerDB, current_user: CurrentVehicleDocumentTrackerUser):
    return service.get_document(db, current_user, document_id)


@router.put("/documents/{document_id}", response_model=DocumentResponse, operation_id="updateVehicleDocumentTrackerDocument")
def update_document(document_id: str, payload: DocumentUpdateRequest, db: VehicleDocumentTrackerDB, current_user: CurrentVehicleDocumentTrackerUser):
    return service.update_document(db, current_user, document_id, payload)


@router.post("/documents/{document_id}/archive", response_model=DocumentResponse, operation_id="archiveVehicleDocumentTrackerDocument")
def archive_document(document_id: str, db: VehicleDocumentTrackerDB, current_user: CurrentVehicleDocumentTrackerUser):
    return service.set_document_archived(db, current_user, document_id, True)


@router.post("/documents/{document_id}/restore", response_model=DocumentResponse, operation_id="restoreVehicleDocumentTrackerDocument")
def restore_document(document_id: str, db: VehicleDocumentTrackerDB, current_user: CurrentVehicleDocumentTrackerUser):
    return service.set_document_archived(db, current_user, document_id, False)


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="deleteVehicleDocumentTrackerDocument")
def delete_document(document_id: str, db: VehicleDocumentTrackerDB, current_user: CurrentVehicleDocumentTrackerUser):
    service.delete_document(db, current_user, document_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
