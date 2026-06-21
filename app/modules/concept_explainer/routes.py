from typing import Annotated

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.auth.service import get_current_user
from app.modules.concept_explainer.db import get_concept_explainer_db
from app.modules.concept_explainer.schemas import (
    ConceptCheckCreateRequest,
    ConceptCheckResponse,
    ConceptCheckUpdateRequest,
    ConceptCreateRequest,
    ConceptDetailResponse,
    ConceptListResponse,
    ConceptResponse,
    ConceptStepCreateRequest,
    ConceptStepResponse,
    ConceptStepUpdateRequest,
    ConceptUpdateRequest,
)
from app.modules.concept_explainer.service import (
    create_check,
    create_concept,
    create_step,
    delete_check,
    delete_concept,
    delete_step,
    get_concept_detail,
    list_concepts,
    mark_concept_reviewed,
    update_check,
    update_concept,
    update_step,
)

router = APIRouter()


@router.get("/concepts", response_model=ConceptListResponse)
def get_concepts(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_concept_explainer_db)],
) -> ConceptListResponse:
    return ConceptListResponse(items=list_concepts(db, current_user))


@router.post(
    "/concepts",
    response_model=ConceptResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_concept_item(
    payload: ConceptCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_concept_explainer_db)],
) -> ConceptResponse:
    return create_concept(db, current_user, payload)


@router.get("/concepts/{concept_id}", response_model=ConceptDetailResponse)
def get_concept(
    concept_id: Annotated[str, Path(min_length=1)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_concept_explainer_db)],
) -> ConceptDetailResponse:
    return get_concept_detail(db, current_user, concept_id)


@router.put("/concepts/{concept_id}", response_model=ConceptResponse)
def update_concept_item(
    concept_id: Annotated[str, Path(min_length=1)],
    payload: ConceptUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_concept_explainer_db)],
) -> ConceptResponse:
    return update_concept(db, current_user, concept_id, payload)


@router.delete("/concepts/{concept_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_concept_item(
    concept_id: Annotated[str, Path(min_length=1)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_concept_explainer_db)],
) -> None:
    delete_concept(db, current_user, concept_id)


@router.post(
    "/concepts/{concept_id}/steps",
    response_model=ConceptStepResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_concept_step(
    concept_id: Annotated[str, Path(min_length=1)],
    payload: ConceptStepCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_concept_explainer_db)],
) -> ConceptStepResponse:
    return create_step(db, current_user, concept_id, payload)


@router.put("/steps/{step_id}", response_model=ConceptStepResponse)
def update_concept_step(
    step_id: Annotated[str, Path(min_length=1)],
    payload: ConceptStepUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_concept_explainer_db)],
) -> ConceptStepResponse:
    return update_step(db, current_user, step_id, payload)


@router.delete("/steps/{step_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_concept_step(
    step_id: Annotated[str, Path(min_length=1)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_concept_explainer_db)],
) -> None:
    delete_step(db, current_user, step_id)


@router.post(
    "/concepts/{concept_id}/checks",
    response_model=ConceptCheckResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_concept_check(
    concept_id: Annotated[str, Path(min_length=1)],
    payload: ConceptCheckCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_concept_explainer_db)],
) -> ConceptCheckResponse:
    return create_check(db, current_user, concept_id, payload)


@router.put("/checks/{check_id}", response_model=ConceptCheckResponse)
def update_concept_check(
    check_id: Annotated[str, Path(min_length=1)],
    payload: ConceptCheckUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_concept_explainer_db)],
) -> ConceptCheckResponse:
    return update_check(db, current_user, check_id, payload)


@router.delete("/checks/{check_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_concept_check(
    check_id: Annotated[str, Path(min_length=1)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_concept_explainer_db)],
) -> None:
    delete_check(db, current_user, check_id)


@router.post("/concepts/{concept_id}/review", response_model=ConceptDetailResponse)
def review_concept(
    concept_id: Annotated[str, Path(min_length=1)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_concept_explainer_db)],
) -> ConceptDetailResponse:
    return mark_concept_reviewed(db, current_user, concept_id)
