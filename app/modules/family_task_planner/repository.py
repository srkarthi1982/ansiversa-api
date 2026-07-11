from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import select

from app.modules.family_task_planner.models import FamilyTask, FamilyTaskCategory, FamilyTaskMember


def get_member(db: Session, member_id: str) -> FamilyTaskMember | None:
    return db.get(FamilyTaskMember, member_id)


def get_category(db: Session, category_id: str) -> FamilyTaskCategory | None:
    return db.get(FamilyTaskCategory, category_id)


def get_task(db: Session, task_id: str) -> FamilyTask | None:
    return db.get(FamilyTask, task_id)


def list_members(db: Session, owner_id: str) -> list[FamilyTaskMember]:
    return list(
        db.execute(
            select(FamilyTaskMember)
            .options(joinedload(FamilyTaskMember.tasks))
            .where(FamilyTaskMember.owner_id == owner_id)
            .order_by(FamilyTaskMember.status.asc(), FamilyTaskMember.name.asc())
        )
        .unique()
        .scalars()
        .all()
    )


def list_categories(db: Session, owner_id: str) -> list[FamilyTaskCategory]:
    return list(
        db.execute(
            select(FamilyTaskCategory)
            .options(joinedload(FamilyTaskCategory.tasks))
            .where(FamilyTaskCategory.owner_id == owner_id)
            .order_by(FamilyTaskCategory.status.asc(), FamilyTaskCategory.name.asc())
        )
        .unique()
        .scalars()
        .all()
    )


def list_tasks(db: Session, owner_id: str) -> list[FamilyTask]:
    return list(
        db.execute(
            select(FamilyTask)
            .options(joinedload(FamilyTask.member), joinedload(FamilyTask.category))
            .where(FamilyTask.owner_id == owner_id)
            .order_by(FamilyTask.due_date.asc(), FamilyTask.updated_at.desc())
        )
        .unique()
        .scalars()
        .all()
    )


def add(db: Session, record: object) -> None:
    db.add(record)


def delete_record(db: Session, record: object) -> None:
    db.delete(record)
