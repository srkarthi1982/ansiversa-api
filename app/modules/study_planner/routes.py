from typing import Annotated

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.auth.service import get_current_user
from app.modules.study_planner.db import get_study_planner_db
from app.modules.study_planner.schemas import (
    StudyLogCreateRequest,
    StudyLogListResponse,
    StudyLogResponse,
    StudyPlanCreateRequest,
    StudyPlannerDashboardResponse,
    StudyPlannerReviewResponse,
    StudyPlanListResponse,
    StudyPlanResponse,
    StudyPlanTaskCreateRequest,
    StudyPlanTaskListResponse,
    StudyPlanTaskResponse,
    StudyPlanTaskUpdateRequest,
    StudyPlanUpdateRequest,
)
from app.modules.study_planner.service import (
    create_log,
    create_plan,
    create_task,
    delete_plan,
    delete_task,
    get_dashboard,
    get_review,
    list_logs,
    list_plans,
    list_tasks,
    update_plan,
    update_task,
)

router = APIRouter()


@router.get("/dashboard", response_model=StudyPlannerDashboardResponse)
def get_study_planner_dashboard(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_study_planner_db)],
) -> StudyPlannerDashboardResponse:
    return get_dashboard(db, current_user)


@router.get("/plans", response_model=StudyPlanListResponse)
def get_study_plans(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_study_planner_db)],
) -> StudyPlanListResponse:
    return StudyPlanListResponse(items=list_plans(db, current_user))


@router.post(
    "/plans",
    response_model=StudyPlanResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_study_plan(
    payload: StudyPlanCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_study_planner_db)],
) -> StudyPlanResponse:
    return create_plan(db, current_user, payload)


@router.put("/plans/{plan_id}", response_model=StudyPlanResponse)
def update_study_plan(
    plan_id: Annotated[int, Path(gt=0)],
    payload: StudyPlanUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_study_planner_db)],
) -> StudyPlanResponse:
    return update_plan(db, current_user, plan_id, payload)


@router.delete("/plans/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_study_plan(
    plan_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_study_planner_db)],
) -> None:
    delete_plan(db, current_user, plan_id)


@router.get("/tasks", response_model=StudyPlanTaskListResponse)
def get_study_tasks(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_study_planner_db)],
) -> StudyPlanTaskListResponse:
    return StudyPlanTaskListResponse(items=list_tasks(db, current_user))


@router.post(
    "/tasks",
    response_model=StudyPlanTaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_study_task(
    payload: StudyPlanTaskCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_study_planner_db)],
) -> StudyPlanTaskResponse:
    return create_task(db, current_user, payload)


@router.put("/tasks/{task_id}", response_model=StudyPlanTaskResponse)
def update_study_task(
    task_id: Annotated[int, Path(gt=0)],
    payload: StudyPlanTaskUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_study_planner_db)],
) -> StudyPlanTaskResponse:
    return update_task(db, current_user, task_id, payload)


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_study_task(
    task_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_study_planner_db)],
) -> None:
    delete_task(db, current_user, task_id)


@router.get("/logs", response_model=StudyLogListResponse)
def get_study_logs(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_study_planner_db)],
) -> StudyLogListResponse:
    return StudyLogListResponse(items=list_logs(db, current_user))


@router.post(
    "/logs",
    response_model=StudyLogResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_study_log(
    payload: StudyLogCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_study_planner_db)],
) -> StudyLogResponse:
    return create_log(db, current_user, payload)


@router.get("/review", response_model=StudyPlannerReviewResponse)
def get_study_review(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_study_planner_db)],
) -> StudyPlannerReviewResponse:
    return get_review(db, current_user)
