from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_parent_db
from app.modules.auth.models import User
from app.modules.auth.service import get_current_user
from app.modules.apps.models import AppCatalogItem
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
from app.modules.activity.service import record_activity_safely

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
    record_activity_safely(user_id=current_user.id, activity_type="favorited",
        title=f"Favorited {favorite.app.name}", description=f"Added {favorite.app.name} to Your Apps.",
        source="app", source_app_slug=favorite.app.slug, action_route=f"/{favorite.app.slug}",
        action_label=f"Open {favorite.app.name}", entity_type="app", entity_id=favorite.app.id,
        deduplication_window=timedelta(minutes=10))

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
    app = db.get(AppCatalogItem, app_id)
    remove_user_favorite(db, current_user, app_id)
    if app:
        record_activity_safely(user_id=current_user.id, activity_type="unfavorited",
            title=f"Removed {app.name} from favorites", description=f"Removed {app.name} from Your Apps.",
            source="app", source_app_slug=app.slug, action_route=f"/{app.slug}",
            action_label=f"Open {app.name}", entity_type="app", entity_id=app.id,
            deduplication_window=timedelta(minutes=10))

    return RemoveFavoriteResponse(ok=True, app_id=app_id)
