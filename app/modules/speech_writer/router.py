from typing import Annotated

from fastapi import APIRouter, Path, status

from app.modules.speech_writer.dependencies import CurrentUser, SpeechWriterDb
from app.modules.speech_writer.schemas import (
    SpeechHistoryCreateRequest,
    SpeechHistoryDetailResponse,
    SpeechHistorySummaryResponse,
    SpeechHistoryUpdateRequest,
    SpeechProjectCreateRequest,
    SpeechProjectDetailResponse,
    SpeechProjectSummaryResponse,
    SpeechProjectUpdateRequest,
    SpeechTemplateCreateRequest,
    SpeechTemplateDetailResponse,
    SpeechTemplateSummaryResponse,
    SpeechTemplateUpdateRequest,
    SpeechCreateRequest,
    SpeechDetailResponse,
    SpeechWriterDashboardResponse,
    SpeechSummaryResponse,
    SpeechUpdateRequest,
)
from app.modules.speech_writer.service import (
    create_speech,
    create_history,
    create_project,
    create_template,
    delete_speech,
    delete_history,
    delete_project,
    delete_template,
    get_speech,
    get_dashboard,
    get_history,
    get_project,
    get_template,
    list_speeches,
    list_history,
    list_projects,
    list_templates,
    update_speech,
    update_history,
    update_project,
    update_template,
)

router = APIRouter()


@router.get("/dashboard", response_model=SpeechWriterDashboardResponse)
def get_speech_writer_dashboard(current_user: CurrentUser, db: SpeechWriterDb) -> SpeechWriterDashboardResponse:
    return get_dashboard(db, current_user)


@router.post("/projects", response_model=SpeechProjectDetailResponse, status_code=status.HTTP_201_CREATED)
def create_speech_project(payload: SpeechProjectCreateRequest, current_user: CurrentUser, db: SpeechWriterDb) -> SpeechProjectDetailResponse:
    return create_project(db, current_user, payload)


@router.get("/projects", response_model=list[SpeechProjectSummaryResponse])
def list_speech_projects(current_user: CurrentUser, db: SpeechWriterDb) -> list[SpeechProjectSummaryResponse]:
    return list_projects(db, current_user)


@router.get("/projects/{project_id}", response_model=SpeechProjectDetailResponse)
def get_speech_project(project_id: Annotated[int, Path(gt=0)], current_user: CurrentUser, db: SpeechWriterDb) -> SpeechProjectDetailResponse:
    return get_project(db, current_user, project_id)


@router.put("/projects/{project_id}", response_model=SpeechProjectDetailResponse)
def update_speech_project(project_id: Annotated[int, Path(gt=0)], payload: SpeechProjectUpdateRequest, current_user: CurrentUser, db: SpeechWriterDb) -> SpeechProjectDetailResponse:
    return update_project(db, current_user, project_id, payload)


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_speech_project(project_id: Annotated[int, Path(gt=0)], current_user: CurrentUser, db: SpeechWriterDb) -> None:
    delete_project(db, current_user, project_id)


@router.post("/speeches", response_model=SpeechDetailResponse, status_code=status.HTTP_201_CREATED)
def create_speech_record(payload: SpeechCreateRequest, current_user: CurrentUser, db: SpeechWriterDb) -> SpeechDetailResponse:
    return create_speech(db, current_user, payload)


@router.get("/speeches", response_model=list[SpeechSummaryResponse])
def list_speech_records(current_user: CurrentUser, db: SpeechWriterDb) -> list[SpeechSummaryResponse]:
    return list_speeches(db, current_user)


@router.get("/speeches/{speech_id}", response_model=SpeechDetailResponse)
def get_speech_record(speech_id: Annotated[int, Path(gt=0)], current_user: CurrentUser, db: SpeechWriterDb) -> SpeechDetailResponse:
    return get_speech(db, current_user, speech_id)


@router.put("/speeches/{speech_id}", response_model=SpeechDetailResponse)
def update_speech_record(speech_id: Annotated[int, Path(gt=0)], payload: SpeechUpdateRequest, current_user: CurrentUser, db: SpeechWriterDb) -> SpeechDetailResponse:
    return update_speech(db, current_user, speech_id, payload)


@router.delete("/speeches/{speech_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_speech_record(speech_id: Annotated[int, Path(gt=0)], current_user: CurrentUser, db: SpeechWriterDb) -> None:
    delete_speech(db, current_user, speech_id)


@router.post("/templates", response_model=SpeechTemplateDetailResponse, status_code=status.HTTP_201_CREATED)
def create_speech_template(payload: SpeechTemplateCreateRequest, current_user: CurrentUser, db: SpeechWriterDb) -> SpeechTemplateDetailResponse:
    return create_template(db, current_user, payload)


@router.get("/templates", response_model=list[SpeechTemplateSummaryResponse])
def list_speech_templates(current_user: CurrentUser, db: SpeechWriterDb) -> list[SpeechTemplateSummaryResponse]:
    return list_templates(db, current_user)


@router.get("/templates/{template_id}", response_model=SpeechTemplateDetailResponse)
def get_speech_template(template_id: Annotated[int, Path(gt=0)], current_user: CurrentUser, db: SpeechWriterDb) -> SpeechTemplateDetailResponse:
    return get_template(db, current_user, template_id)


@router.put("/templates/{template_id}", response_model=SpeechTemplateDetailResponse)
def update_speech_template(template_id: Annotated[int, Path(gt=0)], payload: SpeechTemplateUpdateRequest, current_user: CurrentUser, db: SpeechWriterDb) -> SpeechTemplateDetailResponse:
    return update_template(db, current_user, template_id, payload)


@router.delete("/templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_speech_template(template_id: Annotated[int, Path(gt=0)], current_user: CurrentUser, db: SpeechWriterDb) -> None:
    delete_template(db, current_user, template_id)


@router.post("/history", response_model=SpeechHistoryDetailResponse, status_code=status.HTTP_201_CREATED)
def create_speech_history(payload: SpeechHistoryCreateRequest, current_user: CurrentUser, db: SpeechWriterDb) -> SpeechHistoryDetailResponse:
    return create_history(db, current_user, payload)


@router.get("/history", response_model=list[SpeechHistorySummaryResponse])
def list_speech_history(current_user: CurrentUser, db: SpeechWriterDb) -> list[SpeechHistorySummaryResponse]:
    return list_history(db, current_user)


@router.get("/history/{history_id}", response_model=SpeechHistoryDetailResponse)
def get_speech_history(history_id: Annotated[int, Path(gt=0)], current_user: CurrentUser, db: SpeechWriterDb) -> SpeechHistoryDetailResponse:
    return get_history(db, current_user, history_id)


@router.put("/history/{history_id}", response_model=SpeechHistoryDetailResponse)
def update_speech_history(history_id: Annotated[int, Path(gt=0)], payload: SpeechHistoryUpdateRequest, current_user: CurrentUser, db: SpeechWriterDb) -> SpeechHistoryDetailResponse:
    return update_history(db, current_user, history_id, payload)


@router.delete("/history/{history_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_speech_history(history_id: Annotated[int, Path(gt=0)], current_user: CurrentUser, db: SpeechWriterDb) -> None:
    delete_history(db, current_user, history_id)
