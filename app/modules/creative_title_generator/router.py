from typing import Annotated

from fastapi import APIRouter, Path, status

from app.modules.creative_title_generator.dependencies import CurrentUser, CreativeTitleGeneratorDb
from app.modules.creative_title_generator.schemas import (
    CreativeTitleGeneratorDashboardResponse,
    GeneratedTitleDetailResponse,
    GeneratedTitleSummaryResponse,
    TitleGenerateRequest,
    TitleGenerationResponse,
    TitleJobResponse,
    TitleProjectCreateRequest,
    TitleProjectDetailResponse,
    TitleProjectSummaryResponse,
    TitleProjectUpdateRequest,
)
from app.modules.creative_title_generator.service import (
    create_project,
    delete_project,
    generate_titles,
    get_dashboard,
    get_generated_title,
    get_project,
    list_generated_titles,
    list_history,
    list_projects,
    update_project,
)

router = APIRouter()


@router.get("/dashboard", response_model=CreativeTitleGeneratorDashboardResponse)
def get_creative_title_dashboard(current_user: CurrentUser, db: CreativeTitleGeneratorDb) -> CreativeTitleGeneratorDashboardResponse:
    return get_dashboard(db, current_user)


@router.post("/projects", response_model=TitleProjectDetailResponse, status_code=status.HTTP_201_CREATED)
def create_title_project(payload: TitleProjectCreateRequest, current_user: CurrentUser, db: CreativeTitleGeneratorDb) -> TitleProjectDetailResponse:
    return create_project(db, current_user, payload)


@router.get("/projects", response_model=list[TitleProjectSummaryResponse])
def list_title_projects(current_user: CurrentUser, db: CreativeTitleGeneratorDb) -> list[TitleProjectSummaryResponse]:
    return list_projects(db, current_user)


@router.get("/projects/{project_id}", response_model=TitleProjectDetailResponse)
def get_title_project(project_id: Annotated[int, Path(gt=0)], current_user: CurrentUser, db: CreativeTitleGeneratorDb) -> TitleProjectDetailResponse:
    return get_project(db, current_user, project_id)


@router.put("/projects/{project_id}", response_model=TitleProjectDetailResponse)
def update_title_project(project_id: Annotated[int, Path(gt=0)], payload: TitleProjectUpdateRequest, current_user: CurrentUser, db: CreativeTitleGeneratorDb) -> TitleProjectDetailResponse:
    return update_project(db, current_user, project_id, payload)


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_title_project(project_id: Annotated[int, Path(gt=0)], current_user: CurrentUser, db: CreativeTitleGeneratorDb) -> None:
    delete_project(db, current_user, project_id)


@router.post("/projects/{project_id}/generate", response_model=TitleGenerationResponse, status_code=status.HTTP_201_CREATED)
def generate_project_titles(project_id: Annotated[int, Path(gt=0)], payload: TitleGenerateRequest, current_user: CurrentUser, db: CreativeTitleGeneratorDb) -> TitleGenerationResponse:
    return generate_titles(db, current_user, project_id, payload)


@router.get("/titles", response_model=list[GeneratedTitleSummaryResponse])
def list_titles(current_user: CurrentUser, db: CreativeTitleGeneratorDb) -> list[GeneratedTitleSummaryResponse]:
    return list_generated_titles(db, current_user)


@router.get("/titles/{generated_title_id}", response_model=GeneratedTitleDetailResponse)
def get_title(generated_title_id: Annotated[int, Path(gt=0)], current_user: CurrentUser, db: CreativeTitleGeneratorDb) -> GeneratedTitleDetailResponse:
    return get_generated_title(db, current_user, generated_title_id)


@router.get("/history", response_model=list[TitleJobResponse])
def list_title_history(current_user: CurrentUser, db: CreativeTitleGeneratorDb) -> list[TitleJobResponse]:
    return list_history(db, current_user)
