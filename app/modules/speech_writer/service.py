from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.speech_writer import repository
from app.modules.speech_writer.models import SpeechHistory, SpeechProject, SpeechTemplate, Speech
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

PREVIEW_LENGTH = 220


def _preview(value: str | None) -> str | None:
    if not value:
        return None
    if len(value) <= PREVIEW_LENGTH:
        return value
    return f"{value[:PREVIEW_LENGTH].rstrip()}..."


def _not_found(detail: str) -> None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def _get_owned_project(db: Session, user: User, project_id: int) -> SpeechProject:
    project = repository.get_project(db, project_id)
    if not project or project.owner_id != user.id:
        _not_found("Speech project was not found.")
    return project


def _get_owned_speech(db: Session, user: User, speech_id: int) -> Speech:
    speech = repository.get_speech(db, speech_id)
    if not speech or speech.owner_id != user.id:
        _not_found("Speech was not found.")
    return speech


def _get_owned_template(db: Session, user: User, template_id: int) -> SpeechTemplate:
    template = repository.get_template(db, template_id)
    if not template or template.owner_id != user.id:
        _not_found("Speech template was not found.")
    return template


def _get_owned_history(db: Session, user: User, history_id: int) -> SpeechHistory:
    history = repository.get_history(db, history_id)
    if not history or history.owner_id != user.id:
        _not_found("Speech history record was not found.")
    return history


def _project_summary_response(db: Session, project: SpeechProject) -> SpeechProjectSummaryResponse:
    return SpeechProjectSummaryResponse(
        id=project.id,
        platform_id=project.platform_id,
        title=project.title,
        occasion=project.occasion,
        event_date=project.event_date,
        audience=project.audience,
        tone=project.tone,
        status=project.status,
        purpose_preview=_preview(project.purpose),
        speech_count=repository.count_speeches(db, project.id),
        template_count=repository.count_templates(db, project.id),
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


def _project_detail_response(db: Session, project: SpeechProject) -> SpeechProjectDetailResponse:
    item = _project_summary_response(db, project)
    return SpeechProjectDetailResponse(
        **item.model_dump(),
        purpose=project.purpose,
        notes=project.notes,
    )


def _speech_summary_response(db: Session, speech: Speech, project_title: str) -> SpeechSummaryResponse:
    return SpeechSummaryResponse(
        id=speech.id,
        platform_id=speech.platform_id,
        project_id=speech.project_id,
        project_title=project_title,
        title=speech.title,
        speaker_name=speech.speaker_name,
        occasion=speech.occasion,
        duration_minutes=speech.duration_minutes,
        status=speech.status,
        key_message_preview=_preview(speech.key_message),
        speech_preview=_preview(speech.speech_text),
        history_count=repository.count_history(db, speech.id),
        created_at=speech.created_at,
        updated_at=speech.updated_at,
    )


def _speech_detail_response(db: Session, speech: Speech, project_title: str) -> SpeechDetailResponse:
    item = _speech_summary_response(db, speech, project_title)
    return SpeechDetailResponse(
        **item.model_dump(),
        key_message=speech.key_message,
        speech_text=speech.speech_text,
    )


def _template_summary_response(template: SpeechTemplate, project_title: str) -> SpeechTemplateSummaryResponse:
    return SpeechTemplateSummaryResponse(
        id=template.id,
        platform_id=template.platform_id,
        project_id=template.project_id,
        project_title=project_title,
        title=template.title,
        occasion=template.occasion,
        tone=template.tone,
        template_preview=_preview(template.template_text),
        usage_notes_preview=_preview(template.usage_notes),
        created_at=template.created_at,
        updated_at=template.updated_at,
    )


def _template_detail_response(template: SpeechTemplate, project_title: str) -> SpeechTemplateDetailResponse:
    item = _template_summary_response(template, project_title)
    return SpeechTemplateDetailResponse(
        **item.model_dump(),
        template_text=template.template_text,
        usage_notes=template.usage_notes,
    )


def _history_summary_response(history: SpeechHistory, speech_title: str) -> SpeechHistorySummaryResponse:
    return SpeechHistorySummaryResponse(
        id=history.id,
        platform_id=history.platform_id,
        speech_id=history.speech_id,
        speech_title=speech_title,
        title=history.title,
        event_type=history.event_type,
        occurred_at=history.occurred_at,
        description_preview=_preview(history.description),
        revision_notes_preview=_preview(history.revision_notes),
        created_at=history.created_at,
        updated_at=history.updated_at,
    )


def _history_detail_response(history: SpeechHistory, speech_title: str) -> SpeechHistoryDetailResponse:
    item = _history_summary_response(history, speech_title)
    return SpeechHistoryDetailResponse(
        **item.model_dump(),
        description=history.description,
        revision_notes=history.revision_notes,
    )


def list_projects(db: Session, user: User) -> list[SpeechProjectSummaryResponse]:
    return [_project_summary_response(db, project) for project in repository.list_projects(db, user.id)]


def create_project(db: Session, user: User, payload: SpeechProjectCreateRequest) -> SpeechProjectDetailResponse:
    project = SpeechProject(owner_id=user.id, **payload.model_dump())
    repository.add(db, project)
    db.commit()
    db.refresh(project)
    return _project_detail_response(db, project)


def get_project(db: Session, user: User, project_id: int) -> SpeechProjectDetailResponse:
    return _project_detail_response(db, _get_owned_project(db, user, project_id))


def update_project(db: Session, user: User, project_id: int, payload: SpeechProjectUpdateRequest) -> SpeechProjectDetailResponse:
    project = _get_owned_project(db, user, project_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    db.commit()
    db.refresh(project)
    return _project_detail_response(db, project)


def delete_project(db: Session, user: User, project_id: int) -> None:
    project = _get_owned_project(db, user, project_id)
    repository.delete_project_children(db, project.id)
    repository.delete_record(db, project)
    db.commit()


def list_speeches(db: Session, user: User) -> list[SpeechSummaryResponse]:
    return [
        _speech_summary_response(db, speech, project.title)
        for speech, project in repository.list_speeches(db, user.id)
    ]


def create_speech(db: Session, user: User, payload: SpeechCreateRequest) -> SpeechDetailResponse:
    project = _get_owned_project(db, user, payload.project_id)
    speech = Speech(owner_id=user.id, **payload.model_dump())
    repository.add(db, speech)
    db.commit()
    db.refresh(speech)
    return _speech_detail_response(db, speech, project.title)


def get_speech(db: Session, user: User, speech_id: int) -> SpeechDetailResponse:
    speech = _get_owned_speech(db, user, speech_id)
    project = _get_owned_project(db, user, speech.project_id)
    return _speech_detail_response(db, speech, project.title)


def update_speech(db: Session, user: User, speech_id: int, payload: SpeechUpdateRequest) -> SpeechDetailResponse:
    speech = _get_owned_speech(db, user, speech_id)
    project = _get_owned_project(db, user, speech.project_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(speech, field, value)
    db.commit()
    db.refresh(speech)
    return _speech_detail_response(db, speech, project.title)


def delete_speech(db: Session, user: User, speech_id: int) -> None:
    speech = _get_owned_speech(db, user, speech_id)
    repository.delete_speech_children(db, speech.id)
    repository.delete_record(db, speech)
    db.commit()


def list_templates(db: Session, user: User) -> list[SpeechTemplateSummaryResponse]:
    return [
        _template_summary_response(template, project.title)
        for template, project in repository.list_templates(db, user.id)
    ]


def create_template(db: Session, user: User, payload: SpeechTemplateCreateRequest) -> SpeechTemplateDetailResponse:
    project = _get_owned_project(db, user, payload.project_id)
    template = SpeechTemplate(owner_id=user.id, **payload.model_dump())
    repository.add(db, template)
    db.commit()
    db.refresh(template)
    return _template_detail_response(template, project.title)


def get_template(db: Session, user: User, template_id: int) -> SpeechTemplateDetailResponse:
    template = _get_owned_template(db, user, template_id)
    project = _get_owned_project(db, user, template.project_id)
    return _template_detail_response(template, project.title)


def update_template(db: Session, user: User, template_id: int, payload: SpeechTemplateUpdateRequest) -> SpeechTemplateDetailResponse:
    template = _get_owned_template(db, user, template_id)
    project = _get_owned_project(db, user, template.project_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(template, field, value)
    db.commit()
    db.refresh(template)
    return _template_detail_response(template, project.title)


def delete_template(db: Session, user: User, template_id: int) -> None:
    template = _get_owned_template(db, user, template_id)
    repository.delete_record(db, template)
    db.commit()


def list_history(db: Session, user: User) -> list[SpeechHistorySummaryResponse]:
    return [
        _history_summary_response(history, speech.title)
        for history, speech in repository.list_history(db, user.id)
    ]


def create_history(db: Session, user: User, payload: SpeechHistoryCreateRequest) -> SpeechHistoryDetailResponse:
    speech = _get_owned_speech(db, user, payload.speech_id)
    history = SpeechHistory(owner_id=user.id, **payload.model_dump())
    repository.add(db, history)
    db.commit()
    db.refresh(history)
    return _history_detail_response(history, speech.title)


def get_history(db: Session, user: User, history_id: int) -> SpeechHistoryDetailResponse:
    history = _get_owned_history(db, user, history_id)
    speech = _get_owned_speech(db, user, history.speech_id)
    return _history_detail_response(history, speech.title)


def update_history(db: Session, user: User, history_id: int, payload: SpeechHistoryUpdateRequest) -> SpeechHistoryDetailResponse:
    history = _get_owned_history(db, user, history_id)
    speech = _get_owned_speech(db, user, history.speech_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(history, field, value)
    db.commit()
    db.refresh(history)
    return _history_detail_response(history, speech.title)


def delete_history(db: Session, user: User, history_id: int) -> None:
    history = _get_owned_history(db, user, history_id)
    repository.delete_record(db, history)
    db.commit()


def get_dashboard(db: Session, user: User) -> SpeechWriterDashboardResponse:
    projects = list_projects(db, user)
    speeches = list_speeches(db, user)
    templates = list_templates(db, user)
    history = list_history(db, user)
    return SpeechWriterDashboardResponse(
        projects=projects,
        speeches=speeches,
        templates=templates,
        history=history,
        project_count=len(projects),
        speech_count=len(speeches),
        template_count=len(templates),
        history_count=len(history),
        active_project_count=sum(1 for item in projects if item.status == "active"),
        ready_speech_count=sum(1 for item in speeches if item.status == "ready"),
    )
