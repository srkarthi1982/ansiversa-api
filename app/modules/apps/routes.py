from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_parent_db
from app.modules.apps.schemas import AppCatalogItemResponse, AppCatalogListResponse
from app.modules.apps.service import get_app_by_key, list_apps

router = APIRouter()


@router.get("/", response_model=AppCatalogListResponse)
def list_app_catalog(
    db: Annotated[Session, Depends(get_parent_db)],
) -> AppCatalogListResponse:
    apps = list_apps(db)

    return AppCatalogListResponse(items=apps, total=len(apps))


@router.get("/{app_key}", response_model=AppCatalogItemResponse)
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
