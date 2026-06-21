from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.concept_explainer.models import Concept, ConceptCheck, ConceptStep
from app.modules.concept_explainer.schemas import (
    ConceptCheckCreateRequest,
    ConceptCheckResponse,
    ConceptCheckUpdateRequest,
    ConceptCreateRequest,
    ConceptDetailResponse,
    ConceptResponse,
    ConceptStepCreateRequest,
    ConceptStepResponse,
    ConceptStepUpdateRequest,
    ConceptUpdateRequest,
)


def _count_steps(db: Session, concept_id: str) -> int:
    return int(
        db.execute(
            select(func.count()).select_from(ConceptStep).where(
                ConceptStep.concept_id == concept_id
            )
        ).scalar_one()
    )


def _count_checks(db: Session, concept_id: str) -> int:
    return int(
        db.execute(
            select(func.count()).select_from(ConceptCheck).where(
                ConceptCheck.concept_id == concept_id
            )
        ).scalar_one()
    )


def _concept_response(db: Session, concept: Concept) -> ConceptResponse:
    return ConceptResponse(
        id=concept.id,
        title=concept.title,
        topic=concept.topic,
        description=concept.description,
        status=concept.status,
        step_count=_count_steps(db, concept.id),
        check_count=_count_checks(db, concept.id),
        reviewed_at=concept.reviewed_at,
        created_at=concept.created_at,
        updated_at=concept.updated_at,
    )


def _get_owned_concept(db: Session, user: User, concept_id: str) -> Concept:
    concept = db.get(Concept, concept_id)
    if not concept or concept.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Concept was not found.",
        )

    return concept


def _get_owned_step(db: Session, user: User, step_id: str) -> ConceptStep:
    step = db.get(ConceptStep, step_id)
    if not step:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Concept step was not found.",
        )
    _get_owned_concept(db, user, step.concept_id)

    return step


def _get_owned_check(db: Session, user: User, check_id: str) -> ConceptCheck:
    check = db.get(ConceptCheck, check_id)
    if not check:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Concept check was not found.",
        )
    _get_owned_concept(db, user, check.concept_id)

    return check


def _list_steps(db: Session, concept_id: str) -> list[ConceptStep]:
    return list(
        db.execute(
            select(ConceptStep)
            .where(ConceptStep.concept_id == concept_id)
            .order_by(ConceptStep.position.asc(), ConceptStep.created_at.asc())
        )
        .scalars()
        .all()
    )


def _list_checks(db: Session, concept_id: str) -> list[ConceptCheck]:
    return list(
        db.execute(
            select(ConceptCheck)
            .where(ConceptCheck.concept_id == concept_id)
            .order_by(ConceptCheck.position.asc(), ConceptCheck.created_at.asc())
        )
        .scalars()
        .all()
    )


def list_concepts(db: Session, user: User) -> list[ConceptResponse]:
    concepts = list(
        db.execute(
            select(Concept)
            .where(Concept.user_id == user.id)
            .order_by(Concept.updated_at.desc(), Concept.title.asc())
        )
        .scalars()
        .all()
    )

    return [_concept_response(db, concept) for concept in concepts]


def create_concept(
    db: Session,
    user: User,
    payload: ConceptCreateRequest,
) -> ConceptResponse:
    concept = Concept(
        user_id=user.id,
        title=payload.title,
        topic=payload.topic,
        description=payload.description,
    )
    db.add(concept)
    db.commit()
    db.refresh(concept)

    return _concept_response(db, concept)


def get_concept_detail(
    db: Session,
    user: User,
    concept_id: str,
) -> ConceptDetailResponse:
    concept = _get_owned_concept(db, user, concept_id)
    return ConceptDetailResponse(
        concept=_concept_response(db, concept),
        steps=_list_steps(db, concept.id),
        checks=_list_checks(db, concept.id),
    )


def update_concept(
    db: Session,
    user: User,
    concept_id: str,
    payload: ConceptUpdateRequest,
) -> ConceptResponse:
    concept = _get_owned_concept(db, user, concept_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(concept, field, value)
    db.commit()
    db.refresh(concept)

    return _concept_response(db, concept)


def delete_concept(db: Session, user: User, concept_id: str) -> None:
    concept = _get_owned_concept(db, user, concept_id)
    db.execute(delete(ConceptCheck).where(ConceptCheck.concept_id == concept.id))
    db.execute(delete(ConceptStep).where(ConceptStep.concept_id == concept.id))
    db.delete(concept)
    db.commit()


def create_step(
    db: Session,
    user: User,
    concept_id: str,
    payload: ConceptStepCreateRequest,
) -> ConceptStepResponse:
    concept = _get_owned_concept(db, user, concept_id)
    next_position = len(_list_steps(db, concept.id)) + 1
    step = ConceptStep(
        concept_id=concept.id,
        title=payload.title,
        explanation=payload.explanation,
        position=next_position,
    )
    db.add(step)
    db.commit()
    db.refresh(step)

    return ConceptStepResponse.model_validate(step)


def update_step(
    db: Session,
    user: User,
    step_id: str,
    payload: ConceptStepUpdateRequest,
) -> ConceptStepResponse:
    step = _get_owned_step(db, user, step_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(step, field, value)
    db.commit()
    db.refresh(step)

    return ConceptStepResponse.model_validate(step)


def delete_step(db: Session, user: User, step_id: str) -> None:
    step = _get_owned_step(db, user, step_id)
    concept_id = step.concept_id
    db.delete(step)
    db.flush()
    for index, remaining in enumerate(_list_steps(db, concept_id), start=1):
        remaining.position = index
    db.commit()


def create_check(
    db: Session,
    user: User,
    concept_id: str,
    payload: ConceptCheckCreateRequest,
) -> ConceptCheckResponse:
    concept = _get_owned_concept(db, user, concept_id)
    next_position = len(_list_checks(db, concept.id)) + 1
    check = ConceptCheck(
        concept_id=concept.id,
        question=payload.question,
        expected_answer=payload.expected_answer,
        position=next_position,
    )
    db.add(check)
    db.commit()
    db.refresh(check)

    return ConceptCheckResponse.model_validate(check)


def update_check(
    db: Session,
    user: User,
    check_id: str,
    payload: ConceptCheckUpdateRequest,
) -> ConceptCheckResponse:
    check = _get_owned_check(db, user, check_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(check, field, value)
    db.commit()
    db.refresh(check)

    return ConceptCheckResponse.model_validate(check)


def delete_check(db: Session, user: User, check_id: str) -> None:
    check = _get_owned_check(db, user, check_id)
    concept_id = check.concept_id
    db.delete(check)
    db.flush()
    for index, remaining in enumerate(_list_checks(db, concept_id), start=1):
        remaining.position = index
    db.commit()


def mark_concept_reviewed(
    db: Session,
    user: User,
    concept_id: str,
) -> ConceptDetailResponse:
    concept = _get_owned_concept(db, user, concept_id)
    concept.status = "reviewed"
    concept.reviewed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(concept)

    return ConceptDetailResponse(
        concept=_concept_response(db, concept),
        steps=_list_steps(db, concept.id),
        checks=_list_checks(db, concept.id),
    )
