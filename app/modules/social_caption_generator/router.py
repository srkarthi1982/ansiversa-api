from typing import Annotated

from fastapi import APIRouter, Path, status

from app.modules.social_caption_generator.dependencies import CurrentUser, SocialCaptionGeneratorDb
from app.modules.social_caption_generator.schemas import (
    CaptionHistoryCreateRequest,
    CaptionHistoryDetailResponse,
    CaptionHistorySummaryResponse,
    CaptionHistoryUpdateRequest,
    CaptionProjectCreateRequest,
    CaptionProjectDetailResponse,
    CaptionProjectSummaryResponse,
    CaptionProjectUpdateRequest,
    CaptionTemplateCreateRequest,
    CaptionTemplateDetailResponse,
    CaptionTemplateSummaryResponse,
    CaptionTemplateUpdateRequest,
    SocialCaptionCreateRequest,
    SocialCaptionDetailResponse,
    SocialCaptionGeneratorDashboardResponse,
    SocialCaptionSummaryResponse,
    SocialCaptionUpdateRequest,
)
from app.modules.social_caption_generator.service import (
    create_caption,
    create_history,
    create_project,
    create_template,
    delete_caption,
    delete_history,
    delete_project,
    delete_template,
    get_caption,
    get_dashboard,
    get_history,
    get_project,
    get_template,
    list_captions,
    list_history,
    list_projects,
    list_templates,
    update_caption,
    update_history,
    update_project,
    update_template,
)

router = APIRouter()


@router.get("/dashboard", response_model=SocialCaptionGeneratorDashboardResponse)
def get_social_caption_generator_dashboard(current_user: CurrentUser, db: SocialCaptionGeneratorDb) -> SocialCaptionGeneratorDashboardResponse:
    return get_dashboard(db, current_user)


@router.post("/projects", response_model=CaptionProjectDetailResponse, status_code=status.HTTP_201_CREATED)
def create_caption_project(payload: CaptionProjectCreateRequest, current_user: CurrentUser, db: SocialCaptionGeneratorDb) -> CaptionProjectDetailResponse:
    return create_project(db, current_user, payload)


@router.get("/projects", response_model=list[CaptionProjectSummaryResponse])
def list_caption_projects(current_user: CurrentUser, db: SocialCaptionGeneratorDb) -> list[CaptionProjectSummaryResponse]:
    return list_projects(db, current_user)


@router.get("/projects/{project_id}", response_model=CaptionProjectDetailResponse)
def get_caption_project(project_id: Annotated[int, Path(gt=0)], current_user: CurrentUser, db: SocialCaptionGeneratorDb) -> CaptionProjectDetailResponse:
    return get_project(db, current_user, project_id)


@router.put("/projects/{project_id}", response_model=CaptionProjectDetailResponse)
def update_caption_project(project_id: Annotated[int, Path(gt=0)], payload: CaptionProjectUpdateRequest, current_user: CurrentUser, db: SocialCaptionGeneratorDb) -> CaptionProjectDetailResponse:
    return update_project(db, current_user, project_id, payload)


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_caption_project(project_id: Annotated[int, Path(gt=0)], current_user: CurrentUser, db: SocialCaptionGeneratorDb) -> None:
    delete_project(db, current_user, project_id)


@router.post("/captions", response_model=SocialCaptionDetailResponse, status_code=status.HTTP_201_CREATED)
def create_social_caption(payload: SocialCaptionCreateRequest, current_user: CurrentUser, db: SocialCaptionGeneratorDb) -> SocialCaptionDetailResponse:
    return create_caption(db, current_user, payload)


@router.get("/captions", response_model=list[SocialCaptionSummaryResponse])
def list_social_captions(current_user: CurrentUser, db: SocialCaptionGeneratorDb) -> list[SocialCaptionSummaryResponse]:
    return list_captions(db, current_user)


@router.get("/captions/{caption_id}", response_model=SocialCaptionDetailResponse)
def get_social_caption(caption_id: Annotated[int, Path(gt=0)], current_user: CurrentUser, db: SocialCaptionGeneratorDb) -> SocialCaptionDetailResponse:
    return get_caption(db, current_user, caption_id)


@router.put("/captions/{caption_id}", response_model=SocialCaptionDetailResponse)
def update_social_caption(caption_id: Annotated[int, Path(gt=0)], payload: SocialCaptionUpdateRequest, current_user: CurrentUser, db: SocialCaptionGeneratorDb) -> SocialCaptionDetailResponse:
    return update_caption(db, current_user, caption_id, payload)


@router.delete("/captions/{caption_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_social_caption(caption_id: Annotated[int, Path(gt=0)], current_user: CurrentUser, db: SocialCaptionGeneratorDb) -> None:
    delete_caption(db, current_user, caption_id)


@router.post("/templates", response_model=CaptionTemplateDetailResponse, status_code=status.HTTP_201_CREATED)
def create_caption_template(payload: CaptionTemplateCreateRequest, current_user: CurrentUser, db: SocialCaptionGeneratorDb) -> CaptionTemplateDetailResponse:
    return create_template(db, current_user, payload)


@router.get("/templates", response_model=list[CaptionTemplateSummaryResponse])
def list_caption_templates(current_user: CurrentUser, db: SocialCaptionGeneratorDb) -> list[CaptionTemplateSummaryResponse]:
    return list_templates(db, current_user)


@router.get("/templates/{template_id}", response_model=CaptionTemplateDetailResponse)
def get_caption_template(template_id: Annotated[int, Path(gt=0)], current_user: CurrentUser, db: SocialCaptionGeneratorDb) -> CaptionTemplateDetailResponse:
    return get_template(db, current_user, template_id)


@router.put("/templates/{template_id}", response_model=CaptionTemplateDetailResponse)
def update_caption_template(template_id: Annotated[int, Path(gt=0)], payload: CaptionTemplateUpdateRequest, current_user: CurrentUser, db: SocialCaptionGeneratorDb) -> CaptionTemplateDetailResponse:
    return update_template(db, current_user, template_id, payload)


@router.delete("/templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_caption_template(template_id: Annotated[int, Path(gt=0)], current_user: CurrentUser, db: SocialCaptionGeneratorDb) -> None:
    delete_template(db, current_user, template_id)


@router.post("/history", response_model=CaptionHistoryDetailResponse, status_code=status.HTTP_201_CREATED)
def create_caption_history(payload: CaptionHistoryCreateRequest, current_user: CurrentUser, db: SocialCaptionGeneratorDb) -> CaptionHistoryDetailResponse:
    return create_history(db, current_user, payload)


@router.get("/history", response_model=list[CaptionHistorySummaryResponse])
def list_caption_history(current_user: CurrentUser, db: SocialCaptionGeneratorDb) -> list[CaptionHistorySummaryResponse]:
    return list_history(db, current_user)


@router.get("/history/{history_id}", response_model=CaptionHistoryDetailResponse)
def get_caption_history(history_id: Annotated[int, Path(gt=0)], current_user: CurrentUser, db: SocialCaptionGeneratorDb) -> CaptionHistoryDetailResponse:
    return get_history(db, current_user, history_id)


@router.put("/history/{history_id}", response_model=CaptionHistoryDetailResponse)
def update_caption_history(history_id: Annotated[int, Path(gt=0)], payload: CaptionHistoryUpdateRequest, current_user: CurrentUser, db: SocialCaptionGeneratorDb) -> CaptionHistoryDetailResponse:
    return update_history(db, current_user, history_id, payload)


@router.delete("/history/{history_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_caption_history(history_id: Annotated[int, Path(gt=0)], current_user: CurrentUser, db: SocialCaptionGeneratorDb) -> None:
    delete_history(db, current_user, history_id)
