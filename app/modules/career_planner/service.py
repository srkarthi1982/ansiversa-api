from fastapi import HTTPException, status
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.career_planner.models import (
    CareerGoal,
    CareerMilestone,
    CareerReviewHistoryItem,
    CareerRoadmap,
)
from app.modules.career_planner.schemas import (
    CareerDashboardResponse,
    CareerGoalCreateRequest,
    CareerGoalDetailResponse,
    CareerGoalSummaryResponse,
    CareerGoalUpdateRequest,
    CareerMilestoneCreateRequest,
    CareerMilestoneDetailResponse,
    CareerMilestoneSummaryResponse,
    CareerMilestoneUpdateRequest,
    CareerReviewHistoryCreateRequest,
    CareerReviewHistorySummaryResponse,
    CareerRoadmapCreateRequest,
    CareerRoadmapDetailResponse,
    CareerRoadmapSummaryResponse,
    CareerRoadmapUpdateRequest,
)

PREVIEW_LENGTH = 220


def _preview(value: str | None) -> str | None:
    if not value:
        return None
    if len(value) <= PREVIEW_LENGTH:
        return value
    return f"{value[:PREVIEW_LENGTH].rstrip()}..."


def _not_found(detail: str) -> None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def _get_owned_goal(db: Session, user: User, goal_id: int) -> CareerGoal:
    goal = db.get(CareerGoal, goal_id)
    if not goal or goal.owner_id != user.id:
        _not_found("Career goal was not found.")
    return goal


def _get_owned_roadmap(db: Session, user: User, roadmap_id: int) -> CareerRoadmap:
    roadmap = db.get(CareerRoadmap, roadmap_id)
    if not roadmap or roadmap.owner_id != user.id:
        _not_found("Career roadmap was not found.")
    return roadmap


def _get_owned_milestone(db: Session, user: User, milestone_id: int) -> CareerMilestone:
    milestone = db.get(CareerMilestone, milestone_id)
    if not milestone or milestone.owner_id != user.id:
        _not_found("Career milestone was not found.")
    return milestone


def _get_owned_review_history_item(
    db: Session,
    user: User,
    review_id: int,
) -> CareerReviewHistoryItem:
    review_item = db.get(CareerReviewHistoryItem, review_id)
    if not review_item or review_item.owner_id != user.id:
        _not_found("Career review history item was not found.")
    return review_item


def _optional_owned_goal(db: Session, user: User, goal_id: int | None) -> CareerGoal | None:
    if goal_id is None:
        return None
    return _get_owned_goal(db, user, goal_id)


def _count_roadmaps(db: Session, goal_id: int) -> int:
    return int(
        db.execute(
            select(func.count()).select_from(CareerRoadmap).where(
                CareerRoadmap.goal_id == goal_id
            )
        ).scalar_one()
    )


def _count_milestones(db: Session, roadmap_id: int) -> int:
    return int(
        db.execute(
            select(func.count()).select_from(CareerMilestone).where(
                CareerMilestone.roadmap_id == roadmap_id
            )
        ).scalar_one()
    )


def _goal_summary_response(db: Session, goal: CareerGoal) -> CareerGoalSummaryResponse:
    return CareerGoalSummaryResponse(
        id=goal.id,
        title=goal.title,
        target_role=goal.target_role,
        time_horizon=goal.time_horizon,
        status=goal.status,
        roadmap_count=_count_roadmaps(db, goal.id),
        created_at=goal.created_at,
        updated_at=goal.updated_at,
    )


def _goal_detail_response(db: Session, goal: CareerGoal) -> CareerGoalDetailResponse:
    summary = _goal_summary_response(db, goal)
    return CareerGoalDetailResponse(**summary.model_dump(), notes=goal.notes)


def _roadmap_summary_response(
    db: Session,
    roadmap: CareerRoadmap,
    goal_title: str,
) -> CareerRoadmapSummaryResponse:
    return CareerRoadmapSummaryResponse(
        id=roadmap.id,
        goal_id=roadmap.goal_id,
        goal_title=goal_title,
        title=roadmap.title,
        focus_area=roadmap.focus_area,
        status=roadmap.status,
        milestone_count=_count_milestones(db, roadmap.id),
        sort_order=roadmap.sort_order,
        created_at=roadmap.created_at,
        updated_at=roadmap.updated_at,
    )


def _roadmap_detail_response(
    db: Session,
    roadmap: CareerRoadmap,
    goal_title: str,
) -> CareerRoadmapDetailResponse:
    summary = _roadmap_summary_response(db, roadmap, goal_title)
    return CareerRoadmapDetailResponse(**summary.model_dump(), summary=roadmap.summary)


def _milestone_summary_response(
    milestone: CareerMilestone,
    roadmap_title: str,
) -> CareerMilestoneSummaryResponse:
    return CareerMilestoneSummaryResponse(
        id=milestone.id,
        roadmap_id=milestone.roadmap_id,
        roadmap_title=roadmap_title,
        title=milestone.title,
        due_date=milestone.due_date,
        status=milestone.status,
        success_metric=milestone.success_metric,
        sort_order=milestone.sort_order,
        created_at=milestone.created_at,
        updated_at=milestone.updated_at,
    )


def _milestone_detail_response(
    milestone: CareerMilestone,
    roadmap_title: str,
) -> CareerMilestoneDetailResponse:
    summary = _milestone_summary_response(milestone, roadmap_title)
    return CareerMilestoneDetailResponse(**summary.model_dump(), notes=milestone.notes)


def _review_history_summary_response(
    review_item: CareerReviewHistoryItem,
    goal_title: str | None,
) -> CareerReviewHistorySummaryResponse:
    return CareerReviewHistorySummaryResponse(
        id=review_item.id,
        goal_id=review_item.goal_id,
        goal_title=goal_title,
        title=review_item.title,
        action_type=review_item.action_type,
        notes_preview=_preview(review_item.notes),
        created_at=review_item.created_at,
        updated_at=review_item.updated_at,
    )


def list_goals(db: Session, user: User) -> list[CareerGoalSummaryResponse]:
    goals = list(
        db.execute(
            select(CareerGoal)
            .where(CareerGoal.owner_id == user.id)
            .order_by(CareerGoal.updated_at.desc(), CareerGoal.title.asc())
        )
        .scalars()
        .all()
    )
    return [_goal_summary_response(db, goal) for goal in goals]


def create_goal(
    db: Session,
    user: User,
    payload: CareerGoalCreateRequest,
) -> CareerGoalDetailResponse:
    goal = CareerGoal(
        owner_id=user.id,
        title=payload.title,
        target_role=payload.target_role,
        time_horizon=payload.time_horizon,
        status=payload.status,
        notes=payload.notes,
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return _goal_detail_response(db, goal)


def get_goal(db: Session, user: User, goal_id: int) -> CareerGoalDetailResponse:
    return _goal_detail_response(db, _get_owned_goal(db, user, goal_id))


def update_goal(
    db: Session,
    user: User,
    goal_id: int,
    payload: CareerGoalUpdateRequest,
) -> CareerGoalDetailResponse:
    goal = _get_owned_goal(db, user, goal_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(goal, field, value)
    db.commit()
    db.refresh(goal)
    return _goal_detail_response(db, goal)


def delete_goal(db: Session, user: User, goal_id: int) -> None:
    goal = _get_owned_goal(db, user, goal_id)
    roadmap_ids = list(
        db.execute(select(CareerRoadmap.id).where(CareerRoadmap.goal_id == goal.id)).scalars().all()
    )
    if roadmap_ids:
        db.execute(delete(CareerMilestone).where(CareerMilestone.roadmap_id.in_(roadmap_ids)))
    db.execute(delete(CareerRoadmap).where(CareerRoadmap.goal_id == goal.id))
    db.execute(delete(CareerReviewHistoryItem).where(CareerReviewHistoryItem.goal_id == goal.id))
    db.delete(goal)
    db.commit()


def list_roadmaps(db: Session, user: User) -> list[CareerRoadmapSummaryResponse]:
    rows = db.execute(
        select(CareerRoadmap, CareerGoal.title)
        .join(CareerGoal, CareerGoal.id == CareerRoadmap.goal_id)
        .where(CareerRoadmap.owner_id == user.id)
        .order_by(
            CareerRoadmap.goal_id.asc(),
            CareerRoadmap.sort_order.asc(),
            CareerRoadmap.updated_at.desc(),
        )
    ).all()
    return [_roadmap_summary_response(db, roadmap, goal_title) for roadmap, goal_title in rows]


def create_roadmap(
    db: Session,
    user: User,
    payload: CareerRoadmapCreateRequest,
) -> CareerRoadmapDetailResponse:
    goal = _get_owned_goal(db, user, payload.goal_id)
    roadmap = CareerRoadmap(
        goal_id=goal.id,
        owner_id=user.id,
        title=payload.title,
        focus_area=payload.focus_area,
        status=payload.status,
        summary=payload.summary,
        sort_order=payload.sort_order,
    )
    db.add(roadmap)
    db.commit()
    db.refresh(roadmap)
    return _roadmap_detail_response(db, roadmap, goal.title)


def get_roadmap(db: Session, user: User, roadmap_id: int) -> CareerRoadmapDetailResponse:
    roadmap = _get_owned_roadmap(db, user, roadmap_id)
    goal = _get_owned_goal(db, user, roadmap.goal_id)
    return _roadmap_detail_response(db, roadmap, goal.title)


def update_roadmap(
    db: Session,
    user: User,
    roadmap_id: int,
    payload: CareerRoadmapUpdateRequest,
) -> CareerRoadmapDetailResponse:
    roadmap = _get_owned_roadmap(db, user, roadmap_id)
    goal = _get_owned_goal(db, user, roadmap.goal_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(roadmap, field, value)
    db.commit()
    db.refresh(roadmap)
    return _roadmap_detail_response(db, roadmap, goal.title)


def delete_roadmap(db: Session, user: User, roadmap_id: int) -> None:
    roadmap = _get_owned_roadmap(db, user, roadmap_id)
    db.execute(delete(CareerMilestone).where(CareerMilestone.roadmap_id == roadmap.id))
    db.delete(roadmap)
    db.commit()


def list_milestones(db: Session, user: User) -> list[CareerMilestoneSummaryResponse]:
    rows = db.execute(
        select(CareerMilestone, CareerRoadmap.title)
        .join(CareerRoadmap, CareerRoadmap.id == CareerMilestone.roadmap_id)
        .where(CareerMilestone.owner_id == user.id)
        .order_by(
            CareerMilestone.roadmap_id.asc(),
            CareerMilestone.sort_order.asc(),
            CareerMilestone.updated_at.desc(),
        )
    ).all()
    return [_milestone_summary_response(milestone, roadmap_title) for milestone, roadmap_title in rows]


def create_milestone(
    db: Session,
    user: User,
    payload: CareerMilestoneCreateRequest,
) -> CareerMilestoneDetailResponse:
    roadmap = _get_owned_roadmap(db, user, payload.roadmap_id)
    milestone = CareerMilestone(
        roadmap_id=roadmap.id,
        owner_id=user.id,
        title=payload.title,
        due_date=payload.due_date,
        status=payload.status,
        success_metric=payload.success_metric,
        notes=payload.notes,
        sort_order=payload.sort_order,
    )
    db.add(milestone)
    db.commit()
    db.refresh(milestone)
    return _milestone_detail_response(milestone, roadmap.title)


def get_milestone(db: Session, user: User, milestone_id: int) -> CareerMilestoneDetailResponse:
    milestone = _get_owned_milestone(db, user, milestone_id)
    roadmap = _get_owned_roadmap(db, user, milestone.roadmap_id)
    return _milestone_detail_response(milestone, roadmap.title)


def update_milestone(
    db: Session,
    user: User,
    milestone_id: int,
    payload: CareerMilestoneUpdateRequest,
) -> CareerMilestoneDetailResponse:
    milestone = _get_owned_milestone(db, user, milestone_id)
    roadmap = _get_owned_roadmap(db, user, milestone.roadmap_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(milestone, field, value)
    db.commit()
    db.refresh(milestone)
    return _milestone_detail_response(milestone, roadmap.title)


def delete_milestone(db: Session, user: User, milestone_id: int) -> None:
    milestone = _get_owned_milestone(db, user, milestone_id)
    db.delete(milestone)
    db.commit()


def list_review_history(db: Session, user: User) -> list[CareerReviewHistorySummaryResponse]:
    rows = db.execute(
        select(CareerReviewHistoryItem, CareerGoal.title)
        .outerjoin(CareerGoal, CareerGoal.id == CareerReviewHistoryItem.goal_id)
        .where(CareerReviewHistoryItem.owner_id == user.id)
        .order_by(CareerReviewHistoryItem.created_at.desc())
    ).all()
    return [
        _review_history_summary_response(review_item, goal_title)
        for review_item, goal_title in rows
    ]


def create_review_history_item(
    db: Session,
    user: User,
    payload: CareerReviewHistoryCreateRequest,
) -> CareerReviewHistorySummaryResponse:
    goal = _optional_owned_goal(db, user, payload.goal_id)
    review_item = CareerReviewHistoryItem(
        goal_id=goal.id if goal else None,
        owner_id=user.id,
        title=payload.title,
        action_type=payload.action_type,
        notes=payload.notes,
    )
    db.add(review_item)
    db.commit()
    db.refresh(review_item)
    return _review_history_summary_response(review_item, goal.title if goal else None)


def delete_review_history_item(db: Session, user: User, review_id: int) -> None:
    review_item = _get_owned_review_history_item(db, user, review_id)
    db.delete(review_item)
    db.commit()


def get_dashboard(db: Session, user: User) -> CareerDashboardResponse:
    goals = list_goals(db, user)
    roadmaps = list_roadmaps(db, user)
    milestones = list_milestones(db, user)
    review_history = list_review_history(db, user)
    return CareerDashboardResponse(
        goals=goals,
        roadmaps=roadmaps,
        milestones=milestones,
        review_history=review_history,
        active_goal_count=sum(1 for goal in goals if goal.status == "active"),
        in_progress_roadmap_count=sum(1 for roadmap in roadmaps if roadmap.status == "inProgress"),
        done_milestone_count=sum(1 for milestone in milestones if milestone.status == "done"),
    )
