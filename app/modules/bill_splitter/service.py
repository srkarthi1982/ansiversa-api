from datetime import date,timedelta
from decimal import Decimal,ROUND_DOWN,ROUND_HALF_UP
from math import ceil
from fastapi import HTTPException
from sqlalchemy import func,or_,select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from app.modules.bill_splitter.models import Allocation,Bill,Item,Participant
from app.modules.bill_splitter.schemas import *
CENT=Decimal("0.01");Z=Decimal("0.00")
def money(v):return Decimal(v).quantize(CENT,rounding=ROUND_HALF_UP)
def owner(u):return str(u.id)
def missing(k):raise HTTPException(404,f"{k} not found.")
def bill(db,o,id):return db.scalar(select(Bill).options(selectinload(Bill.participants),selectinload(Bill.items).selectinload(Item.allocations).selectinload(Allocation.participant)).where(Bill.id==id,Bill.owner_id==o))
def participant(b,id):return next((x for x in b.participants if x.id==id),None)
def item(b,id):return next((x for x in b.items if x.id==id),None)
def equal(total,n):
 cents=int(total/CENT);base,remainder=divmod(cents,n);return[Decimal(base+(1 if i<remainder else 0))*CENT for i in range(n)]
def recalc(b):
 b.subtotal_amount=money(sum((x.line_total for x in b.items),Z))
 if b.discount_amount>b.subtotal_amount:raise HTTPException(422,"Discount cannot exceed subtotal.")
 b.total_amount=money(b.subtotal_amount-b.discount_amount+b.tax_amount+b.service_charge_amount+b.tip_amount)
 shares={p.id:Z for p in sorted(b.participants,key=lambda x:(x.sort_order,x.id))}
 for i in b.items:
  for a in i.allocations:shares[a.participant_id]=shares.get(a.participant_id,Z)+a.allocation_amount
 adjustment=b.total_amount-b.subtotal_amount
 if shares and adjustment:
  for p,v in zip(sorted(b.participants,key=lambda x:(x.sort_order,x.id)),equal(adjustment,len(shares))):shares[p.id]+=v
 for p in b.participants:
  p.share_amount=money(shares.get(p.id,Z));out=max(Z,p.share_amount-p.paid_amount);p.settlement_status="settled"if out==0 else("partially_paid"if p.paid_amount>0 else"unpaid")
 if b.status not in{"draft","cancelled"}:
  b.status="settled"if b.participants and all(p.paid_amount>=p.share_amount for p in b.participants)else("partially_settled"if any(p.paid_amount>0 for p in b.participants)else"open")
def ar(a):return AllocationResponse(id=a.id,participant_id=a.participant_id,participant_name=a.participant.name,amount=a.allocation_amount)
def ir(i):return ItemResponse(name=i.name,quantity=i.quantity,unit_price=i.unit_price,split_method=i.split_method,notes=i.notes,id=i.id,line_total=i.line_total,sort_order=i.sort_order,allocations=[ar(a)for a in i.allocations],allocated_amount=money(sum((a.allocation_amount for a in i.allocations),Z)))
def pr(p):return ParticipantResponse(name=p.name,email=p.email,paid_amount=p.paid_amount,notes=p.notes,id=p.id,share_amount=p.share_amount,outstanding_amount=max(Z,p.share_amount-p.paid_amount),settlement_status=p.settlement_status,sort_order=p.sort_order)
def bs(b):return BillSummary(title=b.title,bill_date=b.bill_date,merchant_name=b.merchant_name,currency_code=b.currency_code,discount_amount=b.discount_amount,tax_amount=b.tax_amount,service_charge_amount=b.service_charge_amount,tip_amount=b.tip_amount,status=b.status,notes=b.notes,id=b.id,subtotal_amount=b.subtotal_amount,total_amount=b.total_amount,outstanding_amount=money(sum((max(Z,p.share_amount-p.paid_amount)for p in b.participants),Z)),participant_count=len(b.participants),item_count=len(b.items),created_at=b.created_at,updated_at=b.updated_at)
def detail(b):return BillDetail(**bs(b).model_dump(),participants=[pr(p)for p in sorted(b.participants,key=lambda x:x.sort_order)],items=[ir(i)for i in sorted(b.items,key=lambda x:x.sort_order)],is_fully_allocated=all(money(sum((a.allocation_amount for a in i.allocations),Z))==i.line_total for i in b.items))
def save_bill(db,u,p,id=None):
 b=bill(db,owner(u),id)if id else Bill(owner_id=owner(u),subtotal_amount=Z,total_amount=Z)
 if id and not b:missing("Bill")
 requested_status=p.status
 try:
  for k,v in p.model_dump().items():setattr(b,k,v)
  recalc(b)
  if requested_status=="settled" and (not b.participants or any(x.paid_amount<x.share_amount for x in b.participants)):raise HTTPException(422,"A bill cannot be settled while balances remain outstanding.")
  if requested_status not in{"draft","cancelled"} and (not b.items or not b.participants or any(money(sum((a.allocation_amount for a in x.allocations),Z))!=x.line_total for x in b.items)):raise HTTPException(422,"An active bill requires participants and fully allocated items.")
  if not id:db.add(b)
  db.commit();return detail(bill(db,owner(u),b.id))
 except Exception:
  db.rollback();raise
def get_bill(db,u,id):
 b=bill(db,owner(u),id)
 if not b:missing("Bill")
 return detail(b)
def delete_bill(db,u,id):
 b=bill(db,owner(u),id)
 if not b:missing("Bill")
 db.delete(b);db.commit()
def list_bills(db,u,q,status,currency,period,date_from,date_to,page,size):
 if date_from and date_to and date_from>date_to:raise HTTPException(422,"From date must be on or before to date.")
 f=[Bill.owner_id==owner(u)]
 if q:
  term=f"%{q.strip()}%";f.append(or_(Bill.title.ilike(term),Bill.merchant_name.ilike(term),Bill.notes.ilike(term),Bill.participants.any(Participant.name.ilike(term))))
 if status:f.append(Bill.status==status)
 if currency:f.append(Bill.currency_code==currency.strip().upper())
 today=date.today()
 if period=="recent":f.append(Bill.bill_date>=today-timedelta(days=30))
 elif period=="month":f.append(Bill.bill_date>=today.replace(day=1))
 elif period=="past":f.append(Bill.bill_date<today)
 if date_from:f.append(Bill.bill_date>=date_from)
 if date_to:f.append(Bill.bill_date<=date_to)
 total=db.scalar(select(func.count(Bill.id)).where(*f))or 0;rows=list(db.scalars(select(Bill).options(selectinload(Bill.participants),selectinload(Bill.items)).where(*f).order_by(Bill.bill_date.desc(),Bill.created_at.desc()).offset((page-1)*size).limit(size)));return BillList(items=[bs(x)for x in rows],total=total,page=page,page_size=size,pages=ceil(total/size)if total else 0)
def ensure_unique_participant(db,b,p,id=None):
 name=(p.name or "").strip().lower()
 q=select(Participant).where(Participant.bill_id==b.id,func.lower(Participant.name)==name)
 if id:q=q.where(Participant.id!=id)
 if db.scalar(q):raise HTTPException(409,"Participant names must be unique within a bill.")
def save_participant(db,u,bill_id,p,id=None):
 b=bill(db,owner(u),bill_id)
 if not b:missing("Bill")
 x=participant(b,id)if id else Participant(bill_id=b.id,sort_order=len(b.participants))
 if id and not x:missing("Participant")
 ensure_unique_participant(db,b,p,id)
 for k,v in p.model_dump().items():setattr(x,k,v)
 if id and x.paid_amount>x.share_amount:raise HTTPException(422,"Paid amount cannot exceed the participant share.")
 if not id:db.add(x)
 try:
  db.flush();recalc(b)
  if x.paid_amount>x.share_amount:raise HTTPException(422,"Paid amount cannot exceed the participant share.")
  db.commit()
 except IntegrityError:db.rollback();raise HTTPException(409,"Participant names must be unique within a bill.")
 except Exception:db.rollback();raise
 return get_bill(db,u,bill_id)
def delete_participant(db,u,bill_id,id):
 b=bill(db,owner(u),bill_id)
 if not b:missing("Bill")
 x=participant(b,id)
 if not x:missing("Participant")
 if x.allocations:raise HTTPException(409,"Participants assigned to items cannot be deleted. Replace those allocations first.")
 db.delete(x);db.flush();recalc(b);db.commit()
def save_item(db,u,bill_id,p,id=None):
 b=bill(db,owner(u),bill_id)
 if not b:missing("Bill")
 x=item(b,id)if id else Item(bill_id=b.id,sort_order=len(b.items))
 if id and not x:missing("Item")
 for k,v in p.model_dump().items():setattr(x,k,v)
 x.line_total=money(x.quantity*x.unit_price)
 if id and x.allocations and money(sum((a.allocation_amount for a in x.allocations),Z))!=x.line_total:
  if x.split_method=="custom":db.rollback();raise HTTPException(409,"A custom-split item changed total. Replace its allocations with exact amounts.")
  ids=[a.participant_id for a in x.allocations];amounts=equal(x.line_total,len(ids))if x.split_method=="equal"else[x.line_total]
  for a,amount in zip(x.allocations,amounts):a.allocation_amount=amount
 if not id:db.add(x)
 db.flush();recalc(b);db.commit();return get_bill(db,u,bill_id)
def delete_item(db,u,bill_id,id):
 b=bill(db,owner(u),bill_id)
 if not b:missing("Bill")
 x=item(b,id)
 if not x:missing("Item")
 db.delete(x);db.flush();recalc(b);db.commit()
def replace_allocations(db,u,bill_id,item_id,p):
 b=bill(db,owner(u),bill_id)
 if not b:missing("Bill")
 x=item(b,item_id)
 if not x:missing("Item")
 ids=[a.participant_id for a in p.allocations]
 if len(ids)!=len(set(ids))or any(not participant(b,id)for id in ids):raise HTTPException(422,"Every allocation must reference a unique participant in this bill.")
 if p.split_method=="single_participant" and len(ids)!=1:raise HTTPException(422,"Single-participant allocation requires exactly one participant.")
 if p.split_method=="equal":amounts=equal(x.line_total,len(ids))
 elif p.split_method=="single_participant":amounts=[x.line_total]
 else:
  if any(a.amount is None for a in p.allocations):raise HTTPException(422,"Custom allocations require exact amounts.")
  amounts=[money(a.amount)for a in p.allocations]
 if money(sum(amounts,Z))!=x.line_total:raise HTTPException(422,"Allocations must equal the item total exactly.")
 x.allocations.clear();db.flush();x.split_method=p.split_method
 for a,amount in zip(p.allocations,amounts):x.allocations.append(Allocation(participant_id=a.participant_id,allocation_amount=amount))
 db.flush();recalc(b);db.commit();return get_bill(db,u,bill_id)
def dashboard(db,u):
 rows=list(db.scalars(select(Bill).options(selectinload(Bill.participants)).where(Bill.owner_id==owner(u))));active=[b for b in rows if b.status!="cancelled"]
 return Dashboard(total_bills=len(rows),open_bills=sum(b.status in{"draft","open","partially_settled"}for b in rows),settled_bills=sum(b.status=="settled"for b in rows),outstanding_amount=money(sum((max(Z,p.share_amount-p.paid_amount)for b in active for p in b.participants),Z)),recorded_value=money(sum((b.total_amount for b in active),Z)))
