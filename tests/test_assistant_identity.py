from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.modules.assistant.schemas import AssistantClientContext
from app.modules.assistant.service import build_registry_knowledge_index, query_index
from app.modules.knowledge.registry import KnowledgeRegistry

CASES_PATH = Path(__file__).parent / "fixtures" / "assistant_identity_cases.json"


@pytest.fixture(scope="module")
def index():
    return build_registry_knowledge_index()


@pytest.mark.parametrize("case", json.loads(CASES_PATH.read_text(encoding="utf-8")), ids=lambda case: case["id"])
def test_identity_and_scope_cases(case, index):
    context = AssistantClientContext(currentRoute="/quiz", currentPage="Quiz") if case.get("withContext") else None
    response = query_index(case["question"], index, context=context)
    routes = [action.route for action in response.actions]
    assert response.response_mode == case["expectedMode"]
    assert response.confidence == case["expectedConfidence"]
    assert all(phrase.lower() in response.answer.lower() for phrase in case.get("requiredPhrases", []))
    assert all(phrase.lower() not in response.answer.lower() for phrase in case.get("forbiddenPhrases", []))
    assert all(route in routes for route in case.get("expectedRoutes", []))
    assert all(route not in routes for route in case.get("forbiddenRoutes", []))
    assert all(route in index.allowed_routes for route in routes)
    assert len(routes) <= 3


def test_registry_identity_records_are_public_source_traceable_and_complete():
    records = KnowledgeRegistry.load().platform_identity()
    assert len(records) >= 10
    assert {record["visibility"] for record in records} == {"public"}
    assert all(record["questionIntents"] and record["answer"] and record["sourceReferences"] for record in records)
    assert all(".env" not in json.dumps(record) for record in records)


def test_identity_answer_cannot_be_rewritten_by_provider(index):
    class Provider:
        called = False

        def generate_answer(self, question, context):
            self.called = True
            return "Invented owner and 100+ apps."

    provider = Provider()
    response = query_index("Who founded Ansiversa?", index, answer_provider=provider)
    assert not provider.called
    assert response.response_mode == "deterministic"
    assert "Karthikeyan Ramalingam" in response.answer
    assert "100+" not in response.answer
