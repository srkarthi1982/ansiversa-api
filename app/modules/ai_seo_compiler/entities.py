"""Stable entity resolution boundaries for AI SEO compiler candidates."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Iterable

from app.modules.ai_seo_compiler.normalization import canonical_url, normalize_route, normalize_slug, stable_list
from app.modules.ai_seo_compiler.validation import Severity, ValidationCode, ValidationFinding, ValidationResult, merge_results, validate_route_pair


class EntityType(StrEnum):
    PLATFORM = "platform"
    PUBLIC_PAGE = "public_page"
    CATEGORY = "category"
    APP = "app"
    FAQ = "faq"


@dataclass(frozen=True)
class CategoryEntity:
    category_id: str
    name: str
    slug: str

    def as_dict(self) -> dict[str, str]:
        return {"entityType": EntityType.CATEGORY.value, "categoryId": self.category_id, "name": self.name, "slug": self.slug}


@dataclass(frozen=True)
class PublicPageEntity:
    page_id: str
    name: str
    route: str
    summary: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "route", normalize_route(self.route))

    @property
    def canonical_url(self) -> str:
        return canonical_url(self.route)

    def as_dict(self) -> dict[str, str]:
        return {
            "entityType": EntityType.PUBLIC_PAGE.value,
            "pageId": self.page_id,
            "name": self.name,
            "route": self.route,
            "canonicalUrl": self.canonical_url,
            "summary": self.summary,
        }


@dataclass(frozen=True)
class AppEntity:
    app_id: str
    number: int
    name: str
    slug: str
    category_id: str
    category_name: str
    purpose: str
    short_description: str
    route: str
    aliases: tuple[str, ...] = ()
    related_app_ids: tuple[str, ...] = ()
    capabilities: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "slug", normalize_slug(self.slug))
        object.__setattr__(self, "route", normalize_route(self.route))
        object.__setattr__(self, "aliases", stable_list(self.aliases, lowercase=True, max_items=16))
        object.__setattr__(self, "related_app_ids", tuple(sorted(dict.fromkeys(self.related_app_ids))))
        object.__setattr__(self, "capabilities", stable_list(self.capabilities, max_items=12))

    @property
    def canonical_url(self) -> str:
        return canonical_url(self.route)

    def as_dict(self) -> dict[str, object]:
        return {
            "entityType": EntityType.APP.value,
            "appId": self.app_id,
            "number": self.number,
            "name": self.name,
            "slug": self.slug,
            "categoryId": self.category_id,
            "categoryName": self.category_name,
            "purpose": self.purpose,
            "shortDescription": self.short_description,
            "route": self.route,
            "canonicalUrl": self.canonical_url,
            "aliases": list(self.aliases),
            "relatedAppIds": list(self.related_app_ids),
            "capabilities": list(self.capabilities),
        }


@dataclass(frozen=True)
class PlatformEntity:
    platform_id: str = "ansiversa"
    name: str = "Ansiversa"
    canonical_url: str = "https://ansiversa.com"

    def as_dict(self) -> dict[str, str]:
        return {
            "entityType": EntityType.PLATFORM.value,
            "platformId": self.platform_id,
            "name": self.name,
            "canonicalUrl": self.canonical_url,
        }


@dataclass(frozen=True)
class EntityRelease:
    platform: PlatformEntity
    pages: tuple[PublicPageEntity, ...]
    categories: tuple[CategoryEntity, ...]
    apps: tuple[AppEntity, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "platform": self.platform.as_dict(),
            "pages": [page.as_dict() for page in self.pages],
            "categories": [category.as_dict() for category in self.categories],
            "apps": [app.as_dict() for app in self.apps],
        }


def _duplicate_findings(values: list[object], subject: str) -> list[ValidationFinding]:
    return [
        ValidationFinding(Severity.BLOCKER, ValidationCode.DUPLICATE_IDENTITY, f"Duplicate {subject}: {value}", str(value))
        for value in sorted({value for value in values if values.count(value) > 1})
    ]


def resolve_entities(
    *,
    apps: Iterable[AppEntity],
    categories: Iterable[CategoryEntity],
    pages: Iterable[PublicPageEntity] = (),
    require_full_catalog: bool = True,
) -> tuple[EntityRelease, ValidationResult]:
    sorted_apps = tuple(sorted(apps, key=lambda app: app.number))
    sorted_categories = tuple(sorted(categories, key=lambda category: category.category_id))
    sorted_pages = tuple(sorted(pages, key=lambda page: page.route))
    findings: list[ValidationFinding] = []
    if require_full_catalog and len(sorted_apps) != 100:
        findings.append(ValidationFinding(Severity.BLOCKER, ValidationCode.MISSING_REQUIRED_FIELD, "Release must contain exactly 100 apps", "apps"))
    if require_full_catalog and len(sorted_categories) != 14:
        findings.append(ValidationFinding(Severity.BLOCKER, ValidationCode.MISSING_REQUIRED_FIELD, "Release must contain exactly 14 categories", "categories"))
    findings.extend(_duplicate_findings([app.app_id for app in sorted_apps], "app ID"))
    findings.extend(_duplicate_findings([app.number for app in sorted_apps], "app number"))
    findings.extend(_duplicate_findings([app.slug for app in sorted_apps], "app slug"))
    findings.extend(_duplicate_findings([app.route for app in sorted_apps], "app route"))
    findings.extend(_duplicate_findings([app.canonical_url for app in sorted_apps], "canonical URL"))
    if any(app.number == 101 or app.slug == "app-101" or app.app_id == "app_101" for app in sorted_apps):
        findings.append(ValidationFinding(Severity.BLOCKER, ValidationCode.APP_101_PROHIBITED, "App #101 is prohibited", "app_101"))
    category_ids = {category.category_id for category in sorted_categories}
    app_ids = {app.app_id for app in sorted_apps}
    for app in sorted_apps:
        findings.extend(validate_route_pair(app.route, app.canonical_url, subject=app.app_id).findings)
        if app.category_id not in category_ids:
            findings.append(ValidationFinding(Severity.BLOCKER, ValidationCode.UNRESOLVED_RELATIONSHIP, "Category reference is unresolved", app.app_id))
        for related in app.related_app_ids:
            if related not in app_ids or related == app.app_id:
                findings.append(ValidationFinding(Severity.BLOCKER, ValidationCode.UNRESOLVED_RELATIONSHIP, "Related app reference is unresolved", app.app_id))
    release = EntityRelease(PlatformEntity(), sorted_pages, sorted_categories, sorted_apps)
    return release, merge_results(ValidationResult(tuple(findings)))
