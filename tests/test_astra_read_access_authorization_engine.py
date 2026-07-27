from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

from pydantic import ValidationError

from app.modules.astra_ai.constitutional_contracts import ConstitutionalRequirementReference
from app.modules.astra_ai.read_access_authorization import (
    AstraAuthorityProofIssuer,
    AstraCrossAppPolicy,
    AstraNamedReadCapability,
    AstraNamedReadCapabilityRegistry,
    AstraReadAccessAuthorizationEngine,
    AstraReadAuthorizationError,
    AstraReadAuthorizationRequest,
    AstraReadCapabilityStatus,
    AstraReadHealthOutcome,
    AstraReadPurpose,
    AstraReadSensitivity,
)
from app.modules.astra_ai.runtime import AstraRuntime, AstraRuntimeError

NOW = datetime(2026, 7, 27, 12, 0, tzinfo=timezone.utc)
RUNTIME_ID = "astra_rt_" + "a" * 32
REQ = ConstitutionalRequirementReference(
    constitutional_source="ASTRA-010", requirement_id="AIR-CM-009", requirement_version="1.0.0"
)


def capability(**changes):
    values = dict(
        read_capability_id="read_cap_expense_summary_0001",
        capability_name="expense_summary",
        owning_app_id="expense_tracker",
        owning_module="expense_tracker.reads",
        version="1.0.0",
        status=AstraReadCapabilityStatus.AVAILABLE,
        description="Metadata for an app-owned expense summary read.",
        allowed_purposes=(AstraReadPurpose.USER_REQUESTED_SUMMARY,),
        sensitivity_classification=AstraReadSensitivity.PERSONAL,
        allowed_subject_scope="current_user",
        allowed_tenant_scope="current_tenant",
        allowed_record_scope="owned_records",
        allowed_field_references=("expense.total", "expense.currency"),
        required_field_references=("expense.currency",),
        allowed_filter_references=("expense.date_range",),
        allowed_aggregation_references=("expense.sum",),
        maximum_row_count=100,
        maximum_time_range_days=366,
        timeout_class="short",
        cross_app_policy=AstraCrossAppPolicy.PROHIBITED,
        owner_service_acceptance_required=True,
        governance_requirement_references=(REQ,),
    )
    values.update(changes)
    return AstraNamedReadCapability(**values)


class AstraReadAccessAuthorizationTests(unittest.TestCase):
    def setUp(self):
        self.runtime = AstraRuntime(created_at=NOW, startup_instance_id=RUNTIME_ID)
        self.runtime.startup()

    def tearDown(self):
        if self.runtime.state.value == "ready":
            self.runtime.shutdown()

    def test_runtime_owns_one_lifecycle_bound_degraded_engine(self):
        self.assertEqual(
            tuple(item.value for item in self.runtime.registered_component_identifiers).count(
                "read_access_authorization"
            ),
            1,
        )
        interface = self.runtime.read_access_authorization
        health = interface.health(observed_at=NOW)
        self.assertEqual(health.health_outcome, AstraReadHealthOutcome.DEGRADED)
        self.assertFalse(health.principal_proof_issuer_available)
        self.assertFalse(health.owner_acceptance_issuer_available)
        self.runtime.shutdown()
        with self.assertRaises(AstraRuntimeError):
            interface.health(observed_at=NOW)

    def test_registry_is_deterministic_sealed_and_rejects_duplicates_unknowns(self):
        first = capability(read_capability_id="read_cap_z_summary_0001")
        second = capability(read_capability_id="read_cap_a_summary_0001")
        registry = AstraNamedReadCapabilityRegistry((first, second))
        self.assertEqual(
            tuple(item.read_capability_id for item in registry.capabilities),
            ("read_cap_a_summary_0001", "read_cap_z_summary_0001"),
        )
        with self.assertRaises(AstraReadAuthorizationError):
            AstraNamedReadCapabilityRegistry((first, first))
        with self.assertRaises(AstraReadAuthorizationError):
            registry.get("read_cap_unknown_0001")
        with self.assertRaises(TypeError):
            registry._items["read_cap_extra_0001"] = first

    def test_contracts_reject_wildcards_and_invalid_minimization(self):
        with self.assertRaises(ValidationError):
            capability(required_field_references=("expense.secret",))
        with self.assertRaises(ValidationError):
            AstraReadAuthorizationRequest(
                authorization_request_id="read_req_request_0001",
                runtime_instance_id=RUNTIME_ID,
                conversation_id="conv_conversation_0001",
                current_turn_reference="turn_current_0001",
                intent_resolution_reference="intent_" + "b" * 24,
                read_capability_id="read_cap_expense_summary_0001",
                authenticated_principal_reference="principal:current",
                requested_field_references=("*",),
                requested_row_limit=10,
                requested_time_range_days=30,
                declared_purpose=AstraReadPurpose.USER_REQUESTED_SUMMARY,
                requester_authority_context="authority:current",
                constitutional_requirement_references=(REQ,),
                proofs=(),
                requested_at=NOW,
                request_version="1.0.0",
            )

    def test_owner_issued_proof_rejects_copy_foreign_expired_and_unknown(self):
        issuer = AstraAuthorityProofIssuer(
            runtime_instance_id=RUNTIME_ID, issuer_reference="owner:identity", capacity=2
        )
        proof = issuer.issue(
            proof_id="proof_principal_0001",
            proof_class="principal",
            subject_reference="principal:current",
            scope_references=("scope:current",),
            issued_at=NOW,
            expires_at=NOW + timedelta(minutes=5),
            version="1.0.0",
        )
        self.assertTrue(issuer.validates(proof, observed_at=NOW))
        self.assertFalse(issuer.validates(proof.model_copy(), observed_at=NOW))
        self.assertFalse(issuer.validates(proof, observed_at=NOW + timedelta(minutes=6)))
        foreign = AstraAuthorityProofIssuer(
            runtime_instance_id="astra_rt_" + "b" * 32, issuer_reference="owner:identity"
        )
        self.assertFalse(foreign.validates(proof, observed_at=NOW))

    def test_missing_certified_authorities_fail_before_evidence(self):
        engine = AstraReadAccessAuthorizationEngine(
            runtime=self.runtime, registry=AstraNamedReadCapabilityRegistry((capability(),))
        )
        issuer = AstraAuthorityProofIssuer(runtime_instance_id=RUNTIME_ID, issuer_reference="owner:identity")
        principal = issuer.issue(
            proof_id="proof_principal_0001",
            proof_class="principal",
            subject_reference="principal:current",
            scope_references=("scope:current",),
            issued_at=NOW,
            expires_at=NOW + timedelta(minutes=5),
            version="1.0.0",
        )
        request = AstraReadAuthorizationRequest(
            authorization_request_id="read_req_request_0001",
            runtime_instance_id=RUNTIME_ID,
            conversation_id="conv_conversation_0001",
            current_turn_reference="turn_current_0001",
            intent_resolution_reference="intent_" + "b" * 24,
            read_capability_id="read_cap_expense_summary_0001",
            authenticated_principal_reference="principal:current",
            requested_field_references=("expense.currency",),
            requested_filter_references=("expense.date_range",),
            requested_aggregation_references=("expense.sum",),
            requested_row_limit=10,
            requested_time_range_days=30,
            declared_purpose=AstraReadPurpose.USER_REQUESTED_SUMMARY,
            requester_authority_context="authority:current",
            constitutional_requirement_references=(REQ,),
            proofs=(principal,),
            requested_at=NOW,
            request_version="1.0.0",
        )
        before = self.runtime.evidence_sink.count()
        with self.assertRaisesRegex(AstraReadAuthorizationError, "conversation dependency"):
            engine.authorize(
                request,
                conversation_engine=None,
                conversation_snapshot=None,
                intent_resolution=None,
            )
        self.assertEqual(self.runtime.evidence_sink.count(), before)

    def test_contract_surface_is_metadata_only(self):
        fields = set(AstraReadAuthorizationRequest.model_fields)
        forbidden = {
            "sql",
            "query",
            "session",
            "credential",
            "handler",
            "callback",
            "connection",
            "records",
            "results",
        }
        self.assertFalse(fields & forbidden)
        decision_fields = set(
            __import__(
                "app.modules.astra_ai.read_access_authorization",
                fromlist=["AstraReadAuthorizationDecision"],
            ).AstraReadAuthorizationDecision.model_fields
        )
        self.assertIn("sql_execution_state", decision_fields)
        self.assertNotIn("data", decision_fields)


if __name__ == "__main__":
    unittest.main()
