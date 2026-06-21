from dataclasses import dataclass
from math import ceil

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.modules.faqs.models import Faq


@dataclass(frozen=True)
class FaqListResult:
    items: list[dict[str, str]]
    total: int
    page: int
    page_size: int
    total_pages: int


def _normalize_optional_filter(value: str | None) -> str | None:
    if value is None:
        return None

    normalized = value.strip()
    if not normalized:
        return None

    return normalized


def _normalize_audience(value: str | None) -> str:
    return (_normalize_optional_filter(value) or "user").lower()


def list_public_faqs(
    db: Session,
    app_key: str | None = None,
    query: str | None = None,
    page: int = 1,
    page_size: int = 20,
    audience: str = "user",
) -> FaqListResult:
    normalized_app_key = _normalize_optional_filter(app_key)
    normalized_query = _normalize_optional_filter(query)
    normalized_audience = _normalize_audience(audience)

    filters = [
        Faq.is_published.is_(True),
        Faq.audience == normalized_audience,
    ]

    if normalized_app_key is None:
        filters.append(Faq.app_key.is_(None))
    else:
        filters.append(or_(Faq.app_key.is_(None), Faq.app_key == normalized_app_key))

    if normalized_query is not None:
        search = f"%{normalized_query}%"
        filters.append(
            or_(
                Faq.question.ilike(search),
                Faq.answer.ilike(search),
                Faq.answer_md.ilike(search),
            )
        )

    total_statement = select(func.count(Faq.id)).where(*filters)
    total = int(db.execute(total_statement).scalar_one())
    offset = (page - 1) * page_size

    items_statement = (
        select(
            Faq.id,
            Faq.question,
            Faq.answer,
        )
        .where(*filters)
        .order_by(Faq.sort_order.asc(), Faq.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    items = [dict(row) for row in db.execute(items_statement).mappings().all()]

    return FaqListResult(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=ceil(total / page_size) if total else 0,
    )
