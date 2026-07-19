from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.modules.apps.models import AppCatalogItem
from app.modules.auth.models import User
from app.modules.favorites.models import Favorite


def _is_favoritable_app(app: AppCatalogItem) -> bool:
    return (
        app.visibility == "public"
        and app.status == "active"
        and app.launch_status == "live"
    )


def _app_unavailable_error() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="App is not available for favorites.",
    )


def list_user_favorites(db: Session, user: User) -> list[Favorite]:
    statement = (
        select(Favorite)
        .options(joinedload(Favorite.app))
        .where(Favorite.user_id == user.id)
        .order_by(Favorite.created_at.desc())
    )

    return list(db.execute(statement).scalars().all())


def add_user_favorite(db: Session, user: User, app_id: str) -> Favorite:
    app = db.get(AppCatalogItem, app_id)
    if app is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="App not found.",
        )

    if not _is_favoritable_app(app):
        raise _app_unavailable_error()

    existing = db.execute(
        select(Favorite)
        .options(joinedload(Favorite.app))
        .where(Favorite.user_id == user.id, Favorite.app_id == app_id)
    ).scalar_one_or_none()

    if existing:
        return existing

    favorite = Favorite(user_id=user.id, app_id=app_id)
    db.add(favorite)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        existing = db.execute(
            select(Favorite)
            .options(joinedload(Favorite.app))
            .where(Favorite.user_id == user.id, Favorite.app_id == app_id)
        ).scalar_one_or_none()
        if existing:
            return existing
        raise

    db.refresh(favorite)
    favorite.app = app

    return favorite


def remove_user_favorite(db: Session, user: User, app_id: str) -> None:
    favorite = db.execute(
        select(Favorite).where(Favorite.user_id == user.id, Favorite.app_id == app_id)
    ).scalar_one_or_none()

    if favorite is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorite not found.",
        )

    db.delete(favorite)
    db.commit()
