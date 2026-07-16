from datetime import date
from fastapi import APIRouter,Query,Response
from app.modules.work_log_tracker import service as s
from app.modules.work_log_tracker.dependencies import CurrentUser,DB
from app.modules.work_log_tracker.schemas import *
router=APIRouter()
@router.get("/dashboard",response_model=Dashboard,operation_id="getWorkLogDashboard")
def dash(db:DB,current_user:CurrentUser):return s.dashboard(db,current_user)
@router.get("/projects",response_model=list[ProjectResponse],operation_id="listWorkProjects")
def projects(db:DB,current_user:CurrentUser):return s.list_projects(db,current_user)
@router.post("/projects",response_model=ProjectResponse,status_code=201,operation_id="createWorkProject")
def create_project(payload:ProjectCreate,db:DB,current_user:CurrentUser):return s.save_project(db,current_user,payload)
@router.put("/projects/{project_id}",response_model=ProjectResponse,operation_id="updateWorkProject")
def update_project(project_id:str,payload:ProjectUpdate,db:DB,current_user:CurrentUser):return s.save_project(db,current_user,payload,project_id)
@router.delete("/projects/{project_id}",status_code=204,operation_id="deleteWorkProject")
def delete_project(project_id:str,db:DB,current_user:CurrentUser):s.delete_project(db,current_user,project_id);return Response(status_code=204)
@router.get("/logs",response_model=LogList,operation_id="listWorkLogs")
def logs(db:DB,current_user:CurrentUser,q:str|None=None,project_id:str|None=Query(None,alias="projectId"),status:Status|None=None,entry_mode:Mode|None=Query(None,alias="entryMode"),billable:bool|None=None,period:Period="all",date_from:date|None=Query(None,alias="dateFrom"),date_to:date|None=Query(None,alias="dateTo"),page:int=Query(1,ge=1),page_size:int=Query(20,alias="pageSize",ge=1,le=100)):return s.list_logs(db,current_user,q,project_id,status,entry_mode,billable,period,date_from,date_to,page,page_size)
@router.post("/logs",response_model=LogResponse,status_code=201,operation_id="createWorkLog")
def create_log(payload:LogCreate,db:DB,current_user:CurrentUser):return s.save_log(db,current_user,payload)
@router.get("/logs/{log_id}",response_model=LogResponse,operation_id="getWorkLog")
def get_log(log_id:str,db:DB,current_user:CurrentUser):return s.get_log(db,current_user,log_id)
@router.put("/logs/{log_id}",response_model=LogResponse,operation_id="updateWorkLog")
def update_log(log_id:str,payload:LogUpdate,db:DB,current_user:CurrentUser):return s.save_log(db,current_user,payload,log_id)
@router.delete("/logs/{log_id}",status_code=204,operation_id="deleteWorkLog")
def delete_log(log_id:str,db:DB,current_user:CurrentUser):s.delete_log(db,current_user,log_id);return Response(status_code=204)
