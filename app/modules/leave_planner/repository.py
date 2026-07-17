from datetime import date
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload
from app.modules.leave_planner.models import LeaveEntry, LeaveType

def get_type(db, owner, id): return db.scalar(select(LeaveType).options(selectinload(LeaveType.entries)).where(LeaveType.id == id, LeaveType.owner_id == owner))
def get_type_by_name(db, owner, name, exclude=None):
    query=select(LeaveType).where(LeaveType.owner_id == owner, func.lower(LeaveType.name) == name.lower())
    if exclude: query=query.where(LeaveType.id != exclude)
    return db.scalar(query)
def list_types(db, owner): return list(db.scalars(select(LeaveType).options(selectinload(LeaveType.entries)).where(LeaveType.owner_id == owner).order_by(LeaveType.is_active.desc(), LeaveType.name)))
def get_entry(db, owner, id): return db.scalar(select(LeaveEntry).options(selectinload(LeaveEntry.leave_type)).where(LeaveEntry.id == id, LeaveEntry.owner_id == owner))
def list_entries(db: Session, owner: str, q, type_id, status, period, date_from, date_to, page, size):
    f=[LeaveEntry.owner_id == owner]
    if q:
        term=f"%{q.strip()}%"; f.append(or_(LeaveEntry.title.ilike(term), LeaveEntry.reason.ilike(term), LeaveEntry.notes.ilike(term), LeaveEntry.leave_type.has(LeaveType.name.ilike(term))))
    if type_id: f.append(LeaveEntry.leave_type_id == type_id)
    if status: f.append(LeaveEntry.status == status)
    today=date.today()
    if period == "upcoming": f.append(LeaveEntry.start_date > today)
    elif period == "current": f.extend([LeaveEntry.start_date <= today, LeaveEntry.end_date >= today])
    elif period == "past": f.append(LeaveEntry.end_date < today)
    if date_from: f.append(LeaveEntry.end_date >= date_from)
    if date_to: f.append(LeaveEntry.start_date <= date_to)
    total=db.scalar(select(func.count(LeaveEntry.id)).where(*f)) or 0
    items=list(db.scalars(select(LeaveEntry).options(selectinload(LeaveEntry.leave_type)).where(*f).order_by(LeaveEntry.start_date.desc(), LeaveEntry.created_at.desc()).offset((page-1)*size).limit(size)))
    return items,total
def overlaps(db, owner, start, end, exclude=None):
    q=select(LeaveEntry).where(LeaveEntry.owner_id==owner, LeaveEntry.status.notin_(["cancelled","rejected"]), LeaveEntry.start_date <= end, LeaveEntry.end_date >= start)
    if exclude: q=q.where(LeaveEntry.id != exclude)
    return list(db.scalars(q))
