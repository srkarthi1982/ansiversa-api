from datetime import date,datetime,timedelta
from sqlalchemy import func,or_,select
from sqlalchemy.orm import selectinload
from app.modules.shift_planner.models import Shift,ShiftMember,ShiftType
def get_type(db,owner,id): return db.scalar(select(ShiftType).options(selectinload(ShiftType.shifts)).where(ShiftType.id==id,ShiftType.owner_id==owner))
def type_with_name(db,owner,name,exclude=None):
    q=select(ShiftType).where(ShiftType.owner_id==owner,func.lower(ShiftType.name)==name.casefold())
    if exclude:q=q.where(ShiftType.id!=exclude)
    return db.scalar(q)
def types(db,owner): return list(db.scalars(select(ShiftType).options(selectinload(ShiftType.shifts)).where(ShiftType.owner_id==owner).order_by(ShiftType.is_active.desc(),ShiftType.name)))
def get_member(db,owner,id): return db.scalar(select(ShiftMember).options(selectinload(ShiftMember.shifts)).where(ShiftMember.id==id,ShiftMember.owner_id==owner))
def members(db,owner): return list(db.scalars(select(ShiftMember).options(selectinload(ShiftMember.shifts)).where(ShiftMember.owner_id==owner).order_by(ShiftMember.is_active.desc(),ShiftMember.name)))
def get_shift(db,owner,id): return db.scalar(select(Shift).options(selectinload(Shift.shift_type),selectinload(Shift.member)).where(Shift.id==id,Shift.owner_id==owner))
def shifts(db,owner,q,type_id,member_id,status,period,date_from,date_to,page,size):
    f=[Shift.owner_id==owner]
    if q:
        term=f"%{q.strip()}%"; f.append(or_(Shift.title.ilike(term),Shift.location.ilike(term),Shift.notes.ilike(term),Shift.shift_type.has(ShiftType.name.ilike(term)),Shift.member.has(ShiftMember.name.ilike(term))))
    if type_id:f.append(Shift.shift_type_id==type_id)
    if member_id:f.append(Shift.member_id==member_id)
    if status:f.append(Shift.status==status)
    today=date.today()
    if period=="upcoming":f.append(Shift.shift_date>today)
    elif period=="current":f.append(Shift.shift_date==today)
    elif period=="past":f.append(Shift.shift_date<today)
    if date_from:f.append(Shift.shift_date>=date_from)
    if date_to:f.append(Shift.shift_date<=date_to)
    total=db.scalar(select(func.count(Shift.id)).where(*f)) or 0
    order=Shift.shift_date.asc() if period=="upcoming" else Shift.shift_date.desc()
    items=list(db.scalars(select(Shift).options(selectinload(Shift.shift_type),selectinload(Shift.member)).where(*f).order_by(order,Shift.start_time).offset((page-1)*size).limit(size)))
    return items,total
def member_shifts(db,owner,member_id,exclude=None):
    q=select(Shift).where(Shift.owner_id==owner,Shift.member_id==member_id,Shift.status!="cancelled")
    if exclude:q=q.where(Shift.id!=exclude)
    return list(db.scalars(q))
