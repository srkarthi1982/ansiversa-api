from sqlalchemy import update
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import select

from app.modules.wellness_and_goal_planner.models import WellnessArea, WellnessGoal, WellnessReflection


def get_area(db: Session, area_id: int) -> WellnessArea | None:
    return db.get(WellnessArea, area_id)


def get_goal(db: Session, goal_id: int) -> WellnessGoal | None:
    return db.get(WellnessGoal, goal_id)


def get_reflection(db: Session, reflection_id: int) -> WellnessReflection | None:
    return db.get(WellnessReflection, reflection_id)


def list_areas(db: Session, owner_id: str) -> list[WellnessArea]:
    return list(
        db.execute(
            select(WellnessArea)
            .where(WellnessArea.owner_id == owner_id)
            .order_by(WellnessArea.name.asc(), WellnessArea.updated_at.desc())
        )
        .scalars()
        .all()
    )


def list_goals(db: Session, owner_id: str) -> list[WellnessGoal]:
    return list(
        db.execute(
            select(WellnessGoal)
            .options(joinedload(WellnessGoal.area), joinedload(WellnessGoal.reflections))
            .where(WellnessGoal.owner_id == owner_id)
            .order_by(WellnessGoal.updated_at.desc(), WellnessGoal.title.asc())
        )
        .unique()
        .scalars()
        .all()
    )


def list_reflections(db: Session, owner_id: str) -> list[WellnessReflection]:
    return list(
        db.execute(
            select(WellnessReflection)
            .options(joinedload(WellnessReflection.goal))
            .where(WellnessReflection.owner_id == owner_id)
            .order_by(WellnessReflection.reflection_date.desc(), WellnessReflection.created_at.desc())
        )
        .scalars()
        .all()
    )


def add(db: Session, record: object) -> None:
    db.add(record)


def delete_record(db: Session, record: object) -> None:
    db.delete(record)


def detach_area_from_goals(db: Session, owner_id: str, area_id: int) -> None:
    db.execute(
        update(WellnessGoal)
        .where(WellnessGoal.owner_id == owner_id, WellnessGoal.area_id == area_id)
        .values(area_id=None)
    )


def detach_goal_from_reflections(db: Session, owner_id: str, goal_id: int) -> None:
    db.execute(
        update(WellnessReflection)
        .where(WellnessReflection.owner_id == owner_id, WellnessReflection.goal_id == goal_id)
        .values(goal_id=None)
    )
