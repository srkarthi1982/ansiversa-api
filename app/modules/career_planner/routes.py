from typing import Annotated

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.auth.service import get_current_user
from app.modules.career_planner.db import get_career_planner_db
from app.modules.career_planner.schemas import (
    CareerDashboardResponse,
    CareerGoalCreateRequest,
    CareerGoalDetailResponse,
    CareerGoalUpdateRequest,
    CareerMilestoneCreateRequest,
    CareerMilestoneDetailResponse,
    CareerMilestoneUpdateRequest,
    CareerReviewHistoryCreateRequest,
    CareerReviewHistoryDetailResponse,
    CareerReviewHistorySummaryResponse,
    CareerReviewHistoryUpdateRequest,
    CareerRoadmapCreateRequest,
    CareerRoadmapDetailResponse,
    CareerRoadmapUpdateRequest,
)
from app.modules.career_planner.service import (
    create_goal,
    create_milestone,
    create_review_history_item,
    create_roadmap,
    delete_goal,
    delete_milestone,
    delete_review_history_item,
    delete_roadmap,
    get_dashboard,
    get_goal,
    get_milestone,
    get_review_history_item,
    get_roadmap,
    update_goal,
    update_milestone,
    update_review_history_item,
    update_roadmap,
)

router = APIRouter()


@router.get("/dashboard", response_model=CareerDashboardResponse)
def get_career_dashboard(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_career_planner_db)],
) -> CareerDashboardResponse:
    return get_dashboard(db, current_user)


@router.post(
    "/goals",
    response_model=CareerGoalDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_career_goal(
    payload: CareerGoalCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_career_planner_db)],
) -> CareerGoalDetailResponse:
    return create_goal(db, current_user, payload)


@router.get("/goals/{goal_id}", response_model=CareerGoalDetailResponse)
def get_career_goal(
    goal_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_career_planner_db)],
) -> CareerGoalDetailResponse:
    return get_goal(db, current_user, goal_id)


@router.put("/goals/{goal_id}", response_model=CareerGoalDetailResponse)
def update_career_goal(
    goal_id: Annotated[int, Path(gt=0)],
    payload: CareerGoalUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_career_planner_db)],
) -> CareerGoalDetailResponse:
    return update_goal(db, current_user, goal_id, payload)


@router.delete("/goals/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_career_goal(
    goal_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_career_planner_db)],
) -> None:
    delete_goal(db, current_user, goal_id)


@router.post(
    "/roadmaps",
    response_model=CareerRoadmapDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_career_roadmap(
    payload: CareerRoadmapCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_career_planner_db)],
) -> CareerRoadmapDetailResponse:
    return create_roadmap(db, current_user, payload)


@router.get("/roadmaps/{roadmap_id}", response_model=CareerRoadmapDetailResponse)
def get_career_roadmap(
    roadmap_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_career_planner_db)],
) -> CareerRoadmapDetailResponse:
    return get_roadmap(db, current_user, roadmap_id)


@router.put("/roadmaps/{roadmap_id}", response_model=CareerRoadmapDetailResponse)
def update_career_roadmap(
    roadmap_id: Annotated[int, Path(gt=0)],
    payload: CareerRoadmapUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_career_planner_db)],
) -> CareerRoadmapDetailResponse:
    return update_roadmap(db, current_user, roadmap_id, payload)


@router.delete("/roadmaps/{roadmap_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_career_roadmap(
    roadmap_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_career_planner_db)],
) -> None:
    delete_roadmap(db, current_user, roadmap_id)


@router.post(
    "/milestones",
    response_model=CareerMilestoneDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_career_milestone(
    payload: CareerMilestoneCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_career_planner_db)],
) -> CareerMilestoneDetailResponse:
    return create_milestone(db, current_user, payload)


@router.get("/milestones/{milestone_id}", response_model=CareerMilestoneDetailResponse)
def get_career_milestone(
    milestone_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_career_planner_db)],
) -> CareerMilestoneDetailResponse:
    return get_milestone(db, current_user, milestone_id)


@router.put("/milestones/{milestone_id}", response_model=CareerMilestoneDetailResponse)
def update_career_milestone(
    milestone_id: Annotated[int, Path(gt=0)],
    payload: CareerMilestoneUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_career_planner_db)],
) -> CareerMilestoneDetailResponse:
    return update_milestone(db, current_user, milestone_id, payload)


@router.delete("/milestones/{milestone_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_career_milestone(
    milestone_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_career_planner_db)],
) -> None:
    delete_milestone(db, current_user, milestone_id)


@router.post(
    "/review",
    response_model=CareerReviewHistorySummaryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_career_review_history_item(
    payload: CareerReviewHistoryCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_career_planner_db)],
) -> CareerReviewHistorySummaryResponse:
    return create_review_history_item(db, current_user, payload)


@router.get("/review/{review_id}", response_model=CareerReviewHistoryDetailResponse)
def get_career_review_history_item(
    review_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_career_planner_db)],
) -> CareerReviewHistoryDetailResponse:
    return get_review_history_item(db, current_user, review_id)


@router.put("/review/{review_id}", response_model=CareerReviewHistoryDetailResponse)
def update_career_review_history_item(
    review_id: Annotated[int, Path(gt=0)],
    payload: CareerReviewHistoryUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_career_planner_db)],
) -> CareerReviewHistoryDetailResponse:
    return update_review_history_item(db, current_user, review_id, payload)


@router.delete("/review/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_career_review_history_item(
    review_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_career_planner_db)],
) -> None:
    delete_review_history_item(db, current_user, review_id)
