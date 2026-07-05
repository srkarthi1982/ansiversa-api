from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.wellness_and_goal_planner import repository
from app.modules.wellness_and_goal_planner.models import WellnessArea, WellnessGoal, WellnessReflection
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

PREVIEW_LENGTH = 220


def _preview(value: str | None) -> str | None:
    if not value:
        return None
    if len(value) <= PREVIEW_LENGTH:
        return value
    return f"{value[:PREVIEW_LENGTH].rstrip()}..."


def _required_preview(value: str) -> str:
    return _preview(value) or ""


def _not_found(detail: str) -> None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def _get_owned_area(db: Session, user: User, area_id: int) -> WellnessArea:
    area = repository.get_area(db, area_id)
    if not area or area.owner_id != user.id:
        _not_found("Wellness area was not found.")
    return area


def _get_owned_goal(db: Session, user: User, goal_id: int) -> WellnessGoal:
    goal = repository.get_goal(db, goal_id)
    if not goal or goal.owner_id != user.id:
        _not_found("Wellness goal was not found.")
    return goal


def _get_owned_reflection(db: Session, user: User, reflection_id: int) -> WellnessReflection:
    reflection = repository.get_reflection(db, reflection_id)
    if not reflection or reflection.owner_id != user.id:
        _not_found("Wellness reflection was not found.")
    return reflection


def _validate_area(db: Session, user: User, area_id: int | None) -> None:
    if area_id is not None:
        _get_owned_area(db, user, area_id)


def _validate_goal(db: Session, user: User, goal_id: int | None) -> None:
    if goal_id is not None:
        _get_owned_goal(db, user, goal_id)


def _area_counts(goals: list[WellnessGoal]) -> dict[int, tuple[int, int]]:
    counts: dict[int, tuple[int, int]] = {}
    for goal in goals:
        if goal.area_id is None:
            continue
        total, active = counts.get(goal.area_id, (0, 0))
        counts[goal.area_id] = (total + 1, active + (1 if goal.status == "active" else 0))
    return counts


def _area_summary_response(area: WellnessArea, goals: list[WellnessGoal] | None = None) -> WellnessAreaSummaryResponse:
    counts = _area_counts(goals or [])
    total, active = counts.get(area.id, (0, 0))
    return WellnessAreaSummaryResponse(
        id=area.id,
        name=area.name,
        description_preview=_preview(area.description),
        color=area.color,
        icon=area.icon,
        goal_count=total,
        active_goal_count=active,
        created_at=area.created_at,
        updated_at=area.updated_at,
    )


def _area_detail_response(area: WellnessArea, goals: list[WellnessGoal] | None = None) -> WellnessAreaDetailResponse:
    summary = _area_summary_response(area, goals)
    return WellnessAreaDetailResponse(**summary.model_dump(), description=area.description)


def _goal_summary_response(goal: WellnessGoal) -> WellnessGoalSummaryResponse:
    return WellnessGoalSummaryResponse(
        id=goal.id,
        title=goal.title,
        area_id=goal.area_id,
        area_name=goal.area.name if goal.area else None,
        area_color=goal.area.color if goal.area else None,
        description_preview=_preview(goal.description),
        target_date=goal.target_date,
        status=goal.status,
        priority=goal.priority,
        progress=goal.progress,
        reflection_count=len(goal.reflections),
        created_at=goal.created_at,
        updated_at=goal.updated_at,
    )


def _goal_detail_response(goal: WellnessGoal) -> WellnessGoalDetailResponse:
    summary = _goal_summary_response(goal)
    return WellnessGoalDetailResponse(**summary.model_dump(), description=goal.description)


def _reflection_summary_response(reflection: WellnessReflection) -> WellnessReflectionSummaryResponse:
    return WellnessReflectionSummaryResponse(
        id=reflection.id,
        goal_id=reflection.goal_id,
        goal_title=reflection.goal.title if reflection.goal else None,
        reflection_date=reflection.reflection_date,
        reflection_preview=_required_preview(reflection.reflection),
        mood=reflection.mood,
        notes_preview=_preview(reflection.notes),
        created_at=reflection.created_at,
        updated_at=reflection.updated_at,
    )


def _reflection_detail_response(reflection: WellnessReflection) -> WellnessReflectionDetailResponse:
    summary = _reflection_summary_response(reflection)
    return WellnessReflectionDetailResponse(
        **summary.model_dump(),
        reflection=reflection.reflection,
        notes=reflection.notes,
    )


def list_areas(db: Session, user: User) -> list[WellnessAreaSummaryResponse]:
    goals = repository.list_goals(db, user.id)
    return [_area_summary_response(area, goals) for area in repository.list_areas(db, user.id)]


def create_area(db: Session, user: User, payload: WellnessAreaCreateRequest) -> WellnessAreaDetailResponse:
    area = WellnessArea(owner_id=user.id, **payload.model_dump())
    repository.add(db, area)
    db.commit()
    db.refresh(area)
    return _area_detail_response(area, [])


def get_area(db: Session, user: User, area_id: int) -> WellnessAreaDetailResponse:
    return _area_detail_response(_get_owned_area(db, user, area_id), repository.list_goals(db, user.id))


def update_area(
    db: Session,
    user: User,
    area_id: int,
    payload: WellnessAreaUpdateRequest,
) -> WellnessAreaDetailResponse:
    area = _get_owned_area(db, user, area_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(area, field, value)
    db.commit()
    db.refresh(area)
    return _area_detail_response(area, repository.list_goals(db, user.id))


def delete_area(db: Session, user: User, area_id: int) -> None:
    area = _get_owned_area(db, user, area_id)
    repository.detach_area_from_goals(db, user.id, area.id)
    repository.delete_record(db, area)
    db.commit()


def list_goals(db: Session, user: User) -> list[WellnessGoalSummaryResponse]:
    return [_goal_summary_response(goal) for goal in repository.list_goals(db, user.id)]


def create_goal(db: Session, user: User, payload: WellnessGoalCreateRequest) -> WellnessGoalDetailResponse:
    data = payload.model_dump()
    _validate_area(db, user, data.get("area_id"))
    goal = WellnessGoal(owner_id=user.id, **data)
    repository.add(db, goal)
    db.commit()
    db.refresh(goal)
    return _goal_detail_response(goal)


def get_goal(db: Session, user: User, goal_id: int) -> WellnessGoalDetailResponse:
    return _goal_detail_response(_get_owned_goal(db, user, goal_id))


def update_goal(
    db: Session,
    user: User,
    goal_id: int,
    payload: WellnessGoalUpdateRequest,
) -> WellnessGoalDetailResponse:
    goal = _get_owned_goal(db, user, goal_id)
    data = payload.model_dump(exclude_unset=True)
    if "area_id" in data:
        _validate_area(db, user, data["area_id"])
    for field, value in data.items():
        setattr(goal, field, value)
    db.commit()
    db.refresh(goal)
    return _goal_detail_response(goal)


def delete_goal(db: Session, user: User, goal_id: int) -> None:
    goal = _get_owned_goal(db, user, goal_id)
    repository.detach_goal_from_reflections(db, user.id, goal.id)
    repository.delete_record(db, goal)
    db.commit()


def list_reflections(db: Session, user: User) -> list[WellnessReflectionSummaryResponse]:
    return [_reflection_summary_response(reflection) for reflection in repository.list_reflections(db, user.id)]


def create_reflection(
    db: Session,
    user: User,
    payload: WellnessReflectionCreateRequest,
) -> WellnessReflectionDetailResponse:
    data = payload.model_dump()
    _validate_goal(db, user, data.get("goal_id"))
    reflection = WellnessReflection(owner_id=user.id, **data)
    repository.add(db, reflection)
    db.commit()
    db.refresh(reflection)
    return _reflection_detail_response(reflection)


def get_reflection(db: Session, user: User, reflection_id: int) -> WellnessReflectionDetailResponse:
    return _reflection_detail_response(_get_owned_reflection(db, user, reflection_id))


def update_reflection(
    db: Session,
    user: User,
    reflection_id: int,
    payload: WellnessReflectionUpdateRequest,
) -> WellnessReflectionDetailResponse:
    reflection = _get_owned_reflection(db, user, reflection_id)
    data = payload.model_dump(exclude_unset=True)
    if "goal_id" in data:
        _validate_goal(db, user, data["goal_id"])
    for field, value in data.items():
        setattr(reflection, field, value)
    db.commit()
    db.refresh(reflection)
    return _reflection_detail_response(reflection)


def delete_reflection(db: Session, user: User, reflection_id: int) -> None:
    reflection = _get_owned_reflection(db, user, reflection_id)
    repository.delete_record(db, reflection)
    db.commit()


def get_dashboard(db: Session, user: User) -> WellnessDashboardResponse:
    goals = list_goals(db, user)
    areas = list_areas(db, user)
    reflections = list_reflections(db, user)
    current_month = date.today().isoformat()[:7]
    average_progress = round(sum(goal.progress for goal in goals) / len(goals)) if goals else 0

    return WellnessDashboardResponse(
        areas=areas,
        goals=goals,
        reflections=reflections,
        active_goal_count=sum(1 for goal in goals if goal.status == "active"),
        completed_goal_count=sum(1 for goal in goals if goal.status == "completed"),
        wellness_area_count=len(areas),
        reflections_this_month=sum(1 for reflection in reflections if reflection.reflection_date.startswith(current_month)),
        average_progress=average_progress,
        recent_reflections=reflections[:5],
    )
