from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_parent_db
from app.modules.auth.service import get_current_user
from app.modules.auth.models import User
from .schemas import (
    MetadataCreateRequest,
    MetadataResponse,
    MetadataListResponse,
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


@router.get("/metadata/{key}", response_model=MetadataResponse)
def get_metadata(key: str, db: Annotated[Session, Depends(get_parent_db)]) -> MetadataResponse:
    m = _get_metadata(db, key)
    if m is None:
        from fastapi import HTTPException
        from starlette import status

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Metadata not found.")

    return MetadataResponse(key=m.key, content=m.content)


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