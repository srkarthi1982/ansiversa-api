from typing import Annotated

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from app.modules.ai_notes_summarizer.db import get_ai_notes_summarizer_db
from app.modules.ai_notes_summarizer.schemas import (
    NoteSummaryListResponse,
    NoteSummaryResponse,
    NotesDocumentCreateRequest,
    NotesDocumentDetailResponse,
    NotesDocumentListResponse,
    NotesDocumentUpdateRequest,
)
from app.modules.ai_notes_summarizer.service import (
    create_document,
    create_summary,
    delete_document,
    get_document_detail,
    list_documents,
    list_summaries,
    update_document,
)
from app.modules.auth.models import User
from app.modules.auth.service import get_current_user

router = APIRouter()


@router.get("/documents", response_model=NotesDocumentListResponse)
def get_documents(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_ai_notes_summarizer_db)],
) -> NotesDocumentListResponse:
    return NotesDocumentListResponse(items=list_documents(db, current_user))


@router.post(
    "/documents",
    response_model=NotesDocumentDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_notes_document(
    payload: NotesDocumentCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_ai_notes_summarizer_db)],
) -> NotesDocumentDetailResponse:
    return create_document(db, current_user, payload)


@router.get("/documents/{document_id}", response_model=NotesDocumentDetailResponse)
def get_notes_document(
    document_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_ai_notes_summarizer_db)],
) -> NotesDocumentDetailResponse:
    return get_document_detail(db, current_user, document_id)


@router.put("/documents/{document_id}", response_model=NotesDocumentDetailResponse)
def update_notes_document(
    document_id: Annotated[int, Path(gt=0)],
    payload: NotesDocumentUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_ai_notes_summarizer_db)],
) -> NotesDocumentDetailResponse:
    return update_document(db, current_user, document_id, payload)


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notes_document(
    document_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_ai_notes_summarizer_db)],
) -> None:
    delete_document(db, current_user, document_id)


@router.post(
    "/documents/{document_id}/summaries",
    response_model=NoteSummaryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_notes_summary(
    document_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_ai_notes_summarizer_db)],
) -> NoteSummaryResponse:
    return create_summary(db, current_user, document_id)


@router.get("/summaries", response_model=NoteSummaryListResponse)
def get_summaries(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_ai_notes_summarizer_db)],
) -> NoteSummaryListResponse:
    return NoteSummaryListResponse(items=list_summaries(db, current_user))
