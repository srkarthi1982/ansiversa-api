from __future__ import annotations

import json
import unittest
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import patch

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.modules.assistant.schemas import AssistantClientContext
from app.modules.assistant.service import AssistantKnowledgeIndex, KnowledgeEntry, query_assistant
from app.modules.assistant.tools import AssistantToolContext, AssistantToolExecutor, AssistantToolRegistry
from app.modules.assistant.user_context import PlatformUserContext
from app.modules.quiz.astra_tools import build_quiz_astra_tools
from app.modules.quiz.models import Platform, QuizAttempt, QuizAttemptQuestion, QuizBase, Result, Roadmap, Subject, Topic


class QuizAstraToolTests(unittest.TestCase):
    def setUp(self):
        engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        QuizBase.metadata.create_all(engine)
        self.session_factory = sessionmaker(bind=engine)
        with self.session_factory() as db:
            db.add_all(
                [
                    Platform(id=1, name="Soft Skills", description="Soft skills", is_active=True, icon="icon", type="learning", question_count=20),
                    Platform(id=2, name="Leadership Skills", description="Leadership", is_active=True, icon="icon", type="learning", question_count=20),
                    Subject(id=1, platform_id=1, name="Communication", is_active=True, question_count=10),
                    Subject(id=2, platform_id=2, name="Leadership", is_active=True, question_count=10),
                    Topic(id=1, platform_id=1, subject_id=1, name="Communication", is_active=True, question_count=10),
                    Topic(id=2, platform_id=2, subject_id=2, name="Leadership", is_active=True, question_count=10),
                    Roadmap(id=1, platform_id=1, subject_id=1, topic_id=1, name="Basics", is_active=True, question_count=10),
                    Roadmap(id=2, platform_id=2, subject_id=2, topic_id=2, name="Basics", is_active=True, question_count=10),
                ]
            )
            self._submitted_result(db, user_id="user-a", platform_id=1, subject_id=1, topic_id=1, roadmap_id=1, mark=8)
            self._submitted_result(db, user_id="user-a", platform_id=1, subject_id=1, topic_id=1, roadmap_id=1, mark=6)
            self._submitted_result(db, user_id="user-a", platform_id=2, subject_id=2, topic_id=2, roadmap_id=2, mark=3)
            self._submitted_result(db, user_id="user-a", platform_id=2, subject_id=2, topic_id=2, roadmap_id=2, mark=4)
            self._submitted_result(db, user_id="user-b", platform_id=2, subject_id=2, topic_id=2, roadmap_id=2, mark=10)
            db.commit()
        self.context = AssistantToolContext(
            request_id="req-quiz",
            user=SimpleNamespace(id="user-a"),
            allowed_routes=frozenset({"/quiz/play", "/quiz/results"}),
        )

    def _submitted_result(
        self,
        db: Session,
        *,
        user_id: str,
        platform_id: int,
        subject_id: int,
        topic_id: int,
        roadmap_id: int,
        mark: int,
    ) -> None:
        result = Result(
            user_id=user_id,
            platform_id=platform_id,
            subject_id=subject_id,
            topic_id=topic_id,
            roadmap_id=roadmap_id,
            level="E",
            responses_json=json.dumps([{"id": index, "a": 0, "s": 0} for index in range(1, 11)]),
            mark=mark,
            created_at=datetime.now(timezone.utc),
        )
        db.add(result)
        db.flush()
        attempt = QuizAttempt(
            user_id=user_id,
            platform_id=platform_id,
            subject_id=subject_id,
            topic_id=topic_id,
            roadmap_id=roadmap_id,
            level="E",
            status="submitted",
            submitted_at=result.created_at,
            result_id=result.id,
            expires_at=result.created_at,
            created_at=result.created_at,
        )
        db.add(attempt)
        db.flush()
        db.add_all(
            QuizAttemptQuestion(attempt_id=attempt.id, question_id=position, position=position)
            for position in range(1, 11)
        )

    def _registry(self) -> AssistantToolRegistry:
        registry = AssistantToolRegistry()
        for tool in build_quiz_astra_tools(session_factory=self.session_factory):
            registry.register(tool, owning_app="quiz")
        return registry

    def test_quiz_tools_register_owned_metadata(self):
        registry = self._registry()
        capabilities = registry.list_capabilities(authenticated=True)

        self.assertEqual(len(capabilities), 5)
        self.assertTrue(all(capability.owning_app == "quiz" for capability in capabilities))
        self.assertTrue(all(capability.requires_authentication for capability in capabilities))
        self.assertTrue(all(capability.owner_scoped for capability in capabilities))
        self.assertTrue(all(capability.read_only for capability in capabilities))
        self.assertEqual(registry.lookup_intent("quiz_progress_summary").name, "get_quiz_progress_summary")

    def test_progress_summary_is_owner_scoped_and_bounded(self):
        result = AssistantToolExecutor(self._registry()).execute(
            "get_quiz_progress_summary",
            {},
            self.context,
        )

        self.assertEqual(result.status, "success")
        self.assertEqual(result.data["attemptCount"], 4)
        self.assertEqual(result.data["completedAttemptCount"], 4)
        self.assertEqual(result.data["platformsCompleted"], 2)
        self.assertNotIn("user-a", str(result.data))
        self.assertNotIn("user-b", str(result.data))

    def test_completed_platforms_do_not_expose_internal_ids(self):
        result = AssistantToolExecutor(self._registry()).execute(
            "get_completed_quiz_platforms",
            {},
            self.context,
        )

        self.assertEqual(result.status, "success")
        self.assertEqual(result.data["completedCount"], 2)
        self.assertEqual({item["name"] for item in result.data["completedPlatforms"]}, {"Soft Skills", "Leadership Skills"})
        self.assertNotIn("id", result.data["completedPlatforms"][0])

    def test_recent_attempts_exclude_question_bank_content(self):
        result = AssistantToolExecutor(self._registry()).execute(
            "get_recent_quiz_attempts",
            {"limit": 2},
            self.context,
        )

        self.assertEqual(result.status, "success")
        self.assertEqual(len(result.data["attempts"]), 2)
        payload = str(result.data)
        self.assertNotIn("responses", payload)
        self.assertNotIn("question", payload.lower())
        self.assertNotIn("explanation", payload.lower())

    def test_topic_performance_requires_repeated_evidence(self):
        result = AssistantToolExecutor(self._registry()).execute(
            "get_quiz_topic_performance",
            {},
            self.context,
        )

        self.assertEqual(result.status, "success")
        self.assertEqual(result.data["strongestTopics"][0]["topic"], "Communication")
        self.assertEqual(result.data["weakestTopics"][0]["topic"], "Leadership")
        self.assertEqual(result.data["minimumAttemptEvidence"], 2)

    def test_recommendation_is_deterministic_and_read_only(self):
        result = AssistantToolExecutor(self._registry()).execute(
            "recommend_next_quiz_platform",
            {},
            self.context,
        )

        self.assertEqual(result.status, "success")
        self.assertEqual(result.data["confirmedCompleted"], ["Leadership Skills", "Soft Skills"])
        self.assertEqual(result.actions[0].route, "/quiz/play")

    def test_anonymous_quiz_tool_is_denied(self):
        result = AssistantToolExecutor(self._registry()).execute(
            "get_quiz_progress_summary",
            {},
            AssistantToolContext(request_id="req-anon", allowed_routes=frozenset({"/quiz/play"})),
        )

        self.assertEqual(result.status, "denied")

    def test_assistant_quiz_query_uses_registry_when_gate_enabled(self):
        index = AssistantKnowledgeIndex(
            entries=(
                KnowledgeEntry(
                    id="app:quiz",
                    title="Quiz",
                    source_type="app",
                    route="/quiz/play",
                    summary="Practice quizzes.",
                    keywords=("quiz", "quizzes"),
                    action_label="Open Quiz",
                    action_type="app",
                ),
            ),
            allowed_routes=frozenset({"/quiz/play"}),
        )
        with (
            patch("app.modules.assistant.service.build_knowledge_index", return_value=index),
            patch("app.modules.assistant.service.settings.ASTRA_PERSONAL_DATA_TOOLS_ENABLED", True),
            patch("app.modules.assistant.service.build_assistant_tool_registry", return_value=self._registry()),
            patch(
                "app.modules.assistant.service.build_platform_user_context",
                return_value=PlatformUserContext(
                    profile="tool_execution",
                    is_authenticated=True,
                    user_reference="user-a",
                    current_route="/quiz/play",
                    current_app_slug="quiz",
                ),
            ),
        ):
            response = query_assistant(
                object(),
                "Show my Quiz progress.",
                context=AssistantClientContext(currentRoute="/quiz/play"),
                current_user=SimpleNamespace(id="user-a"),
            )

        self.assertEqual(response.response_mode, "deterministic")
        self.assertIn("completed 4 submitted Quiz attempts", response.answer)
        self.assertEqual(response.sources[0].id, "tool:get_quiz_progress_summary")

    def test_assistant_quiz_query_is_gated_by_default(self):
        index = AssistantKnowledgeIndex(entries=(), allowed_routes=frozenset({"/quiz/play"}))
        with (
            patch("app.modules.assistant.service.build_knowledge_index", return_value=index),
            patch("app.modules.assistant.service.build_assistant_tool_registry") as registry_builder,
        ):
            response = query_assistant(
                object(),
                "Show my Quiz progress.",
                current_user=SimpleNamespace(id="user-a"),
            )

        registry_builder.assert_not_called()
        self.assertIn("not currently available", response.answer)


if __name__ == "__main__":
    unittest.main()
