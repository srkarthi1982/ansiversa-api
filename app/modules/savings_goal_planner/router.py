from datetime import date
from fastapi import APIRouter,Query,Response
from app.modules.savings_goal_planner import service as s
from app.modules.savings_goal_planner.dependencies import CurrentUser,DB
from app.modules.savings_goal_planner.schemas import *
router=APIRouter()
@router.get("/dashboard",response_model=Dashboard,operation_id="getSavingsGoalPlannerDashboard")
def dashboard(db:DB,current_user:CurrentUser):return s.dashboard(db,current_user)
@router.get("/goals",response_model=GoalList,operation_id="listSavingsGoals")
def goals(db:DB,current_user:CurrentUser,q:str|None=None,status:Status|None=None,category:Category|None=None,priority:Priority|None=None,currency:str|None=None,period:Period="all",date_from:date|None=Query(None,alias="dateFrom"),date_to:date|None=Query(None,alias="dateTo"),page:int=Query(1,ge=1),page_size:int=Query(12,alias="pageSize",ge=1,le=100)):return s.list_goals(db,current_user,q,status,category,priority,currency,period,date_from,date_to,page,page_size)
@router.post("/goals",response_model=GoalDetail,status_code=201,operation_id="createSavingsGoal")
def create(payload:GoalCreate,db:DB,current_user:CurrentUser):return s.save_goal(db,current_user,payload)
@router.get("/goals/{goal_id}",response_model=GoalDetail,operation_id="getSavingsGoal")
def get(goal_id:str,db:DB,current_user:CurrentUser):return s.get_goal(db,current_user,goal_id)
@router.put("/goals/{goal_id}",response_model=GoalDetail,operation_id="updateSavingsGoal")
def update(goal_id:str,payload:GoalUpdate,db:DB,current_user:CurrentUser):return s.save_goal(db,current_user,payload,goal_id)
@router.delete("/goals/{goal_id}",status_code=204,operation_id="deleteSavingsGoal")
def delete(goal_id:str,db:DB,current_user:CurrentUser):s.delete_goal(db,current_user,goal_id);return Response(status_code=204)
@router.get("/goals/{goal_id}/transactions",response_model=list[TransactionResponse],operation_id="listSavingsTransactions")
def transactions(goal_id:str,db:DB,current_user:CurrentUser):return s.get_goal(db,current_user,goal_id).transactions
@router.post("/goals/{goal_id}/transactions",response_model=GoalDetail,status_code=201,operation_id="createSavingsTransaction")
def create_transaction(goal_id:str,payload:TransactionCreate,db:DB,current_user:CurrentUser):return s.save_tx(db,current_user,goal_id,payload)
@router.put("/goals/{goal_id}/transactions/{transaction_id}",response_model=GoalDetail,operation_id="updateSavingsTransaction")
def update_transaction(goal_id:str,transaction_id:str,payload:TransactionUpdate,db:DB,current_user:CurrentUser):return s.save_tx(db,current_user,goal_id,payload,transaction_id)
@router.delete("/goals/{goal_id}/transactions/{transaction_id}",status_code=204,operation_id="deleteSavingsTransaction")
def delete_transaction(goal_id:str,transaction_id:str,db:DB,current_user:CurrentUser):s.delete_tx(db,current_user,goal_id,transaction_id);return Response(status_code=204)
@router.get("/goals/{goal_id}/milestones",response_model=list[MilestoneResponse],operation_id="listSavingsMilestones")
def milestones(goal_id:str,db:DB,current_user:CurrentUser):return s.get_goal(db,current_user,goal_id).milestones
@router.post("/goals/{goal_id}/milestones",response_model=GoalDetail,status_code=201,operation_id="createSavingsMilestone")
def create_milestone(goal_id:str,payload:MilestoneCreate,db:DB,current_user:CurrentUser):return s.save_milestone(db,current_user,goal_id,payload)
@router.put("/goals/{goal_id}/milestones/{milestone_id}",response_model=GoalDetail,operation_id="updateSavingsMilestone")
def update_milestone(goal_id:str,milestone_id:str,payload:MilestoneUpdate,db:DB,current_user:CurrentUser):return s.save_milestone(db,current_user,goal_id,payload,milestone_id)
@router.delete("/goals/{goal_id}/milestones/{milestone_id}",status_code=204,operation_id="deleteSavingsMilestone")
def delete_milestone(goal_id:str,milestone_id:str,db:DB,current_user:CurrentUser):s.delete_milestone(db,current_user,goal_id,milestone_id);return Response(status_code=204)
