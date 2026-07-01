from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_parent_db
from app.core.timing import timing_span
from app.modules.apps.schemas import (
    AppCatalogItemResponse,
    AppCatalogResponse,
    AppCatalogListResponse,
    CategoryListResponse,
    CategoryResponse,
)
from app.modules.apps.service import (
    get_app_by_key,
    get_category_by_key_or_slug,
    list_apps,
    list_categories,
)

apps_router = APIRouter()
categories_router = APIRouter()
StatusFilter = Literal["active"]


@apps_router.get("/", response_model=AppCatalogListResponse)
def list_app_catalog(
    db: Annotated[Session, Depends(get_parent_db)],
    status_filter: Annotated[StatusFilter | None, Query(alias="status")] = None,
) -> AppCatalogListResponse:
    with timing_span("apps.list_apps"):
        apps = list_apps(db, status_filter=status_filter)

    with timing_span("apps.build_response_model"):
        return AppCatalogListResponse(items=apps, total=len(apps))


@apps_router.get("/catalog", response_model=AppCatalogResponse)
def get_app_catalog(
    db: Annotated[Session, Depends(get_parent_db)],
    status_filter: Annotated[StatusFilter | None, Query(alias="status")] = None,
) -> AppCatalogResponse:
    with timing_span("apps.catalog.list_apps"):
        apps = list_apps(db, status_filter=status_filter)

    with timing_span("apps.catalog.list_categories"):
        categories = list_categories(db, status_filter=status_filter)

    with timing_span("apps.catalog.build_response_model"):
        live_count = sum(1 for app in apps if app["launch_status"] == "live")
        return AppCatalogResponse(
            apps=apps,
            categories=categories,
            counts={
                "total": len(apps),
                "live": live_count,
                "coming_soon": len(apps) - live_count,
            },
        )


@apps_router.get("/{app_key}", response_model=AppCatalogItemResponse)
def get_app_catalog_item(
    app_key: str,
    db: Annotated[Session, Depends(get_parent_db)],
) -> AppCatalogItemResponse:
    app = get_app_by_key(db, app_key)
    if app is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="App not found.",
        )

    return app


@categories_router.get("/", response_model=CategoryListResponse)
def list_category_catalog(
    db: Annotated[Session, Depends(get_parent_db)],
    status_filter: Annotated[StatusFilter | None, Query(alias="status")] = None,
) -> CategoryListResponse:
    with timing_span("categories.list_categories"):
        categories = list_categories(db, status_filter=status_filter)

    with timing_span("categories.build_response_model"):
        return CategoryListResponse(items=categories, total=len(categories))


@categories_router.get("/{category_key_or_slug}", response_model=CategoryResponse)
def get_category_catalog_item(
    category_key_or_slug: str,
    db: Annotated[Session, Depends(get_parent_db)],
) -> CategoryResponse:
    category = get_category_by_key_or_slug(db, category_key_or_slug)
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found.",
        )

    return category
