from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.lesson_builder.models import LessonPlan, LessonSection
from app.modules.lesson_builder.schemas import (
    LessonCreateRequest,
    LessonDetailResponse,
    LessonResponse,
    LessonSectionCreateRequest,
    LessonSectionReorderRequest,
    LessonSectionUpdateRequest,
    LessonUpdateRequest,
)


def _section_count(db: Session, lesson_id: str) -> int:
    return int(
        db.execute(
            select(func.count()).select_from(LessonSection).where(
                LessonSection.lesson_id == lesson_id
            )
        ).scalar_one()
    )


def _lesson_response(db: Session, lesson: LessonPlan) -> LessonResponse:
    return LessonResponse(
        id=lesson.id,
        title=lesson.title,
        subject=lesson.subject,
        audience=lesson.audience,
        duration_minutes=lesson.duration_minutes,
        objective=lesson.objective,
        status=lesson.status,
        section_count=_section_count(db, lesson.id),
        created_at=lesson.created_at,
        updated_at=lesson.updated_at,
        published_at=lesson.published_at,
    )


def _get_owned_lesson(db: Session, user: User, lesson_id: str) -> LessonPlan:
    lesson = db.get(LessonPlan, lesson_id)
    if not lesson or lesson.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson was not found.",
        )

    return lesson


def _ensure_draft_lesson(lesson: LessonPlan) -> None:
    if lesson.status == "published":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Published lessons are locked.",
        )


def _get_owned_section(db: Session, user: User, section_id: str) -> LessonSection:
    section = db.get(LessonSection, section_id)
    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson section was not found.",
        )
    _get_owned_lesson(db, user, section.lesson_id)

    return section


def _list_sections(db: Session, lesson_id: str) -> list[LessonSection]:
    return list(
        db.execute(
            select(LessonSection)
            .where(LessonSection.lesson_id == lesson_id)
            .order_by(LessonSection.position.asc(), LessonSection.created_at.asc())
        )
        .scalars()
        .all()
    )


def list_lessons(db: Session, user: User) -> list[LessonResponse]:
    lessons = list(
        db.execute(
            select(LessonPlan)
            .where(LessonPlan.user_id == user.id)
            .order_by(LessonPlan.updated_at.desc(), LessonPlan.title.asc())
        )
        .scalars()
        .all()
    )

    return [_lesson_response(db, lesson) for lesson in lessons]


def create_lesson(
    db: Session,
    user: User,
    payload: LessonCreateRequest,
) -> LessonResponse:
    lesson = LessonPlan(
        user_id=user.id,
        title=payload.title,
        subject=payload.subject,
        audience=payload.audience,
        duration_minutes=payload.duration_minutes,
        objective=payload.objective,
    )
    db.add(lesson)
    db.commit()
    db.refresh(lesson)

    return _lesson_response(db, lesson)


def get_lesson_detail(
    db: Session,
    user: User,
    lesson_id: str,
) -> LessonDetailResponse:
    lesson = _get_owned_lesson(db, user, lesson_id)
    return LessonDetailResponse(
        lesson=_lesson_response(db, lesson),
        sections=_list_sections(db, lesson.id),
    )


def update_lesson(
    db: Session,
    user: User,
    lesson_id: str,
    payload: LessonUpdateRequest,
) -> LessonResponse:
    lesson = _get_owned_lesson(db, user, lesson_id)
    _ensure_draft_lesson(lesson)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(lesson, field, value)
    db.commit()
    db.refresh(lesson)

    return _lesson_response(db, lesson)


def delete_lesson(db: Session, user: User, lesson_id: str) -> None:
    lesson = _get_owned_lesson(db, user, lesson_id)
    db.execute(delete(LessonSection).where(LessonSection.lesson_id == lesson.id))
    db.delete(lesson)
    db.commit()


def create_section(
    db: Session,
    user: User,
    lesson_id: str,
    payload: LessonSectionCreateRequest,
) -> LessonSection:
    lesson = _get_owned_lesson(db, user, lesson_id)
    _ensure_draft_lesson(lesson)
    next_position = len(_list_sections(db, lesson.id)) + 1
    section = LessonSection(
        lesson_id=lesson.id,
        title=payload.title,
        section_type=payload.section_type,
        content=payload.content,
        position=next_position,
    )
    db.add(section)
    db.commit()
    db.refresh(section)

    return section


def update_section(
    db: Session,
    user: User,
    section_id: str,
    payload: LessonSectionUpdateRequest,
) -> LessonSection:
    section = _get_owned_section(db, user, section_id)
    lesson = _get_owned_lesson(db, user, section.lesson_id)
    _ensure_draft_lesson(lesson)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(section, field, value)
    db.commit()
    db.refresh(section)

    return section


def delete_section(db: Session, user: User, section_id: str) -> None:
    section = _get_owned_section(db, user, section_id)
    lesson = _get_owned_lesson(db, user, section.lesson_id)
    _ensure_draft_lesson(lesson)
    lesson_id = section.lesson_id
    db.delete(section)
    db.flush()
    for index, remaining in enumerate(_list_sections(db, lesson_id), start=1):
        remaining.position = index
    db.commit()


def reorder_sections(
    db: Session,
    user: User,
    lesson_id: str,
    payload: LessonSectionReorderRequest,
) -> list[LessonSection]:
    lesson = _get_owned_lesson(db, user, lesson_id)
    _ensure_draft_lesson(lesson)
    sections = _list_sections(db, lesson.id)
    existing_ids = [section.id for section in sections]
    if (
        set(payload.section_ids) != set(existing_ids)
        or len(payload.section_ids) != len(existing_ids)
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Section order must include every section exactly once.",
        )

    section_by_id = {section.id: section for section in sections}
    for index, section_id in enumerate(payload.section_ids, start=1):
        section_by_id[section_id].position = index
    db.commit()

    return _list_sections(db, lesson.id)


def publish_lesson(db: Session, user: User, lesson_id: str) -> LessonDetailResponse:
    lesson = _get_owned_lesson(db, user, lesson_id)
    if lesson.status == "published":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Lesson is already published.",
        )

    sections = _list_sections(db, lesson.id)
    if not sections:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Add at least one section before publishing the lesson.",
        )

    lesson.status = "published"
    lesson.published_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(lesson)

    return LessonDetailResponse(
        lesson=_lesson_response(db, lesson),
        sections=_list_sections(db, lesson.id),
    )
