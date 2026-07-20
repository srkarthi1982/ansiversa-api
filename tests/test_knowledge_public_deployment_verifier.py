from __future__ import annotations

import pytest

from app.modules.knowledge import verify_public_deployment as verifier
from app.modules.knowledge.publisher import _serialized_json, build_public_artifacts


@pytest.fixture(scope="module")
def artifacts():
    return build_public_artifacts()


def _result(path: str, body: str, content_type: str = "application/json") -> verifier.FetchResult:
    return verifier.FetchResult(
        path=path,
        url=f"https://ansiversa.com{path}",
        status=200,
        final_url=f"https://ansiversa.com{path}",
        redirects=0,
        content_type=content_type,
        content_length=len(body.encode("utf-8")),
        cache_control="public, max-age=3600",
        etag="",
        last_modified="",
        cors="",
        body=body,
    )


def test_verifier_validates_public_knowledge_counts_and_bill_splitter(artifacts):
    result = _result("/public-ai-knowledge.json", _serialized_json(artifacts.knowledge))

    assert verifier._validate_public_knowledge(result) == []


def test_verifier_rejects_spa_html_fallback():
    result = _result("/llms.txt", "<!doctype html><html></html>", "text/html; charset=utf-8")

    failures = verifier._validate_result(result, "text/plain", "ansiversa.com")

    assert any("returned HTML fallback" in failure for failure in failures)


def test_verifier_validates_jsonld_shape(artifacts):
    result = _result("/public-ai-jsonld.json", _serialized_json(artifacts.jsonld), "application/ld+json")

    assert verifier._validate_jsonld(result) == []


def test_verifier_validates_sitemap_shape(artifacts):
    result = _result("/ai-sitemap.xml", artifacts.sitemap, "application/xml")

    assert verifier._validate_sitemap(result) == []


def test_verifier_rejects_non_https_base_url():
    with pytest.raises(ValueError):
        verifier._normalized_base_url("http://ansiversa.com")
