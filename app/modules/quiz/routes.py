from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.auth.service import get_current_user
from app.modules.quiz.db import get_quiz_db
from app.modules.quiz.schemas import (
    QuizPlatformListResponse,
    QuizRoadmapListResponse,
    QuizSubjectListResponse,
    QuizTopicListResponse,
)
from app.modules.quiz.service import (
    list_platforms,
    list_roadmaps,
    list_subjects,
    list_topics,
)

router = APIRouter()

StatusFilter = Literal["all", "active", "inactive"]
SortDirection = Literal["asc", "desc"]
PlatformSort = Literal["id", "name", "description", "type", "qCount", "status"]
SubjectSort = Literal["id", "name", "platformId", "qCount", "status"]
TopicSort = Literal[
    "id", "name", "platformId", "subjectId", "qCount", "status"
]
RoadmapSort = Literal[
    "id", "name", "platformId", "subjectId", "topicId", "qCount", "status"
]


@router.get("/platforms", response_model=QuizPlatformListResponse)
def get_quiz_platforms(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_quiz_db)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(alias="pageSize", ge=1, le=100)] = 10,
    q: str | None = None,
    status: StatusFilter = "all",
    sort: PlatformSort = "id",
    dir: SortDirection = "asc",
    min_questions: Annotated[int | None, Query(alias="minQuestions", ge=0)] = None,
    max_questions: Annotated[int | None, Query(alias="maxQuestions", ge=0)] = None,
    platform_type: Annotated[str | None, Query(alias="type")] = None,
) -> QuizPlatformListResponse:
    _ = current_user
    result = list_platforms(
        db,
        page=page,
        page_size=page_size,
        q=q,
        status_filter=status,
        sort=sort,
        direction=dir,
        min_questions=min_questions,
        max_questions=max_questions,
        platform_type=platform_type,
    )

    return QuizPlatformListResponse(
        items=result.items, total=result.total, page=result.page, page_size=result.page_size
    )


@router.get("/subjects", response_model=QuizSubjectListResponse)
def get_quiz_subjects(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_quiz_db)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(alias="pageSize", ge=1, le=100)] = 10,
    q: str | None = None,
    status: StatusFilter = "all",
    sort: SubjectSort = "id",
    dir: SortDirection = "asc",
    platform_id: Annotated[int | None, Query(alias="platformId", ge=1)] = None,
    min_questions: Annotated[int | None, Query(alias="minQuestions", ge=0)] = None,
    max_questions: Annotated[int | None, Query(alias="maxQuestions", ge=0)] = None,
) -> QuizSubjectListResponse:
    _ = current_user
    result = list_subjects(
        db,
        page=page,
        page_size=page_size,
        q=q,
        status_filter=status,
        sort=sort,
        direction=dir,
        min_questions=min_questions,
        max_questions=max_questions,
        platform_id=platform_id,
    )

    return QuizSubjectListResponse(
        items=result.items, total=result.total, page=result.page, page_size=result.page_size
    )


@router.get("/topics", response_model=QuizTopicListResponse)
def get_quiz_topics(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_quiz_db)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(alias="pageSize", ge=1, le=100)] = 10,
    q: str | None = None,
    status: StatusFilter = "all",
    sort: TopicSort = "id",
    dir: SortDirection = "asc",
    platform_id: Annotated[int | None, Query(alias="platformId", ge=1)] = None,
    subject_id: Annotated[int | None, Query(alias="subjectId", ge=1)] = None,
    min_questions: Annotated[int | None, Query(alias="minQuestions", ge=0)] = None,
    max_questions: Annotated[int | None, Query(alias="maxQuestions", ge=0)] = None,
) -> QuizTopicListResponse:
    _ = current_user
    result = list_topics(
        db,
        page=page,
        page_size=page_size,
        q=q,
        status_filter=status,
        sort=sort,
        direction=dir,
        min_questions=min_questions,
        max_questions=max_questions,
        platform_id=platform_id,
        subject_id=subject_id,
    )

    return QuizTopicListResponse(
        items=result.items, total=result.total, page=result.page, page_size=result.page_size
    )


@router.get("/roadmaps", response_model=QuizRoadmapListResponse)
def get_quiz_roadmaps(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_quiz_db)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(alias="pageSize", ge=1, le=100)] = 10,
    q: str | None = None,
    status: StatusFilter = "all",
    sort: RoadmapSort = "id",
    dir: SortDirection = "asc",
    platform_id: Annotated[int | None, Query(alias="platformId", ge=1)] = None,
    subject_id: Annotated[int | None, Query(alias="subjectId", ge=1)] = None,
    topic_id: Annotated[int | None, Query(alias="topicId", ge=1)] = None,
    roadmap_id: Annotated[int | None, Query(alias="roadmapId", ge=1)] = None,
    min_questions: Annotated[int | None, Query(alias="minQuestions", ge=0)] = None,
    max_questions: Annotated[int | None, Query(alias="maxQuestions", ge=0)] = None,
) -> QuizRoadmapListResponse:
    _ = current_user
    result = list_roadmaps(
        db,
        page=page,
        page_size=page_size,
        q=q,
        status_filter=status,
        sort=sort,
        direction=dir,
        min_questions=min_questions,
        max_questions=max_questions,
        platform_id=platform_id,
        subject_id=subject_id,
        topic_id=topic_id,
        roadmap_id=roadmap_id,
    )

    return QuizRoadmapListResponse(
        items=result.items, total=result.total, page=result.page, page_size=result.page_size
    )
