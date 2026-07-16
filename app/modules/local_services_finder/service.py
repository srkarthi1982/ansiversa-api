from datetime import date,datetime,time,timedelta
from math import ceil
from fastapi import HTTPException
from sqlalchemy import case,func,or_,select
from sqlalchemy.orm import Session,selectinload
from .models import ServiceCategory,ServiceProvider
from .schemas import *
def fail(code,msg):raise HTTPException(code,msg)
def category_for(db,user,id):
 if not id:return None
 c=db.scalar(select(ServiceCategory).where(ServiceCategory.id==id,ServiceCategory.user_id==str(user.id)))
 if not c:fail(404,"Category not found.")
 return c
def owned_provider(db,user,id):
 x=db.scalar(select(ServiceProvider).where(ServiceProvider.id==id,ServiceProvider.user_id==str(user.id)).options(selectinload(ServiceProvider.category)))
 if not x:fail(404,"Provider not found.")
 return x
def owned_category(db,user,id):
 x=db.scalar(select(ServiceCategory).where(ServiceCategory.id==id,ServiceCategory.user_id==str(user.id)))
 if not x:fail(404,"Category not found.")
 return x
def ensure_mutable(x):
 if x.archived:fail(409,"Archived providers are read-only until restored.")
def duplicate_provider(db,user,p,id=None):
 stmt=select(ServiceProvider).where(ServiceProvider.user_id==str(user.id),func.lower(ServiceProvider.business_name)==p.business_name.lower(),ServiceProvider.category_id==p.category_id)
 if id:stmt=stmt.where(ServiceProvider.id!=id)
 if db.scalar(stmt):fail(409,"Provider already exists in this category.")
def provider_response(x):
 c=x.category
 return ProviderSummary(id=x.id,business_name=x.business_name,category_id=x.category_id,category_name=c.name if c else None,category_color=c.color if c else None,contact_person=x.contact_person,phone=x.phone,alternate_phone=x.alternate_phone,email=x.email,website=x.website,address=x.address,city=x.city,area=x.area,notes=x.notes,rating=x.rating,preferred=x.preferred,archived=x.archived,last_contacted=x.last_contacted,created_at=x.created_at,updated_at=x.updated_at)
def category_response(db,c):
 count=db.scalar(select(func.count()).select_from(ServiceProvider).where(ServiceProvider.category_id==c.id)) or 0
 return CategoryResponse(id=c.id,name=c.name,color=c.color,sort_order=c.sort_order,provider_count=count,created_at=c.created_at,updated_at=c.updated_at)
def save_provider(db,user,p,id=None):
 x=owned_provider(db,user,id) if id else ServiceProvider(user_id=str(user.id))
 if id:ensure_mutable(x)
 category_for(db,user,p.category_id);duplicate_provider(db,user,p,id)
 for k,v in p.model_dump().items():setattr(x,k,v)
 if not id:db.add(x)
 db.commit();db.refresh(x);return get_provider(db,user,x.id)
def get_provider(db,user,id):return ProviderDetail(**provider_response(owned_provider(db,user,id)).model_dump())
def list_providers(db,user,qv=None,category_id=None,preferred=None,archived=None,rating=None,last_contacted_from=None,last_contacted_to=None,page=1,page_size=12):
 if last_contacted_from and last_contacted_to and last_contacted_from>last_contacted_to:fail(422,"Last-contacted-from date cannot be after last-contacted-to date.")
 stmt=select(ServiceProvider).where(ServiceProvider.user_id==str(user.id)).options(selectinload(ServiceProvider.category));term=(qv or "").strip()
 if term:stmt=stmt.where(or_(ServiceProvider.business_name.ilike(f"%{term}%"),ServiceProvider.contact_person.ilike(f"%{term}%"),ServiceProvider.phone.ilike(f"%{term}%"),ServiceProvider.alternate_phone.ilike(f"%{term}%"),ServiceProvider.notes.ilike(f"%{term}%"),ServiceProvider.area.ilike(f"%{term}%"),ServiceProvider.city.ilike(f"%{term}%")))
 if category_id:category_for(db,user,category_id);stmt=stmt.where(ServiceProvider.category_id==category_id)
 if preferred is not None:stmt=stmt.where(ServiceProvider.preferred==preferred)
 if archived is not None:stmt=stmt.where(ServiceProvider.archived==archived)
 if rating:stmt=stmt.where(ServiceProvider.rating==rating)
 if last_contacted_from:stmt=stmt.where(ServiceProvider.last_contacted>=last_contacted_from)
 if last_contacted_to:stmt=stmt.where(ServiceProvider.last_contacted<=last_contacted_to)
 total=db.scalar(select(func.count()).select_from(stmt.order_by(None).subquery())) or 0;pref=case((ServiceProvider.preferred==True,0),else_=1);arch=case((ServiceProvider.archived==False,0),else_=1);xs=db.scalars(stmt.order_by(arch,pref,ServiceProvider.business_name.asc(),ServiceProvider.updated_at.desc()).offset((page-1)*page_size).limit(page_size)).unique().all();return ProviderList(items=[provider_response(x) for x in xs],total=total,page=page,page_size=page_size,pages=max(1,ceil(total/page_size)))
def delete_provider(db,user,id):db.delete(owned_provider(db,user,id));db.commit()
def archive(db,user,id):
 x=owned_provider(db,user,id);x.archived=True;db.commit();return get_provider(db,user,id)
def restore(db,user,id):
 x=owned_provider(db,user,id);x.archived=False;db.commit();return get_provider(db,user,id)
def set_preferred(db,user,id,value):
 x=owned_provider(db,user,id);ensure_mutable(x);x.preferred=value;db.commit();return get_provider(db,user,id)
def save_category(db,user,p,id=None):
 x=owned_category(db,user,id) if id else ServiceCategory(user_id=str(user.id))
 duplicate=db.scalar(select(ServiceCategory).where(ServiceCategory.user_id==str(user.id),func.lower(ServiceCategory.name)==p.name.lower(),ServiceCategory.id!=(id or "")))
 if duplicate:fail(409,"Category name already exists.")
 for k,v in p.model_dump().items():setattr(x,k,v)
 if not id:db.add(x)
 db.commit();db.refresh(x);return category_response(db,x)
def list_categories(db,user,qv=None,page=1,page_size=50):
 stmt=select(ServiceCategory).where(ServiceCategory.user_id==str(user.id));term=(qv or "").strip()
 if term:stmt=stmt.where(ServiceCategory.name.ilike(f"%{term}%"))
 total=db.scalar(select(func.count()).select_from(stmt.order_by(None).subquery())) or 0;xs=db.scalars(stmt.order_by(ServiceCategory.sort_order,ServiceCategory.name).offset((page-1)*page_size).limit(page_size)).all();return CategoryList(items=[category_response(db,x) for x in xs],total=total,page=page,page_size=page_size,pages=max(1,ceil(total/page_size)))
def delete_category(db,user,id):
 c=owned_category(db,user,id);count=db.scalar(select(func.count()).select_from(ServiceProvider).where(ServiceProvider.category_id==id)) or 0
 if count:fail(409,"Move or delete providers before deleting this category.")
 db.delete(c);db.commit()
def dashboard(db,user):
 providers=db.scalars(select(ServiceProvider).where(ServiceProvider.user_id==str(user.id)).options(selectinload(ServiceProvider.category)).order_by(ServiceProvider.updated_at.desc())).unique().all();cats=db.scalar(select(func.count()).select_from(ServiceCategory).where(ServiceCategory.user_id==str(user.id))) or 0;cutoff=date.today()-timedelta(days=30)
 return Dashboard(providers=sum(not x.archived for x in providers),preferred=sum(x.preferred and not x.archived for x in providers),archived=sum(x.archived for x in providers),recently_contacted=sum(x.last_contacted is not None and x.last_contacted>=cutoff for x in providers),categories=cats,recent=[provider_response(x) for x in providers[:5]])
