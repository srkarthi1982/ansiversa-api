import json
from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.resume_builder.models import ResumeItem, ResumeProject, ResumeSection
from app.modules.resume_builder.schemas import (
    ResumeBuilderDashboardResponse,
    ResumeBuilderReviewResponse,
    ResumeItemCreateRequest,
    ResumeItemResponse,
    ResumeItemUpdateRequest,
    ResumePreviewResponse,
    ResumePreviewSectionResponse,
    ResumeProjectCreateRequest,
    ResumeProjectResponse,
    ResumeProjectUpdateRequest,
    ResumeSectionCreateRequest,
    ResumeSectionResponse,
    ResumeSectionUpdateRequest,
)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _count_sections(db: Session, project_id: str, *, enabled_only: bool = False) -> int:
    statement = select(func.count()).select_from(ResumeSection).where(
        ResumeSection.project_id == project_id
    )
    if enabled_only:
        statement = statement.where(ResumeSection.is_enabled.is_(True))

    return int(db.execute(statement).scalar_one())


def _count_items(
    db: Session,
    *,
    project_id: str | None = None,
    section_id: str | None = None,
) -> int:
    statement = select(func.count()).select_from(ResumeItem)
    if section_id is not None:
        statement = statement.where(ResumeItem.section_id == section_id)
    if project_id is not None:
        statement = statement.join(
            ResumeSection,
            ResumeSection.id == ResumeItem.section_id,
        ).where(ResumeSection.project_id == project_id)

    return int(db.execute(statement).scalar_one())


def _completion_rate(total_count: int, completed_count: int) -> int:
    return round((completed_count / total_count) * 100) if total_count else 0


def _decode_item_data(value: str) -> dict[str, Any]:
    try:
        decoded = json.loads(value)
    except json.JSONDecodeError:
        return {"content": value}

    return decoded if isinstance(decoded, dict) else {"content": decoded}


def _encode_item_data(value: dict[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def _project_response(db: Session, project: ResumeProject) -> ResumeProjectResponse:
    return ResumeProjectResponse(
        id=project.id,
        title=project.title,
        template_key=project.template_key,
        is_default=project.is_default,
        section_count=_count_sections(db, project.id),
        item_count=_count_items(db, project_id=project.id),
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


def _section_response(
    db: Session,
    section: ResumeSection,
    project_title: str,
) -> ResumeSectionResponse:
    return ResumeSectionResponse(
        id=section.id,
        project_id=section.project_id,
        project_title=project_title,
        key=section.key,
        order=section.order,
        is_enabled=section.is_enabled,
        item_count=_count_items(db, section_id=section.id),
        created_at=section.created_at,
        updated_at=section.updated_at,
    )


def _item_response(
    item: ResumeItem,
    section: ResumeSection,
    project: ResumeProject,
) -> ResumeItemResponse:
    return ResumeItemResponse(
        id=item.id,
        project_id=project.id,
        project_title=project.title,
        section_id=item.section_id,
        section_key=section.key,
        order=item.order,
        data=_decode_item_data(item.data),
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


def _get_owned_project(db: Session, user: User, project_id: str) -> ResumeProject:
    project = db.get(ResumeProject, project_id)
    if not project or project.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume project was not found.",
        )

    return project


def _get_owned_section(db: Session, user: User, section_id: str) -> ResumeSection:
    row = db.execute(
        select(ResumeSection, ResumeProject)
        .join(ResumeProject, ResumeProject.id == ResumeSection.project_id)
        .where(ResumeSection.id == section_id, ResumeProject.user_id == user.id)
    ).one_or_none()
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume section was not found.",
        )

    section, _project = row
    return section


def _get_owned_item(
    db: Session,
    user: User,
    item_id: str,
) -> tuple[ResumeItem, ResumeSection, ResumeProject]:
    row = db.execute(
        select(ResumeItem, ResumeSection, ResumeProject)
        .join(ResumeSection, ResumeSection.id == ResumeItem.section_id)
        .join(ResumeProject, ResumeProject.id == ResumeSection.project_id)
        .where(ResumeItem.id == item_id, ResumeProject.user_id == user.id)
    ).one_or_none()
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume item was not found.",
        )

    return row


def _set_default_project(db: Session, user: User, project: ResumeProject) -> None:
    projects = db.execute(
        select(ResumeProject).where(ResumeProject.user_id == user.id)
    ).scalars()
    for existing in projects:
        existing.is_default = existing.id == project.id
        existing.updated_at = _now()


def list_projects(db: Session, user: User) -> list[ResumeProjectResponse]:
    projects = list(
        db.execute(
            select(ResumeProject)
            .where(ResumeProject.user_id == user.id)
            .order_by(ResumeProject.updated_at.desc(), ResumeProject.title.asc())
        )
        .scalars()
        .all()
    )

    return [_project_response(db, project) for project in projects]


def create_project(
    db: Session,
    user: User,
    payload: ResumeProjectCreateRequest,
) -> ResumeProjectResponse:
    existing_count = int(
        db.execute(
            select(func.count()).select_from(ResumeProject).where(
                ResumeProject.user_id == user.id
            )
        ).scalar_one()
    )
    project = ResumeProject(
        user_id=user.id,
        title=payload.title,
        template_key=payload.template_key,
        is_default=payload.is_default or existing_count == 0,
        photo_key="",
        photo_url="",
    )
    db.add(project)
    db.flush()
    if project.is_default:
        _set_default_project(db, user, project)
    db.commit()
    db.refresh(project)

    return _project_response(db, project)


def update_project(
    db: Session,
    user: User,
    project_id: str,
    payload: ResumeProjectUpdateRequest,
) -> ResumeProjectResponse:
    project = _get_owned_project(db, user, project_id)
    next_values = payload.model_dump(exclude_unset=True)
    if "template_key" in next_values:
        project.template_key = next_values["template_key"]
    if "title" in next_values:
        project.title = next_values["title"]
    if "is_default" in next_values:
        project.is_default = bool(next_values["is_default"])
        if project.is_default:
            _set_default_project(db, user, project)
    project.updated_at = _now()
    db.commit()
    db.refresh(project)

    return _project_response(db, project)


def delete_project(db: Session, user: User, project_id: str) -> None:
    project = _get_owned_project(db, user, project_id)
    section_ids = list(
        db.execute(
            select(ResumeSection.id).where(ResumeSection.project_id == project.id)
        )
        .scalars()
        .all()
    )
    if section_ids:
        db.execute(delete(ResumeItem).where(ResumeItem.section_id.in_(section_ids)))
    db.execute(delete(ResumeSection).where(ResumeSection.project_id == project.id))
    db.delete(project)
    db.commit()


def list_sections(db: Session, user: User) -> list[ResumeSectionResponse]:
    rows = db.execute(
        select(ResumeSection, ResumeProject.title)
        .join(ResumeProject, ResumeProject.id == ResumeSection.project_id)
        .where(ResumeProject.user_id == user.id)
        .order_by(ResumeSection.order.asc(), ResumeSection.updated_at.desc())
    ).all()

    return [_section_response(db, section, project_title) for section, project_title in rows]


def create_section(
    db: Session,
    user: User,
    payload: ResumeSectionCreateRequest,
) -> ResumeSectionResponse:
    project = _get_owned_project(db, user, payload.project_id)
    section = ResumeSection(
        project_id=project.id,
        key=payload.key,
        order=payload.order,
        is_enabled=payload.is_enabled,
    )
    db.add(section)
    project.updated_at = _now()
    db.commit()
    db.refresh(section)

    return _section_response(db, section, project.title)


def update_section(
    db: Session,
    user: User,
    section_id: str,
    payload: ResumeSectionUpdateRequest,
) -> ResumeSectionResponse:
    section = _get_owned_section(db, user, section_id)
    project = _get_owned_project(db, user, section.project_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(section, field, value)
    section.updated_at = _now()
    project.updated_at = _now()
    db.commit()
    db.refresh(section)

    return _section_response(db, section, project.title)


def delete_section(db: Session, user: User, section_id: str) -> None:
    section = _get_owned_section(db, user, section_id)
    project = _get_owned_project(db, user, section.project_id)
    db.execute(delete(ResumeItem).where(ResumeItem.section_id == section.id))
    db.delete(section)
    project.updated_at = _now()
    db.commit()


def list_items(db: Session, user: User) -> list[ResumeItemResponse]:
    rows = db.execute(
        select(ResumeItem, ResumeSection, ResumeProject)
        .join(ResumeSection, ResumeSection.id == ResumeItem.section_id)
        .join(ResumeProject, ResumeProject.id == ResumeSection.project_id)
        .where(ResumeProject.user_id == user.id)
        .order_by(ResumeItem.updated_at.desc(), ResumeItem.order.asc())
    ).all()

    return [_item_response(item, section, project) for item, section, project in rows]


def create_item(
    db: Session,
    user: User,
    payload: ResumeItemCreateRequest,
) -> ResumeItemResponse:
    section = _get_owned_section(db, user, payload.section_id)
    project = _get_owned_project(db, user, section.project_id)
    item = ResumeItem(
        section_id=section.id,
        order=payload.order,
        data=_encode_item_data(payload.data),
    )
    db.add(item)
    section.updated_at = _now()
    project.updated_at = _now()
    db.commit()
    db.refresh(item)

    return _item_response(item, section, project)


def update_item(
    db: Session,
    user: User,
    item_id: str,
    payload: ResumeItemUpdateRequest,
) -> ResumeItemResponse:
    item, section, project = _get_owned_item(db, user, item_id)
    next_values = payload.model_dump(exclude_unset=True)
    if "section_id" in next_values and next_values["section_id"] != item.section_id:
        section = _get_owned_section(db, user, next_values["section_id"])
        project = _get_owned_project(db, user, section.project_id)
        item.section_id = section.id
    if "order" in next_values:
        item.order = next_values["order"]
    if "data" in next_values:
        item.data = _encode_item_data(next_values["data"])
    item.updated_at = _now()
    section.updated_at = _now()
    project.updated_at = _now()
    db.commit()
    db.refresh(item)

    return _item_response(item, section, project)


def delete_item(db: Session, user: User, item_id: str) -> None:
    item, section, project = _get_owned_item(db, user, item_id)
    db.delete(item)
    section.updated_at = _now()
    project.updated_at = _now()
    db.commit()


def get_preview(
    db: Session,
    user: User,
    project_id: str | None = None,
) -> ResumePreviewResponse:
    project = (
        _get_owned_project(db, user, project_id)
        if project_id
        else db.execute(
            select(ResumeProject)
            .where(ResumeProject.user_id == user.id)
            .order_by(ResumeProject.is_default.desc(), ResumeProject.updated_at.desc())
            .limit(1)
        ).scalar_one_or_none()
    )
    if not project:
        return ResumePreviewResponse(project=None, sections=[])

    section_rows = db.execute(
        select(ResumeSection)
        .where(ResumeSection.project_id == project.id, ResumeSection.is_enabled.is_(True))
        .order_by(ResumeSection.order.asc(), ResumeSection.created_at.asc())
    ).scalars()
    sections: list[ResumePreviewSectionResponse] = []
    for section in section_rows:
        items = list(
            db.execute(
                select(ResumeItem)
                .where(ResumeItem.section_id == section.id)
                .order_by(ResumeItem.order.asc(), ResumeItem.created_at.asc())
            )
            .scalars()
            .all()
        )
        sections.append(
            ResumePreviewSectionResponse(
                section=_section_response(db, section, project.title),
                items=[_item_response(item, section, project) for item in items],
            )
        )

    return ResumePreviewResponse(project=_project_response(db, project), sections=sections)


def get_review(db: Session, user: User) -> ResumeBuilderReviewResponse:
    projects = list(
        db.execute(select(ResumeProject).where(ResumeProject.user_id == user.id))
        .scalars()
        .all()
    )
    project_ids = [project.id for project in projects]
    sections = (
        list(
            db.execute(
                select(ResumeSection).where(ResumeSection.project_id.in_(project_ids))
            )
            .scalars()
            .all()
        )
        if project_ids
        else []
    )
    enabled_sections = [section for section in sections if section.is_enabled]
    section_ids = [section.id for section in sections]
    items = (
        list(
            db.execute(
                select(ResumeItem)
                .where(ResumeItem.section_id.in_(section_ids))
                .order_by(ResumeItem.updated_at.desc())
                .limit(5)
            )
            .scalars()
            .all()
        )
        if section_ids
        else []
    )
    ready_project_count = sum(
        1
        for project in projects
        if _count_sections(db, project.id, enabled_only=True) >= 3
        and _count_items(db, project_id=project.id) >= 3
    )
    recent_items: list[ResumeItemResponse] = []
    for item in items:
        section = db.get(ResumeSection, item.section_id)
        project = db.get(ResumeProject, section.project_id) if section else None
        if section and project:
            recent_items.append(_item_response(item, section, project))

    return ResumeBuilderReviewResponse(
        project_count=len(projects),
        default_project_count=sum(1 for project in projects if project.is_default),
        enabled_section_count=len(enabled_sections),
        item_count=_count_items_for_sections(db, section_ids),
        completion_rate=_completion_rate(len(projects), ready_project_count),
        ready_project_count=ready_project_count,
        recent_items=recent_items,
    )


def _count_items_for_sections(db: Session, section_ids: list[str]) -> int:
    if not section_ids:
        return 0

    return int(
        db.execute(
            select(func.count()).select_from(ResumeItem).where(
                ResumeItem.section_id.in_(section_ids)
            )
        ).scalar_one()
    )


def get_dashboard(db: Session, user: User) -> ResumeBuilderDashboardResponse:
    return ResumeBuilderDashboardResponse(
        projects=list_projects(db, user),
        sections=list_sections(db, user),
        items=list_items(db, user),
        preview=get_preview(db, user),
        review=get_review(db, user),
    )
