import unittest
from decimal import Decimal
from types import SimpleNamespace
from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.modules.bill_splitter.db import Base
from app.modules.bill_splitter.schemas import AllocationReplace,BillCreate,ItemCreate,ParticipantCreate
from app.modules.bill_splitter.service import dashboard,delete_participant,get_bill,replace_allocations,save_bill,save_item,save_participant

class BillSplitterTests(unittest.TestCase):
 def setUp(self):
  e=create_engine("sqlite://",connect_args={"check_same_thread":False},poolclass=StaticPool);Base.metadata.create_all(e);self.db=sessionmaker(bind=e)();self.a=SimpleNamespace(id="a");self.b=SimpleNamespace(id="b");self.bill=save_bill(self.db,self.a,BillCreate(title="Dinner",billDate="2026-07-16",merchantName="Cafe",currencyCode="aed"))
  for name in("A","B","C"):self.bill=save_participant(self.db,self.a,self.bill.id,ParticipantCreate(name=name))
 def tearDown(self):self.db.close()
 def add_item(self,name="Meal",quantity="1",price="100.00"):
  self.bill=save_item(self.db,self.a,self.bill.id,ItemCreate(name=name,quantity=quantity,unitPrice=price,splitMethod="equal"));return self.bill.items[-1]
 def test_decimal_totals_equal_remainder_and_dashboard(self):
  i=self.add_item();ids=[p.id for p in self.bill.participants];self.bill=replace_allocations(self.db,self.a,self.bill.id,i.id,AllocationReplace(splitMethod="equal",allocations=[{"participantId":x}for x in ids]));self.bill=save_bill(self.db,self.a,BillCreate(title="Dinner",billDate="2026-07-16",merchantName="Cafe",currencyCode="AED",discountAmount="1.00",taxAmount="2.00",serviceChargeAmount="1.00",tipAmount="1.00"),self.bill.id);amounts=[a.amount for a in self.bill.items[0].allocations];self.assertEqual(amounts,[Decimal("33.34"),Decimal("33.33"),Decimal("33.33")]);self.assertEqual(self.bill.subtotal_amount,Decimal("100.00"));self.assertEqual(self.bill.total_amount,Decimal("103.00"));self.assertEqual(sum(p.share_amount for p in self.bill.participants),Decimal("103.00"));self.assertEqual(dashboard(self.db,self.a).recorded_value,Decimal("103.00"))
 def test_custom_single_validation_and_safe_participant_delete(self):
  i=self.add_item(price="10.00");ids=[p.id for p in self.bill.participants]
  with self.assertRaises(HTTPException):save_participant(self.db,self.a,self.bill.id,ParticipantCreate(name="a"))
  with self.assertRaises(HTTPException):save_participant(self.db,self.a,self.bill.id,ParticipantCreate(name="b"),ids[0])
  with self.assertRaises(HTTPException):replace_allocations(self.db,self.a,self.bill.id,i.id,AllocationReplace(splitMethod="custom",allocations=[{"participantId":ids[0],"amount":"4"},{"participantId":ids[1],"amount":"4"}]))
  self.bill=replace_allocations(self.db,self.a,self.bill.id,i.id,AllocationReplace(splitMethod="single_participant",allocations=[{"participantId":ids[0]}]));self.assertEqual(self.bill.items[0].allocations[0].amount,Decimal("10.00"))
  with self.assertRaises(HTTPException):delete_participant(self.db,self.a,self.bill.id,ids[0])
  foreign=save_bill(self.db,self.b,BillCreate(title="Other",billDate="2026-07-16"));foreign=save_participant(self.db,self.b,foreign.id,ParticipantCreate(name="X"))
  with self.assertRaises(HTTPException):replace_allocations(self.db,self.a,self.bill.id,i.id,AllocationReplace(splitMethod="single_participant",allocations=[{"participantId":foreign.participants[0].id}]))
 def test_validation_ownership_and_settled_consistency(self):
  with self.assertRaises(ValidationError):BillCreate(title=" ",billDate="2026-07-16")
  with self.assertRaises(ValidationError):BillCreate(title="X",billDate="2026-07-16",currencyCode="US")
  with self.assertRaises(ValidationError):ItemCreate(name="Bad",quantity=0,unitPrice=1)
  with self.assertRaises(ValidationError):ParticipantCreate(name="Bad",email="invalid")
  with self.assertRaises(HTTPException):get_bill(self.db,self.b,self.bill.id)
  i=self.add_item(price="5.00");ids=[p.id for p in self.bill.participants];self.bill=replace_allocations(self.db,self.a,self.bill.id,i.id,AllocationReplace(splitMethod="equal",allocations=[{"participantId":x}for x in ids]))
  with self.assertRaises(HTTPException):save_bill(self.db,self.a,BillCreate(title="Dinner",billDate="2026-07-16",status="settled"),self.bill.id)

if __name__=="__main__":unittest.main()
