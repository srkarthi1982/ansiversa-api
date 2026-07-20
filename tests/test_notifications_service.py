import unittest
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.core.database import ParentBase
from app.modules.apps.models import AppCatalogItem, Category
from app.modules.auth.models import Role, User
from app.modules.notifications.models import Notification
from app.modules.notifications.schemas import NotificationPreferencesUpdateRequest
from app.modules.notifications.service import (
    create_notification, get_notification_preferences, get_unread_count,
    list_user_notifications, mark_all_notifications_read, mark_notification_read,
    serialize_notification, update_notification_preferences,
)


class NotificationServiceTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://", connect_args={"check_same_thread": False},
                                    poolclass=StaticPool)
        ParentBase.metadata.create_all(self.engine)
        self.db = Session(self.engine)
        self.db.add(Role(id=2, name="Member", key="member"))
        self.user = User(id="user-1", email="one@example.com", name="One",
                         password_hash="hash", role_id=2)
        self.other = User(id="user-2", email="two@example.com", name="Two",
                          password_hash="hash", role_id=2)
        category = Category(id="cat-1", key="documents", slug="documents", name="Documents")
        app = AppCatalogItem(id="app-1", key="document-expiry-tracker",
            slug="document-expiry-tracker", name="Document Expiry Tracker", description="Track documents",
            category_id="cat-1", status="active", launch_status="live", visibility="public")
        self.db.add_all([self.user, self.other, category, app]); self.db.commit()

    def tearDown(self):
        self.db.close(); self.engine.dispose()

    def add(self, user_id="user-1", title="Notice", type="info", read=False, minutes=0, metadata=None):
        item = Notification(user_id=user_id, title=title, type=type, is_read=read,
            created_at=datetime.now(timezone.utc) + timedelta(minutes=minutes), metadata_json=metadata)
        self.db.add(item); self.db.commit(); self.db.refresh(item)
        return item

    def test_owner_scope_order_pagination_filters_and_counts(self):
        self.add(title="Old", minutes=1)
        newest = self.add(title="New", type="warning", minutes=2)
        self.add(title="Read", read=True, minutes=3)
        self.add(user_id="user-2", title="Private", minutes=4)
        items, total, unread = list_user_notifications(self.db, self.user, page=1,
            page_size=2, unread_only=True, notification_type=None)
        self.assertEqual([item.id for item in items], [newest.id, items[1].id])
        self.assertEqual((total, unread), (2, 2))
        typed, typed_total, _ = list_user_notifications(self.db, self.user, page=1,
            page_size=10, unread_only=False, notification_type="warning")
        self.assertEqual(([item.id for item in typed], typed_total), ([newest.id], 1))
        page_two, total, _ = list_user_notifications(self.db, self.user, page=2,
            page_size=2, unread_only=False, notification_type=None)
        self.assertEqual((len(page_two), total), (1, 3))

    def test_read_one_is_idempotent_and_cross_account_is_hidden(self):
        item = self.add()
        first = mark_notification_read(self.db, self.user, item.id)
        read_at = first.read_at
        second = mark_notification_read(self.db, self.user, item.id)
        self.assertTrue(second.is_read); self.assertEqual(second.read_at, read_at)
        self.assertEqual(get_unread_count(self.db, self.user), 0)
        with self.assertRaises(HTTPException) as context:
            mark_notification_read(self.db, self.other, item.id)
        self.assertEqual(context.exception.status_code, 404)
        with self.assertRaises(HTTPException):
            mark_notification_read(self.db, self.user, "missing")

    def test_mark_all_only_updates_owner(self):
        self.add(); self.add(); self.add(user_id="user-2")
        self.assertEqual(mark_all_notifications_read(self.db, self.user), 2)
        self.assertEqual(get_unread_count(self.db, self.user), 0)
        self.assertEqual(get_unread_count(self.db, self.other), 1)

    def test_publisher_validates_type_owner_source_and_route(self):
        created = create_notification(self.db, user_id=self.user.id, type="due_soon",
            title="Passport expires", message="Soon", source_app_slug="document-expiry-tracker",
            action_route="/document-expiry-tracker/documents", action_label="Open documents",
            metadata={"privateToken": "must-not-leak"})
        response = serialize_notification(self.db, created)
        self.assertEqual(response.action.route, "/document-expiry-tracker/documents")
        self.assertEqual(response.source_app.name, "Document Expiry Tracker")
        self.assertNotIn("privateToken", response.model_dump_json())
        for kwargs in (
            {"type": "arbitrary"}, {"user_id": "missing"},
            {"source_app_slug": "missing"}, {"action_route": "https://evil.example"},
            {"action_route": "javascript:alert(1)"},
        ):
            payload = {"user_id": self.user.id, "type": "info", "title": "Test", **kwargs}
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                create_notification(self.db, **payload)

    def test_invalid_or_stale_action_is_omitted(self):
        item = self.add(metadata='{"sourceAppSlug":"missing","actionRoute":"//evil.example","actionLabel":"Open"}')
        response = serialize_notification(self.db, item)
        self.assertIsNone(response.source_app); self.assertIsNone(response.action)

    def test_notification_preferences_persist_on_existing_shared_row(self):
        defaults = get_notification_preferences(self.db, self.user)
        self.assertTrue(defaults.notifications_enabled)
        updated = update_notification_preferences(self.db, self.user,
            NotificationPreferencesUpdateRequest(notificationsEnabled=False,
                reminderNotificationsEnabled=False, systemNotificationsEnabled=True))
        self.assertFalse(updated.notifications_enabled)
        self.assertFalse(get_notification_preferences(self.db, self.user).reminder_notifications_enabled)

    def test_list_with_no_notifications_returns_empty_contract(self):
        items, total, unread = list_user_notifications(self.db, self.user, page=1,
            page_size=20, unread_only=False, notification_type=None)

        self.assertEqual(items, [])
        self.assertEqual((total, unread), (0, 0))


if __name__ == "__main__":
    unittest.main()
