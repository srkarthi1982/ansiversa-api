import unittest
from types import SimpleNamespace
from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.modules.shift_planner.db import ShiftPlannerBase
from app.modules.shift_planner.schemas import MemberCreate,ShiftCreate,TypeCreate
from app.modules.shift_planner.service import dashboard,delete_member,delete_type,get_shift,list_shifts,save_member,save_shift,save_type

class ShiftPlannerTests(unittest.TestCase):
    def setUp(self):
        e=create_engine("sqlite://",connect_args={"check_same_thread":False},poolclass=StaticPool);ShiftPlannerBase.metadata.create_all(e);self.db=sessionmaker(bind=e)();self.a=SimpleNamespace(id="a");self.b=SimpleNamespace(id="b")
        self.t=save_type(self.db,self.a,TypeCreate(name="Morning",defaultStartTime="09:00",defaultEndTime="17:00",defaultBreakMinutes=30))
        self.m=save_member(self.db,self.a,MemberCreate(name="Alex",email="alex@example.com"))
    def tearDown(self):self.db.close()
    def payload(self,**x):
        d={"shiftTypeId":self.t.id,"memberId":self.m.id,"title":"Counter","shiftDate":"2026-07-20","startTime":"09:00","endTime":"17:00","breakMinutes":30,"status":"scheduled"};d.update(x);return ShiftCreate(**d)
    def test_duration_overnight_break_and_validation(self):
        self.assertEqual(save_shift(self.db,self.a,self.payload()).duration_minutes,450)
        self.assertEqual(save_shift(self.db,self.a,self.payload(memberId=None,title="Night",startTime="22:00",endTime="06:00",breakMinutes=60)).duration_minutes,420)
        with self.assertRaises(HTTPException):save_shift(self.db,self.a,self.payload(memberId=None,title="Bad",breakMinutes=480))
        with self.assertRaises(ValidationError):MemberCreate(name="Bad",email="invalid")
        with self.assertRaises(ValidationError):self.payload(breakMinutes=-1)
    def test_overlap_back_to_back_cancelled_and_other_member(self):
        first=save_shift(self.db,self.a,self.payload())
        with self.assertRaises(HTTPException) as conflict:save_shift(self.db,self.a,self.payload(title="Overlap",startTime="16:00",endTime="18:00"))
        self.assertEqual(conflict.exception.status_code,409)
        save_shift(self.db,self.a,self.payload(title="Back",startTime="17:00",endTime="18:00",breakMinutes=0))
        save_shift(self.db,self.a,self.payload(title="Cancelled",startTime="10:00",endTime="11:00",breakMinutes=0,status="cancelled"))
        other=save_member(self.db,self.a,MemberCreate(name="Sam"));save_shift(self.db,self.a,self.payload(title="Other",memberId=other.id))
        with self.assertRaises(HTTPException):get_shift(self.db,self.b,first.id)
    def test_ownership_inactive_history_filters_and_metrics(self):
        foreign=save_type(self.db,self.b,TypeCreate(name="Foreign",defaultStartTime="09:00",defaultEndTime="17:00"))
        with self.assertRaises(HTTPException):save_shift(self.db,self.a,self.payload(shiftTypeId=foreign.id))
        completed=save_shift(self.db,self.a,self.payload(status="completed"));self.assertEqual(dashboard(self.db,self.a).completed_hours,7.5)
        result=list_shifts(self.db,self.a," Counter ",self.t.id,None,"completed","all",None,None,1,10);self.assertEqual(result.total,1)
        with self.assertRaises(HTTPException):delete_type(self.db,self.a,self.t.id)
        with self.assertRaises(HTTPException):delete_member(self.db,self.a,self.m.id)

if __name__=="__main__":unittest.main()
