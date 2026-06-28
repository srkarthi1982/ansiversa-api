from fastapi import HTTPException, status
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.proposal_writer.models import (
    ProposalDraft,
    ProposalHistoryItem,
    ProposalProject,
    ProposalSection,
)
from app.modules.proposal_writer.schemas import (
    ProposalDraftCreateRequest,
    ProposalDraftDetailResponse,
    ProposalDraftSummaryResponse,
    ProposalDraftUpdateRequest,
    ProposalHistoryCreateRequest,
    ProposalHistorySummaryResponse,
    ProposalProjectCreateRequest,
    ProposalProjectDetailResponse,
    ProposalProjectSummaryResponse,
    ProposalProjectUpdateRequest,
    ProposalSectionCreateRequest,
    ProposalSectionDetailResponse,
    ProposalSectionSummaryResponse,
    ProposalSectionUpdateRequest,
    ProposalWriterDashboardResponse,
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


def _bad_request(detail: str) -> None:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


def _get_owned_project(db: Session, user: User, project_id: int) -> ProposalProject:
    project = db.get(ProposalProject, project_id)
    if not project or project.owner_id != user.id:
        _not_found("Proposal project was not found.")

    return project


def _get_owned_section(db: Session, user: User, section_id: int) -> ProposalSection:
    section = db.get(ProposalSection, section_id)
    if not section or section.owner_id != user.id:
        _not_found("Proposal section was not found.")

    return section


def _get_owned_draft(db: Session, user: User, draft_id: int) -> ProposalDraft:
    draft = db.get(ProposalDraft, draft_id)
    if not draft or draft.owner_id != user.id:
        _not_found("Proposal draft was not found.")

    return draft


def _get_owned_history_item(db: Session, user: User, history_id: int) -> ProposalHistoryItem:
    history_item = db.get(ProposalHistoryItem, history_id)
    if not history_item or history_item.owner_id != user.id:
        _not_found("Proposal history item was not found.")

    return history_item


def _optional_owned_project(
    db: Session,
    user: User,
    project_id: int | None,
) -> ProposalProject | None:
    if project_id is None:
        return None

    return _get_owned_project(db, user, project_id)


def _optional_owned_draft(
    db: Session,
    user: User,
    draft_id: int | None,
) -> ProposalDraft | None:
    if draft_id is None:
        return None

    return _get_owned_draft(db, user, draft_id)


def _count_sections(db: Session, project_id: int) -> int:
    return int(
        db.execute(
            select(func.count()).select_from(ProposalSection).where(
                ProposalSection.project_id == project_id
            )
        ).scalar_one()
    )


def _count_drafts(db: Session, project_id: int) -> int:
    return int(
        db.execute(
            select(func.count()).select_from(ProposalDraft).where(
                ProposalDraft.project_id == project_id
            )
        ).scalar_one()
    )


def _project_summary_response(
    db: Session,
    project: ProposalProject,
) -> ProposalProjectSummaryResponse:
    return ProposalProjectSummaryResponse(
        id=project.id,
        title=project.title,
        client_name=project.client_name,
        budget_range=project.budget_range,
        due_date=project.due_date,
        status=project.status,
        section_count=_count_sections(db, project.id),
        draft_count=_count_drafts(db, project.id),
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


def _project_detail_response(
    db: Session,
    project: ProposalProject,
) -> ProposalProjectDetailResponse:
    summary = _project_summary_response(db, project)
    return ProposalProjectDetailResponse(
        **summary.model_dump(),
        opportunity=project.opportunity,
    )


def _section_summary_response(
    section: ProposalSection,
    project_title: str,
) -> ProposalSectionSummaryResponse:
    return ProposalSectionSummaryResponse(
        id=section.id,
        project_id=section.project_id,
        project_title=project_title,
        title=section.title,
        content_preview=_preview(section.content) or "",
        sort_order=section.sort_order,
        status=section.status,
        created_at=section.created_at,
        updated_at=section.updated_at,
    )


def _section_detail_response(
    section: ProposalSection,
    project_title: str,
) -> ProposalSectionDetailResponse:
    return ProposalSectionDetailResponse(
        id=section.id,
        project_id=section.project_id,
        project_title=project_title,
        title=section.title,
        content=section.content,
        sort_order=section.sort_order,
        status=section.status,
        created_at=section.created_at,
        updated_at=section.updated_at,
    )


def _draft_summary_response(
    draft: ProposalDraft,
    project_title: str,
) -> ProposalDraftSummaryResponse:
    return ProposalDraftSummaryResponse(
        id=draft.id,
        project_id=draft.project_id,
        project_title=project_title,
        title=draft.title,
        summary_preview=_preview(draft.summary),
        body_preview=_preview(draft.body) or "",
        status=draft.status,
        created_at=draft.created_at,
        updated_at=draft.updated_at,
    )


def _draft_detail_response(
    draft: ProposalDraft,
    project_title: str,
) -> ProposalDraftDetailResponse:
    return ProposalDraftDetailResponse(
        id=draft.id,
        project_id=draft.project_id,
        project_title=project_title,
        title=draft.title,
        summary=draft.summary,
        body=draft.body,
        status=draft.status,
        created_at=draft.created_at,
        updated_at=draft.updated_at,
    )


def _history_summary_response(
    history_item: ProposalHistoryItem,
    project_title: str | None,
    draft_title: str | None,
) -> ProposalHistorySummaryResponse:
    return ProposalHistorySummaryResponse(
        id=history_item.id,
        project_id=history_item.project_id,
        project_title=project_title,
        draft_id=history_item.draft_id,
        draft_title=draft_title,
        title=history_item.title,
        action_type=history_item.action_type,
        notes_preview=_preview(history_item.notes),
        created_at=history_item.created_at,
        updated_at=history_item.updated_at,
    )


def list_projects(db: Session, user: User) -> list[ProposalProjectSummaryResponse]:
    projects = list(
        db.execute(
            select(ProposalProject)
            .where(ProposalProject.owner_id == user.id)
            .order_by(ProposalProject.updated_at.desc(), ProposalProject.title.asc())
        )
        .scalars()
        .all()
    )

    return [_project_summary_response(db, project) for project in projects]


def create_project(
    db: Session,
    user: User,
    payload: ProposalProjectCreateRequest,
) -> ProposalProjectDetailResponse:
    project = ProposalProject(
        owner_id=user.id,
        title=payload.title,
        client_name=payload.client_name,
        opportunity=payload.opportunity,
        budget_range=payload.budget_range,
        due_date=payload.due_date,
        status=payload.status,
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    return _project_detail_response(db, project)


def get_project(
    db: Session,
    user: User,
    project_id: int,
) -> ProposalProjectDetailResponse:
    project = _get_owned_project(db, user, project_id)
    return _project_detail_response(db, project)


def update_project(
    db: Session,
    user: User,
    project_id: int,
    payload: ProposalProjectUpdateRequest,
) -> ProposalProjectDetailResponse:
    project = _get_owned_project(db, user, project_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    db.commit()
    db.refresh(project)

    return _project_detail_response(db, project)


def delete_project(db: Session, user: User, project_id: int) -> None:
    project = _get_owned_project(db, user, project_id)
    db.execute(delete(ProposalHistoryItem).where(ProposalHistoryItem.project_id == project.id))
    db.execute(delete(ProposalDraft).where(ProposalDraft.project_id == project.id))
    db.execute(delete(ProposalSection).where(ProposalSection.project_id == project.id))
    db.delete(project)
    db.commit()


def list_sections(db: Session, user: User) -> list[ProposalSectionSummaryResponse]:
    rows = db.execute(
        select(ProposalSection, ProposalProject.title)
        .join(ProposalProject, ProposalProject.id == ProposalSection.project_id)
        .where(ProposalSection.owner_id == user.id)
        .order_by(
            ProposalSection.project_id.asc(),
            ProposalSection.sort_order.asc(),
            ProposalSection.updated_at.desc(),
        )
    ).all()

    return [_section_summary_response(section, project_title) for section, project_title in rows]


def create_section(
    db: Session,
    user: User,
    payload: ProposalSectionCreateRequest,
) -> ProposalSectionDetailResponse:
    project = _get_owned_project(db, user, payload.project_id)
    section = ProposalSection(
        project_id=project.id,
        owner_id=user.id,
        title=payload.title,
        content=payload.content,
        sort_order=payload.sort_order,
        status=payload.status,
    )
    db.add(section)
    db.commit()
    db.refresh(section)

    return _section_detail_response(section, project.title)


def get_section(
    db: Session,
    user: User,
    section_id: int,
) -> ProposalSectionDetailResponse:
    section = _get_owned_section(db, user, section_id)
    project = _get_owned_project(db, user, section.project_id)
    return _section_detail_response(section, project.title)


def update_section(
    db: Session,
    user: User,
    section_id: int,
    payload: ProposalSectionUpdateRequest,
) -> ProposalSectionDetailResponse:
    section = _get_owned_section(db, user, section_id)
    project = _get_owned_project(db, user, section.project_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(section, field, value)
    db.commit()
    db.refresh(section)

    return _section_detail_response(section, project.title)


def delete_section(db: Session, user: User, section_id: int) -> None:
    section = _get_owned_section(db, user, section_id)
    db.delete(section)
    db.commit()


def list_drafts(db: Session, user: User) -> list[ProposalDraftSummaryResponse]:
    rows = db.execute(
        select(ProposalDraft, ProposalProject.title)
        .join(ProposalProject, ProposalProject.id == ProposalDraft.project_id)
        .where(ProposalDraft.owner_id == user.id)
        .order_by(ProposalDraft.updated_at.desc(), ProposalDraft.title.asc())
    ).all()

    return [_draft_summary_response(draft, project_title) for draft, project_title in rows]


def create_draft(
    db: Session,
    user: User,
    payload: ProposalDraftCreateRequest,
) -> ProposalDraftDetailResponse:
    project = _get_owned_project(db, user, payload.project_id)
    draft = ProposalDraft(
        project_id=project.id,
        owner_id=user.id,
        title=payload.title,
        summary=payload.summary,
        body=payload.body,
        status=payload.status,
    )
    db.add(draft)
    db.commit()
    db.refresh(draft)

    return _draft_detail_response(draft, project.title)


def get_draft(db: Session, user: User, draft_id: int) -> ProposalDraftDetailResponse:
    draft = _get_owned_draft(db, user, draft_id)
    project = _get_owned_project(db, user, draft.project_id)
    return _draft_detail_response(draft, project.title)


def update_draft(
    db: Session,
    user: User,
    draft_id: int,
    payload: ProposalDraftUpdateRequest,
) -> ProposalDraftDetailResponse:
    draft = _get_owned_draft(db, user, draft_id)
    project = _get_owned_project(db, user, draft.project_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(draft, field, value)
    db.commit()
    db.refresh(draft)

    return _draft_detail_response(draft, project.title)


def delete_draft(db: Session, user: User, draft_id: int) -> None:
    draft = _get_owned_draft(db, user, draft_id)
    db.execute(delete(ProposalHistoryItem).where(ProposalHistoryItem.draft_id == draft.id))
    db.delete(draft)
    db.commit()


def list_history(db: Session, user: User) -> list[ProposalHistorySummaryResponse]:
    rows = db.execute(
        select(ProposalHistoryItem, ProposalProject.title, ProposalDraft.title)
        .outerjoin(ProposalProject, ProposalProject.id == ProposalHistoryItem.project_id)
        .outerjoin(ProposalDraft, ProposalDraft.id == ProposalHistoryItem.draft_id)
        .where(ProposalHistoryItem.owner_id == user.id)
        .order_by(ProposalHistoryItem.created_at.desc())
    ).all()

    return [
        _history_summary_response(history_item, project_title, draft_title)
        for history_item, project_title, draft_title in rows
    ]


def create_history_item(
    db: Session,
    user: User,
    payload: ProposalHistoryCreateRequest,
) -> ProposalHistorySummaryResponse:
    project = _optional_owned_project(db, user, payload.project_id)
    draft = _optional_owned_draft(db, user, payload.draft_id)
    if project and draft and draft.project_id != project.id:
        _bad_request("Proposal history draft must belong to the selected project.")
    if draft and project is None:
        project = _get_owned_project(db, user, draft.project_id)

    history_item = ProposalHistoryItem(
        project_id=project.id if project else None,
        draft_id=draft.id if draft else None,
        owner_id=user.id,
        title=payload.title,
        action_type=payload.action_type,
        notes=payload.notes,
    )
    db.add(history_item)
    db.commit()
    db.refresh(history_item)

    return _history_summary_response(
        history_item,
        project.title if project else None,
        draft.title if draft else None,
    )


def delete_history_item(db: Session, user: User, history_id: int) -> None:
    history_item = _get_owned_history_item(db, user, history_id)
    db.delete(history_item)
    db.commit()


def get_dashboard(db: Session, user: User) -> ProposalWriterDashboardResponse:
    projects = list_projects(db, user)
    sections = list_sections(db, user)
    drafts = list_drafts(db, user)
    history = list_history(db, user)

    return ProposalWriterDashboardResponse(
        projects=projects,
        sections=sections,
        drafts=drafts,
        history=history,
        active_project_count=sum(
            1 for project in projects if project.status in {"draft", "active"}
        ),
        ready_section_count=sum(
            1 for section in sections if section.status in {"ready", "approved"}
        ),
        ready_draft_count=sum(1 for draft in drafts if draft.status == "ready"),
        submitted_draft_count=sum(1 for draft in drafts if draft.status == "submitted"),
    )
