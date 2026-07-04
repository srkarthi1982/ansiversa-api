from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.project_tracker import repository
from app.modules.project_tracker.models import ProjectTrackerProject, ProjectTrackerTask
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

PREVIEW_LENGTH = 220


def _preview(value: str | None) -> str | None:
    if not value:
        return None
    if len(value) <= PREVIEW_LENGTH:
        return value
    return f"{value[:PREVIEW_LENGTH].rstrip()}..."


def _not_found(detail: str) -> None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def _get_owned_project(db: Session, user: User, project_id: int) -> ProjectTrackerProject:
    project = repository.get_project(db, project_id)
    if not project or project.owner_id != user.id:
        _not_found("Project was not found.")
    return project


def _get_owned_task(db: Session, user: User, task_id: int) -> ProjectTrackerTask:
    task = repository.get_task(db, task_id)
    if not task or task.owner_id != user.id:
        _not_found("Task was not found.")
    return task


def _project_summary_response(db: Session, project: ProjectTrackerProject) -> ProjectTrackerProjectSummaryResponse:
    return ProjectTrackerProjectSummaryResponse(
        id=project.id,
        platform_id=project.platform_id,
        title=project.title,
        owner_name=project.owner_name,
        status=project.status,
        priority=project.priority,
        due_date=project.due_date,
        notes_preview=_preview(project.notes),
        task_count=repository.count_tasks(db, project.id),
        completed_task_count=repository.count_completed_tasks(db, project.id),
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


def _project_detail_response(db: Session, project: ProjectTrackerProject) -> ProjectTrackerProjectDetailResponse:
    summary = _project_summary_response(db, project)
    return ProjectTrackerProjectDetailResponse(**summary.model_dump(), notes=project.notes)


def _task_summary_response(task: ProjectTrackerTask, project_title: str) -> ProjectTrackerTaskSummaryResponse:
    return ProjectTrackerTaskSummaryResponse(
        id=task.id,
        platform_id=task.platform_id,
        project_id=task.project_id,
        project_title=project_title,
        title=task.title,
        status=task.status,
        priority=task.priority,
        due_date=task.due_date,
        estimate_hours=task.estimate_hours,
        notes_preview=_preview(task.notes),
        created_at=task.created_at,
        updated_at=task.updated_at,
    )


def _task_detail_response(task: ProjectTrackerTask, project_title: str) -> ProjectTrackerTaskDetailResponse:
    summary = _task_summary_response(task, project_title)
    return ProjectTrackerTaskDetailResponse(**summary.model_dump(), notes=task.notes)


def list_projects(db: Session, user: User) -> list[ProjectTrackerProjectSummaryResponse]:
    return [_project_summary_response(db, project) for project in repository.list_projects(db, user.id)]


def create_project(
    db: Session,
    user: User,
    payload: ProjectTrackerProjectCreateRequest,
) -> ProjectTrackerProjectDetailResponse:
    project = ProjectTrackerProject(owner_id=user.id, **payload.model_dump())
    repository.add(db, project)
    db.commit()
    db.refresh(project)
    return _project_detail_response(db, project)


def get_project(db: Session, user: User, project_id: int) -> ProjectTrackerProjectDetailResponse:
    return _project_detail_response(db, _get_owned_project(db, user, project_id))


def update_project(
    db: Session,
    user: User,
    project_id: int,
    payload: ProjectTrackerProjectUpdateRequest,
) -> ProjectTrackerProjectDetailResponse:
    project = _get_owned_project(db, user, project_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    db.commit()
    db.refresh(project)
    return _project_detail_response(db, project)


def delete_project(db: Session, user: User, project_id: int) -> None:
    project = _get_owned_project(db, user, project_id)
    repository.delete_project_tasks(db, project.id)
    repository.delete_record(db, project)
    db.commit()


def list_tasks(db: Session, user: User) -> list[ProjectTrackerTaskSummaryResponse]:
    return [_task_summary_response(task, project.title) for task, project in repository.list_tasks(db, user.id)]


def create_task(
    db: Session,
    user: User,
    payload: ProjectTrackerTaskCreateRequest,
) -> ProjectTrackerTaskDetailResponse:
    project = _get_owned_project(db, user, payload.project_id)
    task = ProjectTrackerTask(owner_id=user.id, **payload.model_dump())
    repository.add(db, task)
    db.commit()
    db.refresh(task)
    return _task_detail_response(task, project.title)


def get_task(db: Session, user: User, task_id: int) -> ProjectTrackerTaskDetailResponse:
    task = _get_owned_task(db, user, task_id)
    project = _get_owned_project(db, user, task.project_id)
    return _task_detail_response(task, project.title)


def update_task(
    db: Session,
    user: User,
    task_id: int,
    payload: ProjectTrackerTaskUpdateRequest,
) -> ProjectTrackerTaskDetailResponse:
    task = _get_owned_task(db, user, task_id)
    project = _get_owned_project(db, user, task.project_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return _task_detail_response(task, project.title)


def delete_task(db: Session, user: User, task_id: int) -> None:
    task = _get_owned_task(db, user, task_id)
    repository.delete_record(db, task)
    db.commit()


def get_dashboard(db: Session, user: User) -> ProjectTrackerDashboardResponse:
    projects = list_projects(db, user)
    tasks = list_tasks(db, user)
    today = date.today().isoformat()
    upcoming_tasks = [
        task for task in sorted(
            [task for task in tasks if task.due_date and task.status != "done"],
            key=lambda task: task.due_date or "",
        )
    ][:5]

    return ProjectTrackerDashboardResponse(
        projects=projects,
        tasks=tasks,
        total_projects=len(projects),
        active_projects=sum(1 for project in projects if project.status == "active"),
        completed_projects=sum(1 for project in projects if project.status == "completed"),
        total_tasks=len(tasks),
        completed_tasks=sum(1 for task in tasks if task.status == "done"),
        blocked_tasks=sum(1 for task in tasks if task.status == "blocked"),
        overdue_tasks=sum(1 for task in tasks if task.due_date and task.due_date < today and task.status != "done"),
        upcoming_tasks=upcoming_tasks,
    )
