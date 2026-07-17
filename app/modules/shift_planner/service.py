from datetime import date,datetime,timedelta
from math import ceil
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.modules.shift_planner import repository as r
from app.modules.shift_planner.models import Shift,ShiftMember,ShiftType
from app.modules.shift_planner.schemas import Dashboard,MemberResponse,ShiftList,ShiftResponse,TypeResponse
def owner(u):return str(u.id)
def missing(k):raise HTTPException(404,f"{k} not found.")
def interval(d,start,end):
    a=datetime.combine(d,start); b=datetime.combine(d,end)
    if b<=a:b+=timedelta(days=1)
    return a,b
def duration(d,start,end,break_minutes):
    a,b=interval(d,start,end); total=int((b-a).total_seconds()/60)
    if break_minutes>=total:raise HTTPException(422,"Break must be shorter than the shift duration.")
    return total-break_minutes
def tr(x):return TypeResponse(name=x.name,code=x.code,description=x.description,default_start_time=x.default_start_time,default_end_time=x.default_end_time,default_break_minutes=x.default_break_minutes,color_key=x.color_key,is_active=x.is_active,id=x.id,shift_count=len(x.shifts),created_at=x.created_at,updated_at=x.updated_at)
def mr(x):return MemberResponse(name=x.name,email=x.email,phone=x.phone,role=x.role,notes=x.notes,is_active=x.is_active,id=x.id,shift_count=len(x.shifts),created_at=x.created_at,updated_at=x.updated_at)
def sr(x):return ShiftResponse(shift_type_id=x.shift_type_id,member_id=x.member_id,title=x.title,shift_date=x.shift_date,start_time=x.start_time,end_time=x.end_time,break_minutes=x.break_minutes,location=x.location,status=x.status,notes=x.notes,id=x.id,shift_type_name=x.shift_type.name,member_name=x.member.name if x.member else None,duration_minutes=x.duration_minutes,is_overnight=x.end_time<=x.start_time,created_at=x.created_at,updated_at=x.updated_at)
def list_types(db,u):return [tr(x) for x in r.types(db,owner(u))]
def save_type(db,u,p,id=None):
    if r.type_with_name(db,owner(u),p.name,id):raise HTTPException(409,"A shift type with this name already exists.")
    x=r.get_type(db,owner(u),id) if id else ShiftType(owner_id=owner(u))
    if id and not x:missing("Shift type")
    for k,v in p.model_dump().items():setattr(x,k,v)
    if not id:db.add(x)
    try:db.commit()
    except IntegrityError:db.rollback();raise HTTPException(409,"A shift type with this name already exists.")
    return tr(r.get_type(db,owner(u),x.id))
def delete_type(db,u,id):
    x=r.get_type(db,owner(u),id)
    if not x:missing("Shift type")
    if x.shifts:raise HTTPException(409,"Shift types with history cannot be deleted. Deactivate this type instead.")
    db.delete(x);db.commit()
def list_members(db,u):return [mr(x) for x in r.members(db,owner(u))]
def save_member(db,u,p,id=None):
    x=r.get_member(db,owner(u),id) if id else ShiftMember(owner_id=owner(u))
    if id and not x:missing("Member")
    for k,v in p.model_dump().items():setattr(x,k,v)
    if not id:db.add(x)
    db.commit();return mr(r.get_member(db,owner(u),x.id))
def delete_member(db,u,id):
    x=r.get_member(db,owner(u),id)
    if not x:missing("Member")
    if x.shifts:raise HTTPException(409,"Members with shift history cannot be deleted. Deactivate this member instead.")
    db.delete(x);db.commit()
def list_shifts(db,u,q,type_id,member_id,status,period,date_from,date_to,page,size):
    items,total=r.shifts(db,owner(u),q,type_id,member_id,status,period,date_from,date_to,page,size)
    return ShiftList(items=[sr(x) for x in items],total=total,page=page,page_size=size,pages=ceil(total/size) if total else 0)
def save_shift(db,u,p,id=None):
    t=r.get_type(db,owner(u),p.shift_type_id)
    if not t:missing("Shift type")
    if not t.is_active and not id:raise HTTPException(409,"Inactive shift types cannot be used for new shifts.")
    m=r.get_member(db,owner(u),p.member_id) if p.member_id else None
    if p.member_id and not m:missing("Member")
    if m and not m.is_active and not id:raise HTTPException(409,"Inactive members cannot be assigned to new shifts.")
    a,b=interval(p.shift_date,p.start_time,p.end_time)
    if p.member_id and p.status!="cancelled":
        for other in r.member_shifts(db,owner(u),p.member_id,id):
            oa,ob=interval(other.shift_date,other.start_time,other.end_time)
            if a<ob and b>oa:raise HTTPException(409,"This member already has an overlapping shift.")
    x=r.get_shift(db,owner(u),id) if id else Shift(owner_id=owner(u))
    if id and not x:missing("Shift")
    for k,v in p.model_dump().items():setattr(x,k,v)
    x.duration_minutes=duration(p.shift_date,p.start_time,p.end_time,p.break_minutes)
    if not id:db.add(x)
    db.commit();return sr(r.get_shift(db,owner(u),x.id))
def get_shift(db,u,id):
    x=r.get_shift(db,owner(u),id)
    if not x:missing("Shift")
    return sr(x)
def delete_shift(db,u,id):
    x=r.get_shift(db,owner(u),id)
    if not x:missing("Shift")
    db.delete(x);db.commit()
def dashboard(db,u):
    items=list(db.scalars(select(Shift).where(Shift.owner_id==owner(u)))); today=date.today(); active=len([x for x in r.members(db,owner(u)) if x.is_active])
    return Dashboard(total_shifts=len(items),upcoming_shifts=sum(x.shift_date>=today and x.status=="scheduled" for x in items),completed_shifts=sum(x.status=="completed" for x in items),cancelled_shifts=sum(x.status=="cancelled" for x in items),scheduled_hours=round(sum(x.duration_minutes for x in items if x.status=="scheduled" and x.shift_date>=today)/60,2),completed_hours=round(sum(x.duration_minutes for x in items if x.status=="completed")/60,2),active_members=active)
