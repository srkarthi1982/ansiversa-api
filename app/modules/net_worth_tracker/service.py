from datetime import date,datetime,time
from decimal import Decimal,ROUND_HALF_UP
from math import ceil
from fastapi import HTTPException
from sqlalchemy import func,or_,select
from sqlalchemy.orm import Session,selectinload
from .models import Account,BalanceEntry,Snapshot,SnapshotItem
from .schemas import *
Q=Decimal("0.01")
def q(v):return Decimal(v).quantize(Q,rounding=ROUND_HALF_UP)
def fail(code,msg):raise HTTPException(code,msg)
def owned(db,user,id):
 x=db.scalar(select(Account).where(Account.id==id,Account.user_id==str(user.id)).options(selectinload(Account.entries)))
 if not x:fail(404,"Account not found.")
 return x
def entries(x):
 xs=sorted(x.entries,key=lambda e:(e.balance_date,e.created_at,e.id),reverse=True);out=[]
 for i,e in enumerate(xs):
  older=xs[i+1].balance_amount if i+1<len(xs) else None;out.append(BalanceResponse(id=e.id,balanceDate=e.balance_date,balance_amount=e.balance_amount,change=q(e.balance_amount-older) if older is not None else None,changeReason=e.change_reason,notes=e.notes,is_latest=i==0,created_at=e.created_at,updated_at=e.updated_at))
 return out
def account(x,detail=False):
 data=dict(id=x.id,name=x.name,account_type=x.account_type,category=x.category,currency_code=x.currency_code,institutionName=x.institution_name,currentBalance=x.current_balance,valuationDate=x.valuation_date,includeInNetWorth=x.include_in_net_worth,status=x.status,notes=x.notes,entry_count=len(x.entries),created_at=x.created_at,updated_at=x.updated_at)
 return AccountDetail(**data,entries=entries(x)) if detail else AccountSummary(**data)
def recalc(db,x):
 latest=db.scalar(select(BalanceEntry).where(BalanceEntry.account_id==x.id).order_by(BalanceEntry.balance_date.desc(),BalanceEntry.created_at.desc(),BalanceEntry.id.desc()))
 x.current_balance=q(latest.balance_amount if latest else 0);x.valuation_date=latest.balance_date if latest else x.valuation_date;db.flush()
def save_account(db,user,p,id=None):
 x=owned(db,user,id) if id else Account(user_id=str(user.id))
 prior=x.current_balance if id else None
 for k,v in p.model_dump().items():setattr(x,k,v)
 x.current_balance=q(x.current_balance)
 if not id:db.add(x);db.flush();db.add(BalanceEntry(account_id=x.id,balance_date=x.valuation_date,balance_amount=x.current_balance,change_reason="Initial balance",created_at=datetime.now(),updated_at=datetime.now()))
 elif prior!=x.current_balance:db.add(BalanceEntry(account_id=x.id,balance_date=x.valuation_date,balance_amount=x.current_balance,change_reason="Account balance update",created_at=datetime.now(),updated_at=datetime.now()))
 db.commit();return get_account(db,user,x.id)
def get_account(db,user,id):return account(owned(db,user,id),True)
def list_accounts(db,user,qv=None,account_type=None,category=None,currency=None,status=None,included=None,updated_from=None,updated_to=None,page=1,page_size=12):
 stmt=select(Account).where(Account.user_id==str(user.id)).options(selectinload(Account.entries));term=(qv or "").strip()
 if term:stmt=stmt.where(or_(Account.name.ilike(f"%{term}%"),Account.institution_name.ilike(f"%{term}%"),Account.notes.ilike(f"%{term}%"),Account.category.ilike(f"%{term}%")))
 for col,val in [(Account.account_type,account_type),(Account.category,category),(Account.currency_code,currency.upper() if currency else None),(Account.status,status),(Account.include_in_net_worth,included)]:
  if val is not None:stmt=stmt.where(col==val)
 if updated_from:stmt=stmt.where(Account.updated_at>=datetime.combine(updated_from,time.min))
 if updated_to:stmt=stmt.where(Account.updated_at<=datetime.combine(updated_to,time.max))
 total=db.scalar(select(func.count()).select_from(stmt.order_by(None).subquery())) or 0;xs=db.scalars(stmt.order_by((Account.status=="archived"),Account.account_type,Account.updated_at.desc()).offset((page-1)*page_size).limit(page_size)).unique().all();return AccountList(items=[account(x) for x in xs],total=total,page=page,page_size=page_size,pages=max(1,ceil(total/page_size)))
def delete_account(db,user,id):
 x=owned(db,user,id);refs=db.scalar(select(func.count()).select_from(SnapshotItem).where(SnapshotItem.account_id==id)) or 0
 protected=refs or len(x.entries)>1 or (x.entries and (x.entries[0].balance_amount!=0 or x.entries[0].change_reason!="Initial balance"))
 if protected:fail(409,"Account has financial history; archive it instead.")
 db.delete(x);db.commit()
def save_entry(db,user,account_id,p,id=None):
 x=owned(db,user,account_id)
 if x.status=="archived":fail(409,"Archived accounts are read-only until restored.")
 e=next((z for z in x.entries if z.id==id),None) if id else BalanceEntry(account_id=x.id,created_at=datetime.now(),updated_at=datetime.now())
 if id and not e:fail(404,"Balance entry not found.")
 for k,v in p.model_dump().items():setattr(e,k,v)
 e.balance_amount=q(e.balance_amount)
 if not id:db.add(e)
 db.flush();recalc(db,x);db.commit();return get_account(db,user,x.id)
def delete_entry(db,user,account_id,id):
 x=owned(db,user,account_id)
 if x.status=="archived":fail(409,"Archived accounts are read-only until restored.")
 e=next((z for z in x.entries if z.id==id),None)
 if not e:fail(404,"Balance entry not found.")
 db.delete(e);db.flush();recalc(db,x);db.commit()
def totals(items):
 d={}
 for x in items:
  if not getattr(x,"included",getattr(x,"include_in_net_worth",False)):continue
  row=d.setdefault(x.currency_code,[Decimal(0),Decimal(0)])
  row[0 if x.account_type=="asset" else 1]+=getattr(x,"balance_amount",getattr(x,"current_balance",Decimal(0)))
 return [CurrencyTotal(currency_code=c,assets=q(v[0]),liabilities=q(v[1]),net_worth=q(v[0]-v[1])) for c,v in sorted(d.items())]
def snap(db,user,id):
 x=db.scalar(select(Snapshot).where(Snapshot.id==id,Snapshot.user_id==str(user.id)).options(selectinload(Snapshot.items)))
 if not x:fail(404,"Snapshot not found.")
 return x
def snapshot(x,detail=False):
 data=dict(id=x.id,snapshot_date=x.snapshot_date,name=x.name,notes=x.notes,account_count=len(x.items),totals=totals(x.items),created_at=x.created_at)
 return SnapshotDetail(**data,items=[SnapshotItemResponse(id=i.id,account_id=i.account_id,account_name=i.account_name,account_type=i.account_type,category=i.category,currency_code=i.currency_code,balance_amount=i.balance_amount,included=i.included) for i in x.items]) if detail else SnapshotSummary(**data)
def create_snapshot(db,user,p):
 if p.snapshot_date>date.today():fail(422,"Snapshot date cannot be in the future.")
 if db.scalar(select(Snapshot).where(Snapshot.user_id==str(user.id),Snapshot.snapshot_date==p.snapshot_date)):fail(409,"Only one snapshot is allowed per date.")
 x=Snapshot(user_id=str(user.id),snapshot_date=p.snapshot_date,name=p.name,notes=p.notes);db.add(x);db.flush();accounts=db.scalars(select(Account).where(Account.user_id==str(user.id),Account.status=="active")).all()
 for a in accounts:db.add(SnapshotItem(snapshot_id=x.id,account_id=a.id,account_name=a.name,account_type=a.account_type,category=a.category,currency_code=a.currency_code,balance_amount=a.current_balance,included=a.include_in_net_worth))
 db.commit();return get_snapshot(db,user,x.id)
def get_snapshot(db,user,id):return snapshot(snap(db,user,id),True)
def list_snapshots(db,user,qv=None,date_from=None,date_to=None,page=1,page_size=12):
 if date_from and date_to and date_from>date_to:fail(422,"Date range is reversed.")
 stmt=select(Snapshot).where(Snapshot.user_id==str(user.id)).options(selectinload(Snapshot.items));term=(qv or "").strip()
 if term:stmt=stmt.where(Snapshot.name.ilike(f"%{term}%"))
 if date_from:stmt=stmt.where(Snapshot.snapshot_date>=date_from)
 if date_to:stmt=stmt.where(Snapshot.snapshot_date<=date_to)
 total=db.scalar(select(func.count()).select_from(stmt.order_by(None).subquery())) or 0;xs=db.scalars(stmt.order_by(Snapshot.snapshot_date.desc(),Snapshot.created_at.desc()).offset((page-1)*page_size).limit(page_size)).unique().all();return SnapshotList(items=[snapshot(x) for x in xs],total=total,page=page,page_size=page_size,pages=max(1,ceil(total/page_size)))
def delete_snapshot(db,user,id):db.delete(snap(db,user,id));db.commit()
def compare(db,user,previous_id,current_id):
 p=snap(db,user,previous_id);c=snap(db,user,current_id);pt={x.currency_code:x for x in totals(p.items)};ct={x.currency_code:x for x in totals(c.items)};rows=[]
 for code in sorted(set(pt)|set(ct)):
  a=pt.get(code,CurrencyTotal(currency_code=code,assets=0,liabilities=0,net_worth=0));b=ct.get(code,CurrencyTotal(currency_code=code,assets=0,liabilities=0,net_worth=0));pct=None if a.net_worth==0 else q((b.net_worth-a.net_worth)/abs(a.net_worth)*100);rows.append(ChangeTotal(**b.model_dump(),asset_difference=q(b.assets-a.assets),liability_difference=q(b.liabilities-a.liabilities),net_worth_difference=q(b.net_worth-a.net_worth),percentage_change=pct))
 return Comparison(previous=snapshot(p),current=snapshot(c),currencies=rows,warning="Currencies are compared independently; no conversion is performed.")
def dashboard(db,user):
 xs=db.scalars(select(Account).where(Account.user_id==str(user.id)).options(selectinload(Account.entries)).order_by(Account.updated_at.desc())).unique().all();active=[x for x in xs if x.status=="active"];latest=db.scalar(select(Snapshot.snapshot_date).where(Snapshot.user_id==str(user.id)).order_by(Snapshot.snapshot_date.desc()));return Dashboard(active_assets=sum(x.account_type=="asset" for x in active),active_liabilities=sum(x.account_type=="liability" for x in active),archived_accounts=sum(x.status=="archived" for x in xs),excluded_accounts=sum(x.status=="active" and not x.include_in_net_worth for x in xs),totals=totals(active),latest_snapshot_date=latest,recent_accounts=[account(x) for x in xs[:5]])
