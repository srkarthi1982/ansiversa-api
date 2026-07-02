from typing import Annotated

from fastapi import APIRouter, Path, status

from app.modules.grammar_and_paraphrasing_assistant.dependencies import CurrentUser, GrammarAndParaphrasingAssistantDb
from app.modules.grammar_and_paraphrasing_assistant.schemas import (
    GrammarAndParaphrasingDashboardResponse,
    GrammarJobResponse,
    GrammarProjectCreateRequest,
    GrammarProjectDetailResponse,
    GrammarProjectSummaryResponse,
    GrammarProjectUpdateRequest,
    GrammarResultDetailResponse,
    GrammarResultSummaryResponse,
    GrammarRunRequest,
    GrammarRunResponse,
)
from app.modules.grammar_and_paraphrasing_assistant.service import (
    create_project,
    delete_project,
    get_dashboard,
    get_project,
    get_result,
    list_history,
    list_projects,
    list_results,
    run_project,
    update_project,
)

router = APIRouter()


@router.get("/dashboard", response_model=GrammarAndParaphrasingDashboardResponse)
def get_grammar_dashboard(current_user: CurrentUser, db: GrammarAndParaphrasingAssistantDb) -> GrammarAndParaphrasingDashboardResponse:
    return get_dashboard(db, current_user)


@router.post("/projects", response_model=GrammarProjectDetailResponse, status_code=status.HTTP_201_CREATED)
def create_grammar_project(payload: GrammarProjectCreateRequest, current_user: CurrentUser, db: GrammarAndParaphrasingAssistantDb) -> GrammarProjectDetailResponse:
    return create_project(db, current_user, payload)


@router.get("/projects", response_model=list[GrammarProjectSummaryResponse])
def list_grammar_projects(current_user: CurrentUser, db: GrammarAndParaphrasingAssistantDb) -> list[GrammarProjectSummaryResponse]:
    return list_projects(db, current_user)


@router.get("/projects/{project_id}", response_model=GrammarProjectDetailResponse)
def get_grammar_project(project_id: Annotated[int, Path(gt=0)], current_user: CurrentUser, db: GrammarAndParaphrasingAssistantDb) -> GrammarProjectDetailResponse:
    return get_project(db, current_user, project_id)


@router.put("/projects/{project_id}", response_model=GrammarProjectDetailResponse)
def update_grammar_project(project_id: Annotated[int, Path(gt=0)], payload: GrammarProjectUpdateRequest, current_user: CurrentUser, db: GrammarAndParaphrasingAssistantDb) -> GrammarProjectDetailResponse:
    return update_project(db, current_user, project_id, payload)


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_grammar_project(project_id: Annotated[int, Path(gt=0)], current_user: CurrentUser, db: GrammarAndParaphrasingAssistantDb) -> None:
    delete_project(db, current_user, project_id)


@router.post("/projects/{project_id}/run", response_model=GrammarRunResponse, status_code=status.HTTP_201_CREATED)
def run_grammar_project(project_id: Annotated[int, Path(gt=0)], payload: GrammarRunRequest, current_user: CurrentUser, db: GrammarAndParaphrasingAssistantDb) -> GrammarRunResponse:
    return run_project(db, current_user, project_id, payload)


@router.get("/results", response_model=list[GrammarResultSummaryResponse])
def list_grammar_results(current_user: CurrentUser, db: GrammarAndParaphrasingAssistantDb) -> list[GrammarResultSummaryResponse]:
    return list_results(db, current_user)


@router.get("/results/{result_id}", response_model=GrammarResultDetailResponse)
def get_grammar_result(result_id: Annotated[int, Path(gt=0)], current_user: CurrentUser, db: GrammarAndParaphrasingAssistantDb) -> GrammarResultDetailResponse:
    return get_result(db, current_user, result_id)


@router.get("/history", response_model=list[GrammarJobResponse])
def list_grammar_history(current_user: CurrentUser, db: GrammarAndParaphrasingAssistantDb) -> list[GrammarJobResponse]:
    return list_history(db, current_user)
