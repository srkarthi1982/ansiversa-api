from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.social_caption_generator import repository
from app.modules.social_caption_generator.models import CaptionHistory, CaptionProject, CaptionTemplate, SocialCaption
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

PREVIEW_LENGTH = 220


def _preview(value: str | None) -> str | None:
    if not value:
        return None
    if len(value) <= PREVIEW_LENGTH:
        return value
    return f"{value[:PREVIEW_LENGTH].rstrip()}..."


def _not_found(detail: str) -> None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def _get_owned_project(db: Session, user: User, project_id: int) -> CaptionProject:
    project = repository.get_project(db, project_id)
    if not project or project.owner_id != user.id:
        _not_found("Caption project was not found.")
    return project


def _get_owned_caption(db: Session, user: User, caption_id: int) -> SocialCaption:
    caption = repository.get_caption(db, caption_id)
    if not caption or caption.owner_id != user.id:
        _not_found("Social caption was not found.")
    return caption


def _get_owned_template(db: Session, user: User, template_id: int) -> CaptionTemplate:
    template = repository.get_template(db, template_id)
    if not template or template.owner_id != user.id:
        _not_found("Caption template was not found.")
    return template


def _get_owned_history(db: Session, user: User, history_id: int) -> CaptionHistory:
    history = repository.get_history(db, history_id)
    if not history or history.owner_id != user.id:
        _not_found("Caption history record was not found.")
    return history


def _project_summary_response(db: Session, project: CaptionProject) -> CaptionProjectSummaryResponse:
    return CaptionProjectSummaryResponse(
        id=project.id,
        platform_id=project.platform_id,
        title=project.title,
        platform=project.platform,
        audience=project.audience,
        tone=project.tone,
        status=project.status,
        campaign_brief_preview=_preview(project.campaign_brief),
        caption_count=repository.count_captions(db, project.id),
        template_count=repository.count_templates(db, project.id),
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


def _project_detail_response(db: Session, project: CaptionProject) -> CaptionProjectDetailResponse:
    item = _project_summary_response(db, project)
    return CaptionProjectDetailResponse(
        **item.model_dump(),
        campaign_brief=project.campaign_brief,
        notes=project.notes,
    )


def _caption_summary_response(db: Session, caption: SocialCaption, project_title: str) -> SocialCaptionSummaryResponse:
    return SocialCaptionSummaryResponse(
        id=caption.id,
        platform_id=caption.platform_id,
        project_id=caption.project_id,
        project_title=project_title,
        title=caption.title,
        platform=caption.platform,
        status=caption.status,
        caption_preview=_preview(caption.caption_text),
        hashtag_preview=_preview(caption.hashtags),
        history_count=repository.count_history(db, caption.id),
        created_at=caption.created_at,
        updated_at=caption.updated_at,
    )


def _caption_detail_response(db: Session, caption: SocialCaption, project_title: str) -> SocialCaptionDetailResponse:
    item = _caption_summary_response(db, caption, project_title)
    return SocialCaptionDetailResponse(
        **item.model_dump(),
        caption_text=caption.caption_text,
        hashtags=caption.hashtags,
        call_to_action=caption.call_to_action,
    )


def _template_summary_response(template: CaptionTemplate, project_title: str) -> CaptionTemplateSummaryResponse:
    return CaptionTemplateSummaryResponse(
        id=template.id,
        platform_id=template.platform_id,
        project_id=template.project_id,
        project_title=project_title,
        title=template.title,
        platform=template.platform,
        tone=template.tone,
        template_preview=_preview(template.template_text),
        usage_notes_preview=_preview(template.usage_notes),
        created_at=template.created_at,
        updated_at=template.updated_at,
    )


def _template_detail_response(template: CaptionTemplate, project_title: str) -> CaptionTemplateDetailResponse:
    item = _template_summary_response(template, project_title)
    return CaptionTemplateDetailResponse(
        **item.model_dump(),
        template_text=template.template_text,
        usage_notes=template.usage_notes,
    )


def _history_summary_response(history: CaptionHistory, caption_title: str) -> CaptionHistorySummaryResponse:
    return CaptionHistorySummaryResponse(
        id=history.id,
        platform_id=history.platform_id,
        caption_id=history.caption_id,
        caption_title=caption_title,
        title=history.title,
        event_type=history.event_type,
        occurred_at=history.occurred_at,
        description_preview=_preview(history.description),
        revision_notes_preview=_preview(history.revision_notes),
        created_at=history.created_at,
        updated_at=history.updated_at,
    )


def _history_detail_response(history: CaptionHistory, caption_title: str) -> CaptionHistoryDetailResponse:
    item = _history_summary_response(history, caption_title)
    return CaptionHistoryDetailResponse(
        **item.model_dump(),
        description=history.description,
        revision_notes=history.revision_notes,
    )


def list_projects(db: Session, user: User) -> list[CaptionProjectSummaryResponse]:
    return [_project_summary_response(db, project) for project in repository.list_projects(db, user.id)]


def create_project(db: Session, user: User, payload: CaptionProjectCreateRequest) -> CaptionProjectDetailResponse:
    project = CaptionProject(owner_id=user.id, **payload.model_dump())
    repository.add(db, project)
    db.commit()
    db.refresh(project)
    return _project_detail_response(db, project)


def get_project(db: Session, user: User, project_id: int) -> CaptionProjectDetailResponse:
    return _project_detail_response(db, _get_owned_project(db, user, project_id))


def update_project(db: Session, user: User, project_id: int, payload: CaptionProjectUpdateRequest) -> CaptionProjectDetailResponse:
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


def list_captions(db: Session, user: User) -> list[SocialCaptionSummaryResponse]:
    return [
        _caption_summary_response(db, caption, project.title)
        for caption, project in repository.list_captions(db, user.id)
    ]


def create_caption(db: Session, user: User, payload: SocialCaptionCreateRequest) -> SocialCaptionDetailResponse:
    project = _get_owned_project(db, user, payload.project_id)
    caption = SocialCaption(owner_id=user.id, **payload.model_dump())
    repository.add(db, caption)
    db.commit()
    db.refresh(caption)
    return _caption_detail_response(db, caption, project.title)


def get_caption(db: Session, user: User, caption_id: int) -> SocialCaptionDetailResponse:
    caption = _get_owned_caption(db, user, caption_id)
    project = _get_owned_project(db, user, caption.project_id)
    return _caption_detail_response(db, caption, project.title)


def update_caption(db: Session, user: User, caption_id: int, payload: SocialCaptionUpdateRequest) -> SocialCaptionDetailResponse:
    caption = _get_owned_caption(db, user, caption_id)
    project = _get_owned_project(db, user, caption.project_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(caption, field, value)
    db.commit()
    db.refresh(caption)
    return _caption_detail_response(db, caption, project.title)


def delete_caption(db: Session, user: User, caption_id: int) -> None:
    caption = _get_owned_caption(db, user, caption_id)
    repository.delete_caption_children(db, caption.id)
    repository.delete_record(db, caption)
    db.commit()


def list_templates(db: Session, user: User) -> list[CaptionTemplateSummaryResponse]:
    return [
        _template_summary_response(template, project.title)
        for template, project in repository.list_templates(db, user.id)
    ]


def create_template(db: Session, user: User, payload: CaptionTemplateCreateRequest) -> CaptionTemplateDetailResponse:
    project = _get_owned_project(db, user, payload.project_id)
    template = CaptionTemplate(owner_id=user.id, **payload.model_dump())
    repository.add(db, template)
    db.commit()
    db.refresh(template)
    return _template_detail_response(template, project.title)


def get_template(db: Session, user: User, template_id: int) -> CaptionTemplateDetailResponse:
    template = _get_owned_template(db, user, template_id)
    project = _get_owned_project(db, user, template.project_id)
    return _template_detail_response(template, project.title)


def update_template(db: Session, user: User, template_id: int, payload: CaptionTemplateUpdateRequest) -> CaptionTemplateDetailResponse:
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


def list_history(db: Session, user: User) -> list[CaptionHistorySummaryResponse]:
    return [
        _history_summary_response(history, caption.title)
        for history, caption in repository.list_history(db, user.id)
    ]


def create_history(db: Session, user: User, payload: CaptionHistoryCreateRequest) -> CaptionHistoryDetailResponse:
    caption = _get_owned_caption(db, user, payload.caption_id)
    history = CaptionHistory(owner_id=user.id, **payload.model_dump())
    repository.add(db, history)
    db.commit()
    db.refresh(history)
    return _history_detail_response(history, caption.title)


def get_history(db: Session, user: User, history_id: int) -> CaptionHistoryDetailResponse:
    history = _get_owned_history(db, user, history_id)
    caption = _get_owned_caption(db, user, history.caption_id)
    return _history_detail_response(history, caption.title)


def update_history(db: Session, user: User, history_id: int, payload: CaptionHistoryUpdateRequest) -> CaptionHistoryDetailResponse:
    history = _get_owned_history(db, user, history_id)
    caption = _get_owned_caption(db, user, history.caption_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(history, field, value)
    db.commit()
    db.refresh(history)
    return _history_detail_response(history, caption.title)


def delete_history(db: Session, user: User, history_id: int) -> None:
    history = _get_owned_history(db, user, history_id)
    repository.delete_record(db, history)
    db.commit()


def get_dashboard(db: Session, user: User) -> SocialCaptionGeneratorDashboardResponse:
    projects = list_projects(db, user)
    captions = list_captions(db, user)
    templates = list_templates(db, user)
    history = list_history(db, user)
    return SocialCaptionGeneratorDashboardResponse(
        projects=projects,
        captions=captions,
        templates=templates,
        history=history,
        project_count=len(projects),
        caption_count=len(captions),
        template_count=len(templates),
        history_count=len(history),
        active_project_count=sum(1 for item in projects if item.status == "active"),
        approved_caption_count=sum(1 for item in captions if item.status == "approved"),
    )
