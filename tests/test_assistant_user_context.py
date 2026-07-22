from __future__ import annotations

import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.core.database import ParentBase
from app.modules.activity.models import ActivityTimelineEntry
from app.modules.apps.models import AppCatalogItem, Category
from app.modules.assistant.schemas import AssistantClientContext
from app.modules.assistant.service import AssistantKnowledgeIndex, KnowledgeEntry, query_assistant
from app.modules.assistant.user_context import build_platform_user_context
from app.modules.auth.models import Role, User, UserPreference
from app.modules.favorites.models import Favorite
from app.modules.notifications.models import Notification


class PlatformUserContextProviderTests(unittest.TestCase):
    def setUp(self):
        engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        ParentBase.metadata.create_all(engine)
        self.db = Session(engine)
        self.role = Role(id=2, name="Member", key="member")
        self.user_a = User(id="user-a", email="a@example.com", name="A", password_hash="hash", role_id=2)
        self.user_b = User(id="user-b", email="b@example.com", name="B", password_hash="hash", role_id=2)
        self.category = Category(id="cat-1", key="learning", slug="learning", name="Learning", status="active")
        self.quiz = self._app("app-quiz", "quiz", "Quiz")
        self.resume = self._app("app-resume", "resume-builder", "Resume Builder")
        self.hidden = self._app("app-hidden", "hidden-app", "Hidden App", visibility="internal")
        self.db.add_all([self.role, self.user_a, self.user_b, self.category, self.quiz, self.resume, self.hidden])
        self.db.commit()

    def tearDown(self):
        self.db.close()

    def _app(self, id: str, slug: str, name: str, *, visibility: str = "public") -> AppCatalogItem:
        return AppCatalogItem(
            id=id,
            key=slug,
            slug=slug,
            name=name,
            description=f"{name} description",
            category_id="cat-1",
            status="active",
            launch_status="live",
            visibility=visibility,
        )

    def _index(self) -> AssistantKnowledgeIndex:
        return AssistantKnowledgeIndex(
            entries=(
                KnowledgeEntry(
                    id="app:quiz",
                    title="Quiz",
                    source_type="app",
                    route="/quiz/play",
                    summary="Quiz app.",
                    keywords=("quiz",),
                    action_label="Open Quiz",
                    action_type="app",
                ),
                KnowledgeEntry(
                    id="app:resume-builder",
                    title="Resume Builder",
                    source_type="app",
                    route="/resume-builder",
                    summary="Resume app.",
                    keywords=("resume",),
                    action_label="Open Resume Builder",
                    action_type="app",
                ),
            ),
            allowed_routes=frozenset({"/apps", "/quiz/play", "/resume-builder"}),
            platform_identity=(
                {
                    "id": "astra-purpose",
                    "questionIntents": ["who is astra"],
                    "aliases": [],
                    "answer": "Astra is Ansiversa's governed Assistant.",
                    "actions": [],
                },
            ),
        )

    def test_minimal_context_validates_route_and_avoids_personal_sources(self):
        context = AssistantClientContext(currentRoute="/quiz/results")
        with (
            patch("app.modules.assistant.user_context.list_user_favorites") as favorites,
            patch("app.modules.assistant.user_context.list_activity") as activity,
            patch("app.modules.assistant.user_context.list_user_notifications") as notifications,
        ):
            result = build_platform_user_context(
                self.db,
                user=self.user_a,
                client_context=context,
                allowed_routes=self._index().allowed_routes,
                profile="minimal",
            )

        self.assertEqual(result.current_route, "/quiz/results")
        self.assertEqual(result.current_app_slug, "quiz")
        self.assertEqual(result.favorite_apps, ())
        self.assertEqual(result.recent_apps, ())
        favorites.assert_not_called()
        activity.assert_not_called()
        notifications.assert_not_called()

    def test_invalid_and_unknown_routes_are_discarded(self):
        external = build_platform_user_context(
            self.db,
            user=None,
            client_context=AssistantClientContext(currentRoute="https://example.com/quiz"),
            allowed_routes=self._index().allowed_routes,
            profile="minimal",
        )
        unknown = build_platform_user_context(
            self.db,
            user=None,
            client_context=AssistantClientContext(currentRoute="/unknown/path"),
            allowed_routes=self._index().allowed_routes,
            profile="minimal",
        )

        self.assertIsNone(external.current_route)
        self.assertIsNone(external.current_app_slug)
        self.assertIsNone(unknown.current_route)
        self.assertIsNone(unknown.current_app_slug)

    def test_personalization_context_is_owner_scoped_and_bounded(self):
        self.db.add_all(
            [
                Favorite(user_id=self.user_a.id, app_id=self.quiz.id),
                Favorite(user_id=self.user_b.id, app_id=self.resume.id),
                ActivityTimelineEntry(
                    user_id=self.user_a.id,
                    activity_type="navigation",
                    title="Opened Quiz",
                    source="app",
                    source_app_id=self.quiz.id,
                    created_at=datetime.now(timezone.utc),
                ),
                ActivityTimelineEntry(
                    user_id=self.user_b.id,
                    activity_type="navigation",
                    title="Opened Resume",
                    source="app",
                    source_app_id=self.resume.id,
                    created_at=datetime.now(timezone.utc),
                ),
            ]
        )
        self.db.commit()

        result = build_platform_user_context(
            self.db,
            user=self.user_a,
            client_context=AssistantClientContext(
                recentAppKeys=["resume-builder", "unknown", "quiz", "quiz", "../bad"]
            ),
            allowed_routes=self._index().allowed_routes,
            profile="personalization",
        )

        self.assertEqual([app.slug for app in result.favorite_apps], ["quiz"])
        self.assertEqual([app.slug for app in result.recent_apps], ["resume-builder", "quiz"])
        self.assertEqual(result.activity_summary.recent_apps, ("quiz",))
        self.assertNotIn("resume-builder", result.activity_summary.recent_apps)
        self.assertEqual(result.backend_owned_sources, ("favorites", "activity"))
        self.assertEqual(result.frontend_validated_sources, ("recent_apps",))

    def test_attention_context_summarizes_notifications_without_message_leakage(self):
        self.db.add_all(
            [
                Notification(
                    user_id=self.user_a.id,
                    title="Reminder",
                    message="Private notification body",
                    type="reminder",
                    is_read=False,
                ),
                Notification(
                    user_id=self.user_a.id,
                    title="System",
                    message="Another private body",
                    type="system",
                    is_read=False,
                ),
                Notification(
                    user_id=self.user_b.id,
                    title="Other User",
                    message="Must not leak",
                    type="system",
                    is_read=False,
                ),
                UserPreference(user_id=self.user_a.id, notifications_enabled=True),
            ]
        )
        self.db.commit()

        result = build_platform_user_context(
            self.db,
            user=self.user_a,
            client_context=None,
            allowed_routes=self._index().allowed_routes,
            profile="attention",
        )
        openai_context = result.to_openai_context()

        self.assertEqual(result.notification_summary.unread_count, 2)
        self.assertEqual(result.notification_summary.types, {"reminder": 1, "system": 1})
        self.assertNotIn("user-a", str(openai_context))
        self.assertNotIn("a@example.com", str(openai_context))
        self.assertNotIn("Private notification body", str(openai_context))

    def test_tool_execution_profile_carries_backend_owned_user_reference_only(self):
        result = build_platform_user_context(
            self.db,
            user=self.user_a,
            client_context=AssistantClientContext(currentRoute="/quiz/play"),
            allowed_routes=self._index().allowed_routes,
            profile="tool_execution",
        )

        self.assertEqual(result.user_reference, self.user_a.id)
        self.assertEqual(result.current_app_slug, "quiz")
        self.assertNotIn("user-a", str(result.to_openai_context()))

    def test_assistant_notification_context_is_deterministic_and_bypasses_openai(self):
        self.db.add(
            Notification(
                user_id=self.user_a.id,
                title="Reminder",
                message="Private notification body",
                type="reminder",
                is_read=False,
            )
        )
        self.db.commit()
        with (
            patch("app.modules.assistant.service.build_knowledge_index", return_value=self._index()),
            patch("app.modules.assistant.service.settings.ASSISTANT_OPENAI_ENABLED", True),
            patch("app.modules.assistant.service.OpenAIResponseProvider") as provider,
        ):
            response = query_assistant(self.db, "Do I have unread notifications?", current_user=self.user_a)

        provider.assert_not_called()
        self.assertEqual(response.response_mode, "deterministic")
        self.assertIn("1 unread notification", response.answer)
        self.assertNotIn("Private notification body", response.answer)
        self.assertEqual(response.sources[0].id, "platform:user-context")

    def test_identity_questions_bypass_user_context_provider(self):
        with (
            patch("app.modules.assistant.service.build_knowledge_index", return_value=self._index()),
            patch("app.modules.assistant.service.build_platform_user_context") as context_provider,
        ):
            response = query_assistant(self.db, "Who is Astra?", current_user=self.user_a)

        context_provider.assert_not_called()
        self.assertEqual(response.response_mode, "deterministic")


if __name__ == "__main__":
    unittest.main()
