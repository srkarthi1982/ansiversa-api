from typing import Annotated

from fastapi import APIRouter, Path, status

from app.modules.project_tracker.dependencies import CurrentUser, ProjectTrackerDb
from app.modules.project_tracker.schemas import (
    ProjectTrackerDashboardResponse,
    ProjectTrackerProjectCreateRequest,
    ProjectTrackerProjectDetailResponse,
    ProjectTrackerProjectSummaryResponse,
    ProjectTrackerProjectUpdateRequest,
    ProjectTrackerTaskCreateRequest,
    ProjectTrackerTaskDetailResponse,
    ProjectTrackerTaskSummaryResponse,
    ProjectTrackerTaskUpdateRequest,
)
from app.modules.project_tracker.service import (
    create_project,
    create_task,
    delete_project,
    delete_task,
    get_dashboard,
    get_project,
    get_task,
    list_projects,
    list_tasks,
    update_project,
    update_task,
)

router = APIRouter()


@router.get("/dashboard", response_model=ProjectTrackerDashboardResponse)
def get_project_tracker_dashboard(current_user: CurrentUser, db: ProjectTrackerDb) -> ProjectTrackerDashboardResponse:
    return get_dashboard(db, current_user)


@router.post("/projects", response_model=ProjectTrackerProjectDetailResponse, status_code=status.HTTP_201_CREATED)
def create_project_tracker_project(
    payload: ProjectTrackerProjectCreateRequest,
    current_user: CurrentUser,
    db: ProjectTrackerDb,
) -> ProjectTrackerProjectDetailResponse:
    return create_project(db, current_user, payload)


@router.get("/projects", response_model=list[ProjectTrackerProjectSummaryResponse])
def list_project_tracker_projects(current_user: CurrentUser, db: ProjectTrackerDb) -> list[ProjectTrackerProjectSummaryResponse]:
    return list_projects(db, current_user)


@router.get("/projects/{project_id}", response_model=ProjectTrackerProjectDetailResponse)
def get_project_tracker_project(
    project_id: Annotated[int, Path(gt=0)],
    current_user: CurrentUser,
    db: ProjectTrackerDb,
) -> ProjectTrackerProjectDetailResponse:
    return get_project(db, current_user, project_id)


@router.put("/projects/{project_id}", response_model=ProjectTrackerProjectDetailResponse)
def update_project_tracker_project(
    project_id: Annotated[int, Path(gt=0)],
    payload: ProjectTrackerProjectUpdateRequest,
    current_user: CurrentUser,
    db: ProjectTrackerDb,
) -> ProjectTrackerProjectDetailResponse:
    return update_project(db, current_user, project_id, payload)


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project_tracker_project(
    project_id: Annotated[int, Path(gt=0)],
    current_user: CurrentUser,
    db: ProjectTrackerDb,
) -> None:
    delete_project(db, current_user, project_id)


@router.post("/tasks", response_model=ProjectTrackerTaskDetailResponse, status_code=status.HTTP_201_CREATED)
def create_project_tracker_task(
    payload: ProjectTrackerTaskCreateRequest,
    current_user: CurrentUser,
    db: ProjectTrackerDb,
) -> ProjectTrackerTaskDetailResponse:
    return create_task(db, current_user, payload)


@router.get("/tasks", response_model=list[ProjectTrackerTaskSummaryResponse])
def list_project_tracker_tasks(current_user: CurrentUser, db: ProjectTrackerDb) -> list[ProjectTrackerTaskSummaryResponse]:
    return list_tasks(db, current_user)


@router.get("/tasks/{task_id}", response_model=ProjectTrackerTaskDetailResponse)
def get_project_tracker_task(
    task_id: Annotated[int, Path(gt=0)],
    current_user: CurrentUser,
    db: ProjectTrackerDb,
) -> ProjectTrackerTaskDetailResponse:
    return get_task(db, current_user, task_id)


@router.put("/tasks/{task_id}", response_model=ProjectTrackerTaskDetailResponse)
def update_project_tracker_task(
    task_id: Annotated[int, Path(gt=0)],
    payload: ProjectTrackerTaskUpdateRequest,
    current_user: CurrentUser,
    db: ProjectTrackerDb,
) -> ProjectTrackerTaskDetailResponse:
    return update_task(db, current_user, task_id, payload)


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project_tracker_task(
    task_id: Annotated[int, Path(gt=0)],
    current_user: CurrentUser,
    db: ProjectTrackerDb,
) -> None:
    delete_task(db, current_user, task_id)
