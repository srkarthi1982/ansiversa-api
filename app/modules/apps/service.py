from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.apps.models import AppCatalogItem


def list_apps(db: Session) -> list[AppCatalogItem]:
    statement = select(AppCatalogItem).order_by(
        AppCatalogItem.is_featured.desc(),
        AppCatalogItem.name.asc(),
    )

    return list(db.execute(statement).scalars().all())


def get_app_by_key(db: Session, app_key: str) -> AppCatalogItem | None:
    statement = select(AppCatalogItem).where(AppCatalogItem.key == app_key)

    return db.execute(statement).scalar_one_or_none()
