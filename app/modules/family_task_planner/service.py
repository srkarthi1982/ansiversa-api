from collections import Counter, defaultdict
from datetime import date, datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.family_task_planner import repository
from app.modules.family_task_planner.models import FamilyTask, FamilyTaskCategory, FamilyTaskMember
from app.modules.family_task_planner.schemas import (
    CalendarDayResponse,
    CategoryCreateRequest,
    CategoryDetailResponse,
    CategoryDistributionResponse,
    CategorySummaryResponse,
    CategoryUpdateRequest,
    FamilyTaskPlannerDashboardResponse,
    MemberCreateRequest,
    MemberDetailResponse,
    MemberSummaryResponse,
    MemberUpdateRequest,
    TaskCreateRequest,
    TaskDetailResponse,
    TaskDuplicateRequest,
    TaskSummaryResponse,
    TaskUpdateRequest,
    WorkloadResponse,
)

PREVIEW_LENGTH = 220


def _today() -> str:
    return date.today().isoformat()


def _preview(value: str | None) -> str | None:
    if not value:
        return None
    if len(value) <= PREVIEW_LENGTH:
        return value
    return f"{value[:PREVIEW_LENGTH].rstrip()}..."


def _not_found(detail: str) -> None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def _get_owned_member(db: Session, user: User, member_id: str) -> FamilyTaskMember:
    member = repository.get_member(db, member_id)
    if not member or member.owner_id != user.id:
        _not_found("Family member was not found.")
    return member


def _get_owned_category(db: Session, user: User, category_id: str) -> FamilyTaskCategory:
    category = repository.get_category(db, category_id)
    if not category or category.owner_id != user.id:
        _not_found("Category was not found.")
    return category


def _get_owned_task(db: Session, user: User, task_id: str) -> FamilyTask:
    task = repository.get_task(db, task_id)
    if not task or task.owner_id != user.id:
        _not_found("Task was not found.")
    return task


def _validate_optional_parent(db: Session, user: User, member_id: str | None, category_id: str | None) -> None:
    if member_id:
        _get_owned_member(db, user, member_id)
    if category_id:
        _get_owned_category(db, user, category_id)


def _member_summary(member: FamilyTaskMember) -> MemberSummaryResponse:
    active_tasks = [task for task in member.tasks if task.status != "archived"]
    return MemberSummaryResponse(
        id=member.id,
        name=member.name,
        color=member.color,
        avatar=member.avatar,
        status=member.status,
        task_count=len(active_tasks),
        pending_count=len([task for task in active_tasks if task.status != "completed"]),
        completed_count=len([task for task in active_tasks if task.status == "completed"]),
        created_at=member.created_at,
        updated_at=member.updated_at,
    )


def _category_summary(category: FamilyTaskCategory) -> CategorySummaryResponse:
    return CategorySummaryResponse(
        id=category.id,
        name=category.name,
        color=category.color,
        description_preview=_preview(category.description),
        status=category.status,
        task_count=len([task for task in category.tasks if task.status != "archived"]),
        created_at=category.created_at,
        updated_at=category.updated_at,
    )


def _task_summary(task: FamilyTask) -> TaskSummaryResponse:
    return TaskSummaryResponse(
        id=task.id,
        member_id=task.member_id,
        member_name=task.member.name if task.member else None,
        category_id=task.category_id,
        category_name=task.category.name if task.category else None,
        title=task.title,
        description_preview=_preview(task.description),
        priority=task.priority,
        due_date=task.due_date,
        recurring=task.recurring,
        status=task.status,
        notes_preview=_preview(task.notes),
        completed_at=task.completed_at,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )


def _category_detail(category: FamilyTaskCategory) -> CategoryDetailResponse:
    return CategoryDetailResponse(**_category_summary(category).model_dump(), description=category.description)


def _task_detail(task: FamilyTask) -> TaskDetailResponse:
    return TaskDetailResponse(**_task_summary(task).model_dump(), description=task.description, notes=task.notes)


def list_members(db: Session, user: User) -> list[MemberSummaryResponse]:
    return [_member_summary(member) for member in repository.list_members(db, user.id)]


def create_member(db: Session, user: User, payload: MemberCreateRequest) -> MemberDetailResponse:
    member = FamilyTaskMember(owner_id=user.id, **payload.model_dump())
    repository.add(db, member)
    db.commit()
    db.refresh(member)
    return MemberDetailResponse(**_member_summary(member).model_dump())


def get_member(db: Session, user: User, member_id: str) -> MemberDetailResponse:
    return MemberDetailResponse(**_member_summary(_get_owned_member(db, user, member_id)).model_dump())


def update_member(db: Session, user: User, member_id: str, payload: MemberUpdateRequest) -> MemberDetailResponse:
    member = _get_owned_member(db, user, member_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(member, field, value)
    db.commit()
    db.refresh(member)
    return MemberDetailResponse(**_member_summary(member).model_dump())


def delete_member(db: Session, user: User, member_id: str) -> None:
    member = _get_owned_member(db, user, member_id)
    repository.delete_record(db, member)
    db.commit()


def list_categories(db: Session, user: User) -> list[CategorySummaryResponse]:
    return [_category_summary(category) for category in repository.list_categories(db, user.id)]


def create_category(db: Session, user: User, payload: CategoryCreateRequest) -> CategoryDetailResponse:
    category = FamilyTaskCategory(owner_id=user.id, **payload.model_dump())
    repository.add(db, category)
    db.commit()
    db.refresh(category)
    return _category_detail(category)


def get_category(db: Session, user: User, category_id: str) -> CategoryDetailResponse:
    return _category_detail(_get_owned_category(db, user, category_id))


def update_category(db: Session, user: User, category_id: str, payload: CategoryUpdateRequest) -> CategoryDetailResponse:
    category = _get_owned_category(db, user, category_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(category, field, value)
    db.commit()
    db.refresh(category)
    return _category_detail(category)


def delete_category(db: Session, user: User, category_id: str) -> None:
    category = _get_owned_category(db, user, category_id)
    repository.delete_record(db, category)
    db.commit()


def list_tasks(db: Session, user: User) -> list[TaskSummaryResponse]:
    return [_task_summary(task) for task in repository.list_tasks(db, user.id)]


def create_task(db: Session, user: User, payload: TaskCreateRequest) -> TaskDetailResponse:
    data = payload.model_dump()
    _validate_optional_parent(db, user, data.get("member_id"), data.get("category_id"))
    completed_at = _today() if data.get("status") == "completed" else None
    task = FamilyTask(owner_id=user.id, completed_at=completed_at, **data)
    repository.add(db, task)
    db.commit()
    db.refresh(task)
    return _task_detail(task)


def get_task(db: Session, user: User, task_id: str) -> TaskDetailResponse:
    return _task_detail(_get_owned_task(db, user, task_id))


def update_task(db: Session, user: User, task_id: str, payload: TaskUpdateRequest) -> TaskDetailResponse:
    task = _get_owned_task(db, user, task_id)
    data = payload.model_dump(exclude_unset=True)
    _validate_optional_parent(db, user, data.get("member_id"), data.get("category_id"))
    if data.get("status") == "completed" and task.status != "completed":
        task.completed_at = _today()
    if data.get("status") and data.get("status") != "completed":
        task.completed_at = None
    for field, value in data.items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return _task_detail(task)


def complete_task(db: Session, user: User, task_id: str) -> TaskDetailResponse:
    task = _get_owned_task(db, user, task_id)
    task.status = "completed"
    task.completed_at = _today()
    db.commit()
    db.refresh(task)
    return _task_detail(task)


def reopen_task(db: Session, user: User, task_id: str) -> TaskDetailResponse:
    task = _get_owned_task(db, user, task_id)
    task.status = "reopened"
    task.completed_at = None
    db.commit()
    db.refresh(task)
    return _task_detail(task)


def duplicate_task(db: Session, user: User, task_id: str, payload: TaskDuplicateRequest) -> TaskDetailResponse:
    task = _get_owned_task(db, user, task_id)
    duplicate = FamilyTask(
        owner_id=user.id,
        member_id=task.member_id,
        category_id=task.category_id,
        title=payload.title or f"{task.title} copy",
        description=task.description,
        priority=task.priority,
        due_date=payload.due_date or task.due_date,
        recurring=task.recurring,
        status="pending",
        notes=task.notes,
    )
    repository.add(db, duplicate)
    db.commit()
    db.refresh(duplicate)
    return _task_detail(duplicate)


def delete_task(db: Session, user: User, task_id: str) -> None:
    task = _get_owned_task(db, user, task_id)
    repository.delete_record(db, task)
    db.commit()


def get_dashboard(db: Session, user: User) -> FamilyTaskPlannerDashboardResponse:
    tasks = [_task_summary(task) for task in repository.list_tasks(db, user.id)]
    members = [_member_summary(member) for member in repository.list_members(db, user.id)]
    categories = [_category_summary(category) for category in repository.list_categories(db, user.id)]
    today = _today()
    week_start = date.today() - timedelta(days=date.today().weekday())
    week_end = week_start + timedelta(days=6)
    visible_tasks = [task for task in tasks if task.status != "archived"]
    completed = [task for task in visible_tasks if task.status == "completed"]
    pending = [task for task in visible_tasks if task.status != "completed"]
    due_today = [task for task in pending if task.due_date == today]
    upcoming = [task for task in pending if task.due_date and task.due_date > today][:8]
    overdue = [task for task in pending if task.due_date and task.due_date < today]
    recent_completed = sorted(completed, key=lambda task: task.completed_at or "", reverse=True)[:8]
    completed_this_week = [
        task for task in completed
        if task.completed_at and week_start <= datetime.fromisoformat(task.completed_at).date() <= week_end
    ]
    grouped: dict[str, list[TaskSummaryResponse]] = defaultdict(list)
    for task in sorted([item for item in pending if item.due_date], key=lambda item: item.due_date or ""):
        if task.due_date:
            grouped[task.due_date].append(task)
    workload = [
        WorkloadResponse(
            member_id=member.id,
            member_name=member.name,
            pending_count=len([task for task in pending if task.member_id == member.id]),
            completed_count=len([task for task in completed if task.member_id == member.id]),
        )
        for member in members
    ]
    unassigned_pending = len([task for task in pending if not task.member_id])
    unassigned_completed = len([task for task in completed if not task.member_id])
    if unassigned_pending or unassigned_completed:
        workload.append(WorkloadResponse(member_id=None, member_name="Unassigned", pending_count=unassigned_pending, completed_count=unassigned_completed))
    member_activity = Counter(task.member_name for task in completed if task.member_name)
    category_counts = Counter(task.category_name or "Uncategorized" for task in visible_tasks)
    category_ids = {task.category_name or "Uncategorized": task.category_id for task in visible_tasks}
    return FamilyTaskPlannerDashboardResponse(
        tasks=tasks,
        members=members,
        categories=categories,
        task_count=len(visible_tasks),
        pending_count=len(pending),
        completed_count=len(completed),
        overdue_count=len(overdue),
        due_today=due_today[:8],
        upcoming_tasks=upcoming,
        recently_completed=recent_completed,
        workload=workload,
        calendar=[CalendarDayResponse(date=day, tasks=items[:12]) for day, items in list(grouped.items())[:14]],
        completed_this_week=len(completed_this_week),
        completion_rate=round((len(completed) / len(visible_tasks)) * 100) if visible_tasks else 0,
        most_active_member=member_activity.most_common(1)[0][0] if member_activity else None,
        category_distribution=[
            CategoryDistributionResponse(category_id=category_ids[name], category_name=name, task_count=count)
            for name, count in category_counts.most_common()
        ],
    )
