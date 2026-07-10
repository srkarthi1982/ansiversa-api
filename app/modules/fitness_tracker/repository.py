from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import Select, select

from app.modules.fitness_tracker.models import FitnessActivity, FitnessLog


def get_activity(db: Session, activity_id: str) -> FitnessActivity | None:
    return db.get(FitnessActivity, activity_id)


def get_log(db: Session, log_id: str) -> FitnessLog | None:
    return db.get(FitnessLog, log_id)


def _paginate(statement: Select[tuple[object]], page: int, page_size: int) -> Select[tuple[object]]:
    return statement.offset((page - 1) * page_size).limit(page_size)


def _activity_search(statement: Select[tuple[FitnessActivity]], query: str | None) -> Select[tuple[FitnessActivity]]:
    if not query:
        return statement
    pattern = f"%{query.strip()}%"
    return statement.where(or_(FitnessActivity.title.ilike(pattern), FitnessActivity.notes.ilike(pattern)))


def _log_search(statement: Select[tuple[FitnessLog]], query: str | None) -> Select[tuple[FitnessLog]]:
    if not query:
        return statement
    pattern = f"%{query.strip()}%"
    return statement.where(or_(FitnessLog.notes.ilike(pattern), FitnessActivity.title.ilike(pattern)))


def list_activities(
    db: Session,
    owner_id: str,
    *,
    query: str | None = None,
    activity_type: str | None = None,
    status: str | None = None,
    sort: str = "updatedAt",
    direction: str = "desc",
    page: int = 1,
    page_size: int = 100,
) -> tuple[list[FitnessActivity], int]:
    statement = select(FitnessActivity).options(joinedload(FitnessActivity.logs)).where(FitnessActivity.owner_id == owner_id)
    if activity_type:
        statement = statement.where(FitnessActivity.activity_type == activity_type)
    if status:
        statement = statement.where(FitnessActivity.status == status)
    statement = _activity_search(statement, query)
    total = db.scalar(select(func.count()).select_from(statement.order_by(None).subquery())) or 0
    sort_column = FitnessActivity.title if sort == "title" else FitnessActivity.updated_at
    statement = statement.order_by(sort_column.asc() if direction == "asc" else sort_column.desc(), FitnessActivity.title.asc())
    return list(db.execute(_paginate(statement, page, page_size)).unique().scalars().all()), total


def list_logs(
    db: Session,
    owner_id: str,
    *,
    query: str | None = None,
    activity_id: str | None = None,
    activity_type: str | None = None,
    date_from: str | None = None,
    date_before: str | None = None,
    sort: str = "logDate",
    direction: str = "desc",
    page: int = 1,
    page_size: int = 100,
) -> tuple[list[FitnessLog], int]:
    statement = (
        select(FitnessLog)
        .join(FitnessLog.activity)
        .options(joinedload(FitnessLog.activity))
        .where(FitnessLog.owner_id == owner_id)
    )
    if activity_id:
        statement = statement.where(FitnessLog.activity_id == activity_id)
    if activity_type:
        statement = statement.where(FitnessActivity.activity_type == activity_type)
    if date_from:
        statement = statement.where(FitnessLog.log_date >= date_from)
    if date_before:
        statement = statement.where(FitnessLog.log_date < date_before)
    statement = _log_search(statement, query)
    total = db.scalar(select(func.count()).select_from(statement.order_by(None).subquery())) or 0
    sort_column = FitnessLog.updated_at if sort == "updatedAt" else FitnessLog.log_date
    statement = statement.order_by(
        sort_column.asc() if direction == "asc" else sort_column.desc(),
        FitnessLog.created_at.desc(),
    )
    return list(db.execute(_paginate(statement, page, page_size)).scalars().all()), total


def count_activities(db: Session, owner_id: str, *, status: str | None = None) -> int:
    statement = select(func.count()).select_from(FitnessActivity).where(FitnessActivity.owner_id == owner_id)
    if status:
        statement = statement.where(FitnessActivity.status == status)
    return db.scalar(statement) or 0


def count_logs(db: Session, owner_id: str) -> int:
    return db.scalar(select(func.count()).select_from(FitnessLog).where(FitnessLog.owner_id == owner_id)) or 0


def total_minutes(db: Session, owner_id: str, *, date_from: str | None = None, date_before: str | None = None) -> int:
    statement = select(func.coalesce(func.sum(FitnessLog.duration_minutes), 0)).where(FitnessLog.owner_id == owner_id)
    if date_from:
        statement = statement.where(FitnessLog.log_date >= date_from)
    if date_before:
        statement = statement.where(FitnessLog.log_date < date_before)
    return int(db.scalar(statement) or 0)


def add(db: Session, record: object) -> None:
    db.add(record)


def delete_record(db: Session, record: object) -> None:
    db.delete(record)
