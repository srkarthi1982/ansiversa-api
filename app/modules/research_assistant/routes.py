from typing import Annotated

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.auth.service import get_current_user
from app.modules.research_assistant.db import get_research_assistant_db
from app.modules.research_assistant.schemas import (
    ResearchNoteCreateRequest,
    ResearchNoteResponse,
    ResearchNoteUpdateRequest,
    ResearchReferenceCreateRequest,
    ResearchReferenceResponse,
    ResearchReferenceUpdateRequest,
    ResearchTopicCreateRequest,
    ResearchTopicDetailResponse,
    ResearchTopicListResponse,
    ResearchTopicResponse,
    ResearchTopicStatusRequest,
    ResearchTopicUpdateRequest,
)
from app.modules.research_assistant.service import (
    create_note,
    create_reference,
    create_topic,
    delete_note,
    delete_reference,
    delete_topic,
    get_topic_detail,
    list_topics,
    update_note,
    update_reference,
    update_topic,
    update_topic_status,
)

router = APIRouter()


@router.get("/topics", response_model=ResearchTopicListResponse)
def get_topics(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_research_assistant_db)],
) -> ResearchTopicListResponse:
    return ResearchTopicListResponse(items=list_topics(db, current_user))


@router.post(
    "/topics",
    response_model=ResearchTopicResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_research_topic(
    payload: ResearchTopicCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_research_assistant_db)],
) -> ResearchTopicResponse:
    return create_topic(db, current_user, payload)


@router.get("/topics/{topic_id}", response_model=ResearchTopicDetailResponse)
def get_research_topic(
    topic_id: Annotated[str, Path(min_length=1)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_research_assistant_db)],
) -> ResearchTopicDetailResponse:
    return get_topic_detail(db, current_user, topic_id)


@router.put("/topics/{topic_id}", response_model=ResearchTopicResponse)
def update_research_topic(
    topic_id: Annotated[str, Path(min_length=1)],
    payload: ResearchTopicUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_research_assistant_db)],
) -> ResearchTopicResponse:
    return update_topic(db, current_user, topic_id, payload)


@router.delete("/topics/{topic_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_research_topic(
    topic_id: Annotated[str, Path(min_length=1)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_research_assistant_db)],
) -> None:
    delete_topic(db, current_user, topic_id)


@router.post(
    "/topics/{topic_id}/notes",
    response_model=ResearchNoteResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_research_note(
    topic_id: Annotated[str, Path(min_length=1)],
    payload: ResearchNoteCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_research_assistant_db)],
) -> ResearchNoteResponse:
    return create_note(db, current_user, topic_id, payload)


@router.put("/notes/{note_id}", response_model=ResearchNoteResponse)
def update_research_note(
    note_id: Annotated[str, Path(min_length=1)],
    payload: ResearchNoteUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_research_assistant_db)],
) -> ResearchNoteResponse:
    return update_note(db, current_user, note_id, payload)


@router.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_research_note(
    note_id: Annotated[str, Path(min_length=1)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_research_assistant_db)],
) -> None:
    delete_note(db, current_user, note_id)


@router.post(
    "/topics/{topic_id}/references",
    response_model=ResearchReferenceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_research_reference(
    topic_id: Annotated[str, Path(min_length=1)],
    payload: ResearchReferenceCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_research_assistant_db)],
) -> ResearchReferenceResponse:
    return create_reference(db, current_user, topic_id, payload)


@router.put("/references/{reference_id}", response_model=ResearchReferenceResponse)
def update_research_reference(
    reference_id: Annotated[str, Path(min_length=1)],
    payload: ResearchReferenceUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_research_assistant_db)],
) -> ResearchReferenceResponse:
    return update_reference(db, current_user, reference_id, payload)


@router.delete("/references/{reference_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_research_reference(
    reference_id: Annotated[str, Path(min_length=1)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_research_assistant_db)],
) -> None:
    delete_reference(db, current_user, reference_id)


@router.post("/topics/{topic_id}/status", response_model=ResearchTopicDetailResponse)
def update_research_status(
    topic_id: Annotated[str, Path(min_length=1)],
    payload: ResearchTopicStatusRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_research_assistant_db)],
) -> ResearchTopicDetailResponse:
    return update_topic_status(db, current_user, topic_id, payload)
