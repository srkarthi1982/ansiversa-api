import unittest
from types import SimpleNamespace
from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import create_engine,select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.modules.salary_breakdown_calculator.db import Base
from app.modules.salary_breakdown_calculator.models import Deduction,Earning,Scenario
from app.modules.salary_breakdown_calculator.schemas import DeductionCreate,EarningCreate,ScenarioCreate
from app.modules.salary_breakdown_calculator.service import annual,compare,dashboard,delete,delete_deduction,delete_earning,get,list_scenarios,save_deduction,save_earning,save_scenario
class SalaryTests(unittest.TestCase):
 def setUp(self):
  e=create_engine("sqlite://",connect_args={"check_same_thread":False},poolclass=StaticPool);Base.metadata.create_all(e);self.db=sessionmaker(bind=e)();self.a=SimpleNamespace(id="a");self.b=SimpleNamespace(id="b");self.s=save_scenario(self.db,self.a,ScenarioCreate(name="Offer A",currencyCode="AED",payFrequency="monthly",baseSalaryAmount=10000,baseSalaryPeriod="monthly"))
 def tearDown(self):self.db.close()
 def test_frequency_normalization_components_and_recalculation(self):
  expected={"weekly":"5200.00","biweekly":"2600.00","semimonthly":"2400.00","monthly":"1200.00","quarterly":"400.00","annual":"100.00"}
  for f,v in expected.items():self.assertEqual(str(annual(100,f)),v)
  self.s=save_earning(self.db,self.a,self.s.id,EarningCreate(name="Housing",earningType="allowance",amount=1000,frequency="monthly",isRecurring=True));self.s=save_earning(self.db,self.a,self.s.id,EarningCreate(name="Joining",earningType="bonus",amount=5000,frequency="annual",isRecurring=False));self.assertEqual(str(self.s.recurring_gross),"132000.00");self.assertEqual(str(self.s.one_time_earnings),"5000.00")
  self.s=save_deduction(self.db,self.a,self.s.id,DeductionCreate(name="Insurance",deductionType="insurance",calculationMethod="fixed_amount",amount=100,frequency="monthly"));self.s=save_deduction(self.db,self.a,self.s.id,DeductionCreate(name="Retirement",deductionType="retirement",calculationMethod="percentage_of_base",percentage=5,frequency="monthly"));self.s=save_deduction(self.db,self.a,self.s.id,DeductionCreate(name="Estimate",deductionType="tax_estimate",calculationMethod="percentage_of_gross",percentage=10,frequency="monthly"));self.assertEqual(str(self.s.recurring_deductions),"20400.00");self.assertEqual(str(self.s.recurring_net),"111600.00")
  eid=self.s.earnings[0].id;delete_earning(self.db,self.a,self.s.id,eid);self.s=get(self.db,self.a,self.s.id);self.assertEqual(str(self.s.recurring_gross),"120000.00")
 def test_validation_archived_ownership_and_negative_net(self):
  for p in [dict(name=" ",baseSalaryAmount=1),dict(name="x",baseSalaryAmount=-1),dict(name="x",baseSalaryAmount=1,currencyCode="US"),dict(name="x",baseSalaryAmount=1,workingDaysPerWeek=8)]:
   with self.assertRaises(ValidationError):ScenarioCreate(**p)
  with self.assertRaises(ValidationError):DeductionCreate(name="x",deductionType="other",calculationMethod="fixed_amount",amount=1,percentage=2)
  with self.assertRaises(ValidationError):DeductionCreate(name="x",deductionType="other",calculationMethod="percentage_of_base",percentage=101)
  with self.assertRaises(HTTPException):get(self.db,self.b,self.s.id)
  self.s=save_scenario(self.db,self.a,ScenarioCreate(name="Offer A",baseSalaryAmount=10000,status="archived"),self.s.id)
  with self.assertRaises(HTTPException):save_earning(self.db,self.a,self.s.id,EarningCreate(name="x",earningType="other",amount=1))
  self.s=save_scenario(self.db,self.a,ScenarioCreate(name="Offer A",baseSalaryAmount=10000,status="active"),self.s.id);self.assertEqual(self.s.status,"active")
  with self.assertRaises(HTTPException):save_deduction(self.db,self.a,self.s.id,DeductionCreate(name="Too much",deductionType="other",calculationMethod="fixed_amount",amount=10001,frequency="monthly"))
 def test_comparison_dashboard_filters_and_cascade(self):
  other=save_scenario(self.db,self.a,ScenarioCreate(name="Offer B",currencyCode="AED",payFrequency="annual",baseSalaryAmount=150000,baseSalaryPeriod="annual"));c=compare(self.db,self.a,self.s.id,other.id);self.assertTrue(c.currency_compatible);self.assertEqual(str(c.net_difference),"30000.00")
  usd=save_scenario(self.db,self.a,ScenarioCreate(name="US Offer",currencyCode="USD",baseSalaryAmount=1000));c=compare(self.db,self.a,self.s.id,usd.id);self.assertFalse(c.currency_compatible);self.assertIsNone(c.net_difference)
  d=dashboard(self.db,self.a);self.assertEqual(len(d.currency_totals),2);self.assertEqual(sum(x.count for x in d.frequency_counts),3)
  found=list_scenarios(self.db,self.a," offer ","active","annual","AED",None,None,None,None,1,1);self.assertEqual(found.total,1);self.assertEqual(len(found.items),1)
  other=save_earning(self.db,self.a,other.id,EarningCreate(name="Bonus",earningType="bonus",amount=1));other=save_deduction(self.db,self.a,other.id,DeductionCreate(name="Fee",deductionType="other",calculationMethod="fixed_amount",amount=1));delete(self.db,self.a,other.id);self.assertIsNone(self.db.scalar(select(Scenario).where(Scenario.id==other.id)));self.assertEqual(len(self.db.scalars(select(Earning)).all()),0);self.assertEqual(len(self.db.scalars(select(Deduction)).all()),0)
if __name__=="__main__":unittest.main()
