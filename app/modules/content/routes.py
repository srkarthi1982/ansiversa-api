from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_parent_db
from app.modules.auth.service import get_current_user
from app.modules.auth.models import User
from .schemas import (
    AboutResponse,
    HomeResponse,
    LegalResponse,
    MetadataCreateRequest,
    MetadataResponse,
    MetadataListResponse,
    OverviewResponse,
    PricingResponse,
    # RemoveMetadataResponse,
)
from .service import (
    get_metadata as _get_metadata,
    list_metadata as _list_metadata,
    upsert_metadata as _upsert_metadata,
    delete_metadata as _delete_metadata,
)

router = APIRouter(prefix="/content", tags=["content"])


@router.get("/metadata", response_model=MetadataListResponse)
def list_metadata(db: Annotated[Session, Depends(get_parent_db)]) -> MetadataListResponse:
    items = _list_metadata(db)

    return MetadataListResponse(
        items=[MetadataResponse(key=m.key, content=m.content) for m in items],
        total=len(items),
    )

@router.get("/metadata/home", response_model=HomeResponse)
def get_home_metadata(db: Annotated[Session, Depends(get_parent_db)]) -> HomeResponse:
    m = _get_metadata(db, "home")
    if m is None:
        from fastapi import HTTPException
        from starlette import status

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Metadata not found.")

    return HomeResponse(**m.content)

@router.get("/metadata/about", response_model=AboutResponse)
def get_about_metadata(db: Annotated[Session, Depends(get_parent_db)]) -> AboutResponse:
    m = _get_metadata(db, "about")
    if m is None:
        from fastapi import HTTPException
        from starlette import status

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Metadata not found.")

    return AboutResponse(**m.content)

@router.get("/metadata/terms", response_model=LegalResponse)
def get_terms_metadata(db: Annotated[Session, Depends(get_parent_db)]) -> LegalResponse:
    m = _get_metadata(db, "terms")
    if m is None:
        from fastapi import HTTPException
        from starlette import status

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Metadata not found.")

    return LegalResponse(**m.content)

@router.get("/metadata/privacy", response_model=LegalResponse)
def get_privacy_metadata(db: Annotated[Session, Depends(get_parent_db)]) -> LegalResponse:
    m = _get_metadata(db, "privacy")
    if m is None:
        from fastapi import HTTPException
        from starlette import status

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Metadata not found.")

    return LegalResponse(**m.content)

@router.get("/metadata/pricing", response_model=PricingResponse)
def get_pricing_metadata(db: Annotated[Session, Depends(get_parent_db)]) -> PricingResponse:
    m = _get_metadata(db, "pricing")
    if m is None:
        from fastapi import HTTPException
        from starlette import status

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Metadata not found.")

    return PricingResponse(**m.content)

@router.get("/metadata/overview/{app_key}", response_model=OverviewResponse)
def get_overview_metadata(app_key: str, db: Annotated[Session, Depends(get_parent_db)]) -> OverviewResponse:
    m = _get_metadata(db, f"overview:{app_key}")
    if m is None:
        from fastapi import HTTPException
        from starlette import status

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Metadata not found.")

    return OverviewResponse(**m.content)

@router.put("/metadata/{key}", response_model=MetadataResponse)
def put_metadata(
    key: str,
    payload: MetadataCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_parent_db)],
) -> MetadataResponse:
    m = _upsert_metadata(db, key, payload.content)

    return MetadataResponse(key=m.key, content=m.content)


@router.delete("/metadata/{key}")
def delete_metadata(
    key: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_parent_db)],
):
    _delete_metadata(db, key)

    return {"ok": True, "key": key}
