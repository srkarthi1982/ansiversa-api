from math import ceil
from fastapi import HTTPException
from sqlalchemy import case,func,or_,select
from sqlalchemy.orm import selectinload
from .models import ChecklistCategory,ChecklistItem,EmergencyChecklist
from .schemas import *
def fail(code,msg):raise HTTPException(code,msg)
def owned_category(db,user,id):
 x=db.scalar(select(ChecklistCategory).where(ChecklistCategory.id==id,ChecklistCategory.user_id==str(user.id)))
 if not x:fail(404,"Category not found.")
 return x
def category_for(db,user,id):
 if not id:return None
 return owned_category(db,user,id)
def owned_checklist(db,user,id):
 x=db.scalar(select(EmergencyChecklist).where(EmergencyChecklist.id==id,EmergencyChecklist.user_id==str(user.id)).options(selectinload(EmergencyChecklist.category),selectinload(EmergencyChecklist.items)))
 if not x:fail(404,"Checklist not found.")
 return x
def owned_item(db,user,checklist_id,item_id):
 checklist=owned_checklist(db,user,checklist_id)
 for item in checklist.items:
  if item.id==item_id:return checklist,item
 fail(404,"Checklist item not found.")
def ensure_mutable(x):
 if x.archived:fail(409,"Archived checklists are read-only until restored.")
def counts(x):
 total=len(x.items);done=sum(i.completed for i in x.items);pct=round(done*100/total) if total else 0
 return total,done,total-done,pct
def checklist_response(x,detail=False):
 c=x.category;total,done,remaining,pct=counts(x)
 base=EmergencyChecklistSummary(id=x.id,title=x.title,category_id=x.category_id,category_name=c.name if c else None,category_color=c.color if c else None,description=x.description,archived=x.archived,total_items=total,completed_items=done,remaining_items=remaining,completion_percentage=pct,created_at=x.created_at,updated_at=x.updated_at)
 if not detail:return base
 return EmergencyChecklistDetail(**base.model_dump(),items=[item_response(i) for i in sorted(x.items,key=lambda i:(i.sort_order,i.title))])
def item_response(x):return ChecklistItemResponse(id=x.id,checklist_id=x.checklist_id,title=x.title,notes=x.notes,completed=x.completed,sort_order=x.sort_order,created_at=x.created_at,updated_at=x.updated_at)
def category_response(db,c):
 count=db.scalar(select(func.count()).select_from(EmergencyChecklist).where(EmergencyChecklist.category_id==c.id)) or 0
 return EmergencyCategoryResponse(id=c.id,name=c.name,color=c.color,sort_order=c.sort_order,checklist_count=count,created_at=c.created_at,updated_at=c.updated_at)
def duplicate_checklist(db,user,p,id=None):
 stmt=select(EmergencyChecklist).where(EmergencyChecklist.user_id==str(user.id),func.lower(EmergencyChecklist.title)==p.title.lower(),EmergencyChecklist.category_id==p.category_id)
 if id:stmt=stmt.where(EmergencyChecklist.id!=id)
 if db.scalar(stmt):fail(409,"Checklist already exists in this category.")
def save_checklist(db,user,p,id=None):
 x=owned_checklist(db,user,id) if id else EmergencyChecklist(user_id=str(user.id))
 if id:ensure_mutable(x)
 category_for(db,user,p.category_id);duplicate_checklist(db,user,p,id)
 for k,v in p.model_dump().items():setattr(x,k,v)
 if not id:db.add(x)
 db.commit();db.refresh(x);return get_checklist(db,user,x.id)
def get_checklist(db,user,id):return checklist_response(owned_checklist(db,user,id),True)
def list_checklists(db,user,qv=None,category_id=None,archived=None,completion=None,page=1,page_size=12):
 stmt=select(EmergencyChecklist).where(EmergencyChecklist.user_id==str(user.id)).options(selectinload(EmergencyChecklist.category),selectinload(EmergencyChecklist.items));term=(qv or "").strip()
 if term:
  item_ids=select(ChecklistItem.checklist_id).where(ChecklistItem.title.ilike(f"%{term}%"))
  stmt=stmt.where(or_(EmergencyChecklist.title.ilike(f"%{term}%"),EmergencyChecklist.description.ilike(f"%{term}%"),EmergencyChecklist.id.in_(item_ids)))
 if category_id:category_for(db,user,category_id);stmt=stmt.where(EmergencyChecklist.category_id==category_id)
 if archived is not None:stmt=stmt.where(EmergencyChecklist.archived==archived)
 xs=db.scalars(stmt.order_by(EmergencyChecklist.updated_at.desc())).unique().all()
 if completion=="completed":xs=[x for x in xs if counts(x)[0]>0 and counts(x)[3]==100]
 if completion=="incomplete":xs=[x for x in xs if counts(x)[3]<100]
 total=len(xs);start=(page-1)*page_size;page_xs=xs[start:start+page_size]
 return EmergencyChecklistList(items=[checklist_response(x) for x in page_xs],total=total,page=page,page_size=page_size,pages=max(1,ceil(total/page_size)))
def delete_checklist(db,user,id):
 x=owned_checklist(db,user,id);ensure_mutable(x);db.delete(x);db.commit()
def archive(db,user,id):
 x=owned_checklist(db,user,id);ensure_mutable(x);x.archived=True;db.commit();return get_checklist(db,user,id)
def restore(db,user,id):
 x=owned_checklist(db,user,id);x.archived=False;db.commit();return get_checklist(db,user,id)
def reset(db,user,id):
 x=owned_checklist(db,user,id);ensure_mutable(x)
 for item in x.items:item.completed=False
 db.commit();return get_checklist(db,user,id)
def complete_all(db,user,id):
 x=owned_checklist(db,user,id);ensure_mutable(x)
 for item in x.items:item.completed=True
 db.commit();return get_checklist(db,user,id)
def save_item(db,user,checklist_id,p,item_id=None):
 checklist=owned_checklist(db,user,checklist_id);ensure_mutable(checklist)
 item=owned_item(db,user,checklist_id,item_id)[1] if item_id else ChecklistItem(checklist_id=checklist.id)
 for k,v in p.model_dump().items():setattr(item,k,v)
 if not item_id:db.add(item)
 db.commit();return get_checklist(db,user,checklist_id)
def toggle_item(db,user,checklist_id,item_id,completed):
 checklist,item=owned_item(db,user,checklist_id,item_id);ensure_mutable(checklist);item.completed=completed;db.commit();return get_checklist(db,user,checklist_id)
def delete_item(db,user,checklist_id,item_id):
 checklist,item=owned_item(db,user,checklist_id,item_id);ensure_mutable(checklist);db.delete(item);db.commit();return get_checklist(db,user,checklist_id)
def save_category(db,user,p,id=None):
 x=owned_category(db,user,id) if id else ChecklistCategory(user_id=str(user.id))
 duplicate=db.scalar(select(ChecklistCategory).where(ChecklistCategory.user_id==str(user.id),func.lower(ChecklistCategory.name)==p.name.lower(),ChecklistCategory.id!=(id or "")))
 if duplicate:fail(409,"Category name already exists.")
 for k,v in p.model_dump().items():setattr(x,k,v)
 if not id:db.add(x)
 db.commit();db.refresh(x);return category_response(db,x)
def list_categories(db,user,qv=None,page=1,page_size=50):
 stmt=select(ChecklistCategory).where(ChecklistCategory.user_id==str(user.id));term=(qv or "").strip()
 if term:stmt=stmt.where(ChecklistCategory.name.ilike(f"%{term}%"))
 total=db.scalar(select(func.count()).select_from(stmt.order_by(None).subquery())) or 0;xs=db.scalars(stmt.order_by(ChecklistCategory.sort_order,ChecklistCategory.name).offset((page-1)*page_size).limit(page_size)).all();return EmergencyCategoryList(items=[category_response(db,x) for x in xs],total=total,page=page,page_size=page_size,pages=max(1,ceil(total/page_size)))
def delete_category(db,user,id):
 c=owned_category(db,user,id);count=db.scalar(select(func.count()).select_from(EmergencyChecklist).where(EmergencyChecklist.category_id==id)) or 0
 if count:fail(409,"Move or delete checklists before deleting this category.")
 db.delete(c);db.commit()
def dashboard(db,user):
 xs=db.scalars(select(EmergencyChecklist).where(EmergencyChecklist.user_id==str(user.id)).options(selectinload(EmergencyChecklist.category),selectinload(EmergencyChecklist.items)).order_by(EmergencyChecklist.updated_at.desc())).unique().all();active=[x for x in xs if not x.archived];cats=db.scalar(select(func.count()).select_from(ChecklistCategory).where(ChecklistCategory.user_id==str(user.id))) or 0
 return EmergencyDashboard(total_checklists=len(active),archived=sum(x.archived for x in xs),completed=sum(counts(x)[0]>0 and counts(x)[3]==100 for x in active),incomplete=sum(counts(x)[3]<100 for x in active),categories=cats,recent=[checklist_response(x) for x in xs[:5]])
