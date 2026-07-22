from __future__ import annotations

import inspect
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from app.modules.assistant import learning_intelligence
from app.modules.assistant.learning_intelligence import (
    MAX_LEARNING_TOOLS,
    learning_intent_for_message,
    query_learning_intelligence,
)
from app.modules.assistant.schemas import AssistantAction, AssistantClientContext
from app.modules.assistant.service import AssistantKnowledgeIndex, KnowledgeEntry, query_assistant
from app.modules.assistant.tools import AssistantToolContext, AssistantToolDefinition, AssistantToolRegistry, AssistantToolResult
from app.modules.assistant.user_context import PlatformUserContext


class AstraLearningIntelligenceTests(unittest.TestCase):
    def setUp(self):
        self.allowed_routes = frozenset({"/quiz/play", "/quiz/results", "/course-tracker/courses"})
        self.platform_context = PlatformUserContext(
            profile="tool_execution",
            is_authenticated=True,
            user_reference="user-a",
            current_route="/course-tracker/courses",
            current_app_slug="course-tracker",
        )

    def _registry(
        self,
        *,
        course_status: str = "success",
        quiz_status: str = "success",
        course_reason: str = "OVERDUE_TARGET_DATE",
        quiz_average: float = 42.0,
    ) -> AssistantToolRegistry:
        registry = AssistantToolRegistry()
        registry.register(
            _tool(
                "recommend_next_course_action",
                "course-tracker",
                ("recommend_next_course_action",),
                lambda context, arguments: AssistantToolResult(
                    tool_name="recommend_next_course_action",
                    source_app="course-tracker",
                    status=course_status,
                    data={
                        "primaryRecommendation": {
                            "course": "Data Structures",
                            "actionType": "continue",
                            "progressPercent": 50,
                            "reasonCode": course_reason,
                            "reason": "this active course is past its target date.",
                        },
                        "alternatives": [],
                    }
                    if course_status == "success"
                    else {"primaryRecommendation": {}, "alternatives": []},
                    summary_facts=("Continue Data Structures.",) if course_status == "success" else ("No active course.",),
                    actions=(AssistantAction(type="app", label="Open Course Tracker", route="/course-tracker/courses"),),
                    metadata={"resultCount": 1 if course_status == "success" else 0},
                ),
                output_schema={
                    "type": "object",
                    "properties": {"primaryRecommendation": {"type": "object"}, "alternatives": {"type": "array"}},
                    "required": ["primaryRecommendation", "alternatives"],
                    "additionalProperties": False,
                },
            ),
            owning_app="course-tracker",
        )
        registry.register(
            _tool(
                "get_quiz_topic_performance",
                "quiz",
                ("quiz_topic_performance",),
                lambda context, arguments: AssistantToolResult(
                    tool_name="get_quiz_topic_performance",
                    source_app="quiz",
                    status=quiz_status,
                    data={
                        "strongestTopics": [{"topic": "Communication", "averageScorePercent": 80, "attemptCount": 2}],
                        "weakestTopics": [{"topic": "Leadership", "averageScorePercent": quiz_average, "attemptCount": 2}],
                        "minimumAttemptEvidence": 2,
                    }
                    if quiz_status == "success"
                    else {"strongestTopics": [], "weakestTopics": [], "minimumAttemptEvidence": 2},
                    summary_facts=("Your weakest Quiz topic is Leadership.",)
                    if quiz_status == "success"
                    else ("There is not enough Quiz topic evidence yet.",),
                    actions=(AssistantAction(type="app", label="Open Quiz", route="/quiz/play"),),
                    metadata={"resultCount": 2 if quiz_status == "success" else 0},
                ),
                output_schema={
                    "type": "object",
                    "properties": {
                        "strongestTopics": {"type": "array"},
                        "weakestTopics": {"type": "array"},
                        "minimumAttemptEvidence": {"type": "integer"},
                    },
                    "required": ["strongestTopics", "weakestTopics", "minimumAttemptEvidence"],
                    "additionalProperties": False,
                },
            ),
            owning_app="quiz",
        )
        return registry

    def test_learning_intent_classifies_cross_app_questions(self):
        self.assertEqual(learning_intent_for_message("What should I study today?"), "daily")
        self.assertEqual(learning_intent_for_message("Should I continue my course or revise Quiz?"), "comparison")
        self.assertEqual(learning_intent_for_message("I have one hour to study."), "time_budget")
        self.assertEqual(learning_intent_for_message("Give me my learning summary."), "summary")
        self.assertIsNone(learning_intent_for_message("Show pricing."))
        self.assertIsNone(learning_intent_for_message("Mark my course as completed."))

    def test_learning_intelligence_combines_registered_tool_results(self):
        response = query_learning_intelligence(
            message="What should I study today?",
            registry=self._registry(),
            current_user=SimpleNamespace(id="user-a"),
            platform_context=self.platform_context,
            allowed_routes=self.allowed_routes,
        )

        self.assertIsNotNone(response)
        self.assertEqual(response.response_mode, "deterministic")
        self.assertIn("Continue Data Structures", response.answer)
        self.assertEqual([source.title for source in response.sources], ["Course Tracker", "Quiz"])
        self.assertEqual(response.actions[0].route, "/course-tracker/courses")

    def test_weakness_intent_prioritizes_quiz_without_changing_course_data(self):
        response = query_learning_intelligence(
            message="Which Quiz topic should I revise?",
            registry=self._registry(course_reason="NEAREST_COMPLETION"),
            current_user=SimpleNamespace(id="user-a"),
            platform_context=self.platform_context,
            allowed_routes=self.allowed_routes,
        )

        self.assertIsNotNone(response)
        self.assertIn("Revise Leadership", response.answer)
        self.assertEqual(response.actions[0].route, "/quiz/play")

    def test_partial_data_uses_available_source_truthfully(self):
        response = query_learning_intelligence(
            message="What should I study today?",
            registry=self._registry(course_status="empty", quiz_status="success"),
            current_user=SimpleNamespace(id="user-a"),
            platform_context=self.platform_context,
            allowed_routes=self.allowed_routes,
        )

        self.assertIsNotNone(response)
        self.assertIn("Revise Leadership", response.answer)
        self.assertEqual([source.title for source in response.sources], ["Quiz"])

    def test_no_data_returns_truthful_empty_guidance(self):
        response = query_learning_intelligence(
            message="What should I study today?",
            registry=self._registry(course_status="empty", quiz_status="empty"),
            current_user=SimpleNamespace(id="user-a"),
            platform_context=self.platform_context,
            allowed_routes=self.allowed_routes,
        )

        self.assertIsNotNone(response)
        self.assertIn("do not have enough Quiz or Course Tracker activity", response.answer)
        self.assertEqual(response.confidence, "low")

    def test_anonymous_learning_intelligence_is_rejected(self):
        response = query_learning_intelligence(
            message="What should I study today?",
            registry=self._registry(),
            current_user=None,
            platform_context=PlatformUserContext(profile="tool_execution", is_authenticated=False),
            allowed_routes=self.allowed_routes,
        )

        self.assertIsNotNone(response)
        self.assertIn("Please sign in", response.answer)
        self.assertEqual(response.sources, [])

    def test_learning_module_does_not_import_app_databases_or_services(self):
        source = inspect.getsource(learning_intelligence)

        self.assertNotIn("app.modules.quiz", source)
        self.assertNotIn("app.modules.course_tracker", source)
        self.assertNotIn("sqlalchemy", source)
        self.assertLessEqual(MAX_LEARNING_TOOLS, 2)

    def test_assistant_learning_query_is_gated_by_default(self):
        index = AssistantKnowledgeIndex(entries=(), allowed_routes=self.allowed_routes)
        with (
            patch("app.modules.assistant.service.build_knowledge_index", return_value=index),
            patch("app.modules.assistant.service.build_assistant_tool_registry") as registry_builder,
        ):
            response = query_assistant(
                object(),
                "What should I study today?",
                current_user=SimpleNamespace(id="user-a"),
            )

        registry_builder.assert_not_called()
        self.assertIn("not currently available", response.answer)

    def test_assistant_learning_query_uses_registry_when_gate_enabled(self):
        index = AssistantKnowledgeIndex(
            entries=(
                KnowledgeEntry(
                    id="app:quiz",
                    title="Quiz",
                    source_type="app",
                    route="/quiz/play",
                    summary="Practice quizzes.",
                    keywords=("quiz",),
                    action_label="Open Quiz",
                    action_type="app",
                ),
                KnowledgeEntry(
                    id="app:course-tracker",
                    title="Course Tracker",
                    source_type="app",
                    route="/course-tracker/courses",
                    summary="Track course progress.",
                    keywords=("course",),
                    action_label="Open Course Tracker",
                    action_type="app",
                ),
            ),
            allowed_routes=self.allowed_routes,
        )
        with (
            patch("app.modules.assistant.service.build_knowledge_index", return_value=index),
            patch("app.modules.assistant.service.settings.ASTRA_PERSONAL_DATA_TOOLS_ENABLED", True),
            patch("app.modules.assistant.service.build_assistant_tool_registry", return_value=self._registry()),
            patch("app.modules.assistant.service.build_platform_user_context", return_value=self.platform_context),
        ):
            response = query_assistant(
                object(),
                "What should I study today?",
                context=AssistantClientContext(currentRoute="/course-tracker/courses"),
                current_user=SimpleNamespace(id="user-a"),
            )

        self.assertEqual(response.response_mode, "deterministic")
        self.assertIn("Continue Data Structures", response.answer)
        self.assertEqual(len(response.sources), 2)


def _tool(
    name: str,
    source_app: str,
    intents: tuple[str, ...],
    handler,
    *,
    output_schema: dict,
) -> AssistantToolDefinition:
    return AssistantToolDefinition(
        name=name,
        description=f"{name} test tool.",
        source_app=source_app,
        input_schema={"type": "object", "properties": {}, "additionalProperties": False},
        output_schema=output_schema,
        handler=handler,
        requires_authentication=True,
        read_only=True,
        timeout_seconds=2.0,
        visibility="authenticated",
        deterministic_intents=intents,
        max_result_items=5,
        owner_scoped=True,
        permission_scope="owner",
        version="1.0.0",
        enabled=True,
        deprecated=False,
        documentation_path=f"app/modules/{source_app}/astra-ai.md",
    )


if __name__ == "__main__":
    unittest.main()
