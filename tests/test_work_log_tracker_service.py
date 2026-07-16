import unittest
from datetime import date
from types import SimpleNamespace
from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.modules.work_log_tracker.db import WorkLogBase
from app.modules.work_log_tracker.schemas import LogCreate,ProjectCreate
from app.modules.work_log_tracker.service import dashboard,delete_project,get_log,list_logs,save_log,save_project

class WorkLogTrackerTests(unittest.TestCase):
 def setUp(self):
  e=create_engine("sqlite://",connect_args={"check_same_thread":False},poolclass=StaticPool);WorkLogBase.metadata.create_all(e);self.db=sessionmaker(bind=e)();self.a=SimpleNamespace(id="a");self.b=SimpleNamespace(id="b");self.p=save_project(self.db,self.a,ProjectCreate(name="Platform",code="PLAT",clientName="Ansiversa",defaultBillable=True))
 def tearDown(self):self.db.close()
 def timed(self,**x):
  d={"projectId":self.p.id,"title":"Implementation","workDate":"2026-07-20","startTime":"09:00","endTime":"17:00","breakMinutes":30,"entryMode":"timed","status":"completed","isBillable":True};d.update(x);return LogCreate(**d)
 def manual(self,**x):
  d={"projectId":self.p.id,"title":"Documentation","workDate":"2026-07-20","manualDurationMinutes":90,"entryMode":"manual","status":"completed","isBillable":False};d.update(x);return LogCreate(**d)
 def test_projects_duplicates_ownership_and_safe_delete(self):
  self.assertTrue(self.p.default_billable)
  with self.assertRaises(HTTPException):save_project(self.db,self.a,ProjectCreate(name="Platform",code="OTHER"))
  foreign=save_project(self.db,self.b,ProjectCreate(name="Foreign"))
  with self.assertRaises(HTTPException):save_log(self.db,self.a,self.timed(projectId=foreign.id))
  created=save_log(self.db,self.a,self.timed())
  with self.assertRaises(HTTPException):delete_project(self.db,self.a,self.p.id)
  with self.assertRaises(HTTPException):get_log(self.db,self.b,created.id)
 def test_modes_duration_break_overnight_and_bounds(self):
  self.assertEqual(save_log(self.db,self.a,self.timed()).duration_minutes,450)
  self.assertEqual(save_log(self.db,self.a,self.manual()).duration_minutes,90)
  self.assertEqual(save_log(self.db,self.a,self.timed(title="Night",workDate="2026-07-21",startTime="22:00",endTime="06:00",breakMinutes=60)).duration_minutes,420)
  with self.assertRaises(HTTPException):save_log(self.db,self.a,self.timed(title="Bad",workDate="2026-07-22",breakMinutes=480))
  with self.assertRaises(ValidationError):self.manual(manualDurationMinutes=0)
  with self.assertRaises(ValidationError):self.manual(manualDurationMinutes=1441)
  with self.assertRaises(ValidationError):self.timed(breakMinutes=-1)
 def test_overlap_back_to_back_cancelled_manual_filters_and_metrics(self):
  first=save_log(self.db,self.a,self.timed())
  with self.assertRaises(HTTPException):save_log(self.db,self.a,self.timed(title="Overlap",startTime="16:00",endTime="18:00",breakMinutes=0))
  save_log(self.db,self.a,self.timed(title="Back",startTime="17:00",endTime="18:00",breakMinutes=0))
  save_log(self.db,self.a,self.timed(title="Cancelled",startTime="10:00",endTime="11:00",breakMinutes=0,status="cancelled"))
  save_log(self.db,self.a,self.manual(title="Manual overlap"));save_log(self.db,self.a,self.manual(title="Manual overlap two"))
  result=list_logs(self.db,self.a," implementation ",self.p.id,"completed","timed",True,"all",None,None,1,10);self.assertEqual(result.total,1)
  with self.assertRaises(HTTPException):list_logs(self.db,self.a,None,None,None,None,None,"all",date(2026,7,22),date(2026,7,20),1,10)
  metrics=dashboard(self.db,self.a);self.assertGreater(metrics.billable_minutes,0);self.assertGreater(metrics.non_billable_minutes,0)
  switched=save_log(self.db,self.a,self.manual(title="Switched",workDate="2026-07-22"),first.id);self.assertIsNone(switched.start_time);self.assertEqual(switched.break_minutes,0)

if __name__=="__main__":unittest.main()
