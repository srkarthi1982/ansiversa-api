from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.goal_tracker import repository
from app.modules.goal_tracker.models import GoalTrackerCheckIn, GoalTrackerGoal, GoalTrackerMilestone
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

PREVIEW_LENGTH = 220


def _preview(value: str | None) -> str | None:
    if not value:
        return None
    if len(value) <= PREVIEW_LENGTH:
        return value
    return f"{value[:PREVIEW_LENGTH].rstrip()}..."


def _not_found(detail: str) -> None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def _get_owned_goal(db: Session, user: User, goal_id: str) -> GoalTrackerGoal:
    goal = repository.get_goal(db, goal_id)
    if not goal or goal.owner_id != user.id:
        _not_found("Goal was not found.")
    return goal


def _get_owned_milestone(db: Session, user: User, milestone_id: str) -> GoalTrackerMilestone:
    milestone = repository.get_milestone(db, milestone_id)
    if not milestone or milestone.owner_id != user.id:
        _not_found("Milestone was not found.")
    return milestone


def _get_owned_check_in(db: Session, user: User, check_in_id: str) -> GoalTrackerCheckIn:
    check_in = repository.get_check_in(db, check_in_id)
    if not check_in or check_in.owner_id != user.id:
        _not_found("Check-in was not found.")
    return check_in


def _goal_summary_response(goal: GoalTrackerGoal) -> GoalSummaryResponse:
    check_ins = sorted(goal.check_ins, key=lambda item: (item.check_in_date, item.created_at), reverse=True)
    completed_milestones = sum(1 for milestone in goal.milestones if milestone.status == "completed")
    return GoalSummaryResponse(
        id=goal.id,
        title=goal.title,
        category=goal.category,
        description_preview=_preview(goal.description),
        target_date=goal.target_date,
        status=goal.status,
        priority=goal.priority,
        progress=goal.progress,
        milestone_count=len(goal.milestones),
        completed_milestone_count=completed_milestones,
        check_in_count=len(goal.check_ins),
        last_check_in_date=check_ins[0].check_in_date if check_ins else None,
        created_at=goal.created_at,
        updated_at=goal.updated_at,
    )


def _milestone_summary_response(milestone: GoalTrackerMilestone) -> MilestoneSummaryResponse:
    return MilestoneSummaryResponse(
        id=milestone.id,
        goal_id=milestone.goal_id,
        goal_title=milestone.goal.title,
        title=milestone.title,
        target_date=milestone.target_date,
        status=milestone.status,
        sort_order=milestone.sort_order,
        created_at=milestone.created_at,
        updated_at=milestone.updated_at,
    )


def _check_in_summary_response(check_in: GoalTrackerCheckIn) -> CheckInSummaryResponse:
    return CheckInSummaryResponse(
        id=check_in.id,
        goal_id=check_in.goal_id,
        goal_title=check_in.goal.title,
        check_in_date=check_in.check_in_date,
        progress=check_in.progress,
        mood=check_in.mood,
        note_preview=_preview(check_in.note),
        created_at=check_in.created_at,
    )


def _goal_detail_response(goal: GoalTrackerGoal) -> GoalDetailResponse:
    summary = _goal_summary_response(goal)
    milestones = sorted(goal.milestones, key=lambda item: (item.sort_order, item.updated_at))
    check_ins = sorted(goal.check_ins, key=lambda item: (item.check_in_date, item.created_at), reverse=True)
    return GoalDetailResponse(
        **summary.model_dump(),
        description=goal.description,
        milestones=[_milestone_summary_response(milestone) for milestone in milestones],
        check_ins=[_check_in_summary_response(check_in) for check_in in check_ins],
    )


def _milestone_detail_response(milestone: GoalTrackerMilestone) -> MilestoneDetailResponse:
    return MilestoneDetailResponse(**_milestone_summary_response(milestone).model_dump())


def _check_in_detail_response(check_in: GoalTrackerCheckIn) -> CheckInDetailResponse:
    return CheckInDetailResponse(**_check_in_summary_response(check_in).model_dump(), note=check_in.note)


def list_goals(db: Session, user: User) -> list[GoalSummaryResponse]:
    return [_goal_summary_response(goal) for goal in repository.list_goals(db, user.id)]


def create_goal(db: Session, user: User, payload: GoalCreateRequest) -> GoalDetailResponse:
    goal = GoalTrackerGoal(owner_id=user.id, **payload.model_dump())
    repository.add(db, goal)
    db.commit()
    db.refresh(goal)
    return _goal_detail_response(goal)


def get_goal(db: Session, user: User, goal_id: str) -> GoalDetailResponse:
    return _goal_detail_response(_get_owned_goal(db, user, goal_id))


def update_goal(db: Session, user: User, goal_id: str, payload: GoalUpdateRequest) -> GoalDetailResponse:
    goal = _get_owned_goal(db, user, goal_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(goal, field, value)
    db.commit()
    db.refresh(goal)
    return _goal_detail_response(goal)


def duplicate_goal(db: Session, user: User, goal_id: str, payload: GoalDuplicateRequest) -> GoalDetailResponse:
    source = _get_owned_goal(db, user, goal_id)
    duplicate = GoalTrackerGoal(
        owner_id=user.id,
        title=payload.title or f"{source.title} Copy",
        category=source.category,
        description=source.description,
        target_date=source.target_date,
        status="active",
        priority=source.priority,
        progress=source.progress,
    )
    repository.add(db, duplicate)
    db.flush()
    for milestone in sorted(source.milestones, key=lambda item: (item.sort_order, item.created_at)):
        repository.add(
            db,
            GoalTrackerMilestone(
                owner_id=user.id,
                goal_id=duplicate.id,
                title=milestone.title,
                target_date=milestone.target_date,
                status=milestone.status,
                sort_order=milestone.sort_order,
            ),
        )
    db.commit()
    db.refresh(duplicate)
    return _goal_detail_response(duplicate)


def delete_goal(db: Session, user: User, goal_id: str) -> None:
    goal = _get_owned_goal(db, user, goal_id)
    repository.delete_record(db, goal)
    db.commit()


def list_milestones(db: Session, user: User) -> list[MilestoneSummaryResponse]:
    return [_milestone_summary_response(milestone) for milestone in repository.list_milestones(db, user.id)]


def create_milestone(db: Session, user: User, payload: MilestoneCreateRequest) -> MilestoneDetailResponse:
    data = payload.model_dump()
    _get_owned_goal(db, user, data["goal_id"])
    milestone = GoalTrackerMilestone(owner_id=user.id, **data)
    repository.add(db, milestone)
    db.commit()
    db.refresh(milestone)
    return _milestone_detail_response(milestone)


def get_milestone(db: Session, user: User, milestone_id: str) -> MilestoneDetailResponse:
    return _milestone_detail_response(_get_owned_milestone(db, user, milestone_id))


def update_milestone(
    db: Session,
    user: User,
    milestone_id: str,
    payload: MilestoneUpdateRequest,
) -> MilestoneDetailResponse:
    milestone = _get_owned_milestone(db, user, milestone_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(milestone, field, value)
    db.commit()
    db.refresh(milestone)
    return _milestone_detail_response(milestone)


def delete_milestone(db: Session, user: User, milestone_id: str) -> None:
    milestone = _get_owned_milestone(db, user, milestone_id)
    repository.delete_record(db, milestone)
    db.commit()


def list_check_ins(db: Session, user: User) -> list[CheckInSummaryResponse]:
    return [_check_in_summary_response(check_in) for check_in in repository.list_check_ins(db, user.id)]


def create_check_in(db: Session, user: User, payload: CheckInCreateRequest) -> CheckInDetailResponse:
    data = payload.model_dump()
    goal = _get_owned_goal(db, user, data["goal_id"])
    check_in = GoalTrackerCheckIn(owner_id=user.id, **data)
    goal.progress = check_in.progress
    if check_in.progress >= 100:
        goal.status = "completed"
    repository.add(db, check_in)
    db.commit()
    db.refresh(check_in)
    return _check_in_detail_response(check_in)


def get_check_in(db: Session, user: User, check_in_id: str) -> CheckInDetailResponse:
    return _check_in_detail_response(_get_owned_check_in(db, user, check_in_id))


def update_check_in(db: Session, user: User, check_in_id: str, payload: CheckInUpdateRequest) -> CheckInDetailResponse:
    check_in = _get_owned_check_in(db, user, check_in_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(check_in, field, value)
    db.commit()
    db.refresh(check_in)
    return _check_in_detail_response(check_in)


def delete_check_in(db: Session, user: User, check_in_id: str) -> None:
    check_in = _get_owned_check_in(db, user, check_in_id)
    repository.delete_record(db, check_in)
    db.commit()


def get_dashboard(db: Session, user: User) -> GoalTrackerDashboardResponse:
    goals = repository.list_goals(db, user.id)
    milestones = repository.list_milestones(db, user.id)
    check_ins = repository.list_check_ins(db, user.id)
    month_prefix = date.today().isoformat()[:7]
    return GoalTrackerDashboardResponse(
        goals=[_goal_summary_response(goal) for goal in goals],
        milestones=[_milestone_summary_response(milestone) for milestone in milestones],
        check_ins=[_check_in_summary_response(check_in) for check_in in check_ins],
        active_goal_count=sum(1 for goal in goals if goal.status == "active"),
        completed_goal_count=sum(1 for goal in goals if goal.status == "completed"),
        paused_goal_count=sum(1 for goal in goals if goal.status == "paused"),
        average_progress=round(sum(goal.progress for goal in goals) / len(goals)) if goals else 0,
        check_ins_this_month=sum(1 for check_in in check_ins if check_in.check_in_date.startswith(month_prefix)),
        high_priority_goal_count=sum(1 for goal in goals if goal.priority == "high"),
        recent_check_ins=[_check_in_summary_response(check_in) for check_in in check_ins[:5]],
    )
