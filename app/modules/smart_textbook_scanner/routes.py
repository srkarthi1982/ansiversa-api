from typing import Annotated

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.auth.service import get_current_user
from app.modules.smart_textbook_scanner.db import get_smart_textbook_scanner_db
from app.modules.smart_textbook_scanner.schemas import (
    ExtractedNoteCreateRequest,
    ExtractedNoteListResponse,
    ExtractedNoteResponse,
    SmartTextbookScannerDashboardResponse,
    SmartTextbookScannerReviewResponse,
    TextbookPageCreateRequest,
    TextbookPageListResponse,
    TextbookPageResponse,
    TextbookPageUpdateRequest,
    TextbookScanCreateRequest,
    TextbookScanListResponse,
    TextbookScanResponse,
    TextbookScanUpdateRequest,
)
from app.modules.smart_textbook_scanner.service import (
    create_note,
    create_page,
    create_scan,
    delete_page,
    delete_scan,
    get_dashboard,
    get_page,
    get_review,
    list_notes,
    list_pages,
    list_scans,
    update_page,
    update_scan,
)

router = APIRouter()


@router.get("/dashboard", response_model=SmartTextbookScannerDashboardResponse)
def get_scanner_dashboard(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_smart_textbook_scanner_db)],
) -> SmartTextbookScannerDashboardResponse:
    return get_dashboard(db, current_user)


@router.get("/scans", response_model=TextbookScanListResponse)
def get_textbook_scans(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_smart_textbook_scanner_db)],
) -> TextbookScanListResponse:
    return TextbookScanListResponse(items=list_scans(db, current_user))


@router.post("/scans", response_model=TextbookScanResponse, status_code=status.HTTP_201_CREATED)
def create_textbook_scan(
    payload: TextbookScanCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_smart_textbook_scanner_db)],
) -> TextbookScanResponse:
    return create_scan(db, current_user, payload)


@router.put("/scans/{scan_id}", response_model=TextbookScanResponse)
def update_textbook_scan(
    scan_id: Annotated[int, Path(gt=0)],
    payload: TextbookScanUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_smart_textbook_scanner_db)],
) -> TextbookScanResponse:
    return update_scan(db, current_user, scan_id, payload)


@router.delete("/scans/{scan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_textbook_scan(
    scan_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_smart_textbook_scanner_db)],
) -> None:
    delete_scan(db, current_user, scan_id)


@router.get("/pages", response_model=TextbookPageListResponse)
def get_textbook_pages(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_smart_textbook_scanner_db)],
) -> TextbookPageListResponse:
    return TextbookPageListResponse(items=list_pages(db, current_user))


@router.get("/pages/{page_id}", response_model=TextbookPageResponse)
def get_textbook_page(
    page_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_smart_textbook_scanner_db)],
) -> TextbookPageResponse:
    return get_page(db, current_user, page_id)


@router.post("/pages", response_model=TextbookPageResponse, status_code=status.HTTP_201_CREATED)
def create_textbook_page(
    payload: TextbookPageCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_smart_textbook_scanner_db)],
) -> TextbookPageResponse:
    return create_page(db, current_user, payload)


@router.put("/pages/{page_id}", response_model=TextbookPageResponse)
def update_textbook_page(
    page_id: Annotated[int, Path(gt=0)],
    payload: TextbookPageUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_smart_textbook_scanner_db)],
) -> TextbookPageResponse:
    return update_page(db, current_user, page_id, payload)


@router.delete("/pages/{page_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_textbook_page(
    page_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_smart_textbook_scanner_db)],
) -> None:
    delete_page(db, current_user, page_id)


@router.get("/notes", response_model=ExtractedNoteListResponse)
def get_extracted_notes(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_smart_textbook_scanner_db)],
) -> ExtractedNoteListResponse:
    return ExtractedNoteListResponse(items=list_notes(db, current_user))


@router.post("/notes", response_model=ExtractedNoteResponse, status_code=status.HTTP_201_CREATED)
def create_extracted_note(
    payload: ExtractedNoteCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_smart_textbook_scanner_db)],
) -> ExtractedNoteResponse:
    return create_note(db, current_user, payload)


@router.get("/review", response_model=SmartTextbookScannerReviewResponse)
def get_scanner_review(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_smart_textbook_scanner_db)],
) -> SmartTextbookScannerReviewResponse:
    return get_review(db, current_user)
