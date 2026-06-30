from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.modules.job_description_analyzer.models import (
    AnalysisHistory,
    JobAnalysis,
    JobDescription,
    SkillMatch,
)


def get_job(db: Session, job_id: int) -> JobDescription | None:
    return db.get(JobDescription, job_id)


def get_analysis(db: Session, analysis_id: int) -> JobAnalysis | None:
    return db.get(JobAnalysis, analysis_id)


def get_skill(db: Session, skill_id: int) -> SkillMatch | None:
    return db.get(SkillMatch, skill_id)


def get_history(db: Session, history_id: int) -> AnalysisHistory | None:
    return db.get(AnalysisHistory, history_id)


def list_jobs(db: Session, owner_id: str) -> list[JobDescription]:
    return list(
        db.execute(
            select(JobDescription)
            .where(JobDescription.owner_id == owner_id)
            .order_by(JobDescription.updated_at.desc(), JobDescription.company_name.asc(), JobDescription.title.asc())
        )
        .scalars()
        .all()
    )


def list_analysis(db: Session, owner_id: str) -> list[tuple[JobAnalysis, JobDescription]]:
    return list(
        db.execute(
            select(JobAnalysis, JobDescription)
            .join(JobDescription, JobDescription.id == JobAnalysis.job_description_id)
            .where(JobAnalysis.owner_id == owner_id)
            .order_by(JobAnalysis.updated_at.desc(), JobAnalysis.match_score.desc())
        ).all()
    )


def list_skills(db: Session, owner_id: str) -> list[tuple[SkillMatch, JobAnalysis]]:
    return list(
        db.execute(
            select(SkillMatch, JobAnalysis)
            .join(JobAnalysis, JobAnalysis.id == SkillMatch.analysis_id)
            .where(SkillMatch.owner_id == owner_id)
            .order_by(SkillMatch.updated_at.desc(), SkillMatch.skill_name.asc())
        ).all()
    )


def list_history(db: Session, owner_id: str) -> list[tuple[AnalysisHistory, JobAnalysis]]:
    return list(
        db.execute(
            select(AnalysisHistory, JobAnalysis)
            .join(JobAnalysis, JobAnalysis.id == AnalysisHistory.analysis_id)
            .where(AnalysisHistory.owner_id == owner_id)
            .order_by(AnalysisHistory.updated_at.desc(), AnalysisHistory.occurred_at.desc())
        ).all()
    )


def count_analysis(db: Session, job_id: int) -> int:
    return int(db.execute(select(func.count()).select_from(JobAnalysis).where(JobAnalysis.job_description_id == job_id)).scalar_one())


def count_skills(db: Session, analysis_id: int) -> int:
    return int(db.execute(select(func.count()).select_from(SkillMatch).where(SkillMatch.analysis_id == analysis_id)).scalar_one())


def count_history(db: Session, analysis_id: int) -> int:
    return int(db.execute(select(func.count()).select_from(AnalysisHistory).where(AnalysisHistory.analysis_id == analysis_id)).scalar_one())


def add(db: Session, record: object) -> None:
    db.add(record)


def delete_record(db: Session, record: object) -> None:
    db.delete(record)


def delete_job_children(db: Session, job_id: int) -> None:
    analysis_ids = list(db.execute(select(JobAnalysis.id).where(JobAnalysis.job_description_id == job_id)).scalars().all())
    if analysis_ids:
        db.execute(delete(SkillMatch).where(SkillMatch.analysis_id.in_(analysis_ids)))
        db.execute(delete(AnalysisHistory).where(AnalysisHistory.analysis_id.in_(analysis_ids)))
    db.execute(delete(JobAnalysis).where(JobAnalysis.job_description_id == job_id))


def delete_analysis_children(db: Session, analysis_id: int) -> None:
    db.execute(delete(SkillMatch).where(SkillMatch.analysis_id == analysis_id))
    db.execute(delete(AnalysisHistory).where(AnalysisHistory.analysis_id == analysis_id))
