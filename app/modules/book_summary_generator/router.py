from typing import Annotated

from fastapi import APIRouter, Path, status

from app.modules.book_summary_generator.dependencies import BookSummaryGeneratorDb, CurrentUser
from app.modules.book_summary_generator.schemas import (
    BookCollectionCreateRequest,
    BookCollectionDetailResponse,
    BookCollectionSummaryResponse,
    BookCollectionUpdateRequest,
    BookSummaryCreateRequest,
    BookSummaryDetailResponse,
    BookSummaryGeneratorDashboardResponse,
    BookSummarySummaryResponse,
    BookSummaryUpdateRequest,
    SummaryHistoryCreateRequest,
    SummaryHistoryDetailResponse,
    SummaryHistorySummaryResponse,
    SummaryHistoryUpdateRequest,
    SummaryNoteCreateRequest,
    SummaryNoteDetailResponse,
    SummaryNoteSummaryResponse,
    SummaryNoteUpdateRequest,
)
from app.modules.book_summary_generator.service import (
    create_book,
    create_history,
    create_note,
    create_summary,
    delete_book,
    delete_history,
    delete_note,
    delete_summary,
    get_book,
    get_dashboard,
    get_history,
    get_note,
    get_summary,
    list_books,
    list_history,
    list_notes,
    list_summaries,
    update_book,
    update_history,
    update_note,
    update_summary,
)

router = APIRouter()


@router.get("/dashboard", response_model=BookSummaryGeneratorDashboardResponse)
def get_book_summary_generator_dashboard(current_user: CurrentUser, db: BookSummaryGeneratorDb) -> BookSummaryGeneratorDashboardResponse:
    return get_dashboard(db, current_user)


@router.post("/books", response_model=BookCollectionDetailResponse, status_code=status.HTTP_201_CREATED)
def create_book_collection(payload: BookCollectionCreateRequest, current_user: CurrentUser, db: BookSummaryGeneratorDb) -> BookCollectionDetailResponse:
    return create_book(db, current_user, payload)


@router.get("/books", response_model=list[BookCollectionSummaryResponse])
def list_book_collections(current_user: CurrentUser, db: BookSummaryGeneratorDb) -> list[BookCollectionSummaryResponse]:
    return list_books(db, current_user)


@router.get("/books/{book_id}", response_model=BookCollectionDetailResponse)
def get_book_collection(book_id: Annotated[int, Path(gt=0)], current_user: CurrentUser, db: BookSummaryGeneratorDb) -> BookCollectionDetailResponse:
    return get_book(db, current_user, book_id)


@router.put("/books/{book_id}", response_model=BookCollectionDetailResponse)
def update_book_collection(book_id: Annotated[int, Path(gt=0)], payload: BookCollectionUpdateRequest, current_user: CurrentUser, db: BookSummaryGeneratorDb) -> BookCollectionDetailResponse:
    return update_book(db, current_user, book_id, payload)


@router.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book_collection(book_id: Annotated[int, Path(gt=0)], current_user: CurrentUser, db: BookSummaryGeneratorDb) -> None:
    delete_book(db, current_user, book_id)


@router.post("/summaries", response_model=BookSummaryDetailResponse, status_code=status.HTTP_201_CREATED)
def create_book_summary(payload: BookSummaryCreateRequest, current_user: CurrentUser, db: BookSummaryGeneratorDb) -> BookSummaryDetailResponse:
    return create_summary(db, current_user, payload)


@router.get("/summaries", response_model=list[BookSummarySummaryResponse])
def list_book_summaries(current_user: CurrentUser, db: BookSummaryGeneratorDb) -> list[BookSummarySummaryResponse]:
    return list_summaries(db, current_user)


@router.get("/summaries/{summary_id}", response_model=BookSummaryDetailResponse)
def get_book_summary(summary_id: Annotated[int, Path(gt=0)], current_user: CurrentUser, db: BookSummaryGeneratorDb) -> BookSummaryDetailResponse:
    return get_summary(db, current_user, summary_id)


@router.put("/summaries/{summary_id}", response_model=BookSummaryDetailResponse)
def update_book_summary(summary_id: Annotated[int, Path(gt=0)], payload: BookSummaryUpdateRequest, current_user: CurrentUser, db: BookSummaryGeneratorDb) -> BookSummaryDetailResponse:
    return update_summary(db, current_user, summary_id, payload)


@router.delete("/summaries/{summary_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book_summary(summary_id: Annotated[int, Path(gt=0)], current_user: CurrentUser, db: BookSummaryGeneratorDb) -> None:
    delete_summary(db, current_user, summary_id)


@router.post("/notes", response_model=SummaryNoteDetailResponse, status_code=status.HTTP_201_CREATED)
def create_summary_note(payload: SummaryNoteCreateRequest, current_user: CurrentUser, db: BookSummaryGeneratorDb) -> SummaryNoteDetailResponse:
    return create_note(db, current_user, payload)


@router.get("/notes", response_model=list[SummaryNoteSummaryResponse])
def list_summary_notes(current_user: CurrentUser, db: BookSummaryGeneratorDb) -> list[SummaryNoteSummaryResponse]:
    return list_notes(db, current_user)


@router.get("/notes/{note_id}", response_model=SummaryNoteDetailResponse)
def get_summary_note(note_id: Annotated[int, Path(gt=0)], current_user: CurrentUser, db: BookSummaryGeneratorDb) -> SummaryNoteDetailResponse:
    return get_note(db, current_user, note_id)


@router.put("/notes/{note_id}", response_model=SummaryNoteDetailResponse)
def update_summary_note(note_id: Annotated[int, Path(gt=0)], payload: SummaryNoteUpdateRequest, current_user: CurrentUser, db: BookSummaryGeneratorDb) -> SummaryNoteDetailResponse:
    return update_note(db, current_user, note_id, payload)


@router.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_summary_note(note_id: Annotated[int, Path(gt=0)], current_user: CurrentUser, db: BookSummaryGeneratorDb) -> None:
    delete_note(db, current_user, note_id)


@router.post("/history", response_model=SummaryHistoryDetailResponse, status_code=status.HTTP_201_CREATED)
def create_summary_history(payload: SummaryHistoryCreateRequest, current_user: CurrentUser, db: BookSummaryGeneratorDb) -> SummaryHistoryDetailResponse:
    return create_history(db, current_user, payload)


@router.get("/history", response_model=list[SummaryHistorySummaryResponse])
def list_summary_history(current_user: CurrentUser, db: BookSummaryGeneratorDb) -> list[SummaryHistorySummaryResponse]:
    return list_history(db, current_user)


@router.get("/history/{history_id}", response_model=SummaryHistoryDetailResponse)
def get_summary_history(history_id: Annotated[int, Path(gt=0)], current_user: CurrentUser, db: BookSummaryGeneratorDb) -> SummaryHistoryDetailResponse:
    return get_history(db, current_user, history_id)


@router.put("/history/{history_id}", response_model=SummaryHistoryDetailResponse)
def update_summary_history(history_id: Annotated[int, Path(gt=0)], payload: SummaryHistoryUpdateRequest, current_user: CurrentUser, db: BookSummaryGeneratorDb) -> SummaryHistoryDetailResponse:
    return update_history(db, current_user, history_id, payload)


@router.delete("/history/{history_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_summary_history(history_id: Annotated[int, Path(gt=0)], current_user: CurrentUser, db: BookSummaryGeneratorDb) -> None:
    delete_history(db, current_user, history_id)
