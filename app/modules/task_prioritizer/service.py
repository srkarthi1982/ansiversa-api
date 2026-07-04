from datetime import date, datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.task_prioritizer import repository
from app.modules.task_prioritizer.models import TaskPrioritizerPriorityRule, TaskPrioritizerTask
from app.modules.task_prioritizer.schemas import (
    TaskPrioritizerDashboardResponse,
    TaskPrioritizerHistoryResponse,
    TaskPrioritizerPriorityAssignRequest,
    TaskPrioritizerRuleCreateRequest,
    TaskPrioritizerRuleResponse,
    TaskPrioritizerRuleUpdateRequest,
    TaskPrioritizerTaskCreateRequest,
    TaskPrioritizerTaskDetailResponse,
    TaskPrioritizerTaskSummaryResponse,
    TaskPrioritizerTaskUpdateRequest,
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


def _get_owned_task(db: Session, user: User, task_id: int) -> TaskPrioritizerTask:
    task = repository.get_task(db, task_id)
    if not task or task.owner_id != user.id:
        _not_found("Task was not found.")
    return task


def _get_owned_rule(db: Session, user: User, rule_id: int) -> TaskPrioritizerPriorityRule:
    rule = repository.get_rule(db, rule_id)
    if not rule or rule.owner_id != user.id:
        _not_found("Priority rule was not found.")
    return rule


def _due_date_score(value: str | None) -> float:
    if not value:
        return 0
    try:
        days = (date.fromisoformat(value[:10]) - date.today()).days
    except ValueError:
        return 0
    if days < 0:
        return 5
    if days <= 1:
        return 4
    if days <= 3:
        return 3
    if days <= 7:
        return 2
    return 1


def _label_for_score(score: float) -> str:
    if score >= 26:
        return "urgent"
    if score >= 18:
        return "high"
    if score >= 10:
        return "medium"
    return "low"


def _matching_rule(task: TaskPrioritizerTask, rules: list[TaskPrioritizerPriorityRule]) -> TaskPrioritizerPriorityRule | None:
    for rule in rules:
        if rule.category == task.category:
            return rule
    return next((rule for rule in rules if rule.category is None), None)


def _score_task(task: TaskPrioritizerTask, rules: list[TaskPrioritizerPriorityRule]) -> tuple[float, str]:
    rule = _matching_rule(task, rules)
    impact_weight = rule.impact_weight if rule else 2
    urgency_weight = rule.urgency_weight if rule else 2
    effort_weight = rule.effort_weight if rule else 1
    due_date_weight = rule.due_date_weight if rule else 2
    score = (
        task.impact * impact_weight
        + task.urgency * urgency_weight
        + (6 - task.effort) * effort_weight
        + _due_date_score(task.due_date) * due_date_weight
    )
    rounded = round(score, 1)
    return rounded, _label_for_score(rounded)


def _apply_system_priority(db: Session, user: User, task: TaskPrioritizerTask, reason: str) -> None:
    if task.manual_override:
        return
    previous_priority = task.priority_label
    score, label = _score_task(task, repository.list_enabled_rules(db, user.id))
    task.priority_score = score
    task.priority_label = label
    repository.record_priority(
        db,
        owner_id=user.id,
        task_id=task.id,
        priority_score=score,
        priority_label=label,
        source="system",
        reason=reason,
    )
    if previous_priority != label:
        repository.record_history(
            db,
            owner_id=user.id,
            task_id=task.id,
            action_type="recalculated",
            previous_priority=previous_priority,
            new_priority=label,
            priority_score=score,
            notes=reason,
        )


def _task_summary_response(task: TaskPrioritizerTask) -> TaskPrioritizerTaskSummaryResponse:
    return TaskPrioritizerTaskSummaryResponse(
        id=task.id,
        platform_id=task.platform_id,
        title=task.title,
        category=task.category,
        status=task.status,
        due_date=task.due_date,
        effort=task.effort,
        impact=task.impact,
        urgency=task.urgency,
        priority_score=task.priority_score,
        priority_label=task.priority_label,
        manual_override=task.manual_override,
        notes_preview=_preview(task.notes),
        created_at=task.created_at,
        updated_at=task.updated_at,
    )


def _task_detail_response(task: TaskPrioritizerTask) -> TaskPrioritizerTaskDetailResponse:
    summary = _task_summary_response(task)
    return TaskPrioritizerTaskDetailResponse(**summary.model_dump(), notes=task.notes)


def _rule_response(rule: TaskPrioritizerPriorityRule) -> TaskPrioritizerRuleResponse:
    return TaskPrioritizerRuleResponse.model_validate(rule)


def _history_response(item: tuple[object, TaskPrioritizerTask | None]) -> TaskPrioritizerHistoryResponse:
    history, task = item
    return TaskPrioritizerHistoryResponse(
        id=history.id,
        task_id=history.task_id,
        task_title=task.title if task else None,
        action_type=history.action_type,
        previous_priority=history.previous_priority,
        new_priority=history.new_priority,
        priority_score=history.priority_score,
        notes=history.notes,
        created_at=history.created_at,
    )


def list_tasks(db: Session, user: User) -> list[TaskPrioritizerTaskSummaryResponse]:
    return [_task_summary_response(task) for task in repository.list_tasks(db, user.id)]


def create_task(db: Session, user: User, payload: TaskPrioritizerTaskCreateRequest) -> TaskPrioritizerTaskDetailResponse:
    data = payload.model_dump()
    priority_label = data.pop("priority_label")
    manual_override = data.pop("manual_override")
    task = TaskPrioritizerTask(owner_id=user.id, priority_label=priority_label, manual_override=manual_override, **data)
    repository.add(db, task)
    db.flush()
    if task.manual_override:
        task.priority_score = max(task.priority_score, 1)
        repository.record_priority(
            db,
            owner_id=user.id,
            task_id=task.id,
            priority_score=task.priority_score,
            priority_label=task.priority_label,
            source="manual",
            reason="Manual priority set during task creation.",
        )
    else:
        _apply_system_priority(db, user, task, "Initial local priority calculation.")
    repository.record_history(
        db,
        owner_id=user.id,
        task_id=task.id,
        action_type="created",
        new_priority=task.priority_label,
        priority_score=task.priority_score,
        notes="Task created.",
    )
    db.commit()
    db.refresh(task)
    return _task_detail_response(task)


def get_task(db: Session, user: User, task_id: int) -> TaskPrioritizerTaskDetailResponse:
    return _task_detail_response(_get_owned_task(db, user, task_id))


def update_task(
    db: Session,
    user: User,
    task_id: int,
    payload: TaskPrioritizerTaskUpdateRequest,
) -> TaskPrioritizerTaskDetailResponse:
    task = _get_owned_task(db, user, task_id)
    previous_priority = task.priority_label
    previous_status = task.status
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    _apply_system_priority(db, user, task, "Task details changed.")
    action_type = "status-change" if previous_status != task.status else "updated"
    repository.record_history(
        db,
        owner_id=user.id,
        task_id=task.id,
        action_type=action_type,
        previous_priority=previous_priority,
        new_priority=task.priority_label,
        priority_score=task.priority_score,
        notes="Task updated.",
    )
    db.commit()
    db.refresh(task)
    return _task_detail_response(task)


def delete_task(db: Session, user: User, task_id: int) -> None:
    task = _get_owned_task(db, user, task_id)
    repository.record_history(
        db,
        owner_id=user.id,
        task_id=None,
        action_type="deleted",
        previous_priority=task.priority_label,
        notes=f"Deleted task: {task.title}",
    )
    repository.delete_record(db, task)
    db.commit()


def duplicate_task(db: Session, user: User, task_id: int) -> TaskPrioritizerTaskDetailResponse:
    task = _get_owned_task(db, user, task_id)
    duplicate = TaskPrioritizerTask(
        owner_id=user.id,
        platform_id=task.platform_id,
        title=f"{task.title} Copy",
        category=task.category,
        status="inbox",
        due_date=task.due_date,
        effort=task.effort,
        impact=task.impact,
        urgency=task.urgency,
        priority_score=task.priority_score,
        priority_label=task.priority_label,
        manual_override=task.manual_override,
        notes=task.notes,
    )
    repository.add(db, duplicate)
    db.flush()
    repository.record_history(
        db,
        owner_id=user.id,
        task_id=duplicate.id,
        action_type="duplicated",
        new_priority=duplicate.priority_label,
        priority_score=duplicate.priority_score,
        notes=f"Duplicated from task {task.id}.",
    )
    db.commit()
    db.refresh(duplicate)
    return _task_detail_response(duplicate)


def assign_priority(
    db: Session,
    user: User,
    task_id: int,
    payload: TaskPrioritizerPriorityAssignRequest,
) -> TaskPrioritizerTaskDetailResponse:
    task = _get_owned_task(db, user, task_id)
    previous_priority = task.priority_label
    task.priority_label = payload.priority_label
    task.priority_score = payload.priority_score if payload.priority_score is not None else task.priority_score
    task.manual_override = True
    repository.record_priority(
        db,
        owner_id=user.id,
        task_id=task.id,
        priority_score=task.priority_score,
        priority_label=task.priority_label,
        source="manual",
        reason=payload.reason,
    )
    repository.record_history(
        db,
        owner_id=user.id,
        task_id=task.id,
        action_type="priority-assigned",
        previous_priority=previous_priority,
        new_priority=task.priority_label,
        priority_score=task.priority_score,
        notes=payload.reason,
    )
    db.commit()
    db.refresh(task)
    return _task_detail_response(task)


def recalculate_priorities(db: Session, user: User) -> TaskPrioritizerDashboardResponse:
    for task in repository.list_tasks(db, user.id):
        _apply_system_priority(db, user, task, "Priorities recalculated from local task inputs.")
    db.commit()
    return get_dashboard(db, user)


def list_rules(db: Session, user: User) -> list[TaskPrioritizerRuleResponse]:
    return [_rule_response(rule) for rule in repository.list_rules(db, user.id)]


def create_rule(
    db: Session,
    user: User,
    payload: TaskPrioritizerRuleCreateRequest,
) -> TaskPrioritizerRuleResponse:
    rule = TaskPrioritizerPriorityRule(owner_id=user.id, **payload.model_dump())
    repository.add(db, rule)
    db.commit()
    db.refresh(rule)
    return _rule_response(rule)


def update_rule(
    db: Session,
    user: User,
    rule_id: int,
    payload: TaskPrioritizerRuleUpdateRequest,
) -> TaskPrioritizerRuleResponse:
    rule = _get_owned_rule(db, user, rule_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(rule, field, value)
    db.commit()
    db.refresh(rule)
    return _rule_response(rule)


def delete_rule(db: Session, user: User, rule_id: int) -> None:
    rule = _get_owned_rule(db, user, rule_id)
    repository.delete_record(db, rule)
    db.commit()


def list_history(db: Session, user: User) -> list[TaskPrioritizerHistoryResponse]:
    return [_history_response(item) for item in repository.list_history(db, user.id)]


def get_dashboard(db: Session, user: User) -> TaskPrioritizerDashboardResponse:
    tasks = list_tasks(db, user)
    rules = list_rules(db, user)
    history = list_history(db, user)
    today = date.today().isoformat()
    open_tasks = [task for task in tasks if task.status != "done"]
    top_tasks = sorted(open_tasks, key=lambda task: (task.priority_score, task.updated_at.timestamp()), reverse=True)[:5]
    average_score = round(sum(task.priority_score for task in tasks) / len(tasks), 1) if tasks else 0

    return TaskPrioritizerDashboardResponse(
        tasks=tasks,
        rules=rules,
        history=history,
        total_tasks=len(tasks),
        open_tasks=len(open_tasks),
        urgent_tasks=sum(1 for task in tasks if task.priority_label == "urgent"),
        overdue_tasks=sum(1 for task in open_tasks if task.due_date and task.due_date < today),
        manual_overrides=sum(1 for task in tasks if task.manual_override),
        average_priority_score=average_score,
        top_tasks=top_tasks,
    )
