from datetime import date, timedelta
from math import ceil
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.modules.leave_planner import repository
from app.modules.leave_planner.models import LeaveEntry, LeaveType
from app.modules.leave_planner.schemas import *

def owner(user): return str(user.id)
def missing(kind): raise HTTPException(404, f"{kind} not found.")
def duration(start, end, day_type):
    if day_type != "full_day":
        if start.weekday() >= 5: raise HTTPException(422, "Half-day leave must fall on a weekday.")
        return 0.5
    count=0; current=start
    while current <= end:
        if current.weekday() < 5: count += 1
        current += timedelta(days=1)
    if count == 0: raise HTTPException(422, "Leave range must include at least one weekday.")
    return float(count)
def type_response(item):
    used=sum(x.duration_days for x in item.entries if x.status in {"approved","taken"}); planned=sum(x.duration_days for x in item.entries if x.status in {"planned","pending"}); allowance=item.annual_allowance_days+item.carry_forward_days
    return LeavePlannerTypeResponse(name=item.name,code=item.code,description=item.description,annual_allowance_days=item.annual_allowance_days,carry_forward_days=item.carry_forward_days,color_key=item.color_key,is_active=item.is_active,id=item.id,used_days=used,planned_days=planned,remaining_days=allowance-used,entry_count=len(item.entries),created_at=item.created_at,updated_at=item.updated_at)
def entry_response(item): return LeavePlannerEntryResponse(leave_type_id=item.leave_type_id,title=item.title,start_date=item.start_date,end_date=item.end_date,day_type=item.day_type,status=item.status,reason=item.reason,notes=item.notes,id=item.id,leave_type_name=item.leave_type.name,duration_days=item.duration_days,created_at=item.created_at,updated_at=item.updated_at)
def list_types(db,user): return [type_response(x) for x in repository.list_types(db,owner(user))]
def create_type(db,user,payload):
    if repository.get_type_by_name(db,owner(user),payload.name): raise HTTPException(409,"A leave type with this name already exists.")
    item=LeaveType(owner_id=owner(user),**payload.model_dump()); db.add(item)
    try: db.commit()
    except IntegrityError: db.rollback(); raise HTTPException(409,"A leave type with this name already exists.")
    return type_response(repository.get_type(db,owner(user),item.id))
def update_type(db,user,id,payload):
    item=repository.get_type(db,owner(user),id)
    if not item: missing("Leave type")
    if repository.get_type_by_name(db,owner(user),payload.name,id): raise HTTPException(409,"A leave type with this name already exists.")
    for k,v in payload.model_dump().items(): setattr(item,k,v)
    try: db.commit()
    except IntegrityError: db.rollback(); raise HTTPException(409,"A leave type with this name already exists.")
    return type_response(repository.get_type(db,owner(user),id))
def delete_type(db,user,id):
    item=repository.get_type(db,owner(user),id)
    if not item: missing("Leave type")
    if item.entries: raise HTTPException(409,"Leave types with history cannot be deleted. Deactivate this type instead.")
    db.delete(item); db.commit()
def list_entries(db,user,q,type_id,status,period,date_from,date_to,page,size):
    items,total=repository.list_entries(db,owner(user),q,type_id,status,period,date_from,date_to,page,size)
    return LeavePlannerEntryListResponse(items=[entry_response(x) for x in items],total=total,page=page,page_size=size,pages=ceil(total/size) if total else 0)
def save_entry(db,user,payload,id=None):
    item=repository.get_entry(db,owner(user),id) if id else None
    if id and not item: missing("Leave entry")
    leave_type=repository.get_type(db,owner(user),payload.leave_type_id)
    if not leave_type: missing("Leave type")
    if not leave_type.is_active and (not item or item.leave_type_id != leave_type.id): raise HTTPException(409,"Inactive leave types cannot be used for new entries.")
    conflicts=repository.overlaps(db,owner(user),payload.start_date,payload.end_date,id)
    for conflict in conflicts:
        opposite_same_day_halves=(payload.start_date==payload.end_date==conflict.start_date==conflict.end_date and payload.day_type in {"first_half","second_half"} and conflict.day_type in {"first_half","second_half"} and payload.day_type != conflict.day_type)
        if not opposite_same_day_halves: raise HTTPException(409,"This leave overlaps another active leave entry.")
    item=item or LeaveEntry(owner_id=owner(user))
    for k,v in payload.model_dump().items(): setattr(item,k,v)
    item.duration_days=duration(payload.start_date,payload.end_date,payload.day_type)
    if not id: db.add(item)
    db.commit(); return entry_response(repository.get_entry(db,owner(user),item.id))
def get_entry(db,user,id):
    item=repository.get_entry(db,owner(user),id)
    if not item: missing("Leave entry")
    return entry_response(item)
def delete_entry(db,user,id):
    item=repository.get_entry(db,owner(user),id)
    if not item: missing("Leave entry")
    db.delete(item); db.commit()
def dashboard(db,user):
    types=repository.list_types(db,owner(user)); entries=list(db.scalars(select(LeaveEntry).where(LeaveEntry.owner_id==owner(user))))
    allowance=sum(x.annual_allowance_days+x.carry_forward_days for x in types); used=sum(x.duration_days for x in entries if x.status in {"approved","taken"}); planned=sum(x.duration_days for x in entries if x.status in {"planned","pending"})
    return LeavePlannerDashboardResponse(total_allowance=allowance,used_leave=used,planned_leave=planned,remaining_leave=allowance-used,upcoming_count=sum(x.start_date>date.today() and x.status not in {"cancelled","rejected"} for x in entries))
