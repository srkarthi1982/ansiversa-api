from math import ceil

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.meeting_scheduler import repository
from app.modules.meeting_scheduler.models import Meeting, MeetingAgendaItem, MeetingParticipant
from app.modules.meeting_scheduler.schemas import MeetingSchedulerAgendaItemCreateRequest, MeetingSchedulerAgendaItemUpdateRequest, MeetingSchedulerDashboardResponse, MeetingSchedulerMeetingCreateRequest, MeetingSchedulerMeetingDetailResponse, MeetingSchedulerMeetingListResponse, MeetingSchedulerMeetingResponse, MeetingSchedulerMeetingUpdateRequest, MeetingSchedulerParticipantCreateRequest, MeetingSchedulerParticipantUpdateRequest


def _owner(user: User) -> str:
    return str(user.id)


def _not_found(kind: str):
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{kind} not found.")


def _meeting_response(meeting: Meeting) -> MeetingSchedulerMeetingResponse:
    data = MeetingSchedulerMeetingResponse.model_validate(meeting)
    data.participant_count = len(meeting.participants) if "participants" in meeting.__dict__ else 0
    data.agenda_item_count = len(meeting.agenda_items) if "agenda_items" in meeting.__dict__ else 0
    return data


def list_meetings(db: Session, user: User, q, status_filter, period, page, page_size):
    items, total = repository.list_meetings(db, _owner(user), q, status_filter, period, page, page_size)
    return MeetingSchedulerMeetingListResponse(items=[_meeting_response(item) for item in items], total=total, page=page, page_size=page_size, pages=ceil(total / page_size) if total else 0)


def create_meeting(db: Session, user: User, payload: MeetingSchedulerMeetingCreateRequest):
    meeting = Meeting(owner_id=_owner(user), **payload.model_dump())
    db.add(meeting); db.commit(); db.refresh(meeting)
    return _meeting_response(meeting)


def get_meeting(db: Session, user: User, meeting_id: str):
    meeting = repository.get_meeting(db, _owner(user), meeting_id, True)
    if not meeting: _not_found("Meeting")
    meeting.participants.sort(key=lambda item: item.created_at)
    meeting.agenda_items.sort(key=lambda item: (item.sort_order, item.created_at))
    return MeetingSchedulerMeetingDetailResponse(**_meeting_response(meeting).model_dump(), participants=meeting.participants, agenda_items=meeting.agenda_items)


def update_meeting(db: Session, user: User, meeting_id: str, payload: MeetingSchedulerMeetingUpdateRequest):
    meeting = repository.get_meeting(db, _owner(user), meeting_id)
    if not meeting: _not_found("Meeting")
    for key, value in payload.model_dump().items(): setattr(meeting, key, value)
    db.commit(); db.refresh(meeting)
    return _meeting_response(meeting)


def delete_meeting(db: Session, user: User, meeting_id: str):
    meeting = repository.get_meeting(db, _owner(user), meeting_id)
    if not meeting: _not_found("Meeting")
    db.delete(meeting); db.commit()


def _owned_meeting(db, user, meeting_id):
    meeting = repository.get_meeting(db, _owner(user), meeting_id)
    if not meeting: _not_found("Meeting")
    return meeting


def create_participant(db, user, meeting_id, payload: MeetingSchedulerParticipantCreateRequest):
    _owned_meeting(db, user, meeting_id)
    item = MeetingParticipant(meeting_id=meeting_id, **payload.model_dump())
    db.add(item); db.commit(); db.refresh(item)
    return item


def list_participants(db, user, meeting_id):
    return get_meeting(db, user, meeting_id).participants


def update_participant(db, user, meeting_id, participant_id, payload: MeetingSchedulerParticipantUpdateRequest):
    _owned_meeting(db, user, meeting_id)
    item = repository.get_participant(db, meeting_id, participant_id)
    if not item: _not_found("Participant")
    for key, value in payload.model_dump().items(): setattr(item, key, value)
    db.commit(); db.refresh(item)
    return item


def delete_participant(db, user, meeting_id, participant_id):
    _owned_meeting(db, user, meeting_id)
    item = repository.get_participant(db, meeting_id, participant_id)
    if not item: _not_found("Participant")
    db.delete(item); db.commit()


def create_agenda_item(db, user, meeting_id, payload: MeetingSchedulerAgendaItemCreateRequest):
    _owned_meeting(db, user, meeting_id)
    item = MeetingAgendaItem(meeting_id=meeting_id, **payload.model_dump())
    db.add(item); db.commit(); db.refresh(item)
    return item


def list_agenda_items(db, user, meeting_id):
    return get_meeting(db, user, meeting_id).agenda_items


def update_agenda_item(db, user, meeting_id, item_id, payload: MeetingSchedulerAgendaItemUpdateRequest):
    _owned_meeting(db, user, meeting_id)
    item = repository.get_agenda_item(db, meeting_id, item_id)
    if not item: _not_found("Agenda item")
    for key, value in payload.model_dump().items(): setattr(item, key, value)
    db.commit(); db.refresh(item)
    return item


def delete_agenda_item(db, user, meeting_id, item_id):
    _owned_meeting(db, user, meeting_id)
    item = repository.get_agenda_item(db, meeting_id, item_id)
    if not item: _not_found("Agenda item")
    db.delete(item); db.commit()


def dashboard(db: Session, user: User):
    owner = _owner(user)
    meetings = list(db.scalars(select(Meeting).where(Meeting.owner_id == owner)))
    ids = [item.id for item in meetings]
    pending = db.scalar(select(func.count(MeetingParticipant.id)).where(MeetingParticipant.meeting_id.in_(ids), MeetingParticipant.response_status == "pending")) if ids else 0
    from datetime import date
    return MeetingSchedulerDashboardResponse(total_meetings=len(meetings), upcoming_meetings=sum(item.meeting_date >= date.today() and item.status not in {"completed", "cancelled"} for item in meetings), completed_meetings=sum(item.status == "completed" for item in meetings), pending_responses=pending or 0)
