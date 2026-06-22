from fastapi import HTTPException, status
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.study_planner.models import StudyLog, StudyPlan, StudyPlanTask
from app.modules.study_planner.schemas import (
    StudyLogCreateRequest,
    StudyLogResponse,
    StudyPlanCreateRequest,
    StudyPlannerDashboardResponse,
    StudyPlannerReviewResponse,
    StudyPlanResponse,
    StudyPlanTaskCreateRequest,
    StudyPlanTaskResponse,
    StudyPlanTaskUpdateRequest,
    StudyPlanUpdateRequest,
)


def _count_tasks(db: Session, plan_id: int, *, status_value: str | None = None) -> int:
    statement = select(func.count()).select_from(StudyPlanTask).where(
        StudyPlanTask.plan_id == plan_id
    )
    if status_value is not None:
        statement = statement.where(StudyPlanTask.status == status_value)

    return int(db.execute(statement).scalar_one())


def _sum_minutes(db: Session, plan_id: int | None = None, owner_id: str | None = None) -> int:
    statement = select(func.coalesce(func.sum(StudyLog.minutes), 0)).select_from(
        StudyLog
    )
    if plan_id is not None:
        statement = statement.where(StudyLog.plan_id == plan_id)
    if owner_id is not None:
        statement = statement.where(StudyLog.owner_id == owner_id)

    return int(db.execute(statement).scalar_one())


def _plan_response(db: Session, plan: StudyPlan) -> StudyPlanResponse:
    return StudyPlanResponse(
        id=plan.id,
        title=plan.title,
        subject=plan.subject,
        goal=plan.goal,
        start_date=plan.start_date,
        target_date=plan.target_date,
        status=plan.status,
        task_count=_count_tasks(db, plan.id),
        completed_task_count=_count_tasks(db, plan.id, status_value="completed"),
        total_minutes=_sum_minutes(db, plan.id),
        created_at=plan.created_at,
        updated_at=plan.updated_at,
    )


def _task_response(task: StudyPlanTask, plan_title: str) -> StudyPlanTaskResponse:
    return StudyPlanTaskResponse(
        id=task.id,
        plan_id=task.plan_id,
        plan_title=plan_title,
        title=task.title,
        notes=task.notes,
        due_date=task.due_date,
        priority=task.priority,
        status=task.status,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )


def _log_response(
    log: StudyLog,
    plan_title: str,
    task_title: str | None,
) -> StudyLogResponse:
    return StudyLogResponse(
        id=log.id,
        plan_id=log.plan_id,
        plan_title=plan_title,
        task_id=log.task_id,
        task_title=task_title,
        study_date=log.study_date,
        minutes=log.minutes,
        focus=log.focus,
        reflection=log.reflection,
        created_at=log.created_at,
    )


def _get_owned_plan(db: Session, user: User, plan_id: int) -> StudyPlan:
    plan = db.get(StudyPlan, plan_id)
    if not plan or plan.owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study plan was not found.",
        )

    return plan


def _get_owned_task(db: Session, user: User, task_id: int) -> StudyPlanTask:
    task = db.get(StudyPlanTask, task_id)
    if not task or task.owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study task was not found.",
        )

    return task


def list_plans(db: Session, user: User) -> list[StudyPlanResponse]:
    plans = list(
        db.execute(
            select(StudyPlan)
            .where(StudyPlan.owner_id == user.id)
            .order_by(StudyPlan.updated_at.desc(), StudyPlan.title.asc())
        )
        .scalars()
        .all()
    )

    return [_plan_response(db, plan) for plan in plans]


def create_plan(
    db: Session,
    user: User,
    payload: StudyPlanCreateRequest,
) -> StudyPlanResponse:
    plan = StudyPlan(
        owner_id=user.id,
        title=payload.title,
        subject=payload.subject,
        goal=payload.goal,
        start_date=payload.start_date,
        target_date=payload.target_date,
        status="active",
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)

    return _plan_response(db, plan)


def update_plan(
    db: Session,
    user: User,
    plan_id: int,
    payload: StudyPlanUpdateRequest,
) -> StudyPlanResponse:
    plan = _get_owned_plan(db, user, plan_id)
    next_values = payload.model_dump(exclude_unset=True)
    start_date = next_values.get("start_date", plan.start_date)
    target_date = next_values.get("target_date", plan.target_date)
    if target_date < start_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="targetDate must be on or after startDate.",
        )

    for field, value in next_values.items():
        setattr(plan, field, value)
    db.commit()
    db.refresh(plan)

    return _plan_response(db, plan)


def delete_plan(db: Session, user: User, plan_id: int) -> None:
    plan = _get_owned_plan(db, user, plan_id)
    db.execute(delete(StudyLog).where(StudyLog.plan_id == plan.id))
    db.execute(delete(StudyPlanTask).where(StudyPlanTask.plan_id == plan.id))
    db.delete(plan)
    db.commit()


def list_tasks(db: Session, user: User) -> list[StudyPlanTaskResponse]:
    rows = db.execute(
        select(StudyPlanTask, StudyPlan.title)
        .join(StudyPlan, StudyPlan.id == StudyPlanTask.plan_id)
        .where(StudyPlanTask.owner_id == user.id)
        .order_by(StudyPlanTask.updated_at.desc(), StudyPlanTask.title.asc())
    ).all()

    return [_task_response(task, plan_title) for task, plan_title in rows]


def create_task(
    db: Session,
    user: User,
    payload: StudyPlanTaskCreateRequest,
) -> StudyPlanTaskResponse:
    plan = _get_owned_plan(db, user, payload.plan_id)
    task = StudyPlanTask(
        owner_id=user.id,
        plan_id=plan.id,
        title=payload.title,
        notes=payload.notes,
        due_date=payload.due_date,
        priority=payload.priority,
        status="pending",
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    return _task_response(task, plan.title)


def update_task(
    db: Session,
    user: User,
    task_id: int,
    payload: StudyPlanTaskUpdateRequest,
) -> StudyPlanTaskResponse:
    task = _get_owned_task(db, user, task_id)
    plan = _get_owned_plan(db, user, task.plan_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)

    return _task_response(task, plan.title)


def delete_task(db: Session, user: User, task_id: int) -> None:
    task = _get_owned_task(db, user, task_id)
    db.execute(delete(StudyLog).where(StudyLog.task_id == task.id))
    db.delete(task)
    db.commit()


def list_logs(db: Session, user: User) -> list[StudyLogResponse]:
    rows = db.execute(
        select(StudyLog, StudyPlan.title, StudyPlanTask.title)
        .join(StudyPlan, StudyPlan.id == StudyLog.plan_id)
        .outerjoin(StudyPlanTask, StudyPlanTask.id == StudyLog.task_id)
        .where(StudyLog.owner_id == user.id)
        .order_by(StudyLog.study_date.desc(), StudyLog.created_at.desc())
    ).all()

    return [
        _log_response(log, plan_title, task_title)
        for log, plan_title, task_title in rows
    ]


def create_log(
    db: Session,
    user: User,
    payload: StudyLogCreateRequest,
) -> StudyLogResponse:
    plan = _get_owned_plan(db, user, payload.plan_id)
    task_title = None
    if payload.task_id is not None:
        task = _get_owned_task(db, user, payload.task_id)
        if task.plan_id != plan.id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Study task must belong to the selected plan.",
            )
        task_title = task.title

    log = StudyLog(
        owner_id=user.id,
        plan_id=plan.id,
        task_id=payload.task_id,
        study_date=payload.study_date,
        minutes=payload.minutes,
        focus=payload.focus,
        reflection=payload.reflection,
    )
    db.add(log)
    db.commit()
    db.refresh(log)

    return _log_response(log, plan.title, task_title)


def get_review(db: Session, user: User) -> StudyPlannerReviewResponse:
    plans = list(
        db.execute(select(StudyPlan).where(StudyPlan.owner_id == user.id))
        .scalars()
        .all()
    )
    tasks = list(
        db.execute(select(StudyPlanTask).where(StudyPlanTask.owner_id == user.id))
        .scalars()
        .all()
    )
    total_task_count = len(tasks)
    completed_task_count = len(
        [task for task in tasks if task.status == "completed"]
    )
    completion_rate = (
        round((completed_task_count / total_task_count) * 100)
        if total_task_count
        else 0
    )

    return StudyPlannerReviewResponse(
        active_plan_count=len([plan for plan in plans if plan.status == "active"]),
        completed_plan_count=len(
            [plan for plan in plans if plan.status == "completed"]
        ),
        total_task_count=total_task_count,
        completed_task_count=completed_task_count,
        total_minutes=_sum_minutes(db, owner_id=user.id),
        completion_rate=completion_rate,
        recent_logs=list_logs(db, user)[:5],
    )


def get_dashboard(db: Session, user: User) -> StudyPlannerDashboardResponse:
    return StudyPlannerDashboardResponse(
        plans=list_plans(db, user),
        tasks=list_tasks(db, user),
        logs=list_logs(db, user),
        review=get_review(db, user),
    )
