from __future__ import annotations

import unittest
from datetime import date, datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.modules.assistant.schemas import AssistantClientContext
from app.modules.assistant.service import AssistantKnowledgeIndex, KnowledgeEntry, query_assistant
from app.modules.assistant.tools import AssistantToolContext, AssistantToolExecutor, AssistantToolRegistry
from app.modules.assistant.user_context import PlatformUserContext
from app.modules.course_tracker.astra_tools import build_course_tracker_astra_tools
from app.modules.course_tracker.models import Course, CourseModule, CourseProgressLog
from app.modules.course_tracker.db import CourseTrackerBase
from app.modules.course_tracker.service import COURSE_TRACKER_STALLED_DAYS


class CourseTrackerAstraToolTests(unittest.TestCase):
    def setUp(self):
        engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        CourseTrackerBase.metadata.create_all(engine)
        self.session_factory = sessionmaker(bind=engine)
        today = date.today()
        now = datetime.now(timezone.utc)
        with self.session_factory() as db:
            python = Course(
                owner_id="user-a",
                title="Python Fundamentals",
                provider="Ansiversa Academy",
                category="Programming",
                goal="Private goal should not leave Course Tracker.",
                start_date=today - timedelta(days=30),
                target_date=today + timedelta(days=4),
                status="active",
                created_at=now - timedelta(days=30),
                updated_at=now - timedelta(days=1),
            )
            data_structures = Course(
                owner_id="user-a",
                title="Data Structures",
                provider="Open Learning",
                category="Computer Science",
                goal="Private goal should not leave Course Tracker.",
                start_date=today - timedelta(days=40),
                target_date=today - timedelta(days=1),
                status="active",
                created_at=now - timedelta(days=40),
                updated_at=now - timedelta(days=20),
            )
            sql = Course(
                owner_id="user-a",
                title="Introduction to SQL",
                provider="Ansiversa Academy",
                category="Databases",
                goal="Private goal should not leave Course Tracker.",
                start_date=today - timedelta(days=60),
                target_date=today - timedelta(days=10),
                status="completed",
                created_at=now - timedelta(days=60),
                updated_at=now - timedelta(days=3),
            )
            paused = Course(
                owner_id="user-a",
                title="Cloud Basics",
                provider="Cloud School",
                category="Infrastructure",
                goal="Private goal should not leave Course Tracker.",
                start_date=today - timedelta(days=20),
                target_date=None,
                status="paused",
                created_at=now - timedelta(days=20),
                updated_at=now - timedelta(days=4),
            )
            other = Course(
                owner_id="user-b",
                title="Another User Course",
                provider="Hidden Provider",
                category="Hidden",
                goal="Never exposed.",
                start_date=today,
                target_date=today,
                status="active",
                created_at=now,
                updated_at=now,
            )
            db.add_all([python, data_structures, sql, paused, other])
            db.flush()
            db.add_all(
                [
                    CourseModule(course_id=python.id, owner_id="user-a", title="Syntax", notes="Private notes", sequence=1, status="completed"),
                    CourseModule(course_id=python.id, owner_id="user-a", title="Functions", notes="Private notes", sequence=2, status="completed"),
                    CourseModule(course_id=python.id, owner_id="user-a", title="Classes", notes="Private notes", sequence=3, status="inProgress"),
                    CourseModule(course_id=data_structures.id, owner_id="user-a", title="Arrays", notes="Private notes", sequence=1, status="completed"),
                    CourseModule(course_id=data_structures.id, owner_id="user-a", title="Trees", notes="Private notes", sequence=2, status="notStarted"),
                    CourseModule(course_id=sql.id, owner_id="user-a", title="Select", notes="Private notes", sequence=1, status="completed"),
                    CourseModule(course_id=other.id, owner_id="user-b", title="Hidden", notes="Hidden notes", sequence=1, status="completed"),
                ]
            )
            db.add_all(
                [
                    CourseProgressLog(
                        course_id=python.id,
                        owner_id="user-a",
                        progress_date=today - timedelta(days=1),
                        minutes=45,
                        summary="Private progress summary",
                        reflection="Private reflection",
                    ),
                    CourseProgressLog(
                        course_id=data_structures.id,
                        owner_id="user-a",
                        progress_date=today - timedelta(days=COURSE_TRACKER_STALLED_DAYS + 2),
                        minutes=30,
                        summary="Private progress summary",
                        reflection="Private reflection",
                    ),
                    CourseProgressLog(
                        course_id=sql.id,
                        owner_id="user-a",
                        progress_date=today - timedelta(days=3),
                        minutes=60,
                        summary="Private progress summary",
                        reflection="Private reflection",
                    ),
                    CourseProgressLog(
                        course_id=other.id,
                        owner_id="user-b",
                        progress_date=today,
                        minutes=120,
                        summary="Hidden summary",
                        reflection="Hidden reflection",
                    ),
                ]
            )
            db.commit()
        self.context = AssistantToolContext(
            request_id="req-course",
            user=SimpleNamespace(id="user-a"),
            allowed_routes=frozenset({"/course-tracker/courses", "/course-tracker"}),
        )

    def _registry(self) -> AssistantToolRegistry:
        registry = AssistantToolRegistry()
        for tool in build_course_tracker_astra_tools(session_factory=self.session_factory):
            registry.register(tool, owning_app="course-tracker")
        return registry

    def test_course_tracker_tools_register_owned_metadata(self):
        registry = self._registry()
        capabilities = registry.list_capabilities(authenticated=True)

        self.assertEqual(len(capabilities), 7)
        self.assertTrue(all(capability.owning_app == "course-tracker" for capability in capabilities))
        self.assertTrue(all(capability.requires_authentication for capability in capabilities))
        self.assertTrue(all(capability.owner_scoped for capability in capabilities))
        self.assertTrue(all(capability.read_only for capability in capabilities))
        self.assertEqual(registry.lookup_intent("course_progress_summary").name, "get_course_progress_summary")

    def test_progress_summary_is_owner_scoped_and_excludes_private_text(self):
        result = AssistantToolExecutor(self._registry()).execute("get_course_progress_summary", {}, self.context)

        self.assertEqual(result.status, "success")
        self.assertEqual(result.data["courseCount"], 4)
        self.assertEqual(result.data["activeCourseCount"], 2)
        self.assertEqual(result.data["completedCourseCount"], 1)
        payload = str(result.data)
        self.assertNotIn("Another User Course", payload)
        self.assertNotIn("Private goal", payload)
        self.assertNotIn("Private progress", payload)
        self.assertNotIn("user-a", payload)

    def test_active_courses_are_bounded_and_do_not_expose_internal_ids(self):
        result = AssistantToolExecutor(self._registry()).execute("get_active_courses", {"limit": 1}, self.context)

        self.assertEqual(result.status, "success")
        self.assertEqual(result.data["activeCount"], 2)
        self.assertEqual(len(result.data["courses"]), 1)
        self.assertEqual(result.data["courses"][0]["name"], "Python Fundamentals")
        self.assertNotIn("id", result.data["courses"][0])
        self.assertNotIn("notes", str(result.data).lower())

    def test_completed_courses_follow_course_status(self):
        result = AssistantToolExecutor(self._registry()).execute("get_completed_courses", {}, self.context)

        self.assertEqual(result.status, "success")
        self.assertEqual(result.data["completedCount"], 1)
        self.assertEqual(result.data["completedCourses"][0]["name"], "Introduction to SQL")
        self.assertNotIn("Python Fundamentals", str(result.data))

    def test_nearest_completion_is_deterministic(self):
        result = AssistantToolExecutor(self._registry()).execute("get_course_nearest_completion", {}, self.context)

        self.assertEqual(result.status, "success")
        self.assertEqual(result.data["course"]["name"], "Python Fundamentals")
        self.assertEqual(result.data["reasonCode"], "HIGHEST_ACTIVE_PROGRESS")

    def test_stalled_courses_use_course_tracker_threshold(self):
        result = AssistantToolExecutor(self._registry()).execute("get_stalled_courses", {}, self.context)

        self.assertEqual(result.status, "success")
        self.assertEqual(result.data["thresholdDays"], COURSE_TRACKER_STALLED_DAYS)
        self.assertEqual(result.data["stalledCourses"][0]["name"], "Data Structures")
        self.assertEqual(result.data["stalledCourses"][0]["reasonCode"], "INACTIVE_THRESHOLD_REACHED")

    def test_deadline_summary_is_schema_backed(self):
        result = AssistantToolExecutor(self._registry()).execute("get_course_deadline_summary", {}, self.context)

        self.assertEqual(result.status, "success")
        self.assertEqual(result.data["overdueCount"], 1)
        self.assertEqual(result.data["dueSoonCount"], 1)
        self.assertEqual([item["name"] for item in result.data["courses"]], ["Data Structures", "Python Fundamentals"])

    def test_recommendation_prefers_overdue_then_explains_reason(self):
        result = AssistantToolExecutor(self._registry()).execute("recommend_next_course_action", {}, self.context)

        self.assertEqual(result.status, "success")
        self.assertEqual(result.data["primaryRecommendation"]["course"], "Data Structures")
        self.assertEqual(result.data["primaryRecommendation"]["reasonCode"], "OVERDUE_TARGET_DATE")
        self.assertEqual(result.actions[0].route, "/course-tracker/courses")

    def test_anonymous_course_tracker_tool_is_denied(self):
        result = AssistantToolExecutor(self._registry()).execute(
            "get_course_progress_summary",
            {},
            AssistantToolContext(request_id="req-anon", allowed_routes=frozenset({"/course-tracker/courses"})),
        )

        self.assertEqual(result.status, "denied")

    def test_caller_cannot_override_course_tracker_owner(self):
        result = AssistantToolExecutor(self._registry()).execute(
            "get_active_courses",
            {"userId": "user-b"},
            self.context,
        )

        self.assertEqual(result.status, "invalid_request")

    def test_assistant_course_query_uses_registry_when_gate_enabled(self):
        index = AssistantKnowledgeIndex(
            entries=(
                KnowledgeEntry(
                    id="app:course-tracker",
                    title="Course Tracker",
                    source_type="app",
                    route="/course-tracker/courses",
                    summary="Track course progress.",
                    keywords=("course", "courses", "study"),
                    action_label="Open Course Tracker",
                    action_type="app",
                ),
            ),
            allowed_routes=frozenset({"/course-tracker/courses"}),
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
                    current_route="/course-tracker/courses",
                    current_app_slug="course-tracker",
                ),
            ),
        ):
            response = query_assistant(
                object(),
                "Show my Course Tracker progress.",
                context=AssistantClientContext(currentRoute="/course-tracker/courses"),
                current_user=SimpleNamespace(id="user-a"),
            )

        self.assertEqual(response.response_mode, "deterministic")
        self.assertIn("active Course Tracker", response.answer)
        self.assertEqual(response.sources[0].id, "tool:get_course_progress_summary")
        self.assertEqual(response.sources[0].title, "Course Tracker")

    def test_current_course_tracker_context_routes_vague_continue_prompt(self):
        index = AssistantKnowledgeIndex(
            entries=(
                KnowledgeEntry(
                    id="app:course-tracker",
                    title="Course Tracker",
                    source_type="app",
                    route="/course-tracker/courses",
                    summary="Track course progress.",
                    keywords=("course", "courses", "study"),
                    action_label="Open Course Tracker",
                    action_type="app",
                ),
            ),
            allowed_routes=frozenset({"/course-tracker/courses"}),
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
                    current_route="/course-tracker/courses",
                    current_app_slug="course-tracker",
                ),
            ),
        ):
            response = query_assistant(
                object(),
                "Continue where I stopped.",
                context=AssistantClientContext(currentRoute="/course-tracker/courses"),
                current_user=SimpleNamespace(id="user-a"),
        )

        self.assertEqual(response.response_mode, "deterministic")
        self.assertEqual(response.sources[0].id, "tool:course-tracker-learning")
        self.assertIn("Data Structures", response.answer)

    def test_assistant_course_query_is_gated_by_default(self):
        index = AssistantKnowledgeIndex(entries=(), allowed_routes=frozenset({"/course-tracker/courses"}))
        with (
            patch("app.modules.assistant.service.build_knowledge_index", return_value=index),
            patch("app.modules.assistant.service.build_assistant_tool_registry") as registry_builder,
        ):
            response = query_assistant(
                object(),
                "Show my Course Tracker progress.",
                current_user=SimpleNamespace(id="user-a"),
            )

        registry_builder.assert_not_called()
        self.assertIn("not currently available", response.answer)

    def test_write_intent_does_not_execute_course_tracker_tool(self):
        index = AssistantKnowledgeIndex(entries=(), allowed_routes=frozenset({"/course-tracker/courses"}))
        with (
            patch("app.modules.assistant.service.build_knowledge_index", return_value=index),
            patch("app.modules.assistant.service.settings.ASTRA_PERSONAL_DATA_TOOLS_ENABLED", True),
            patch("app.modules.assistant.service.build_assistant_tool_registry") as registry_builder,
        ):
            response = query_assistant(
                object(),
                "Change my course to completed.",
                current_user=SimpleNamespace(id="user-a"),
            )

        registry_builder.assert_not_called()
        self.assertNotEqual(response.sources[0].id if response.sources else "", "tool:get_completed_courses")


if __name__ == "__main__":
    unittest.main()
