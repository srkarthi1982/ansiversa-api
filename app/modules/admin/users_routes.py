from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_parent_db
from app.modules.admin.schemas import AdminUserListResponse, AdminUserResponse
from app.modules.admin.users_service import get_admin_user, list_admin_users
from app.modules.auth.dependencies import require_admin_user
from app.modules.auth.models import User

router = APIRouter()


@router.get("/users", response_model=AdminUserListResponse)
def list_users(
    current_admin: Annotated[User, Depends(require_admin_user)],
    db: Annotated[Session, Depends(get_parent_db)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(alias="pageSize", ge=1, le=200)] = 10,
    q: str | None = None,
    status: str | None = None,
    role_id: Annotated[int | None, Query(alias="roleId", ge=1)] = None,
    plan: str | None = None,
    plan_status: Annotated[str | None, Query(alias="planStatus")] = None,
    country_code: Annotated[str | None, Query(alias="countryCode")] = None,
    sort: str | None = None,
    dir: str | None = None,
    sort_by: Annotated[str | None, Query(alias="sortBy")] = None,
    sort_direction: Annotated[str | None, Query(alias="sortDirection")] = None,
) -> AdminUserListResponse:
    _ = current_admin
    result = list_admin_users(
        db,
        page=page,
        page_size=page_size,
        q=q,
        status_filter=status,
        role_id=role_id,
        plan=plan,
        plan_status=plan_status,
        country_code=country_code,
        sort=sort,
        dir=dir,
        sort_by=sort_by,
        sort_direction=sort_direction,
    )

    return AdminUserListResponse(
        items=result.items,
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        total_pages=result.total_pages,
        sort=result.sort,
        dir=result.dir,  # type: ignore[arg-type]
        q=result.q,
        status=result.status,
        role_id=result.role_id,
        plan=result.plan,
        plan_status=result.plan_status,
        country_code=result.country_code,
    )


@router.get("/users/{user_id}", response_model=AdminUserResponse)
def get_user(
    user_id: str,
    current_admin: Annotated[User, Depends(require_admin_user)],
    db: Annotated[Session, Depends(get_parent_db)],
) -> AdminUserResponse:
    _ = current_admin
    return get_admin_user(db, user_id)  # type: ignore[return-value]
