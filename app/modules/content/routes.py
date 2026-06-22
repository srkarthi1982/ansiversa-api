from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import JSONResponse

from app.core.database import get_parent_db
from app.modules.auth.dependencies import require_admin_user
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
    get_metadata_content as _get_metadata_content,
    list_metadata as _list_metadata,
    upsert_metadata as _upsert_metadata,
    delete_metadata as _delete_metadata,
)

router = APIRouter(prefix="/content", tags=["content"])
METADATA_NO_STORE_HEADERS = {
    "Cache-Control": "no-store, max-age=0",
    "Pragma": "no-cache",
    "Expires": "0",
    "Vary": "Origin",
}


def _metadata_json_response(content: object) -> Response:
    return JSONResponse(
        content=jsonable_encoder(content),
        headers=METADATA_NO_STORE_HEADERS,
    )


def _not_found() -> None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Metadata not found.")


def _required_metadata_content(db: Session, key: str) -> dict:
    content = _get_metadata_content(db, key)
    if content is None:
        _not_found()

    return content


@router.get("/metadata", response_model=MetadataListResponse)
def list_metadata(
    db: Annotated[Session, Depends(get_parent_db)],
) -> Response:
    items = _list_metadata(db)
    response = MetadataListResponse(
        items=[MetadataResponse(key=m.key, content=m.content) for m in items],
        total=len(items),
    )

    return _metadata_json_response(response)

@router.get("/metadata/home", response_model=HomeResponse)
def get_home_metadata(
    db: Annotated[Session, Depends(get_parent_db)],
) -> Response:
    content = _required_metadata_content(db, "home")

    return _metadata_json_response(HomeResponse(**content))

@router.get("/metadata/about", response_model=AboutResponse)
def get_about_metadata(
    db: Annotated[Session, Depends(get_parent_db)],
) -> Response:
    content = _required_metadata_content(db, "about")

    return _metadata_json_response(AboutResponse(**content))

@router.get("/metadata/terms", response_model=LegalResponse)
def get_terms_metadata(
    db: Annotated[Session, Depends(get_parent_db)],
) -> Response:
    content = _required_metadata_content(db, "terms")

    return _metadata_json_response(LegalResponse(**content))

@router.get("/metadata/privacy", response_model=LegalResponse)
def get_privacy_metadata(
    db: Annotated[Session, Depends(get_parent_db)],
) -> Response:
    content = _required_metadata_content(db, "privacy")

    return _metadata_json_response(LegalResponse(**content))

@router.get("/metadata/pricing", response_model=PricingResponse)
def get_pricing_metadata(
    db: Annotated[Session, Depends(get_parent_db)],
) -> Response:
    content = _required_metadata_content(db, "pricing")

    return _metadata_json_response(PricingResponse(**content))

@router.get("/metadata/overview/{app_key}", response_model=OverviewResponse)
def get_overview_metadata(
    app_key: str,
    db: Annotated[Session, Depends(get_parent_db)],
) -> Response:
    content = _required_metadata_content(db, f"overview:{app_key}")

    return _metadata_json_response(OverviewResponse(**content))

@router.put("/metadata/{key}", response_model=MetadataResponse)
def put_metadata(
    key: str,
    payload: MetadataCreateRequest,
    current_user: Annotated[User, Depends(require_admin_user)],
    db: Annotated[Session, Depends(get_parent_db)],
) -> MetadataResponse:
    m = _upsert_metadata(db, key, payload.content)

    return MetadataResponse(key=m.key, content=m.content)


@router.delete("/metadata/{key}")
def delete_metadata(
    key: str,
    current_user: Annotated[User, Depends(require_admin_user)],
    db: Annotated[Session, Depends(get_parent_db)],
):
    _delete_metadata(db, key)

    return {"ok": True, "key": key}
