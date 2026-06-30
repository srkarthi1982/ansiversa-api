from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.job_description_analyzer import repository
from app.modules.job_description_analyzer.models import AnalysisHistory, JobAnalysis, JobDescription, SkillMatch
from app.modules.job_description_analyzer.schemas import (
    AnalysisHistoryCreateRequest,
    AnalysisHistoryDetailResponse,
    AnalysisHistorySummaryResponse,
    AnalysisHistoryUpdateRequest,
    JobAnalysisCreateRequest,
    JobAnalysisDetailResponse,
    JobAnalysisSummaryResponse,
    JobAnalysisUpdateRequest,
    JobDescriptionAnalyzerDashboardResponse,
    JobDescriptionCreateRequest,
    JobDescriptionDetailResponse,
    JobDescriptionSummaryResponse,
    JobDescriptionUpdateRequest,
    SkillMatchCreateRequest,
    SkillMatchDetailResponse,
    SkillMatchSummaryResponse,
    SkillMatchUpdateRequest,
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


def _get_owned_job(db: Session, user: User, job_id: int) -> JobDescription:
    job = repository.get_job(db, job_id)
    if not job or job.owner_id != user.id:
        _not_found("Job description was not found.")
    return job


def _get_owned_analysis(db: Session, user: User, analysis_id: int) -> JobAnalysis:
    analysis = repository.get_analysis(db, analysis_id)
    if not analysis or analysis.owner_id != user.id:
        _not_found("Job analysis was not found.")
    return analysis


def _get_owned_skill(db: Session, user: User, skill_id: int) -> SkillMatch:
    skill = repository.get_skill(db, skill_id)
    if not skill or skill.owner_id != user.id:
        _not_found("Skill match was not found.")
    return skill


def _get_owned_history(db: Session, user: User, history_id: int) -> AnalysisHistory:
    history = repository.get_history(db, history_id)
    if not history or history.owner_id != user.id:
        _not_found("Analysis history record was not found.")
    return history


def _job_summary_response(db: Session, job: JobDescription) -> JobDescriptionSummaryResponse:
    return JobDescriptionSummaryResponse(
        id=job.id,
        platform_id=job.platform_id,
        title=job.title,
        company_name=job.company_name,
        location=job.location,
        employment_type=job.employment_type,
        status=job.status,
        seniority=job.seniority,
        description_preview=_preview(job.description_text),
        analysis_count=repository.count_analysis(db, job.id),
        created_at=job.created_at,
        updated_at=job.updated_at,
    )


def _job_detail_response(db: Session, job: JobDescription) -> JobDescriptionDetailResponse:
    summary = _job_summary_response(db, job)
    return JobDescriptionDetailResponse(
        **summary.model_dump(),
        source_url=job.source_url,
        description_text=job.description_text,
        notes=job.notes,
    )


def _analysis_summary_response(db: Session, analysis: JobAnalysis, job_title: str) -> JobAnalysisSummaryResponse:
    return JobAnalysisSummaryResponse(
        id=analysis.id,
        platform_id=analysis.platform_id,
        job_description_id=analysis.job_description_id,
        job_title=job_title,
        title=analysis.title,
        status=analysis.status,
        match_score=analysis.match_score,
        summary_preview=_preview(analysis.summary),
        skill_count=repository.count_skills(db, analysis.id),
        history_count=repository.count_history(db, analysis.id),
        created_at=analysis.created_at,
        updated_at=analysis.updated_at,
    )


def _analysis_detail_response(db: Session, analysis: JobAnalysis, job_title: str) -> JobAnalysisDetailResponse:
    summary = _analysis_summary_response(db, analysis, job_title)
    return JobAnalysisDetailResponse(
        **summary.model_dump(),
        summary=analysis.summary,
        keywords=analysis.keywords,
        responsibilities=analysis.responsibilities,
        recommendations=analysis.recommendations,
    )


def _skill_summary_response(skill: SkillMatch, analysis_title: str) -> SkillMatchSummaryResponse:
    return SkillMatchSummaryResponse(
        id=skill.id,
        platform_id=skill.platform_id,
        analysis_id=skill.analysis_id,
        analysis_title=analysis_title,
        skill_name=skill.skill_name,
        category=skill.category,
        match_level=skill.match_level,
        evidence_preview=_preview(skill.evidence),
        created_at=skill.created_at,
        updated_at=skill.updated_at,
    )


def _skill_detail_response(skill: SkillMatch, analysis_title: str) -> SkillMatchDetailResponse:
    summary = _skill_summary_response(skill, analysis_title)
    return SkillMatchDetailResponse(
        **summary.model_dump(),
        evidence=skill.evidence,
        recommendation=skill.recommendation,
    )


def _history_summary_response(history: AnalysisHistory, analysis_title: str) -> AnalysisHistorySummaryResponse:
    return AnalysisHistorySummaryResponse(
        id=history.id,
        platform_id=history.platform_id,
        analysis_id=history.analysis_id,
        analysis_title=analysis_title,
        title=history.title,
        event_type=history.event_type,
        occurred_at=history.occurred_at,
        summary_preview=_preview(history.summary),
        next_steps_preview=_preview(history.next_steps),
        created_at=history.created_at,
        updated_at=history.updated_at,
    )


def _history_detail_response(history: AnalysisHistory, analysis_title: str) -> AnalysisHistoryDetailResponse:
    summary = _history_summary_response(history, analysis_title)
    return AnalysisHistoryDetailResponse(
        **summary.model_dump(),
        summary=history.summary,
        next_steps=history.next_steps,
    )


def list_jobs(db: Session, user: User) -> list[JobDescriptionSummaryResponse]:
    return [_job_summary_response(db, job) for job in repository.list_jobs(db, user.id)]


def create_job(db: Session, user: User, payload: JobDescriptionCreateRequest) -> JobDescriptionDetailResponse:
    job = JobDescription(owner_id=user.id, **payload.model_dump())
    repository.add(db, job)
    db.commit()
    db.refresh(job)
    return _job_detail_response(db, job)


def get_job(db: Session, user: User, job_id: int) -> JobDescriptionDetailResponse:
    return _job_detail_response(db, _get_owned_job(db, user, job_id))


def update_job(db: Session, user: User, job_id: int, payload: JobDescriptionUpdateRequest) -> JobDescriptionDetailResponse:
    job = _get_owned_job(db, user, job_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(job, field, value)
    db.commit()
    db.refresh(job)
    return _job_detail_response(db, job)


def delete_job(db: Session, user: User, job_id: int) -> None:
    job = _get_owned_job(db, user, job_id)
    repository.delete_job_children(db, job.id)
    repository.delete_record(db, job)
    db.commit()


def list_analysis(db: Session, user: User) -> list[JobAnalysisSummaryResponse]:
    return [
        _analysis_summary_response(db, analysis, job.title)
        for analysis, job in repository.list_analysis(db, user.id)
    ]


def create_analysis(db: Session, user: User, payload: JobAnalysisCreateRequest) -> JobAnalysisDetailResponse:
    job = _get_owned_job(db, user, payload.job_description_id)
    analysis = JobAnalysis(owner_id=user.id, **payload.model_dump())
    repository.add(db, analysis)
    db.commit()
    db.refresh(analysis)
    return _analysis_detail_response(db, analysis, job.title)


def get_analysis(db: Session, user: User, analysis_id: int) -> JobAnalysisDetailResponse:
    analysis = _get_owned_analysis(db, user, analysis_id)
    job = _get_owned_job(db, user, analysis.job_description_id)
    return _analysis_detail_response(db, analysis, job.title)


def update_analysis(db: Session, user: User, analysis_id: int, payload: JobAnalysisUpdateRequest) -> JobAnalysisDetailResponse:
    analysis = _get_owned_analysis(db, user, analysis_id)
    job = _get_owned_job(db, user, analysis.job_description_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(analysis, field, value)
    db.commit()
    db.refresh(analysis)
    return _analysis_detail_response(db, analysis, job.title)


def delete_analysis(db: Session, user: User, analysis_id: int) -> None:
    analysis = _get_owned_analysis(db, user, analysis_id)
    repository.delete_analysis_children(db, analysis.id)
    repository.delete_record(db, analysis)
    db.commit()


def list_skills(db: Session, user: User) -> list[SkillMatchSummaryResponse]:
    return [
        _skill_summary_response(skill, analysis.title)
        for skill, analysis in repository.list_skills(db, user.id)
    ]


def create_skill(db: Session, user: User, payload: SkillMatchCreateRequest) -> SkillMatchDetailResponse:
    analysis = _get_owned_analysis(db, user, payload.analysis_id)
    skill = SkillMatch(owner_id=user.id, **payload.model_dump())
    repository.add(db, skill)
    db.commit()
    db.refresh(skill)
    return _skill_detail_response(skill, analysis.title)


def get_skill(db: Session, user: User, skill_id: int) -> SkillMatchDetailResponse:
    skill = _get_owned_skill(db, user, skill_id)
    analysis = _get_owned_analysis(db, user, skill.analysis_id)
    return _skill_detail_response(skill, analysis.title)


def update_skill(db: Session, user: User, skill_id: int, payload: SkillMatchUpdateRequest) -> SkillMatchDetailResponse:
    skill = _get_owned_skill(db, user, skill_id)
    analysis = _get_owned_analysis(db, user, skill.analysis_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(skill, field, value)
    db.commit()
    db.refresh(skill)
    return _skill_detail_response(skill, analysis.title)


def delete_skill(db: Session, user: User, skill_id: int) -> None:
    skill = _get_owned_skill(db, user, skill_id)
    repository.delete_record(db, skill)
    db.commit()


def list_history(db: Session, user: User) -> list[AnalysisHistorySummaryResponse]:
    return [
        _history_summary_response(history, analysis.title)
        for history, analysis in repository.list_history(db, user.id)
    ]


def create_history(db: Session, user: User, payload: AnalysisHistoryCreateRequest) -> AnalysisHistoryDetailResponse:
    analysis = _get_owned_analysis(db, user, payload.analysis_id)
    history = AnalysisHistory(owner_id=user.id, **payload.model_dump())
    repository.add(db, history)
    db.commit()
    db.refresh(history)
    return _history_detail_response(history, analysis.title)


def get_history(db: Session, user: User, history_id: int) -> AnalysisHistoryDetailResponse:
    history = _get_owned_history(db, user, history_id)
    analysis = _get_owned_analysis(db, user, history.analysis_id)
    return _history_detail_response(history, analysis.title)


def update_history(db: Session, user: User, history_id: int, payload: AnalysisHistoryUpdateRequest) -> AnalysisHistoryDetailResponse:
    history = _get_owned_history(db, user, history_id)
    analysis = _get_owned_analysis(db, user, history.analysis_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(history, field, value)
    db.commit()
    db.refresh(history)
    return _history_detail_response(history, analysis.title)


def delete_history(db: Session, user: User, history_id: int) -> None:
    history = _get_owned_history(db, user, history_id)
    repository.delete_record(db, history)
    db.commit()


def get_dashboard(db: Session, user: User) -> JobDescriptionAnalyzerDashboardResponse:
    jobs = list_jobs(db, user)
    analysis = list_analysis(db, user)
    skills = list_skills(db, user)
    history = list_history(db, user)
    return JobDescriptionAnalyzerDashboardResponse(
        jobs=jobs,
        analysis=analysis,
        skills=skills,
        history=history,
        job_count=len(jobs),
        analysis_count=len(analysis),
        skill_count=len(skills),
        history_count=len(history),
        reviewed_job_count=sum(1 for item in jobs if item.status == "reviewed"),
        strong_skill_count=sum(1 for item in skills if item.match_level == "strong"),
    )
