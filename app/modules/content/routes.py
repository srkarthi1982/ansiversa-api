import hashlib
import json
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.encoders import jsonable_encoder
from starlette import status
from starlette.responses import JSONResponse
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
    get_metadata_content as _get_metadata_content,
    list_metadata as _list_metadata,
    upsert_metadata as _upsert_metadata,
    delete_metadata as _delete_metadata,
)

router = APIRouter(prefix="/content", tags=["content"])
METADATA_CACHE_CONTROL = "no-cache"


def _metadata_etag(content: object) -> str:
    encoded = jsonable_encoder(content)
    serialized = json.dumps(
        encoded,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    return f'W/"{hashlib.sha256(serialized).hexdigest()}"'


def _cached_json_response(request: Request, content: object) -> Response:
    encoded = jsonable_encoder(content)
    etag = _metadata_etag(encoded)
    headers = {
        "Cache-Control": METADATA_CACHE_CONTROL,
        "ETag": etag,
        "Vary": "Origin",
    }

    if request.headers.get("if-none-match") == etag:
        return Response(status_code=status.HTTP_304_NOT_MODIFIED, headers=headers)

    return JSONResponse(content=encoded, headers=headers)


def _not_found() -> None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Metadata not found.")


@router.get("/metadata", response_model=MetadataListResponse)
def list_metadata(
    request: Request,
    db: Annotated[Session, Depends(get_parent_db)],
) -> Response:
    items = _list_metadata(db)
    response = MetadataListResponse(
        items=[MetadataResponse(key=m.key, content=m.content) for m in items],
        total=len(items),
    )

    return _cached_json_response(request, response)

@router.get("/metadata/home", response_model=HomeResponse)
def get_home_metadata(
    request: Request,
    db: Annotated[Session, Depends(get_parent_db)],
) -> Response:
    content = _get_metadata_content(db, "home")
    if content is None:
        _not_found()

    return _cached_json_response(request, HomeResponse(**content))

@router.get("/metadata/about", response_model=AboutResponse)
def get_about_metadata(
    request: Request,
    db: Annotated[Session, Depends(get_parent_db)],
) -> Response:
    content = _get_metadata_content(db, "about")
    if content is None:
        _not_found()

    return _cached_json_response(request, AboutResponse(**content))

@router.get("/metadata/terms", response_model=LegalResponse)
def get_terms_metadata(
    request: Request,
    db: Annotated[Session, Depends(get_parent_db)],
) -> Response:
    content = _get_metadata_content(db, "terms")
    if content is None:
        _not_found()

    return _cached_json_response(request, LegalResponse(**content))

@router.get("/metadata/privacy", response_model=LegalResponse)
def get_privacy_metadata(
    request: Request,
    db: Annotated[Session, Depends(get_parent_db)],
) -> Response:
    content = _get_metadata_content(db, "privacy")
    if content is None:
        _not_found()

    return _cached_json_response(request, LegalResponse(**content))

@router.get("/metadata/pricing", response_model=PricingResponse)
def get_pricing_metadata(
    request: Request,
    db: Annotated[Session, Depends(get_parent_db)],
) -> Response:
    content = _get_metadata_content(db, "pricing")
    if content is None:
        _not_found()

    return _cached_json_response(request, PricingResponse(**content))

@router.get("/metadata/overview/{app_key}", response_model=OverviewResponse)
def get_overview_metadata(
    app_key: str,
    request: Request,
    db: Annotated[Session, Depends(get_parent_db)],
) -> Response:
    content = _get_metadata_content(db, f"overview:{app_key}")
    if content is None:
        _not_found()

    return _cached_json_response(request, OverviewResponse(**content))

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
