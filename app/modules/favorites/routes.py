from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_parent_db
from app.modules.auth.models import User
from app.modules.auth.service import get_current_user
from app.modules.favorites.models import Favorite
from app.modules.favorites.schemas import (
    AddFavoriteRequest,
    AddFavoriteResponse,
    FavoriteAppResponse,
    FavoriteListResponse,
    FavoriteResponse,
    RemoveFavoriteResponse,
)
from app.modules.favorites.service import (
    add_user_favorite,
    list_user_favorites,
    remove_user_favorite,
)

router = APIRouter()


def _serialize_favorite(favorite: Favorite) -> FavoriteResponse:
    return FavoriteResponse(
        favorite_id=favorite.id,
        created_at=favorite.created_at,
        app=FavoriteAppResponse.model_validate(favorite.app),
    )


@router.get("/favorites", response_model=FavoriteListResponse)
def list_favorites(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_parent_db)],
) -> FavoriteListResponse:
    favorites = list_user_favorites(db, current_user)

    return FavoriteListResponse(
        items=[_serialize_favorite(favorite) for favorite in favorites],
        total=len(favorites),
    )


@router.post("/favorites", response_model=AddFavoriteResponse)
def add_favorite(
    payload: AddFavoriteRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_parent_db)],
) -> AddFavoriteResponse:
    favorite = add_user_favorite(db, current_user, payload.app_id)
    response = _serialize_favorite(favorite)

    return AddFavoriteResponse(
        favorite_id=response.favorite_id,
        created_at=response.created_at,
        app=response.app,
    )


@router.delete("/favorites/{app_id}", response_model=RemoveFavoriteResponse)
def remove_favorite(
    app_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_parent_db)],
) -> RemoveFavoriteResponse:
    remove_user_favorite(db, current_user, app_id)

    return RemoveFavoriteResponse(ok=True, app_id=app_id)
