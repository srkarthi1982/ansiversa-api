from fastapi import APIRouter, Response, status

from app.modules.wellness_and_goal_planner import service
from app.modules.wellness_and_goal_planner.dependencies import (
    CurrentWellnessAndGoalPlannerUser,
    WellnessAndGoalPlannerDB,
)
from app.modules.wellness_and_goal_planner.schemas import (
    WellnessAreaCreateRequest,
    WellnessAreaDetailResponse,
    WellnessAreaSummaryResponse,
    WellnessAreaUpdateRequest,
    WellnessDashboardResponse,
    WellnessGoalCreateRequest,
    WellnessGoalDetailResponse,
    WellnessGoalSummaryResponse,
    WellnessGoalUpdateRequest,
    WellnessReflectionCreateRequest,
    WellnessReflectionDetailResponse,
    WellnessReflectionSummaryResponse,
    WellnessReflectionUpdateRequest,
)

router = APIRouter()


@router.get("/dashboard", response_model=WellnessDashboardResponse)
def get_dashboard(db: WellnessAndGoalPlannerDB, current_user: CurrentWellnessAndGoalPlannerUser):
    return service.get_dashboard(db, current_user)


@router.get("/areas", response_model=list[WellnessAreaSummaryResponse])
def list_areas(db: WellnessAndGoalPlannerDB, current_user: CurrentWellnessAndGoalPlannerUser):
    return service.list_areas(db, current_user)


@router.post("/areas", response_model=WellnessAreaDetailResponse, status_code=status.HTTP_201_CREATED)
def create_area(
    payload: WellnessAreaCreateRequest,
    db: WellnessAndGoalPlannerDB,
    current_user: CurrentWellnessAndGoalPlannerUser,
):
    return service.create_area(db, current_user, payload)


@router.get("/areas/{area_id}", response_model=WellnessAreaDetailResponse)
def get_area(area_id: str, db: WellnessAndGoalPlannerDB, current_user: CurrentWellnessAndGoalPlannerUser):
    return service.get_area(db, current_user, area_id)


@router.put("/areas/{area_id}", response_model=WellnessAreaDetailResponse)
def update_area(
    area_id: str,
    payload: WellnessAreaUpdateRequest,
    db: WellnessAndGoalPlannerDB,
    current_user: CurrentWellnessAndGoalPlannerUser,
):
    return service.update_area(db, current_user, area_id, payload)


@router.delete("/areas/{area_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_area(area_id: str, db: WellnessAndGoalPlannerDB, current_user: CurrentWellnessAndGoalPlannerUser):
    service.delete_area(db, current_user, area_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/goals", response_model=list[WellnessGoalSummaryResponse])
def list_goals(db: WellnessAndGoalPlannerDB, current_user: CurrentWellnessAndGoalPlannerUser):
    return service.list_goals(db, current_user)


@router.post("/goals", response_model=WellnessGoalDetailResponse, status_code=status.HTTP_201_CREATED)
def create_goal(
    payload: WellnessGoalCreateRequest,
    db: WellnessAndGoalPlannerDB,
    current_user: CurrentWellnessAndGoalPlannerUser,
):
    return service.create_goal(db, current_user, payload)


@router.get("/goals/{goal_id}", response_model=WellnessGoalDetailResponse)
def get_goal(goal_id: str, db: WellnessAndGoalPlannerDB, current_user: CurrentWellnessAndGoalPlannerUser):
    return service.get_goal(db, current_user, goal_id)


@router.put("/goals/{goal_id}", response_model=WellnessGoalDetailResponse)
def update_goal(
    goal_id: str,
    payload: WellnessGoalUpdateRequest,
    db: WellnessAndGoalPlannerDB,
    current_user: CurrentWellnessAndGoalPlannerUser,
):
    return service.update_goal(db, current_user, goal_id, payload)


@router.delete("/goals/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_goal(goal_id: str, db: WellnessAndGoalPlannerDB, current_user: CurrentWellnessAndGoalPlannerUser):
    service.delete_goal(db, current_user, goal_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/reflections", response_model=list[WellnessReflectionSummaryResponse])
def list_reflections(db: WellnessAndGoalPlannerDB, current_user: CurrentWellnessAndGoalPlannerUser):
    return service.list_reflections(db, current_user)


@router.post("/reflections", response_model=WellnessReflectionDetailResponse, status_code=status.HTTP_201_CREATED)
def create_reflection(
    payload: WellnessReflectionCreateRequest,
    db: WellnessAndGoalPlannerDB,
    current_user: CurrentWellnessAndGoalPlannerUser,
):
    return service.create_reflection(db, current_user, payload)


@router.get("/reflections/{reflection_id}", response_model=WellnessReflectionDetailResponse)
def get_reflection(
    reflection_id: str,
    db: WellnessAndGoalPlannerDB,
    current_user: CurrentWellnessAndGoalPlannerUser,
):
    return service.get_reflection(db, current_user, reflection_id)


@router.put("/reflections/{reflection_id}", response_model=WellnessReflectionDetailResponse)
def update_reflection(
    reflection_id: str,
    payload: WellnessReflectionUpdateRequest,
    db: WellnessAndGoalPlannerDB,
    current_user: CurrentWellnessAndGoalPlannerUser,
):
    return service.update_reflection(db, current_user, reflection_id, payload)


@router.delete("/reflections/{reflection_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reflection(
    reflection_id: str,
    db: WellnessAndGoalPlannerDB,
    current_user: CurrentWellnessAndGoalPlannerUser,
):
    service.delete_reflection(db, current_user, reflection_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
