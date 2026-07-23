from __future__ import annotations

import importlib
import json

import pytest

from app.modules.ai_seo_compiler import COMPILER_RUNTIME_ENABLED, stable_digest, stable_json
from app.modules.ai_seo_compiler.fixtures import ValidationFixture, validate_fixture
from app.modules.ai_seo_compiler.inventory import (
    SourceInventory,
    SourceInventoryItem,
    SourceKind,
    SourceRepository,
    SourceVisibility,
    classify_source,
)


def _source(path: str, field_name: str = "purpose") -> SourceInventoryItem:
    return SourceInventoryItem(
        repository=SourceRepository.BACKEND,
        path=path,
        section="Purpose",
        field_name=field_name,
    )


def test_compiler_foundation_is_disabled_by_default():
    assert COMPILER_RUNTIME_ENABLED is False


def test_source_inventory_has_stable_ordering():
    later = _source("app/modules/quiz/story.md", "purpose")
    earlier = _source("app/modules/content/data/overview/bill-splitter.json", "summary")
    inventory = SourceInventory.from_items([later, earlier])
    assert [item.path for item in inventory.items] == [
        "app/modules/content/data/overview/bill-splitter.json",
        "app/modules/quiz/story.md",
    ]


def test_stable_serialization_and_digest_are_deterministic():
    inventory = SourceInventory.from_items(
        [
            _source("app/modules/quiz/story.md"),
            SourceInventoryItem(
                repository=SourceRepository.FRONTEND,
                path="src/app/router/appOverviewRegistry.ts",
                section="Registry",
                field_name="route",
            ),
        ]
    ).as_dict()
    shuffled = {"items": list(reversed(inventory["items"])), "compilerRuntimeEnabled": False, "schemaVersion": 1}
    assert stable_json(inventory) == stable_json(json.loads(stable_json(inventory)))
    assert stable_digest(inventory) == stable_digest(json.loads(stable_json(inventory)))
    assert stable_digest(inventory) != stable_digest(shuffled)


@pytest.mark.parametrize(
    ("repository", "path", "expected"),
    [
        (SourceRepository.BACKEND, "app/modules/content/data/overview/quiz.json", SourceKind.BACKEND_OVERVIEW_JSON),
        (SourceRepository.BACKEND, "app/modules/quiz/story.md", SourceKind.STORY_MD),
        (SourceRepository.BACKEND, "app/modules/quiz/destination.md", SourceKind.DESTINATION_MD),
        (SourceRepository.BACKEND, "app/modules/quiz/market-study.md", SourceKind.MARKET_STUDY_MD),
        (SourceRepository.BACKEND, "app/modules/quiz/marketing.md", SourceKind.MARKETING_MD),
        (SourceRepository.BACKEND, "docs/ai-seo-compiler-validation-pipeline.md", SourceKind.SEO_ARCHITECTURE_DOC),
        (SourceRepository.FRONTEND, "src/app/router/appOverviewRegistry.ts", SourceKind.FRONTEND_APP_REGISTRY),
        (SourceRepository.FRONTEND, "src/app/router/routes.ts", SourceKind.FRONTEND_ROUTE_REGISTRY),
    ],
)
def test_allowlisted_source_classification(repository, path, expected):
    assert classify_source(repository, path) is expected


@pytest.mark.parametrize(
    "path",
    [
        "/app/modules/quiz/story.md",
        "../ansiversa-api/app/modules/quiz/story.md",
        "app/modules/quiz/private-notes.md",
        "app/modules/quiz/story.md/../destination.md",
    ],
)
def test_source_inventory_rejects_non_allowlisted_or_unsafe_paths(path):
    with pytest.raises(ValueError):
        SourceInventoryItem(
            repository=SourceRepository.BACKEND,
            path=path,
            section="Purpose",
            field_name="purpose",
        )


def test_fixture_validation_rejects_unsupported_visibility():
    source = _source("app/modules/quiz/story.md")
    with pytest.raises(ValueError, match="unsupported"):
        ValidationFixture(
            fixture_id="bad-visibility",
            source=source,
            claims=("Quiz helps users practice.",),
            expected_visibility="unsupported",
        )


def test_fixture_validation_rejects_prohibited_visibility():
    source = SourceInventoryItem(
        repository=SourceRepository.BACKEND,
        path="app/modules/quiz/story.md",
        section="Purpose",
        field_name="purpose",
        visibility=SourceVisibility.PROHIBITED,
    )
    fixture = ValidationFixture(
        fixture_id="prohibited-source",
        source=source,
        claims=("Do not publish.",),
        expected_visibility=SourceVisibility.PUBLIC,
    )
    with pytest.raises(ValueError, match="Prohibited source visibility"):
        validate_fixture(fixture)


def test_fixture_validation_rejects_unsafe_claim_data():
    fixture = ValidationFixture(
        fixture_id="unsafe-claim",
        source=_source("app/modules/quiz/story.md"),
        claims=("DATABASE_URL=postgresql://user:pass@example/db",),
    )
    with pytest.raises(ValueError, match="Unsafe fixture data detected"):
        validate_fixture(fixture)


def test_fixture_validation_accepts_bounded_public_claims():
    fixture = ValidationFixture(
        fixture_id="safe-public-claim",
        source=_source("app/modules/quiz/story.md"),
        claims=("Quiz helps users practice approved learning workflows.",),
    )
    validate_fixture(fixture)
    assert fixture.as_dict()["expectedVisibility"] == "public"


def test_compiler_package_is_not_registered_with_runtime_routes():
    main_source = importlib.import_module("app.main")
    route_modules = {getattr(route.endpoint, "__module__", "") for route in main_source.app.routes}
    assert not any(module.startswith("app.modules.ai_seo_compiler") for module in route_modules)
