from typing import Annotated

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.auth.service import get_current_user
from app.modules.lesson_builder.db import get_lesson_builder_db
from app.modules.lesson_builder.schemas import (
    LessonCreateRequest,
    LessonDetailResponse,
    LessonListResponse,
    LessonResponse,
    LessonSectionCreateRequest,
    LessonSectionListResponse,
    LessonSectionReorderRequest,
    LessonSectionResponse,
    LessonSectionUpdateRequest,
    LessonUpdateRequest,
)
from app.modules.lesson_builder.service import (
    create_lesson,
    create_section,
    delete_lesson,
    delete_section,
    get_lesson_detail,
    list_lessons,
    publish_lesson,
    reorder_sections,
    update_lesson,
    update_section,
)

router = APIRouter()


@router.get("/lessons", response_model=LessonListResponse)
def get_lessons(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_lesson_builder_db)],
) -> LessonListResponse:
    return LessonListResponse(items=list_lessons(db, current_user))


@router.post(
    "/lessons",
    response_model=LessonResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_lesson_plan(
    payload: LessonCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_lesson_builder_db)],
) -> LessonResponse:
    return create_lesson(db, current_user, payload)


@router.get("/lessons/{lesson_id}", response_model=LessonDetailResponse)
def get_lesson(
    lesson_id: Annotated[str, Path(min_length=1)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_lesson_builder_db)],
) -> LessonDetailResponse:
    return get_lesson_detail(db, current_user, lesson_id)


@router.patch("/lessons/{lesson_id}", response_model=LessonResponse)
def update_lesson_plan(
    lesson_id: Annotated[str, Path(min_length=1)],
    payload: LessonUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_lesson_builder_db)],
) -> LessonResponse:
    return update_lesson(db, current_user, lesson_id, payload)


@router.delete("/lessons/{lesson_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lesson_plan(
    lesson_id: Annotated[str, Path(min_length=1)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_lesson_builder_db)],
) -> None:
    delete_lesson(db, current_user, lesson_id)


@router.post(
    "/lessons/{lesson_id}/sections",
    response_model=LessonSectionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_lesson_section(
    lesson_id: Annotated[str, Path(min_length=1)],
    payload: LessonSectionCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_lesson_builder_db)],
) -> LessonSectionResponse:
    return create_section(db, current_user, lesson_id, payload)


@router.patch("/sections/{section_id}", response_model=LessonSectionResponse)
def update_lesson_section(
    section_id: Annotated[str, Path(min_length=1)],
    payload: LessonSectionUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_lesson_builder_db)],
) -> LessonSectionResponse:
    return update_section(db, current_user, section_id, payload)


@router.delete("/sections/{section_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lesson_section(
    section_id: Annotated[str, Path(min_length=1)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_lesson_builder_db)],
) -> None:
    delete_section(db, current_user, section_id)


@router.post(
    "/lessons/{lesson_id}/sections/reorder",
    response_model=LessonSectionListResponse,
)
def reorder_lesson_sections(
    lesson_id: Annotated[str, Path(min_length=1)],
    payload: LessonSectionReorderRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_lesson_builder_db)],
) -> LessonSectionListResponse:
    return LessonSectionListResponse(
        items=reorder_sections(db, current_user, lesson_id, payload)
    )


@router.post("/lessons/{lesson_id}/publish", response_model=LessonDetailResponse)
def publish_lesson_plan(
    lesson_id: Annotated[str, Path(min_length=1)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_lesson_builder_db)],
) -> LessonDetailResponse:
    return publish_lesson(db, current_user, lesson_id)
