from datetime import date,datetime,timedelta
from decimal import Decimal,ROUND_HALF_UP
from math import ceil
from fastapi import HTTPException
from sqlalchemy import case,func,or_,select
from sqlalchemy.orm import selectinload
from app.modules.salary_breakdown_calculator.constants import FACTORS
from app.modules.salary_breakdown_calculator.models import Deduction,Earning,Scenario
from app.modules.salary_breakdown_calculator.schemas import *
C=Decimal("0.01");Z=Decimal("0.00")
def money(v):return Decimal(v).quantize(C,rounding=ROUND_HALF_UP)
def annual(v,f):return money(Decimal(v)*FACTORS[f])
def oid(u):return str(u.id)
def missing(k):raise HTTPException(404,f"{k} not found.")
def query():return select(Scenario).options(selectinload(Scenario.earnings),selectinload(Scenario.deductions))
def model(db,o,id):return db.scalar(query().where(Scenario.id==id,Scenario.owner_id==o))
def calc(s):
 base=annual(s.base_salary_amount,s.base_salary_period);rec_earn=sum((annual(x.amount,x.frequency)for x in s.earnings if x.is_recurring),Z);one_earn=sum((money(x.amount)for x in s.earnings if not x.is_recurring),Z);gross=money(base+rec_earn);rec_ded=Z;one_ded=Z
 values={}
 for x in s.deductions:
  if x.calculation_method=="fixed_amount":v=annual(x.amount,x.frequency)if x.is_recurring else money(x.amount)
  else:v=money((base if x.calculation_method=="percentage_of_base" else gross)*x.percentage/100)
  values[x.id]=v
  if x.is_recurring:rec_ded+=v
  else:one_ded+=v
 rec_ded=money(rec_ded);one_ded=money(one_ded);net=money(gross-rec_ded)
 if net<0:raise HTTPException(422,"Recurring deductions cannot exceed recurring gross pay.")
 return{"base":base,"monthly":money(base/12),"weekly":money(base/52),"period":money(base/FACTORS[s.pay_frequency]),"rec_earn":money(rec_earn),"one_earn":money(one_earn),"gross":gross,"rec_ded":rec_ded,"one_ded":one_ded,"net":net,"ratio":money(net/gross*100)if gross else Z,"values":values}
def er(x):
 a=annual(x.amount,x.frequency)if x.is_recurring else money(x.amount);return EarningResponse(name=x.name,earning_type=x.earning_type,amount=x.amount,frequency=x.frequency,is_taxable=x.is_taxable,is_recurring=x.is_recurring,effective_date=x.effective_date,notes=x.notes,id=x.id,sort_order=x.sort_order,annual_amount=a,monthly_amount=money(a/12)if x.is_recurring else Z,created_at=x.created_at,updated_at=x.updated_at)
def dr(x,t):
 a=t["values"][x.id];return DeductionResponse(name=x.name,deduction_type=x.deduction_type,calculation_method=x.calculation_method,amount=x.amount,percentage=x.percentage,frequency=x.frequency,is_recurring=x.is_recurring,effective_date=x.effective_date,notes=x.notes,id=x.id,sort_order=x.sort_order,annual_amount=a,monthly_amount=money(a/12)if x.is_recurring else Z,calculated_annual=a,calculated_monthly=money(a/12)if x.is_recurring else Z,created_at=x.created_at,updated_at=x.updated_at)
def summary(s):
 t=calc(s);return ScenarioSummary(name=s.name,description=s.description,currency_code=s.currency_code,pay_frequency=s.pay_frequency,base_salary_amount=s.base_salary_amount,base_salary_period=s.base_salary_period,working_days_per_week=s.working_days_per_week,working_hours_per_week=s.working_hours_per_week,status=s.status,notes=s.notes,id=s.id,annual_base=t["base"],monthly_base=t["monthly"],weekly_base=t["weekly"],period_base=t["period"],recurring_earnings=t["rec_earn"],one_time_earnings=t["one_earn"],recurring_gross=t["gross"],recurring_deductions=t["rec_ded"],one_time_deductions=t["one_ded"],recurring_net=t["net"],net_to_gross_percent=t["ratio"],earning_count=len(s.earnings),deduction_count=len(s.deductions),created_at=s.created_at,updated_at=s.updated_at)
def detail(s):
 t=calc(s);return ScenarioDetail(**summary(s).model_dump(),earnings=[er(x)for x in sorted(s.earnings,key=lambda x:(x.sort_order,x.id))],deductions=[dr(x,t)for x in sorted(s.deductions,key=lambda x:(x.sort_order,x.id))])
def save_scenario(db,u,p,id=None):
 s=model(db,oid(u),id)if id else Scenario(owner_id=oid(u))
 if id and not s:missing("Scenario")
 try:
  for k,v in p.model_dump().items():setattr(s,k,v)
  if not id:db.add(s)
  db.flush();calc(s);db.commit();return detail(model(db,oid(u),s.id))
 except Exception:db.rollback();raise
def get(db,u,id):
 s=model(db,oid(u),id)
 if not s:missing("Scenario")
 return detail(s)
def delete(db,u,id):
 s=model(db,oid(u),id)
 if not s:missing("Scenario")
 db.delete(s);db.commit()
def list_scenarios(db,u,q,status,frequency,currency,created_from,created_to,updated_from,updated_to,page,size):
 if created_from and created_to and created_from>created_to or updated_from and updated_to and updated_from>updated_to:raise HTTPException(422,"From date must be on or before to date.")
 f=[Scenario.owner_id==oid(u)]
 if q:
  t=f"%{q.strip()}%";f.append(or_(Scenario.name.ilike(t),Scenario.description.ilike(t),Scenario.notes.ilike(t),Scenario.earnings.any(Earning.name.ilike(t)),Scenario.deductions.any(Deduction.name.ilike(t))))
 if status:f.append(Scenario.status==status)
 if frequency:f.append(Scenario.pay_frequency==frequency)
 if currency:f.append(Scenario.currency_code==currency.strip().upper())
 if created_from:f.append(func.date(Scenario.created_at)>=created_from)
 if created_to:f.append(func.date(Scenario.created_at)<=created_to)
 if updated_from:f.append(func.date(Scenario.updated_at)>=updated_from)
 if updated_to:f.append(func.date(Scenario.updated_at)<=updated_to)
 total=db.scalar(select(func.count(Scenario.id)).where(*f))or 0;rank=case((Scenario.status=="active",0),(Scenario.status=="draft",1),else_=2);rows=list(db.scalars(query().where(*f).order_by(rank,Scenario.updated_at.desc(),Scenario.created_at.desc()).offset((page-1)*size).limit(size)));return ScenarioList(items=[summary(x)for x in rows],total=total,page=page,page_size=size,pages=ceil(total/size)if total else 0)
def save_earning(db,u,sid,p,id=None):
 s=model(db,oid(u),sid)
 if not s:missing("Scenario")
 if s.status=="archived":raise HTTPException(409,"Archived scenarios are read-only.")
 x=next((x for x in s.earnings if x.id==id),None)if id else Earning(scenario_id=s.id,sort_order=len(s.earnings))
 if id and not x:missing("Earning")
 try:
  for k,v in p.model_dump().items():setattr(x,k,v)
  if not id:db.add(x)
  db.flush();db.expire(s,["earnings"]);calc(s);db.commit();db.expire_all();return detail(model(db,oid(u),sid))
 except Exception:db.rollback();raise
def delete_earning(db,u,sid,id):
 s=model(db,oid(u),sid)
 if not s:missing("Scenario")
 if s.status=="archived":raise HTTPException(409,"Archived scenarios are read-only.")
 x=next((x for x in s.earnings if x.id==id),None)
 if not x:missing("Earning")
 db.delete(x);db.flush();db.expire(s,["earnings"]);calc(s);db.commit()
def save_deduction(db,u,sid,p,id=None):
 s=model(db,oid(u),sid)
 if not s:missing("Scenario")
 if s.status=="archived":raise HTTPException(409,"Archived scenarios are read-only.")
 x=next((x for x in s.deductions if x.id==id),None)if id else Deduction(scenario_id=s.id,sort_order=len(s.deductions))
 if id and not x:missing("Deduction")
 try:
  for k,v in p.model_dump().items():setattr(x,k,v)
  if not id:db.add(x)
  db.flush();db.expire(s,["deductions"]);calc(s);db.commit();db.expire_all();return detail(model(db,oid(u),sid))
 except Exception:db.rollback();raise
def delete_deduction(db,u,sid,id):
 s=model(db,oid(u),sid)
 if not s:missing("Scenario")
 if s.status=="archived":raise HTTPException(409,"Archived scenarios are read-only.")
 x=next((x for x in s.deductions if x.id==id),None)
 if not x:missing("Deduction")
 db.delete(x);db.flush();db.expire(s,["deductions"]);calc(s);db.commit()
def compare(db,u,left,right):
 a=model(db,oid(u),left);b=model(db,oid(u),right)
 if not a or not b:missing("Scenario")
 sa,sb=summary(a),summary(b);ok=a.currency_code==b.currency_code
 return Comparison(left=sa,right=sb,currency_compatible=ok,warning=None if ok else"Currencies differ; no currency conversion or monetary differences are applied.",base_difference=money(sb.annual_base-sa.annual_base)if ok else None,gross_difference=money(sb.recurring_gross-sa.recurring_gross)if ok else None,deduction_difference=money(sb.recurring_deductions-sa.recurring_deductions)if ok else None,net_difference=money(sb.recurring_net-sa.recurring_net)if ok else None)
def dashboard(db,u):
 rows=list(db.scalars(query().where(Scenario.owner_id==oid(u))));active=[s for s in rows if s.status!="archived"];curr=[]
 for code in sorted({s.currency_code for s in active}):
  group=[summary(s)for s in active if s.currency_code==code];curr.append(CurrencyTotal(currency_code=code,recurring_gross=money(sum((s.recurring_gross for s in group),Z)),recurring_net=money(sum((s.recurring_net for s in group),Z))))
 return Dashboard(total_scenarios=len(rows),active_scenarios=sum(s.status=="active"for s in rows),archived_scenarios=sum(s.status=="archived"for s in rows),recent_scenarios=sum(s.created_at>=datetime.now()-timedelta(days=30)for s in rows),currency_totals=curr,frequency_counts=[FrequencyCount(frequency=f,count=sum(s.pay_frequency==f for s in rows))for f in FACTORS])
