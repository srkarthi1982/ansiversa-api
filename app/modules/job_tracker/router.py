from typing import Annotated

from fastapi import APIRouter, Path, status

from app.modules.job_tracker.dependencies import CurrentUser, JobTrackerDb
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
from app.modules.job_tracker.service import (
    create_application,
    create_history,
    create_insight,
    create_job,
    delete_application,
    delete_history,
    delete_insight,
    delete_job,
    get_application,
    get_dashboard,
    get_history,
    get_insight,
    get_job,
    list_applications,
    list_history,
    list_insights,
    list_jobs,
    update_application,
    update_insight,
    update_job,
)

router = APIRouter()


@router.get("/dashboard", response_model=JobTrackerDashboardResponse)
def get_job_tracker_dashboard(current_user: CurrentUser, db: JobTrackerDb) -> JobTrackerDashboardResponse:
    return get_dashboard(db, current_user)


@router.post("/jobs", response_model=JobListingDetailResponse, status_code=status.HTTP_201_CREATED)
def create_job_listing(payload: JobListingCreateRequest, current_user: CurrentUser, db: JobTrackerDb) -> JobListingDetailResponse:
    return create_job(db, current_user, payload)


@router.get("/jobs", response_model=list[JobListingSummaryResponse])
def list_job_listings(current_user: CurrentUser, db: JobTrackerDb) -> list[JobListingSummaryResponse]:
    return list_jobs(db, current_user)


@router.get("/jobs/{job_id}", response_model=JobListingDetailResponse)
def get_job_listing(job_id: Annotated[int, Path(gt=0)], current_user: CurrentUser, db: JobTrackerDb) -> JobListingDetailResponse:
    return get_job(db, current_user, job_id)


@router.put("/jobs/{job_id}", response_model=JobListingDetailResponse)
def update_job_listing(job_id: Annotated[int, Path(gt=0)], payload: JobListingUpdateRequest, current_user: CurrentUser, db: JobTrackerDb) -> JobListingDetailResponse:
    return update_job(db, current_user, job_id, payload)


@router.delete("/jobs/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job_listing(job_id: Annotated[int, Path(gt=0)], current_user: CurrentUser, db: JobTrackerDb) -> None:
    delete_job(db, current_user, job_id)


@router.post("/applications", response_model=JobApplicationDetailResponse, status_code=status.HTTP_201_CREATED)
def create_job_application(payload: JobApplicationCreateRequest, current_user: CurrentUser, db: JobTrackerDb) -> JobApplicationDetailResponse:
    return create_application(db, current_user, payload)


@router.get("/applications", response_model=list[JobApplicationSummaryResponse])
def list_job_applications(current_user: CurrentUser, db: JobTrackerDb) -> list[JobApplicationSummaryResponse]:
    return list_applications(db, current_user)


@router.get("/applications/{application_id}", response_model=JobApplicationDetailResponse)
def get_job_application(application_id: Annotated[int, Path(gt=0)], current_user: CurrentUser, db: JobTrackerDb) -> JobApplicationDetailResponse:
    return get_application(db, current_user, application_id)


@router.put("/applications/{application_id}", response_model=JobApplicationDetailResponse)
def update_job_application(application_id: Annotated[int, Path(gt=0)], payload: JobApplicationUpdateRequest, current_user: CurrentUser, db: JobTrackerDb) -> JobApplicationDetailResponse:
    return update_application(db, current_user, application_id, payload)


@router.delete("/applications/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job_application(application_id: Annotated[int, Path(gt=0)], current_user: CurrentUser, db: JobTrackerDb) -> None:
    delete_application(db, current_user, application_id)


@router.post("/insights", response_model=ApplicationInsightDetailResponse, status_code=status.HTTP_201_CREATED)
def create_application_insight(payload: ApplicationInsightCreateRequest, current_user: CurrentUser, db: JobTrackerDb) -> ApplicationInsightDetailResponse:
    return create_insight(db, current_user, payload)


@router.get("/insights", response_model=list[ApplicationInsightSummaryResponse])
def list_application_insights(current_user: CurrentUser, db: JobTrackerDb) -> list[ApplicationInsightSummaryResponse]:
    return list_insights(db, current_user)


@router.get("/insights/{insight_id}", response_model=ApplicationInsightDetailResponse)
def get_application_insight(insight_id: Annotated[int, Path(gt=0)], current_user: CurrentUser, db: JobTrackerDb) -> ApplicationInsightDetailResponse:
    return get_insight(db, current_user, insight_id)


@router.put("/insights/{insight_id}", response_model=ApplicationInsightDetailResponse)
def update_application_insight(insight_id: Annotated[int, Path(gt=0)], payload: ApplicationInsightUpdateRequest, current_user: CurrentUser, db: JobTrackerDb) -> ApplicationInsightDetailResponse:
    return update_insight(db, current_user, insight_id, payload)


@router.delete("/insights/{insight_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application_insight(insight_id: Annotated[int, Path(gt=0)], current_user: CurrentUser, db: JobTrackerDb) -> None:
    delete_insight(db, current_user, insight_id)


@router.post("/history", response_model=ApplicationHistoryDetailResponse, status_code=status.HTTP_201_CREATED)
def create_application_history(payload: ApplicationHistoryCreateRequest, current_user: CurrentUser, db: JobTrackerDb) -> ApplicationHistoryDetailResponse:
    return create_history(db, current_user, payload)


@router.get("/history", response_model=list[ApplicationHistorySummaryResponse])
def list_application_history(current_user: CurrentUser, db: JobTrackerDb) -> list[ApplicationHistorySummaryResponse]:
    return list_history(db, current_user)


@router.get("/history/{history_id}", response_model=ApplicationHistoryDetailResponse)
def get_application_history(history_id: Annotated[int, Path(gt=0)], current_user: CurrentUser, db: JobTrackerDb) -> ApplicationHistoryDetailResponse:
    return get_history(db, current_user, history_id)


@router.delete("/history/{history_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application_history(history_id: Annotated[int, Path(gt=0)], current_user: CurrentUser, db: JobTrackerDb) -> None:
    delete_history(db, current_user, history_id)
