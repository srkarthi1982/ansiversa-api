"""Source inventory models for the disabled AI SEO compiler foundation."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum
from pathlib import PurePosixPath
from typing import Iterable


class SourceRepository(StrEnum):
    BACKEND = "ansiversa-api"
    FRONTEND = "ansiversa"


class SourceKind(StrEnum):
    BACKEND_OVERVIEW_JSON = "backend_overview_json"
    FRONTEND_APP_REGISTRY = "frontend_app_registry"
    FRONTEND_ROUTE_REGISTRY = "frontend_route_registry"
    STORY_MD = "story_md"
    DESTINATION_MD = "destination_md"
    MARKET_STUDY_MD = "market_study_md"
    MARKETING_MD = "marketing_md"
    SEO_ARCHITECTURE_DOC = "seo_architecture_doc"


class SourceVisibility(StrEnum):
    PUBLIC = "public"
    GOVERNANCE_ONLY = "governance_only"
    PROHIBITED = "prohibited"


_MODULE_DOC_RE = re.compile(r"^app/modules/[a-z0-9_]+/(story|destination|market-study|marketing)\.md$")
_OVERVIEW_RE = re.compile(r"^app/modules/content/data/overview/[a-z0-9-]+\.json$")
_SEO_DOC_RE = re.compile(r"^docs/(ai-seo-[a-z0-9-]+|iterations/2026-08-ai-seo/[a-z0-9-]+)\.md$")


def _safe_relative_path(path: str) -> str:
    normalized = str(PurePosixPath(path))
    if path != normalized or path.startswith(("/", "~")) or normalized.startswith("../") or "/../" in normalized:
        raise ValueError(f"Source path must be normalized and repository-relative: {path}")
    if normalized == "." or not normalized:
        raise ValueError("Source path is required")
    return normalized


def classify_source(repository: SourceRepository | str, path: str) -> SourceKind:
    repo = SourceRepository(repository)
    normalized = _safe_relative_path(path)
    if repo is SourceRepository.BACKEND:
        if _OVERVIEW_RE.fullmatch(normalized):
            return SourceKind.BACKEND_OVERVIEW_JSON
        module_doc = _MODULE_DOC_RE.fullmatch(normalized)
        if module_doc:
            return {
                "story": SourceKind.STORY_MD,
                "destination": SourceKind.DESTINATION_MD,
                "market-study": SourceKind.MARKET_STUDY_MD,
                "marketing": SourceKind.MARKETING_MD,
            }[module_doc.group(1)]
        if _SEO_DOC_RE.fullmatch(normalized):
            return SourceKind.SEO_ARCHITECTURE_DOC
    if repo is SourceRepository.FRONTEND:
        if normalized == "src/app/router/appOverviewRegistry.ts":
            return SourceKind.FRONTEND_APP_REGISTRY
        if normalized == "src/app/router/routes.ts":
            return SourceKind.FRONTEND_ROUTE_REGISTRY
    raise ValueError(f"Source is not allowlisted for AI SEO compiler inventory: {repo}:{normalized}")


@dataclass(frozen=True)
class SourceInventoryItem:
    repository: SourceRepository
    path: str
    section: str
    field_name: str
    visibility: SourceVisibility = SourceVisibility.PUBLIC
    kind: SourceKind | None = None

    def __post_init__(self) -> None:
        normalized = _safe_relative_path(self.path)
        if not self.section.strip():
            raise ValueError("Source inventory section is required")
        if not self.field_name.strip():
            raise ValueError("Source inventory field_name is required")
        kind = self.kind or classify_source(self.repository, normalized)
        object.__setattr__(self, "repository", SourceRepository(self.repository))
        object.__setattr__(self, "path", normalized)
        object.__setattr__(self, "section", self.section.strip())
        object.__setattr__(self, "field_name", self.field_name.strip())
        object.__setattr__(self, "visibility", SourceVisibility(self.visibility))
        object.__setattr__(self, "kind", SourceKind(kind))

    def as_dict(self) -> dict[str, str]:
        return {
            "repository": self.repository.value,
            "path": self.path,
            "section": self.section,
            "fieldName": self.field_name,
            "visibility": self.visibility.value,
            "kind": self.kind.value if self.kind else classify_source(self.repository, self.path).value,
        }


@dataclass(frozen=True)
class SourceInventory:
    items: tuple[SourceInventoryItem, ...]

    @classmethod
    def from_items(cls, items: Iterable[SourceInventoryItem]) -> "SourceInventory":
        normalized = tuple(
            sorted(
                items,
                key=lambda item: (
                    item.repository.value,
                    item.path,
                    item.section,
                    item.field_name,
                    item.visibility.value,
                ),
            )
        )
        keys = [(item.repository, item.path, item.section, item.field_name) for item in normalized]
        if len(keys) != len(set(keys)):
            raise ValueError("Duplicate source inventory item")
        return cls(normalized)

    def as_dict(self) -> dict[str, object]:
        return {
            "schemaVersion": 1,
            "compilerRuntimeEnabled": False,
            "items": [item.as_dict() for item in self.items],
        }
