from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.database import get_parent_db
from app.modules.admin.apps_service import (
    create_admin_app,
    delete_admin_app,
    get_admin_apps_meta,
    list_admin_apps,
    update_admin_app,
)
from app.modules.admin.schemas import (
    AdminAppListResponse,
    AdminAppsMetaResponse,
    AppMutationResponse,
    CreateAppRequest,
    DeleteAppResponse,
    UpdateAppRequest,
)
from app.modules.auth.dependencies import require_admin_user
from app.modules.auth.models import User

router = APIRouter()


@router.get("/apps", response_model=AdminAppListResponse)
def list_apps(
    current_admin: Annotated[User, Depends(require_admin_user)],
    db: Annotated[Session, Depends(get_parent_db)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(alias="pageSize", ge=1, le=200)] = 10,
    q: str | None = None,
    status: str | None = None,
    category_id: Annotated[str | None, Query(alias="categoryId")] = None,
    launch_status: Annotated[str | None, Query(alias="launchStatus")] = None,
    visibility: str | None = None,
    pricing_gate: Annotated[str | None, Query(alias="pricingGate")] = None,
    featured_only: Annotated[bool, Query(alias="featuredOnly")] = False,
    sort: str | None = None,
    dir: str | None = None,
    sort_by: Annotated[str | None, Query(alias="sortBy")] = None,
    sort_direction: Annotated[str | None, Query(alias="sortDirection")] = None,
) -> AdminAppListResponse:
    _ = current_admin
    result = list_admin_apps(
        db,
        page=page,
        page_size=page_size,
        q=q,
        status_filter=status,
        category_id=category_id,
        launch_status=launch_status,
        visibility=visibility,
        pricing_gate=pricing_gate,
        featured_only=featured_only,
        sort=sort,
        dir=dir,
        sort_by=sort_by,
        sort_direction=sort_direction,
    )

    return AdminAppListResponse(
        items=result.items,
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        total_pages=result.total_pages,
        sort=result.sort,
        dir=result.dir,  # type: ignore[arg-type]
        q=result.q,
        category_id=result.category_id,
        status=result.status,
        launch_status=result.launch_status,
        visibility=result.visibility,
        pricing_gate=result.pricing_gate,
        featured_only=result.featured_only,
    )


@router.get("/apps/meta", response_model=AdminAppsMetaResponse)
def get_apps_meta(
    current_admin: Annotated[User, Depends(require_admin_user)],
    db: Annotated[Session, Depends(get_parent_db)],
) -> AdminAppsMetaResponse:
    _ = current_admin
    return AdminAppsMetaResponse(**get_admin_apps_meta(db))


@router.post("/apps", response_model=AppMutationResponse)
def create_app(
    payload: CreateAppRequest,
    current_admin: Annotated[User, Depends(require_admin_user)],
    db: Annotated[Session, Depends(get_parent_db)],
    request: Request,
) -> AppMutationResponse:
    app_id = create_admin_app(db, current_admin, payload, request=request)

    return AppMutationResponse(ok=True, id=app_id)


@router.patch("/apps/{app_id}", response_model=AppMutationResponse)
def update_app(
    app_id: str,
    payload: UpdateAppRequest,
    current_admin: Annotated[User, Depends(require_admin_user)],
    db: Annotated[Session, Depends(get_parent_db)],
    request: Request,
) -> AppMutationResponse:
    updated_id = update_admin_app(
        db,
        current_admin,
        app_id,
        payload,
        request=request,
    )

    return AppMutationResponse(ok=True, id=updated_id)


@router.delete("/apps/{app_id}", response_model=DeleteAppResponse)
def delete_app(
    app_id: str,
    current_admin: Annotated[User, Depends(require_admin_user)],
    db: Annotated[Session, Depends(get_parent_db)],
    request: Request,
) -> DeleteAppResponse:
    delete_admin_app(db, current_admin, app_id, request=request)

    return DeleteAppResponse(ok=True)
