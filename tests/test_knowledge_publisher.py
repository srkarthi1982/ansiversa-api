from __future__ import annotations

import copy
import json
from xml.etree import ElementTree

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.modules.knowledge import builder
from app.modules.knowledge.publisher import (
    LLMS_FULL_PATH,
    LLMS_PATH,
    PUBLIC_AI_JSONLD_PATH,
    PUBLIC_AI_KNOWLEDGE_PATH,
    PUBLIC_AI_METADATA_PATH,
    PUBLIC_AI_SITEMAP_PATH,
    ROBOTS_PATH,
    _serialized_json,
    build_public_artifacts,
    canonical_url,
    validate_public_artifacts,
)
from app.modules.knowledge.registry import KnowledgeRegistry


@pytest.fixture(scope="module")
def registry_data():
    return builder.build_registry()[0]


@pytest.fixture(scope="module")
def artifacts(registry_data):
    return build_public_artifacts(KnowledgeRegistry(registry_data))


def test_public_export_matches_registry_counts(artifacts):
    knowledge = artifacts.knowledge
    assert knowledge["canonicalSource"]["name"] == "Canonical AI Knowledge Registry"
    assert len(knowledge["apps"]) == 100
    assert len(knowledge["categories"]) == 14
    assert all(app["visibility"] == "public" for app in knowledge["apps"])
    assert all(category["visibility"] == "public" for category in knowledge["categories"])


def test_public_export_filters_non_public_registry_records(registry_data):
    data = copy.deepcopy(registry_data)
    data["apps"][0]["visibility"] = "internal"
    data["apps"][1]["visibility"] = "restricted"
    data["pages"][0]["visibility"] = "authenticated"
    artifacts = build_public_artifacts(KnowledgeRegistry(data))
    names = {app["name"] for app in artifacts.knowledge["apps"]}
    page_routes = {page["route"] for page in artifacts.knowledge["pages"]}
    assert data["apps"][0]["name"] not in names
    assert data["apps"][1]["name"] not in names
    assert data["pages"][0]["route"] not in page_routes


def test_public_export_shape_contains_routes_aliases_capabilities_and_relationships(artifacts):
    bill_splitter = next(app for app in artifacts.knowledge["apps"] if app["slug"] == "bill-splitter")
    assert bill_splitter["canonicalUrl"] == "https://ansiversa.com/bill-splitter"
    assert bill_splitter["exploreUrl"].startswith("https://ansiversa.com/bill-splitter")
    assert bill_splitter["aliases"]
    assert bill_splitter["capabilities"]
    assert bill_splitter["relatedApps"]
    assert artifacts.knowledge["relationships"]
    assert all(relationship["visibility"] == "public" for relationship in artifacts.knowledge["relationships"])


def test_public_artifacts_are_valid_json_xml_and_jsonld(artifacts):
    validate_public_artifacts(artifacts)
    json.loads(_serialized_json(artifacts.knowledge))
    json.loads(_serialized_json(artifacts.jsonld))
    json.loads(_serialized_json(artifacts.metadata))
    ElementTree.fromstring(artifacts.sitemap)
    assert artifacts.jsonld["@context"] == "https://schema.org"
    graph_types = {node["@type"] for node in artifacts.jsonld["@graph"]}
    assert {"Organization", "WebSite", "CollectionPage", "FAQPage", "SoftwareApplication"} <= graph_types
    assert sum(1 for node in artifacts.jsonld["@graph"] if node["@type"] == "SoftwareApplication") == 100


def test_llms_generation_uses_markdown_convention(artifacts):
    assert artifacts.llms.startswith("# Ansiversa\n\n>")
    assert "## Core Resources" in artifacts.llms
    assert "## Public Apps" in artifacts.llms
    assert "https://ansiversa.com/public-ai-knowledge.json" in artifacts.llms
    assert artifacts.llms_full.startswith("# Ansiversa Full Public AI Context\n\n>")
    assert "Future Version Ideas" not in artifacts.llms_full
    assert "story.md" not in artifacts.llms_full
    assert " in V1" not in artifacts.llms_full
    assert "API-driven protected routes" not in artifacts.llms_full


def test_metadata_generation_covers_pages_and_apps(artifacts):
    metadata = artifacts.metadata
    assert metadata["schemaVersion"] == 1
    routes = {page["route"] for page in metadata["pages"]}
    assert {"/", "/about", "/pricing", "/faq", "/contact", "/apps"} <= routes
    assert "/bill-splitter" in routes
    assert all(page["canonical"].startswith("https://ansiversa.com") for page in metadata["pages"])
    assert all(page["openGraph"]["url"] == page["canonical"] for page in metadata["pages"])
    assert all(page["twitter"]["card"] == "summary" for page in metadata["pages"])


def test_canonical_url_validation():
    assert canonical_url("/") == "https://ansiversa.com"
    assert canonical_url("/apps") == "https://ansiversa.com/apps"
    with pytest.raises(ValueError):
        canonical_url("https://example.com")
    with pytest.raises(ValueError):
        canonical_url("//example.com")


def test_committed_public_artifacts_are_current(artifacts):
    expected = {
        PUBLIC_AI_KNOWLEDGE_PATH: _serialized_json(artifacts.knowledge),
        PUBLIC_AI_JSONLD_PATH: _serialized_json(artifacts.jsonld),
        PUBLIC_AI_METADATA_PATH: _serialized_json(artifacts.metadata),
        PUBLIC_AI_SITEMAP_PATH: artifacts.sitemap,
        LLMS_PATH: artifacts.llms,
        LLMS_FULL_PATH: artifacts.llms_full,
        ROBOTS_PATH: artifacts.robots,
    }
    for path, content in expected.items():
        assert path.exists(), f"Missing public artifact: {path}"
        assert path.read_text(encoding="utf-8") == content


def test_public_artifact_routes_are_served():
    client = TestClient(app)
    for route, expected_content_type in (
        ("/llms.txt", "text/plain"),
        ("/llms-full.txt", "text/plain"),
        ("/ai-sitemap.xml", "application/xml"),
        ("/public-ai-knowledge.json", "application/json"),
        ("/public-ai-jsonld.json", "application/ld+json"),
        ("/public-ai-metadata.json", "application/json"),
        ("/robots.txt", "text/plain"),
        ("/api/v1/knowledge/public", "application/json"),
        ("/api/v1/knowledge/public/jsonld", "application/ld+json"),
        ("/api/v1/knowledge/public/metadata", "application/json"),
    ):
        response = client.get(route)
        assert response.status_code == 200
        assert response.headers["content-type"].startswith(expected_content_type)
        assert not response.text.lstrip().lower().startswith("<!doctype html>")
        assert response.headers["cache-control"] == "public, max-age=3600"
        assert response.headers["access-control-allow-origin"] == "*"
        assert response.headers["x-robots-tag"] == "index, follow"


def test_public_artifacts_exclude_stale_boundary_and_include_bill_splitter(artifacts):
    serialized = "\n".join(
        (
            _serialized_json(artifacts.knowledge),
            _serialized_json(artifacts.jsonld),
            _serialized_json(artifacts.metadata),
            artifacts.sitemap,
            artifacts.llms,
            artifacts.llms_full,
            artifacts.robots,
        )
    )
    assert "100+" not in serialized
    assert "bill-splitter" in serialized
    assert artifacts.knowledge["platform"]["appCount"] == 100
    assert artifacts.knowledge["platform"]["catalogBoundary"]["fixedAppCount"] == 100


def test_robots_references_public_ai_resources(artifacts):
    assert "Sitemap: https://ansiversa.com/ai-sitemap.xml" in artifacts.robots
    assert "LLMs: https://ansiversa.com/llms.txt" in artifacts.robots
    assert "qa.ansiversa.com" not in artifacts.robots
