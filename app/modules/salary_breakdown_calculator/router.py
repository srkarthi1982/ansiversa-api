from datetime import date
from fastapi import APIRouter,Query,Response
from app.modules.salary_breakdown_calculator import service as s
from app.modules.salary_breakdown_calculator.dependencies import CurrentUser,DB
from app.modules.salary_breakdown_calculator.schemas import *
router=APIRouter()
@router.get("/dashboard",response_model=Dashboard,operation_id="getSalaryBreakdownDashboard")
def dashboard(db:DB,current_user:CurrentUser):return s.dashboard(db,current_user)
@router.get("/scenarios",response_model=ScenarioList,operation_id="listSalaryScenarios")
def scenarios(db:DB,current_user:CurrentUser,q:str|None=None,status:Status|None=None,pay_frequency:Frequency|None=Query(None,alias="payFrequency"),currency:str|None=None,created_from:date|None=Query(None,alias="createdFrom"),created_to:date|None=Query(None,alias="createdTo"),updated_from:date|None=Query(None,alias="updatedFrom"),updated_to:date|None=Query(None,alias="updatedTo"),page:int=Query(1,ge=1),page_size:int=Query(12,alias="pageSize",ge=1,le=100)):return s.list_scenarios(db,current_user,q,status,pay_frequency,currency,created_from,created_to,updated_from,updated_to,page,page_size)
@router.post("/scenarios",response_model=ScenarioDetail,status_code=201,operation_id="createSalaryScenario")
def create(payload:ScenarioCreate,db:DB,current_user:CurrentUser):return s.save_scenario(db,current_user,payload)
@router.get("/scenarios/{scenario_id}",response_model=ScenarioDetail,operation_id="getSalaryScenario")
def get(scenario_id:str,db:DB,current_user:CurrentUser):return s.get(db,current_user,scenario_id)
@router.put("/scenarios/{scenario_id}",response_model=ScenarioDetail,operation_id="updateSalaryScenario")
def update(scenario_id:str,payload:ScenarioUpdate,db:DB,current_user:CurrentUser):return s.save_scenario(db,current_user,payload,scenario_id)
@router.delete("/scenarios/{scenario_id}",status_code=204,operation_id="deleteSalaryScenario")
def delete(scenario_id:str,db:DB,current_user:CurrentUser):s.delete(db,current_user,scenario_id);return Response(status_code=204)
@router.get("/scenarios/{scenario_id}/earnings",response_model=list[EarningResponse],operation_id="listSalaryEarnings")
def le(scenario_id:str,db:DB,current_user:CurrentUser):return s.get(db,current_user,scenario_id).earnings
@router.post("/scenarios/{scenario_id}/earnings",response_model=ScenarioDetail,status_code=201,operation_id="createSalaryEarning")
def ce(scenario_id:str,payload:EarningCreate,db:DB,current_user:CurrentUser):return s.save_earning(db,current_user,scenario_id,payload)
@router.put("/scenarios/{scenario_id}/earnings/{earning_id}",response_model=ScenarioDetail,operation_id="updateSalaryEarning")
def ue(scenario_id:str,earning_id:str,payload:EarningUpdate,db:DB,current_user:CurrentUser):return s.save_earning(db,current_user,scenario_id,payload,earning_id)
@router.delete("/scenarios/{scenario_id}/earnings/{earning_id}",status_code=204,operation_id="deleteSalaryEarning")
def de(scenario_id:str,earning_id:str,db:DB,current_user:CurrentUser):s.delete_earning(db,current_user,scenario_id,earning_id);return Response(status_code=204)
@router.get("/scenarios/{scenario_id}/deductions",response_model=list[DeductionResponse],operation_id="listSalaryDeductions")
def ld(scenario_id:str,db:DB,current_user:CurrentUser):return s.get(db,current_user,scenario_id).deductions
@router.post("/scenarios/{scenario_id}/deductions",response_model=ScenarioDetail,status_code=201,operation_id="createSalaryDeduction")
def cd(scenario_id:str,payload:DeductionCreate,db:DB,current_user:CurrentUser):return s.save_deduction(db,current_user,scenario_id,payload)
@router.put("/scenarios/{scenario_id}/deductions/{deduction_id}",response_model=ScenarioDetail,operation_id="updateSalaryDeduction")
def ud(scenario_id:str,deduction_id:str,payload:DeductionUpdate,db:DB,current_user:CurrentUser):return s.save_deduction(db,current_user,scenario_id,payload,deduction_id)
@router.delete("/scenarios/{scenario_id}/deductions/{deduction_id}",status_code=204,operation_id="deleteSalaryDeduction")
def dd(scenario_id:str,deduction_id:str,db:DB,current_user:CurrentUser):s.delete_deduction(db,current_user,scenario_id,deduction_id);return Response(status_code=204)
@router.get("/compare",response_model=Comparison,operation_id="compareSalaryScenarios")
def compare(db:DB,current_user:CurrentUser,left_id:str=Query(alias="leftId"),right_id:str=Query(alias="rightId")):return s.compare(db,current_user,left_id,right_id)
