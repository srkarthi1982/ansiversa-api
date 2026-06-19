"""Sync the parent Apps catalog to the locked approved 100-app list.

Run a safe preview:

    python -m app.modules.apps.scripts.sync_approved_catalog

Apply reviewed changes:

    python -m app.modules.apps.scripts.sync_approved_catalog --apply
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.database import ParentSessionLocal
from app.modules.apps.models import AppCatalogItem, Category


APPROVED_CATEGORIES = [
    "Learning & Education",
    "Career & Professional",
    "Content & AI Writing",
    "Utilities & Productivity",
    "Personal Life & Wellness",
    "Mobility & Travel",
    "Business & UAE",
    "Documents & Records",
    "Home & Family",
    "Health & Medical",
    "Vehicle & Driving",
    "Work & Planning",
    "Personal Finance",
    "Daily Life",
]

CATEGORY_ID_BY_NAME = {
    "Learning & Education": "cat_learning",
    "Career & Professional": "cat_career",
    "Content & AI Writing": "cat_writing",
    "Utilities & Productivity": "cat_utility",
    "Personal Life & Wellness": "cat_lifestyle",
}

CATEGORY_DESCRIPTION_BY_NAME = {
    "Learning & Education": "Learning, study, knowledge, and education tools.",
    "Career & Professional": "Career growth, professional documents, and workplace support.",
    "Content & AI Writing": "Writing, editing, translation, and content generation tools.",
    "Utilities & Productivity": "Everyday productivity utilities and technical helpers.",
    "Personal Life & Wellness": "Personal planning, wellness, habits, and family life tools.",
    "Mobility & Travel": "Travel, vehicle use, parking, and trip cost tools.",
    "Business & UAE": "Business operations and UAE-focused compliance helpers.",
    "Documents & Records": "Document planning, records, expiry, and secure organization tools.",
    "Home & Family": "Household, family, home inventory, and reminder tools.",
    "Health & Medical": "Health tracking, medical records, and care reminders.",
    "Vehicle & Driving": "Fuel, driving, and vehicle document management tools.",
    "Work & Planning": "Work schedules, leave, meetings, and planning tools.",
    "Personal Finance": "Personal money planning, splitting, savings, and net worth tools.",
    "Daily Life": "Daily decision, errand, local service, and emergency planning tools.",
}

APP_DESCRIPTION_BY_NAME = {
    "Quiz": "Practice knowledge through focused quizzes.",
    "JSON Formatter": "Format, validate, and inspect JSON quickly.",
    "Password Generator": "Generate strong passwords for everyday use.",
    "QR Code Creator": "Create QR codes for links and text.",
    "Markdown Editor": "Write and preview Markdown content.",
    "Study Timer": "Run focused study sessions with clear timing.",
    "Formula Finder": "Find useful formulas across common subjects.",
    "Lesson Builder": "Build structured lessons and learning material.",
    "Memory Trainer": "Practice memory through focused recall exercises.",
    "Daily Word Challenge": "Learn and review a daily vocabulary word.",
    "Eco Habit Tracker": "Track eco-friendly habits and progress.",
    "Mood Journal": "Record moods and daily reflections.",
}


@dataclass(frozen=True)
class ApprovedApp:
    order: int
    name: str
    key: str
    slug: str
    category_name: str


@dataclass(frozen=True)
class CatalogReport:
    categories_synced: int
    apps_synced: int
    archived_apps: list[str]
    missing_apps: list[str]
    duplicate_keys: list[str]
    duplicate_slugs: list[str]
    invalid_category_apps: list[str]


def default_approved_path() -> Path:
    return Path(__file__).resolve().parents[5] / "approved-apps.md"


def slugify(value: str) -> str:
    normalized = value.strip().lower()
    normalized = normalized.replace("+", " plus ")
    normalized = normalized.replace("&", " and ")
    normalized = normalized.replace("/", " ")
    normalized = re.sub(r"[^a-z0-9]+", "-", normalized)
    return re.sub(r"-+", "-", normalized).strip("-")


def stable_id(prefix: str, slug: str) -> str:
    return f"{prefix}_{slug}"


def parse_approved_apps(path: Path) -> list[ApprovedApp]:
    if not path.exists():
        raise ValueError(f"Approved apps source not found: {path}")

    current_category: str | None = None
    apps: list[ApprovedApp] = []
    heading_pattern = re.compile(r"^##\s+.+?\s+(.+?)\s+\((\d+)\)\s*$")
    app_pattern = re.compile(r"^(\d+)\.\s+(.+?)\s*$")

    for line in path.read_text(encoding="utf-8").splitlines():
        heading_match = heading_pattern.match(line.strip())
        if heading_match:
            current_category = heading_match.group(1).strip()
            if current_category not in APPROVED_CATEGORIES:
                raise ValueError(f"Unexpected category in approved list: {current_category}")
            continue

        app_match = app_pattern.match(line.strip())
        if not app_match:
            continue
        if current_category is None:
            raise ValueError(f"Approved app is missing a category: {line}")

        order = int(app_match.group(1))
        name = app_match.group(2).strip()
        slug = slugify(name)
        apps.append(
            ApprovedApp(
                order=order,
                name=name,
                key=slug,
                slug=slug,
                category_name=current_category,
            )
        )

    if len(apps) != 100:
        raise ValueError(f"Expected 100 approved apps, found {len(apps)}.")
    if [app.order for app in apps] != list(range(1, 101)):
        raise ValueError("Approved app numbering must be exactly 1 through 100.")

    return apps


def assert_unique_approved(apps: list[ApprovedApp]) -> None:
    duplicate_keys = sorted({app.key for app in apps if sum(1 for item in apps if item.key == app.key) > 1})
    duplicate_slugs = sorted({app.slug for app in apps if sum(1 for item in apps if item.slug == app.slug) > 1})
    if duplicate_keys or duplicate_slugs:
        raise ValueError(f"Approved list has duplicate keys={duplicate_keys}, slugs={duplicate_slugs}.")


def find_category(db: Session, name: str) -> Category | None:
    preferred_id = CATEGORY_ID_BY_NAME.get(name, stable_id("cat", slugify(name)))
    key = slugify(name)
    return db.execute(
        select(Category).where(
            or_(
                Category.id == preferred_id,
                Category.key == key,
                Category.slug == key,
                Category.name == name,
            )
        )
    ).scalar_one_or_none()


def sync_categories(db: Session) -> dict[str, str]:
    category_ids: dict[str, str] = {}
    approved_category_ids: set[str] = set()
    for index, name in enumerate(APPROVED_CATEGORIES, start=1):
        key = slugify(name)
        category = find_category(db, name)
        if category is None:
            category = Category(
                id=CATEGORY_ID_BY_NAME.get(name, stable_id("cat", key)),
                key=key,
                slug=key,
                name=name,
                description=CATEGORY_DESCRIPTION_BY_NAME[name],
                sort_order=index,
                status="active",
            )
            db.add(category)
        else:
            category.key = key
            category.slug = key
            category.name = name
            category.description = CATEGORY_DESCRIPTION_BY_NAME[name]
            category.sort_order = index
            category.status = "active"
            category.updated_at = func.now()

        category_ids[name] = category.id
        approved_category_ids.add(category.id)

    for category in db.execute(select(Category)).scalars().all():
        if category.id in approved_category_ids:
            continue
        category.status = "disabled"
        category.updated_at = func.now()

    return category_ids


def find_existing_app(db: Session, app: ApprovedApp) -> AppCatalogItem | None:
    exact = db.execute(
        select(AppCatalogItem).where(
            or_(AppCatalogItem.key == app.key, AppCatalogItem.slug == app.slug)
        )
    ).scalar_one_or_none()
    if exact is not None:
        return exact

    return db.execute(
        select(AppCatalogItem).where(AppCatalogItem.name == app.name)
    ).scalar_one_or_none()


def app_description(app: ApprovedApp) -> str:
    return APP_DESCRIPTION_BY_NAME.get(app.name, f"{app.name} for the Ansiversa app ecosystem.")


def app_url(slug: str) -> str:
    return f"https://ansiversa.com/{slug}"


def sync_apps(
    db: Session,
    approved_apps: list[ApprovedApp],
    category_ids: dict[str, str],
) -> list[str]:
    approved_ids: set[str] = set()
    approved_keys = {app.key for app in approved_apps}
    approved_slugs = {app.slug for app in approved_apps}

    for app in approved_apps:
        existing = find_existing_app(db, app)
        category_id = category_ids[app.category_name]
        if existing is None:
            existing = AppCatalogItem(
                id=stable_id("app", app.slug),
                key=app.key,
                slug=app.slug,
                name=app.name,
                description=app_description(app),
                category_id=category_id,
                status="active",
                is_featured=False,
                website_url=app_url(app.slug),
                admin_url=None,
                capabilities="[]",
                launch_status="comingSoon",
                visibility="public",
                pricing_gate="free",
                logo_key=app.slug,
            )
            db.add(existing)
        else:
            existing.key = app.key
            existing.slug = app.slug
            existing.name = app.name
            existing.description = existing.description or app_description(app)
            existing.category_id = category_id
            existing.status = "active"
            existing.visibility = "public"
            existing.pricing_gate = "free"
            existing.logo_key = existing.logo_key or app.slug
            if not existing.website_url:
                existing.website_url = app_url(app.slug)
            if not existing.capabilities:
                existing.capabilities = "[]"
            existing.updated_at = func.now()

        approved_ids.add(existing.id)

    archived: list[str] = []
    all_apps = db.execute(select(AppCatalogItem)).scalars().all()
    for existing in all_apps:
        if (
            existing.id in approved_ids
            or existing.key in approved_keys
            or existing.slug in approved_slugs
        ):
            continue
        if existing.status != "archived" or existing.launch_status != "disabled":
            archived.append(f"{existing.name} ({existing.key}/{existing.slug})")
        existing.status = "archived"
        existing.launch_status = "disabled"
        existing.visibility = "internal"
        existing.updated_at = func.now()

    return sorted(archived)


def duplicate_values(rows: list[str]) -> list[str]:
    return sorted({value for value in rows if rows.count(value) > 1})


def verify_catalog(db: Session, approved_apps: list[ApprovedApp]) -> CatalogReport:
    approved_keys = {app.key for app in approved_apps}
    approved_slugs = {app.slug for app in approved_apps}
    approved_names = {app.name for app in approved_apps}

    active_categories = db.execute(
        select(Category).where(Category.status == "active")
    ).scalars().all()
    approved_active_apps = db.execute(
        select(AppCatalogItem).where(
            AppCatalogItem.status == "active",
            AppCatalogItem.visibility == "public",
            AppCatalogItem.pricing_gate == "free",
        )
    ).scalars().all()
    all_apps = db.execute(select(AppCatalogItem)).scalars().all()
    active_category_ids = {category.id for category in active_categories}

    active_keys = [app.key for app in approved_active_apps]
    active_slugs = [app.slug for app in approved_active_apps]
    found_keys = {app.key for app in all_apps}
    found_slugs = {app.slug for app in all_apps}
    found_names = {app.name for app in all_apps}

    missing_apps = [
        app.name
        for app in approved_apps
        if app.key not in found_keys and app.slug not in found_slugs and app.name not in found_names
    ]
    invalid_category_apps = sorted(
        f"{app.name} ({app.category_id})"
        for app in approved_active_apps
        if app.category_id not in active_category_ids
    )
    archived_apps = sorted(
        f"{app.name} ({app.key}/{app.slug})"
        for app in all_apps
        if app.name not in approved_names
        and app.key not in approved_keys
        and app.slug not in approved_slugs
        and app.status in {"archived", "disabled"}
    )

    return CatalogReport(
        categories_synced=len(active_categories),
        apps_synced=len(approved_active_apps),
        archived_apps=archived_apps,
        missing_apps=missing_apps,
        duplicate_keys=duplicate_values(active_keys),
        duplicate_slugs=duplicate_values(active_slugs),
        invalid_category_apps=invalid_category_apps,
    )


def plan_catalog_report(db: Session, approved_apps: list[ApprovedApp]) -> CatalogReport:
    approved_keys = {app.key for app in approved_apps}
    approved_slugs = {app.slug for app in approved_apps}
    approved_names = {app.name for app in approved_apps}
    all_apps = db.execute(select(AppCatalogItem)).scalars().all()
    by_key = {app.key: app for app in all_apps}
    by_slug = {app.slug: app for app in all_apps}
    by_name = {app.name: app for app in all_apps}

    approved_ids: set[str] = set()
    for app in approved_apps:
        existing = by_key.get(app.key) or by_slug.get(app.slug) or by_name.get(app.name)
        approved_ids.add(existing.id if existing is not None else stable_id("app", app.slug))

    archived_apps = sorted(
        f"{app.name} ({app.key}/{app.slug})"
        for app in all_apps
        if app.id not in approved_ids
        and app.name not in approved_names
        and app.key not in approved_keys
        and app.slug not in approved_slugs
    )

    return CatalogReport(
        categories_synced=len(APPROVED_CATEGORIES),
        apps_synced=len(approved_apps),
        archived_apps=archived_apps,
        missing_apps=[],
        duplicate_keys=duplicate_values([app.key for app in approved_apps]),
        duplicate_slugs=duplicate_values([app.slug for app in approved_apps]),
        invalid_category_apps=[],
    )


def print_report(report: CatalogReport, *, applied: bool) -> None:
    mode = "applied" if applied else "dry-run"
    print(f"Catalog sync report ({mode})")
    print(f"Categories count: {report.categories_synced}")
    print(f"Approved active apps count: {report.apps_synced}")
    print(f"Duplicate keys: {report.duplicate_keys or 'none'}")
    print(f"Duplicate slugs: {report.duplicate_slugs or 'none'}")
    print(f"Invalid category apps: {report.invalid_category_apps or 'none'}")
    print(f"Missing approved apps: {report.missing_apps or 'none'}")
    if report.archived_apps:
        print("Archived/inactive old apps:")
        for app in report.archived_apps:
            print(f"- {app}")
    else:
        print("Archived/inactive old apps: none")


def sync_approved_catalog(source_path: Path, *, apply: bool) -> CatalogReport:
    approved_apps = parse_approved_apps(source_path)
    assert_unique_approved(approved_apps)

    with ParentSessionLocal() as db:
        if not apply:
            return plan_catalog_report(db, approved_apps)

        category_ids = sync_categories(db)
        sync_apps(db, approved_apps, category_ids)
        db.commit()
        report = verify_catalog(db, approved_apps)
        return report


def verify_approved_catalog(source_path: Path) -> CatalogReport:
    approved_apps = parse_approved_apps(source_path)
    assert_unique_approved(approved_apps)
    with ParentSessionLocal() as db:
        return verify_catalog(db, approved_apps)


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync approved Ansiversa Apps catalog data.")
    parser.add_argument("--apply", action="store_true", help="Write changes. Defaults to dry-run.")
    parser.add_argument(
        "--source",
        type=Path,
        default=default_approved_path(),
        help="Path to approved-apps.md.",
    )
    args = parser.parse_args()

    report = sync_approved_catalog(args.source, apply=args.apply)
    print_report(report, applied=args.apply)

    if args.apply:
        failed = (
            report.categories_synced != 14
            or report.apps_synced != 100
            or bool(report.duplicate_keys)
            or bool(report.duplicate_slugs)
            or bool(report.invalid_category_apps)
            or bool(report.missing_apps)
        )
        if failed:
            raise SystemExit("Catalog verification failed after sync.")


if __name__ == "__main__":
    main()
