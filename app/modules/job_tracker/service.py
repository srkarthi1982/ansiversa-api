from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.job_tracker import repository
from app.modules.job_tracker.models import (
    ApplicationHistory,
    ApplicationInsight,
    JobApplication,
    JobListing,
)
from app.modules.job_tracker.schemas import (
    ApplicationHistoryCreateRequest,
    ApplicationHistoryDetailResponse,
    ApplicationHistorySummaryResponse,
    ApplicationInsightCreateRequest,
    ApplicationInsightDetailResponse,
    ApplicationInsightSummaryResponse,
    ApplicationInsightUpdateRequest,
    JobApplicationCreateRequest,
    JobApplicationDetailResponse,
    JobApplicationSummaryResponse,
    JobApplicationUpdateRequest,
    JobListingCreateRequest,
    JobListingDetailResponse,
    JobListingSummaryResponse,
    JobListingUpdateRequest,
    JobTrackerDashboardResponse,
)

PREVIEW_LENGTH = 220
ACTIVE_APPLICATION_STATUSES = {"applied", "screening", "interviewing", "offer"}


def _preview(value: str | None) -> str | None:
    if not value:
        return None
    if len(value) <= PREVIEW_LENGTH:
        return value
    return f"{value[:PREVIEW_LENGTH].rstrip()}..."


def _not_found(detail: str) -> None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def _application_title(application: JobApplication) -> str:
    return f"{application.role_title} at {application.company_name}"


def _get_owned_job(db: Session, user: User, job_id: int) -> JobListing:
    job = repository.get_job(db, job_id)
    if not job or job.owner_id != user.id:
        _not_found("Job listing was not found.")
    return job


def _get_owned_application(db: Session, user: User, application_id: int) -> JobApplication:
    application = repository.get_application(db, application_id)
    if not application or application.owner_id != user.id:
        _not_found("Job application was not found.")
    return application


def _get_owned_insight(db: Session, user: User, insight_id: int) -> ApplicationInsight:
    insight = repository.get_insight(db, insight_id)
    if not insight or insight.owner_id != user.id:
        _not_found("Application insight was not found.")
    return insight


def _get_owned_history(db: Session, user: User, history_id: int) -> ApplicationHistory:
    history = repository.get_history(db, history_id)
    if not history or history.owner_id != user.id:
        _not_found("Application history record was not found.")
    return history


def _job_summary_response(db: Session, job: JobListing) -> JobListingSummaryResponse:
    return JobListingSummaryResponse(
        id=job.id,
        platform_id=job.platform_id,
        title=job.title,
        company_name=job.company_name,
        location=job.location,
        employment_type=job.employment_type,
        status=job.status,
        priority=job.priority,
        salary_range=job.salary_range,
        description_preview=_preview(job.description),
        application_count=repository.count_applications(db, job.id),
        created_at=job.created_at,
        updated_at=job.updated_at,
    )


def _job_detail_response(db: Session, job: JobListing) -> JobListingDetailResponse:
    summary = _job_summary_response(db, job)
    return JobListingDetailResponse(
        **summary.model_dump(),
        source_url=job.source_url,
        description=job.description,
        notes=job.notes,
    )


def _application_summary_response(
    db: Session,
    application: JobApplication,
    job_title: str,
) -> JobApplicationSummaryResponse:
    return JobApplicationSummaryResponse(
        id=application.id,
        platform_id=application.platform_id,
        job_id=application.job_id,
        job_title=job_title,
        role_title=application.role_title,
        company_name=application.company_name,
        status=application.status,
        applied_at=application.applied_at,
        follow_up_date=application.follow_up_date,
        contact_name=application.contact_name,
        insight_count=repository.count_insights(db, application.id),
        history_count=repository.count_history(db, application.id),
        created_at=application.created_at,
        updated_at=application.updated_at,
    )


def _application_detail_response(
    db: Session,
    application: JobApplication,
    job_title: str,
) -> JobApplicationDetailResponse:
    summary = _application_summary_response(db, application, job_title)
    return JobApplicationDetailResponse(
        **summary.model_dump(),
        contact_email=application.contact_email,
        resume_version=application.resume_version,
        cover_letter_version=application.cover_letter_version,
        notes=application.notes,
    )


def _insight_summary_response(
    insight: ApplicationInsight,
    application_title: str,
) -> ApplicationInsightSummaryResponse:
    return ApplicationInsightSummaryResponse(
        id=insight.id,
        platform_id=insight.platform_id,
        application_id=insight.application_id,
        application_title=application_title,
        title=insight.title,
        category=insight.category,
        priority=insight.priority,
        status=insight.status,
        recommendation_preview=_preview(insight.recommendation),
        created_at=insight.created_at,
        updated_at=insight.updated_at,
    )


def _insight_detail_response(
    insight: ApplicationInsight,
    application_title: str,
) -> ApplicationInsightDetailResponse:
    summary = _insight_summary_response(insight, application_title)
    return ApplicationInsightDetailResponse(
        **summary.model_dump(),
        recommendation=insight.recommendation,
        notes=insight.notes,
    )


def _history_summary_response(
    history: ApplicationHistory,
    application_title: str,
) -> ApplicationHistorySummaryResponse:
    return ApplicationHistorySummaryResponse(
        id=history.id,
        platform_id=history.platform_id,
        application_id=history.application_id,
        application_title=application_title,
        title=history.title,
        event_type=history.event_type,
        occurred_at=history.occurred_at,
        summary_preview=_preview(history.summary),
        next_steps_preview=_preview(history.next_steps),
        created_at=history.created_at,
        updated_at=history.updated_at,
    )


def _history_detail_response(
    history: ApplicationHistory,
    application_title: str,
) -> ApplicationHistoryDetailResponse:
    summary = _history_summary_response(history, application_title)
    return ApplicationHistoryDetailResponse(
        **summary.model_dump(),
        summary=history.summary,
        next_steps=history.next_steps,
    )


def list_jobs(db: Session, user: User) -> list[JobListingSummaryResponse]:
    return [_job_summary_response(db, job) for job in repository.list_jobs(db, user.id)]


def create_job(db: Session, user: User, payload: JobListingCreateRequest) -> JobListingDetailResponse:
    job = JobListing(owner_id=user.id, **payload.model_dump())
    repository.add(db, job)
    db.commit()
    db.refresh(job)
    return _job_detail_response(db, job)


def get_job(db: Session, user: User, job_id: int) -> JobListingDetailResponse:
    return _job_detail_response(db, _get_owned_job(db, user, job_id))


def update_job(db: Session, user: User, job_id: int, payload: JobListingUpdateRequest) -> JobListingDetailResponse:
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


def list_applications(db: Session, user: User) -> list[JobApplicationSummaryResponse]:
    return [
        _application_summary_response(db, application, job.title)
        for application, job in repository.list_applications(db, user.id)
    ]


def create_application(db: Session, user: User, payload: JobApplicationCreateRequest) -> JobApplicationDetailResponse:
    job = _get_owned_job(db, user, payload.job_id)
    application = JobApplication(owner_id=user.id, **payload.model_dump())
    repository.add(db, application)
    db.commit()
    db.refresh(application)
    return _application_detail_response(db, application, job.title)


def get_application(db: Session, user: User, application_id: int) -> JobApplicationDetailResponse:
    application = _get_owned_application(db, user, application_id)
    job = _get_owned_job(db, user, application.job_id)
    return _application_detail_response(db, application, job.title)


def update_application(db: Session, user: User, application_id: int, payload: JobApplicationUpdateRequest) -> JobApplicationDetailResponse:
    application = _get_owned_application(db, user, application_id)
    data = payload.model_dump(exclude_unset=True)
    job = _get_owned_job(db, user, application.job_id)
    for field, value in data.items():
        setattr(application, field, value)
    db.commit()
    db.refresh(application)
    return _application_detail_response(db, application, job.title)


def delete_application(db: Session, user: User, application_id: int) -> None:
    application = _get_owned_application(db, user, application_id)
    repository.delete_application_children(db, application.id)
    repository.delete_record(db, application)
    db.commit()


def list_insights(db: Session, user: User) -> list[ApplicationInsightSummaryResponse]:
    return [
        _insight_summary_response(insight, _application_title(application))
        for insight, application in repository.list_insights(db, user.id)
    ]


def create_insight(db: Session, user: User, payload: ApplicationInsightCreateRequest) -> ApplicationInsightDetailResponse:
    application = _get_owned_application(db, user, payload.application_id)
    insight = ApplicationInsight(owner_id=user.id, **payload.model_dump())
    repository.add(db, insight)
    db.commit()
    db.refresh(insight)
    return _insight_detail_response(insight, _application_title(application))


def get_insight(db: Session, user: User, insight_id: int) -> ApplicationInsightDetailResponse:
    insight = _get_owned_insight(db, user, insight_id)
    application = _get_owned_application(db, user, insight.application_id)
    return _insight_detail_response(insight, _application_title(application))


def update_insight(db: Session, user: User, insight_id: int, payload: ApplicationInsightUpdateRequest) -> ApplicationInsightDetailResponse:
    insight = _get_owned_insight(db, user, insight_id)
    data = payload.model_dump(exclude_unset=True)
    application = _get_owned_application(db, user, insight.application_id)
    for field, value in data.items():
        setattr(insight, field, value)
    db.commit()
    db.refresh(insight)
    return _insight_detail_response(insight, _application_title(application))


def delete_insight(db: Session, user: User, insight_id: int) -> None:
    insight = _get_owned_insight(db, user, insight_id)
    repository.delete_record(db, insight)
    db.commit()


def list_history(db: Session, user: User) -> list[ApplicationHistorySummaryResponse]:
    return [
        _history_summary_response(history, _application_title(application))
        for history, application in repository.list_history(db, user.id)
    ]


def create_history(db: Session, user: User, payload: ApplicationHistoryCreateRequest) -> ApplicationHistoryDetailResponse:
    application = _get_owned_application(db, user, payload.application_id)
    history = ApplicationHistory(owner_id=user.id, **payload.model_dump())
    repository.add(db, history)
    db.commit()
    db.refresh(history)
    return _history_detail_response(history, _application_title(application))


def get_history(db: Session, user: User, history_id: int) -> ApplicationHistoryDetailResponse:
    history = _get_owned_history(db, user, history_id)
    application = _get_owned_application(db, user, history.application_id)
    return _history_detail_response(history, _application_title(application))


def delete_history(db: Session, user: User, history_id: int) -> None:
    history = _get_owned_history(db, user, history_id)
    repository.delete_record(db, history)
    db.commit()


def get_dashboard(db: Session, user: User) -> JobTrackerDashboardResponse:
    jobs = list_jobs(db, user)
    applications = list_applications(db, user)
    insights = list_insights(db, user)
    history = list_history(db, user)
    return JobTrackerDashboardResponse(
        jobs=jobs,
        applications=applications,
        insights=insights,
        history=history,
        job_count=len(jobs),
        application_count=len(applications),
        insight_count=len(insights),
        history_count=len(history),
        active_application_count=sum(1 for item in applications if item.status in ACTIVE_APPLICATION_STATUSES),
        urgent_insight_count=sum(1 for item in insights if item.priority == "urgent"),
    )
