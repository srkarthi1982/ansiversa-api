from typing import Annotated

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.auth.service import get_current_user
from app.modules.client_feedback_analyzer.db import get_client_feedback_analyzer_db
from app.modules.client_feedback_analyzer.schemas import (
    ClientFeedbackAnalyzerDashboardResponse,
    ClientFeedbackCreateRequest,
    ClientFeedbackDetailResponse,
    ClientFeedbackSummaryResponse,
    ClientFeedbackUpdateRequest,
    ClientProfileCreateRequest,
    ClientProfileDetailResponse,
    ClientProfileSummaryResponse,
    ClientProfileUpdateRequest,
    FeedbackInsightCreateRequest,
    FeedbackInsightDetailResponse,
    FeedbackInsightSummaryResponse,
    FeedbackInsightUpdateRequest,
    FeedbackReportCreateRequest,
    FeedbackReportDetailResponse,
    FeedbackReportSummaryResponse,
    FeedbackReportUpdateRequest,
)
from app.modules.client_feedback_analyzer.service import (
    create_client,
    create_feedback,
    create_insight,
    create_report,
    delete_client,
    delete_feedback,
    delete_insight,
    delete_report,
    get_client,
    get_dashboard,
    get_feedback,
    get_insight,
    get_report,
    list_clients,
    list_feedback,
    list_insights,
    list_reports,
    update_client,
    update_feedback,
    update_insight,
    update_report,
)

router = APIRouter()


@router.get("/dashboard", response_model=ClientFeedbackAnalyzerDashboardResponse)
def get_client_feedback_dashboard(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_client_feedback_analyzer_db)],
) -> ClientFeedbackAnalyzerDashboardResponse:
    return get_dashboard(db, current_user)


@router.post("/clients", response_model=ClientProfileDetailResponse, status_code=status.HTTP_201_CREATED)
def create_client_profile(
    payload: ClientProfileCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_client_feedback_analyzer_db)],
) -> ClientProfileDetailResponse:
    return create_client(db, current_user, payload)


@router.get("/clients", response_model=list[ClientProfileSummaryResponse])
def list_client_profiles(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_client_feedback_analyzer_db)],
) -> list[ClientProfileSummaryResponse]:
    return list_clients(db, current_user)


@router.get("/clients/{client_id}", response_model=ClientProfileDetailResponse)
def get_client_profile(
    client_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_client_feedback_analyzer_db)],
) -> ClientProfileDetailResponse:
    return get_client(db, current_user, client_id)


@router.put("/clients/{client_id}", response_model=ClientProfileDetailResponse)
def update_client_profile(
    client_id: Annotated[int, Path(gt=0)],
    payload: ClientProfileUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_client_feedback_analyzer_db)],
) -> ClientProfileDetailResponse:
    return update_client(db, current_user, client_id, payload)


@router.delete("/clients/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client_profile(
    client_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_client_feedback_analyzer_db)],
) -> None:
    delete_client(db, current_user, client_id)


@router.post("/feedback", response_model=ClientFeedbackDetailResponse, status_code=status.HTTP_201_CREATED)
def create_client_feedback(
    payload: ClientFeedbackCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_client_feedback_analyzer_db)],
) -> ClientFeedbackDetailResponse:
    return create_feedback(db, current_user, payload)


@router.get("/feedback", response_model=list[ClientFeedbackSummaryResponse])
def list_client_feedback(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_client_feedback_analyzer_db)],
) -> list[ClientFeedbackSummaryResponse]:
    return list_feedback(db, current_user)


@router.get("/feedback/{feedback_id}", response_model=ClientFeedbackDetailResponse)
def get_client_feedback(
    feedback_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_client_feedback_analyzer_db)],
) -> ClientFeedbackDetailResponse:
    return get_feedback(db, current_user, feedback_id)


@router.put("/feedback/{feedback_id}", response_model=ClientFeedbackDetailResponse)
def update_client_feedback(
    feedback_id: Annotated[int, Path(gt=0)],
    payload: ClientFeedbackUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_client_feedback_analyzer_db)],
) -> ClientFeedbackDetailResponse:
    return update_feedback(db, current_user, feedback_id, payload)


@router.delete("/feedback/{feedback_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client_feedback(
    feedback_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_client_feedback_analyzer_db)],
) -> None:
    delete_feedback(db, current_user, feedback_id)


@router.post("/insights", response_model=FeedbackInsightDetailResponse, status_code=status.HTTP_201_CREATED)
def create_feedback_insight(
    payload: FeedbackInsightCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_client_feedback_analyzer_db)],
) -> FeedbackInsightDetailResponse:
    return create_insight(db, current_user, payload)


@router.get("/insights", response_model=list[FeedbackInsightSummaryResponse])
def list_feedback_insights(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_client_feedback_analyzer_db)],
) -> list[FeedbackInsightSummaryResponse]:
    return list_insights(db, current_user)


@router.get("/insights/{insight_id}", response_model=FeedbackInsightDetailResponse)
def get_feedback_insight(
    insight_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_client_feedback_analyzer_db)],
) -> FeedbackInsightDetailResponse:
    return get_insight(db, current_user, insight_id)


@router.put("/insights/{insight_id}", response_model=FeedbackInsightDetailResponse)
def update_feedback_insight(
    insight_id: Annotated[int, Path(gt=0)],
    payload: FeedbackInsightUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_client_feedback_analyzer_db)],
) -> FeedbackInsightDetailResponse:
    return update_insight(db, current_user, insight_id, payload)


@router.delete("/insights/{insight_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_feedback_insight(
    insight_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_client_feedback_analyzer_db)],
) -> None:
    delete_insight(db, current_user, insight_id)


@router.post("/reports", response_model=FeedbackReportDetailResponse, status_code=status.HTTP_201_CREATED)
def create_feedback_report(
    payload: FeedbackReportCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_client_feedback_analyzer_db)],
) -> FeedbackReportDetailResponse:
    return create_report(db, current_user, payload)


@router.get("/reports", response_model=list[FeedbackReportSummaryResponse])
def list_feedback_reports(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_client_feedback_analyzer_db)],
) -> list[FeedbackReportSummaryResponse]:
    return list_reports(db, current_user)


@router.get("/reports/{report_id}", response_model=FeedbackReportDetailResponse)
def get_feedback_report(
    report_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_client_feedback_analyzer_db)],
) -> FeedbackReportDetailResponse:
    return get_report(db, current_user, report_id)


@router.put("/reports/{report_id}", response_model=FeedbackReportDetailResponse)
def update_feedback_report(
    report_id: Annotated[int, Path(gt=0)],
    payload: FeedbackReportUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_client_feedback_analyzer_db)],
) -> FeedbackReportDetailResponse:
    return update_report(db, current_user, report_id, payload)


@router.delete("/reports/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_feedback_report(
    report_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_client_feedback_analyzer_db)],
) -> None:
    delete_report(db, current_user, report_id)
