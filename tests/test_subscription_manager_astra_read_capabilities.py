import unittest
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import patch

from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.modules.subscription_manager import astra_read_capabilities as astra_capabilities
from app.modules.subscription_manager.astra_read_capabilities import (
    CAPABILITY_VERSION,
    SubscriptionAstraAuthorizationReference,
    SubscriptionAstraCapabilityError,
    SubscriptionAstraCapabilityStatus,
    SubscriptionAstraParameter,
    SubscriptionAstraReadRequest,
    capability_catalog,
    deterministic_answer,
    execute_read_capability,
    mutation_surface_report,
)
from app.modules.subscription_manager.db import SubscriptionManagerBase
from app.modules.subscription_manager.models import SubscriptionCategory, SubscriptionRecord

NOW = datetime(2026, 7, 28, 12, 0, tzinfo=timezone.utc)


class SubscriptionManagerAstraReadCapabilityTests(unittest.TestCase):
    def setUp(self):
        engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        SubscriptionManagerBase.metadata.create_all(engine)
        self.db = sessionmaker(bind=engine)()
        self.user_a = SimpleNamespace(id="user-a")
        self.user_b = SimpleNamespace(id="user-b")
        self.streaming = self._category("cat-streaming", "Streaming", self.user_a.id)
        self.productivity = self._category("cat-productivity", "Productivity", self.user_a.id)
        self.foreign = self._category("cat-foreign", "Foreign", self.user_b.id)
        self.db.add_all(
            [
                self.streaming,
                self.productivity,
                self.foreign,
                self._subscription("sub-netflix", self.user_a.id, self.streaming.id, "Netflix", "Netflix", 10, "AED", "monthly", "2026-07-29"),
                self._subscription("sub-weekly", self.user_a.id, self.streaming.id, "Weekly Music", "Music", 12, "AED", "weekly", "2026-08-27"),
                self._subscription("sub-annual", self.user_a.id, self.productivity.id, "Design Pro", "Design", 120, "USD", "annual", "2026-08-28"),
                self._subscription("sub-overdue", self.user_a.id, self.productivity.id, "Old CRM", "CRM", 20, "AED", "monthly", "2026-07-01"),
                self._subscription("sub-inactive", self.user_a.id, self.productivity.id, "Paused Tool", "Tool", 99, "AED", "monthly", "2026-07-30", status="paused"),
                self._subscription("sub-missing-date", self.user_a.id, self.productivity.id, "Manual Renewal", "Manual", 5, "AED", "custom", ""),
                self._subscription("sub-foreign", self.user_b.id, self.foreign.id, "Other User", "Other", 999, "AED", "monthly", "2026-07-29"),
            ]
        )
        self.db.commit()

    def tearDown(self):
        self.db.close()

    def test_catalog_is_fixed_versioned_and_app_owned(self):
        catalog = capability_catalog()
        self.assertEqual(len(catalog), 10)
        self.assertEqual(catalog[0].capability_id, "subscription.count_all")
        self.assertTrue(all(item.capability_version == CAPABILITY_VERSION for item in catalog))
        self.assertTrue(all(item.app_identity == "subscription_manager" for item in catalog))

    def test_count_all_and_active_are_owned_by_authenticated_user(self):
        all_result = execute_read_capability(self.db, self.user_a, self._request("subscription.count_all"))
        active_result = execute_read_capability(self.db, self.user_a, self._request("subscription.count_active"))
        foreign_result = execute_read_capability(self.db, self.user_b, self._request("subscription.count_all"))

        self.assertEqual(all_result.summary["count"], 6)
        self.assertEqual(active_result.summary["count"], 5)
        self.assertEqual(foreign_result.summary["count"], 1)
        self.assertEqual(deterministic_answer(active_result)["subject"], "active subscriptions")

    def test_list_active_excludes_inactive_and_is_deterministically_ordered(self):
        result = execute_read_capability(self.db, self.user_a, self._request("subscription.list_active", limit=3))

        self.assertEqual(result.record_count, 5)
        self.assertEqual(result.returned_count, 3)
        self.assertTrue(result.truncated)
        self.assertEqual([record["id"] for record in result.records], ["sub-overdue", "sub-netflix", "sub-weekly"])
        self.assertNotIn("sub-inactive", [record["id"] for record in result.records])

    def test_highest_cost_uses_monthly_normalization_and_deterministic_tie(self):
        result = execute_read_capability(self.db, self.user_a, self._request("subscription.highest_cost"))

        self.assertEqual(result.summary["subscription"]["id"], "sub-weekly")
        self.assertEqual(result.summary["subscription"]["monthly_estimate"], "52.00")

    def test_totals_are_grouped_by_currency_without_fx_conversion(self):
        result = execute_read_capability(self.db, self.user_a, self._request("subscription.monthly_cost_estimate"))

        self.assertEqual(
            result.records,
            (
                {"currency": "AED", "monthly_estimate": "87.00", "annual_estimate": "1044.00", "subscription_count": 4},
                {"currency": "USD", "monthly_estimate": "10.00", "annual_estimate": "120.00", "subscription_count": 1},
            ),
        )
        self.assertIn("currency_grouped_no_fx", result.reason_codes)

    def test_renewal_windows_include_exact_day_and_exclude_31_days(self):
        within_30 = execute_read_capability(
            self.db,
            self.user_a,
            self._request("subscription.renewing_within_days", parameters=(SubscriptionAstraParameter(name="days", value=30),)),
        )
        this_month = execute_read_capability(self.db, self.user_a, self._request("subscription.renewing_this_month"))

        self.assertEqual([record["id"] for record in within_30.records], ["sub-netflix", "sub-weekly"])
        self.assertNotIn("sub-annual", [record["id"] for record in within_30.records])
        self.assertEqual([record["id"] for record in this_month.records], ["sub-netflix"])

    def test_overdue_and_category_grouping_exclude_inactive(self):
        overdue = execute_read_capability(self.db, self.user_a, self._request("subscription.overdue_renewals"))
        grouped = execute_read_capability(self.db, self.user_a, self._request("subscription.group_by_category"))

        self.assertEqual([record["id"] for record in overdue.records], ["sub-overdue"])
        self.assertEqual(
            grouped.records,
            (
                {"category": "Productivity", "currency": "AED", "monthly_estimate": "25.00", "subscription_count": 2},
                {"category": "Productivity", "currency": "USD", "monthly_estimate": "10.00", "subscription_count": 1},
                {"category": "Streaming", "currency": "AED", "monthly_estimate": "62.00", "subscription_count": 2},
            ),
        )

    def test_empty_account_returns_empty_without_successful_records(self):
        result = execute_read_capability(self.db, SimpleNamespace(id="empty-user"), self._request("subscription.count_active"))

        self.assertEqual(result.status.value, "empty")
        self.assertEqual(result.record_count, 0)

    def test_request_validation_fails_closed_for_unsupported_surfaces(self):
        with self.assertRaises(SubscriptionAstraCapabilityError):
            execute_read_capability(self.db, self.user_a, self._request("subscription.unknown"))
        with self.assertRaises(ValidationError):
            self._request("subscription.list_active", limit=51)
        with self.assertRaises(ValidationError):
            self._request("subscription.count_active", caller_supplied_user_id="user-b")
        with self.assertRaises(SubscriptionAstraCapabilityError):
            execute_read_capability(
                self.db,
                self.user_a,
                self._request("subscription.count_active", parameters=(SubscriptionAstraParameter(name="days", value=30),)),
            )
        with self.assertRaises(ValidationError):
            self._request(
                "subscription.renewing_within_days",
                parameters=(SubscriptionAstraParameter(name="days", value=30), SubscriptionAstraParameter(name="days", value=31)),
            )
        with self.assertRaises(SubscriptionAstraCapabilityError):
            execute_read_capability(self.db, None, self._request("subscription.count_active"))

    def test_authorization_fails_for_stale_foreign_or_disabled_decision(self):
        with self.assertRaises(ValidationError):
            self._request("subscription.count_active", issued_at=NOW - timedelta(minutes=16))
        with self.assertRaises(ValidationError):
            self._request("subscription.count_active", app_scope="app:foreign")
        with self.assertRaises(ValidationError):
            self._request("subscription.count_active", decision_status="owner_acceptance_required")
        with self.assertRaises(ValidationError):
            self._request("subscription.count_active", production_state="approved")

    def test_disabled_capability_fails_closed(self):
        disabled = capability_catalog()[1].model_copy(update={"status": SubscriptionAstraCapabilityStatus.DISABLED})
        with patch.object(astra_capabilities, "capability_catalog", return_value=(disabled,)):
            with self.assertRaises(SubscriptionAstraCapabilityError):
                execute_read_capability(self.db, self.user_a, self._request("subscription.count_active"))

    def test_mutation_surface_and_raw_query_parameters_are_absent(self):
        self.assertTrue(mutation_surface_report()["mutation_surface_absent"])
        with self.assertRaises(ValidationError):
            SubscriptionAstraParameter(name="sql", value="select * from subscriptions")
        with self.assertRaises(ValidationError):
            SubscriptionAstraReadRequest(
                capability_id="subscription.count_active",
                capability_version=CAPABILITY_VERSION,
                app_identity="subscription_manager",
                request_reference="read-raw-sql-0001",
                requested_maximum_result_count=10,
                authorization_reference=self._authorization("subscription.count_active"),
                purpose="raw SQL",
                observed_at=NOW,
                raw_sql="select 1",
            )

    def _request(
        self,
        capability_id,
        *,
        limit=10,
        parameters=(),
        issued_at=NOW,
        app_scope="app:subscription_manager",
        decision_status="authorized_metadata_only",
        production_state="not_approved",
        caller_supplied_user_id=None,
    ):
        return SubscriptionAstraReadRequest(
            capability_id=capability_id,
            capability_version=CAPABILITY_VERSION,
            app_identity="subscription_manager",
            request_reference=f"read-request-{capability_id.replace('.', '-')}",
            requested_maximum_result_count=limit,
            authorization_reference=self._authorization(
                capability_id,
                issued_at=issued_at,
                app_scope=app_scope,
                decision_status=decision_status,
                production_state=production_state,
            ),
            purpose="user_requested_summary",
            observed_at=NOW,
            parameters=parameters,
            caller_supplied_user_id=caller_supplied_user_id,
        )

    def _authorization(
        self,
        capability_id,
        *,
        issued_at=NOW,
        app_scope="app:subscription_manager",
        decision_status="authorized_metadata_only",
        production_state="not_approved",
    ):
        return SubscriptionAstraAuthorizationReference(
            authorization_id=f"auth-ref-{capability_id.replace('.', '-')}",
            capability_id=capability_id,
            capability_version=CAPABILITY_VERSION,
            app_scope=app_scope,
            decision_status=decision_status,
            authenticated_principal_reference="principal:user-a",
            issued_at=issued_at,
            expires_at=NOW + timedelta(minutes=5),
            production_authorization_state=production_state,
        )

    def _category(self, id, name, owner_id):
        return SubscriptionCategory(id=id, owner_id=owner_id, name=name)

    def _subscription(self, id, owner_id, category_id, name, provider, amount, currency, frequency, next_billing_date, status="active"):
        return SubscriptionRecord(
            id=id,
            owner_id=owner_id,
            category_id=category_id,
            name=name,
            provider=provider,
            billing_amount=amount,
            currency_code=currency,
            billing_frequency=frequency,
            next_billing_date=next_billing_date,
            status=status,
        )


if __name__ == "__main__":
    unittest.main()
