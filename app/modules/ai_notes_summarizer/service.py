import json
import re

from fastapi import HTTPException, status
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.modules.ai_notes_summarizer.models import (
    NoteSummary,
    NotesDocument,
    SummaryJob,
)
from app.modules.ai_notes_summarizer.schemas import (
    NoteSummaryResponse,
    NotesDocumentCreateRequest,
    NotesDocumentDetailResponse,
    NotesDocumentResponse,
    NotesDocumentUpdateRequest,
    SummaryJobResponse,
)
from app.modules.auth.models import User


def _count_summaries(db: Session, document_id: int) -> int:
    return int(
        db.execute(
            select(func.count()).select_from(NoteSummary).where(
                NoteSummary.document_id == document_id
            )
        ).scalar_one()
    )


def _document_response(
    db: Session,
    document: NotesDocument,
) -> NotesDocumentResponse:
    return NotesDocumentResponse(
        id=document.id,
        title=document.title,
        source_text=document.content,
        summary_count=_count_summaries(db, document.id),
        created_at=document.created_at,
        updated_at=document.updated_at,
    )


def _summary_response(summary: NoteSummary, document_title: str) -> NoteSummaryResponse:
    return NoteSummaryResponse(
        id=summary.id,
        document_id=summary.document_id,
        document_title=document_title,
        summary=summary.content,
        key_points=json.loads(summary.meta or "{}").get("keyPoints", []),
        action_items=json.loads(summary.meta or "{}").get("actionItems", []),
        word_count=summary.original_length or 0,
        created_at=summary.created_at,
    )


def _job_response(job: SummaryJob) -> SummaryJobResponse:
    return SummaryJobResponse(
        id=job.id,
        document_id=job.document_id,
        status=job.status,
        created_at=job.created_at,
    )


def _get_owned_document(
    db: Session,
    user: User,
    document_id: int,
) -> NotesDocument:
    document = db.get(NotesDocument, document_id)
    if not document or document.owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notes document was not found.",
        )

    return document


def _sentences(source_text: str) -> list[str]:
    normalized = re.sub(r"\s+", " ", source_text.strip())
    items = re.split(r"(?<=[.!?])\s+", normalized)
    return [item.strip() for item in items if item.strip()]


def _generate_summary_parts(source_text: str) -> tuple[str, list[str], list[str], int]:
    sentences = _sentences(source_text)
    words = re.findall(r"\b[\w'-]+\b", source_text)
    word_count = len(words)
    summary_sentences = sentences[:3] if sentences else [source_text.strip()]
    summary = " ".join(summary_sentences)
    if len(summary) > 900:
        summary = f"{summary[:897].rstrip()}..."

    key_points = sentences[:5]
    if not key_points:
        key_points = [source_text.strip()[:240]]

    action_markers = ("todo", "action", "next", "follow up", "review", "prepare")
    action_items = [
        sentence
        for sentence in sentences
        if any(marker in sentence.lower() for marker in action_markers)
    ][:5]
    if not action_items:
        action_items = ["Review the summary and mark any follow-up work manually."]

    return summary, key_points, action_items, word_count


def _list_summaries_for_document(
    db: Session,
    document: NotesDocument,
) -> list[NoteSummaryResponse]:
    summaries = list(
        db.execute(
            select(NoteSummary)
            .where(NoteSummary.document_id == document.id)
            .order_by(NoteSummary.created_at.desc())
        )
        .scalars()
        .all()
    )
    return [_summary_response(summary, document.title) for summary in summaries]


def _list_jobs_for_document(
    db: Session,
    document_id: int,
) -> list[SummaryJobResponse]:
    jobs = list(
        db.execute(
            select(SummaryJob)
            .where(SummaryJob.document_id == document_id)
            .order_by(SummaryJob.created_at.desc())
        )
        .scalars()
        .all()
    )
    return [_job_response(job) for job in jobs]


def list_documents(db: Session, user: User) -> list[NotesDocumentResponse]:
    documents = list(
        db.execute(
            select(NotesDocument)
            .where(NotesDocument.owner_id == user.id)
            .order_by(NotesDocument.updated_at.desc(), NotesDocument.title.asc())
        )
        .scalars()
        .all()
    )

    return [_document_response(db, document) for document in documents]


def create_document(
    db: Session,
    user: User,
    payload: NotesDocumentCreateRequest,
) -> NotesDocumentDetailResponse:
    document = NotesDocument(
        owner_id=user.id,
        title=payload.title,
        content=payload.source_text,
        source_type="paste",
    )
    db.add(document)
    db.flush()
    create_summary(db, user, document.id, commit=False)
    db.commit()
    db.refresh(document)

    return get_document_detail(db, user, document.id)


def get_document_detail(
    db: Session,
    user: User,
    document_id: int,
) -> NotesDocumentDetailResponse:
    document = _get_owned_document(db, user, document_id)
    return NotesDocumentDetailResponse(
        document=_document_response(db, document),
        summaries=_list_summaries_for_document(db, document),
        jobs=_list_jobs_for_document(db, document.id),
    )


def update_document(
    db: Session,
    user: User,
    document_id: int,
    payload: NotesDocumentUpdateRequest,
) -> NotesDocumentDetailResponse:
    document = _get_owned_document(db, user, document_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        if field == "source_text":
            field = "content"
        setattr(document, field, value)
    db.commit()
    db.refresh(document)

    return get_document_detail(db, user, document.id)


def delete_document(db: Session, user: User, document_id: int) -> None:
    document = _get_owned_document(db, user, document_id)
    db.execute(delete(SummaryJob).where(SummaryJob.document_id == document.id))
    db.execute(delete(NoteSummary).where(NoteSummary.document_id == document.id))
    db.delete(document)
    db.commit()


def create_summary(
    db: Session,
    user: User,
    document_id: int,
    *,
    commit: bool = True,
) -> NoteSummaryResponse:
    document = _get_owned_document(db, user, document_id)
    summary_text, key_points, action_items, word_count = _generate_summary_parts(
        document.content
    )
    summary = NoteSummary(
        document_id=document.id,
        owner_id=user.id,
        summary_type="standard",
        content=summary_text,
        original_length=word_count,
        summary_length=len(re.findall(r"\b[\w'-]+\b", summary_text)),
        meta=json.dumps({"keyPoints": key_points, "actionItems": action_items}),
    )
    db.add(summary)
    db.flush()
    job = SummaryJob(
        document_id=document.id,
        owner_id=user.id,
        job_type="summary",
        input=json.dumps({"documentId": document.id}),
        output=json.dumps({"summaryId": summary.id}),
        status="complete",
    )
    db.add(job)
    if commit:
        db.commit()
        db.refresh(summary)

    return _summary_response(summary, document.title)


def list_summaries(db: Session, user: User) -> list[NoteSummaryResponse]:
    rows = db.execute(
        select(NoteSummary, NotesDocument.title)
        .join(NotesDocument, NotesDocument.id == NoteSummary.document_id)
        .where(NotesDocument.owner_id == user.id)
        .order_by(NoteSummary.created_at.desc())
    ).all()

    return [_summary_response(summary, title) for summary, title in rows]
