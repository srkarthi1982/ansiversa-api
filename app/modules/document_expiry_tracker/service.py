from __future__ import annotations

import json
from collections import Counter
from datetime import date, datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.document_expiry_tracker import repository
from app.modules.document_expiry_tracker.models import DocumentRecord
from app.modules.document_expiry_tracker.schemas import (
    DocumentExpiryDashboardResponse,
    DocumentExpiryDocumentCreateRequest,
    DocumentExpiryDocumentDetailResponse,
    DocumentExpiryDocumentSummaryResponse,
    DocumentExpiryDocumentUpdateRequest,
    DocumentExpiryRenewRequest,
    DocumentExpiryTypeCount,
    DocumentSort,
    DocumentStatus,
    ExpiryPeriod,
)


def _today() -> date:
    return date.today()


def _parse_date(value: str | None) -> date | None:
    return date.fromisoformat(value) if value else None


def _tags_from_storage(value: str | None) -> list[str]:
    if not value:
        return []
    try:
        decoded = json.loads(value)
    except json.JSONDecodeError:
        return []
    return [str(item) for item in decoded if str(item).strip()]


def _tags_to_storage(tags: list[str]) -> str:
    return json.dumps(tags, separators=(",", ":"))


def _notes_preview(value: str | None) -> str | None:
    if not value:
        return None
    normalized = " ".join(value.split())
    if len(normalized) <= 140:
        return normalized
    return f"{normalized[:137]}..."


def calculate_status(document: DocumentRecord, today: date | None = None) -> DocumentStatus:
    if document.archived:
        return "archived"
    expiry_date = _parse_date(document.expiry_date)
    if not expiry_date:
        return "active"
    current = today or _today()
    if expiry_date < current:
        return "expired"
    if expiry_date <= current + timedelta(days=document.renewal_reminder_days):
        return "expiringSoon"
    return "active"


def _reminder_date(document: DocumentRecord) -> str | None:
    expiry_date = _parse_date(document.expiry_date)
    if not expiry_date:
        return None
    return (expiry_date - timedelta(days=document.renewal_reminder_days)).isoformat()


def _days_until_expiry(document: DocumentRecord) -> int | None:
    expiry_date = _parse_date(document.expiry_date)
    if not expiry_date:
        return None
    return (expiry_date - _today()).days


def _summary(document: DocumentRecord) -> DocumentExpiryDocumentSummaryResponse:
    return DocumentExpiryDocumentSummaryResponse(
        id=document.id,
        title=document.title,
        document_type=document.document_type,
        document_number=document.document_number,
        issuing_authority=document.issuing_authority,
        country=document.country,
        issue_date=document.issue_date,
        expiry_date=document.expiry_date,
        renewal_reminder_days=document.renewal_reminder_days,
        status=calculate_status(document),
        days_until_expiry=_days_until_expiry(document),
        reminder_date=_reminder_date(document),
        tags=_tags_from_storage(document.tags),
        archived=document.archived,
        renewal_count=document.renewal_count,
        last_renewed_at=document.last_renewed_at,
        notes_preview=_notes_preview(document.notes),
        created_at=document.created_at,
        updated_at=document.updated_at,
    )


def _detail(document: DocumentRecord) -> DocumentExpiryDocumentDetailResponse:
    return DocumentExpiryDocumentDetailResponse(**_summary(document).model_dump(), notes=document.notes)


def _not_found() -> None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document was not found.")


def _commit_or_conflict(db: Session) -> None:
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A document with this title and type already exists.") from exc


def _get_owned_document(db: Session, user: User, document_id: str) -> DocumentRecord:
    document = repository.get_document(db, document_id)
    if not document or document.owner_id != user.id:
        _not_found()
    return document


def _apply_create_fields(document: DocumentRecord, payload: DocumentExpiryDocumentCreateRequest) -> None:
    document.title = payload.title
    document.document_type = payload.document_type
    document.document_number = payload.document_number
    document.issuing_authority = payload.issuing_authority
    document.country = payload.country
    document.issue_date = payload.issue_date
    document.expiry_date = payload.expiry_date
    document.renewal_reminder_days = payload.renewal_reminder_days
    document.notes = payload.notes
    document.tags = _tags_to_storage(payload.tags)


def _apply_update_fields(document: DocumentRecord, payload: DocumentExpiryDocumentUpdateRequest) -> None:
    updates = payload.model_dump(exclude_unset=True)
    for field_name, value in updates.items():
        if field_name == "tags":
            document.tags = _tags_to_storage(value or [])
        else:
            setattr(document, field_name, value)


def _matches_period(document: DocumentRecord, period: ExpiryPeriod) -> bool:
    if period == "all":
        return True
    expiry_date = _parse_date(document.expiry_date)
    current = _today()
    if period == "noExpiry":
        return expiry_date is None
    if period == "expired":
        return bool(expiry_date and expiry_date < current)
    if not expiry_date or expiry_date < current:
        return False
    days = (expiry_date - current).days
    thresholds = {"upcoming7": 7, "upcoming30": 30, "upcoming90": 90}
    return days <= thresholds[period]


def _filter_documents(
    documents: list[DocumentRecord],
    query: str | None,
    document_type: str | None,
    document_status: DocumentStatus | None,
    country: str | None,
    tag: str | None,
    expiry_period: ExpiryPeriod,
) -> list[DocumentRecord]:
    term = (query or "").strip().lower()
    type_filter = (document_type or "").strip().lower()
    country_filter = (country or "").strip().lower()
    tag_filter = (tag or "").strip().lower()
    result: list[DocumentRecord] = []
    for document in documents:
        tags = _tags_from_storage(document.tags)
        haystack = [document.title, document.document_type, document.document_number or "", document.issuing_authority or "", document.country, " ".join(tags)]
        if term and not any(term in item.lower() for item in haystack):
            continue
        if type_filter and document.document_type.lower() != type_filter:
            continue
        if country_filter and document.country.lower() != country_filter:
            continue
        if tag_filter and tag_filter not in tags:
            continue
        if document_status and calculate_status(document) != document_status:
            continue
        if not _matches_period(document, expiry_period):
            continue
        result.append(document)
    return result


def _sort_documents(documents: list[DocumentRecord], sort_by: DocumentSort) -> list[DocumentRecord]:
    if sort_by == "createdAt":
        return sorted(documents, key=lambda item: item.created_at, reverse=True)
    if sort_by == "title":
        return sorted(documents, key=lambda item: item.title.lower())
    return sorted(documents, key=lambda item: (_parse_date(item.expiry_date) is None, _parse_date(item.expiry_date) or date.max, item.title.lower()))


def list_documents(
    db: Session,
    user: User,
    query: str | None = None,
    document_type: str | None = None,
    document_status: DocumentStatus | None = None,
    country: str | None = None,
    tag: str | None = None,
    expiry_period: ExpiryPeriod = "all",
    sort_by: DocumentSort = "expiryDate",
    include_archived: bool = False,
) -> list[DocumentExpiryDocumentSummaryResponse]:
    documents = repository.list_documents(db, user.id, include_archived=include_archived)
    filtered = _filter_documents(documents, query, document_type, document_status, country, tag, expiry_period)
    return [_summary(document) for document in _sort_documents(filtered, sort_by)]


def get_dashboard(db: Session, user: User) -> DocumentExpiryDashboardResponse:
    all_documents = repository.list_documents(db, user.id, include_archived=True)
    active_scope = [document for document in all_documents if not document.archived]
    summaries = [_summary(document) for document in _sort_documents(active_scope, "expiryDate")]
    status_counts = Counter(summary.status for summary in summaries)
    type_counts = Counter(document.document_type for document in active_scope)
    country_counts = Counter(document.country for document in active_scope)

    return DocumentExpiryDashboardResponse(
        documents=summaries,
        total_documents=len(active_scope),
        active_count=status_counts["active"],
        expiring_soon_count=status_counts["expiringSoon"],
        expired_count=status_counts["expired"],
        archived_count=len([document for document in all_documents if document.archived]),
        upcoming_7_count=len([document for document in active_scope if _matches_period(document, "upcoming7")]),
        upcoming_30_count=len([document for document in active_scope if _matches_period(document, "upcoming30")]),
        upcoming_90_count=len([document for document in active_scope if _matches_period(document, "upcoming90")]),
        no_expiry_count=len([document for document in active_scope if not document.expiry_date]),
        type_distribution=[DocumentExpiryTypeCount(label=label, count=count) for label, count in type_counts.most_common(6)],
        country_distribution=[DocumentExpiryTypeCount(label=label, count=count) for label, count in country_counts.most_common(6)],
        upcoming_renewals=summaries[:8],
    )


def create_document(db: Session, user: User, payload: DocumentExpiryDocumentCreateRequest) -> DocumentExpiryDocumentDetailResponse:
    document = DocumentRecord(owner_id=user.id, title=payload.title, document_type=payload.document_type, country=payload.country)
    _apply_create_fields(document, payload)
    repository.add(db, document)
    _commit_or_conflict(db)
    db.refresh(document)
    return _detail(document)


def get_document(db: Session, user: User, document_id: str) -> DocumentExpiryDocumentDetailResponse:
    return _detail(_get_owned_document(db, user, document_id))


def update_document(db: Session, user: User, document_id: str, payload: DocumentExpiryDocumentUpdateRequest) -> DocumentExpiryDocumentDetailResponse:
    document = _get_owned_document(db, user, document_id)
    _apply_update_fields(document, payload)
    _commit_or_conflict(db)
    db.refresh(document)
    return _detail(document)


def archive_document(db: Session, user: User, document_id: str) -> DocumentExpiryDocumentDetailResponse:
    document = _get_owned_document(db, user, document_id)
    document.archived = True
    _commit_or_conflict(db)
    db.refresh(document)
    return _detail(document)


def restore_document(db: Session, user: User, document_id: str) -> DocumentExpiryDocumentDetailResponse:
    document = _get_owned_document(db, user, document_id)
    document.archived = False
    _commit_or_conflict(db)
    db.refresh(document)
    return _detail(document)


def renew_document(db: Session, user: User, document_id: str, payload: DocumentExpiryRenewRequest) -> DocumentExpiryDocumentDetailResponse:
    document = _get_owned_document(db, user, document_id)
    document.issue_date = payload.issue_date
    document.expiry_date = payload.expiry_date
    if payload.notes is not None:
        document.notes = payload.notes
    document.last_renewed_at = datetime.now(timezone.utc).date().isoformat()
    document.renewal_count += 1
    document.archived = False
    _commit_or_conflict(db)
    db.refresh(document)
    return _detail(document)


def delete_document(db: Session, user: User, document_id: str) -> None:
    document = _get_owned_document(db, user, document_id)
    repository.delete_record(db, document)
    db.commit()
