from typing import Annotated

from fastapi import APIRouter, Path, status

from app.modules.snippet_generator.dependencies import CurrentUser, SnippetGeneratorDb
from app.modules.snippet_generator.schemas import (
    SnippetCategoryCreateRequest,
    SnippetCategoryDetailResponse,
    SnippetCategorySummaryResponse,
    SnippetCategoryUpdateRequest,
    SnippetCreateRequest,
    SnippetDetailResponse,
    SnippetGeneratorDashboardResponse,
    SnippetHistoryCreateRequest,
    SnippetHistoryDetailResponse,
    SnippetHistorySummaryResponse,
    SnippetHistoryUpdateRequest,
    SnippetProjectCreateRequest,
    SnippetProjectDetailResponse,
    SnippetProjectSummaryResponse,
    SnippetProjectUpdateRequest,
    SnippetSummaryResponse,
    SnippetUpdateRequest,
)
from app.modules.snippet_generator.service import (
    create_category,
    create_history,
    create_project,
    create_snippet,
    delete_category,
    delete_history,
    delete_project,
    delete_snippet,
    get_category,
    get_dashboard,
    get_history,
    get_project,
    get_snippet,
    list_categories,
    list_history,
    list_projects,
    list_snippets,
    update_category,
    update_history,
    update_project,
    update_snippet,
)

router = APIRouter()


@router.get("/dashboard", response_model=SnippetGeneratorDashboardResponse)
def get_snippet_generator_dashboard(current_user: CurrentUser, db: SnippetGeneratorDb) -> SnippetGeneratorDashboardResponse:
    return get_dashboard(db, current_user)


@router.post("/projects", response_model=SnippetProjectDetailResponse, status_code=status.HTTP_201_CREATED)
def create_snippet_project(payload: SnippetProjectCreateRequest, current_user: CurrentUser, db: SnippetGeneratorDb) -> SnippetProjectDetailResponse:
    return create_project(db, current_user, payload)


@router.get("/projects", response_model=list[SnippetProjectSummaryResponse])
def list_snippet_projects(current_user: CurrentUser, db: SnippetGeneratorDb) -> list[SnippetProjectSummaryResponse]:
    return list_projects(db, current_user)


@router.get("/projects/{project_id}", response_model=SnippetProjectDetailResponse)
def get_snippet_project(project_id: Annotated[int, Path(gt=0)], current_user: CurrentUser, db: SnippetGeneratorDb) -> SnippetProjectDetailResponse:
    return get_project(db, current_user, project_id)


@router.put("/projects/{project_id}", response_model=SnippetProjectDetailResponse)
def update_snippet_project(project_id: Annotated[int, Path(gt=0)], payload: SnippetProjectUpdateRequest, current_user: CurrentUser, db: SnippetGeneratorDb) -> SnippetProjectDetailResponse:
    return update_project(db, current_user, project_id, payload)


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_snippet_project(project_id: Annotated[int, Path(gt=0)], current_user: CurrentUser, db: SnippetGeneratorDb) -> None:
    delete_project(db, current_user, project_id)


@router.post("/categories", response_model=SnippetCategoryDetailResponse, status_code=status.HTTP_201_CREATED)
def create_snippet_category(payload: SnippetCategoryCreateRequest, current_user: CurrentUser, db: SnippetGeneratorDb) -> SnippetCategoryDetailResponse:
    return create_category(db, current_user, payload)


@router.get("/categories", response_model=list[SnippetCategorySummaryResponse])
def list_snippet_categories(current_user: CurrentUser, db: SnippetGeneratorDb) -> list[SnippetCategorySummaryResponse]:
    return list_categories(db, current_user)


@router.get("/categories/{category_id}", response_model=SnippetCategoryDetailResponse)
def get_snippet_category(category_id: Annotated[int, Path(gt=0)], current_user: CurrentUser, db: SnippetGeneratorDb) -> SnippetCategoryDetailResponse:
    return get_category(db, current_user, category_id)


@router.put("/categories/{category_id}", response_model=SnippetCategoryDetailResponse)
def update_snippet_category(category_id: Annotated[int, Path(gt=0)], payload: SnippetCategoryUpdateRequest, current_user: CurrentUser, db: SnippetGeneratorDb) -> SnippetCategoryDetailResponse:
    return update_category(db, current_user, category_id, payload)


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_snippet_category(category_id: Annotated[int, Path(gt=0)], current_user: CurrentUser, db: SnippetGeneratorDb) -> None:
    delete_category(db, current_user, category_id)


@router.post("/snippets", response_model=SnippetDetailResponse, status_code=status.HTTP_201_CREATED)
def create_snippet_record(payload: SnippetCreateRequest, current_user: CurrentUser, db: SnippetGeneratorDb) -> SnippetDetailResponse:
    return create_snippet(db, current_user, payload)


@router.get("/snippets", response_model=list[SnippetSummaryResponse])
def list_snippet_records(current_user: CurrentUser, db: SnippetGeneratorDb) -> list[SnippetSummaryResponse]:
    return list_snippets(db, current_user)


@router.get("/snippets/{snippet_id}", response_model=SnippetDetailResponse)
def get_snippet_record(snippet_id: Annotated[int, Path(gt=0)], current_user: CurrentUser, db: SnippetGeneratorDb) -> SnippetDetailResponse:
    return get_snippet(db, current_user, snippet_id)


@router.put("/snippets/{snippet_id}", response_model=SnippetDetailResponse)
def update_snippet_record(snippet_id: Annotated[int, Path(gt=0)], payload: SnippetUpdateRequest, current_user: CurrentUser, db: SnippetGeneratorDb) -> SnippetDetailResponse:
    return update_snippet(db, current_user, snippet_id, payload)


@router.delete("/snippets/{snippet_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_snippet_record(snippet_id: Annotated[int, Path(gt=0)], current_user: CurrentUser, db: SnippetGeneratorDb) -> None:
    delete_snippet(db, current_user, snippet_id)


@router.post("/history", response_model=SnippetHistoryDetailResponse, status_code=status.HTTP_201_CREATED)
def create_snippet_history(payload: SnippetHistoryCreateRequest, current_user: CurrentUser, db: SnippetGeneratorDb) -> SnippetHistoryDetailResponse:
    return create_history(db, current_user, payload)


@router.get("/history", response_model=list[SnippetHistorySummaryResponse])
def list_snippet_history(current_user: CurrentUser, db: SnippetGeneratorDb) -> list[SnippetHistorySummaryResponse]:
    return list_history(db, current_user)


@router.get("/history/{history_id}", response_model=SnippetHistoryDetailResponse)
def get_snippet_history(history_id: Annotated[int, Path(gt=0)], current_user: CurrentUser, db: SnippetGeneratorDb) -> SnippetHistoryDetailResponse:
    return get_history(db, current_user, history_id)


@router.put("/history/{history_id}", response_model=SnippetHistoryDetailResponse)
def update_snippet_history(history_id: Annotated[int, Path(gt=0)], payload: SnippetHistoryUpdateRequest, current_user: CurrentUser, db: SnippetGeneratorDb) -> SnippetHistoryDetailResponse:
    return update_history(db, current_user, history_id, payload)


@router.delete("/history/{history_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_snippet_history(history_id: Annotated[int, Path(gt=0)], current_user: CurrentUser, db: SnippetGeneratorDb) -> None:
    delete_history(db, current_user, history_id)
