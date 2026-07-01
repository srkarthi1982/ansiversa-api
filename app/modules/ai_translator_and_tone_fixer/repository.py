from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.modules.ai_translator_and_tone_fixer.models import (
    Translation,
    TranslationHistory,
    TranslationProject,
    TranslationTemplate,
)


def get_project(db: Session, project_id: int) -> TranslationProject | None:
    return db.get(TranslationProject, project_id)


def get_translation(db: Session, translation_id: int) -> Translation | None:
    return db.get(Translation, translation_id)


def get_template(db: Session, template_id: int) -> TranslationTemplate | None:
    return db.get(TranslationTemplate, template_id)


def get_history(db: Session, history_id: int) -> TranslationHistory | None:
    return db.get(TranslationHistory, history_id)


def list_projects(db: Session, owner_id: str) -> list[TranslationProject]:
    return list(
        db.execute(
            select(TranslationProject)
            .where(TranslationProject.owner_id == owner_id)
            .order_by(TranslationProject.updated_at.desc(), TranslationProject.title.asc())
        )
        .scalars()
        .all()
    )


def list_translations(db: Session, owner_id: str) -> list[tuple[Translation, TranslationProject]]:
    return list(
        db.execute(
            select(Translation, TranslationProject)
            .join(TranslationProject, TranslationProject.id == Translation.project_id)
            .where(Translation.owner_id == owner_id)
            .order_by(Translation.updated_at.desc(), Translation.title.asc())
        ).all()
    )


def list_templates(db: Session, owner_id: str) -> list[tuple[TranslationTemplate, TranslationProject]]:
    return list(
        db.execute(
            select(TranslationTemplate, TranslationProject)
            .join(TranslationProject, TranslationProject.id == TranslationTemplate.project_id)
            .where(TranslationTemplate.owner_id == owner_id)
            .order_by(TranslationTemplate.updated_at.desc(), TranslationTemplate.title.asc())
        ).all()
    )


def list_history(db: Session, owner_id: str) -> list[tuple[TranslationHistory, Translation]]:
    return list(
        db.execute(
            select(TranslationHistory, Translation)
            .join(Translation, Translation.id == TranslationHistory.translation_id)
            .where(TranslationHistory.owner_id == owner_id)
            .order_by(TranslationHistory.updated_at.desc(), TranslationHistory.occurred_at.desc())
        ).all()
    )


def count_translations(db: Session, project_id: int) -> int:
    return int(db.execute(select(func.count()).select_from(Translation).where(Translation.project_id == project_id)).scalar_one())


def count_templates(db: Session, project_id: int) -> int:
    return int(db.execute(select(func.count()).select_from(TranslationTemplate).where(TranslationTemplate.project_id == project_id)).scalar_one())


def count_history(db: Session, translation_id: int) -> int:
    return int(db.execute(select(func.count()).select_from(TranslationHistory).where(TranslationHistory.translation_id == translation_id)).scalar_one())


def add(db: Session, record: object) -> None:
    db.add(record)


def delete_record(db: Session, record: object) -> None:
    db.delete(record)


def delete_project_children(db: Session, project_id: int) -> None:
    translation_ids = list(db.execute(select(Translation.id).where(Translation.project_id == project_id)).scalars().all())
    if translation_ids:
        db.execute(delete(TranslationHistory).where(TranslationHistory.translation_id.in_(translation_ids)))
    db.execute(delete(Translation).where(Translation.project_id == project_id))
    db.execute(delete(TranslationTemplate).where(TranslationTemplate.project_id == project_id))


def delete_translation_children(db: Session, translation_id: int) -> None:
    db.execute(delete(TranslationHistory).where(TranslationHistory.translation_id == translation_id))
