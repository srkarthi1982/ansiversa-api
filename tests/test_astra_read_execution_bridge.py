from __future__ import annotations

import unittest
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.modules.astra_ai import read_execution
from app.modules.astra_ai.constitutional_contracts import (
    FailurePosture,
    GovernanceOutcome,
)
from app.modules.astra_ai.read_access_authorization import (
    AstraOwnerAcceptanceState,
    AstraReadAuthorizationDecision,
    AstraReadCheckResult,
    AstraReadDecisionStatus,
)
from app.modules.astra_ai.read_execution import (
    AstraReadAdapterDefinition,
    AstraReadAdapterRegistry,
    AstraReadExecutionError,
)
from app.modules.astra_ai.runtime import AstraRuntime, AstraRuntimeError
from app.modules.subscription_manager import astra_read_capabilities as subscription_reads
from app.modules.subscription_manager.astra_read_capabilities import (
    CAPABILITY_VERSION,
    SubscriptionAstraAuthorizationReference,
    SubscriptionAstraParameter,
    SubscriptionAstraReadRequest,
    issue_read_grant,
)
from app.modules.subscription_manager.db import SubscriptionManagerBase
from app.modules.subscription_manager.models import SubscriptionCategory, SubscriptionRecord


NOW = datetime(2026, 7, 29, 12, 0, tzinfo=timezone.utc)
RUNTIME_ID = "astra_rt_" + "c" * 32


class AstraReadExecutionBridgeTests(unittest.TestCase):
    def setUp(self):
        engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        SubscriptionManagerBase.metadata.create_all(engine)
        self.db = sessionmaker(bind=engine)()
        self.user_a = SimpleNamespace(id="user-a")
        self.user_b = SimpleNamespace(id="user-b")
        category = SubscriptionCategory(id="cat-streaming", owner_id=self.user_a.id, name="Streaming")
        self.db.add_all(
            [
                category,
                SubscriptionRecord(
                    id="sub-netflix",
                    owner_id=self.user_a.id,
                    category_id=category.id,
                    name="Netflix",
                    provider="Netflix",
                    billing_amount=10,
                    currency_code="AED",
                    billing_frequency="monthly",
                    next_billing_date="2026-08-01",
                    status="active",
                ),
                SubscriptionRecord(
                    id="sub-paused",
                    owner_id=self.user_a.id,
                    category_id=category.id,
                    name="Paused",
                    provider="Paused",
                    billing_amount=5,
                    currency_code="AED",
                    billing_frequency="monthly",
                    next_billing_date="2026-08-02",
                    status="paused",
                ),
            ]
        )
        self.db.commit()
        self.runtime = AstraRuntime(created_at=NOW, startup_instance_id=RUNTIME_ID)
        self.runtime.startup()
        self.decision = self._decision()
        self.runtime._read_execution_bridge.register_read_authorization_decision(
            self.decision,
            registration_authority=self.runtime._read_execution_registration_authority,
        )

    def tearDown(self):
        self.db.close()
        if self.runtime.state.value == "ready":
            self.runtime.shutdown()

    def test_runtime_owned_bridge_executes_subscription_adapter_with_exact_grant(self):
        grant = self._grant("subscription.count_active")
        request = self._execution_request(grant, "subscription.count_active")

        with self._clocks(NOW):
            result = self.runtime.read_execution.execute(request, db=self.db, authenticated_user=self.user_a)

        self.assertEqual(result.status.value, "ok")
        self.assertEqual(result.owning_app_id, "subscription_manager")
        self.assertEqual(result.adapter_capability_id, "subscription.count_active")
        self.assertEqual(result.summary["count"], 1)
        self.assertEqual(result.record_count, 1)
        self.assertIn("governed_read_execution_bridge", result.reason_codes)
        self.assertEqual(result.production_authorization_state, "not_approved")
        self.assertEqual(result.data_mutation_state, "prohibited")

    def test_reused_grant_and_copied_request_fail_closed(self):
        grant = self._grant("subscription.count_active")
        request = self._execution_request(grant, "subscription.count_active")

        with self._clocks(NOW):
            self.runtime.read_execution.execute(request, db=self.db, authenticated_user=self.user_a)
        with self._clocks(NOW):
            with self.assertRaises(AstraReadExecutionError):
                self.runtime.read_execution.execute(request, db=self.db, authenticated_user=self.user_a)

        second = self._execution_request(self._grant("subscription.count_active"), "subscription.count_active", request_id="read_exec_req_request_0002")
        copied = second.model_copy()
        with self._clocks(NOW):
            with self.assertRaisesRegex(AstraReadExecutionError, "exact Runtime-issued"):
                self.runtime.read_execution.execute(copied, db=self.db, authenticated_user=self.user_a)

    def test_subject_capability_and_execution_context_mismatches_fail_closed(self):
        grant = self._grant("subscription.count_active")
        request = self._execution_request(grant, "subscription.count_active")

        with self._clocks(NOW):
            with self.assertRaisesRegex(AstraReadExecutionError, "authenticated subject"):
                self.runtime.read_execution.execute(request, db=self.db, authenticated_user=self.user_b)

        with self.assertRaisesRegex(AstraReadExecutionError, "grant does not match"):
            self._execution_request(
                self._grant("subscription.count_active"),
                "subscription.list_active",
                request_id="read_exec_req_request_0003",
            )

        mismatched = self._execution_request(
            self._grant("subscription.count_active"),
            "subscription.count_active",
            request_id="read_exec_req_request_0004",
        )
        object.__setattr__(mismatched, "execution_context_reference", "read-exec/mismatched-context")
        with self._clocks(NOW):
            with self.assertRaisesRegex(AstraReadExecutionError, "context"):
                self.runtime.read_execution.execute(mismatched, db=self.db, authenticated_user=self.user_a)

    def test_unsupported_app_write_operation_and_unregistered_adapter_fail_closed(self):
        foreign_decision = self._decision(authorization_id="read_auth_foreign_0001", owning_app_id="expense_tracker")
        with self.assertRaisesRegex(AstraReadExecutionError, "Subscription Manager"):
            self.runtime._read_execution_bridge.register_read_authorization_decision(
                foreign_decision,
                registration_authority=self.runtime._read_execution_registration_authority,
            )

        grant = self._grant("subscription.count_active")
        with self.assertRaises(AstraReadExecutionError):
            self.runtime.read_execution.issue_request(
                execution_request_id="read_exec_req_request_0005",
                read_authorization_decision=self.decision,
                app_read_grant=grant,
                authenticated_principal_reference="principal:user-a",
                request_reference="subscription/request/count-active",
                requested_maximum_result_count=50,
                requested_at=NOW,
                adapter_capability_id="subscription.unknown",
                adapter_capability_version=CAPABILITY_VERSION,
            )
        write_request = self._execution_request(
            self._grant("subscription.count_active"),
            "subscription.count_active",
            request_id="read_exec_req_request_0009",
        )
        object.__setattr__(write_request, "operation", "write")
        with self._clocks(NOW):
            with self.assertRaisesRegex(AstraReadExecutionError, "read operations"):
                self.runtime.read_execution.execute(write_request, db=self.db, authenticated_user=self.user_a)

        definition = AstraReadAdapterDefinition(
            owning_app_id="subscription_manager",
            adapter_capability_id="subscription.count_active",
            adapter_capability_version=CAPABILITY_VERSION,
            operation="read",
            implementation_reference="ASTRA-READ-EXEC-001",
        )
        registry = AstraReadAdapterRegistry(((definition, lambda context: SimpleNamespace()),))
        bridge = read_execution.AstraReadExecutionBridge(
            runtime=self.runtime,
            registration_authority=self.runtime._read_execution_registration_authority,
            request_authority=self.runtime._read_execution_request_authority,
            registry=registry,
        )
        bridge.register_read_authorization_decision(
            self.decision,
            registration_authority=self.runtime._read_execution_registration_authority,
        )
        bad_request = bridge.issue_request(
            execution_request_id="read_exec_req_request_0006",
            read_authorization_decision=self.decision,
            app_read_grant=self._grant("subscription.count_active"),
            authenticated_principal_reference="principal:user-a",
            request_reference="subscription/request/count-active",
            requested_maximum_result_count=50,
            requested_at=NOW,
            adapter_capability_id="subscription.count_active",
            adapter_capability_version=CAPABILITY_VERSION,
        )
        with self._clocks(NOW):
            with self.assertRaisesRegex(AstraReadExecutionError, "invalid contract"):
                bridge.execute(bad_request, db=self.db, authenticated_user=self.user_a)

    def test_adapter_result_redaction_failure_is_bounded(self):
        definition = AstraReadAdapterDefinition(
            owning_app_id="subscription_manager",
            adapter_capability_id="subscription.count_active",
            adapter_capability_version=CAPABILITY_VERSION,
            operation="read",
            implementation_reference="ASTRA-READ-EXEC-001",
        )

        def leaking_adapter(context):
            return subscription_reads.SubscriptionAstraReadResult(
                capability_id="subscription.count_active",
                capability_version=CAPABILITY_VERSION,
                status=subscription_reads.SubscriptionAstraResultStatus.OK,
                result_kind=subscription_reads.SubscriptionAstraResultKind.COUNT,
                summary={"token": "authorization: bearer raw-secret", "count": 1},
                calculation_basis="app_owned",
                record_count=1,
                returned_count=0,
                truncated=False,
                reason_codes=("app_owned_read",),
                observed_at=NOW,
                app_scope="app:subscription_manager",
                user_scope_state="authenticated_user_only",
                authorization_state="authorized_metadata_only",
                production_authorization_state="not_approved",
            )

        bridge = read_execution.AstraReadExecutionBridge(
            runtime=self.runtime,
            registration_authority=self.runtime._read_execution_registration_authority,
            request_authority=self.runtime._read_execution_request_authority,
            registry=AstraReadAdapterRegistry(((definition, leaking_adapter),)),
        )
        bridge.register_read_authorization_decision(
            self.decision,
            registration_authority=self.runtime._read_execution_registration_authority,
        )
        request = bridge.issue_request(
            execution_request_id="read_exec_req_request_0007",
            read_authorization_decision=self.decision,
            app_read_grant=self._grant("subscription.count_active"),
            authenticated_principal_reference="principal:user-a",
            request_reference="subscription/request/count-active",
            requested_maximum_result_count=50,
            requested_at=NOW,
            adapter_capability_id="subscription.count_active",
            adapter_capability_version=CAPABILITY_VERSION,
        )
        with self._clocks(NOW):
            with self.assertRaisesRegex(AstraReadExecutionError, "private material|failed closed"):
                bridge.execute(request, db=self.db, authenticated_user=self.user_a)

    def test_runtime_shutdown_invalidates_bridge_access(self):
        interface = self.runtime.read_execution
        self.runtime.shutdown()
        with self.assertRaises(AstraRuntimeError):
            interface.issue_request(
                execution_request_id="read_exec_req_request_0008",
                read_authorization_decision=self.decision,
                app_read_grant=self._grant("subscription.count_active"),
                authenticated_principal_reference="principal:user-a",
                request_reference="subscription/request/count-active",
                requested_maximum_result_count=50,
                requested_at=NOW,
                adapter_capability_id="subscription.count_active",
                adapter_capability_version=CAPABILITY_VERSION,
            )

    def _decision(self, *, authorization_id="read_auth_subscription_0001", owning_app_id="subscription_manager"):
        return AstraReadAuthorizationDecision(
            authorization_decision_id=authorization_id,
            authorization_request_id="read_req_subscription_0001",
            governance_decision_reference="READ-EXEC-GOV-001",
            read_capability_id="read_cap_subscription_count_active_0001",
            owning_app_id=owning_app_id,
            decision_status=AstraReadDecisionStatus.AUTHORIZED_METADATA_ONLY,
            governance_outcome=GovernanceOutcome.ALLOW,
            purpose_result=AstraReadCheckResult.SATISFIED,
            principal_scope_result=AstraReadCheckResult.SATISFIED,
            tenant_scope_result=AstraReadCheckResult.SATISFIED,
            app_scope_result=AstraReadCheckResult.SATISFIED,
            record_scope_result=AstraReadCheckResult.SATISFIED,
            field_scope_result=AstraReadCheckResult.SATISFIED,
            filter_scope_result=AstraReadCheckResult.SATISFIED,
            minimization_result=AstraReadCheckResult.SATISFIED,
            row_limit_result=AstraReadCheckResult.SATISFIED,
            time_range_result=AstraReadCheckResult.SATISFIED,
            aggregation_result=AstraReadCheckResult.SATISFIED,
            cross_app_result=AstraReadCheckResult.SATISFIED,
            owner_acceptance_requirement=AstraOwnerAcceptanceState.ACCEPTED,
            evidence_references=("evd_read_auth_fixture_0001",),
            failure_posture=FailurePosture.FAIL_CLOSED,
            authorized_scope_summary=("subscription.count",),
            issued_at=NOW,
            version="1.0.0",
        )

    def _authorization_reference(self, capability_id):
        return SubscriptionAstraAuthorizationReference(
            authorization_id=self.decision.authorization_decision_id,
            governance_decision_reference=self.decision.governance_decision_reference,
            capability_id=capability_id,
            capability_version=CAPABILITY_VERSION,
            app_scope="app:subscription_manager",
            decision_status="authorized_metadata_only",
            authenticated_principal_reference="principal:user-a",
            issued_at=NOW,
            expires_at=NOW + timedelta(minutes=5),
        )

    def _grant(self, capability_id, *, parameters=()):
        request = SubscriptionAstraReadRequest(
            capability_id=capability_id,
            capability_version=CAPABILITY_VERSION,
            app_identity="subscription_manager",
            request_reference="subscription/request/count-active",
            requested_maximum_result_count=50,
            authorization_reference=self._authorization_reference(capability_id),
            purpose="Summarize current user subscriptions.",
            observed_at=NOW,
            parameters=parameters,
        )
        return issue_read_grant(authenticated_user=self.user_a, request=request)

    def _execution_request(self, grant, capability_id, *, request_id="read_exec_req_request_0001"):
        return self.runtime.read_execution.issue_request(
            execution_request_id=request_id,
            read_authorization_decision=self.decision,
            app_read_grant=grant,
            authenticated_principal_reference="principal:user-a",
            request_reference=grant.request_reference,
            requested_maximum_result_count=grant.maximum_result_count,
            requested_at=NOW,
            adapter_capability_id=capability_id,
            adapter_capability_version=CAPABILITY_VERSION,
        )

    def _clocks(self, observed_at):
        @contextmanager
        def _patched():
            with (
                patch.object(read_execution, "_utc_now", return_value=observed_at),
                patch.object(subscription_reads._SUBSCRIPTION_ASTRA_EXECUTION_CLOCK, "now", return_value=observed_at),
            ):
                yield

        return _patched()


if __name__ == "__main__":
    unittest.main()
