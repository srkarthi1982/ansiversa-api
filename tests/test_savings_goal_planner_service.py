import unittest
from datetime import date,timedelta
from decimal import Decimal
from types import SimpleNamespace
from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import create_engine,select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.modules.savings_goal_planner.db import Base
from app.modules.savings_goal_planner.models import Goal,Milestone,Transaction
from app.modules.savings_goal_planner.schemas import GoalCreate,MilestoneCreate,TransactionCreate
from app.modules.savings_goal_planner.service import dashboard,delete_goal,delete_milestone,delete_tx,get_goal,list_goals,save_goal,save_milestone,save_tx
class SavingsTests(unittest.TestCase):
 def setUp(self):
  e=create_engine("sqlite://",connect_args={"check_same_thread":False},poolclass=StaticPool);Base.metadata.create_all(e);self.db=sessionmaker(bind=e)();self.a=SimpleNamespace(id="a");self.b=SimpleNamespace(id="b");self.g=save_goal(self.db,self.a,GoalCreate(name="Emergency Fund",category="emergency",currencyCode="AED",targetAmount="1000.00",startingAmount="100.00",targetDate=date.today()+timedelta(days=28),priority="high"))
 def tearDown(self):self.db.close()
 def tx(self,t,a):self.g=save_tx(self.db,self.a,self.g.id,TransactionCreate(transactionDate=date.today(),transactionType=t,amount=a));return self.g
 def test_money_progress_pace_completion_and_recalculation(self):
  self.tx("contribution","333.33");self.assertEqual(self.g.current_amount,Decimal("433.33"));self.assertEqual(self.g.remaining_amount,Decimal("566.67"));self.assertGreater(self.g.required_weekly,0)
  x=self.g.transactions[0];self.g=save_tx(self.db,self.a,self.g.id,TransactionCreate(transactionDate=date.today(),transactionType="contribution",amount="400"),x.id);self.assertEqual(self.g.current_amount,Decimal("500.00"));delete_tx(self.db,self.a,self.g.id,x.id);self.g=get_goal(self.db,self.a,self.g.id);self.assertEqual(self.g.current_amount,Decimal("100.00"))
  self.tx("contribution","900");self.assertEqual(self.g.status,"completed");self.assertEqual(self.g.progress_percent,Decimal("100.00"))
  with self.assertRaises(HTTPException):self.tx("contribution","0.01")
 def test_withdrawals_states_milestones_and_ownership(self):
  self.tx("contribution","200");self.tx("withdrawal","50");self.tx("adjustment_increase","20");self.tx("adjustment_decrease","10");self.assertEqual(self.g.current_amount,Decimal("260.00"))
  with self.assertRaises(HTTPException):self.tx("withdrawal","300")
  self.g=save_milestone(self.db,self.a,self.g.id,MilestoneCreate(name="First",targetAmount="200"));self.assertEqual(self.g.milestones[0].status,"reached");mid=self.g.milestones[0].id;delete_milestone(self.db,self.a,self.g.id,mid)
  with self.assertRaises(HTTPException):get_goal(self.db,self.b,self.g.id)
  tx_id=self.g.transactions[0].id
  paused=GoalCreate(name="Emergency Fund",targetAmount=1000,startingAmount=100,status="paused");self.g=save_goal(self.db,self.a,paused,self.g.id)
  with self.assertRaises(HTTPException):self.tx("contribution","1")
  with self.assertRaises(HTTPException):delete_tx(self.db,self.a,self.g.id,tx_id)
  for status in("cancelled","archived"):
   self.g=save_goal(self.db,self.a,GoalCreate(name="Emergency Fund",targetAmount=1000,startingAmount=100,status=status),self.g.id)
   with self.assertRaises(HTTPException):self.tx("contribution","1")
   with self.assertRaises(HTTPException):delete_tx(self.db,self.a,self.g.id,tx_id)
 def test_validation_filters_dashboard_currency_and_cascade(self):
  for payload in [dict(name=" ",targetAmount=1),dict(name="x",targetAmount=0),dict(name="x",targetAmount=1,startingAmount=2),dict(name="x",targetAmount=1,currencyCode="US")]:
   with self.assertRaises(ValidationError):GoalCreate(**payload)
  travel=save_goal(self.db,self.a,GoalCreate(name="Travel",category="travel",currencyCode="USD",targetAmount=500,targetDate=date.today()-timedelta(days=1)))
  d=dashboard(self.db,self.a);self.assertEqual(len(d.currency_totals),2);self.assertEqual(d.overdue_goals,1)
  found=list_goals(self.db,self.a," travel ",None,"travel",None,"usd","overdue",None,None,1,10);self.assertEqual(found.total,1)
  travel=save_tx(self.db,self.a,travel.id,TransactionCreate(transactionDate=date.today(),transactionType="contribution",amount=10));travel=save_milestone(self.db,self.a,travel.id,MilestoneCreate(name="Start",targetAmount=10));delete_goal(self.db,self.a,travel.id);self.assertIsNone(self.db.scalar(select(Goal).where(Goal.id==travel.id)));self.assertEqual(len(self.db.scalars(select(Transaction)).all()),0);self.assertEqual(len(self.db.scalars(select(Milestone)).all()),0)
if __name__=="__main__":unittest.main()
