from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import select

from app.modules.goal_tracker.models import GoalTrackerCheckIn, GoalTrackerGoal, GoalTrackerMilestone


def get_goal(db: Session, goal_id: str) -> GoalTrackerGoal | None:
    return db.get(GoalTrackerGoal, goal_id)


def get_milestone(db: Session, milestone_id: str) -> GoalTrackerMilestone | None:
    return db.get(GoalTrackerMilestone, milestone_id)


def get_check_in(db: Session, check_in_id: str) -> GoalTrackerCheckIn | None:
    return db.get(GoalTrackerCheckIn, check_in_id)


def list_goals(db: Session, owner_id: str) -> list[GoalTrackerGoal]:
    return list(
        db.execute(
            select(GoalTrackerGoal)
            .options(joinedload(GoalTrackerGoal.milestones), joinedload(GoalTrackerGoal.check_ins))
            .where(GoalTrackerGoal.owner_id == owner_id)
            .order_by(GoalTrackerGoal.updated_at.desc(), GoalTrackerGoal.title.asc())
        )
        .unique()
        .scalars()
        .all()
    )


def list_milestones(db: Session, owner_id: str) -> list[GoalTrackerMilestone]:
    return list(
        db.execute(
            select(GoalTrackerMilestone)
            .options(joinedload(GoalTrackerMilestone.goal))
            .where(GoalTrackerMilestone.owner_id == owner_id)
            .order_by(GoalTrackerMilestone.sort_order.asc(), GoalTrackerMilestone.updated_at.desc())
        )
        .scalars()
        .all()
    )


def list_check_ins(db: Session, owner_id: str) -> list[GoalTrackerCheckIn]:
    return list(
        db.execute(
            select(GoalTrackerCheckIn)
            .options(joinedload(GoalTrackerCheckIn.goal))
            .where(GoalTrackerCheckIn.owner_id == owner_id)
            .order_by(GoalTrackerCheckIn.check_in_date.desc(), GoalTrackerCheckIn.created_at.desc())
        )
        .scalars()
        .all()
    )


def add(db: Session, record: object) -> None:
    db.add(record)


def delete_record(db: Session, record: object) -> None:
    db.delete(record)
