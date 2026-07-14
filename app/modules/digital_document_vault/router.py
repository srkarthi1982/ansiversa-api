from fastapi import APIRouter, File, Form, Query, Response, UploadFile, status
from pydantic import ValidationError

from app.modules.digital_document_vault import service
from app.modules.digital_document_vault.dependencies import CurrentDigitalDocumentVaultUser, DigitalDocumentVaultDB
from app.modules.digital_document_vault.schemas import (
    DocumentSort,
    ExpiryFilter,
    VaultCategoryCreateRequest,
    VaultCategoryResponse,
    VaultCategoryUpdateRequest,
    VaultDashboardResponse,
    VaultDocumentDetailResponse,
    VaultDocumentMetadataRequest,
    VaultDocumentSummaryResponse,
)

router = APIRouter()


def _metadata_from_form(
    title: str,
    category_id: str,
    document_type: str,
    description: str | None,
    tags: str | None,
    issue_date: str | None,
    expiry_date: str | None,
) -> VaultDocumentMetadataRequest:
    try:
        return VaultDocumentMetadataRequest(
            title=title,
            categoryId=category_id,
            documentType=document_type,
            description=description,
            tags=tags or "",
            issueDate=issue_date,
            expiryDate=expiry_date,
        )
    except ValidationError as exc:
        raise exc


@router.get("/dashboard", response_model=VaultDashboardResponse, operation_id="getDigitalDocumentVaultDashboard")
def get_dashboard(db: DigitalDocumentVaultDB, current_user: CurrentDigitalDocumentVaultUser):
    return service.get_dashboard(db, current_user)


@router.get("/categories", response_model=list[VaultCategoryResponse], operation_id="listDigitalDocumentVaultCategories")
def list_categories(db: DigitalDocumentVaultDB, current_user: CurrentDigitalDocumentVaultUser):
    return service.list_categories(db, current_user)


@router.post("/categories", response_model=VaultCategoryResponse, status_code=status.HTTP_201_CREATED, operation_id="createDigitalDocumentVaultCategory")
def create_category(payload: VaultCategoryCreateRequest, db: DigitalDocumentVaultDB, current_user: CurrentDigitalDocumentVaultUser):
    return service.create_category(db, current_user, payload)


@router.put("/categories/{category_id}", response_model=VaultCategoryResponse, operation_id="updateDigitalDocumentVaultCategory")
def update_category(category_id: str, payload: VaultCategoryUpdateRequest, db: DigitalDocumentVaultDB, current_user: CurrentDigitalDocumentVaultUser):
    return service.update_category(db, current_user, category_id, payload)


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="deleteDigitalDocumentVaultCategory")
def delete_category(category_id: str, db: DigitalDocumentVaultDB, current_user: CurrentDigitalDocumentVaultUser):
    service.delete_category(db, current_user, category_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/documents", response_model=list[VaultDocumentSummaryResponse], operation_id="listDigitalDocumentVaultDocuments")
def list_documents(
    db: DigitalDocumentVaultDB,
    current_user: CurrentDigitalDocumentVaultUser,
    q: str | None = Query(default=None),
    category_id: str | None = Query(default=None, alias="categoryId"),
    document_type: str | None = Query(default=None, alias="documentType"),
    expiry_filter: ExpiryFilter = Query(default="all", alias="expiryFilter"),
    sort_by: DocumentSort = Query(default="uploadedAt", alias="sortBy"),
):
    return service.list_documents(db, current_user, q, category_id, document_type, expiry_filter, sort_by)


@router.post("/documents", response_model=VaultDocumentDetailResponse, status_code=status.HTTP_201_CREATED, operation_id="createDigitalDocumentVaultDocument")
async def create_document(
    db: DigitalDocumentVaultDB,
    current_user: CurrentDigitalDocumentVaultUser,
    title: str = Form(...),
    category_id: str = Form(..., alias="categoryId"),
    document_type: str = Form(..., alias="documentType"),
    description: str | None = Form(default=None),
    tags: str | None = Form(default=None),
    issue_date: str | None = Form(default=None, alias="issueDate"),
    expiry_date: str | None = Form(default=None, alias="expiryDate"),
    file: UploadFile = File(...),
):
    payload = _metadata_from_form(title, category_id, document_type, description, tags, issue_date, expiry_date)
    return await service.create_document(db, current_user, payload, file)


@router.get("/documents/{document_id}", response_model=VaultDocumentDetailResponse, operation_id="getDigitalDocumentVaultDocument")
def get_document(document_id: str, db: DigitalDocumentVaultDB, current_user: CurrentDigitalDocumentVaultUser):
    return service.get_document(db, current_user, document_id)


@router.put("/documents/{document_id}", response_model=VaultDocumentDetailResponse, operation_id="updateDigitalDocumentVaultDocument")
def update_document(document_id: str, payload: VaultDocumentMetadataRequest, db: DigitalDocumentVaultDB, current_user: CurrentDigitalDocumentVaultUser):
    return service.update_document(db, current_user, document_id, payload)


@router.post("/documents/{document_id}/replace-file", response_model=VaultDocumentDetailResponse, operation_id="replaceDigitalDocumentVaultDocumentFile")
async def replace_document_file(document_id: str, db: DigitalDocumentVaultDB, current_user: CurrentDigitalDocumentVaultUser, file: UploadFile = File(...)):
    return await service.replace_document_file(db, current_user, document_id, file)


@router.get("/documents/{document_id}/download", operation_id="downloadDigitalDocumentVaultDocument")
def download_document(document_id: str, db: DigitalDocumentVaultDB, current_user: CurrentDigitalDocumentVaultUser):
    document = service.get_document_file(db, current_user, document_id)
    return Response(
        content=service.file_blob_from_storage(document.file_blob),
        media_type=document.mime_type,
        headers={"Content-Disposition": f'attachment; filename="{document.file_name}"'},
    )


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="deleteDigitalDocumentVaultDocument")
def delete_document(document_id: str, db: DigitalDocumentVaultDB, current_user: CurrentDigitalDocumentVaultUser):
    service.delete_document(db, current_user, document_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
