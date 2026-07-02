from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.grammar_and_paraphrasing_assistant.models import GrammarJob, GrammarProject, GrammarResult


def get_project(db: Session, project_id: int) -> GrammarProject | None:
    return db.get(GrammarProject, project_id)


def get_result(db: Session, result_id: int) -> GrammarResult | None:
    return db.get(GrammarResult, result_id)


def list_projects(db: Session, owner_id: str) -> list[GrammarProject]:
    return list(
        db.execute(
            select(GrammarProject)
            .where(GrammarProject.owner_id == owner_id)
            .order_by(GrammarProject.updated_at.desc(), GrammarProject.title.asc())
        )
        .scalars()
        .all()
    )


def list_results(db: Session, owner_id: str) -> list[tuple[GrammarResult, GrammarProject]]:
    return list(
        db.execute(
            select(GrammarResult, GrammarProject)
            .join(GrammarProject, GrammarProject.id == GrammarResult.project_id)
            .where(GrammarResult.owner_id == owner_id)
            .order_by(GrammarResult.created_at.desc(), GrammarResult.id.desc())
        ).all()
    )


def list_history(db: Session, owner_id: str) -> list[tuple[GrammarJob, GrammarProject]]:
    return list(
        db.execute(
            select(GrammarJob, GrammarProject)
            .join(GrammarProject, GrammarProject.id == GrammarJob.project_id)
            .where(GrammarJob.owner_id == owner_id)
            .order_by(GrammarJob.started_at.desc(), GrammarJob.id.desc())
        ).all()
    )


def count_results(db: Session, project_id: int) -> int:
    return int(db.execute(select(func.count()).select_from(GrammarResult).where(GrammarResult.project_id == project_id)).scalar_one())


def latest_result(db: Session, project_id: int) -> GrammarResult | None:
    return db.execute(
        select(GrammarResult)
        .where(GrammarResult.project_id == project_id)
        .order_by(GrammarResult.created_at.desc(), GrammarResult.id.desc())
    ).scalars().first()


def add(db: Session, record: object) -> None:
    db.add(record)


def delete_record(db: Session, record: object) -> None:
    db.delete(record)
