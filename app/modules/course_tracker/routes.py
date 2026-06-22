from typing import Annotated

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.auth.service import get_current_user
from app.modules.course_tracker.db import get_course_tracker_db
from app.modules.course_tracker.schemas import (
    CourseCreateRequest,
    CourseListResponse,
    CourseModuleCreateRequest,
    CourseModuleListResponse,
    CourseModuleResponse,
    CourseModuleUpdateRequest,
    CourseProgressLogCreateRequest,
    CourseProgressLogListResponse,
    CourseProgressLogResponse,
    CourseResponse,
    CourseTrackerDashboardResponse,
    CourseTrackerReviewResponse,
    CourseUpdateRequest,
)
from app.modules.course_tracker.service import (
    create_course,
    create_module,
    create_progress_log,
    delete_course,
    delete_module,
    get_dashboard,
    get_review,
    list_courses,
    list_modules,
    list_progress_logs,
    update_course,
    update_module,
)

router = APIRouter()


@router.get("/dashboard", response_model=CourseTrackerDashboardResponse)
def get_course_tracker_dashboard(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_course_tracker_db)],
) -> CourseTrackerDashboardResponse:
    return get_dashboard(db, current_user)


@router.get("/courses", response_model=CourseListResponse)
def get_courses(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_course_tracker_db)],
) -> CourseListResponse:
    return CourseListResponse(items=list_courses(db, current_user))


@router.post(
    "/courses",
    response_model=CourseResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_course_record(
    payload: CourseCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_course_tracker_db)],
) -> CourseResponse:
    return create_course(db, current_user, payload)


@router.put("/courses/{course_id}", response_model=CourseResponse)
def update_course_record(
    course_id: Annotated[int, Path(gt=0)],
    payload: CourseUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_course_tracker_db)],
) -> CourseResponse:
    return update_course(db, current_user, course_id, payload)


@router.delete("/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course_record(
    course_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_course_tracker_db)],
) -> None:
    delete_course(db, current_user, course_id)


@router.get("/modules", response_model=CourseModuleListResponse)
def get_course_modules(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_course_tracker_db)],
) -> CourseModuleListResponse:
    return CourseModuleListResponse(items=list_modules(db, current_user))


@router.post(
    "/modules",
    response_model=CourseModuleResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_course_module(
    payload: CourseModuleCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_course_tracker_db)],
) -> CourseModuleResponse:
    return create_module(db, current_user, payload)


@router.put("/modules/{module_id}", response_model=CourseModuleResponse)
def update_course_module(
    module_id: Annotated[int, Path(gt=0)],
    payload: CourseModuleUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_course_tracker_db)],
) -> CourseModuleResponse:
    return update_module(db, current_user, module_id, payload)


@router.delete("/modules/{module_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course_module(
    module_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_course_tracker_db)],
) -> None:
    delete_module(db, current_user, module_id)


@router.get("/progress-logs", response_model=CourseProgressLogListResponse)
def get_progress_logs(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_course_tracker_db)],
) -> CourseProgressLogListResponse:
    return CourseProgressLogListResponse(items=list_progress_logs(db, current_user))


@router.post(
    "/progress-logs",
    response_model=CourseProgressLogResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_course_progress_log(
    payload: CourseProgressLogCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_course_tracker_db)],
) -> CourseProgressLogResponse:
    return create_progress_log(db, current_user, payload)


@router.get("/review", response_model=CourseTrackerReviewResponse)
def get_course_review(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_course_tracker_db)],
) -> CourseTrackerReviewResponse:
    return get_review(db, current_user)
