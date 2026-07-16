from datetime import date
from fastapi import APIRouter, Query, Response
from app.modules.leave_planner import service
from app.modules.leave_planner.dependencies import CurrentLeavePlannerUser, LeavePlannerDB
from app.modules.leave_planner.schemas import *
router=APIRouter()
@router.get("/dashboard",response_model=LeavePlannerDashboardResponse,operation_id="getLeavePlannerDashboard")
def dashboard(db:LeavePlannerDB,current_user:CurrentLeavePlannerUser): return service.dashboard(db,current_user)
@router.get("/types",response_model=list[LeavePlannerTypeResponse],operation_id="listLeavePlannerTypes")
def types(db:LeavePlannerDB,current_user:CurrentLeavePlannerUser): return service.list_types(db,current_user)
@router.post("/types",response_model=LeavePlannerTypeResponse,status_code=201,operation_id="createLeavePlannerType")
def create_type(payload:LeavePlannerTypeCreateRequest,db:LeavePlannerDB,current_user:CurrentLeavePlannerUser): return service.create_type(db,current_user,payload)
@router.put("/types/{type_id}",response_model=LeavePlannerTypeResponse,operation_id="updateLeavePlannerType")
def update_type(type_id:str,payload:LeavePlannerTypeUpdateRequest,db:LeavePlannerDB,current_user:CurrentLeavePlannerUser): return service.update_type(db,current_user,type_id,payload)
@router.delete("/types/{type_id}",status_code=204,operation_id="deleteLeavePlannerType")
def delete_type(type_id:str,db:LeavePlannerDB,current_user:CurrentLeavePlannerUser): service.delete_type(db,current_user,type_id); return Response(status_code=204)
@router.get("/leaves",response_model=LeavePlannerEntryListResponse,operation_id="listLeavePlannerEntries")
def leaves(db:LeavePlannerDB,current_user:CurrentLeavePlannerUser,q:str|None=None,leave_type_id:str|None=Query(None,alias="leaveTypeId"),status_filter:LeaveStatus|None=Query(None,alias="status"),period:LeavePeriod="all",date_from:date|None=Query(None,alias="dateFrom"),date_to:date|None=Query(None,alias="dateTo"),page:int=Query(1,ge=1),page_size:int=Query(20,alias="pageSize",ge=1,le=100)): return service.list_entries(db,current_user,q,leave_type_id,status_filter,period,date_from,date_to,page,page_size)
@router.post("/leaves",response_model=LeavePlannerEntryResponse,status_code=201,operation_id="createLeavePlannerEntry")
def create_leave(payload:LeavePlannerEntryCreateRequest,db:LeavePlannerDB,current_user:CurrentLeavePlannerUser): return service.save_entry(db,current_user,payload)
@router.get("/leaves/{leave_id}",response_model=LeavePlannerEntryResponse,operation_id="getLeavePlannerEntry")
def get_leave(leave_id:str,db:LeavePlannerDB,current_user:CurrentLeavePlannerUser): return service.get_entry(db,current_user,leave_id)
@router.put("/leaves/{leave_id}",response_model=LeavePlannerEntryResponse,operation_id="updateLeavePlannerEntry")
def update_leave(leave_id:str,payload:LeavePlannerEntryUpdateRequest,db:LeavePlannerDB,current_user:CurrentLeavePlannerUser): return service.save_entry(db,current_user,payload,leave_id)
@router.delete("/leaves/{leave_id}",status_code=204,operation_id="deleteLeavePlannerEntry")
def delete_leave(leave_id:str,db:LeavePlannerDB,current_user:CurrentLeavePlannerUser): service.delete_entry(db,current_user,leave_id); return Response(status_code=204)
