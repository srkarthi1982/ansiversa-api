from sqlalchemy import delete, func, select, update
from sqlalchemy.orm import Session

from app.modules.snippet_generator.models import (
    Snippet,
    SnippetCategory,
    SnippetHistory,
    SnippetProject,
)


def get_project(db: Session, project_id: int) -> SnippetProject | None:
    return db.get(SnippetProject, project_id)


def get_snippet(db: Session, snippet_id: int) -> Snippet | None:
    return db.get(Snippet, snippet_id)


def get_category(db: Session, category_id: int) -> SnippetCategory | None:
    return db.get(SnippetCategory, category_id)


def get_history(db: Session, history_id: int) -> SnippetHistory | None:
    return db.get(SnippetHistory, history_id)


def list_projects(db: Session, owner_id: str) -> list[SnippetProject]:
    return list(
        db.execute(
            select(SnippetProject)
            .where(SnippetProject.owner_id == owner_id)
            .order_by(SnippetProject.updated_at.desc(), SnippetProject.title.asc())
        )
        .scalars()
        .all()
    )


def list_snippets(db: Session, owner_id: str) -> list[tuple[Snippet, SnippetProject, SnippetCategory | None]]:
    return list(
        db.execute(
            select(Snippet, SnippetProject, SnippetCategory)
            .join(SnippetProject, SnippetProject.id == Snippet.project_id)
            .outerjoin(SnippetCategory, SnippetCategory.id == Snippet.category_id)
            .where(Snippet.owner_id == owner_id)
            .order_by(Snippet.updated_at.desc(), Snippet.title.asc())
        ).all()
    )


def list_categories(db: Session, owner_id: str) -> list[tuple[SnippetCategory, SnippetProject]]:
    return list(
        db.execute(
            select(SnippetCategory, SnippetProject)
            .join(SnippetProject, SnippetProject.id == SnippetCategory.project_id)
            .where(SnippetCategory.owner_id == owner_id)
            .order_by(SnippetCategory.updated_at.desc(), SnippetCategory.name.asc())
        ).all()
    )


def list_history(db: Session, owner_id: str) -> list[tuple[SnippetHistory, Snippet]]:
    return list(
        db.execute(
            select(SnippetHistory, Snippet)
            .join(Snippet, Snippet.id == SnippetHistory.snippet_id)
            .where(SnippetHistory.owner_id == owner_id)
            .order_by(SnippetHistory.updated_at.desc(), SnippetHistory.occurred_at.desc())
        ).all()
    )


def count_snippets(db: Session, project_id: int) -> int:
    return int(db.execute(select(func.count()).select_from(Snippet).where(Snippet.project_id == project_id)).scalar_one())


def count_categories(db: Session, project_id: int) -> int:
    return int(db.execute(select(func.count()).select_from(SnippetCategory).where(SnippetCategory.project_id == project_id)).scalar_one())


def count_category_snippets(db: Session, category_id: int) -> int:
    return int(db.execute(select(func.count()).select_from(Snippet).where(Snippet.category_id == category_id)).scalar_one())


def count_history(db: Session, snippet_id: int) -> int:
    return int(db.execute(select(func.count()).select_from(SnippetHistory).where(SnippetHistory.snippet_id == snippet_id)).scalar_one())


def add(db: Session, record: object) -> None:
    db.add(record)


def delete_record(db: Session, record: object) -> None:
    db.delete(record)


def delete_project_children(db: Session, project_id: int) -> None:
    snippet_ids = list(db.execute(select(Snippet.id).where(Snippet.project_id == project_id)).scalars().all())
    if snippet_ids:
        db.execute(delete(SnippetHistory).where(SnippetHistory.snippet_id.in_(snippet_ids)))
    db.execute(delete(Snippet).where(Snippet.project_id == project_id))
    db.execute(delete(SnippetCategory).where(SnippetCategory.project_id == project_id))


def delete_snippet_children(db: Session, snippet_id: int) -> None:
    db.execute(delete(SnippetHistory).where(SnippetHistory.snippet_id == snippet_id))


def clear_category_from_snippets(db: Session, category_id: int) -> None:
    db.execute(update(Snippet).where(Snippet.category_id == category_id).values(category_id=None))
