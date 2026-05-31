from dataclasses import dataclass
from datetime import datetime
from math import ceil
from uuid import uuid4

from fastapi import HTTPException, Request, status
from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session

from app.modules.admin.schemas import CreateFaqRequest, UpdateFaqRequest
from app.modules.audit.service import write_audit_log
from app.modules.auth.models import User
from app.modules.faqs.models import Faq


DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 200
SORT_OPTIONS = {
    "order",
    "order-asc",
    "order-desc",
    "newest",
    "oldest",
    "question-asc",
    "question-desc",
    "audience-asc",
    "audience-desc",
    "category-asc",
    "category-desc",
    "published-asc",
    "published-desc",
    "updated-asc",
    "updated-desc",
}


@dataclass(frozen=True)
class AdminFaqListResult:
    items: list[Faq]
    total: int
    page: int
    page_size: int
    total_pages: int
    sort: str
    dir: str
    q: str
    app_key: str
    audience: str
    category: str
    is_published: bool | str


def normalize_optional(value: str | None) -> str | None:
    if value is None:
        return None

    trimmed = value.strip()
    return trimmed or None


def normalize_audience(value: str | None) -> str:
    normalized = (value or "user").strip()
    return "admin" if normalized == "admin" else "user"


def normalize_sort(sort: str | None, sort_by: str | None, sort_direction: str | None) -> str:
    if sort and sort in SORT_OPTIONS:
        return sort

    key = (sort_by or "").strip()
    direction = "desc" if (sort_direction or "").strip().lower() == "desc" else "asc"
    if key in {"sortOrder", "sort_order", "order"}:
        return f"order-{direction}"
    if key == "question":
        return f"question-{direction}"
    if key == "audience":
        return f"audience-{direction}"
    if key == "category":
        return f"category-{direction}"
    if key in {"isPublished", "is_published", "published"}:
        return f"published-{direction}"
    if key == "updatedAt":
        return f"updated-{direction}"
    if key == "createdAt":
        return "newest" if direction == "desc" else "oldest"

    return "order"


def default_dir(sort: str, requested_dir: str | None) -> str:
    if requested_dir in {"asc", "desc"}:
        return requested_dir
    if sort in {"newest"} or sort.endswith("-desc"):
        return "desc"

    return "asc"


def build_filters(
    q: str | None,
    app_key: str | None,
    audience: str | None,
    category: str | None,
    is_published: bool | None,
) -> list[object]:
    filters: list[object] = []
    trimmed_q = (q or "").strip()
    if trimmed_q:
        wildcard = f"%{trimmed_q}%"
        filters.append(
            or_(
                Faq.question.ilike(wildcard),
                Faq.answer.ilike(wildcard),
                Faq.answer_md.ilike(wildcard),
                Faq.category.ilike(wildcard),
                Faq.audience.ilike(wildcard),
                Faq.app_key.ilike(wildcard),
            )
        )

    normalized_app_key = normalize_optional(app_key)
    if app_key is not None:
        if normalized_app_key is None:
            filters.append(Faq.app_key.is_(None))
        else:
            filters.append(Faq.app_key == normalized_app_key)

    normalized_audience = normalize_optional(audience)
    if normalized_audience is not None:
        filters.append(Faq.audience == normalize_audience(normalized_audience))

    normalized_category = normalize_optional(category)
    if category is not None:
        if normalized_category is None:
            filters.append(Faq.category.is_(None))
        else:
            filters.append(Faq.category == normalized_category)

    if is_published is not None:
        filters.append(Faq.is_published.is_(is_published))

    return filters


def apply_sort(statement: Select[tuple[Faq]], sort: str, dir: str) -> Select[tuple[Faq]]:
    if sort == "newest":
        return statement.order_by(Faq.created_at.asc() if dir == "asc" else Faq.created_at.desc())
    if sort == "oldest":
        return statement.order_by(Faq.created_at.desc() if dir == "desc" else Faq.created_at.asc())
    if sort == "question-asc":
        return statement.order_by(Faq.question.asc())
    if sort == "question-desc":
        return statement.order_by(Faq.question.desc())
    if sort == "audience-asc":
        return statement.order_by(Faq.audience.asc(), Faq.sort_order.asc())
    if sort == "audience-desc":
        return statement.order_by(Faq.audience.desc(), Faq.sort_order.asc())
    if sort == "category-asc":
        return statement.order_by(Faq.category.asc(), Faq.sort_order.asc())
    if sort == "category-desc":
        return statement.order_by(Faq.category.desc(), Faq.sort_order.asc())
    if sort == "published-asc":
        return statement.order_by(Faq.is_published.asc(), Faq.sort_order.asc())
    if sort == "published-desc":
        return statement.order_by(Faq.is_published.desc(), Faq.sort_order.asc())
    if sort == "updated-asc":
        return statement.order_by(Faq.updated_at.asc())
    if sort == "updated-desc":
        return statement.order_by(Faq.updated_at.desc())
    if sort == "order-desc":
        return statement.order_by(Faq.sort_order.desc(), Faq.question.asc())

    return statement.order_by(Faq.sort_order.asc(), Faq.question.asc())


def list_admin_faqs(
    db: Session,
    page: int = 1,
    page_size: int = DEFAULT_PAGE_SIZE,
    q: str | None = None,
    app_key: str | None = None,
    audience: str | None = None,
    category: str | None = None,
    is_published: bool | None = None,
    sort: str | None = None,
    dir: str | None = None,
    sort_by: str | None = None,
    sort_direction: str | None = None,
) -> AdminFaqListResult:
    normalized_sort = normalize_sort(sort, sort_by, sort_direction)
    normalized_dir = default_dir(normalized_sort, dir)
    normalized_page_size = max(1, min(page_size, MAX_PAGE_SIZE))
    filters = build_filters(q, app_key, audience, category, is_published)

    total_statement = select(func.count(Faq.id))
    if filters:
        total_statement = total_statement.where(*filters)
    total = int(db.execute(total_statement).scalar_one())
    total_pages = max(1, ceil(total / normalized_page_size))
    normalized_page = min(max(page, 1), total_pages)
    offset = (normalized_page - 1) * normalized_page_size

    statement = select(Faq).offset(offset).limit(normalized_page_size)
    if filters:
        statement = statement.where(*filters)
    statement = apply_sort(statement, normalized_sort, normalized_dir)

    items = list(db.execute(statement).scalars().all())

    return AdminFaqListResult(
        items=items,
        total=total,
        page=normalized_page,
        page_size=normalized_page_size,
        total_pages=total_pages,
        sort=normalized_sort,
        dir=normalized_dir,
        q=q or "",
        app_key=app_key or "",
        audience=audience or "",
        category=category or "",
        is_published=is_published if is_published is not None else "",
    )


def _answer_from_payload(payload: CreateFaqRequest | UpdateFaqRequest) -> str | None:
    if payload.answer_md is not None:
        return payload.answer_md.strip()
    if payload.answer is not None:
        return payload.answer.strip()

    return None


def _next_sort_order(db: Session, audience: str) -> int:
    max_sort = db.execute(
        select(func.max(Faq.sort_order)).where(Faq.audience == audience)
    ).scalar_one_or_none()
    return int(max_sort or 0) + 1


def create_admin_faq(
    db: Session,
    admin: User,
    payload: CreateFaqRequest,
    request: Request | None = None,
) -> Faq:
    answer = _answer_from_payload(payload)
    if not answer:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Answer is required.")

    audience = normalize_audience(payload.audience)
    sort_order = payload.sort_order if isinstance(payload.sort_order, int) else _next_sort_order(db, audience)
    faq = Faq(
        id=str(uuid4()),
        question=payload.question.strip(),
        answer=answer,
        answer_md=answer,
        app_key=normalize_optional(payload.app_key),
        audience=audience,
        category=normalize_optional(payload.category),
        sort_order=sort_order,
        is_published=bool(payload.is_published),
    )
    db.add(faq)
    db.commit()
    db.refresh(faq)

    write_audit_log(
        db,
        admin,
        "admin.faq.create",
        "Faq",
        entity_id=faq.id,
        entity_label=faq.question,
        metadata={
            "appKey": faq.app_key,
            "audience": faq.audience,
            "category": faq.category,
            "sortOrder": faq.sort_order,
            "isPublished": faq.is_published,
        },
        request=request,
    )

    return faq


def _changed_fields(existing: Faq, updates: dict[str, object]) -> list[str]:
    checks = [
        ("question", "question", existing.question),
        ("answer", "answer", existing.answer),
        ("answer_md", "answer_md", existing.answer_md),
        ("app_key", "appKey", existing.app_key),
        ("audience", "audience", existing.audience),
        ("category", "category", existing.category),
        ("sort_order", "sortOrder", existing.sort_order),
        ("is_published", "is_published", existing.is_published),
    ]

    return [
        public_name
        for update_key, public_name, old_value in checks
        if update_key in updates and updates[update_key] != old_value
    ]


def update_admin_faq(
    db: Session,
    admin: User,
    faq_id: str,
    payload: UpdateFaqRequest,
    request: Request | None = None,
) -> Faq:
    existing = db.get(Faq, faq_id)
    if existing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="FAQ not found.")

    payload_fields = payload.model_fields_set
    updates: dict[str, object] = {}
    if "question" in payload_fields and payload.question is not None:
        updates["question"] = payload.question.strip()

    if "answer_md" in payload_fields or "answer" in payload_fields:
        answer = _answer_from_payload(payload)
        if not answer:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Answer is required.")
        updates["answer"] = answer
        updates["answer_md"] = answer

    if "app_key" in payload_fields:
        updates["app_key"] = normalize_optional(payload.app_key)
    if "audience" in payload_fields:
        updates["audience"] = normalize_audience(payload.audience)
    if "category" in payload_fields:
        updates["category"] = normalize_optional(payload.category)
    if isinstance(payload.sort_order, int):
        updates["sort_order"] = payload.sort_order
    if payload.is_published is not None:
        updates["is_published"] = payload.is_published

    if not updates:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No updates provided.")

    changed = _changed_fields(existing, updates)
    previous_sort_order = existing.sort_order
    next_sort_order = updates.get("sort_order", previous_sort_order)

    for key, value in updates.items():
        setattr(existing, key, value)
    existing.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(existing)

    write_audit_log(
        db,
        admin,
        "admin.faq.update",
        "Faq",
        entity_id=existing.id,
        entity_label=existing.question,
        metadata={"changed": changed or list(updates.keys())},
        request=request,
    )

    if isinstance(next_sort_order, int) and next_sort_order != previous_sort_order:
        write_audit_log(
            db,
            admin,
            "admin.faq.reorder",
            "Faq",
            entity_id=existing.id,
            entity_label=existing.question,
            metadata={
                "from": previous_sort_order,
                "to": next_sort_order,
            },
            request=request,
        )

    return existing


def delete_admin_faq(
    db: Session,
    admin: User,
    faq_id: str,
    request: Request | None = None,
) -> str:
    existing = db.get(Faq, faq_id)
    if existing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="FAQ not found.")

    metadata = {
        "appKey": existing.app_key,
        "audience": existing.audience,
        "category": existing.category,
        "sortOrder": existing.sort_order,
    }
    entity_label = existing.question
    db.delete(existing)
    db.commit()

    write_audit_log(
        db,
        admin,
        "admin.faq.delete",
        "Faq",
        entity_id=faq_id,
        entity_label=entity_label,
        metadata=metadata,
        request=request,
    )

    return faq_id
