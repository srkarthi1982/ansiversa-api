"""Immutable registry reader and Phase 1 Assistant adapter."""

from __future__ import annotations

import json
from functools import lru_cache
from typing import Any

from app.modules.knowledge.builder import REGISTRY_PATH, VISIBILITIES, normalize_text


class KnowledgeRegistry:
    def __init__(self, data: dict[str, Any]):
        self.data = data

    @classmethod
    @lru_cache(maxsize=1)
    def load(cls) -> "KnowledgeRegistry":
        return cls(json.loads(REGISTRY_PATH.read_text(encoding="utf-8")))

    def apps(self, allowed_visibility: set[str] | None = None) -> list[dict[str, Any]]:
        allowed = allowed_visibility or {"public"}
        if not allowed <= VISIBILITIES: raise ValueError("Unknown visibility")
        return [app for app in self.data["apps"] if app["visibility"] in allowed]

    def pages(self, allowed_visibility: set[str] | None = None) -> list[dict[str, Any]]:
        allowed = allowed_visibility or {"public"}
        if not allowed <= VISIBILITIES: raise ValueError("Unknown visibility")
        return [page for page in self.data["pages"] if page["visibility"] in allowed]

    def platform_identity(self, allowed_visibility: set[str] | None = None) -> list[dict[str, Any]]:
        allowed = allowed_visibility or {"public"}
        return [
            item
            for item in self.data.get("platformIdentityKnowledge", [])
            if item["visibility"] in allowed
        ]

    def lookup_app(self, query: str, allowed_visibility: set[str] | None = None) -> list[dict[str, Any]]:
        query = normalize_text(query).lower()
        results = []
        for app in self.apps(allowed_visibility):
            searchable = [app["name"].lower(), app["slug"], app["category"].lower(), *app["searchAliases"], *[value.lower() for value in app["searchPhrases"]], *[value.lower() for value in app["currentCapabilities"]]]
            score = 100 if query in {app["name"].lower(), app["slug"]} else 80 if query in app["searchAliases"] else 50 if any(query in value for value in searchable) else 0
            if score: results.append((score, app["number"], app))
        return [app for _, _, app in sorted(results, key=lambda item: (-item[0], item[1]))]

    def related(self, slug: str) -> list[dict[str, str]]:
        app = next((item for item in self.apps() if item["slug"] == slug), None)
        return app["relatedApps"] if app else []
