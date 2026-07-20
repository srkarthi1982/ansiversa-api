from __future__ import annotations

import copy
import json

import pytest

from app.modules.knowledge import builder
from app.modules.knowledge.registry import KnowledgeRegistry


@pytest.fixture(scope="module")
def generated():
    return builder.build_registry()[0]


def test_generates_exactly_100_apps(generated):
    assert len(generated["apps"]) == 100
    assert [app["number"] for app in generated["apps"]] == list(range(1, 101))


def test_output_is_deterministic(generated):
    assert builder.serialized_registry(generated) == builder.serialized_registry(builder.build_registry()[0])


def test_maps_canonical_catalog_and_routes(generated):
    expected = {app["slug"] for app in builder._frontend_apps()}
    assert {app["slug"] for app in generated["apps"]} == expected
    assert all(app["overviewRoute"] == f"/{app['slug']}" for app in generated["apps"])


def test_generates_platform_record(generated):
    assert generated["platform"]["catalogBoundary"]["fixedAppCount"] == 100
    assert generated["platform"]["catalogBoundary"]["growthModel"] == "horizontal"


def test_generates_14_categories(generated):
    assert len(generated["categories"]) == 14
    assert all(app["categoryId"] for app in generated["apps"])


def test_markdown_section_extraction_is_bounded_and_ignores_fences():
    sections = builder.parse_markdown_sections("## Purpose\nSafe text\n```\nTOKEN=secret\n```\n## Future Version Ideas\nPlanned only")
    assert sections == {"purpose": "Safe text", "future": "Planned only"}


def test_missing_markdown_section_stays_missing():
    assert builder.parse_markdown_sections("## Unmapped\nDo not infer") == {}


def test_current_and_future_are_separate(generated):
    future_apps = [app for app in generated["apps"] if app["futureDirection"]]
    assert future_apps
    assert all(app["futureDirection"]["state"] == "future" for app in future_apps)


def test_aliases_are_normalized_and_deduplicated(generated):
    salary = next(app for app in generated["apps"] if app["slug"] == "salary-breakdown-calculator")
    assert "net salary" in salary["searchAliases"]
    assert salary["searchAliases"] == list(dict.fromkeys(salary["searchAliases"]))
    assert all(alias == alias.lower() for alias in salary["searchAliases"])


def test_related_apps_are_valid_and_bounded(generated):
    slugs = {app["slug"] for app in generated["apps"]}
    assert all(0 < len(app["relatedApps"]) <= 3 for app in generated["apps"])
    assert all(related["slug"] in slugs and related["slug"] != app["slug"] for app in generated["apps"] for related in app["relatedApps"])


def test_source_traceability(generated):
    assert all(app["sourceReferences"] for app in generated["apps"])
    assert all(not ref["path"].startswith(("/", "C:")) for app in generated["apps"] for ref in app["sourceReferences"])


def test_visibility_filter_excludes_internal_and_restricted(generated):
    data = copy.deepcopy(generated)
    data["apps"][0]["visibility"] = "restricted"
    registry = KnowledgeRegistry(data)
    assert data["apps"][0] not in registry.apps()
    assert data["apps"][0] in registry.apps({"public", "restricted"})


def test_restricted_source_patterns_are_rejected(generated):
    invalid = copy.deepcopy(generated)
    invalid["apps"][0]["purpose"] = "DATABASE_URL=postgresql://user:pass@example/db"
    with pytest.raises(ValueError, match="Restricted pattern"):
        builder.validate_registry(invalid)


def test_invalid_route_is_rejected(generated):
    invalid = copy.deepcopy(generated); invalid["apps"][0]["overviewRoute"] = "https://example.com"
    with pytest.raises(ValueError, match="Invalid canonical route"):
        builder.validate_registry(invalid)


def test_duplicate_slug_is_rejected(generated):
    invalid = copy.deepcopy(generated); invalid["apps"][1]["slug"] = invalid["apps"][0]["slug"]
    with pytest.raises(ValueError, match="Duplicate app slug"):
        builder.validate_registry(invalid)


def test_unknown_app_is_rejected(generated):
    invalid = copy.deepcopy(generated); invalid["apps"][0]["slug"] = "unknown-app"
    with pytest.raises(ValueError, match="unknown or missing"):
        builder.validate_registry(invalid)


def test_stale_registry_comparison_fails(generated):
    assert builder.serialized_registry(generated) != builder.serialized_registry({**generated, "generatorVersion": "stale"})


def test_committed_registry_is_current(generated):
    assert builder.REGISTRY_PATH.read_text(encoding="utf-8") == builder.serialized_registry(generated)


def test_adapter_exact_alias_category_problem_and_capability_queries(generated):
    registry = KnowledgeRegistry(generated)
    assert registry.lookup_app("JSON Formatter")[0]["slug"] == "json-formatter"
    assert registry.lookup_app("net salary")[0]["slug"] == "salary-breakdown-calculator"
    assert registry.lookup_app("personal finance")
    assert registry.lookup_app("Compare periods clearly")[0]["slug"] == "salary-breakdown-calculator"
    assert registry.lookup_app("Six pay frequencies")[0]["slug"] == "salary-breakdown-calculator"


def test_adapter_related_and_future_contract(generated):
    registry = KnowledgeRegistry(generated)
    assert registry.related("salary-breakdown-calculator")
    future = next(app for app in registry.apps() if app["futureDirection"])
    assert future["futureDirection"]["state"] == "future"


def test_adapter_pages_and_cache_contract():
    KnowledgeRegistry.load.cache_clear()
    first = KnowledgeRegistry.load()
    second = KnowledgeRegistry.load()
    assert first is second
    page_routes = {page["route"] for page in first.pages()}
    assert {"/pricing", "/about", "/privacy", "/terms", "/faq", "/contact"} <= page_routes
    assert {"/profile", "/settings", "/subscription", "/login", "/register"} <= page_routes
