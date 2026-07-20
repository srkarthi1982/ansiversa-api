from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.modules.assistant.service import build_registry_knowledge_index, query_index
from app.modules.knowledge.registry import KnowledgeRegistry

CASES_PATH = Path(__file__).parent / "fixtures" / "assistant_knowledge_cases.json"


@pytest.fixture(scope="module")
def registry():
    return KnowledgeRegistry.load()


@pytest.fixture(scope="module")
def index():
    return build_registry_knowledge_index()


@pytest.fixture(scope="module")
def cases():
    return json.loads(CASES_PATH.read_text(encoding="utf-8"))


def test_audit_fixture_covers_required_groups(cases):
    groups = {case["group"] for case in cases}
    assert {"A", "B", "C", "D", "E", "F", "H", "I", "J", "K", "N", "O", "P", "Q"} <= groups


def test_registry_shape_before_audit(registry, index):
    apps = registry.apps({"public"})
    categories = registry.data["categories"]
    assert len(apps) == 100
    assert len(categories) == 14
    assert {app["visibility"] for app in apps} == {"public"}
    assert all(entry.visibility == "public" for entry in index.entries)


@pytest.mark.parametrize(
    "case",
    json.loads(CASES_PATH.read_text(encoding="utf-8")),
    ids=lambda case: case["id"],
)
def test_assistant_knowledge_audit_cases(case, index):
    response = query_index(case["question"], index)
    answer = response.answer
    source_titles = [source.title for source in response.sources]
    routes = [action.route for action in response.actions]

    assert all(route in index.allowed_routes for route in routes)
    assert all(not source.id.startswith("internal:") for source in response.sources)

    if expected_mode := case.get("expectedMode"):
        assert response.response_mode == expected_mode
    if expected_source := case.get("expectedSource"):
        assert source_titles
        assert source_titles[0] == expected_source
    if expected_sources := case.get("expectedSourcesInclude"):
        assert set(expected_sources) <= set(source_titles)
    if expected_route := case.get("expectedRoute"):
        assert expected_route in routes
    if expected_text := case.get("expectedAnswerContains"):
        assert expected_text.lower() in answer.lower()
    for expected_text in case.get("expectedAnswerIncludesAll", []):
        assert expected_text in answer
    for forbidden_text in case.get("forbiddenAnswerContains", []):
        assert forbidden_text.lower() not in answer.lower()


def test_mocked_openai_remains_grounded_to_retrieved_records(index):
    class Provider:
        def __init__(self):
            self.context = ""

        def generate_answer(self, question, context):
            self.context = context
            return "Bill Splitter helps allocate item-level costs and track settlement progress."

    provider = Provider()
    response = query_index("Bill Splitter", index, answer_provider=provider)
    assert response.response_mode == "openai_grounded"
    assert response.sources[0].title == "Bill Splitter"
    assert "Title: Bill Splitter" in provider.context
    assert "/admin" not in provider.context
    assert response.actions[0].route == "/bill-splitter/bills"
