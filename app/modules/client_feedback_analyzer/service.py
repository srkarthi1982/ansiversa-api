from fastapi import HTTPException, status
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.client_feedback_analyzer.models import (
    ClientFeedback,
    ClientProfile,
    FeedbackInsight,
    FeedbackReport,
)
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

PREVIEW_LENGTH = 220


def _preview(value: str | None) -> str | None:
    if not value:
        return None
    if len(value) <= PREVIEW_LENGTH:
        return value
    return f"{value[:PREVIEW_LENGTH].rstrip()}..."


def _not_found(detail: str) -> None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def _get_owned_client(db: Session, user: User, client_id: int) -> ClientProfile:
    client = db.get(ClientProfile, client_id)
    if not client or client.owner_id != user.id:
        _not_found("Client profile was not found.")
    return client


def _get_owned_feedback(db: Session, user: User, feedback_id: int) -> ClientFeedback:
    feedback = db.get(ClientFeedback, feedback_id)
    if not feedback or feedback.owner_id != user.id:
        _not_found("Client feedback was not found.")
    return feedback


def _get_owned_insight(db: Session, user: User, insight_id: int) -> FeedbackInsight:
    insight = db.get(FeedbackInsight, insight_id)
    if not insight or insight.owner_id != user.id:
        _not_found("Feedback insight was not found.")
    return insight


def _get_owned_report(db: Session, user: User, report_id: int) -> FeedbackReport:
    report = db.get(FeedbackReport, report_id)
    if not report or report.owner_id != user.id:
        _not_found("Feedback report was not found.")
    return report


def _optional_owned_feedback(
    db: Session,
    user: User,
    feedback_id: int | None,
) -> ClientFeedback | None:
    if feedback_id is None:
        return None
    return _get_owned_feedback(db, user, feedback_id)


def _count_feedback(db: Session, client_id: int) -> int:
    return int(db.execute(select(func.count()).select_from(ClientFeedback).where(ClientFeedback.client_id == client_id)).scalar_one())


def _count_client_insights(db: Session, client_id: int) -> int:
    return int(db.execute(select(func.count()).select_from(FeedbackInsight).where(FeedbackInsight.client_id == client_id)).scalar_one())


def _count_feedback_insights(db: Session, feedback_id: int) -> int:
    return int(db.execute(select(func.count()).select_from(FeedbackInsight).where(FeedbackInsight.feedback_id == feedback_id)).scalar_one())


def _client_summary_response(db: Session, client: ClientProfile) -> ClientProfileSummaryResponse:
    return ClientProfileSummaryResponse(
        id=client.id,
        platform_id=client.platform_id,
        name=client.name,
        company_name=client.company_name,
        contact_name=client.contact_name,
        email=client.email,
        industry=client.industry,
        segment=client.segment,
        feedback_count=_count_feedback(db, client.id),
        insight_count=_count_client_insights(db, client.id),
        created_at=client.created_at,
        updated_at=client.updated_at,
    )


def _client_detail_response(db: Session, client: ClientProfile) -> ClientProfileDetailResponse:
    summary = _client_summary_response(db, client)
    return ClientProfileDetailResponse(**summary.model_dump(), notes=client.notes)


def _feedback_summary_response(
    db: Session,
    feedback: ClientFeedback,
    client_name: str,
) -> ClientFeedbackSummaryResponse:
    return ClientFeedbackSummaryResponse(
        id=feedback.id,
        platform_id=feedback.platform_id,
        client_id=feedback.client_id,
        client_name=client_name,
        title=feedback.title,
        source=feedback.source,
        feedback_preview=_preview(feedback.feedback_text),
        sentiment=feedback.sentiment,
        rating=feedback.rating,
        status=feedback.status,
        received_at=feedback.received_at,
        tags_preview=_preview(feedback.tags),
        insight_count=_count_feedback_insights(db, feedback.id),
        created_at=feedback.created_at,
        updated_at=feedback.updated_at,
    )


def _feedback_detail_response(
    db: Session,
    feedback: ClientFeedback,
    client_name: str,
) -> ClientFeedbackDetailResponse:
    summary = _feedback_summary_response(db, feedback, client_name)
    return ClientFeedbackDetailResponse(
        **summary.model_dump(),
        feedback_text=feedback.feedback_text,
        tags=feedback.tags,
    )


def _insight_summary_response(
    insight: FeedbackInsight,
    client_name: str,
    feedback_title: str | None,
) -> FeedbackInsightSummaryResponse:
    return FeedbackInsightSummaryResponse(
        id=insight.id,
        platform_id=insight.platform_id,
        client_id=insight.client_id,
        client_name=client_name,
        feedback_id=insight.feedback_id,
        feedback_title=feedback_title,
        title=insight.title,
        category=insight.category,
        sentiment=insight.sentiment,
        priority=insight.priority,
        recommendation_preview=_preview(insight.recommendation),
        status=insight.status,
        created_at=insight.created_at,
        updated_at=insight.updated_at,
    )


def _insight_detail_response(
    insight: FeedbackInsight,
    client_name: str,
    feedback_title: str | None,
) -> FeedbackInsightDetailResponse:
    summary = _insight_summary_response(insight, client_name, feedback_title)
    return FeedbackInsightDetailResponse(
        **summary.model_dump(),
        recommendation=insight.recommendation,
        notes=insight.notes,
    )


def _report_summary_response(report: FeedbackReport) -> FeedbackReportSummaryResponse:
    return FeedbackReportSummaryResponse(
        id=report.id,
        platform_id=report.platform_id,
        title=report.title,
        scope=report.scope,
        summary_preview=_preview(report.summary),
        period_start=report.period_start,
        period_end=report.period_end,
        status=report.status,
        created_at=report.created_at,
        updated_at=report.updated_at,
    )


def _report_detail_response(report: FeedbackReport) -> FeedbackReportDetailResponse:
    summary = _report_summary_response(report)
    return FeedbackReportDetailResponse(**summary.model_dump(), summary=report.summary)


def list_clients(db: Session, user: User) -> list[ClientProfileSummaryResponse]:
    clients = list(db.execute(select(ClientProfile).where(ClientProfile.owner_id == user.id).order_by(ClientProfile.updated_at.desc(), ClientProfile.name.asc())).scalars().all())
    return [_client_summary_response(db, client) for client in clients]


def create_client(db: Session, user: User, payload: ClientProfileCreateRequest) -> ClientProfileDetailResponse:
    client = ClientProfile(owner_id=user.id, **payload.model_dump())
    db.add(client)
    db.commit()
    db.refresh(client)
    return _client_detail_response(db, client)


def get_client(db: Session, user: User, client_id: int) -> ClientProfileDetailResponse:
    return _client_detail_response(db, _get_owned_client(db, user, client_id))


def update_client(db: Session, user: User, client_id: int, payload: ClientProfileUpdateRequest) -> ClientProfileDetailResponse:
    client = _get_owned_client(db, user, client_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(client, field, value)
    db.commit()
    db.refresh(client)
    return _client_detail_response(db, client)


def delete_client(db: Session, user: User, client_id: int) -> None:
    client = _get_owned_client(db, user, client_id)
    feedback_ids = list(db.execute(select(ClientFeedback.id).where(ClientFeedback.client_id == client.id)).scalars().all())
    if feedback_ids:
        db.execute(delete(FeedbackInsight).where(FeedbackInsight.feedback_id.in_(feedback_ids)))
    db.execute(delete(FeedbackInsight).where(FeedbackInsight.client_id == client.id))
    db.execute(delete(ClientFeedback).where(ClientFeedback.client_id == client.id))
    db.delete(client)
    db.commit()


def list_feedback(db: Session, user: User) -> list[ClientFeedbackSummaryResponse]:
    rows = db.execute(
        select(ClientFeedback, ClientProfile.name)
        .join(ClientProfile, ClientProfile.id == ClientFeedback.client_id)
        .where(ClientFeedback.owner_id == user.id)
        .order_by(ClientFeedback.updated_at.desc(), ClientFeedback.title.asc())
    ).all()
    return [_feedback_summary_response(db, feedback, client_name) for feedback, client_name in rows]


def create_feedback(db: Session, user: User, payload: ClientFeedbackCreateRequest) -> ClientFeedbackDetailResponse:
    client = _get_owned_client(db, user, payload.client_id)
    feedback = ClientFeedback(owner_id=user.id, **payload.model_dump())
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return _feedback_detail_response(db, feedback, client.name)


def get_feedback(db: Session, user: User, feedback_id: int) -> ClientFeedbackDetailResponse:
    feedback = _get_owned_feedback(db, user, feedback_id)
    client = _get_owned_client(db, user, feedback.client_id)
    return _feedback_detail_response(db, feedback, client.name)


def update_feedback(db: Session, user: User, feedback_id: int, payload: ClientFeedbackUpdateRequest) -> ClientFeedbackDetailResponse:
    feedback = _get_owned_feedback(db, user, feedback_id)
    data = payload.model_dump(exclude_unset=True)
    if "client_id" in data and data["client_id"] is not None:
        _get_owned_client(db, user, data["client_id"])
    for field, value in data.items():
        setattr(feedback, field, value)
    db.commit()
    db.refresh(feedback)
    client = _get_owned_client(db, user, feedback.client_id)
    return _feedback_detail_response(db, feedback, client.name)


def delete_feedback(db: Session, user: User, feedback_id: int) -> None:
    feedback = _get_owned_feedback(db, user, feedback_id)
    db.execute(delete(FeedbackInsight).where(FeedbackInsight.feedback_id == feedback.id))
    db.delete(feedback)
    db.commit()


def list_insights(db: Session, user: User) -> list[FeedbackInsightSummaryResponse]:
    rows = db.execute(
        select(FeedbackInsight, ClientProfile.name, ClientFeedback.title)
        .join(ClientProfile, ClientProfile.id == FeedbackInsight.client_id)
        .outerjoin(ClientFeedback, ClientFeedback.id == FeedbackInsight.feedback_id)
        .where(FeedbackInsight.owner_id == user.id)
        .order_by(FeedbackInsight.updated_at.desc(), FeedbackInsight.priority.desc())
    ).all()
    return [_insight_summary_response(insight, client_name, feedback_title) for insight, client_name, feedback_title in rows]


def create_insight(db: Session, user: User, payload: FeedbackInsightCreateRequest) -> FeedbackInsightDetailResponse:
    client = _get_owned_client(db, user, payload.client_id)
    feedback = _optional_owned_feedback(db, user, payload.feedback_id)
    if feedback and feedback.client_id != client.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Feedback must belong to the selected client.")
    insight = FeedbackInsight(owner_id=user.id, **payload.model_dump())
    db.add(insight)
    db.commit()
    db.refresh(insight)
    return _insight_detail_response(insight, client.name, feedback.title if feedback else None)


def get_insight(db: Session, user: User, insight_id: int) -> FeedbackInsightDetailResponse:
    insight = _get_owned_insight(db, user, insight_id)
    client = _get_owned_client(db, user, insight.client_id)
    feedback = _optional_owned_feedback(db, user, insight.feedback_id)
    return _insight_detail_response(insight, client.name, feedback.title if feedback else None)


def update_insight(db: Session, user: User, insight_id: int, payload: FeedbackInsightUpdateRequest) -> FeedbackInsightDetailResponse:
    insight = _get_owned_insight(db, user, insight_id)
    data = payload.model_dump(exclude_unset=True)
    client = _get_owned_client(db, user, data.get("client_id") or insight.client_id)
    feedback = _optional_owned_feedback(db, user, data.get("feedback_id") if "feedback_id" in data else insight.feedback_id)
    if feedback and feedback.client_id != client.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Feedback must belong to the selected client.")
    for field, value in data.items():
        setattr(insight, field, value)
    db.commit()
    db.refresh(insight)
    return _insight_detail_response(insight, client.name, feedback.title if feedback else None)


def delete_insight(db: Session, user: User, insight_id: int) -> None:
    insight = _get_owned_insight(db, user, insight_id)
    db.delete(insight)
    db.commit()


def list_reports(db: Session, user: User) -> list[FeedbackReportSummaryResponse]:
    reports = list(db.execute(select(FeedbackReport).where(FeedbackReport.owner_id == user.id).order_by(FeedbackReport.updated_at.desc(), FeedbackReport.title.asc())).scalars().all())
    return [_report_summary_response(report) for report in reports]


def create_report(db: Session, user: User, payload: FeedbackReportCreateRequest) -> FeedbackReportDetailResponse:
    report = FeedbackReport(owner_id=user.id, **payload.model_dump())
    db.add(report)
    db.commit()
    db.refresh(report)
    return _report_detail_response(report)


def get_report(db: Session, user: User, report_id: int) -> FeedbackReportDetailResponse:
    return _report_detail_response(_get_owned_report(db, user, report_id))


def update_report(db: Session, user: User, report_id: int, payload: FeedbackReportUpdateRequest) -> FeedbackReportDetailResponse:
    report = _get_owned_report(db, user, report_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(report, field, value)
    db.commit()
    db.refresh(report)
    return _report_detail_response(report)


def delete_report(db: Session, user: User, report_id: int) -> None:
    report = _get_owned_report(db, user, report_id)
    db.delete(report)
    db.commit()


def get_dashboard(db: Session, user: User) -> ClientFeedbackAnalyzerDashboardResponse:
    clients = list_clients(db, user)
    feedback = list_feedback(db, user)
    insights = list_insights(db, user)
    reports = list_reports(db, user)
    return ClientFeedbackAnalyzerDashboardResponse(
        clients=clients,
        feedback=feedback,
        insights=insights,
        reports=reports,
        client_count=len(clients),
        feedback_count=len(feedback),
        insight_count=len(insights),
        report_count=len(reports),
        negative_feedback_count=sum(1 for item in feedback if item.sentiment == "negative"),
        urgent_insight_count=sum(1 for item in insights if item.priority == "urgent"),
    )
