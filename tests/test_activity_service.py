import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.core.database import ParentBase
from app.modules.activity.models import ActivityTimelineEntry
from app.modules.activity.service import list_activity, record_activity, record_app_navigation, serialize_activity
from app.modules.apps.models import AppCatalogItem, Category
from app.modules.auth.models import Role, User


class ActivityServiceTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        ParentBase.metadata.create_all(self.engine); self.db = Session(self.engine)
        self.db.add(Role(id=2, name="Member", key="member"))
        self.user = User(id="user-1", email="one@example.com", name="One", password_hash="hash", role_id=2)
        self.other = User(id="user-2", email="two@example.com", name="Two", password_hash="hash", role_id=2)
        category = Category(id="cat-1", key="finance", slug="finance", name="Finance")
        app = AppCatalogItem(id="app-1", key="savings-goal-planner", slug="savings-goal-planner", name="Savings Goal Planner", description="Goals", category_id="cat-1", status="active", launch_status="live", visibility="public")
        self.db.add_all([self.user, self.other, category, app]); self.db.commit()

    def tearDown(self): self.db.close(); self.engine.dispose()

    def test_owner_scope_order_pagination_and_filters(self):
        older = record_activity(self.db, user_id=self.user.id, activity_type="account", title="Profile", source="account")
        newer = record_activity(self.db, user_id=self.user.id, activity_type="created", title="Created a goal", source="app", source_app_slug="savings-goal-planner")
        record_activity(self.db, user_id=self.other.id, activity_type="system", title="Private", source="platform")
        older.created_at = datetime.now(timezone.utc) - timedelta(days=1); newer.created_at = datetime.now(timezone.utc); self.db.commit()
        items, total = list_activity(self.db, self.user, page=1, page_size=1)
        self.assertEqual(([item.id for item in items], total), ([newer.id], 2))
        page, _ = list_activity(self.db, self.user, page=2, page_size=1); self.assertEqual(page[0].id, older.id)
        filtered, total = list_activity(self.db, self.user, page=1, page_size=10, activity_type="created", app_slug="savings-goal-planner")
        self.assertEqual(([item.id for item in filtered], total), ([newer.id], 1))

    def test_route_safety_types_owner_and_sanitization(self):
        entry = record_activity(self.db, user_id=self.user.id, activity_type="updated", title="  Updated\n a goal  ", description=" safe\t summary ", source="app", source_app_slug="savings-goal-planner", action_route="/savings-goal-planner/goals/1", action_label="Open goal")
        response = serialize_activity(entry); self.assertEqual(response.title, "Updated a goal"); self.assertEqual(response.action.route, "/savings-goal-planner/goals/1")
        for kwargs in ({"activity_type": "anything"}, {"user_id": "missing"}, {"source_app_slug": "missing"}, {"action_route": "javascript:alert(1)"}, {"action_route": "https://evil.example"}):
            payload = {"user_id": self.user.id, "activity_type": "system", "title": "Safe", "source": "platform", **kwargs}
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError): record_activity(self.db, **payload)
        stale = ActivityTimelineEntry(user_id=self.user.id, activity_type="system", title="Stored", source="platform", action_route="//evil.example", action_label="Bad")
        self.db.add(stale); self.db.commit(); self.assertIsNone(serialize_activity(stale).action)

    def test_navigation_deduplication_cooldown(self):
        first = record_app_navigation(self.db, self.user, "savings-goal-planner")
        second = record_app_navigation(self.db, self.user, "savings-goal-planner")
        self.assertEqual(first.id, second.id)
        self.assertEqual(self.db.query(ActivityTimelineEntry).count(), 1)

    def test_generic_assistant_event_contains_no_prompt_answer_or_sensitive_values(self):
        entry = record_activity(self.db, user_id=self.user.id, activity_type="assistant", title="Used Ansiversa AI", description="Asked the platform assistant for help.", source="assistant")
        stored = f"{entry.title} {entry.description}"
        self.assertNotIn("prompt", stored.lower()); self.assertNotIn("AED", stored); self.assertIsNone(entry.entity_id)

    def test_safe_wrapper_failure_policy_does_not_raise(self):
        from app.modules.activity.service import record_activity_safely
        with patch("app.modules.activity.service.ParentSessionLocal", side_effect=RuntimeError("database unavailable")):
            record_activity_safely(user_id=self.user.id, activity_type="system", title="Safe")

    def test_retention_keeps_only_latest_bounded_records(self):
        with patch("app.modules.activity.service.RETENTION_LIMIT", 2):
            for index in range(3):
                record_activity(self.db, user_id=self.user.id, activity_type="system",
                    title=f"Safe event {index}", source="platform")
        _items, total = list_activity(self.db, self.user, page=1, page_size=10)
        self.assertEqual(total, 2)


if __name__ == "__main__": unittest.main()
