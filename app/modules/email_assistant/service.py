from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from fastapi import HTTPException, status

from app.modules.auth.models import User
from app.modules.email_assistant.models import (
    EmailDraft,
    EmailHistoryItem,
    EmailProject,
    EmailTemplate,
)
from app.modules.email_assistant.schemas import (
    EmailAssistantDashboardResponse,
    EmailDraftCreateRequest,
    EmailDraftListItemResponse,
    EmailDraftResponse,
    EmailDraftUpdateRequest,
    EmailHistoryCreateRequest,
    EmailHistoryListItemResponse,
    EmailHistoryResponse,
    EmailHistoryUpdateRequest,
    EmailProjectCreateRequest,
    EmailProjectResponse,
    EmailProjectUpdateRequest,
    EmailTemplateCreateRequest,
    EmailTemplateListItemResponse,
    EmailTemplateResponse,
    EmailTemplateUpdateRequest,
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


def _get_owned_project(db: Session, user: User, project_id: int) -> EmailProject:
    project = db.get(EmailProject, project_id)
    if not project or project.owner_id != user.id:
        _not_found("Email project was not found.")

    return project


def _get_owned_draft(db: Session, user: User, draft_id: int) -> EmailDraft:
    draft = db.get(EmailDraft, draft_id)
    if not draft or draft.owner_id != user.id:
        _not_found("Email draft was not found.")

    return draft


def _get_owned_template(db: Session, user: User, template_id: int) -> EmailTemplate:
    template = db.get(EmailTemplate, template_id)
    if not template or template.owner_id != user.id:
        _not_found("Email template was not found.")

    return template


def _get_owned_history_item(db: Session, user: User, history_id: int) -> EmailHistoryItem:
    history_item = db.get(EmailHistoryItem, history_id)
    if not history_item or history_item.owner_id != user.id:
        _not_found("Email history item was not found.")

    return history_item


def _optional_owned_template(
    db: Session,
    user: User,
    template_id: int | None,
) -> EmailTemplate | None:
    if template_id is None:
        return None

    return _get_owned_template(db, user, template_id)


def _optional_owned_project(
    db: Session,
    user: User,
    project_id: int | None,
) -> EmailProject | None:
    if project_id is None:
        return None

    return _get_owned_project(db, user, project_id)


def _optional_owned_draft(
    db: Session,
    user: User,
    draft_id: int | None,
) -> EmailDraft | None:
    if draft_id is None:
        return None

    return _get_owned_draft(db, user, draft_id)


def _count_drafts(db: Session, project_id: int) -> int:
    return int(
        db.execute(
            select(func.count()).select_from(EmailDraft).where(
                EmailDraft.project_id == project_id
            )
        ).scalar_one()
    )


def _count_history(db: Session, project_id: int) -> int:
    return int(
        db.execute(
            select(func.count()).select_from(EmailHistoryItem).where(
                EmailHistoryItem.project_id == project_id
            )
        ).scalar_one()
    )


def _project_response(db: Session, project: EmailProject) -> EmailProjectResponse:
    return EmailProjectResponse(
        id=project.id,
        title=project.title,
        audience=project.audience,
        goal=project.goal,
        tone=project.tone,
        status=project.status,
        draft_count=_count_drafts(db, project.id),
        history_count=_count_history(db, project.id),
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


def _draft_response(
    draft: EmailDraft,
    project_title: str,
    template_title: str | None,
) -> EmailDraftResponse:
    return EmailDraftResponse(
        id=draft.id,
        project_id=draft.project_id,
        project_title=project_title,
        template_id=draft.template_id,
        template_title=template_title,
        subject=draft.subject,
        body=draft.body,
        tone=draft.tone,
        status=draft.status,
        created_at=draft.created_at,
        updated_at=draft.updated_at,
    )


def _draft_list_item_response(
    draft: EmailDraft,
    project_title: str,
    template_title: str | None,
) -> EmailDraftListItemResponse:
    return EmailDraftListItemResponse(
        id=draft.id,
        project_id=draft.project_id,
        project_title=project_title,
        template_id=draft.template_id,
        template_title=template_title,
        subject=draft.subject,
        body_preview=_preview(draft.body) or "",
        tone=draft.tone,
        status=draft.status,
        created_at=draft.created_at,
        updated_at=draft.updated_at,
    )


def _template_response(template: EmailTemplate) -> EmailTemplateResponse:
    return EmailTemplateResponse(
        id=template.id,
        title=template.title,
        category=template.category,
        subject_pattern=template.subject_pattern,
        body_pattern=template.body_pattern,
        tone=template.tone,
        created_at=template.created_at,
        updated_at=template.updated_at,
    )


def _template_list_item_response(template: EmailTemplate) -> EmailTemplateListItemResponse:
    return EmailTemplateListItemResponse(
        id=template.id,
        title=template.title,
        category=template.category,
        subject_pattern=template.subject_pattern,
        body_pattern_preview=_preview(template.body_pattern) or "",
        tone=template.tone,
        created_at=template.created_at,
        updated_at=template.updated_at,
    )


def _history_response(
    history_item: EmailHistoryItem,
    project_title: str | None,
    draft_subject: str | None,
) -> EmailHistoryResponse:
    return EmailHistoryResponse(
        id=history_item.id,
        project_id=history_item.project_id,
        project_title=project_title,
        draft_id=history_item.draft_id,
        draft_subject=draft_subject,
        title=history_item.title,
        action_type=history_item.action_type,
        notes=history_item.notes,
        created_at=history_item.created_at,
        updated_at=history_item.updated_at,
    )


def _history_list_item_response(
    history_item: EmailHistoryItem,
    project_title: str | None,
    draft_subject: str | None,
) -> EmailHistoryListItemResponse:
    return EmailHistoryListItemResponse(
        id=history_item.id,
        project_id=history_item.project_id,
        project_title=project_title,
        draft_id=history_item.draft_id,
        draft_subject=draft_subject,
        title=history_item.title,
        action_type=history_item.action_type,
        notes_preview=_preview(history_item.notes),
        created_at=history_item.created_at,
        updated_at=history_item.updated_at,
    )


def list_projects(db: Session, user: User) -> list[EmailProjectResponse]:
    projects = list(
        db.execute(
            select(EmailProject)
            .where(EmailProject.owner_id == user.id)
            .order_by(EmailProject.updated_at.desc(), EmailProject.title.asc())
        )
        .scalars()
        .all()
    )

    return [_project_response(db, project) for project in projects]


def create_project(
    db: Session,
    user: User,
    payload: EmailProjectCreateRequest,
) -> EmailProjectResponse:
    project = EmailProject(
        owner_id=user.id,
        title=payload.title,
        audience=payload.audience,
        goal=payload.goal,
        tone=payload.tone,
        status="draft",
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    return _project_response(db, project)


def update_project(
    db: Session,
    user: User,
    project_id: int,
    payload: EmailProjectUpdateRequest,
) -> EmailProjectResponse:
    project = _get_owned_project(db, user, project_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    db.commit()
    db.refresh(project)

    return _project_response(db, project)


def delete_project(db: Session, user: User, project_id: int) -> None:
    project = _get_owned_project(db, user, project_id)
    db.execute(delete(EmailHistoryItem).where(EmailHistoryItem.project_id == project.id))
    db.execute(delete(EmailDraft).where(EmailDraft.project_id == project.id))
    db.delete(project)
    db.commit()


def list_drafts(db: Session, user: User) -> list[EmailDraftListItemResponse]:
    rows = db.execute(
        select(EmailDraft, EmailProject.title, EmailTemplate.title)
        .join(EmailProject, EmailProject.id == EmailDraft.project_id)
        .outerjoin(EmailTemplate, EmailTemplate.id == EmailDraft.template_id)
        .where(EmailDraft.owner_id == user.id)
        .order_by(EmailDraft.updated_at.desc())
    ).all()

    return [
        _draft_list_item_response(draft, project_title, template_title)
        for draft, project_title, template_title in rows
    ]


def get_draft(db: Session, user: User, draft_id: int) -> EmailDraftResponse:
    draft = _get_owned_draft(db, user, draft_id)
    project = _get_owned_project(db, user, draft.project_id)
    template = _optional_owned_template(db, user, draft.template_id)
    return _draft_response(draft, project.title, template.title if template else None)


def create_draft(
    db: Session,
    user: User,
    payload: EmailDraftCreateRequest,
) -> EmailDraftResponse:
    project = _get_owned_project(db, user, payload.project_id)
    template = _optional_owned_template(db, user, payload.template_id)
    draft = EmailDraft(
        owner_id=user.id,
        project_id=project.id,
        template_id=template.id if template else None,
        subject=payload.subject,
        body=payload.body,
        tone=payload.tone,
        status=payload.status,
    )
    if project.status == "draft":
        project.status = "active"
    db.add(draft)
    db.commit()
    db.refresh(draft)

    return _draft_response(draft, project.title, template.title if template else None)


def update_draft(
    db: Session,
    user: User,
    draft_id: int,
    payload: EmailDraftUpdateRequest,
) -> EmailDraftResponse:
    draft = _get_owned_draft(db, user, draft_id)
    project = _get_owned_project(db, user, draft.project_id)
    values = payload.model_dump(exclude_unset=True)
    template_id = values.get("template_id", draft.template_id)
    template = _optional_owned_template(db, user, template_id)
    for field, value in values.items():
        setattr(draft, field, value)
    db.commit()
    db.refresh(draft)

    return _draft_response(draft, project.title, template.title if template else None)


def delete_draft(db: Session, user: User, draft_id: int) -> None:
    draft = _get_owned_draft(db, user, draft_id)
    db.execute(delete(EmailHistoryItem).where(EmailHistoryItem.draft_id == draft.id))
    db.delete(draft)
    db.commit()


def list_templates(db: Session, user: User) -> list[EmailTemplateListItemResponse]:
    templates = list(
        db.execute(
            select(EmailTemplate)
            .where(EmailTemplate.owner_id == user.id)
            .order_by(EmailTemplate.updated_at.desc(), EmailTemplate.title.asc())
        )
        .scalars()
        .all()
    )

    return [_template_list_item_response(template) for template in templates]


def get_template(db: Session, user: User, template_id: int) -> EmailTemplateResponse:
    template = _get_owned_template(db, user, template_id)
    return _template_response(template)


def create_template(
    db: Session,
    user: User,
    payload: EmailTemplateCreateRequest,
) -> EmailTemplateResponse:
    template = EmailTemplate(
        owner_id=user.id,
        title=payload.title,
        category=payload.category,
        subject_pattern=payload.subject_pattern,
        body_pattern=payload.body_pattern,
        tone=payload.tone,
    )
    db.add(template)
    db.commit()
    db.refresh(template)

    return _template_response(template)


def update_template(
    db: Session,
    user: User,
    template_id: int,
    payload: EmailTemplateUpdateRequest,
) -> EmailTemplateResponse:
    template = _get_owned_template(db, user, template_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(template, field, value)
    db.commit()
    db.refresh(template)

    return _template_response(template)


def delete_template(db: Session, user: User, template_id: int) -> None:
    template = _get_owned_template(db, user, template_id)
    for draft in db.execute(
        select(EmailDraft).where(EmailDraft.template_id == template.id)
    ).scalars():
        draft.template_id = None
    db.delete(template)
    db.commit()


def list_history(db: Session, user: User) -> list[EmailHistoryListItemResponse]:
    rows = db.execute(
        select(EmailHistoryItem, EmailProject.title, EmailDraft.subject)
        .outerjoin(EmailProject, EmailProject.id == EmailHistoryItem.project_id)
        .outerjoin(EmailDraft, EmailDraft.id == EmailHistoryItem.draft_id)
        .where(EmailHistoryItem.owner_id == user.id)
        .order_by(EmailHistoryItem.updated_at.desc())
    ).all()

    return [
        _history_list_item_response(history_item, project_title, draft_subject)
        for history_item, project_title, draft_subject in rows
    ]


def get_history_item(db: Session, user: User, history_id: int) -> EmailHistoryResponse:
    history_item = _get_owned_history_item(db, user, history_id)
    project = _optional_owned_project(db, user, history_item.project_id)
    draft = _optional_owned_draft(db, user, history_item.draft_id)
    return _history_response(
        history_item,
        project.title if project else None,
        draft.subject if draft else None,
    )


def create_history_item(
    db: Session,
    user: User,
    payload: EmailHistoryCreateRequest,
) -> EmailHistoryResponse:
    project = _optional_owned_project(db, user, payload.project_id)
    draft = _optional_owned_draft(db, user, payload.draft_id)
    if draft and project and draft.project_id != project.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email draft does not belong to the selected project.",
        )
    if draft and project is None:
        project = _get_owned_project(db, user, draft.project_id)
    history_item = EmailHistoryItem(
        owner_id=user.id,
        project_id=project.id if project else None,
        draft_id=draft.id if draft else None,
        title=payload.title,
        action_type=payload.action_type,
        notes=payload.notes,
    )
    if project and payload.action_type == "sent":
        project.status = "completed"
    if draft and payload.action_type == "sent":
        draft.status = "sent"
    db.add(history_item)
    db.commit()
    db.refresh(history_item)

    return _history_response(
        history_item,
        project.title if project else None,
        draft.subject if draft else None,
    )


def update_history_item(
    db: Session,
    user: User,
    history_id: int,
    payload: EmailHistoryUpdateRequest,
) -> EmailHistoryResponse:
    history_item = _get_owned_history_item(db, user, history_id)
    project = _optional_owned_project(db, user, history_item.project_id)
    draft = _optional_owned_draft(db, user, history_item.draft_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(history_item, field, value)
    db.commit()
    db.refresh(history_item)

    return _history_response(
        history_item,
        project.title if project else None,
        draft.subject if draft else None,
    )


def delete_history_item(db: Session, user: User, history_id: int) -> None:
    history_item = _get_owned_history_item(db, user, history_id)
    db.delete(history_item)
    db.commit()


def get_dashboard(db: Session, user: User) -> EmailAssistantDashboardResponse:
    projects = list_projects(db, user)
    drafts = list_drafts(db, user)
    templates = list_templates(db, user)
    history = list_history(db, user)

    return EmailAssistantDashboardResponse(
        projects=projects,
        drafts=drafts,
        templates=templates,
        history=history,
        active_project_count=len([project for project in projects if project.status == "active"]),
        ready_draft_count=len([draft for draft in drafts if draft.status == "ready"]),
        template_count=len(templates),
    )
