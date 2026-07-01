from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.ai_translator_and_tone_fixer import repository
from app.modules.ai_translator_and_tone_fixer.models import Translation, TranslationHistory, TranslationProject, TranslationTemplate
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

PREVIEW_LENGTH = 220


def _preview(value: str | None) -> str | None:
    if not value:
        return None
    if len(value) <= PREVIEW_LENGTH:
        return value
    return f"{value[:PREVIEW_LENGTH].rstrip()}..."


def _not_found(detail: str) -> None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def _get_owned_project(db: Session, user: User, project_id: int) -> TranslationProject:
    project = repository.get_project(db, project_id)
    if not project or project.owner_id != user.id:
        _not_found("Translation project was not found.")
    return project


def _get_owned_translation(db: Session, user: User, translation_id: int) -> Translation:
    translation = repository.get_translation(db, translation_id)
    if not translation or translation.owner_id != user.id:
        _not_found("Translation was not found.")
    return translation


def _get_owned_template(db: Session, user: User, template_id: int) -> TranslationTemplate:
    template = repository.get_template(db, template_id)
    if not template or template.owner_id != user.id:
        _not_found("Translation template was not found.")
    return template


def _get_owned_history(db: Session, user: User, history_id: int) -> TranslationHistory:
    history = repository.get_history(db, history_id)
    if not history or history.owner_id != user.id:
        _not_found("Translation history record was not found.")
    return history


def _project_summary_response(db: Session, project: TranslationProject) -> TranslationProjectSummaryResponse:
    return TranslationProjectSummaryResponse(
        id=project.id,
        platform_id=project.platform_id,
        title=project.title,
        source_language=project.source_language,
        target_language=project.target_language,
        tone=project.tone,
        status=project.status,
        goal_preview=_preview(project.goal),
        translation_count=repository.count_translations(db, project.id),
        template_count=repository.count_templates(db, project.id),
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


def _project_detail_response(db: Session, project: TranslationProject) -> TranslationProjectDetailResponse:
    item = _project_summary_response(db, project)
    return TranslationProjectDetailResponse(
        **item.model_dump(),
        goal=project.goal,
        notes=project.notes,
    )


def _translation_summary_response(db: Session, translation: Translation, project_title: str) -> TranslationSummaryResponse:
    return TranslationSummaryResponse(
        id=translation.id,
        platform_id=translation.platform_id,
        project_id=translation.project_id,
        project_title=project_title,
        title=translation.title,
        source_language=translation.source_language,
        target_language=translation.target_language,
        tone=translation.tone,
        status=translation.status,
        source_preview=_preview(translation.source_text),
        translated_preview=_preview(translation.translated_text),
        history_count=repository.count_history(db, translation.id),
        created_at=translation.created_at,
        updated_at=translation.updated_at,
    )


def _translation_detail_response(db: Session, translation: Translation, project_title: str) -> TranslationDetailResponse:
    item = _translation_summary_response(db, translation, project_title)
    return TranslationDetailResponse(
        **item.model_dump(),
        source_text=translation.source_text,
        translated_text=translation.translated_text,
        notes=translation.notes,
    )


def _template_summary_response(template: TranslationTemplate, project_title: str) -> TranslationTemplateSummaryResponse:
    return TranslationTemplateSummaryResponse(
        id=template.id,
        platform_id=template.platform_id,
        project_id=template.project_id,
        project_title=project_title,
        title=template.title,
        source_language=template.source_language,
        target_language=template.target_language,
        tone=template.tone,
        template_preview=_preview(template.template_text),
        usage_notes_preview=_preview(template.usage_notes),
        created_at=template.created_at,
        updated_at=template.updated_at,
    )


def _template_detail_response(template: TranslationTemplate, project_title: str) -> TranslationTemplateDetailResponse:
    item = _template_summary_response(template, project_title)
    return TranslationTemplateDetailResponse(
        **item.model_dump(),
        template_text=template.template_text,
        usage_notes=template.usage_notes,
    )


def _history_summary_response(history: TranslationHistory, translation_title: str) -> TranslationHistorySummaryResponse:
    return TranslationHistorySummaryResponse(
        id=history.id,
        platform_id=history.platform_id,
        translation_id=history.translation_id,
        translation_title=translation_title,
        title=history.title,
        event_type=history.event_type,
        occurred_at=history.occurred_at,
        description_preview=_preview(history.description),
        revision_notes_preview=_preview(history.revision_notes),
        created_at=history.created_at,
        updated_at=history.updated_at,
    )


def _history_detail_response(history: TranslationHistory, translation_title: str) -> TranslationHistoryDetailResponse:
    item = _history_summary_response(history, translation_title)
    return TranslationHistoryDetailResponse(
        **item.model_dump(),
        description=history.description,
        revision_notes=history.revision_notes,
    )


def list_projects(db: Session, user: User) -> list[TranslationProjectSummaryResponse]:
    return [_project_summary_response(db, project) for project in repository.list_projects(db, user.id)]


def create_project(db: Session, user: User, payload: TranslationProjectCreateRequest) -> TranslationProjectDetailResponse:
    project = TranslationProject(owner_id=user.id, **payload.model_dump())
    repository.add(db, project)
    db.commit()
    db.refresh(project)
    return _project_detail_response(db, project)


def get_project(db: Session, user: User, project_id: int) -> TranslationProjectDetailResponse:
    return _project_detail_response(db, _get_owned_project(db, user, project_id))


def update_project(db: Session, user: User, project_id: int, payload: TranslationProjectUpdateRequest) -> TranslationProjectDetailResponse:
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


def list_translations(db: Session, user: User) -> list[TranslationSummaryResponse]:
    return [
        _translation_summary_response(db, translation, project.title)
        for translation, project in repository.list_translations(db, user.id)
    ]


def create_translation(db: Session, user: User, payload: TranslationCreateRequest) -> TranslationDetailResponse:
    project = _get_owned_project(db, user, payload.project_id)
    translation = Translation(owner_id=user.id, **payload.model_dump())
    repository.add(db, translation)
    db.commit()
    db.refresh(translation)
    return _translation_detail_response(db, translation, project.title)


def get_translation(db: Session, user: User, translation_id: int) -> TranslationDetailResponse:
    translation = _get_owned_translation(db, user, translation_id)
    project = _get_owned_project(db, user, translation.project_id)
    return _translation_detail_response(db, translation, project.title)


def update_translation(db: Session, user: User, translation_id: int, payload: TranslationUpdateRequest) -> TranslationDetailResponse:
    translation = _get_owned_translation(db, user, translation_id)
    project = _get_owned_project(db, user, translation.project_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(translation, field, value)
    db.commit()
    db.refresh(translation)
    return _translation_detail_response(db, translation, project.title)


def delete_translation(db: Session, user: User, translation_id: int) -> None:
    translation = _get_owned_translation(db, user, translation_id)
    repository.delete_translation_children(db, translation.id)
    repository.delete_record(db, translation)
    db.commit()


def list_templates(db: Session, user: User) -> list[TranslationTemplateSummaryResponse]:
    return [
        _template_summary_response(template, project.title)
        for template, project in repository.list_templates(db, user.id)
    ]


def create_template(db: Session, user: User, payload: TranslationTemplateCreateRequest) -> TranslationTemplateDetailResponse:
    project = _get_owned_project(db, user, payload.project_id)
    template = TranslationTemplate(owner_id=user.id, **payload.model_dump())
    repository.add(db, template)
    db.commit()
    db.refresh(template)
    return _template_detail_response(template, project.title)


def get_template(db: Session, user: User, template_id: int) -> TranslationTemplateDetailResponse:
    template = _get_owned_template(db, user, template_id)
    project = _get_owned_project(db, user, template.project_id)
    return _template_detail_response(template, project.title)


def update_template(db: Session, user: User, template_id: int, payload: TranslationTemplateUpdateRequest) -> TranslationTemplateDetailResponse:
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


def list_history(db: Session, user: User) -> list[TranslationHistorySummaryResponse]:
    return [
        _history_summary_response(history, translation.title)
        for history, translation in repository.list_history(db, user.id)
    ]


def create_history(db: Session, user: User, payload: TranslationHistoryCreateRequest) -> TranslationHistoryDetailResponse:
    translation = _get_owned_translation(db, user, payload.translation_id)
    history = TranslationHistory(owner_id=user.id, **payload.model_dump())
    repository.add(db, history)
    db.commit()
    db.refresh(history)
    return _history_detail_response(history, translation.title)


def get_history(db: Session, user: User, history_id: int) -> TranslationHistoryDetailResponse:
    history = _get_owned_history(db, user, history_id)
    translation = _get_owned_translation(db, user, history.translation_id)
    return _history_detail_response(history, translation.title)


def update_history(db: Session, user: User, history_id: int, payload: TranslationHistoryUpdateRequest) -> TranslationHistoryDetailResponse:
    history = _get_owned_history(db, user, history_id)
    translation = _get_owned_translation(db, user, history.translation_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(history, field, value)
    db.commit()
    db.refresh(history)
    return _history_detail_response(history, translation.title)


def delete_history(db: Session, user: User, history_id: int) -> None:
    history = _get_owned_history(db, user, history_id)
    repository.delete_record(db, history)
    db.commit()


def get_dashboard(db: Session, user: User) -> AiTranslatorAndToneFixerDashboardResponse:
    projects = list_projects(db, user)
    translations = list_translations(db, user)
    templates = list_templates(db, user)
    history = list_history(db, user)
    return AiTranslatorAndToneFixerDashboardResponse(
        projects=projects,
        translations=translations,
        templates=templates,
        history=history,
        project_count=len(projects),
        translation_count=len(translations),
        template_count=len(templates),
        history_count=len(history),
        active_project_count=sum(1 for item in projects if item.status == "active"),
        ready_translation_count=sum(1 for item in translations if item.status == "ready"),
    )
