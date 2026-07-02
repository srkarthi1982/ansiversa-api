from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.creative_title_generator.models import GeneratedTitle, TitleJob, TitleProject


def get_project(db: Session, project_id: int) -> TitleProject | None:
    return db.get(TitleProject, project_id)


def get_generated_title(db: Session, generated_title_id: int) -> GeneratedTitle | None:
    return db.get(GeneratedTitle, generated_title_id)


def list_projects(db: Session, owner_id: str) -> list[TitleProject]:
    return list(
        db.execute(
            select(TitleProject)
            .where(TitleProject.owner_id == owner_id)
            .order_by(TitleProject.updated_at.desc(), TitleProject.title.asc())
        )
        .scalars()
        .all()
    )


def list_generated_titles(db: Session, owner_id: str) -> list[tuple[GeneratedTitle, TitleProject]]:
    return list(
        db.execute(
            select(GeneratedTitle, TitleProject)
            .join(TitleProject, TitleProject.id == GeneratedTitle.project_id)
            .where(GeneratedTitle.owner_id == owner_id)
            .order_by(GeneratedTitle.created_at.desc(), GeneratedTitle.id.desc())
        ).all()
    )


def list_history(db: Session, owner_id: str) -> list[tuple[TitleJob, TitleProject]]:
    return list(
        db.execute(
            select(TitleJob, TitleProject)
            .join(TitleProject, TitleProject.id == TitleJob.project_id)
            .where(TitleJob.owner_id == owner_id)
            .order_by(TitleJob.started_at.desc(), TitleJob.id.desc())
        ).all()
    )


def count_results(db: Session, project_id: int) -> int:
    return int(db.execute(select(func.count()).select_from(GeneratedTitle).where(GeneratedTitle.project_id == project_id)).scalar_one())


def latest_generated_title(db: Session, project_id: int) -> GeneratedTitle | None:
    return db.execute(
        select(GeneratedTitle)
        .where(GeneratedTitle.project_id == project_id)
        .order_by(GeneratedTitle.created_at.desc(), GeneratedTitle.id.desc())
    ).scalars().first()


def add(db: Session, record: object) -> None:
    db.add(record)


def delete_record(db: Session, record: object) -> None:
    db.delete(record)
