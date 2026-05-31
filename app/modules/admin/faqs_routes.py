from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.database import get_parent_db
from app.modules.admin.faqs_service import (
    create_admin_faq,
    delete_admin_faq,
    list_admin_faqs,
    update_admin_faq,
)
from app.modules.admin.schemas import (
    AdminFaqListResponse,
    CreateFaqRequest,
    DeleteFaqResponse,
    FaqMutationResponse,
    UpdateFaqRequest,
)
from app.modules.auth.dependencies import require_admin_user
from app.modules.auth.models import User

router = APIRouter()


@router.get("/faqs", response_model=AdminFaqListResponse)
def list_faqs(
    current_admin: Annotated[User, Depends(require_admin_user)],
    db: Annotated[Session, Depends(get_parent_db)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(alias="pageSize", ge=1, le=200)] = 10,
    q: str | None = None,
    app_key: Annotated[str | None, Query(alias="appKey")] = None,
    audience: str | None = None,
    category: str | None = None,
    is_published: Annotated[bool | None, Query(alias="isPublished")] = None,
    sort: str | None = None,
    dir: str | None = None,
    sort_by: Annotated[str | None, Query(alias="sortBy")] = None,
    sort_direction: Annotated[str | None, Query(alias="sortDirection")] = None,
) -> AdminFaqListResponse:
    _ = current_admin
    result = list_admin_faqs(
        db,
        page=page,
        page_size=page_size,
        q=q,
        app_key=app_key,
        audience=audience,
        category=category,
        is_published=is_published,
        sort=sort,
        dir=dir,
        sort_by=sort_by,
        sort_direction=sort_direction,
    )

    return AdminFaqListResponse(
        items=result.items,
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        total_pages=result.total_pages,
        sort=result.sort,
        dir=result.dir,  # type: ignore[arg-type]
        q=result.q,
        app_key=result.app_key,
        audience=result.audience,
        category=result.category,
        is_published=result.is_published,
    )


@router.post("/faqs", response_model=FaqMutationResponse)
def create_faq(
    payload: CreateFaqRequest,
    current_admin: Annotated[User, Depends(require_admin_user)],
    db: Annotated[Session, Depends(get_parent_db)],
    request: Request,
) -> FaqMutationResponse:
    faq = create_admin_faq(db, current_admin, payload, request=request)

    return FaqMutationResponse(ok=True, id=faq.id, item=faq)


@router.patch("/faqs/{faq_id}", response_model=FaqMutationResponse)
def update_faq(
    faq_id: str,
    payload: UpdateFaqRequest,
    current_admin: Annotated[User, Depends(require_admin_user)],
    db: Annotated[Session, Depends(get_parent_db)],
    request: Request,
) -> FaqMutationResponse:
    faq = update_admin_faq(db, current_admin, faq_id, payload, request=request)

    return FaqMutationResponse(ok=True, id=faq.id, item=faq)


@router.delete("/faqs/{faq_id}", response_model=DeleteFaqResponse)
def delete_faq(
    faq_id: str,
    current_admin: Annotated[User, Depends(require_admin_user)],
    db: Annotated[Session, Depends(get_parent_db)],
    request: Request,
) -> DeleteFaqResponse:
    deleted_id = delete_admin_faq(db, current_admin, faq_id, request=request)

    return DeleteFaqResponse(ok=True, id=deleted_id)
