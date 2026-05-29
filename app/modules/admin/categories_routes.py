from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.database import get_parent_db
from app.modules.admin.schemas import (
    AdminCategoryListResponse,
    CategoryMutationResponse,
    CreateCategoryRequest,
    DeleteCategoryResponse,
    UpdateCategoryRequest,
)
from app.modules.admin.categories_service import (
    create_admin_category,
    delete_admin_category,
    list_admin_categories,
    update_admin_category,
)
from app.modules.auth.dependencies import require_admin_user
from app.modules.auth.models import User

router = APIRouter()


@router.get("/categories", response_model=AdminCategoryListResponse)
def list_categories(
    current_admin: Annotated[User, Depends(require_admin_user)],
    db: Annotated[Session, Depends(get_parent_db)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(alias="pageSize", ge=1, le=200)] = 10,
    q: str | None = None,
    status: str | None = None,
    sort: str | None = None,
    dir: str | None = None,
    sort_by: Annotated[str | None, Query(alias="sortBy")] = None,
    sort_direction: Annotated[str | None, Query(alias="sortDirection")] = None,
) -> AdminCategoryListResponse:
    _ = current_admin
    result = list_admin_categories(
        db,
        page=page,
        page_size=page_size,
        q=q,
        status_filter=status,
        sort=sort,
        dir=dir,
        sort_by=sort_by,
        sort_direction=sort_direction,
    )

    return AdminCategoryListResponse(
        items=result.items,
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        total_pages=result.total_pages,
        sort=result.sort,
        dir=result.dir,  # type: ignore[arg-type]
        q=result.q,
        status=result.status,
    )


@router.post("/categories", response_model=CategoryMutationResponse)
def create_category(
    payload: CreateCategoryRequest,
    current_admin: Annotated[User, Depends(require_admin_user)],
    db: Annotated[Session, Depends(get_parent_db)],
    request: Request,
) -> CategoryMutationResponse:
    category_id = create_admin_category(db, current_admin, payload, request=request)

    return CategoryMutationResponse(ok=True, id=category_id)


@router.patch("/categories/{category_id}", response_model=CategoryMutationResponse)
def update_category(
    category_id: str,
    payload: UpdateCategoryRequest,
    current_admin: Annotated[User, Depends(require_admin_user)],
    db: Annotated[Session, Depends(get_parent_db)],
    request: Request,
) -> CategoryMutationResponse:
    updated_id = update_admin_category(
        db,
        current_admin,
        category_id,
        payload,
        request=request,
    )

    return CategoryMutationResponse(ok=True, id=updated_id)


@router.delete("/categories/{category_id}", response_model=DeleteCategoryResponse)
def delete_category(
    category_id: str,
    current_admin: Annotated[User, Depends(require_admin_user)],
    db: Annotated[Session, Depends(get_parent_db)],
    request: Request,
) -> DeleteCategoryResponse:
    delete_admin_category(db, current_admin, category_id, request=request)

    return DeleteCategoryResponse(ok=True)
