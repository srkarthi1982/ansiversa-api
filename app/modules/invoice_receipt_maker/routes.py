from typing import Annotated

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.auth.service import get_current_user
from app.modules.invoice_receipt_maker.db import get_invoice_receipt_maker_db
from app.modules.invoice_receipt_maker.schemas import (
    InvoiceReceiptDashboardResponse,
    InvoiceReceiptDocumentCreateRequest,
    InvoiceReceiptDocumentDetailResponse,
    InvoiceReceiptDocumentUpdateRequest,
    InvoiceReceiptHistoryCreateRequest,
    InvoiceReceiptHistorySummaryResponse,
    InvoiceReceiptItemCreateRequest,
    InvoiceReceiptItemDetailResponse,
    InvoiceReceiptItemUpdateRequest,
    InvoiceReceiptProjectCreateRequest,
    InvoiceReceiptProjectDetailResponse,
    InvoiceReceiptProjectUpdateRequest,
)
from app.modules.invoice_receipt_maker.service import (
    create_document,
    create_history_item,
    create_item,
    create_project,
    delete_document,
    delete_history_item,
    delete_item,
    delete_project,
    get_dashboard,
    get_document,
    get_item,
    get_project,
    update_document,
    update_item,
    update_project,
)

router = APIRouter()


@router.get("/dashboard", response_model=InvoiceReceiptDashboardResponse)
def get_invoice_receipt_dashboard(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_invoice_receipt_maker_db)],
) -> InvoiceReceiptDashboardResponse:
    return get_dashboard(db, current_user)


@router.post(
    "/projects",
    response_model=InvoiceReceiptProjectDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_invoice_receipt_project(
    payload: InvoiceReceiptProjectCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_invoice_receipt_maker_db)],
) -> InvoiceReceiptProjectDetailResponse:
    return create_project(db, current_user, payload)


@router.get("/projects/{project_id}", response_model=InvoiceReceiptProjectDetailResponse)
def get_invoice_receipt_project(
    project_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_invoice_receipt_maker_db)],
) -> InvoiceReceiptProjectDetailResponse:
    return get_project(db, current_user, project_id)


@router.put("/projects/{project_id}", response_model=InvoiceReceiptProjectDetailResponse)
def update_invoice_receipt_project(
    project_id: Annotated[int, Path(gt=0)],
    payload: InvoiceReceiptProjectUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_invoice_receipt_maker_db)],
) -> InvoiceReceiptProjectDetailResponse:
    return update_project(db, current_user, project_id, payload)


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_invoice_receipt_project(
    project_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_invoice_receipt_maker_db)],
) -> None:
    delete_project(db, current_user, project_id)


@router.post(
    "/documents",
    response_model=InvoiceReceiptDocumentDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_invoice_receipt_document(
    payload: InvoiceReceiptDocumentCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_invoice_receipt_maker_db)],
) -> InvoiceReceiptDocumentDetailResponse:
    return create_document(db, current_user, payload)


@router.get("/documents/{document_id}", response_model=InvoiceReceiptDocumentDetailResponse)
def get_invoice_receipt_document(
    document_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_invoice_receipt_maker_db)],
) -> InvoiceReceiptDocumentDetailResponse:
    return get_document(db, current_user, document_id)


@router.put("/documents/{document_id}", response_model=InvoiceReceiptDocumentDetailResponse)
def update_invoice_receipt_document(
    document_id: Annotated[int, Path(gt=0)],
    payload: InvoiceReceiptDocumentUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_invoice_receipt_maker_db)],
) -> InvoiceReceiptDocumentDetailResponse:
    return update_document(db, current_user, document_id, payload)


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_invoice_receipt_document(
    document_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_invoice_receipt_maker_db)],
) -> None:
    delete_document(db, current_user, document_id)


@router.post(
    "/items",
    response_model=InvoiceReceiptItemDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_invoice_receipt_item(
    payload: InvoiceReceiptItemCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_invoice_receipt_maker_db)],
) -> InvoiceReceiptItemDetailResponse:
    return create_item(db, current_user, payload)


@router.get("/items/{item_id}", response_model=InvoiceReceiptItemDetailResponse)
def get_invoice_receipt_item(
    item_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_invoice_receipt_maker_db)],
) -> InvoiceReceiptItemDetailResponse:
    return get_item(db, current_user, item_id)


@router.put("/items/{item_id}", response_model=InvoiceReceiptItemDetailResponse)
def update_invoice_receipt_item(
    item_id: Annotated[int, Path(gt=0)],
    payload: InvoiceReceiptItemUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_invoice_receipt_maker_db)],
) -> InvoiceReceiptItemDetailResponse:
    return update_item(db, current_user, item_id, payload)


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_invoice_receipt_item(
    item_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_invoice_receipt_maker_db)],
) -> None:
    delete_item(db, current_user, item_id)


@router.post(
    "/history",
    response_model=InvoiceReceiptHistorySummaryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_invoice_receipt_history_item(
    payload: InvoiceReceiptHistoryCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_invoice_receipt_maker_db)],
) -> InvoiceReceiptHistorySummaryResponse:
    return create_history_item(db, current_user, payload)


@router.delete("/history/{history_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_invoice_receipt_history_item(
    history_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_invoice_receipt_maker_db)],
) -> None:
    delete_history_item(db, current_user, history_id)
