from fastapi import HTTPException, status
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.course_tracker.models import (
    Course,
    CourseModule,
    CourseProgressLog,
)
from app.modules.course_tracker.schemas import (
    CourseCreateRequest,
    CourseModuleCreateRequest,
    CourseModuleResponse,
    CourseModuleUpdateRequest,
    CourseProgressLogCreateRequest,
    CourseProgressLogResponse,
    CourseResponse,
    CourseTrackerDashboardResponse,
    CourseTrackerReviewResponse,
    CourseUpdateRequest,
)


def _count_modules(db: Session, course_id: int, *, status_value: str | None = None) -> int:
    statement = select(func.count()).select_from(CourseModule).where(
        CourseModule.course_id == course_id
    )
    if status_value is not None:
        statement = statement.where(CourseModule.status == status_value)

    return int(db.execute(statement).scalar_one())


def _sum_minutes(db: Session, course_id: int | None = None, owner_id: str | None = None) -> int:
    statement = select(func.coalesce(func.sum(CourseProgressLog.minutes), 0)).select_from(
        CourseProgressLog
    )
    if course_id is not None:
        statement = statement.where(CourseProgressLog.course_id == course_id)
    if owner_id is not None:
        statement = statement.where(CourseProgressLog.owner_id == owner_id)

    return int(db.execute(statement).scalar_one())


def _completion_rate(total_count: int, completed_count: int) -> int:
    return round((completed_count / total_count) * 100) if total_count else 0


def _course_response(db: Session, course: Course) -> CourseResponse:
    module_count = _count_modules(db, course.id)
    completed_module_count = _count_modules(db, course.id, status_value="completed")
    return CourseResponse(
        id=course.id,
        title=course.title,
        provider=course.provider,
        category=course.category,
        goal=course.goal,
        start_date=course.start_date,
        target_date=course.target_date,
        status=course.status,
        module_count=module_count,
        completed_module_count=completed_module_count,
        total_minutes=_sum_minutes(db, course.id),
        completion_rate=_completion_rate(module_count, completed_module_count),
        created_at=course.created_at,
        updated_at=course.updated_at,
    )


def _module_response(module: CourseModule, course_title: str) -> CourseModuleResponse:
    return CourseModuleResponse(
        id=module.id,
        course_id=module.course_id,
        course_title=course_title,
        title=module.title,
        notes=module.notes,
        sequence=module.sequence,
        status=module.status,
        created_at=module.created_at,
        updated_at=module.updated_at,
    )


def _log_response(
    log: CourseProgressLog,
    course_title: str,
    module_title: str | None,
) -> CourseProgressLogResponse:
    return CourseProgressLogResponse(
        id=log.id,
        course_id=log.course_id,
        course_title=course_title,
        module_id=log.module_id,
        module_title=module_title,
        progress_date=log.progress_date,
        minutes=log.minutes,
        summary=log.summary,
        reflection=log.reflection,
        created_at=log.created_at,
    )


def _get_owned_course(db: Session, user: User, course_id: int) -> Course:
    course = db.get(Course, course_id)
    if not course or course.owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course was not found.",
        )

    return course


def _get_owned_module(db: Session, user: User, module_id: int) -> CourseModule:
    module = db.get(CourseModule, module_id)
    if not module or module.owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course module was not found.",
        )

    return module


def list_courses(db: Session, user: User) -> list[CourseResponse]:
    courses = list(
        db.execute(
            select(Course)
            .where(Course.owner_id == user.id)
            .order_by(Course.updated_at.desc(), Course.title.asc())
        )
        .scalars()
        .all()
    )

    return [_course_response(db, course) for course in courses]


def create_course(db: Session, user: User, payload: CourseCreateRequest) -> CourseResponse:
    course = Course(
        owner_id=user.id,
        title=payload.title,
        provider=payload.provider,
        category=payload.category,
        goal=payload.goal,
        start_date=payload.start_date,
        target_date=payload.target_date,
        status="active",
    )
    db.add(course)
    db.commit()
    db.refresh(course)

    return _course_response(db, course)


def update_course(
    db: Session,
    user: User,
    course_id: int,
    payload: CourseUpdateRequest,
) -> CourseResponse:
    course = _get_owned_course(db, user, course_id)
    next_values = payload.model_dump(exclude_unset=True)
    start_date = next_values.get("start_date", course.start_date)
    target_date = next_values.get("target_date", course.target_date)
    if target_date is not None and target_date < start_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="targetDate must be on or after startDate.",
        )

    for field, value in next_values.items():
        setattr(course, field, value)
    db.commit()
    db.refresh(course)

    return _course_response(db, course)


def delete_course(db: Session, user: User, course_id: int) -> None:
    course = _get_owned_course(db, user, course_id)
    db.execute(delete(CourseProgressLog).where(CourseProgressLog.course_id == course.id))
    db.execute(delete(CourseModule).where(CourseModule.course_id == course.id))
    db.delete(course)
    db.commit()


def list_modules(db: Session, user: User) -> list[CourseModuleResponse]:
    rows = db.execute(
        select(CourseModule, Course.title)
        .join(Course, Course.id == CourseModule.course_id)
        .where(CourseModule.owner_id == user.id)
        .order_by(CourseModule.sequence.asc(), CourseModule.updated_at.desc())
    ).all()

    return [_module_response(module, course_title) for module, course_title in rows]


def create_module(
    db: Session,
    user: User,
    payload: CourseModuleCreateRequest,
) -> CourseModuleResponse:
    course = _get_owned_course(db, user, payload.course_id)
    module = CourseModule(
        owner_id=user.id,
        course_id=course.id,
        title=payload.title,
        notes=payload.notes,
        sequence=payload.sequence,
        status="notStarted",
    )
    db.add(module)
    db.commit()
    db.refresh(module)

    return _module_response(module, course.title)


def update_module(
    db: Session,
    user: User,
    module_id: int,
    payload: CourseModuleUpdateRequest,
) -> CourseModuleResponse:
    module = _get_owned_module(db, user, module_id)
    course = _get_owned_course(db, user, module.course_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(module, field, value)
    db.commit()
    db.refresh(module)

    return _module_response(module, course.title)


def delete_module(db: Session, user: User, module_id: int) -> None:
    module = _get_owned_module(db, user, module_id)
    db.execute(delete(CourseProgressLog).where(CourseProgressLog.module_id == module.id))
    db.delete(module)
    db.commit()


def list_progress_logs(db: Session, user: User) -> list[CourseProgressLogResponse]:
    rows = db.execute(
        select(CourseProgressLog, Course.title, CourseModule.title)
        .join(Course, Course.id == CourseProgressLog.course_id)
        .outerjoin(CourseModule, CourseModule.id == CourseProgressLog.module_id)
        .where(CourseProgressLog.owner_id == user.id)
        .order_by(CourseProgressLog.progress_date.desc(), CourseProgressLog.created_at.desc())
    ).all()

    return [
        _log_response(log, course_title, module_title)
        for log, course_title, module_title in rows
    ]


def create_progress_log(
    db: Session,
    user: User,
    payload: CourseProgressLogCreateRequest,
) -> CourseProgressLogResponse:
    course = _get_owned_course(db, user, payload.course_id)
    module_title = None
    if payload.module_id is not None:
        module = _get_owned_module(db, user, payload.module_id)
        if module.course_id != course.id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Course module must belong to the selected course.",
            )
        module_title = module.title

    log = CourseProgressLog(
        owner_id=user.id,
        course_id=course.id,
        module_id=payload.module_id,
        progress_date=payload.progress_date,
        minutes=payload.minutes,
        summary=payload.summary,
        reflection=payload.reflection,
    )
    db.add(log)
    db.commit()
    db.refresh(log)

    return _log_response(log, course.title, module_title)


def get_review(db: Session, user: User) -> CourseTrackerReviewResponse:
    courses = list(db.execute(select(Course).where(Course.owner_id == user.id)).scalars().all())
    modules = list(
        db.execute(select(CourseModule).where(CourseModule.owner_id == user.id))
        .scalars()
        .all()
    )
    total_module_count = len(modules)
    completed_module_count = len(
        [module for module in modules if module.status == "completed"]
    )

    return CourseTrackerReviewResponse(
        active_course_count=len([course for course in courses if course.status == "active"]),
        completed_course_count=len(
            [course for course in courses if course.status == "completed"]
        ),
        total_module_count=total_module_count,
        completed_module_count=completed_module_count,
        total_minutes=_sum_minutes(db, owner_id=user.id),
        completion_rate=_completion_rate(total_module_count, completed_module_count),
        recent_logs=list_progress_logs(db, user)[:5],
    )


def get_dashboard(db: Session, user: User) -> CourseTrackerDashboardResponse:
    return CourseTrackerDashboardResponse(
        courses=list_courses(db, user),
        modules=list_modules(db, user),
        progress_logs=list_progress_logs(db, user),
        review=get_review(db, user),
    )
