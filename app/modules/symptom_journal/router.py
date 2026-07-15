from datetime import date
from fastapi import APIRouter, Query, Response, status
from app.modules.symptom_journal import service
from app.modules.symptom_journal.dependencies import CurrentSymptomJournalUser, SymptomJournalDB
from app.modules.symptom_journal.schemas import ArchiveFilter, CategoryCreateRequest, CategoryResponse, CategoryUpdateRequest, DashboardResponse, EntryCreateRequest, EntryDetailResponse, EntryListResponse, EntrySort, EntryUpdateRequest, InsightsResponse, SeverityFilter

router = APIRouter()


@router.get("/dashboard", response_model=DashboardResponse, operation_id="getSymptomJournalDashboard")
def get_dashboard(db: SymptomJournalDB, current_user: CurrentSymptomJournalUser):
    return service.get_dashboard(db, current_user)


@router.get("/insights", response_model=InsightsResponse, operation_id="getSymptomJournalInsights")
def get_insights(db: SymptomJournalDB, current_user: CurrentSymptomJournalUser):
    return service.get_insights(db, current_user)


@router.get("/categories", response_model=list[CategoryResponse], operation_id="listSymptomJournalCategories")
def list_categories(db: SymptomJournalDB, current_user: CurrentSymptomJournalUser):
    return service.list_categories(db, current_user)


@router.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED, operation_id="createSymptomJournalCategory")
def create_category(payload: CategoryCreateRequest, db: SymptomJournalDB, current_user: CurrentSymptomJournalUser):
    return service.create_category(db, current_user, payload)


@router.put("/categories/{category_id}", response_model=CategoryResponse, operation_id="updateSymptomJournalCategory")
def update_category(category_id: str, payload: CategoryUpdateRequest, db: SymptomJournalDB, current_user: CurrentSymptomJournalUser):
    return service.update_category(db, current_user, category_id, payload)


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="deleteSymptomJournalCategory")
def delete_category(category_id: str, db: SymptomJournalDB, current_user: CurrentSymptomJournalUser):
    service.delete_category(db, current_user, category_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/entries", response_model=EntryListResponse, operation_id="listSymptomJournalEntries")
def list_entries(db: SymptomJournalDB, current_user: CurrentSymptomJournalUser, q: str | None = Query(default=None), archive_filter: ArchiveFilter = Query(default="active", alias="archiveFilter"), category_id: str | None = Query(default=None, alias="categoryId"), severity_filter: SeverityFilter = Query(default="all", alias="severityFilter"), body_location: str | None = Query(default=None, alias="bodyLocation"), date_from: date | None = Query(default=None, alias="dateFrom"), date_to: date | None = Query(default=None, alias="dateTo"), sort_by: EntrySort = Query(default="date", alias="sortBy"), page: int = Query(default=1, ge=1), page_size: int = Query(default=25, alias="pageSize", ge=1, le=100)):
    return service.list_entries(db, current_user, q, archive_filter, category_id, severity_filter, body_location, date_from, date_to, sort_by, page, page_size)


@router.post("/entries", response_model=EntryDetailResponse, status_code=status.HTTP_201_CREATED, operation_id="createSymptomJournalEntry")
def create_entry(payload: EntryCreateRequest, db: SymptomJournalDB, current_user: CurrentSymptomJournalUser):
    return service.create_entry(db, current_user, payload)


@router.get("/entries/{entry_id}", response_model=EntryDetailResponse, operation_id="getSymptomJournalEntry")
def get_entry(entry_id: str, db: SymptomJournalDB, current_user: CurrentSymptomJournalUser):
    return service.get_entry(db, current_user, entry_id)


@router.put("/entries/{entry_id}", response_model=EntryDetailResponse, operation_id="updateSymptomJournalEntry")
def update_entry(entry_id: str, payload: EntryUpdateRequest, db: SymptomJournalDB, current_user: CurrentSymptomJournalUser):
    return service.update_entry(db, current_user, entry_id, payload)


@router.post("/entries/{entry_id}/archive", response_model=EntryDetailResponse, operation_id="archiveSymptomJournalEntry")
def archive_entry(entry_id: str, db: SymptomJournalDB, current_user: CurrentSymptomJournalUser):
    return service.set_entry_archived(db, current_user, entry_id, True)


@router.post("/entries/{entry_id}/restore", response_model=EntryDetailResponse, operation_id="restoreSymptomJournalEntry")
def restore_entry(entry_id: str, db: SymptomJournalDB, current_user: CurrentSymptomJournalUser):
    return service.set_entry_archived(db, current_user, entry_id, False)


@router.delete("/entries/{entry_id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="deleteSymptomJournalEntry")
def delete_entry(entry_id: str, db: SymptomJournalDB, current_user: CurrentSymptomJournalUser):
    service.delete_entry(db, current_user, entry_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
