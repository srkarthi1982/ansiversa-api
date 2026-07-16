from datetime import date,datetime,time,timedelta
from math import ceil
from fastapi import HTTPException
from sqlalchemy import case,func,or_,select
from sqlalchemy.orm import Session,selectinload
from .models import Errand,ErrandCategory
from .schemas import *
def fail(code,msg):raise HTTPException(code,msg)
def owned_errand(db,user,id):
 x=db.scalar(select(Errand).where(Errand.id==id,Errand.user_id==str(user.id)).options(selectinload(Errand.category)))
 if not x:fail(404,"Errand not found.")
 return x
def owned_category(db,user,id):
 x=db.scalar(select(ErrandCategory).where(ErrandCategory.id==id,ErrandCategory.user_id==str(user.id)))
 if not x:fail(404,"Category not found.")
 return x
def assert_mutable(x):
 if x.status=="archived":fail(409,"Archived errands are read-only until restored.")
def category_for(db,user,id):
 if not id:return None
 c=owned_category(db,user,id)
 return c
def flags(x):
 today=date.today();open_status=x.status in {"pending","in_progress"}
 return open_status and x.due_date is not None and x.due_date<today,open_status and x.due_date==today,open_status and x.due_date is not None and today<=x.due_date<=today+timedelta(days=7)
def summarize(x):
 overdue,due_today,due_soon=flags(x);c=x.category
 return ErrandSummary(id=x.id,title=x.title,description=x.description,category_id=x.category_id,category_name=c.name if c else None,category_color=c.color if c else None,priority=x.priority,due_date=x.due_date,estimated_minutes=x.estimated_minutes,location=x.location,status=x.status,notes=x.notes,is_overdue=overdue,is_due_today=due_today,is_due_soon=due_soon,created_at=x.created_at,updated_at=x.updated_at,completed_at=x.completed_at)
def category_response(db,c):
 count=db.scalar(select(func.count()).select_from(Errand).where(Errand.category_id==c.id)) or 0
 return CategoryResponse(id=c.id,name=c.name,color=c.color,sort_order=c.sort_order,errand_count=count,created_at=c.created_at,updated_at=c.updated_at)
def validate_status(p):
 if p.status=="completed" and p.due_date is None:pass
def save_errand(db,user,p,id=None):
 x=owned_errand(db,user,id) if id else Errand(user_id=str(user.id))
 if id:assert_mutable(x)
 category_for(db,user,p.category_id)
 if p.status=="archived" and (not id or x.status!="completed"):fail(409,"Only completed errands can be archived.")
 if id and x.status=="completed" and p.status not in {"completed","pending","in_progress","archived","cancelled"}:fail(409,"Completed errands can be reopened, archived, or cancelled.")
 for k,v in p.model_dump().items():setattr(x,k,v)
 if x.status=="completed" and not x.completed_at:x.completed_at=datetime.now()
 if x.status!="completed":x.completed_at=None
 if not id:db.add(x)
 db.commit();db.refresh(x);return get_errand(db,user,x.id)
def get_errand(db,user,id):return summarize(owned_errand(db,user,id))
def list_errands(db,user,qv=None,status=None,category_id=None,priority=None,overdue=None,due_today=None,due_soon=None,due_from=None,due_to=None,page=1,page_size=12):
 if due_from and due_to and due_from>due_to:fail(422,"Due-from date cannot be after due-to date.")
 stmt=select(Errand).where(Errand.user_id==str(user.id)).options(selectinload(Errand.category));term=(qv or "").strip()
 if term:stmt=stmt.where(or_(Errand.title.ilike(f"%{term}%"),Errand.description.ilike(f"%{term}%"),Errand.notes.ilike(f"%{term}%"),Errand.location.ilike(f"%{term}%")))
 if status:stmt=stmt.where(Errand.status==status)
 if category_id:category_for(db,user,category_id);stmt=stmt.where(Errand.category_id==category_id)
 if priority:stmt=stmt.where(Errand.priority==priority)
 today=date.today();open_status=["pending","in_progress"]
 if overdue:stmt=stmt.where(Errand.status.in_(open_status),Errand.due_date<today)
 if due_today:stmt=stmt.where(Errand.status.in_(open_status),Errand.due_date==today)
 if due_soon:stmt=stmt.where(Errand.status.in_(open_status),Errand.due_date.between(today,today+timedelta(days=7)))
 if due_from:stmt=stmt.where(Errand.due_date>=due_from)
 if due_to:stmt=stmt.where(Errand.due_date<=due_to)
 total=db.scalar(select(func.count()).select_from(stmt.order_by(None).subquery())) or 0;prio=case((Errand.priority=="high",0),(Errand.priority=="medium",1),else_=2);status_order=case((Errand.status=="in_progress",0),(Errand.status=="pending",1),(Errand.status=="completed",2),(Errand.status=="cancelled",3),else_=4);xs=db.scalars(stmt.order_by(status_order,Errand.due_date.asc().nulls_last(),prio,Errand.updated_at.desc()).offset((page-1)*page_size).limit(page_size)).unique().all();return ErrandList(items=[summarize(x) for x in xs],total=total,page=page,page_size=page_size,pages=max(1,ceil(total/page_size)))
def set_status(db,user,id,status):
 x=owned_errand(db,user,id)
 if status=="archived" and x.status!="completed":fail(409,"Only completed errands can be archived.")
 if status in {"pending","in_progress","completed","cancelled"} and x.status=="archived":fail(409,"Restore archived errands before changing status.")
 x.status=status;x.completed_at=datetime.now() if status=="completed" else None;db.commit();return get_errand(db,user,id)
def archive(db,user,id):return set_status(db,user,id,"archived")
def restore(db,user,id):
 x=owned_errand(db,user,id)
 if x.status!="archived":fail(409,"Only archived errands can be restored.")
 x.status="completed";db.commit();return get_errand(db,user,id)
def delete_errand(db,user,id):db.delete(owned_errand(db,user,id));db.commit()
def save_category(db,user,p,id=None):
 x=owned_category(db,user,id) if id else ErrandCategory(user_id=str(user.id))
 duplicate=db.scalar(select(ErrandCategory).where(ErrandCategory.user_id==str(user.id),func.lower(ErrandCategory.name)==p.name.lower(),ErrandCategory.id!=(id or "")))
 if duplicate:fail(409,"Category name already exists.")
 for k,v in p.model_dump().items():setattr(x,k,v)
 if not id:db.add(x)
 db.commit();db.refresh(x);return category_response(db,x)
def list_categories(db,user,qv=None,page=1,page_size=50):
 stmt=select(ErrandCategory).where(ErrandCategory.user_id==str(user.id));term=(qv or "").strip()
 if term:stmt=stmt.where(ErrandCategory.name.ilike(f"%{term}%"))
 total=db.scalar(select(func.count()).select_from(stmt.order_by(None).subquery())) or 0;xs=db.scalars(stmt.order_by(ErrandCategory.sort_order,ErrandCategory.name).offset((page-1)*page_size).limit(page_size)).all();return CategoryList(items=[category_response(db,x) for x in xs],total=total,page=page,page_size=page_size,pages=max(1,ceil(total/page_size)))
def delete_category(db,user,id):
 c=owned_category(db,user,id);count=db.scalar(select(func.count()).select_from(Errand).where(Errand.category_id==id)) or 0
 if count:fail(409,"Move or delete errands before deleting this category.")
 db.delete(c);db.commit()
def dashboard(db,user):
 xs=db.scalars(select(Errand).where(Errand.user_id==str(user.id)).options(selectinload(Errand.category)).order_by(Errand.updated_at.desc())).unique().all();counts={s:sum(x.status==s for x in xs) for s in ["pending","in_progress","completed","archived","cancelled"]};return Dashboard(**counts,overdue=sum(flags(x)[0] for x in xs),due_today=sum(flags(x)[1] for x in xs),due_soon=sum(flags(x)[2] for x in xs),total_active=sum(x.status!="archived" for x in xs),recent=[summarize(x) for x in xs[:5]])
