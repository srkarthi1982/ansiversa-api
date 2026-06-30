from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.modules.prompt_builder.models import (
    Prompt,
    PromptHistory,
    PromptProject,
    PromptTemplate,
)


def get_project(db: Session, project_id: int) -> PromptProject | None:
    return db.get(PromptProject, project_id)


def get_prompt(db: Session, prompt_id: int) -> Prompt | None:
    return db.get(Prompt, prompt_id)


def get_template(db: Session, template_id: int) -> PromptTemplate | None:
    return db.get(PromptTemplate, template_id)


def get_history(db: Session, history_id: int) -> PromptHistory | None:
    return db.get(PromptHistory, history_id)


def list_projects(db: Session, owner_id: str) -> list[PromptProject]:
    return list(
        db.execute(
            select(PromptProject)
            .where(PromptProject.owner_id == owner_id)
            .order_by(PromptProject.updated_at.desc(), PromptProject.title.asc())
        )
        .scalars()
        .all()
    )


def list_prompts(db: Session, owner_id: str) -> list[tuple[Prompt, PromptProject]]:
    return list(
        db.execute(
            select(Prompt, PromptProject)
            .join(PromptProject, PromptProject.id == Prompt.project_id)
            .where(Prompt.owner_id == owner_id)
            .order_by(Prompt.updated_at.desc(), Prompt.title.asc())
        ).all()
    )


def list_templates(db: Session, owner_id: str) -> list[tuple[PromptTemplate, PromptProject]]:
    return list(
        db.execute(
            select(PromptTemplate, PromptProject)
            .join(PromptProject, PromptProject.id == PromptTemplate.project_id)
            .where(PromptTemplate.owner_id == owner_id)
            .order_by(PromptTemplate.updated_at.desc(), PromptTemplate.title.asc())
        ).all()
    )


def list_history(db: Session, owner_id: str) -> list[tuple[PromptHistory, Prompt]]:
    return list(
        db.execute(
            select(PromptHistory, Prompt)
            .join(Prompt, Prompt.id == PromptHistory.prompt_id)
            .where(PromptHistory.owner_id == owner_id)
            .order_by(PromptHistory.updated_at.desc(), PromptHistory.occurred_at.desc())
        ).all()
    )


def count_prompts(db: Session, project_id: int) -> int:
    return int(db.execute(select(func.count()).select_from(Prompt).where(Prompt.project_id == project_id)).scalar_one())


def count_templates(db: Session, project_id: int) -> int:
    return int(db.execute(select(func.count()).select_from(PromptTemplate).where(PromptTemplate.project_id == project_id)).scalar_one())


def count_history(db: Session, prompt_id: int) -> int:
    return int(db.execute(select(func.count()).select_from(PromptHistory).where(PromptHistory.prompt_id == prompt_id)).scalar_one())


def add(db: Session, record: object) -> None:
    db.add(record)


def delete_record(db: Session, record: object) -> None:
    db.delete(record)


def delete_project_children(db: Session, project_id: int) -> None:
    prompt_ids = list(db.execute(select(Prompt.id).where(Prompt.project_id == project_id)).scalars().all())
    if prompt_ids:
        db.execute(delete(PromptHistory).where(PromptHistory.prompt_id.in_(prompt_ids)))
    db.execute(delete(Prompt).where(Prompt.project_id == project_id))
    db.execute(delete(PromptTemplate).where(PromptTemplate.project_id == project_id))


def delete_prompt_children(db: Session, prompt_id: int) -> None:
    db.execute(delete(PromptHistory).where(PromptHistory.prompt_id == prompt_id))
