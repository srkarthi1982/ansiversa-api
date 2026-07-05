from fastapi import APIRouter, Response, status

from app.modules.goal_tracker import service
from app.modules.goal_tracker.dependencies import CurrentGoalTrackerUser, GoalTrackerDB
from app.modules.goal_tracker.schemas import (
    CheckInCreateRequest,
    CheckInDetailResponse,
    CheckInSummaryResponse,
    CheckInUpdateRequest,
    GoalCreateRequest,
    GoalDetailResponse,
    GoalDuplicateRequest,
    GoalSummaryResponse,
    GoalTrackerDashboardResponse,
    GoalUpdateRequest,
    MilestoneCreateRequest,
    MilestoneDetailResponse,
    MilestoneSummaryResponse,
    MilestoneUpdateRequest,
)

router = APIRouter()


@router.get("/dashboard", response_model=GoalTrackerDashboardResponse)
def get_dashboard(db: GoalTrackerDB, current_user: CurrentGoalTrackerUser):
    return service.get_dashboard(db, current_user)


@router.get("/goals", response_model=list[GoalSummaryResponse])
def list_goals(db: GoalTrackerDB, current_user: CurrentGoalTrackerUser):
    return service.list_goals(db, current_user)


@router.post("/goals", response_model=GoalDetailResponse, status_code=status.HTTP_201_CREATED)
def create_goal(payload: GoalCreateRequest, db: GoalTrackerDB, current_user: CurrentGoalTrackerUser):
    return service.create_goal(db, current_user, payload)


@router.get("/goals/{goal_id}", response_model=GoalDetailResponse)
def get_goal(goal_id: str, db: GoalTrackerDB, current_user: CurrentGoalTrackerUser):
    return service.get_goal(db, current_user, goal_id)


@router.put("/goals/{goal_id}", response_model=GoalDetailResponse)
def update_goal(
    goal_id: str,
    payload: GoalUpdateRequest,
    db: GoalTrackerDB,
    current_user: CurrentGoalTrackerUser,
):
    return service.update_goal(db, current_user, goal_id, payload)


@router.post("/goals/{goal_id}/duplicate", response_model=GoalDetailResponse, status_code=status.HTTP_201_CREATED)
def duplicate_goal(
    goal_id: str,
    payload: GoalDuplicateRequest,
    db: GoalTrackerDB,
    current_user: CurrentGoalTrackerUser,
):
    return service.duplicate_goal(db, current_user, goal_id, payload)


@router.delete("/goals/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_goal(goal_id: str, db: GoalTrackerDB, current_user: CurrentGoalTrackerUser):
    service.delete_goal(db, current_user, goal_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/milestones", response_model=list[MilestoneSummaryResponse])
def list_milestones(db: GoalTrackerDB, current_user: CurrentGoalTrackerUser):
    return service.list_milestones(db, current_user)


@router.post("/milestones", response_model=MilestoneDetailResponse, status_code=status.HTTP_201_CREATED)
def create_milestone(payload: MilestoneCreateRequest, db: GoalTrackerDB, current_user: CurrentGoalTrackerUser):
    return service.create_milestone(db, current_user, payload)


@router.get("/milestones/{milestone_id}", response_model=MilestoneDetailResponse)
def get_milestone(milestone_id: str, db: GoalTrackerDB, current_user: CurrentGoalTrackerUser):
    return service.get_milestone(db, current_user, milestone_id)


@router.put("/milestones/{milestone_id}", response_model=MilestoneDetailResponse)
def update_milestone(
    milestone_id: str,
    payload: MilestoneUpdateRequest,
    db: GoalTrackerDB,
    current_user: CurrentGoalTrackerUser,
):
    return service.update_milestone(db, current_user, milestone_id, payload)


@router.delete("/milestones/{milestone_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_milestone(milestone_id: str, db: GoalTrackerDB, current_user: CurrentGoalTrackerUser):
    service.delete_milestone(db, current_user, milestone_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/check-ins", response_model=list[CheckInSummaryResponse])
def list_check_ins(db: GoalTrackerDB, current_user: CurrentGoalTrackerUser):
    return service.list_check_ins(db, current_user)


@router.post("/check-ins", response_model=CheckInDetailResponse, status_code=status.HTTP_201_CREATED)
def create_check_in(payload: CheckInCreateRequest, db: GoalTrackerDB, current_user: CurrentGoalTrackerUser):
    return service.create_check_in(db, current_user, payload)


@router.get("/check-ins/{check_in_id}", response_model=CheckInDetailResponse)
def get_check_in(check_in_id: str, db: GoalTrackerDB, current_user: CurrentGoalTrackerUser):
    return service.get_check_in(db, current_user, check_in_id)


@router.put("/check-ins/{check_in_id}", response_model=CheckInDetailResponse)
def update_check_in(
    check_in_id: str,
    payload: CheckInUpdateRequest,
    db: GoalTrackerDB,
    current_user: CurrentGoalTrackerUser,
):
    return service.update_check_in(db, current_user, check_in_id, payload)


@router.delete("/check-ins/{check_in_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_check_in(check_in_id: str, db: GoalTrackerDB, current_user: CurrentGoalTrackerUser):
    service.delete_check_in(db, current_user, check_in_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
