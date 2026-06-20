from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.modules.apps.models import AppCatalogItem, Category


def list_apps(db: Session, status_filter: str | None = None) -> list[dict[str, object]]:
    statement = select(
        AppCatalogItem.id.label("id"),
        AppCatalogItem.key.label("key"),
        AppCatalogItem.slug.label("slug"),
        AppCatalogItem.name.label("name"),
        AppCatalogItem.description.label("description"),
        AppCatalogItem.category_id.label("category_id"),
        AppCatalogItem.status.label("status"),
        AppCatalogItem.launch_status.label("launch_status"),
    ).order_by(
        AppCatalogItem.is_featured.desc(),
        AppCatalogItem.name.asc(),
    )
    if status_filter is not None:
        statement = statement.where(AppCatalogItem.status == status_filter)

    return [dict(row) for row in db.execute(statement).mappings().all()]


def get_app_by_key(db: Session, app_key: str) -> AppCatalogItem | None:
    statement = select(AppCatalogItem).where(AppCatalogItem.key == app_key)

    return db.execute(statement).scalar_one_or_none()


def list_categories(db: Session, status_filter: str | None = None) -> list[dict[str, object]]:
    statement = select(
        Category.id.label("id"),
        Category.name.label("name"),
        Category.description.label("description"),
    ).order_by(
        Category.sort_order.asc(),
        Category.name.asc(),
    )
    if status_filter is not None:
        statement = statement.where(Category.status == status_filter)

    return [dict(row) for row in db.execute(statement).mappings().all()]


def get_category_by_key_or_slug(db: Session, category_key_or_slug: str) -> Category | None:
    statement = select(Category).where(
        or_(
            Category.key == category_key_or_slug,
            Category.slug == category_key_or_slug,
        )
    )

    return db.execute(statement).scalar_one_or_none()
