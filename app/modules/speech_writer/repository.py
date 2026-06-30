from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.modules.speech_writer.models import (
    SpeechHistory,
    SpeechProject,
    SpeechTemplate,
    Speech,
)


def get_project(db: Session, project_id: int) -> SpeechProject | None:
    return db.get(SpeechProject, project_id)


def get_speech(db: Session, speech_id: int) -> Speech | None:
    return db.get(Speech, speech_id)


def get_template(db: Session, template_id: int) -> SpeechTemplate | None:
    return db.get(SpeechTemplate, template_id)


def get_history(db: Session, history_id: int) -> SpeechHistory | None:
    return db.get(SpeechHistory, history_id)


def list_projects(db: Session, owner_id: str) -> list[SpeechProject]:
    return list(
        db.execute(
            select(SpeechProject)
            .where(SpeechProject.owner_id == owner_id)
            .order_by(SpeechProject.updated_at.desc(), SpeechProject.title.asc())
        )
        .scalars()
        .all()
    )


def list_speeches(db: Session, owner_id: str) -> list[tuple[Speech, SpeechProject]]:
    return list(
        db.execute(
            select(Speech, SpeechProject)
            .join(SpeechProject, SpeechProject.id == Speech.project_id)
            .where(Speech.owner_id == owner_id)
            .order_by(Speech.updated_at.desc(), Speech.title.asc())
        ).all()
    )


def list_templates(db: Session, owner_id: str) -> list[tuple[SpeechTemplate, SpeechProject]]:
    return list(
        db.execute(
            select(SpeechTemplate, SpeechProject)
            .join(SpeechProject, SpeechProject.id == SpeechTemplate.project_id)
            .where(SpeechTemplate.owner_id == owner_id)
            .order_by(SpeechTemplate.updated_at.desc(), SpeechTemplate.title.asc())
        ).all()
    )


def list_history(db: Session, owner_id: str) -> list[tuple[SpeechHistory, Speech]]:
    return list(
        db.execute(
            select(SpeechHistory, Speech)
            .join(Speech, Speech.id == SpeechHistory.speech_id)
            .where(SpeechHistory.owner_id == owner_id)
            .order_by(SpeechHistory.updated_at.desc(), SpeechHistory.occurred_at.desc())
        ).all()
    )


def count_speeches(db: Session, project_id: int) -> int:
    return int(db.execute(select(func.count()).select_from(Speech).where(Speech.project_id == project_id)).scalar_one())


def count_templates(db: Session, project_id: int) -> int:
    return int(db.execute(select(func.count()).select_from(SpeechTemplate).where(SpeechTemplate.project_id == project_id)).scalar_one())


def count_history(db: Session, speech_id: int) -> int:
    return int(db.execute(select(func.count()).select_from(SpeechHistory).where(SpeechHistory.speech_id == speech_id)).scalar_one())


def add(db: Session, record: object) -> None:
    db.add(record)


def delete_record(db: Session, record: object) -> None:
    db.delete(record)


def delete_project_children(db: Session, project_id: int) -> None:
    speech_ids = list(db.execute(select(Speech.id).where(Speech.project_id == project_id)).scalars().all())
    if speech_ids:
        db.execute(delete(SpeechHistory).where(SpeechHistory.speech_id.in_(speech_ids)))
    db.execute(delete(Speech).where(Speech.project_id == project_id))
    db.execute(delete(SpeechTemplate).where(SpeechTemplate.project_id == project_id))


def delete_speech_children(db: Session, speech_id: int) -> None:
    db.execute(delete(SpeechHistory).where(SpeechHistory.speech_id == speech_id))
