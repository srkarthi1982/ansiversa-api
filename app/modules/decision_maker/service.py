from datetime import date,datetime,time,timedelta
from decimal import Decimal,ROUND_HALF_UP
from math import ceil
from fastapi import HTTPException
from sqlalchemy import case,func,or_,select
from sqlalchemy.orm import Session,selectinload
from .models import Criterion,Decision,Option,Rating
from .schemas import *
Q=Decimal("0.01")
def q(v):return Decimal(v).quantize(Q,rounding=ROUND_HALF_UP)
def fail(code,msg):raise HTTPException(code,msg)
def owned(db,user,id):
 x=db.scalar(select(Decision).where(Decision.id==id,Decision.user_id==str(user.id)).options(selectinload(Decision.options),selectinload(Decision.criteria),selectinload(Decision.ratings)))
 if not x:fail(404,"Decision not found.")
 return x
def mutable(x):
 if x.status=="archived":fail(409,"Archived decisions are read-only until restored.")
 if x.status=="decided":fail(409,"Move the decision to revisiting before changing its evaluation.")
def active(x):return [o for o in x.options if o.is_active],[c for c in x.criteria if c.is_active]
def result(x):
 opts,criteria=active(x);ratings={(r.option_id,r.criterion_id):r for r in x.ratings};weight_total=sum((c.weight for c in criteria),Decimal(0));normalized={c.id:q(c.weight/weight_total*100) if weight_total else Decimal(0) for c in criteria};rows=[]
 for o in sorted(x.options,key=lambda z:(z.sort_order,z.name.lower(),z.id)):
  required=len(criteria) if o.is_active else 0;found=[ratings.get((o.id,c.id)) for c in criteria] if o.is_active else [];complete=bool(required) and all(found);contrib=[];score=Decimal(0)
  for c,r in zip(criteria,found):
   if not r:continue
   normalized_rating=Decimal(r.rating)/Decimal(x.rating_scale) if c.direction=="higher_is_better" else Decimal(x.rating_scale+1-r.rating)/Decimal(x.rating_scale);part=(c.weight/weight_total)*normalized_rating*100 if weight_total else Decimal(0);score+=part;contrib.append(Contribution(criterion_id=c.id,rating=r.rating,contribution=q(part)))
  rows.append(dict(model=o,completion=q(Decimal(sum(r is not None for r in found))*100/required) if required else Decimal(0),score=q(score) if complete else None,contributions=contrib))
 complete_rows=sorted([r for r in rows if r["score"] is not None and r["model"].is_active],key=lambda r:(-r["score"],r["model"].sort_order,r["model"].name.lower(),r["model"].id));rank=0;previous=None
 for i,r in enumerate(complete_rows,1):
  if r["score"]!=previous:rank=i;previous=r["score"]
  r["rank"]=rank;r["tied"]=sum(z["score"]==r["score"] for z in complete_rows)>1
 option_rows=[]
 for r in rows:
  o=r["model"];option_rows.append(OptionResponse(id=o.id,name=o.name,description=o.description,pros=o.pros,cons=o.cons,risks=o.risks,assumptions=o.assumptions,notes=o.notes,is_active=o.is_active,sort_order=o.sort_order,completion_percent=r["completion"],score=r["score"],rank=r.get("rank"),is_tied=r.get("tied",False),contributions=r["contributions"]))
 criterion_rows=[CriterionResponse(id=c.id,name=c.name,description=c.description,weight=c.weight,direction=c.direction,is_active=c.is_active,sort_order=c.sort_order,normalized_weight=normalized[c.id]) for c in sorted(x.criteria,key=lambda z:(z.sort_order,z.name.lower(),z.id))]
 evaluation=bool(len(opts)>=2 and criteria and all(r["score"] is not None for r in rows if r["model"].is_active));return option_rows,criterion_rows,[RatingResponse(id=r.id,option_id=r.option_id,criterion_id=r.criterion_id,rating=r.rating,notes=r.notes) for r in x.ratings],evaluation
def summary(x):
 _,_,_,done=result(x);return DecisionSummary(id=x.id,title=x.title,question=x.question,description=x.description,decision_type=x.decision_type,rating_scale=x.rating_scale,status=x.status,target_date=x.target_date,selected_option_id=x.selected_option_id,outcome=x.outcome,reflection=x.reflection,notes=x.notes,option_count=len(x.options),criterion_count=len(x.criteria),evaluation_complete=done,created_at=x.created_at,updated_at=x.updated_at,decided_at=x.decided_at)
def detail(x):
 opts,criteria,ratings,done=result(x);base=summary(x).model_dump();return DecisionDetail(**base,description=x.description,selected_option_id=x.selected_option_id,outcome=x.outcome,reflection=x.reflection,notes=x.notes,options=opts,criteria=criteria,ratings=ratings,warning="Scores support structured thinking; the user remains responsible for the final choice.")
def validate_state(x,p):
 opts,criteria=active(x);ratings={(r.option_id,r.criterion_id) for r in x.ratings};complete=bool(len(opts)>=2 and criteria and all((o.id,c.id) in ratings for o in opts for c in criteria));selected=next((o for o in x.options if o.id==p.selected_option_id and o.is_active),None) if p.selected_option_id else None
 if p.selected_option_id and not selected:fail(422,"Selected option must be an active option in this decision.")
 if p.status=="evaluating" and (len(opts)<2 or not criteria):fail(409,"Evaluating requires two active options and one active criterion.")
 if p.status=="decided" and (not selected or not complete):fail(409,"Decided requires a selected option and a complete rating matrix.")
 if p.rating_scale!=x.rating_scale and x.ratings:fail(409,"Rating scale cannot change after ratings exist.")
def restore_only(x,p):
 if x.status!="archived":return
 changed=[k for k,v in p.model_dump().items() if k!="status" and getattr(x,k)!=v]
 if p.status=="archived" or changed:fail(409,"Archived decisions are restore-only until restored.")
def save_decision(db,user,p,id=None):
 x=owned(db,user,id) if id else Decision(user_id=str(user.id),rating_scale=p.rating_scale)
 if id:restore_only(x,p);validate_state(x,p)
 elif p.status not in {"draft","cancelled"} or p.selected_option_id:fail(409,"New decisions must begin as draft or cancelled without a selected option.")
 for k,v in p.model_dump().items():setattr(x,k,v)
 x.decided_at=datetime.now() if x.status=="decided" else None
 if not id:db.add(x)
 db.commit();return get(db,user,x.id)
def get(db,user,id):return detail(owned(db,user,id))
def list_decisions(db,user,qv=None,status=None,decision_type=None,due_soon=None,overdue=None,created_from=None,created_to=None,updated_from=None,updated_to=None,page=1,page_size=12):
 if created_from and created_to and created_from>created_to:fail(422,"Created-from date cannot be after created-to date.")
 if updated_from and updated_to and updated_from>updated_to:fail(422,"Updated-from date cannot be after updated-to date.")
 stmt=select(Decision).where(Decision.user_id==str(user.id)).options(selectinload(Decision.options),selectinload(Decision.criteria),selectinload(Decision.ratings));term=(qv or "").strip()
 if term:stmt=stmt.where(or_(Decision.title.ilike(f"%{term}%"),Decision.question.ilike(f"%{term}%"),Decision.description.ilike(f"%{term}%"),Decision.notes.ilike(f"%{term}%")))
 if status:stmt=stmt.where(Decision.status==status)
 if decision_type:stmt=stmt.where(Decision.decision_type==decision_type)
 today=date.today();open_states=["draft","evaluating","revisiting"]
 if due_soon:stmt=stmt.where(Decision.status.in_(open_states),Decision.target_date.between(today,today+timedelta(days=7)))
 if overdue:stmt=stmt.where(Decision.status.in_(open_states),Decision.target_date<today)
 for col,start,end in [(Decision.created_at,created_from,created_to),(Decision.updated_at,updated_from,updated_to)]:
  if start:stmt=stmt.where(col>=datetime.combine(start,time.min))
  if end:stmt=stmt.where(col<=datetime.combine(end,time.max))
 total=db.scalar(select(func.count()).select_from(stmt.order_by(None).subquery())) or 0;priority=case((Decision.status.in_(["evaluating","revisiting"]),0),(Decision.status=="draft",1),(Decision.status=="decided",2),(Decision.status=="cancelled",3),else_=4);xs=db.scalars(stmt.order_by(priority,Decision.target_date.asc().nulls_last(),Decision.updated_at.desc()).offset((page-1)*page_size).limit(page_size)).unique().all();return DecisionList(items=[summary(x) for x in xs],total=total,page=page,page_size=page_size,pages=max(1,ceil(total/page_size)))
def save_option(db,user,did,p,id=None):
 x=owned(db,user,did);mutable(x);duplicate=next((o for o in x.options if o.name.lower()==p.name.lower() and o.id!=id),None)
 if duplicate:fail(409,"Option name already exists in this decision.")
 o=next((o for o in x.options if o.id==id),None) if id else Option(decision_id=x.id,sort_order=max([z.sort_order for z in x.options],default=0)+1)
 if id and not o:fail(404,"Option not found.")
 if id and x.selected_option_id==id and not p.is_active:fail(409,"The selected option cannot be made inactive. Clear or change the selection first.")
 for k,v in p.model_dump().items():setattr(o,k,v)
 if not id:db.add(o)
 db.commit();return get(db,user,did)
def delete_option(db,user,did,id):
 x=owned(db,user,did);mutable(x);o=next((o for o in x.options if o.id==id),None)
 if not o:fail(404,"Option not found.")
 if x.selected_option_id==id:fail(409,"Clear or change the selected option before deleting it.")
 db.query(Rating).filter(Rating.decision_id==did,Rating.option_id==id).delete();db.delete(o);db.commit()
def save_criterion(db,user,did,p,id=None):
 x=owned(db,user,did);mutable(x);duplicate=next((c for c in x.criteria if c.name.lower()==p.name.lower() and c.id!=id),None)
 if duplicate:fail(409,"Criterion name already exists in this decision.")
 c=next((c for c in x.criteria if c.id==id),None) if id else Criterion(decision_id=x.id,sort_order=max([z.sort_order for z in x.criteria],default=0)+1)
 if id and not c:fail(404,"Criterion not found.")
 for k,v in p.model_dump().items():setattr(c,k,v)
 if not id:db.add(c)
 db.commit();return get(db,user,did)
def delete_criterion(db,user,did,id):
 x=owned(db,user,did);mutable(x);c=next((c for c in x.criteria if c.id==id),None)
 if not c:fail(404,"Criterion not found.")
 db.query(Rating).filter(Rating.decision_id==did,Rating.criterion_id==id).delete();db.delete(c);db.commit()
def upsert_ratings(db,user,did,p):
 x=owned(db,user,did);mutable(x);opts={o.id:o for o in x.options if o.is_active};criteria={c.id:c for c in x.criteria if c.is_active}
 pairs=[(item.option_id,item.criterion_id) for item in p.ratings]
 if len(pairs)!=len(set(pairs)):fail(422,"A rating matrix request cannot contain duplicate option and criterion pairs.")
 for item in p.ratings:
  if item.option_id not in opts or item.criterion_id not in criteria:fail(422,"Ratings require active options and criteria in this decision.")
  if not 1<=item.rating<=x.rating_scale:fail(422,f"Rating must be between 1 and {x.rating_scale}.")
  r=next((r for r in x.ratings if r.option_id==item.option_id and r.criterion_id==item.criterion_id),None)
  if not r:r=Rating(decision_id=x.id,option_id=item.option_id,criterion_id=item.criterion_id);db.add(r)
  r.rating=item.rating;r.notes=item.notes
 db.commit();return get(db,user,did)
def delete_rating(db,user,did,id):
 x=owned(db,user,did);mutable(x);r=next((r for r in x.ratings if r.id==id),None)
 if not r:fail(404,"Rating not found.")
 db.delete(r);db.commit()
def delete_decision(db,user,id):
 x=owned(db,user,id)
 if x.status=="archived":fail(409,"Restore the decision before deleting it.")
 db.delete(x);db.commit()
def dashboard(db,user):
 xs=db.scalars(select(Decision).where(Decision.user_id==str(user.id)).options(selectinload(Decision.options),selectinload(Decision.criteria),selectinload(Decision.ratings)).order_by(Decision.updated_at.desc())).unique().all();today=date.today();counts={s:sum(x.status==s for x in xs) for s in ["draft","evaluating","decided","revisiting","archived"]};open_states={"draft","evaluating","revisiting"};return Dashboard(total=len(xs),**counts,due_soon=sum(x.status in open_states and x.target_date is not None and today<=x.target_date<=today+timedelta(days=7) for x in xs),overdue=sum(x.status in open_states and x.target_date is not None and x.target_date<today for x in xs),recent=[summary(x) for x in xs[:5]])
