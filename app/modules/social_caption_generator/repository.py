from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.modules.social_caption_generator.models import (
    CaptionHistory,
    CaptionProject,
    CaptionTemplate,
    SocialCaption,
)


def get_project(db: Session, project_id: int) -> CaptionProject | None:
    return db.get(CaptionProject, project_id)


def get_caption(db: Session, caption_id: int) -> SocialCaption | None:
    return db.get(SocialCaption, caption_id)


def get_template(db: Session, template_id: int) -> CaptionTemplate | None:
    return db.get(CaptionTemplate, template_id)


def get_history(db: Session, history_id: int) -> CaptionHistory | None:
    return db.get(CaptionHistory, history_id)


def list_projects(db: Session, owner_id: str) -> list[CaptionProject]:
    return list(
        db.execute(
            select(CaptionProject)
            .where(CaptionProject.owner_id == owner_id)
            .order_by(CaptionProject.updated_at.desc(), CaptionProject.title.asc())
        )
        .scalars()
        .all()
    )


def list_captions(db: Session, owner_id: str) -> list[tuple[SocialCaption, CaptionProject]]:
    return list(
        db.execute(
            select(SocialCaption, CaptionProject)
            .join(CaptionProject, CaptionProject.id == SocialCaption.project_id)
            .where(SocialCaption.owner_id == owner_id)
            .order_by(SocialCaption.updated_at.desc(), SocialCaption.title.asc())
        ).all()
    )


def list_templates(db: Session, owner_id: str) -> list[tuple[CaptionTemplate, CaptionProject]]:
    return list(
        db.execute(
            select(CaptionTemplate, CaptionProject)
            .join(CaptionProject, CaptionProject.id == CaptionTemplate.project_id)
            .where(CaptionTemplate.owner_id == owner_id)
            .order_by(CaptionTemplate.updated_at.desc(), CaptionTemplate.title.asc())
        ).all()
    )


def list_history(db: Session, owner_id: str) -> list[tuple[CaptionHistory, SocialCaption]]:
    return list(
        db.execute(
            select(CaptionHistory, SocialCaption)
            .join(SocialCaption, SocialCaption.id == CaptionHistory.caption_id)
            .where(CaptionHistory.owner_id == owner_id)
            .order_by(CaptionHistory.updated_at.desc(), CaptionHistory.occurred_at.desc())
        ).all()
    )


def count_captions(db: Session, project_id: int) -> int:
    return int(db.execute(select(func.count()).select_from(SocialCaption).where(SocialCaption.project_id == project_id)).scalar_one())


def count_templates(db: Session, project_id: int) -> int:
    return int(db.execute(select(func.count()).select_from(CaptionTemplate).where(CaptionTemplate.project_id == project_id)).scalar_one())


def count_history(db: Session, caption_id: int) -> int:
    return int(db.execute(select(func.count()).select_from(CaptionHistory).where(CaptionHistory.caption_id == caption_id)).scalar_one())


def add(db: Session, record: object) -> None:
    db.add(record)


def delete_record(db: Session, record: object) -> None:
    db.delete(record)


def delete_project_children(db: Session, project_id: int) -> None:
    caption_ids = list(db.execute(select(SocialCaption.id).where(SocialCaption.project_id == project_id)).scalars().all())
    if caption_ids:
        db.execute(delete(CaptionHistory).where(CaptionHistory.caption_id.in_(caption_ids)))
    db.execute(delete(SocialCaption).where(SocialCaption.project_id == project_id))
    db.execute(delete(CaptionTemplate).where(CaptionTemplate.project_id == project_id))


def delete_caption_children(db: Session, caption_id: int) -> None:
    db.execute(delete(CaptionHistory).where(CaptionHistory.caption_id == caption_id))
