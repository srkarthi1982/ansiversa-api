import unittest
from datetime import date,timedelta
from types import SimpleNamespace
from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import create_engine,select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.modules.decision_maker.db import Base
from app.modules.decision_maker.models import Criterion,Decision,Option,Rating
from app.modules.decision_maker.schemas import CriterionCreate,DecisionCreate,OptionCreate,RatingMatrix,RatingUpsert
from app.modules.decision_maker.service import dashboard,delete_criterion,delete_decision,delete_option,get,list_decisions,save_criterion,save_decision,save_option,upsert_ratings
class DecisionMakerTests(unittest.TestCase):
 def setUp(self):
  e=create_engine("sqlite://",connect_args={"check_same_thread":False},poolclass=StaticPool);Base.metadata.create_all(e);self.db=sessionmaker(bind=e)();self.a=SimpleNamespace(id="a");self.b=SimpleNamespace(id="b");self.d=save_decision(self.db,self.a,DecisionCreate(title="Choose role",question="Which role should I choose?",decisionType="career",ratingScale=5,targetDate=date.today()+timedelta(days=3)))
 def tearDown(self):self.db.close()
 def setup_matrix(self):
  self.d=save_option(self.db,self.a,self.d.id,OptionCreate(name="A",pros="Growth"));self.d=save_option(self.db,self.a,self.d.id,OptionCreate(name="B"));self.d=save_criterion(self.db,self.a,self.d.id,CriterionCreate(name="Growth",weight=3));self.d=save_criterion(self.db,self.a,self.d.id,CriterionCreate(name="Cost",weight=1,direction="lower_is_better"));o=self.d.options;c=self.d.criteria;ratings=[RatingUpsert(optionId=o[0].id,criterionId=c[0].id,rating=5),RatingUpsert(optionId=o[0].id,criterionId=c[1].id,rating=4),RatingUpsert(optionId=o[1].id,criterionId=c[0].id,rating=3),RatingUpsert(optionId=o[1].id,criterionId=c[1].id,rating=1)];self.d=upsert_ratings(self.db,self.a,self.d.id,RatingMatrix(ratings=ratings));return o,c
 def test_validation_duplicate_ownership_filters_dashboard(self):
  for p in [dict(title=" ",question="x"),dict(title="x",question=" "),dict(title="x",question="q",ratingScale=7)]:
   with self.assertRaises(ValidationError):DecisionCreate(**p)
  save_option(self.db,self.a,self.d.id,OptionCreate(name="Same"))
  with self.assertRaises(HTTPException):save_option(self.db,self.a,self.d.id,OptionCreate(name="same"))
  with self.assertRaises(HTTPException):get(self.db,self.b,self.d.id)
  found=list_decisions(self.db,self.a," choose ",None,"career",True,None,None,None,None,None,1,10);self.assertEqual(found.total,1);self.assertEqual(dashboard(self.db,self.a).total,1)
  with self.assertRaises(HTTPException):list_decisions(self.db,self.a,created_from=date.today(),created_to=date.today()-timedelta(days=1))
 def test_scoring_direction_weights_incomplete_tie_and_scale_guard(self):
  o,c=self.setup_matrix();self.assertTrue(self.d.evaluation_complete);self.assertEqual(str(self.d.criteria[0].normalized_weight),"75.00");self.assertEqual(str(self.d.options[0].score),"85.00");self.assertEqual(str(self.d.options[1].score),"70.00")
  self.d=upsert_ratings(self.db,self.a,self.d.id,RatingMatrix(ratings=[RatingUpsert(optionId=o[1].id,criterionId=c[0].id,rating=4)]));self.assertEqual([x.rank for x in self.d.options],[1,1]);self.assertTrue(all(x.is_tied for x in self.d.options))
  with self.assertRaises(HTTPException):upsert_ratings(self.db,self.a,self.d.id,RatingMatrix(ratings=[RatingUpsert(optionId=o[0].id,criterionId=c[0].id,rating=5),RatingUpsert(optionId=o[0].id,criterionId=c[0].id,rating=4)]))
  self.d=save_option(self.db,self.a,self.d.id,OptionCreate(name="Incomplete"));self.assertIsNone(self.d.options[2].score);self.assertEqual(str(self.d.options[2].completion_percent),"0.00")
  with self.assertRaises(HTTPException):save_decision(self.db,self.a,DecisionCreate(title=self.d.title,question=self.d.question,ratingScale=10),self.d.id)
 def test_status_selected_protection_archived_and_cascade(self):
  o,c=self.setup_matrix();payload=DecisionCreate(title=self.d.title,question=self.d.question,decisionType="career",ratingScale=5,status="decided",targetDate=self.d.target_date,selectedOptionId=o[1].id,outcome="Selected B");self.d=save_decision(self.db,self.a,payload,self.d.id);self.assertIsNotNone(self.d.decided_at)
  with self.assertRaises(HTTPException):delete_option(self.db,self.a,self.d.id,o[1].id)
  revisit=payload.model_copy(update={"status":"revisiting"});self.d=save_decision(self.db,self.a,revisit,self.d.id);delete_criterion(self.db,self.a,self.d.id,c[0].id);self.assertEqual(self.db.scalar(select(Rating).where(Rating.criterion_id==c[0].id)),None)
  archived=revisit.model_copy(update={"status":"archived"});self.d=save_decision(self.db,self.a,archived,self.d.id)
  with self.assertRaises(HTTPException):save_option(self.db,self.a,self.d.id,OptionCreate(name="Blocked"))
  did=self.d.id;delete_decision(self.db,self.a,did);self.assertIsNone(self.db.scalar(select(Decision).where(Decision.id==did)));self.assertEqual(len(self.db.scalars(select(Option)).all()),0);self.assertEqual(len(self.db.scalars(select(Criterion)).all()),0)
if __name__=="__main__":unittest.main()
