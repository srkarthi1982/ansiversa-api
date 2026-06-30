from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.modules.job_tracker.models import (
    ApplicationHistory,
    ApplicationInsight,
    JobApplication,
    JobListing,
)


def get_job(db: Session, job_id: int) -> JobListing | None:
    return db.get(JobListing, job_id)


def get_application(db: Session, application_id: int) -> JobApplication | None:
    return db.get(JobApplication, application_id)


def get_insight(db: Session, insight_id: int) -> ApplicationInsight | None:
    return db.get(ApplicationInsight, insight_id)


def get_history(db: Session, history_id: int) -> ApplicationHistory | None:
    return db.get(ApplicationHistory, history_id)


def list_jobs(db: Session, owner_id: str) -> list[JobListing]:
    return list(
        db.execute(
            select(JobListing)
            .where(JobListing.owner_id == owner_id)
            .order_by(JobListing.updated_at.desc(), JobListing.company_name.asc(), JobListing.title.asc())
        )
        .scalars()
        .all()
    )


def list_applications(db: Session, owner_id: str) -> list[tuple[JobApplication, JobListing]]:
    return list(
        db.execute(
            select(JobApplication, JobListing)
            .join(JobListing, JobListing.id == JobApplication.job_id)
            .where(JobApplication.owner_id == owner_id)
            .order_by(JobApplication.updated_at.desc(), JobApplication.company_name.asc())
        ).all()
    )


def list_insights(db: Session, owner_id: str) -> list[tuple[ApplicationInsight, JobApplication]]:
    return list(
        db.execute(
            select(ApplicationInsight, JobApplication)
            .join(JobApplication, JobApplication.id == ApplicationInsight.application_id)
            .where(ApplicationInsight.owner_id == owner_id)
            .order_by(ApplicationInsight.updated_at.desc(), ApplicationInsight.priority.desc())
        ).all()
    )


def list_history(db: Session, owner_id: str) -> list[tuple[ApplicationHistory, JobApplication]]:
    return list(
        db.execute(
            select(ApplicationHistory, JobApplication)
            .join(JobApplication, JobApplication.id == ApplicationHistory.application_id)
            .where(ApplicationHistory.owner_id == owner_id)
            .order_by(ApplicationHistory.updated_at.desc(), ApplicationHistory.occurred_at.desc())
        ).all()
    )


def count_applications(db: Session, job_id: int) -> int:
    return int(db.execute(select(func.count()).select_from(JobApplication).where(JobApplication.job_id == job_id)).scalar_one())


def count_insights(db: Session, application_id: int) -> int:
    return int(db.execute(select(func.count()).select_from(ApplicationInsight).where(ApplicationInsight.application_id == application_id)).scalar_one())


def count_history(db: Session, application_id: int) -> int:
    return int(db.execute(select(func.count()).select_from(ApplicationHistory).where(ApplicationHistory.application_id == application_id)).scalar_one())


def add(db: Session, record: object) -> None:
    db.add(record)


def delete_record(db: Session, record: object) -> None:
    db.delete(record)


def delete_job_children(db: Session, job_id: int) -> None:
    application_ids = list(db.execute(select(JobApplication.id).where(JobApplication.job_id == job_id)).scalars().all())
    if application_ids:
        db.execute(delete(ApplicationInsight).where(ApplicationInsight.application_id.in_(application_ids)))
        db.execute(delete(ApplicationHistory).where(ApplicationHistory.application_id.in_(application_ids)))
    db.execute(delete(JobApplication).where(JobApplication.job_id == job_id))


def delete_application_children(db: Session, application_id: int) -> None:
    db.execute(delete(ApplicationInsight).where(ApplicationInsight.application_id == application_id))
    db.execute(delete(ApplicationHistory).where(ApplicationHistory.application_id == application_id))
