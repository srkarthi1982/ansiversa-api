from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.modules.project_tracker.models import ProjectTrackerProject, ProjectTrackerTask


def get_project(db: Session, project_id: int) -> ProjectTrackerProject | None:
    return db.get(ProjectTrackerProject, project_id)


def get_task(db: Session, task_id: int) -> ProjectTrackerTask | None:
    return db.get(ProjectTrackerTask, task_id)


def list_projects(db: Session, owner_id: str) -> list[ProjectTrackerProject]:
    return list(
        db.execute(
            select(ProjectTrackerProject)
            .where(ProjectTrackerProject.owner_id == owner_id)
            .order_by(ProjectTrackerProject.updated_at.desc(), ProjectTrackerProject.title.asc())
        )
        .scalars()
        .all()
    )


def list_tasks(db: Session, owner_id: str) -> list[tuple[ProjectTrackerTask, ProjectTrackerProject]]:
    return list(
        db.execute(
            select(ProjectTrackerTask, ProjectTrackerProject)
            .join(ProjectTrackerProject, ProjectTrackerProject.id == ProjectTrackerTask.project_id)
            .where(ProjectTrackerTask.owner_id == owner_id)
            .order_by(ProjectTrackerTask.updated_at.desc(), ProjectTrackerTask.title.asc())
        ).all()
    )


def count_tasks(db: Session, project_id: int) -> int:
    return int(db.execute(select(func.count()).select_from(ProjectTrackerTask).where(ProjectTrackerTask.project_id == project_id)).scalar_one())


def count_completed_tasks(db: Session, project_id: int) -> int:
    return int(
        db.execute(
            select(func.count())
            .select_from(ProjectTrackerTask)
            .where(ProjectTrackerTask.project_id == project_id, ProjectTrackerTask.status == "done")
        ).scalar_one()
    )


def add(db: Session, record: object) -> None:
    db.add(record)


def delete_record(db: Session, record: object) -> None:
    db.delete(record)


def delete_project_tasks(db: Session, project_id: int) -> None:
    db.execute(delete(ProjectTrackerTask).where(ProjectTrackerTask.project_id == project_id))
