import re
from dataclasses import dataclass
from datetime import datetime
from math import ceil

from fastapi import HTTPException, Request, status
from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session

from app.modules.admin.schemas import CreateCategoryRequest, UpdateCategoryRequest
from app.modules.apps.models import AppCatalogItem, Category
from app.modules.audit.service import write_audit_log
from app.modules.auth.models import User


DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 200
STATUS_OPTIONS = {"active", "disabled"}
SORT_OPTIONS = {
    "newest",
    "oldest",
    "name-asc",
    "name-desc",
    "id-asc",
    "id-desc",
    "key-asc",
    "key-desc",
    "sortOrder",
    "sortOrder-asc",
    "sortOrder-desc",
    "apps-asc",
    "apps-desc",
    "status-asc",
    "status-desc",
    "updated-asc",
    "updated-desc",
}


@dataclass(frozen=True)
class AdminCategoryListItem:
    id: str
    key: str | None
    slug: str
    name: str
    description: str | None
    sort_order: int
    status: str
    created_at: datetime
    updated_at: datetime
    apps_count: int


@dataclass(frozen=True)
class AdminCategoryListResult:
    items: list[AdminCategoryListItem]
    total: int
    page: int
    page_size: int
    total_pages: int
    sort: str
    dir: str
    q: str
    status: str


def normalize_key(value: str | None) -> str:
    if value is None:
        return ""

    return re.sub(r"\s+", "-", value.strip().lower())


def validate_status(value: str | None) -> str:
    normalized = (value or "active").strip().lower()
    if normalized in STATUS_OPTIONS:
        return normalized

    return "active"


def normalize_sort(sort: str | None, sort_by: str | None, sort_direction: str | None) -> str:
    if sort and sort in SORT_OPTIONS:
        return sort

    key = (sort_by or "").strip()
    direction = "desc" if (sort_direction or "").strip().lower() == "desc" else "asc"
    if key == "name":
        return f"name-{direction}"
    if key == "id":
        return f"id-{direction}"
    if key == "key":
        return f"key-{direction}"
    if key == "sortOrder":
        return f"sortOrder-{direction}"
    if key == "apps":
        return f"apps-{direction}"
    if key == "status":
        return f"status-{direction}"
    if key == "updatedAt":
        return f"updated-{direction}"
    if key == "createdAt":
        return "newest" if direction == "desc" else "oldest"

    return "sortOrder"


def default_dir(sort: str, requested_dir: str | None) -> str:
    if requested_dir in {"asc", "desc"}:
        return requested_dir

    if sort == "newest":
        return "desc"

    if sort.endswith("-desc"):
        return "desc"

    return "asc"


def build_filters(q: str | None, status_filter: str | None) -> list[object]:
    filters: list[object] = []
    trimmed_q = (q or "").strip()
    if trimmed_q:
        wildcard = f"%{trimmed_q}%"
        filters.append(
            or_(
                Category.name.ilike(wildcard),
                Category.id.ilike(wildcard),
                Category.slug.ilike(wildcard),
                Category.key.ilike(wildcard),
                Category.description.ilike(wildcard),
            )
        )

    if status_filter:
        filters.append(Category.status == validate_status(status_filter))

    return filters


def apply_sort(
    statement: Select[tuple[Category, int]],
    sort: str,
    dir: str,
    apps_count_expr: object,
) -> Select[tuple[Category, int]]:
    if sort == "name-asc":
        return statement.order_by(Category.name.asc())
    if sort == "name-desc":
        return statement.order_by(Category.name.desc())
    if sort == "id-asc":
        return statement.order_by(Category.id.asc())
    if sort == "id-desc":
        return statement.order_by(Category.id.desc())
    if sort == "key-asc":
        return statement.order_by(Category.key.asc())
    if sort == "key-desc":
        return statement.order_by(Category.key.desc())
    if sort == "sortOrder-asc":
        return statement.order_by(Category.sort_order.asc(), Category.name.asc())
    if sort == "sortOrder-desc":
        return statement.order_by(Category.sort_order.desc(), Category.name.asc())
    if sort == "apps-asc":
        return statement.order_by(apps_count_expr.asc(), Category.name.asc())
    if sort == "apps-desc":
        return statement.order_by(apps_count_expr.desc(), Category.name.asc())
    if sort == "status-asc":
        return statement.order_by(Category.status.asc(), Category.name.asc())
    if sort == "status-desc":
        return statement.order_by(Category.status.desc(), Category.name.asc())
    if sort == "updated-asc":
        return statement.order_by(Category.updated_at.asc())
    if sort == "updated-desc":
        return statement.order_by(Category.updated_at.desc())
    if sort == "oldest":
        return statement.order_by(Category.created_at.desc() if dir == "desc" else Category.created_at.asc())
    if sort == "newest":
        return statement.order_by(Category.created_at.asc() if dir == "asc" else Category.created_at.desc())

    return statement.order_by(Category.sort_order.asc(), Category.name.asc())


def list_admin_categories(
    db: Session,
    page: int = 1,
    page_size: int = DEFAULT_PAGE_SIZE,
    q: str | None = None,
    status_filter: str | None = None,
    sort: str | None = None,
    dir: str | None = None,
    sort_by: str | None = None,
    sort_direction: str | None = None,
) -> AdminCategoryListResult:
    normalized_sort = normalize_sort(sort, sort_by, sort_direction)
    normalized_dir = default_dir(normalized_sort, dir)
    normalized_page_size = max(1, min(page_size, MAX_PAGE_SIZE))
    filters = build_filters(q, status_filter)

    total_statement = select(func.count(Category.id))
    if filters:
        total_statement = total_statement.where(*filters)
    total = int(db.execute(total_statement).scalar_one())
    total_pages = max(1, ceil(total / normalized_page_size))
    normalized_page = min(max(page, 1), total_pages)
    offset = (normalized_page - 1) * normalized_page_size

    apps_count_expr = func.count(AppCatalogItem.id)
    statement = (
        select(Category, apps_count_expr.label("apps_count"))
        .outerjoin(AppCatalogItem, AppCatalogItem.category_id == Category.id)
        .group_by(
            Category.id,
            Category.key,
            Category.slug,
            Category.name,
            Category.description,
            Category.sort_order,
            Category.status,
            Category.created_at,
            Category.updated_at,
        )
        .offset(offset)
        .limit(normalized_page_size)
    )
    if filters:
        statement = statement.where(*filters)
    statement = apply_sort(statement, normalized_sort, normalized_dir, apps_count_expr)

    rows = db.execute(statement).all()
    items = [
        AdminCategoryListItem(
            id=category.id,
            key=category.key,
            slug=category.slug,
            name=category.name,
            description=category.description,
            sort_order=category.sort_order if isinstance(category.sort_order, int) else 0,
            status=validate_status(category.status),
            created_at=category.created_at,
            updated_at=category.updated_at,
            apps_count=int(apps_count or 0),
        )
        for category, apps_count in rows
    ]

    return AdminCategoryListResult(
        items=items,
        total=total,
        page=normalized_page,
        page_size=normalized_page_size,
        total_pages=total_pages,
        sort=normalized_sort,
        dir=normalized_dir,
        q=q or "",
        status=status_filter or "",
    )


def ensure_create_id(value: str) -> str:
    trimmed = value.strip()
    if not re.fullmatch(r"cat_[a-z0-9_-]+", trimmed):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID must start with cat_ and use lowercase letters, numbers, dashes, or underscores.",
        )

    return trimmed


def raise_duplicate_create() -> None:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Category with the same id, key, or slug already exists.",
    )


def create_admin_category(
    db: Session,
    admin: User,
    payload: CreateCategoryRequest,
    request: Request | None = None,
) -> str:
    category_id = ensure_create_id(payload.id)
    normalized_key = normalize_key(payload.key)
    slug_source = category_id.removeprefix("cat_")
    normalized_slug = normalized_key or normalize_key(slug_source) or normalize_key(payload.name)
    normalized_status = validate_status(payload.status)
    sort_order = payload.sort_order if isinstance(payload.sort_order, int) else 0

    conflict_filters = [
        Category.id == category_id,
        Category.slug == normalized_slug,
    ]
    if normalized_key:
        conflict_filters.append(Category.key == normalized_key)

    conflict = db.execute(select(Category.id).where(or_(*conflict_filters))).scalar_one_or_none()
    if conflict:
        raise_duplicate_create()

    category = Category(
        id=category_id,
        key=normalized_key or None,
        slug=normalized_slug,
        name=payload.name.strip(),
        description=(payload.description or "").strip(),
        sort_order=sort_order,
        status=normalized_status,
    )
    db.add(category)
    db.commit()

    write_audit_log(
        db,
        admin,
        "admin.categories.create",
        "Category",
        entity_id=category_id,
        entity_label=payload.name.strip(),
        metadata={
            "key": normalized_key or None,
            "slug": normalized_slug,
            "status": normalized_status,
        },
        request=request,
    )

    return category_id


def update_admin_category(
    db: Session,
    admin: User,
    category_id: str,
    payload: UpdateCategoryRequest,
    request: Request | None = None,
) -> str:
    existing = db.get(Category, category_id)
    if existing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found.")

    updates: dict[str, object] = {}
    if payload.name is not None:
        updates["name"] = payload.name.strip()
    if payload.description is not None:
        updates["description"] = payload.description.strip()
    if isinstance(payload.sort_order, int):
        updates["sort_order"] = payload.sort_order
    if payload.status is not None:
        updates["status"] = validate_status(payload.status)
    if payload.key is not None:
        normalized_key = normalize_key(payload.key)
        updates["key"] = normalized_key or None
        if normalized_key:
            updates["slug"] = normalized_key

    if "key" in updates or "slug" in updates:
        conflict_filters = []
        if updates.get("slug"):
            conflict_filters.append(Category.slug == updates["slug"])
        if updates.get("key"):
            conflict_filters.append(Category.key == updates["key"])

        if conflict_filters:
            conflict = db.execute(select(Category.id).where(or_(*conflict_filters))).scalar_one_or_none()
            if conflict and conflict != category_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Category key or slug already exists.",
                )

    changed = _changed_fields(existing, updates)
    existing_status = validate_status(existing.status if existing else None)
    next_status = str(updates.get("status") or existing_status)
    if updates:
        updates["updated_at"] = func.now()
        db.query(Category).filter(Category.id == category_id).update(updates, synchronize_session=False)
        db.commit()

    entity_label = str(updates.get("name") or (existing.name if existing else category_id))
    write_audit_log(
        db,
        admin,
        "admin.categories.update",
        "Category",
        entity_id=category_id,
        entity_label=entity_label,
        metadata={"changed": changed or [key for key in updates if key != "updated_at"]},
        request=request,
    )

    if "status" in updates and next_status != existing_status:
        write_audit_log(
            db,
            admin,
            "admin.categories.status",
            "Category",
            entity_id=category_id,
            entity_label=entity_label,
            metadata={
                "from": existing_status,
                "to": next_status,
            },
            request=request,
        )

    return category_id


def _changed_fields(existing: Category | None, updates: dict[str, object]) -> list[str]:
    if existing is None:
        return [key for key in updates if key != "updated_at"]

    checks = [
        ("name", updates.get("name"), existing.name),
        ("description", updates.get("description"), existing.description),
        ("sortOrder", updates.get("sort_order"), existing.sort_order),
        ("status", updates.get("status"), validate_status(existing.status)),
        ("key", updates.get("key"), existing.key),
        ("slug", updates.get("slug"), existing.slug),
    ]

    return [
        public_name
        for public_name, new_value, old_value in checks
        if new_value is not None and new_value != old_value
    ]


def delete_admin_category(
    db: Session,
    admin: User,
    category_id: str,
    request: Request | None = None,
) -> None:
    existing = db.get(Category, category_id)
    if existing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found.")

    usage = int(
        db.execute(
            select(func.count(AppCatalogItem.id)).where(AppCatalogItem.category_id == category_id)
        ).scalar_one()
    )
    if usage > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete category because it is used by {usage} apps.",
        )

    db.query(Category).filter(Category.id == category_id).delete()
    db.commit()

    write_audit_log(
        db,
        admin,
        "admin.categories.delete",
        "Category",
        entity_id=category_id,
        entity_label=existing.name if existing else category_id,
        metadata={
            "key": existing.key if existing else None,
            "slug": existing.slug if existing else None,
        },
        request=request,
    )
