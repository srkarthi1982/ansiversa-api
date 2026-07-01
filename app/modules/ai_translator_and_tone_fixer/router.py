from typing import Annotated

from fastapi import APIRouter, Path, status

from app.modules.ai_translator_and_tone_fixer.dependencies import CurrentUser, AiTranslatorAndToneFixerDb
from app.modules.ai_translator_and_tone_fixer.schemas import (
    AiTranslatorAndToneFixerDashboardResponse,
    TranslationCreateRequest,
    TranslationDetailResponse,
    TranslationHistoryCreateRequest,
    TranslationHistoryDetailResponse,
    TranslationHistorySummaryResponse,
    TranslationHistoryUpdateRequest,
    TranslationProjectCreateRequest,
    TranslationProjectDetailResponse,
    TranslationProjectSummaryResponse,
    TranslationProjectUpdateRequest,
    TranslationSummaryResponse,
    TranslationTemplateCreateRequest,
    TranslationTemplateDetailResponse,
    TranslationTemplateSummaryResponse,
    TranslationTemplateUpdateRequest,
    TranslationUpdateRequest,
)
from app.modules.ai_translator_and_tone_fixer.service import (
    create_history,
    create_project,
    create_translation,
    create_template,
    delete_history,
    delete_project,
    delete_translation,
    delete_template,
    get_dashboard,
    get_history,
    get_project,
    get_translation,
    get_template,
    list_history,
    list_projects,
    list_translations,
    list_templates,
    update_history,
    update_project,
    update_translation,
    update_template,
)

router = APIRouter()


@router.get("/dashboard", response_model=AiTranslatorAndToneFixerDashboardResponse)
def get_ai_translator_and_tone_fixer_dashboard(current_user: CurrentUser, db: AiTranslatorAndToneFixerDb) -> AiTranslatorAndToneFixerDashboardResponse:
    return get_dashboard(db, current_user)


@router.post("/projects", response_model=TranslationProjectDetailResponse, status_code=status.HTTP_201_CREATED)
def create_translation_project(payload: TranslationProjectCreateRequest, current_user: CurrentUser, db: AiTranslatorAndToneFixerDb) -> TranslationProjectDetailResponse:
    return create_project(db, current_user, payload)


@router.get("/projects", response_model=list[TranslationProjectSummaryResponse])
def list_translation_projects(current_user: CurrentUser, db: AiTranslatorAndToneFixerDb) -> list[TranslationProjectSummaryResponse]:
    return list_projects(db, current_user)


@router.get("/projects/{project_id}", response_model=TranslationProjectDetailResponse)
def get_translation_project(project_id: Annotated[int, Path(gt=0)], current_user: CurrentUser, db: AiTranslatorAndToneFixerDb) -> TranslationProjectDetailResponse:
    return get_project(db, current_user, project_id)


@router.put("/projects/{project_id}", response_model=TranslationProjectDetailResponse)
def update_translation_project(project_id: Annotated[int, Path(gt=0)], payload: TranslationProjectUpdateRequest, current_user: CurrentUser, db: AiTranslatorAndToneFixerDb) -> TranslationProjectDetailResponse:
    return update_project(db, current_user, project_id, payload)


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_translation_project(project_id: Annotated[int, Path(gt=0)], current_user: CurrentUser, db: AiTranslatorAndToneFixerDb) -> None:
    delete_project(db, current_user, project_id)


@router.post("/translations", response_model=TranslationDetailResponse, status_code=status.HTTP_201_CREATED)
def create_translation_record(payload: TranslationCreateRequest, current_user: CurrentUser, db: AiTranslatorAndToneFixerDb) -> TranslationDetailResponse:
    return create_translation(db, current_user, payload)


@router.get("/translations", response_model=list[TranslationSummaryResponse])
def list_translation_records(current_user: CurrentUser, db: AiTranslatorAndToneFixerDb) -> list[TranslationSummaryResponse]:
    return list_translations(db, current_user)


@router.get("/translations/{translation_id}", response_model=TranslationDetailResponse)
def get_translation_record(translation_id: Annotated[int, Path(gt=0)], current_user: CurrentUser, db: AiTranslatorAndToneFixerDb) -> TranslationDetailResponse:
    return get_translation(db, current_user, translation_id)


@router.put("/translations/{translation_id}", response_model=TranslationDetailResponse)
def update_translation_record(translation_id: Annotated[int, Path(gt=0)], payload: TranslationUpdateRequest, current_user: CurrentUser, db: AiTranslatorAndToneFixerDb) -> TranslationDetailResponse:
    return update_translation(db, current_user, translation_id, payload)


@router.delete("/translations/{translation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_translation_record(translation_id: Annotated[int, Path(gt=0)], current_user: CurrentUser, db: AiTranslatorAndToneFixerDb) -> None:
    delete_translation(db, current_user, translation_id)


@router.post("/templates", response_model=TranslationTemplateDetailResponse, status_code=status.HTTP_201_CREATED)
def create_translation_template(payload: TranslationTemplateCreateRequest, current_user: CurrentUser, db: AiTranslatorAndToneFixerDb) -> TranslationTemplateDetailResponse:
    return create_template(db, current_user, payload)


@router.get("/templates", response_model=list[TranslationTemplateSummaryResponse])
def list_translation_templates(current_user: CurrentUser, db: AiTranslatorAndToneFixerDb) -> list[TranslationTemplateSummaryResponse]:
    return list_templates(db, current_user)


@router.get("/templates/{template_id}", response_model=TranslationTemplateDetailResponse)
def get_translation_template(template_id: Annotated[int, Path(gt=0)], current_user: CurrentUser, db: AiTranslatorAndToneFixerDb) -> TranslationTemplateDetailResponse:
    return get_template(db, current_user, template_id)


@router.put("/templates/{template_id}", response_model=TranslationTemplateDetailResponse)
def update_translation_template(template_id: Annotated[int, Path(gt=0)], payload: TranslationTemplateUpdateRequest, current_user: CurrentUser, db: AiTranslatorAndToneFixerDb) -> TranslationTemplateDetailResponse:
    return update_template(db, current_user, template_id, payload)


@router.delete("/templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_translation_template(template_id: Annotated[int, Path(gt=0)], current_user: CurrentUser, db: AiTranslatorAndToneFixerDb) -> None:
    delete_template(db, current_user, template_id)


@router.post("/history", response_model=TranslationHistoryDetailResponse, status_code=status.HTTP_201_CREATED)
def create_translation_history(payload: TranslationHistoryCreateRequest, current_user: CurrentUser, db: AiTranslatorAndToneFixerDb) -> TranslationHistoryDetailResponse:
    return create_history(db, current_user, payload)


@router.get("/history", response_model=list[TranslationHistorySummaryResponse])
def list_translation_history(current_user: CurrentUser, db: AiTranslatorAndToneFixerDb) -> list[TranslationHistorySummaryResponse]:
    return list_history(db, current_user)


@router.get("/history/{history_id}", response_model=TranslationHistoryDetailResponse)
def get_translation_history(history_id: Annotated[int, Path(gt=0)], current_user: CurrentUser, db: AiTranslatorAndToneFixerDb) -> TranslationHistoryDetailResponse:
    return get_history(db, current_user, history_id)


@router.put("/history/{history_id}", response_model=TranslationHistoryDetailResponse)
def update_translation_history(history_id: Annotated[int, Path(gt=0)], payload: TranslationHistoryUpdateRequest, current_user: CurrentUser, db: AiTranslatorAndToneFixerDb) -> TranslationHistoryDetailResponse:
    return update_history(db, current_user, history_id, payload)


@router.delete("/history/{history_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_translation_history(history_id: Annotated[int, Path(gt=0)], current_user: CurrentUser, db: AiTranslatorAndToneFixerDb) -> None:
    delete_history(db, current_user, history_id)
