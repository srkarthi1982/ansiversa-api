import unittest
from types import SimpleNamespace
from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.modules.emergency_checklist.db import Base
from app.modules.emergency_checklist.schemas import ChecklistItemCreate,EmergencyCategoryCreate,EmergencyChecklistCreate
from app.modules.emergency_checklist.service import archive,complete_all,dashboard,delete_category,delete_checklist,delete_item,get_checklist,list_categories,list_checklists,reset,restore,save_category,save_checklist,save_item,toggle_item
class EmergencyChecklistTests(unittest.TestCase):
 def setUp(self):
  e=create_engine("sqlite://",connect_args={"check_same_thread":False},poolclass=StaticPool);Base.metadata.create_all(e);self.db=sessionmaker(bind=e)();self.a=SimpleNamespace(id="a");self.b=SimpleNamespace(id="b");self.cat=save_category(self.db,self.a,EmergencyCategoryCreate(name="Fire",color="red",sortOrder=1))
 def tearDown(self):self.db.close()
 def make(self,**kw):
  data=dict(title="Home fire plan",categoryId=self.cat.id,description="Family preparation");data.update(kw);return save_checklist(self.db,self.a,EmergencyChecklistCreate(**data))
 def test_crud_ownership_completion_reset_search_filters_dashboard(self):
  with self.assertRaises(ValidationError):EmergencyChecklistCreate(title=" ")
  x=self.make();x=save_item(self.db,self.a,x.id,ChecklistItemCreate(title="Check extinguisher",notes="Kitchen",sortOrder=2));x=save_item(self.db,self.a,x.id,ChecklistItemCreate(title="Review exit route",sortOrder=1))
  self.assertEqual(x.total_items,2);self.assertEqual([i.title for i in x.items],["Review exit route","Check extinguisher"])
  with self.assertRaises(HTTPException):get_checklist(self.db,self.b,x.id)
  item=x.items[0];x=toggle_item(self.db,self.a,x.id,item.id,True);self.assertEqual(x.completed_items,1);self.assertEqual(x.completion_percentage,50)
  x=complete_all(self.db,self.a,x.id);self.assertEqual(x.completion_percentage,100)
  self.assertEqual(list_checklists(self.db,self.a,completion="completed").total,1)
  x=reset(self.db,self.a,x.id);self.assertEqual(x.completed_items,0);self.assertEqual(list_checklists(self.db,self.a,"route",self.cat.id,False,"incomplete",1,10).total,1)
  d=dashboard(self.db,self.a);self.assertEqual(d.total_checklists,1);self.assertEqual(d.incomplete,1);self.assertEqual(d.categories,1)
 def test_archive_restore_duplicates_delete_contracts(self):
  x=self.make()
  with self.assertRaises(HTTPException):self.make(title="home fire plan")
  x=archive(self.db,self.a,x.id);self.assertTrue(x.archived)
  with self.assertRaises(HTTPException):save_item(self.db,self.a,x.id,ChecklistItemCreate(title="Blocked"))
  with self.assertRaises(HTTPException):delete_checklist(self.db,self.a,x.id)
  x=restore(self.db,self.a,x.id);self.assertFalse(x.archived)
  x=save_item(self.db,self.a,x.id,ChecklistItemCreate(title="Water",sortOrder=1));x=delete_item(self.db,self.a,x.id,x.items[0].id);self.assertEqual(x.total_items,0)
  with self.assertRaises(HTTPException):delete_category(self.db,self.a,self.cat.id)
  delete_checklist(self.db,self.a,x.id);delete_category(self.db,self.a,self.cat.id);self.assertEqual(list_categories(self.db,self.a).total,0)
if __name__=="__main__":unittest.main()
