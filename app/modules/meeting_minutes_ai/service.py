from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from fastapi import HTTPException, status

from app.modules.auth.models import User
from app.modules.meeting_minutes_ai.models import (
    MeetingActionItem,
    MeetingNote,
    MeetingRecord,
    MeetingSummary,
)
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


def _get_owned_meeting(db: Session, user: User, meeting_id: int) -> MeetingRecord:
    meeting = db.get(MeetingRecord, meeting_id)
    if not meeting or meeting.owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting was not found.",
        )

    return meeting


def _get_owned_note(db: Session, user: User, note_id: int) -> MeetingNote:
    note = db.get(MeetingNote, note_id)
    if not note or note.owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting note was not found.",
        )

    return note


def _get_owned_action_item(db: Session, user: User, action_item_id: int) -> MeetingActionItem:
    action_item = db.get(MeetingActionItem, action_item_id)
    if not action_item or action_item.owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting action item was not found.",
        )

    return action_item


def _get_owned_summary(db: Session, user: User, summary_id: int) -> MeetingSummary:
    summary = db.get(MeetingSummary, summary_id)
    if not summary or summary.owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting summary was not found.",
        )

    return summary


def _count_for_meeting(db: Session, model: type[MeetingNote | MeetingActionItem | MeetingSummary], meeting_id: int) -> int:
    return int(
        db.execute(
            select(func.count()).select_from(model).where(model.meeting_id == meeting_id)
        ).scalar_one()
    )


def _meeting_response(db: Session, meeting: MeetingRecord) -> MeetingResponse:
    return MeetingResponse(
        id=meeting.id,
        title=meeting.title,
        meeting_date=meeting.meeting_date,
        participants=meeting.participants,
        context=meeting.context,
        status=meeting.status,
        note_count=_count_for_meeting(db, MeetingNote, meeting.id),
        action_item_count=_count_for_meeting(db, MeetingActionItem, meeting.id),
        summary_count=_count_for_meeting(db, MeetingSummary, meeting.id),
        created_at=meeting.created_at,
        updated_at=meeting.updated_at,
    )


def _note_response(note: MeetingNote, meeting_title: str) -> MeetingNoteResponse:
    return MeetingNoteResponse(
        id=note.id,
        meeting_id=note.meeting_id,
        meeting_title=meeting_title,
        note_type=note.note_type,
        content=note.content,
        created_at=note.created_at,
        updated_at=note.updated_at,
    )


def _action_item_response(
    action_item: MeetingActionItem,
    meeting_title: str,
) -> MeetingActionItemResponse:
    return MeetingActionItemResponse(
        id=action_item.id,
        meeting_id=action_item.meeting_id,
        meeting_title=meeting_title,
        title=action_item.title,
        owner_name=action_item.owner_name,
        due_date=action_item.due_date,
        status=action_item.status,
        created_at=action_item.created_at,
        updated_at=action_item.updated_at,
    )


def _summary_response(summary: MeetingSummary, meeting_title: str) -> MeetingSummaryResponse:
    return MeetingSummaryResponse(
        id=summary.id,
        meeting_id=summary.meeting_id,
        meeting_title=meeting_title,
        summary_text=summary.summary_text,
        decisions=summary.decisions,
        risks=summary.risks,
        created_at=summary.created_at,
        updated_at=summary.updated_at,
    )


def list_meetings(db: Session, user: User) -> list[MeetingResponse]:
    meetings = list(
        db.execute(
            select(MeetingRecord)
            .where(MeetingRecord.owner_id == user.id)
            .order_by(MeetingRecord.updated_at.desc(), MeetingRecord.title.asc())
        )
        .scalars()
        .all()
    )
    return [_meeting_response(db, meeting) for meeting in meetings]


def create_meeting(
    db: Session,
    user: User,
    payload: MeetingCreateRequest,
) -> MeetingResponse:
    meeting = MeetingRecord(
        owner_id=user.id,
        title=payload.title,
        meeting_date=payload.meeting_date,
        participants=payload.participants,
        context=payload.context,
        status="draft",
    )
    db.add(meeting)
    db.commit()
    db.refresh(meeting)

    return _meeting_response(db, meeting)


def update_meeting(
    db: Session,
    user: User,
    meeting_id: int,
    payload: MeetingUpdateRequest,
) -> MeetingResponse:
    meeting = _get_owned_meeting(db, user, meeting_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(meeting, field, value)
    db.commit()
    db.refresh(meeting)

    return _meeting_response(db, meeting)


def delete_meeting(db: Session, user: User, meeting_id: int) -> None:
    meeting = _get_owned_meeting(db, user, meeting_id)
    db.execute(delete(MeetingSummary).where(MeetingSummary.meeting_id == meeting.id))
    db.execute(delete(MeetingActionItem).where(MeetingActionItem.meeting_id == meeting.id))
    db.execute(delete(MeetingNote).where(MeetingNote.meeting_id == meeting.id))
    db.delete(meeting)
    db.commit()


def list_notes(db: Session, user: User) -> list[MeetingNoteResponse]:
    rows = db.execute(
        select(MeetingNote, MeetingRecord.title)
        .join(MeetingRecord, MeetingRecord.id == MeetingNote.meeting_id)
        .where(MeetingNote.owner_id == user.id)
        .order_by(MeetingNote.updated_at.desc())
    ).all()

    return [_note_response(note, title) for note, title in rows]


def create_note(db: Session, user: User, payload: MeetingNoteCreateRequest) -> MeetingNoteResponse:
    meeting = _get_owned_meeting(db, user, payload.meeting_id)
    note = MeetingNote(
        owner_id=user.id,
        meeting_id=meeting.id,
        note_type=payload.note_type,
        content=payload.content,
    )
    if meeting.status == "draft":
        meeting.status = "capturing"
    db.add(note)
    db.commit()
    db.refresh(note)

    return _note_response(note, meeting.title)


def update_note(
    db: Session,
    user: User,
    note_id: int,
    payload: MeetingNoteUpdateRequest,
) -> MeetingNoteResponse:
    note = _get_owned_note(db, user, note_id)
    meeting = _get_owned_meeting(db, user, note.meeting_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(note, field, value)
    db.commit()
    db.refresh(note)

    return _note_response(note, meeting.title)


def delete_note(db: Session, user: User, note_id: int) -> None:
    note = _get_owned_note(db, user, note_id)
    db.delete(note)
    db.commit()


def list_action_items(db: Session, user: User) -> list[MeetingActionItemResponse]:
    rows = db.execute(
        select(MeetingActionItem, MeetingRecord.title)
        .join(MeetingRecord, MeetingRecord.id == MeetingActionItem.meeting_id)
        .where(MeetingActionItem.owner_id == user.id)
        .order_by(MeetingActionItem.updated_at.desc())
    ).all()

    return [_action_item_response(action_item, title) for action_item, title in rows]


def create_action_item(
    db: Session,
    user: User,
    payload: MeetingActionItemCreateRequest,
) -> MeetingActionItemResponse:
    meeting = _get_owned_meeting(db, user, payload.meeting_id)
    action_item = MeetingActionItem(
        owner_id=user.id,
        meeting_id=meeting.id,
        title=payload.title,
        owner_name=payload.owner_name,
        due_date=payload.due_date,
        status=payload.status,
    )
    if meeting.status == "draft":
        meeting.status = "capturing"
    db.add(action_item)
    db.commit()
    db.refresh(action_item)

    return _action_item_response(action_item, meeting.title)


def update_action_item(
    db: Session,
    user: User,
    action_item_id: int,
    payload: MeetingActionItemUpdateRequest,
) -> MeetingActionItemResponse:
    action_item = _get_owned_action_item(db, user, action_item_id)
    meeting = _get_owned_meeting(db, user, action_item.meeting_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(action_item, field, value)
    db.commit()
    db.refresh(action_item)

    return _action_item_response(action_item, meeting.title)


def delete_action_item(db: Session, user: User, action_item_id: int) -> None:
    action_item = _get_owned_action_item(db, user, action_item_id)
    db.delete(action_item)
    db.commit()


def list_summaries(db: Session, user: User) -> list[MeetingSummaryResponse]:
    rows = db.execute(
        select(MeetingSummary, MeetingRecord.title)
        .join(MeetingRecord, MeetingRecord.id == MeetingSummary.meeting_id)
        .where(MeetingSummary.owner_id == user.id)
        .order_by(MeetingSummary.updated_at.desc())
    ).all()

    return [_summary_response(summary, title) for summary, title in rows]


def create_summary(
    db: Session,
    user: User,
    payload: MeetingSummaryCreateRequest,
) -> MeetingSummaryResponse:
    meeting = _get_owned_meeting(db, user, payload.meeting_id)
    summary = MeetingSummary(
        owner_id=user.id,
        meeting_id=meeting.id,
        summary_text=payload.summary_text,
        decisions=payload.decisions,
        risks=payload.risks,
    )
    meeting.status = "reviewed"
    db.add(summary)
    db.commit()
    db.refresh(summary)

    return _summary_response(summary, meeting.title)


def update_summary(
    db: Session,
    user: User,
    summary_id: int,
    payload: MeetingSummaryUpdateRequest,
) -> MeetingSummaryResponse:
    summary = _get_owned_summary(db, user, summary_id)
    meeting = _get_owned_meeting(db, user, summary.meeting_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(summary, field, value)
    db.commit()
    db.refresh(summary)

    return _summary_response(summary, meeting.title)


def delete_summary(db: Session, user: User, summary_id: int) -> None:
    summary = _get_owned_summary(db, user, summary_id)
    db.delete(summary)
    db.commit()


def get_dashboard(db: Session, user: User) -> MeetingMinutesDashboardResponse:
    meetings = list_meetings(db, user)
    notes = list_notes(db, user)
    action_items = list_action_items(db, user)
    summaries = list_summaries(db, user)

    return MeetingMinutesDashboardResponse(
        meetings=meetings,
        notes=notes,
        action_items=action_items,
        summaries=summaries,
        open_action_count=len([item for item in action_items if item.status != "done"]),
        reviewed_meeting_count=len([meeting for meeting in meetings if meeting.status == "reviewed"]),
        transcript_count=len([note for note in notes if note.note_type == "transcript"]),
    )
