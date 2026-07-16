import unittest
from datetime import date,timedelta
from types import SimpleNamespace
from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.modules.net_worth_tracker.db import Base
from app.modules.net_worth_tracker.schemas import AccountCreate,BalanceCreate,SnapshotCreate
from app.modules.net_worth_tracker.service import compare,create_snapshot,dashboard,delete_account,delete_entry,get_account,save_account,save_entry
class NetWorthTests(unittest.TestCase):
 def setUp(self):
  e=create_engine("sqlite://",connect_args={"check_same_thread":False},poolclass=StaticPool);Base.metadata.create_all(e);self.db=sessionmaker(bind=e)();self.a=SimpleNamespace(id="a");self.b=SimpleNamespace(id="b");self.today=date.today()
 def tearDown(self):self.db.close()
 def make(self,name="Cash",kind="asset",category="cash",amount=100,currency="AED",included=True):return save_account(self.db,self.a,AccountCreate(name=name,accountType=kind,category=category,currencyCode=currency,currentBalance=amount,valuationDate=self.today,includeInNetWorth=included))
 def test_validation_totals_currency_negative_and_ownership(self):
  for p in [dict(name=" ",accountType="asset",category="cash",currentBalance=1,valuationDate=self.today),dict(name="x",accountType="asset",category="mortgage",currentBalance=1,valuationDate=self.today),dict(name="x",accountType="asset",category="cash",currentBalance=-1,valuationDate=self.today),dict(name="x",accountType="asset",category="cash",currencyCode="US",currentBalance=1,valuationDate=self.today)]:
   with self.assertRaises(ValidationError):AccountCreate(**p)
  self.make();self.make("Loan","liability","personal_loan",150);self.make("USD","asset","cash",20,"USD");self.make("Excluded","asset","cash",999,"AED",False);d=dashboard(self.db,self.a);aed=next(x for x in d.totals if x.currency_code=="AED");self.assertEqual(str(aed.net_worth),"-50.00");self.assertEqual(len(d.totals),2)
  with self.assertRaises(HTTPException):get_account(self.db,self.b,self.make("Private").id)
 def test_balance_recalculation_archive_and_safe_delete(self):
  x=self.make();x=save_entry(self.db,self.a,x.id,BalanceCreate(balanceDate=self.today+timedelta(1),balanceAmount=200));eid=x.entries[0].id;x=save_entry(self.db,self.a,x.id,BalanceCreate(balanceDate=self.today+timedelta(1),balanceAmount=250),eid);self.assertEqual(str(x.current_balance),"250.00");delete_entry(self.db,self.a,x.id,eid);self.assertEqual(str(get_account(self.db,self.a,x.id).current_balance),"100.00")
  with self.assertRaises(HTTPException):delete_account(self.db,self.a,x.id)
  z=self.make("Empty",amount=0);delete_account(self.db,self.a,z.id)
  archived=save_account(self.db,self.a,AccountCreate(name="Cash",accountType="asset",category="cash",currentBalance=100,valuationDate=self.today,status="archived"),x.id)
  with self.assertRaises(HTTPException):save_entry(self.db,self.a,archived.id,BalanceCreate(balanceDate=self.today,balanceAmount=1))
 def test_snapshot_immutability_comparison_and_duplicate(self):
  x=self.make();p=create_snapshot(self.db,self.a,SnapshotCreate(snapshotDate=self.today-timedelta(1),name="Before"));save_entry(self.db,self.a,x.id,BalanceCreate(balanceDate=self.today,balanceAmount=150));c=create_snapshot(self.db,self.a,SnapshotCreate(snapshotDate=self.today,name="After"));cmp=compare(self.db,self.a,p.id,c.id);self.assertEqual(str(cmp.currencies[0].net_worth_difference),"50.00");self.assertEqual(str(p.items[0].balance_amount),"100.00")
  with self.assertRaises(HTTPException):create_snapshot(self.db,self.a,SnapshotCreate(snapshotDate=self.today,name="Duplicate"))
if __name__=="__main__":unittest.main()
