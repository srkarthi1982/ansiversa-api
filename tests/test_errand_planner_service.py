import unittest
from datetime import date,timedelta
from types import SimpleNamespace
from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.modules.errand_planner.db import Base
from app.modules.errand_planner.schemas import CategoryCreate,ErrandCreate
from app.modules.errand_planner.service import archive,dashboard,delete_category,delete_errand,get_errand,list_categories,list_errands,restore,save_category,save_errand,set_status
class ErrandPlannerTests(unittest.TestCase):
 def setUp(self):
  e=create_engine("sqlite://",connect_args={"check_same_thread":False},poolclass=StaticPool);Base.metadata.create_all(e);self.db=sessionmaker(bind=e)();self.a=SimpleNamespace(id="a");self.b=SimpleNamespace(id="b");self.cat=save_category(self.db,self.a,CategoryCreate(name="Grocery",color="green",sortOrder=1))
 def tearDown(self):self.db.close()
 def make(self,**kw):
  data=dict(title="Buy milk",description="Weekly shop",categoryId=self.cat.id,priority="high",dueDate=date.today(),estimatedMinutes=30,location="Market",status="pending",notes="Use card");data.update(kw);return save_errand(self.db,self.a,ErrandCreate(**data))
 def test_validation_duplicate_ownership_search_filters_dashboard(self):
  for p in [dict(title=" "),dict(title="x",priority="urgent"),dict(title="x",estimatedMinutes=0)]:
   with self.assertRaises(ValidationError):ErrandCreate(**p)
  with self.assertRaises(HTTPException):save_category(self.db,self.a,CategoryCreate(name=" grocery "))
  e=self.make();self.assertTrue(e.is_due_today);self.assertTrue(e.is_due_soon);self.assertFalse(e.is_overdue)
  with self.assertRaises(HTTPException):get_errand(self.db,self.b,e.id)
  self.assertEqual(list_errands(self.db,self.a,"milk",None,self.cat.id,"high",None,True,None,None,None,1,10).total,1)
  summary=list_errands(self.db,self.a,"milk",None,self.cat.id,"high",None,True,None,None,None,1,10).items[0]
  self.assertNotIn("description",summary.model_dump())
  self.assertNotIn("notes",summary.model_dump())
  self.assertEqual(dashboard(self.db,self.a).pending,1);self.assertEqual(list_categories(self.db,self.a).items[0].errand_count,1)
  with self.assertRaises(HTTPException):list_errands(self.db,self.a,due_from=date.today(),due_to=date.today()-timedelta(days=1))
 def test_status_archive_restore_delete_category_rules(self):
  e=self.make(dueDate=date.today()-timedelta(days=1));self.assertTrue(get_errand(self.db,self.a,e.id).is_overdue)
  with self.assertRaises(HTTPException):archive(self.db,self.a,e.id)
  e=set_status(self.db,self.a,e.id,"completed");self.assertIsNotNone(e.completed_at)
  e=archive(self.db,self.a,e.id);self.assertEqual(e.status,"archived")
  with self.assertRaises(HTTPException):save_errand(self.db,self.a,ErrandCreate(title="Blocked",status="pending"),e.id)
  with self.assertRaises(HTTPException):delete_errand(self.db,self.a,e.id)
  e=restore(self.db,self.a,e.id);self.assertEqual(e.status,"completed")
  e=set_status(self.db,self.a,e.id,"pending");self.assertIsNone(e.completed_at)
  with self.assertRaises(HTTPException):delete_category(self.db,self.a,self.cat.id)
  delete_errand(self.db,self.a,e.id);delete_category(self.db,self.a,self.cat.id);self.assertEqual(list_categories(self.db,self.a).total,0)
if __name__=="__main__":unittest.main()
