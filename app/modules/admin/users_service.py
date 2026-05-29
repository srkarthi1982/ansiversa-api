from dataclasses import dataclass
from datetime import datetime
from math import ceil

from fastapi import HTTPException, status
from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session

from app.modules.auth.models import Role, User


DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 200
STATUS_OPTIONS = {"active", "disabled"}
SORT_OPTIONS = {
    "newest",
    "oldest",
    "name-asc",
    "name-desc",
    "email-asc",
    "email-desc",
    "role-asc",
    "role-desc",
    "status-asc",
    "status-desc",
    "plan-asc",
    "plan-desc",
    "planStatus-asc",
    "planStatus-desc",
    "country-asc",
    "country-desc",
    "updated-asc",
    "updated-desc",
}


@dataclass(frozen=True)
class AdminUserRoleItem:
    id: int
    name: str | None
    key: str | None


@dataclass(frozen=True)
class AdminUserItem:
    id: str
    email: str
    name: str
    role_id: int
    role: AdminUserRoleItem | None
    role_name: str | None
    status: str
    plan: str | None
    plan_status: str | None
    country_code: str | None
    region_code: str | None
    city: str | None
    timezone: str | None
    location_source: str
    location_captured_at: datetime | None
    avatar_url: str | None
    avatar_updated_at: datetime | None
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class AdminUserListResult:
    items: list[AdminUserItem]
    total: int
    page: int
    page_size: int
    total_pages: int
    sort: str
    dir: str
    q: str
    status: str
    role_id: int | str
    plan: str
    plan_status: str
    country_code: str


def normalize_status(value: str | None) -> str:
    normalized = (value or "active").strip().lower()
    if normalized == "disabled":
        return "disabled"

    return "active"


def normalize_sort(sort: str | None, sort_by: str | None, sort_direction: str | None) -> str:
    if sort and sort in SORT_OPTIONS:
        return sort

    key = (sort_by or "").strip()
    direction = "desc" if (sort_direction or "").strip().lower() == "desc" else "asc"
    if key == "name":
        return f"name-{direction}"
    if key == "email":
        return f"email-{direction}"
    if key == "role":
        return f"role-{direction}"
    if key == "status":
        return f"status-{direction}"
    if key == "plan":
        return f"plan-{direction}"
    if key == "planStatus":
        return f"planStatus-{direction}"
    if key in {"country", "countryCode"}:
        return f"country-{direction}"
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
    status_filter: str | None,
    role_id: int | None,
    plan: str | None,
    plan_status: str | None,
    country_code: str | None,
) -> list[object]:
    filters: list[object] = []
    trimmed_q = (q or "").strip()
    if trimmed_q:
        wildcard = f"%{trimmed_q}%"
        filters.append(
            or_(
                User.email.ilike(wildcard),
                User.name.ilike(wildcard),
                User.city.ilike(wildcard),
                User.country_code.ilike(wildcard),
                User.region_code.ilike(wildcard),
            )
        )
    if status_filter:
        filters.append(User.status == normalize_status(status_filter))
    if role_id is not None:
        filters.append(User.role_id == role_id)
    if plan:
        filters.append(User.plan == plan.strip())
    if plan_status:
        filters.append(User.plan_status == plan_status.strip())
    if country_code:
        filters.append(User.country_code == country_code.strip().upper())

    return filters


def apply_sort(statement: Select[tuple[User, Role | None]], sort: str, dir: str) -> Select[tuple[User, Role | None]]:
    if sort == "name-asc":
        return statement.order_by(User.name.asc())
    if sort == "name-desc":
        return statement.order_by(User.name.desc())
    if sort == "email-asc":
        return statement.order_by(User.email.asc())
    if sort == "email-desc":
        return statement.order_by(User.email.desc())
    if sort == "role-asc":
        return statement.order_by(Role.name.asc())
    if sort == "role-desc":
        return statement.order_by(Role.name.desc())
    if sort == "status-asc":
        return statement.order_by(User.status.asc())
    if sort == "status-desc":
        return statement.order_by(User.status.desc())
    if sort == "plan-asc":
        return statement.order_by(User.plan.asc())
    if sort == "plan-desc":
        return statement.order_by(User.plan.desc())
    if sort == "planStatus-asc":
        return statement.order_by(User.plan_status.asc())
    if sort == "planStatus-desc":
        return statement.order_by(User.plan_status.desc())
    if sort == "country-asc":
        return statement.order_by(User.country_code.asc(), User.city.asc())
    if sort == "country-desc":
        return statement.order_by(User.country_code.desc(), User.city.asc())
    if sort == "updated-asc":
        return statement.order_by(User.updated_at.asc())
    if sort == "updated-desc":
        return statement.order_by(User.updated_at.desc())
    if sort == "oldest":
        return statement.order_by(User.created_at.desc() if dir == "desc" else User.created_at.asc())

    return statement.order_by(User.created_at.asc() if dir == "asc" else User.created_at.desc())


def _to_user_item(user: User, role: Role | None) -> AdminUserItem:
    role_item = (
        AdminUserRoleItem(
            id=role.id,
            name=role.name,
            key=role.key,
        )
        if role
        else None
    )

    return AdminUserItem(
        id=user.id,
        email=user.email,
        name=user.name,
        role_id=user.role_id,
        role=role_item,
        role_name=role.name if role else None,
        status=normalize_status(user.status),
        plan=user.plan,
        plan_status=user.plan_status,
        country_code=user.country_code,
        region_code=user.region_code,
        city=user.city,
        timezone=user.timezone,
        location_source=user.location_source or "unknown",
        location_captured_at=user.location_captured_at,
        avatar_url=user.avatar_url,
        avatar_updated_at=user.avatar_updated_at,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


def list_admin_users(
    db: Session,
    page: int = 1,
    page_size: int = DEFAULT_PAGE_SIZE,
    q: str | None = None,
    status_filter: str | None = None,
    role_id: int | None = None,
    plan: str | None = None,
    plan_status: str | None = None,
    country_code: str | None = None,
    sort: str | None = None,
    dir: str | None = None,
    sort_by: str | None = None,
    sort_direction: str | None = None,
) -> AdminUserListResult:
    normalized_sort = normalize_sort(sort, sort_by, sort_direction)
    normalized_dir = default_dir(normalized_sort, dir)
    normalized_page_size = max(1, min(page_size, MAX_PAGE_SIZE))
    filters = build_filters(q, status_filter, role_id, plan, plan_status, country_code)

    total_statement = select(func.count(User.id))
    if filters:
        total_statement = total_statement.where(*filters)
    total = int(db.execute(total_statement).scalar_one())
    total_pages = max(1, ceil(total / normalized_page_size))
    normalized_page = min(max(page, 1), total_pages)
    offset = (normalized_page - 1) * normalized_page_size

    statement = (
        select(User, Role)
        .outerjoin(Role, User.role_id == Role.id)
        .offset(offset)
        .limit(normalized_page_size)
    )
    if filters:
        statement = statement.where(*filters)
    statement = apply_sort(statement, normalized_sort, normalized_dir)

    rows = db.execute(statement).all()
    items = [_to_user_item(user, role) for user, role in rows]

    return AdminUserListResult(
        items=items,
        total=total,
        page=normalized_page,
        page_size=normalized_page_size,
        total_pages=total_pages,
        sort=normalized_sort,
        dir=normalized_dir,
        q=q or "",
        status=status_filter or "",
        role_id=role_id if role_id is not None else "",
        plan=plan or "",
        plan_status=plan_status or "",
        country_code=country_code or "",
    )


def get_admin_user(db: Session, user_id: str) -> AdminUserItem:
    row = (
        db.execute(
            select(User, Role)
            .outerjoin(Role, User.role_id == Role.id)
            .where(User.id == user_id)
        )
        .first()
    )
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    user, role = row
    return _to_user_item(user, role)
