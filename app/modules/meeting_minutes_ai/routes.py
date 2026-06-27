from typing import Annotated

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.auth.service import get_current_user
from app.modules.meeting_minutes_ai.db import get_meeting_minutes_ai_db
from app.modules.meeting_minutes_ai.schemas import (
    MeetingActionItemCreateRequest,
    MeetingActionItemResponse,
    MeetingActionItemUpdateRequest,
    MeetingCreateRequest,
    MeetingMinutesDashboardResponse,
    MeetingNoteCreateRequest,
    MeetingNoteResponse,
    MeetingNoteUpdateRequest,
    MeetingResponse,
    MeetingSummaryCreateRequest,
    MeetingSummaryResponse,
    MeetingSummaryUpdateRequest,
    MeetingUpdateRequest,
)
from app.modules.meeting_minutes_ai.service import (
    create_action_item,
    create_meeting,
    create_note,
    create_summary,
    delete_action_item,
    delete_meeting,
    delete_note,
    delete_summary,
    get_dashboard,
    update_action_item,
    update_meeting,
    update_note,
    update_summary,
)

router = APIRouter()


@router.get("/dashboard", response_model=MeetingMinutesDashboardResponse)
def get_meeting_minutes_dashboard(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_meeting_minutes_ai_db)],
) -> MeetingMinutesDashboardResponse:
    return get_dashboard(db, current_user)


@router.post("/meetings", response_model=MeetingResponse, status_code=status.HTTP_201_CREATED)
def create_meeting_record(
    payload: MeetingCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_meeting_minutes_ai_db)],
) -> MeetingResponse:
    return create_meeting(db, current_user, payload)


@router.put("/meetings/{meeting_id}", response_model=MeetingResponse)
def update_meeting_record(
    meeting_id: Annotated[int, Path(gt=0)],
    payload: MeetingUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_meeting_minutes_ai_db)],
) -> MeetingResponse:
    return update_meeting(db, current_user, meeting_id, payload)


@router.delete("/meetings/{meeting_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_meeting_record(
    meeting_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_meeting_minutes_ai_db)],
) -> None:
    delete_meeting(db, current_user, meeting_id)


@router.post("/notes", response_model=MeetingNoteResponse, status_code=status.HTTP_201_CREATED)
def create_meeting_note(
    payload: MeetingNoteCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_meeting_minutes_ai_db)],
) -> MeetingNoteResponse:
    return create_note(db, current_user, payload)


@router.put("/notes/{note_id}", response_model=MeetingNoteResponse)
def update_meeting_note(
    note_id: Annotated[int, Path(gt=0)],
    payload: MeetingNoteUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_meeting_minutes_ai_db)],
) -> MeetingNoteResponse:
    return update_note(db, current_user, note_id, payload)


@router.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_meeting_note(
    note_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_meeting_minutes_ai_db)],
) -> None:
    delete_note(db, current_user, note_id)


@router.post(
    "/action-items",
    response_model=MeetingActionItemResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_meeting_action_item(
    payload: MeetingActionItemCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_meeting_minutes_ai_db)],
) -> MeetingActionItemResponse:
    return create_action_item(db, current_user, payload)


@router.put("/action-items/{action_item_id}", response_model=MeetingActionItemResponse)
def update_meeting_action_item(
    action_item_id: Annotated[int, Path(gt=0)],
    payload: MeetingActionItemUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_meeting_minutes_ai_db)],
) -> MeetingActionItemResponse:
    return update_action_item(db, current_user, action_item_id, payload)


@router.delete("/action-items/{action_item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_meeting_action_item(
    action_item_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_meeting_minutes_ai_db)],
) -> None:
    delete_action_item(db, current_user, action_item_id)


@router.post("/summaries", response_model=MeetingSummaryResponse, status_code=status.HTTP_201_CREATED)
def create_meeting_summary(
    payload: MeetingSummaryCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_meeting_minutes_ai_db)],
) -> MeetingSummaryResponse:
    return create_summary(db, current_user, payload)


@router.put("/summaries/{summary_id}", response_model=MeetingSummaryResponse)
def update_meeting_summary(
    summary_id: Annotated[int, Path(gt=0)],
    payload: MeetingSummaryUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_meeting_minutes_ai_db)],
) -> MeetingSummaryResponse:
    return update_summary(db, current_user, summary_id, payload)


@router.delete("/summaries/{summary_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_meeting_summary(
    summary_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_meeting_minutes_ai_db)],
) -> None:
    delete_summary(db, current_user, summary_id)
