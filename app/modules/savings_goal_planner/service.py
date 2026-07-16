from datetime import date,timedelta
from decimal import Decimal,ROUND_HALF_UP
from math import ceil
from fastapi import HTTPException
from sqlalchemy import case,func,or_,select
from sqlalchemy.orm import selectinload
from app.modules.savings_goal_planner.models import Goal,Milestone,Transaction
from app.modules.savings_goal_planner.schemas import *
C=Decimal("0.01");Z=Decimal("0.00")
def money(v):return Decimal(v).quantize(C,rounding=ROUND_HALF_UP)
def oid(u):return str(u.id)
def missing(k):raise HTTPException(404,f"{k} not found.")
def query():return select(Goal).options(selectinload(Goal.transactions),selectinload(Goal.milestones))
def get_model(db,o,id):return db.scalar(query().where(Goal.id==id,Goal.owner_id==o))
def signed(t):return Decimal(1)if t in{"contribution","adjustment_increase"}else Decimal(-1)
def balance(g,skip=None,replacement=None):return money(g.starting_amount+sum((signed(x.transaction_type)*x.amount for x in g.transactions if x.id!=skip),Z)+(signed(replacement.transaction_type)*replacement.amount if replacement else Z))
def derive(g,projected=None):
 b=money(projected if projected is not None else balance(g));g.current_amount=b
 if b<0:raise HTTPException(422,"A transaction cannot reduce the saved amount below zero.")
 if b>g.target_amount:raise HTTPException(422,"Overfunding is not supported; the saved amount cannot exceed the target.")
 if g.status not in{"cancelled","archived","paused"}:g.status="completed"if b==g.target_amount else"active"
 today=date.today()
 for m in g.milestones:
  if m.status!="cancelled":m.status="reached"if b>=m.target_amount else("missed"if m.target_date and m.target_date<today else"pending")
def metrics(g):
 remaining=max(Z,money(g.target_amount-g.current_amount));progress=money(g.current_amount/g.target_amount*100);days=(g.target_date-date.today()).days if g.target_date else None;months=Decimal(max(days or 0,0))/Decimal("30.44")if days is not None else None
 weekly=money(remaining/(Decimal(days)/7))if days and days>0 and remaining else Z;monthly=money(remaining/months)if months and months>0 and remaining else Z
 return remaining,progress,days,money(months)if months is not None else None,weekly,monthly,bool(days is not None and days<0 and g.status=="active"),bool(days is not None and 0<=days<=30 and g.status=="active")
def tr(x):return TransactionResponse(transaction_date=x.transaction_date,transaction_type=x.transaction_type,amount=x.amount,description=x.description,notes=x.notes,id=x.id,created_at=x.created_at,updated_at=x.updated_at)
def mr(x):return MilestoneResponse(name=x.name,target_amount=x.target_amount,target_date=x.target_date,status=x.status,notes=x.notes,id=x.id,sort_order=x.sort_order,created_at=x.created_at,updated_at=x.updated_at)
def summary(g):
 r,p,d,mo,w,m,over,due=metrics(g);return GoalSummary(name=g.name,description=g.description,category=g.category,currency_code=g.currency_code,target_amount=g.target_amount,starting_amount=g.starting_amount,target_date=g.target_date,priority=g.priority,status=g.status,notes=g.notes,id=g.id,current_amount=g.current_amount,remaining_amount=r,progress_percent=p,days_remaining=d,months_remaining=mo,required_weekly=w,required_monthly=m,is_overdue=over,is_due_soon=due,transaction_count=len(g.transactions),milestone_count=len(g.milestones),created_at=g.created_at,updated_at=g.updated_at)
def detail(g):
 contributions=[x for x in g.transactions if x.transaction_type=="contribution"];avg=money(sum((x.amount for x in contributions),Z)/len(contributions))if contributions else Z;last=max((x.transaction_date for x in contributions),default=None);return GoalDetail(**summary(g).model_dump(),transactions=[tr(x)for x in sorted(g.transactions,key=lambda x:(x.transaction_date,x.created_at,x.id),reverse=True)],milestones=[mr(x)for x in sorted(g.milestones,key=lambda x:(x.sort_order,x.created_at,x.id))],average_contribution=avg,last_contribution_date=last)
def save_goal(db,u,p,id=None):
 g=get_model(db,oid(u),id)if id else Goal(owner_id=oid(u),current_amount=Z)
 if id and not g:missing("Goal")
 try:
  for k,v in p.model_dump().items():setattr(g,k,v)
  if id and balance(g)>g.target_amount:raise HTTPException(422,"The new target cannot be below the current saved amount.")
  if p.status=="completed" and balance(g)<g.target_amount:raise HTTPException(422,"A goal cannot be completed before it is fully funded.")
  if not id:db.add(g)
  db.flush();derive(g);db.commit();return detail(get_model(db,oid(u),g.id))
 except Exception:db.rollback();raise
def get_goal(db,u,id):
 g=get_model(db,oid(u),id)
 if not g:missing("Goal")
 return detail(g)
def delete_goal(db,u,id):
 g=get_model(db,oid(u),id)
 if not g:missing("Goal")
 db.delete(g);db.commit()
def list_goals(db,u,q,status,category,priority,currency,period,date_from,date_to,page,size):
 if date_from and date_to and date_from>date_to:raise HTTPException(422,"From date must be on or before to date.")
 f=[Goal.owner_id==oid(u)];today=date.today()
 if q:
  t=f"%{q.strip()}%";f.append(or_(Goal.name.ilike(t),Goal.description.ilike(t),Goal.notes.ilike(t),Goal.category.ilike(t)))
 if status:f.append(Goal.status==status)
 if category:f.append(Goal.category==category)
 if priority:f.append(Goal.priority==priority)
 if currency:f.append(Goal.currency_code==currency.strip().upper())
 if period=="due_soon":f.extend([Goal.status=="active",Goal.target_date>=today,Goal.target_date<=today+timedelta(days=30)])
 elif period=="overdue":f.extend([Goal.status=="active",Goal.target_date<today])
 elif period=="completed":f.append(Goal.status=="completed")
 if date_from:f.append(Goal.target_date>=date_from)
 if date_to:f.append(Goal.target_date<=date_to)
 total=db.scalar(select(func.count(Goal.id)).where(*f))or 0;rank=case((Goal.status=="active",0),(Goal.status=="paused",1),(Goal.status=="completed",2),else_=3);rows=list(db.scalars(query().where(*f).order_by(rank,Goal.target_date.is_(None),Goal.target_date,Goal.created_at.desc()).offset((page-1)*size).limit(size)));return GoalList(items=[summary(x)for x in rows],total=total,page=page,page_size=size,pages=ceil(total/size)if total else 0)
def save_tx(db,u,goal_id,p,id=None):
 g=get_model(db,oid(u),goal_id)
 if not g:missing("Goal")
 if g.status in{"paused","cancelled","archived"}:raise HTTPException(409,f"Transactions are blocked while a goal is {g.status}.")
 x=next((x for x in g.transactions if x.id==id),None)if id else Transaction(goal_id=g.id)
 if id and not x:missing("Transaction")
 try:
  for k,v in p.model_dump().items():setattr(x,k,v)
  projected=balance(g,skip=id,replacement=x)
  if projected<0:raise HTTPException(422,"Withdrawal or decrease exceeds the saved amount.")
  if projected>g.target_amount:raise HTTPException(422,"This transaction would overfund the goal.")
  if not id:db.add(x)
  db.flush();derive(g,projected);db.commit();db.expire_all();return detail(get_model(db,oid(u),g.id))
 except Exception:db.rollback();raise
def delete_tx(db,u,goal_id,id):
 g=get_model(db,oid(u),goal_id)
 if not g:missing("Goal")
 if g.status=="archived":raise HTTPException(409,"Archived goals are read-only.")
 x=next((x for x in g.transactions if x.id==id),None)
 if not x:missing("Transaction")
 projected=balance(g,skip=id);db.delete(x);db.flush();derive(g,projected);db.commit()
def save_milestone(db,u,goal_id,p,id=None):
 g=get_model(db,oid(u),goal_id)
 if not g:missing("Goal")
 if g.status=="archived":raise HTTPException(409,"Archived goals are read-only.")
 x=next((x for x in g.milestones if x.id==id),None)if id else Milestone(goal_id=g.id,sort_order=len(g.milestones))
 if id and not x:missing("Milestone")
 if p.target_amount>g.target_amount:raise HTTPException(422,"Milestone target cannot exceed the goal target.")
 for k,v in p.model_dump().items():setattr(x,k,v)
 if x.status!="cancelled":x.status="reached"if g.current_amount>=x.target_amount else("missed"if x.target_date and x.target_date<date.today()else"pending")
 if not id:db.add(x)
 db.flush();derive(g);db.commit();db.expire_all();return detail(get_model(db,oid(u),g.id))
def delete_milestone(db,u,goal_id,id):
 g=get_model(db,oid(u),goal_id)
 if not g:missing("Goal")
 if g.status=="archived":raise HTTPException(409,"Archived goals are read-only.")
 x=next((x for x in g.milestones if x.id==id),None)
 if not x:missing("Milestone")
 db.delete(x);db.commit()
def dashboard(db,u):
 rows=list(db.scalars(query().where(Goal.owner_id==oid(u))));today=date.today();included=[g for g in rows if g.status not in{"cancelled","archived"}];currencies=[]
 for code in sorted({g.currency_code for g in included}):
  group=[g for g in included if g.currency_code==code];currencies.append(CurrencyTotal(currency_code=code,target_amount=money(sum((g.target_amount for g in group),Z)),saved_amount=money(sum((g.current_amount for g in group),Z)),remaining_amount=money(sum((max(Z,g.target_amount-g.current_amount)for g in group),Z))))
 recent=sum(x.transaction_type=="contribution"and x.transaction_date>=today-timedelta(days=30)for g in rows for x in g.transactions);return Dashboard(active_goals=sum(g.status in{"active","paused"}for g in rows),completed_goals=sum(g.status=="completed"for g in rows),due_soon_goals=sum(metrics(g)[7]for g in rows),overdue_goals=sum(metrics(g)[6]for g in rows),recent_contributions=recent,currency_totals=currencies)
