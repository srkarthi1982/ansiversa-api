from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from app.modules.apps.models import AppCatalogItem, Category


def get_app_catalog(db: Session, status_filter: str | None = None) -> dict[str, object]:
    app_join_condition = AppCatalogItem.category_id == Category.id
    if status_filter is not None:
        app_join_condition = and_(
            app_join_condition,
            AppCatalogItem.status == status_filter,
        )

    statement = (
        select(
            AppCatalogItem.id.label("app_id"),
            AppCatalogItem.key.label("app_key"),
            AppCatalogItem.slug.label("app_slug"),
            AppCatalogItem.name.label("app_name"),
            AppCatalogItem.description.label("app_description"),
            AppCatalogItem.category_id.label("app_category_id"),
            AppCatalogItem.status.label("app_status"),
            AppCatalogItem.launch_status.label("app_launch_status"),
            AppCatalogItem.destination_progress.label("app_destination_progress"),
            AppCatalogItem.destination_status.label("app_destination_status"),
            AppCatalogItem.is_featured.label("app_is_featured"),
            Category.id.label("category_id"),
            Category.name.label("category_name"),
            Category.description.label("category_description"),
            Category.sort_order.label("category_sort_order"),
        )
        .select_from(Category)
        .outerjoin(AppCatalogItem, app_join_condition)
    )
    if status_filter is not None:
        statement = statement.where(Category.status == status_filter)

    rows = db.execute(statement).mappings().all()
    apps_by_id: dict[str, dict[str, object]] = {}
    categories_by_id: dict[str, dict[str, object]] = {}
    category_order: dict[str, tuple[int, str]] = {}

    for row in rows:
        category_id = row["category_id"]
        categories_by_id[category_id] = {
            "id": category_id,
            "name": row["category_name"],
            "description": row["category_description"],
        }
        category_order[category_id] = (
            row["category_sort_order"],
            row["category_name"],
        )

        app_id = row["app_id"]
        if app_id is None:
            continue

        apps_by_id[app_id] = {
            "id": app_id,
            "key": row["app_key"],
            "slug": row["app_slug"],
            "name": row["app_name"],
            "description": row["app_description"],
            "category_id": row["app_category_id"],
            "status": row["app_status"],
            "launch_status": row["app_launch_status"],
            "destination_progress": row["app_destination_progress"],
            "destination_status": row["app_destination_status"],
            "_is_featured": row["app_is_featured"],
        }

    apps = sorted(
        apps_by_id.values(),
        key=lambda app: (not app["_is_featured"], str(app["name"])),
    )
    for app in apps:
        del app["_is_featured"]

    categories = sorted(
        categories_by_id.values(),
        key=lambda category: category_order[category["id"]],
    )
    live_count = sum(1 for app in apps if app["launch_status"] == "live")

    return {
        "apps": apps,
        "categories": categories,
        "counts": {
            "total": len(apps),
            "live": live_count,
            "coming_soon": len(apps) - live_count,
        },
    }


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
        AppCatalogItem.destination_progress.label("destination_progress"),
        AppCatalogItem.destination_status.label("destination_status"),
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
