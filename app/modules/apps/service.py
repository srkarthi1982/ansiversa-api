from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.modules.apps.models import AppCatalogItem, Category


def list_apps(db: Session) -> list[AppCatalogItem]:
    statement = select(AppCatalogItem).order_by(
        AppCatalogItem.is_featured.desc(),
        AppCatalogItem.name.asc(),
    )

    return list(db.execute(statement).scalars().all())


def get_app_by_key(db: Session, app_key: str) -> AppCatalogItem | None:
    statement = select(AppCatalogItem).where(AppCatalogItem.key == app_key)

    return db.execute(statement).scalar_one_or_none()


def list_categories(db: Session) -> list[Category]:
    statement = select(Category).order_by(
        Category.sort_order.asc(),
        Category.name.asc(),
    )

    return list(db.execute(statement).scalars().all())


def get_category_by_key_or_slug(db: Session, category_key_or_slug: str) -> Category | None:
    statement = select(Category).where(
        or_(
            Category.key == category_key_or_slug,
            Category.slug == category_key_or_slug,
        )
    )

    return db.execute(statement).scalar_one_or_none()
