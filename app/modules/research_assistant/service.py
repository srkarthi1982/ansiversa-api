from fastapi import HTTPException, status
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.research_assistant.models import (
    ResearchNote,
    ResearchReference,
    ResearchTopic,
)
from app.modules.research_assistant.schemas import (
    ResearchNoteCreateRequest,
    ResearchNoteResponse,
    ResearchNoteUpdateRequest,
    ResearchReferenceCreateRequest,
    ResearchReferenceResponse,
    ResearchReferenceUpdateRequest,
    ResearchTopicCreateRequest,
    ResearchTopicDetailResponse,
    ResearchTopicResponse,
    ResearchTopicStatusRequest,
    ResearchTopicUpdateRequest,
)


def _count_notes(db: Session, topic_id: str) -> int:
    return int(
        db.execute(
            select(func.count()).select_from(ResearchNote).where(
                ResearchNote.topic_id == topic_id
            )
        ).scalar_one()
    )


def _count_references(db: Session, topic_id: str) -> int:
    return int(
        db.execute(
            select(func.count()).select_from(ResearchReference).where(
                ResearchReference.topic_id == topic_id
            )
        ).scalar_one()
    )


def _topic_response(db: Session, topic: ResearchTopic) -> ResearchTopicResponse:
    return ResearchTopicResponse(
        id=topic.id,
        title=topic.title,
        question=topic.question,
        summary=topic.summary,
        status=topic.status,
        note_count=_count_notes(db, topic.id),
        reference_count=_count_references(db, topic.id),
        created_at=topic.created_at,
        updated_at=topic.updated_at,
    )


def _get_owned_topic(db: Session, user: User, topic_id: str) -> ResearchTopic:
    topic = db.get(ResearchTopic, topic_id)
    if not topic or topic.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research topic was not found.",
        )

    return topic


def _get_owned_note(db: Session, user: User, note_id: str) -> ResearchNote:
    note = db.get(ResearchNote, note_id)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research note was not found.",
        )
    _get_owned_topic(db, user, note.topic_id)

    return note


def _get_owned_reference(
    db: Session,
    user: User,
    reference_id: str,
) -> ResearchReference:
    reference = db.get(ResearchReference, reference_id)
    if not reference:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research reference was not found.",
        )
    _get_owned_topic(db, user, reference.topic_id)

    return reference


def _list_notes(db: Session, topic_id: str) -> list[ResearchNote]:
    return list(
        db.execute(
            select(ResearchNote)
            .where(ResearchNote.topic_id == topic_id)
            .order_by(ResearchNote.position.asc(), ResearchNote.created_at.asc())
        )
        .scalars()
        .all()
    )


def _list_references(db: Session, topic_id: str) -> list[ResearchReference]:
    return list(
        db.execute(
            select(ResearchReference)
            .where(ResearchReference.topic_id == topic_id)
            .order_by(
                ResearchReference.position.asc(),
                ResearchReference.created_at.asc(),
            )
        )
        .scalars()
        .all()
    )


def list_topics(db: Session, user: User) -> list[ResearchTopicResponse]:
    topics = list(
        db.execute(
            select(ResearchTopic)
            .where(ResearchTopic.user_id == user.id)
            .order_by(ResearchTopic.updated_at.desc(), ResearchTopic.title.asc())
        )
        .scalars()
        .all()
    )

    return [_topic_response(db, topic) for topic in topics]


def create_topic(
    db: Session,
    user: User,
    payload: ResearchTopicCreateRequest,
) -> ResearchTopicResponse:
    topic = ResearchTopic(
        user_id=user.id,
        title=payload.title,
        question=payload.question,
        summary=payload.summary,
    )
    db.add(topic)
    db.commit()
    db.refresh(topic)

    return _topic_response(db, topic)


def get_topic_detail(
    db: Session,
    user: User,
    topic_id: str,
) -> ResearchTopicDetailResponse:
    topic = _get_owned_topic(db, user, topic_id)
    return ResearchTopicDetailResponse(
        topic=_topic_response(db, topic),
        notes=_list_notes(db, topic.id),
        references=_list_references(db, topic.id),
    )


def update_topic(
    db: Session,
    user: User,
    topic_id: str,
    payload: ResearchTopicUpdateRequest,
) -> ResearchTopicResponse:
    topic = _get_owned_topic(db, user, topic_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(topic, field, value)
    db.commit()
    db.refresh(topic)

    return _topic_response(db, topic)


def delete_topic(db: Session, user: User, topic_id: str) -> None:
    topic = _get_owned_topic(db, user, topic_id)
    db.execute(delete(ResearchReference).where(ResearchReference.topic_id == topic.id))
    db.execute(delete(ResearchNote).where(ResearchNote.topic_id == topic.id))
    db.delete(topic)
    db.commit()


def create_note(
    db: Session,
    user: User,
    topic_id: str,
    payload: ResearchNoteCreateRequest,
) -> ResearchNoteResponse:
    topic = _get_owned_topic(db, user, topic_id)
    next_position = len(_list_notes(db, topic.id)) + 1
    note = ResearchNote(
        topic_id=topic.id,
        title=payload.title,
        body=payload.body,
        position=next_position,
    )
    db.add(note)
    db.commit()
    db.refresh(note)

    return ResearchNoteResponse.model_validate(note)


def update_note(
    db: Session,
    user: User,
    note_id: str,
    payload: ResearchNoteUpdateRequest,
) -> ResearchNoteResponse:
    note = _get_owned_note(db, user, note_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(note, field, value)
    db.commit()
    db.refresh(note)

    return ResearchNoteResponse.model_validate(note)


def delete_note(db: Session, user: User, note_id: str) -> None:
    note = _get_owned_note(db, user, note_id)
    topic_id = note.topic_id
    db.delete(note)
    db.flush()
    for index, remaining in enumerate(_list_notes(db, topic_id), start=1):
        remaining.position = index
    db.commit()


def create_reference(
    db: Session,
    user: User,
    topic_id: str,
    payload: ResearchReferenceCreateRequest,
) -> ResearchReferenceResponse:
    topic = _get_owned_topic(db, user, topic_id)
    next_position = len(_list_references(db, topic.id)) + 1
    reference = ResearchReference(
        topic_id=topic.id,
        title=payload.title,
        url=payload.url,
        notes=payload.notes,
        position=next_position,
    )
    db.add(reference)
    db.commit()
    db.refresh(reference)

    return ResearchReferenceResponse.model_validate(reference)


def update_reference(
    db: Session,
    user: User,
    reference_id: str,
    payload: ResearchReferenceUpdateRequest,
) -> ResearchReferenceResponse:
    reference = _get_owned_reference(db, user, reference_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(reference, field, value)
    db.commit()
    db.refresh(reference)

    return ResearchReferenceResponse.model_validate(reference)


def delete_reference(db: Session, user: User, reference_id: str) -> None:
    reference = _get_owned_reference(db, user, reference_id)
    topic_id = reference.topic_id
    db.delete(reference)
    db.flush()
    for index, remaining in enumerate(_list_references(db, topic_id), start=1):
        remaining.position = index
    db.commit()


def update_topic_status(
    db: Session,
    user: User,
    topic_id: str,
    payload: ResearchTopicStatusRequest,
) -> ResearchTopicDetailResponse:
    topic = _get_owned_topic(db, user, topic_id)
    topic.status = payload.status
    db.commit()
    db.refresh(topic)

    return ResearchTopicDetailResponse(
        topic=_topic_response(db, topic),
        notes=_list_notes(db, topic.id),
        references=_list_references(db, topic.id),
    )
