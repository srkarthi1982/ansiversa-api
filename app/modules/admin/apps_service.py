import json
import re
from dataclasses import dataclass
from datetime import datetime
from math import ceil
from urllib.parse import urlsplit, urlunsplit
from uuid import uuid4

from fastapi import HTTPException, Request, status
from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session

from app.modules.admin.schemas import CreateAppRequest, UpdateAppRequest
from app.modules.apps.models import AppCatalogItem, Category
from app.modules.audit.service import write_audit_log
from app.modules.auth.models import User


DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 200
STATUS_OPTIONS = {"alpha", "beta", "live", "archived", "coming-soon"}
LAUNCH_STATUS_OPTIONS = {"live", "beta", "comingSoon", "disabled"}
VISIBILITY_OPTIONS = {"public", "private", "internal"}
PRICING_GATE_OPTIONS = {"free", "pro"}
SORT_OPTIONS = {
    "newest",
    "oldest",
    "name-asc",
    "name-desc",
    "category-asc",
    "category-desc",
    "status-asc",
    "status-desc",
    "featured-asc",
    "featured-desc",
    "updated-asc",
    "updated-desc",
}
KEY_PATTERN = re.compile(r"[-a-z0-9_]+")
CAPABILITY_CATALOG = [
    {"key": "public", "label": "Public website", "icon": "home", "order": 10},
    {"key": "admin", "label": "Admin UI", "icon": "about", "order": 20},
    {"key": "bookmarks", "label": "Bookmarks supported", "icon": "heart", "order": 30},
    {"key": "favorites", "label": "Favorites supported", "icon": "heart-filled", "order": 40},
    {"key": "ai", "label": "AI features", "icon": "search", "order": 50},
    {"key": "billing", "label": "Paid / billing", "icon": "pricing", "order": 60},
    {"key": "dashboard", "label": "Dashboard integrated", "icon": "apps", "order": 70},
]
CAPABILITY_ORDER = {entry["key"]: int(entry["order"]) for entry in CAPABILITY_CATALOG}


@dataclass(frozen=True)
class AdminAppListItem:
    id: str
    key: str
    slug: str
    name: str
    description: str | None
    category_id: str
    category_name: str | None
    status: str
    version: str
    launch_status: str
    visibility: str
    pricing_gate: str
    is_featured: bool
    website_url: str | None
    admin_url: str | None
    logo_key: str | None
    capabilities: list[str]
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class AdminAppListResult:
    items: list[AdminAppListItem]
    total: int
    page: int
    page_size: int
    total_pages: int
    sort: str
    dir: str
    q: str
    category_id: str
    status: str
    launch_status: str
    visibility: str
    pricing_gate: str
    featured_only: bool


def normalize_key(value: str | None) -> str:
    if value is None:
        return ""

    return re.sub(r"\s+", "-", value.strip().lower())


def require_valid_key(value: str, field_name: str) -> str:
    normalized = normalize_key(value)
    if not normalized:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{field_name} is required.")
    if KEY_PATTERN.fullmatch(normalized) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{field_name} must be lowercase letters, numbers, dashes, or underscores.",
        )

    return normalized


def validate_status(value: str | None) -> str:
    normalized = (value or "live").strip().lower()
    if normalized in STATUS_OPTIONS:
        return normalized

    return "live"


def normalize_launch_status(value: str | None, fallback_legacy_status: str | None = None) -> str:
    normalized = (value or "").strip()
    if normalized in LAUNCH_STATUS_OPTIONS:
        return normalized

    legacy = (fallback_legacy_status or "").strip().lower()
    legacy_map = {
        "live": "live",
        "beta": "beta",
        "alpha": "beta",
        "coming-soon": "comingSoon",
        "comingsoon": "comingSoon",
        "archived": "disabled",
        "disabled": "disabled",
    }
    return legacy_map.get(legacy, "comingSoon")


def normalize_visibility(value: str | None) -> str:
    normalized = (value or "").strip().lower()
    if normalized in VISIBILITY_OPTIONS:
        return normalized

    return "public"


def normalize_pricing_gate(value: str | None) -> str:
    normalized = (value or "").strip().lower()
    if normalized in PRICING_GATE_OPTIONS:
        return normalized

    return "free"


def normalize_url(value: str | None) -> str | None:
    trimmed = (value or "").strip()
    if not trimmed:
        return None

    parsed = urlsplit(trimmed)
    if not parsed.scheme or not parsed.netloc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="URL is invalid.")

    path = parsed.path or "/"
    return urlunsplit((parsed.scheme, parsed.netloc, path, parsed.query, parsed.fragment))


def sanitize_capabilities(value: object) -> list[str]:
    if not isinstance(value, list):
        return []

    deduped = {item for item in value if isinstance(item, str) and item in CAPABILITY_ORDER}
    return sorted(deduped, key=lambda item: CAPABILITY_ORDER.get(item, 999))


def parse_capabilities_json(value: str | None) -> list[str]:
    if not value or not value.strip():
        return []

    try:
        return sanitize_capabilities(json.loads(value))
    except (TypeError, ValueError):
        return []


def serialize_capabilities(value: object) -> str:
    return json.dumps(sanitize_capabilities(value))


def normalize_sort(sort: str | None, sort_by: str | None, sort_direction: str | None) -> str:
    if sort and sort in SORT_OPTIONS:
        return sort

    key = (sort_by or "").strip()
    direction = "desc" if (sort_direction or "").strip().lower() == "desc" else "asc"
    if key == "name":
        return f"name-{direction}"
    if key == "category":
        return f"category-{direction}"
    if key == "status":
        return f"status-{direction}"
    if key == "featured":
        return f"featured-{direction}"
    if key == "updatedAt":
        return f"updated-{direction}"
    if key == "createdAt":
        return "newest" if direction == "desc" else "oldest"

    return "newest"


def default_dir(sort: str, requested_dir: str | None) -> str:
    if requested_dir in {"asc", "desc"}:
        return requested_dir
    if sort == "newest":
        return "desc"
    if sort.endswith("-desc"):
        return "desc"

    return "asc"


def build_filters(
    q: str | None,
    category_id: str | None,
    status_filter: str | None,
    launch_status: str | None,
    visibility: str | None,
    pricing_gate: str | None,
    featured_only: bool,
) -> list[object]:
    filters: list[object] = []
    trimmed_q = (q or "").strip()
    if trimmed_q:
        wildcard = f"%{trimmed_q}%"
        filters.append(
            or_(
                AppCatalogItem.name.ilike(wildcard),
                AppCatalogItem.key.ilike(wildcard),
                AppCatalogItem.slug.ilike(wildcard),
                AppCatalogItem.description.ilike(wildcard),
            )
        )
    if category_id:
        filters.append(AppCatalogItem.category_id == category_id)
    if status_filter:
        filters.append(AppCatalogItem.status == validate_status(status_filter))
    if launch_status:
        filters.append(AppCatalogItem.launch_status == normalize_launch_status(launch_status))
    if visibility:
        filters.append(AppCatalogItem.visibility == normalize_visibility(visibility))
    if pricing_gate:
        filters.append(AppCatalogItem.pricing_gate == normalize_pricing_gate(pricing_gate))
    if featured_only:
        filters.append(AppCatalogItem.is_featured.is_(True))

    return filters


def apply_sort(statement: Select[tuple[AppCatalogItem, str | None]], sort: str, dir: str) -> Select[tuple[AppCatalogItem, str | None]]:
    if sort == "name-asc":
        return statement.order_by(AppCatalogItem.name.asc())
    if sort == "name-desc":
        return statement.order_by(AppCatalogItem.name.desc())
    if sort == "category-asc":
        return statement.order_by(Category.name.asc())
    if sort == "category-desc":
        return statement.order_by(Category.name.desc())
    if sort == "status-asc":
        return statement.order_by(AppCatalogItem.status.asc())
    if sort == "status-desc":
        return statement.order_by(AppCatalogItem.status.desc())
    if sort == "featured-asc":
        return statement.order_by(AppCatalogItem.is_featured.asc())
    if sort == "featured-desc":
        return statement.order_by(AppCatalogItem.is_featured.desc())
    if sort == "updated-asc":
        return statement.order_by(AppCatalogItem.updated_at.asc())
    if sort == "updated-desc":
        return statement.order_by(AppCatalogItem.updated_at.desc())
    if sort == "oldest":
        return statement.order_by(AppCatalogItem.created_at.desc() if dir == "desc" else AppCatalogItem.created_at.asc())

    return statement.order_by(AppCatalogItem.created_at.asc() if dir == "asc" else AppCatalogItem.created_at.desc())


def _to_list_item(app: AppCatalogItem, category_name: str | None) -> AdminAppListItem:
    status_value = validate_status(app.status)
    return AdminAppListItem(
        id=app.id,
        key=app.key,
        slug=app.slug,
        name=app.name,
        description=app.description,
        category_id=app.category_id,
        category_name=category_name,
        status=status_value,
        version=app.version,
        launch_status=normalize_launch_status(app.launch_status, status_value),
        visibility=normalize_visibility(app.visibility),
        pricing_gate=normalize_pricing_gate(app.pricing_gate),
        is_featured=bool(app.is_featured),
        website_url=app.website_url,
        admin_url=app.admin_url,
        logo_key=app.logo_key,
        capabilities=parse_capabilities_json(app.capabilities),
        created_at=app.created_at,
        updated_at=app.updated_at,
    )


def list_admin_apps(
    db: Session,
    page: int = 1,
    page_size: int = DEFAULT_PAGE_SIZE,
    q: str | None = None,
    status_filter: str | None = None,
    category_id: str | None = None,
    launch_status: str | None = None,
    visibility: str | None = None,
    pricing_gate: str | None = None,
    featured_only: bool = False,
    sort: str | None = None,
    dir: str | None = None,
    sort_by: str | None = None,
    sort_direction: str | None = None,
) -> AdminAppListResult:
    normalized_sort = normalize_sort(sort, sort_by, sort_direction)
    normalized_dir = default_dir(normalized_sort, dir)
    normalized_page_size = max(1, min(page_size, MAX_PAGE_SIZE))
    filters = build_filters(
        q,
        category_id,
        status_filter,
        launch_status,
        visibility,
        pricing_gate,
        featured_only,
    )

    total_statement = select(func.count(AppCatalogItem.id))
    if filters:
        total_statement = total_statement.where(*filters)
    total = int(db.execute(total_statement).scalar_one())
    total_pages = max(1, ceil(total / normalized_page_size))
    normalized_page = min(max(page, 1), total_pages)
    offset = (normalized_page - 1) * normalized_page_size

    statement = (
        select(AppCatalogItem, Category.name.label("category_name"))
        .outerjoin(Category, AppCatalogItem.category_id == Category.id)
        .offset(offset)
        .limit(normalized_page_size)
    )
    if filters:
        statement = statement.where(*filters)
    statement = apply_sort(statement, normalized_sort, normalized_dir)

    rows = db.execute(statement).all()
    items = [_to_list_item(app, category_name) for app, category_name in rows]

    return AdminAppListResult(
        items=items,
        total=total,
        page=normalized_page,
        page_size=normalized_page_size,
        total_pages=total_pages,
        sort=normalized_sort,
        dir=normalized_dir,
        q=q or "",
        category_id=category_id or "",
        status=status_filter or "",
        launch_status=launch_status or "",
        visibility=visibility or "",
        pricing_gate=pricing_gate or "",
        featured_only=featured_only,
    )


def get_admin_apps_meta(db: Session) -> dict[str, object]:
    categories = db.execute(
        select(Category.id, Category.name).order_by(Category.sort_order.asc(), Category.name.asc())
    ).all()

    return {
        "categories": [{"id": category_id, "name": name} for category_id, name in categories],
        "allowed_statuses": ["alpha", "beta", "live", "archived", "coming-soon"],
        "allowed_launch_statuses": ["live", "beta", "comingSoon", "disabled"],
        "allowed_visibility_values": ["public", "private", "internal"],
        "allowed_pricing_gates": ["free", "pro"],
        "capability_options": CAPABILITY_CATALOG,
    }


def ensure_category_exists(db: Session, category_id: str) -> None:
    if db.get(Category, category_id) is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category does not exist.")


def raise_duplicate_app() -> None:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="App key or slug already exists.",
    )


def check_duplicate_key_or_slug(db: Session, key: str | None, slug: str | None, app_id: str | None = None) -> None:
    filters = []
    if key:
        filters.append(AppCatalogItem.key == key)
    if slug:
        filters.append(AppCatalogItem.slug == slug)
    if not filters:
        return

    conflict = db.execute(select(AppCatalogItem.id).where(or_(*filters)).limit(1)).scalar_one_or_none()
    if conflict and conflict != app_id:
        raise_duplicate_app()


def create_admin_app(
    db: Session,
    admin: User,
    payload: CreateAppRequest,
    request: Request | None = None,
) -> str:
    normalized_key = require_valid_key(payload.key, "Key")
    normalized_slug = require_valid_key(payload.slug, "Slug")
    category_id = payload.category_id.strip()
    ensure_category_exists(db, category_id)
    check_duplicate_key_or_slug(db, normalized_key, normalized_slug)

    normalized_status = validate_status(payload.status)
    normalized_launch_status = normalize_launch_status(payload.launch_status, normalized_status)
    normalized_visibility = normalize_visibility(payload.visibility)
    normalized_pricing_gate = normalize_pricing_gate(payload.pricing_gate)
    normalized_logo_key = (payload.logo_key or normalized_key).strip().lower() or normalized_key
    normalized_capabilities = sanitize_capabilities(payload.capabilities or [])
    app_id = str(uuid4())

    app = AppCatalogItem(
        id=app_id,
        key=normalized_key,
        slug=normalized_slug,
        name=payload.name.strip(),
        description=(payload.description or "").strip(),
        category_id=category_id,
        status=normalized_status,
        is_featured=bool(payload.is_featured),
        website_url=normalize_url(payload.website_url),
        admin_url=normalize_url(payload.admin_url),
        capabilities=serialize_capabilities(normalized_capabilities),
        launch_status=normalized_launch_status,
        visibility=normalized_visibility,
        pricing_gate=normalized_pricing_gate,
        logo_key=normalized_logo_key,
    )
    db.add(app)
    db.commit()

    write_audit_log(
        db,
        admin,
        "admin.apps.create",
        "App",
        entity_id=app_id,
        entity_label=payload.name.strip(),
        metadata={
            "key": normalized_key,
            "slug": normalized_slug,
            "categoryId": category_id,
            "status": normalized_status,
            "launchStatus": normalized_launch_status,
            "visibility": normalized_visibility,
            "pricingGate": normalized_pricing_gate,
            "isFeatured": bool(payload.is_featured),
            "logoKey": normalized_logo_key,
            "capabilities": normalized_capabilities,
        },
        request=request,
    )

    return app_id


def update_admin_app(
    db: Session,
    admin: User,
    app_id: str,
    payload: UpdateAppRequest,
    request: Request | None = None,
) -> str:
    existing = db.get(AppCatalogItem, app_id)
    if existing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="App not found.")

    updates: dict[str, object | None] = {}
    if payload.name is not None:
        updates["name"] = payload.name.strip()
    if payload.key is not None:
        updates["key"] = require_valid_key(payload.key, "Key")
    if payload.slug is not None:
        updates["slug"] = require_valid_key(payload.slug, "Slug")
    if payload.description is not None:
        updates["description"] = payload.description.strip()
    if payload.category_id is not None:
        category_id = payload.category_id.strip()
        ensure_category_exists(db, category_id)
        updates["category_id"] = category_id
    if payload.status is not None:
        updates["status"] = validate_status(payload.status)
    if payload.launch_status is not None:
        updates["launch_status"] = normalize_launch_status(
            payload.launch_status,
            str(updates.get("status") or existing.status),
        )
    if payload.visibility is not None:
        updates["visibility"] = normalize_visibility(payload.visibility)
    if payload.pricing_gate is not None:
        updates["pricing_gate"] = normalize_pricing_gate(payload.pricing_gate)
    if payload.is_featured is not None:
        updates["is_featured"] = bool(payload.is_featured)
    if payload.website_url is not None:
        updates["website_url"] = normalize_url(payload.website_url)
    if payload.admin_url is not None:
        updates["admin_url"] = normalize_url(payload.admin_url)
    if payload.logo_key is not None:
        updates["logo_key"] = payload.logo_key.strip().lower() or existing.key
    if payload.capabilities is not None:
        updates["capabilities"] = serialize_capabilities(payload.capabilities)

    check_duplicate_key_or_slug(
        db,
        str(updates.get("key")) if updates.get("key") else None,
        str(updates.get("slug")) if updates.get("slug") else None,
        app_id=app_id,
    )

    changed = _changed_fields(existing, updates)
    existing_status = validate_status(existing.status)
    existing_featured = bool(existing.is_featured)
    next_status = str(updates.get("status") or existing_status)
    next_featured = bool(updates.get("is_featured")) if "is_featured" in updates else existing_featured

    if updates:
        updates["updated_at"] = func.now()
        db.query(AppCatalogItem).filter(AppCatalogItem.id == app_id).update(updates, synchronize_session=False)
        db.commit()

    entity_label = str(updates.get("name") or existing.name or app_id)
    write_audit_log(
        db,
        admin,
        "admin.apps.update",
        "App",
        entity_id=app_id,
        entity_label=entity_label,
        metadata={"changed": changed or [key for key in updates if key != "updated_at"]},
        request=request,
    )

    if "status" in updates and next_status != existing_status:
        write_audit_log(
            db,
            admin,
            "admin.apps.status",
            "App",
            entity_id=app_id,
            entity_label=entity_label,
            metadata={"from": existing_status, "to": next_status},
            request=request,
        )

    if "is_featured" in updates and next_featured != existing_featured:
        write_audit_log(
            db,
            admin,
            "admin.apps.featured",
            "App",
            entity_id=app_id,
            entity_label=entity_label,
            metadata={"from": existing_featured, "to": next_featured},
            request=request,
        )

    return app_id


def _changed_fields(existing: AppCatalogItem, updates: dict[str, object | None]) -> list[str]:
    checks = [
        ("name", updates.get("name"), existing.name),
        ("key", updates.get("key"), existing.key),
        ("slug", updates.get("slug"), existing.slug),
        ("description", updates.get("description"), existing.description),
        ("categoryId", updates.get("category_id"), existing.category_id),
        ("status", updates.get("status"), validate_status(existing.status)),
        ("launchStatus", updates.get("launch_status"), normalize_launch_status(existing.launch_status, existing.status)),
        ("visibility", updates.get("visibility"), normalize_visibility(existing.visibility)),
        ("pricingGate", updates.get("pricing_gate"), normalize_pricing_gate(existing.pricing_gate)),
        ("isFeatured", updates.get("is_featured"), bool(existing.is_featured)),
        ("websiteUrl", updates.get("website_url"), existing.website_url),
        ("adminUrl", updates.get("admin_url"), existing.admin_url),
        ("logoKey", updates.get("logo_key"), existing.logo_key),
        ("capabilities", updates.get("capabilities"), existing.capabilities),
    ]

    return [
        public_name
        for public_name, new_value, old_value in checks
        if public_name in _public_names_for_updates(updates) and new_value != old_value
    ]


def _public_names_for_updates(updates: dict[str, object | None]) -> set[str]:
    mapping = {
        "name": "name",
        "key": "key",
        "slug": "slug",
        "description": "description",
        "category_id": "categoryId",
        "status": "status",
        "launch_status": "launchStatus",
        "visibility": "visibility",
        "pricing_gate": "pricingGate",
        "is_featured": "isFeatured",
        "website_url": "websiteUrl",
        "admin_url": "adminUrl",
        "logo_key": "logoKey",
        "capabilities": "capabilities",
    }
    return {mapping[key] for key in updates if key in mapping}


def delete_admin_app(
    db: Session,
    admin: User,
    app_id: str,
    request: Request | None = None,
) -> None:
    existing = db.get(AppCatalogItem, app_id)
    db.query(AppCatalogItem).filter(AppCatalogItem.id == app_id).delete()
    db.commit()

    write_audit_log(
        db,
        admin,
        "admin.apps.delete",
        "App",
        entity_id=app_id,
        entity_label=existing.name if existing else app_id,
        metadata={
            "key": existing.key if existing else None,
            "slug": existing.slug if existing else None,
        },
        request=request,
    )
