from typing import Annotated

from fastapi import APIRouter, Path, status

from app.modules.prompt_builder.dependencies import CurrentUser, PromptBuilderDb
from app.modules.prompt_builder.schemas import (
    PromptBuilderDashboardResponse,
    PromptCreateRequest,
    PromptDetailResponse,
    PromptHistoryCreateRequest,
    PromptHistoryDetailResponse,
    PromptHistorySummaryResponse,
    PromptHistoryUpdateRequest,
    PromptProjectCreateRequest,
    PromptProjectDetailResponse,
    PromptProjectSummaryResponse,
    PromptProjectUpdateRequest,
    PromptSummaryResponse,
    PromptTemplateCreateRequest,
    PromptTemplateDetailResponse,
    PromptTemplateSummaryResponse,
    PromptTemplateUpdateRequest,
    PromptUpdateRequest,
)
from app.modules.prompt_builder.service import (
    create_history,
    create_project,
    create_prompt,
    create_template,
    delete_history,
    delete_project,
    delete_prompt,
    delete_template,
    get_dashboard,
    get_history,
    get_project,
    get_prompt,
    get_template,
    list_history,
    list_projects,
    list_prompts,
    list_templates,
    update_history,
    update_project,
    update_prompt,
    update_template,
)

router = APIRouter()


@router.get("/dashboard", response_model=PromptBuilderDashboardResponse)
def get_prompt_builder_dashboard(current_user: CurrentUser, db: PromptBuilderDb) -> PromptBuilderDashboardResponse:
    return get_dashboard(db, current_user)


@router.post("/projects", response_model=PromptProjectDetailResponse, status_code=status.HTTP_201_CREATED)
def create_prompt_project(payload: PromptProjectCreateRequest, current_user: CurrentUser, db: PromptBuilderDb) -> PromptProjectDetailResponse:
    return create_project(db, current_user, payload)


@router.get("/projects", response_model=list[PromptProjectSummaryResponse])
def list_prompt_projects(current_user: CurrentUser, db: PromptBuilderDb) -> list[PromptProjectSummaryResponse]:
    return list_projects(db, current_user)


@router.get("/projects/{project_id}", response_model=PromptProjectDetailResponse)
def get_prompt_project(project_id: Annotated[int, Path(gt=0)], current_user: CurrentUser, db: PromptBuilderDb) -> PromptProjectDetailResponse:
    return get_project(db, current_user, project_id)


@router.put("/projects/{project_id}", response_model=PromptProjectDetailResponse)
def update_prompt_project(project_id: Annotated[int, Path(gt=0)], payload: PromptProjectUpdateRequest, current_user: CurrentUser, db: PromptBuilderDb) -> PromptProjectDetailResponse:
    return update_project(db, current_user, project_id, payload)


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_prompt_project(project_id: Annotated[int, Path(gt=0)], current_user: CurrentUser, db: PromptBuilderDb) -> None:
    delete_project(db, current_user, project_id)


@router.post("/prompts", response_model=PromptDetailResponse, status_code=status.HTTP_201_CREATED)
def create_prompt_record(payload: PromptCreateRequest, current_user: CurrentUser, db: PromptBuilderDb) -> PromptDetailResponse:
    return create_prompt(db, current_user, payload)


@router.get("/prompts", response_model=list[PromptSummaryResponse])
def list_prompt_records(current_user: CurrentUser, db: PromptBuilderDb) -> list[PromptSummaryResponse]:
    return list_prompts(db, current_user)


@router.get("/prompts/{prompt_id}", response_model=PromptDetailResponse)
def get_prompt_record(prompt_id: Annotated[int, Path(gt=0)], current_user: CurrentUser, db: PromptBuilderDb) -> PromptDetailResponse:
    return get_prompt(db, current_user, prompt_id)


@router.put("/prompts/{prompt_id}", response_model=PromptDetailResponse)
def update_prompt_record(prompt_id: Annotated[int, Path(gt=0)], payload: PromptUpdateRequest, current_user: CurrentUser, db: PromptBuilderDb) -> PromptDetailResponse:
    return update_prompt(db, current_user, prompt_id, payload)


@router.delete("/prompts/{prompt_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_prompt_record(prompt_id: Annotated[int, Path(gt=0)], current_user: CurrentUser, db: PromptBuilderDb) -> None:
    delete_prompt(db, current_user, prompt_id)


@router.post("/templates", response_model=PromptTemplateDetailResponse, status_code=status.HTTP_201_CREATED)
def create_prompt_template(payload: PromptTemplateCreateRequest, current_user: CurrentUser, db: PromptBuilderDb) -> PromptTemplateDetailResponse:
    return create_template(db, current_user, payload)


@router.get("/templates", response_model=list[PromptTemplateSummaryResponse])
def list_prompt_templates(current_user: CurrentUser, db: PromptBuilderDb) -> list[PromptTemplateSummaryResponse]:
    return list_templates(db, current_user)


@router.get("/templates/{template_id}", response_model=PromptTemplateDetailResponse)
def get_prompt_template(template_id: Annotated[int, Path(gt=0)], current_user: CurrentUser, db: PromptBuilderDb) -> PromptTemplateDetailResponse:
    return get_template(db, current_user, template_id)


@router.put("/templates/{template_id}", response_model=PromptTemplateDetailResponse)
def update_prompt_template(template_id: Annotated[int, Path(gt=0)], payload: PromptTemplateUpdateRequest, current_user: CurrentUser, db: PromptBuilderDb) -> PromptTemplateDetailResponse:
    return update_template(db, current_user, template_id, payload)


@router.delete("/templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_prompt_template(template_id: Annotated[int, Path(gt=0)], current_user: CurrentUser, db: PromptBuilderDb) -> None:
    delete_template(db, current_user, template_id)


@router.post("/history", response_model=PromptHistoryDetailResponse, status_code=status.HTTP_201_CREATED)
def create_prompt_history(payload: PromptHistoryCreateRequest, current_user: CurrentUser, db: PromptBuilderDb) -> PromptHistoryDetailResponse:
    return create_history(db, current_user, payload)


@router.get("/history", response_model=list[PromptHistorySummaryResponse])
def list_prompt_history(current_user: CurrentUser, db: PromptBuilderDb) -> list[PromptHistorySummaryResponse]:
    return list_history(db, current_user)


@router.get("/history/{history_id}", response_model=PromptHistoryDetailResponse)
def get_prompt_history(history_id: Annotated[int, Path(gt=0)], current_user: CurrentUser, db: PromptBuilderDb) -> PromptHistoryDetailResponse:
    return get_history(db, current_user, history_id)


@router.put("/history/{history_id}", response_model=PromptHistoryDetailResponse)
def update_prompt_history(history_id: Annotated[int, Path(gt=0)], payload: PromptHistoryUpdateRequest, current_user: CurrentUser, db: PromptBuilderDb) -> PromptHistoryDetailResponse:
    return update_history(db, current_user, history_id, payload)


@router.delete("/history/{history_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_prompt_history(history_id: Annotated[int, Path(gt=0)], current_user: CurrentUser, db: PromptBuilderDb) -> None:
    delete_history(db, current_user, history_id)
