from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_parent_db
from app.modules.faqs.schemas import FaqListResponse
from app.modules.faqs.service import list_public_faqs

router = APIRouter()


@router.get("", response_model=FaqListResponse)
def list_faqs(
    db: Annotated[Session, Depends(get_parent_db)],
    app_key: Annotated[str | None, Query(alias="appKey")] = None,
    q: Annotated[str | None, Query(min_length=1)] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(alias="pageSize", ge=1, le=100)] = 20,
    audience: Annotated[str, Query(min_length=1)] = "user",
) -> FaqListResponse:
    result = list_public_faqs(
        db,
        app_key=app_key,
        query=q,
        page=page,
        page_size=page_size,
        audience=audience,
    )

    return FaqListResponse(
        items=result.items,
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        total_pages=result.total_pages,
    )
