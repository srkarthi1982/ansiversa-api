from datetime import date

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.modules.meeting_scheduler.models import Meeting, MeetingAgendaItem, MeetingParticipant


def get_meeting(db: Session, owner_id: str, meeting_id: str, detail: bool = False):
    query = select(Meeting).where(Meeting.id == meeting_id, Meeting.owner_id == owner_id)
    if detail:
        query = query.options(selectinload(Meeting.participants), selectinload(Meeting.agenda_items))
    return db.scalar(query)


def list_meetings(db: Session, owner_id: str, q: str | None, status: str | None, period: str, page: int, page_size: int):
    filters = [Meeting.owner_id == owner_id]
    if q:
        term = f"%{q.strip()}%"
        filters.append(or_(Meeting.title.ilike(term), Meeting.description.ilike(term), Meeting.location.ilike(term)))
    if status:
        filters.append(Meeting.status == status)
    if period == "upcoming":
        filters.append(Meeting.meeting_date >= date.today())
    elif period == "past":
        filters.append(Meeting.meeting_date < date.today())
    total = db.scalar(select(func.count(Meeting.id)).where(*filters)) or 0
    items = list(db.scalars(select(Meeting).options(selectinload(Meeting.participants), selectinload(Meeting.agenda_items)).where(*filters).order_by(Meeting.meeting_date.desc(), Meeting.start_time.desc()).offset((page - 1) * page_size).limit(page_size)))
    return items, total


def get_participant(db: Session, meeting_id: str, participant_id: str):
    return db.scalar(select(MeetingParticipant).where(MeetingParticipant.id == participant_id, MeetingParticipant.meeting_id == meeting_id))


def get_agenda_item(db: Session, meeting_id: str, item_id: str):
    return db.scalar(select(MeetingAgendaItem).where(MeetingAgendaItem.id == item_id, MeetingAgendaItem.meeting_id == meeting_id))
