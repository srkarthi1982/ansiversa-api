from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.digital_document_vault import repository
from app.modules.digital_document_vault.constants import ALLOWED_FILE_EXTENSIONS, ALLOWED_MIME_TYPES, MAX_FILE_SIZE_BYTES
from app.modules.digital_document_vault.models import VaultCategory, VaultDocument
from app.modules.digital_document_vault.schemas import (
    DocumentSort,
    ExpiryFilter,
    ExpiryStatus,
    VaultCategoryCreateRequest,
    VaultCategoryResponse,
    VaultCategoryUpdateRequest,
    VaultCountItem,
    VaultDashboardResponse,
    VaultDocumentDetailResponse,
    VaultDocumentMetadataRequest,
    VaultDocumentSummaryResponse,
    VaultStorageItem,
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


def _preview(value: str | None) -> str | None:
    if not value:
        return None
    normalized = " ".join(value.split())
    if len(normalized) <= 140:
        return normalized
    return f"{normalized[:137]}..."


def _expiry_status(document: VaultDocument, today: date | None = None) -> ExpiryStatus:
    expiry_date = _parse_date(document.expiry_date)
    if not expiry_date:
        return "noExpiry"
    current = today or _today()
    if expiry_date < current:
        return "expired"
    if expiry_date <= current + timedelta(days=30):
        return "expiringSoon"
    return "active"


def _days_until_expiry(document: VaultDocument) -> int | None:
    expiry_date = _parse_date(document.expiry_date)
    if not expiry_date:
        return None
    return (expiry_date - _today()).days


def _category_summary(category: VaultCategory, document_count: int = 0) -> VaultCategoryResponse:
    return VaultCategoryResponse(
        id=category.id,
        name=category.name,
        document_count=document_count,
        created_at=category.created_at,
        updated_at=category.updated_at,
    )


def _document_summary(document: VaultDocument) -> VaultDocumentSummaryResponse:
    return VaultDocumentSummaryResponse(
        id=document.id,
        title=document.title,
        category_id=document.category_id,
        category_name=document.category.name,
        document_type=document.document_type,
        description_preview=_preview(document.description),
        tags=_tags_from_storage(document.tags),
        file_name=document.file_name,
        stored_file_name=document.stored_file_name,
        mime_type=document.mime_type,
        file_size=document.file_size,
        issue_date=document.issue_date,
        expiry_date=document.expiry_date,
        expiry_status=_expiry_status(document),
        days_until_expiry=_days_until_expiry(document),
        uploaded_at=document.uploaded_at,
        updated_at=document.updated_at,
    )


def _document_detail(document: VaultDocument) -> VaultDocumentDetailResponse:
    return VaultDocumentDetailResponse(**_document_summary(document).model_dump(), description=document.description)


def _not_found(resource: str) -> None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{resource} was not found.")


def _commit_or_conflict(db: Session, message: str) -> None:
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=message) from exc


def _get_owned_category(db: Session, user: User, category_id: str) -> VaultCategory:
    category = repository.get_category(db, category_id)
    if not category or category.owner_id != user.id:
        _not_found("Category")
    return category


def _get_owned_document(db: Session, user: User, document_id: str) -> VaultDocument:
    document = repository.get_document(db, document_id)
    if not document or document.owner_id != user.id:
        _not_found("Document")
    return document


async def _read_upload(file: UploadFile) -> tuple[str, str, bytes]:
    file_name = Path(file.filename or "").name.strip()
    extension = Path(file_name).suffix.lower()
    if not file_name or extension not in ALLOWED_FILE_EXTENSIONS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Upload a PDF, JPG, PNG, or DOCX file.")
    content_type = (file.content_type or "").strip().lower()
    if content_type and content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This file type is not supported.")
    content = await file.read()
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty.")
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file must be 10 MB or smaller.")
    return file_name, content_type or _mime_from_extension(extension), content


def _mime_from_extension(extension: str) -> str:
    return {
        ".pdf": "application/pdf",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }[extension]


def _stored_file_name(file_name: str) -> str:
    extension = Path(file_name).suffix.lower()
    return f"{uuid4().hex}{extension}"


def _apply_metadata(document: VaultDocument, payload: VaultDocumentMetadataRequest) -> None:
    document.title = payload.title
    document.category_id = payload.category_id
    document.document_type = payload.document_type
    document.description = payload.description
    document.tags = _tags_to_storage(payload.tags)
    document.issue_date = payload.issue_date
    document.expiry_date = payload.expiry_date


def list_categories(db: Session, user: User) -> list[VaultCategoryResponse]:
    counts = repository.document_counts_by_category(db, user.id)
    return [_category_summary(category, counts.get(category.id, 0)) for category in repository.list_categories(db, user.id)]


def create_category(db: Session, user: User, payload: VaultCategoryCreateRequest) -> VaultCategoryResponse:
    category = VaultCategory(owner_id=user.id, name=payload.name)
    repository.add(db, category)
    _commit_or_conflict(db, "A category with this name already exists.")
    db.refresh(category)
    return _category_summary(category, 0)


def update_category(db: Session, user: User, category_id: str, payload: VaultCategoryUpdateRequest) -> VaultCategoryResponse:
    category = _get_owned_category(db, user, category_id)
    category.name = payload.name
    _commit_or_conflict(db, "A category with this name already exists.")
    db.refresh(category)
    return _category_summary(category, repository.count_documents_for_category(db, user.id, category.id))


def delete_category(db: Session, user: User, category_id: str) -> None:
    category = _get_owned_category(db, user, category_id)
    if repository.count_documents_for_category(db, user.id, category.id) > 0:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Category has documents. Reassign or delete documents first.")
    repository.delete_record(db, category)
    db.commit()


def _matches_filter(document: VaultDocument, expiry_filter: ExpiryFilter) -> bool:
    if expiry_filter == "all":
        return True
    status_value = _expiry_status(document)
    if expiry_filter == "expiring":
        return status_value == "expiringSoon"
    if expiry_filter == "expired":
        return status_value == "expired"
    return status_value == "noExpiry"


def _filter_documents(
    documents: list[VaultDocument],
    query: str | None,
    category_id: str | None,
    document_type: str | None,
    expiry_filter: ExpiryFilter,
) -> list[VaultDocument]:
    term = (query or "").strip().lower()
    category_filter = (category_id or "").strip()
    type_filter = (document_type or "").strip().lower()
    result: list[VaultDocument] = []
    for document in documents:
        tags = _tags_from_storage(document.tags)
        haystack = [document.title, document.category.name, document.document_type, document.file_name, document.description or "", " ".join(tags)]
        if term and not any(term in item.lower() for item in haystack):
            continue
        if category_filter and document.category_id != category_filter:
            continue
        if type_filter and document.document_type.lower() != type_filter:
            continue
        if not _matches_filter(document, expiry_filter):
            continue
        result.append(document)
    return result


def _sort_documents(documents: list[VaultDocument], sort_by: DocumentSort) -> list[VaultDocument]:
    if sort_by == "title":
        return sorted(documents, key=lambda item: item.title.lower())
    if sort_by == "fileSize":
        return sorted(documents, key=lambda item: item.file_size, reverse=True)
    if sort_by == "expiryDate":
        return sorted(documents, key=lambda item: (_parse_date(item.expiry_date) is None, _parse_date(item.expiry_date) or date.max, item.title.lower()))
    return sorted(documents, key=lambda item: item.uploaded_at, reverse=True)


def list_documents(
    db: Session,
    user: User,
    query: str | None = None,
    category_id: str | None = None,
    document_type: str | None = None,
    expiry_filter: ExpiryFilter = "all",
    sort_by: DocumentSort = "uploadedAt",
) -> list[VaultDocumentSummaryResponse]:
    documents = repository.list_documents(db, user.id)
    filtered = _filter_documents(documents, query, category_id, document_type, expiry_filter)
    return [_document_summary(document) for document in _sort_documents(filtered, sort_by)]


async def create_document(db: Session, user: User, payload: VaultDocumentMetadataRequest, file: UploadFile) -> VaultDocumentDetailResponse:
    category = _get_owned_category(db, user, payload.category_id)
    file_name, mime_type, content = await _read_upload(file)
    document = VaultDocument(
        owner_id=user.id,
        category_id=category.id,
        title=payload.title,
        document_type=payload.document_type,
        file_name=file_name,
        stored_file_name=_stored_file_name(file_name),
        mime_type=mime_type,
        file_size=len(content),
        file_blob=content,
    )
    _apply_metadata(document, payload)
    repository.add(db, document)
    _commit_or_conflict(db, "A document with this stored file already exists.")
    db.refresh(document)
    document.category = category
    return _document_detail(document)


def get_document(db: Session, user: User, document_id: str) -> VaultDocumentDetailResponse:
    return _document_detail(_get_owned_document(db, user, document_id))


def get_document_file(db: Session, user: User, document_id: str) -> VaultDocument:
    return _get_owned_document(db, user, document_id)


def update_document(db: Session, user: User, document_id: str, payload: VaultDocumentMetadataRequest) -> VaultDocumentDetailResponse:
    document = _get_owned_document(db, user, document_id)
    category = _get_owned_category(db, user, payload.category_id)
    _apply_metadata(document, payload)
    _commit_or_conflict(db, "Unable to update document metadata.")
    db.refresh(document)
    document.category = category
    return _document_detail(document)


async def replace_document_file(db: Session, user: User, document_id: str, file: UploadFile) -> VaultDocumentDetailResponse:
    document = _get_owned_document(db, user, document_id)
    file_name, mime_type, content = await _read_upload(file)
    document.file_name = file_name
    document.stored_file_name = _stored_file_name(file_name)
    document.mime_type = mime_type
    document.file_size = len(content)
    document.file_blob = content
    _commit_or_conflict(db, "Unable to replace document file.")
    db.refresh(document)
    return _document_detail(document)


def delete_document(db: Session, user: User, document_id: str) -> None:
    document = _get_owned_document(db, user, document_id)
    repository.delete_record(db, document)
    db.commit()


def get_dashboard(db: Session, user: User) -> VaultDashboardResponse:
    documents = repository.list_documents(db, user.id)
    summaries = [_document_summary(document) for document in _sort_documents(documents, "uploadedAt")]
    categories = list_categories(db, user)
    category_counts = Counter(document.category.name for document in documents)
    type_counts = Counter(document.document_type for document in documents)
    storage_by_type: dict[str, int] = defaultdict(int)
    for document in documents:
        storage_by_type[document.document_type] += document.file_size

    return VaultDashboardResponse(
        documents=summaries,
        categories=categories,
        total_documents=len(documents),
        total_storage_bytes=sum(document.file_size for document in documents),
        expiring_documents_count=len([document for document in documents if _expiry_status(document) == "expiringSoon"]),
        expired_documents_count=len([document for document in documents if _expiry_status(document) == "expired"]),
        no_expiry_count=len([document for document in documents if _expiry_status(document) == "noExpiry"]),
        category_distribution=[VaultCountItem(label=label, count=count) for label, count in category_counts.most_common(8)],
        type_distribution=[VaultCountItem(label=label, count=count) for label, count in type_counts.most_common(8)],
        storage_by_type=[VaultStorageItem(label=label, bytes=bytes_used) for label, bytes_used in sorted(storage_by_type.items(), key=lambda item: item[1], reverse=True)[:8]],
        recent_documents=summaries[:8],
    )
