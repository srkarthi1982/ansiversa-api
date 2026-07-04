from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.task_prioritizer.models import (
    TaskPrioritizerPriorityHistory,
    TaskPrioritizerPriorityRule,
    TaskPrioritizerTask,
    TaskPrioritizerTaskPriority,
)


def get_task(db: Session, task_id: int) -> TaskPrioritizerTask | None:
    return db.get(TaskPrioritizerTask, task_id)


def get_rule(db: Session, rule_id: int) -> TaskPrioritizerPriorityRule | None:
    return db.get(TaskPrioritizerPriorityRule, rule_id)


def list_tasks(db: Session, owner_id: str) -> list[TaskPrioritizerTask]:
    return list(
        db.execute(
            select(TaskPrioritizerTask)
            .where(TaskPrioritizerTask.owner_id == owner_id)
            .order_by(TaskPrioritizerTask.priority_score.desc(), TaskPrioritizerTask.updated_at.desc())
        )
        .scalars()
        .all()
    )


def list_rules(db: Session, owner_id: str) -> list[TaskPrioritizerPriorityRule]:
    return list(
        db.execute(
            select(TaskPrioritizerPriorityRule)
            .where(TaskPrioritizerPriorityRule.owner_id == owner_id)
            .order_by(TaskPrioritizerPriorityRule.is_enabled.desc(), TaskPrioritizerPriorityRule.updated_at.desc())
        )
        .scalars()
        .all()
    )


def list_enabled_rules(db: Session, owner_id: str) -> list[TaskPrioritizerPriorityRule]:
    return list(
        db.execute(
            select(TaskPrioritizerPriorityRule)
            .where(
                TaskPrioritizerPriorityRule.owner_id == owner_id,
                TaskPrioritizerPriorityRule.is_enabled.is_(True),
            )
            .order_by(TaskPrioritizerPriorityRule.category.asc(), TaskPrioritizerPriorityRule.updated_at.desc())
        )
        .scalars()
        .all()
    )


def list_history(db: Session, owner_id: str) -> list[tuple[TaskPrioritizerPriorityHistory, TaskPrioritizerTask | None]]:
    return list(
        db.execute(
            select(TaskPrioritizerPriorityHistory, TaskPrioritizerTask)
            .outerjoin(TaskPrioritizerTask, TaskPrioritizerTask.id == TaskPrioritizerPriorityHistory.task_id)
            .where(TaskPrioritizerPriorityHistory.owner_id == owner_id)
            .order_by(TaskPrioritizerPriorityHistory.created_at.desc())
            .limit(100)
        ).all()
    )


def add(db: Session, record: object) -> None:
    db.add(record)


def delete_record(db: Session, record: object) -> None:
    db.delete(record)


def record_priority(
    db: Session,
    *,
    owner_id: str,
    task_id: int,
    priority_score: float,
    priority_label: str,
    source: str,
    reason: str | None,
) -> TaskPrioritizerTaskPriority:
    priority = TaskPrioritizerTaskPriority(
        owner_id=owner_id,
        task_id=task_id,
        priority_score=priority_score,
        priority_label=priority_label,
        source=source,
        reason=reason,
    )
    add(db, priority)
    return priority


def record_history(
    db: Session,
    *,
    owner_id: str,
    task_id: int | None,
    action_type: str,
    previous_priority: str | None = None,
    new_priority: str | None = None,
    priority_score: float | None = None,
    notes: str | None = None,
) -> TaskPrioritizerPriorityHistory:
    history = TaskPrioritizerPriorityHistory(
        owner_id=owner_id,
        task_id=task_id,
        action_type=action_type,
        previous_priority=previous_priority,
        new_priority=new_priority,
        priority_score=priority_score,
        notes=notes,
    )
    add(db, history)
    return history
