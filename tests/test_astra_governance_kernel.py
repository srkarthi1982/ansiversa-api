from __future__ import annotations

import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from pydantic import ValidationError

from app.modules.astra_ai.configuration import ASTRA_CONFIGURATION_ID, ASTRA_CONFIGURATION_VERSION, get_astra_configuration
from app.modules.astra_ai.constitutional_contracts import (
    ApprovalState,
    AuthorityClass,
    ConstitutionalRequirementReference,
    DecisionReasonClass,
    FailurePosture,
    GovernanceOutcome,
    ProductionAuthorizationState,
    RuntimeUseState,
    SafetyClassification,
)
from app.modules.astra_ai.governance import (
    ConsentState,
    ConstitutionalComplianceState,
    GovernanceEvaluationInput,
    GovernancePolicyFact,
    OwnerAuthorityStatus,
    PolicyFactValue,
    PrecedenceLevel,
    evaluate_governance,
)


TIMESTAMP = datetime(2026, 7, 26, 12, 0, tzinfo=timezone.utc)


def requirement():
    return ConstitutionalRequirementReference(
        constitutional_source="ASTRA-010",
        requirement_id="AIR-CM-009",
        requirement_version="1.0.0",
    )


def governance_input(**overrides):
    values = {
        "evaluation_id": "GOV-EVAL-001",
        "requirement_references": (requirement(),),
        "requested_authority_class": AuthorityClass.READ_ONLY,
        "safety_classification": SafetyClassification.PUBLIC,
        "approval_state": ApprovalState.NOT_REQUIRED,
        "consent_state": ConsentState.NOT_REQUIRED,
        "configuration_id": ASTRA_CONFIGURATION_ID,
        "configuration_version": ASTRA_CONFIGURATION_VERSION,
        "owner_authority_status": OwnerAuthorityStatus.NOT_APPLICABLE,
        "policy_facts": (),
        "requested_failure_posture": FailurePosture.FAIL_CLOSED,
        "constitutional_compliance": ConstitutionalComplianceState.KNOWN_COMPLIANT,
        "production_authorization_state": ProductionAuthorizationState.NOT_APPROVED,
        "provider_use_requested": False,
        "memory_use_requested": False,
        "adaptation_use_requested": False,
        "execution_handoff_requested": False,
        "evaluation_timestamp": TIMESTAMP,
        "evaluation_version": "1.0.0",
    }
    values.update(overrides)
    return GovernanceEvaluationInput(**values)


def policy_fact(precedence_level, fact_value, fact_reference):
    return GovernancePolicyFact(
        precedence_level=precedence_level,
        fact_value=fact_value,
        fact_reference=fact_reference,
        summary="Bounded governance fact.",
    )


class AstraGovernanceKernelTests(unittest.TestCase):
    def test_disabled_configuration_keeps_public_read_only_evaluation_non_authorizing(self):
        first = evaluate_governance(governance_input())
        second = evaluate_governance(governance_input())

        self.assertEqual(first, second)
        self.assertEqual(first.decision.outcome, GovernanceOutcome.FAIL_CLOSED)
        self.assertEqual(first.decision.decision_reason_class, DecisionReasonClass.FAIL_CLOSED_DEFAULT)
        self.assertEqual(first.decision.safety_classification, SafetyClassification.PUBLIC)
        self.assertEqual(first.evidence.decision_or_operation_reference, "GOV-EVAL-001")

    def test_enabled_configuration_cannot_be_injected_through_input(self):
        with self.assertRaises(ValidationError):
            GovernanceEvaluationInput(**{**governance_input().model_dump(), "feature_enabled": True})

        self.assertFalse(get_astra_configuration().configuration.feature_enabled)

    def test_unknown_compliance_fails_closed(self):
        result = evaluate_governance(
            governance_input(constitutional_compliance=ConstitutionalComplianceState.UNKNOWN)
        )

        self.assertEqual(result.decision.outcome, GovernanceOutcome.FAIL_CLOSED)
        self.assertEqual(result.decision.failure_posture, FailurePosture.FAIL_CLOSED)

    def test_unknown_and_prohibited_safety_cannot_allow(self):
        for safety in (SafetyClassification.UNKNOWN, SafetyClassification.PROHIBITED):
            with self.subTest(safety=safety):
                result = evaluate_governance(governance_input(safety_classification=safety))
                self.assertEqual(result.decision.outcome, GovernanceOutcome.FAIL_CLOSED)

    def test_private_write_and_high_impact_require_explicit_approval(self):
        for safety in (SafetyClassification.PRIVATE_WRITE, SafetyClassification.HIGH_IMPACT):
            with self.subTest(safety=safety):
                result = evaluate_governance(
                    governance_input(
                        safety_classification=safety,
                        requested_authority_class=AuthorityClass.APPROVAL_REQUIRED,
                    )
                )
                self.assertEqual(result.decision.outcome, GovernanceOutcome.FAIL_CLOSED)

    def test_production_boundary_requires_explicit_production_approval(self):
        result = evaluate_governance(
            governance_input(
                requested_authority_class=AuthorityClass.PRODUCTION_BOUNDARY,
                approval_state=ApprovalState.APPROVED,
                production_authorization_state=ProductionAuthorizationState.NOT_APPROVED,
            )
        )

        self.assertEqual(result.decision.outcome, GovernanceOutcome.FAIL_CLOSED)
        self.assertEqual(result.decision.authority_class, AuthorityClass.PRODUCTION_BOUNDARY)

    def test_required_pending_or_denied_approval_cannot_allow(self):
        for approval_state in (ApprovalState.REQUIRED, ApprovalState.PENDING, ApprovalState.DENIED):
            with self.subTest(approval_state=approval_state):
                result = evaluate_governance(governance_input(approval_state=approval_state))
                self.assertEqual(result.decision.outcome, GovernanceOutcome.FAIL_CLOSED)

    def test_malformed_or_missing_constitutional_references_are_rejected(self):
        with self.assertRaises(ValidationError):
            governance_input(requirement_references=())

        with self.assertRaises(ValidationError):
            GovernanceEvaluationInput(
                **{
                    **governance_input().model_dump(),
                    "requirement_references": (
                        {
                            "constitutional_source": "ASTRA-999",
                            "requirement_id": "BAD",
                            "requirement_version": "1",
                        },
                    ),
                }
            )

    def test_contradictory_facts_fail_closed(self):
        result = evaluate_governance(
            governance_input(
                owner_authority_status=OwnerAuthorityStatus.CONFLICT,
                approval_state=ApprovalState.APPROVED,
                consent_state=ConsentState.DENIED,
            )
        )

        self.assertEqual(result.decision.outcome, GovernanceOutcome.FAIL_CLOSED)

    def test_disabled_configuration_cannot_authorize_runtime_behavior(self):
        for field in (
            "provider_use_requested",
            "memory_use_requested",
            "adaptation_use_requested",
            "execution_handoff_requested",
        ):
            with self.subTest(field=field):
                result = evaluate_governance(governance_input(**{field: True}))
                self.assertEqual(result.decision.outcome, GovernanceOutcome.FAIL_CLOSED)
                self.assertEqual(result.decision.failure_posture, FailurePosture.FAIL_CLOSED)

    def test_environment_scope_does_not_create_authority(self):
        loaded = get_astra_configuration()
        result = evaluate_governance(
            governance_input(
                requested_authority_class=AuthorityClass.PRODUCTION_BOUNDARY,
                approval_state=ApprovalState.APPROVED,
                production_authorization_state=loaded.configuration.production_authorization_state,
            )
        )

        self.assertEqual(loaded.configuration.production_authorization_state, ProductionAuthorizationState.NOT_APPROVED)
        self.assertEqual(result.decision.outcome, GovernanceOutcome.FAIL_CLOSED)

    def test_environment_scope_does_not_enable_disabled_configuration_allow(self):
        loaded = get_astra_configuration()
        result = evaluate_governance(governance_input())

        self.assertFalse(loaded.configuration.feature_enabled)
        self.assertEqual(result.decision.outcome, GovernanceOutcome.FAIL_CLOSED)
        self.assertEqual(result.decision.decision_reason_class, DecisionReasonClass.FAIL_CLOSED_DEFAULT)

    def test_lower_precedence_allow_cannot_override_constitutional_constraints(self):
        result = evaluate_governance(
            governance_input(
                safety_classification=SafetyClassification.PROHIBITED,
                policy_facts=(
                    GovernancePolicyFact(
                        precedence_level=PrecedenceLevel.USER_INTENT,
                        fact_value=PolicyFactValue.ALLOW,
                        fact_reference="user:intent:allow",
                        summary="User asked to allow.",
                    ),
                ),
            )
        )

        self.assertEqual(result.decision.outcome, GovernanceOutcome.FAIL_CLOSED)
        self.assertEqual(result.decision.decision_reason_class, DecisionReasonClass.CONSTITUTIONAL_PRECEDENCE)

    def test_unknown_precedence_fact_fails_closed(self):
        result = evaluate_governance(
            governance_input(
                policy_facts=(
                    GovernancePolicyFact(
                        precedence_level=PrecedenceLevel.ACCEPTED_CONSTITUTION,
                        fact_value=PolicyFactValue.UNKNOWN,
                        fact_reference="constitution:unknown",
                        summary="Classification unresolved.",
                    ),
                ),
            )
        )

        self.assertEqual(result.decision.outcome, GovernanceOutcome.FAIL_CLOSED)

    def test_binding_block_overrides_lower_allow(self):
        result = evaluate_governance(
            governance_input(
                policy_facts=(
                    policy_fact(
                        PrecedenceLevel.USER_INTENT,
                        PolicyFactValue.ALLOW,
                        "user:intent:allow",
                    ),
                    policy_fact(
                        PrecedenceLevel.BINDING_CONSTRAINT,
                        PolicyFactValue.BLOCK,
                        "binding:constraint:block",
                    ),
                )
            )
        )

        self.assertEqual(result.decision.outcome, GovernanceOutcome.FAIL_CLOSED)
        self.assertEqual(result.decision.decision_reason_class, DecisionReasonClass.CONSTITUTIONAL_PRECEDENCE)

    def test_constitutional_block_overrides_user_allow(self):
        result = evaluate_governance(
            governance_input(
                policy_facts=(
                    policy_fact(
                        PrecedenceLevel.USER_INTENT,
                        PolicyFactValue.ALLOW,
                        "user:intent:allow",
                    ),
                    policy_fact(
                        PrecedenceLevel.ACCEPTED_CONSTITUTION,
                        PolicyFactValue.BLOCK,
                        "constitution:block",
                    ),
                )
            )
        )

        self.assertEqual(result.decision.outcome, GovernanceOutcome.FAIL_CLOSED)
        self.assertEqual(result.decision.decision_reason_class, DecisionReasonClass.CONSTITUTIONAL_PRECEDENCE)

    def test_binding_allow_is_not_overridden_by_provider_block(self):
        result = evaluate_governance(
            governance_input(
                policy_facts=(
                    policy_fact(
                        PrecedenceLevel.PROVIDER_OUTPUT_OR_INFERENCE,
                        PolicyFactValue.BLOCK,
                        "provider:inference:block",
                    ),
                    policy_fact(
                        PrecedenceLevel.BINDING_CONSTRAINT,
                        PolicyFactValue.ALLOW,
                        "binding:constraint:allow",
                    ),
                )
            )
        )

        self.assertEqual(result.decision.outcome, GovernanceOutcome.FAIL_CLOSED)
        self.assertEqual(result.decision.decision_reason_class, DecisionReasonClass.FAIL_CLOSED_DEFAULT)

    def test_same_level_allow_block_conflict_fails_closed(self):
        result = evaluate_governance(
            governance_input(
                policy_facts=(
                    policy_fact(
                        PrecedenceLevel.APPROVED_RUNTIME_POLICY,
                        PolicyFactValue.ALLOW,
                        "runtime:policy:allow",
                    ),
                    policy_fact(
                        PrecedenceLevel.APPROVED_RUNTIME_POLICY,
                        PolicyFactValue.BLOCK,
                        "runtime:policy:block",
                    ),
                )
            )
        )

        self.assertEqual(result.decision.outcome, GovernanceOutcome.FAIL_CLOSED)
        self.assertEqual(result.decision.decision_reason_class, DecisionReasonClass.CONSTITUTIONAL_PRECEDENCE)

    def test_unknown_at_decisive_highest_level_fails_closed(self):
        result = evaluate_governance(
            governance_input(
                policy_facts=(
                    policy_fact(
                        PrecedenceLevel.ACCEPTED_CONSTITUTION,
                        PolicyFactValue.UNKNOWN,
                        "constitution:unknown",
                    ),
                    policy_fact(
                        PrecedenceLevel.USER_INTENT,
                        PolicyFactValue.ALLOW,
                        "user:intent:allow",
                    ),
                )
            )
        )

        self.assertEqual(result.decision.outcome, GovernanceOutcome.FAIL_CLOSED)
        self.assertEqual(result.decision.decision_reason_class, DecisionReasonClass.CONSTITUTIONAL_PRECEDENCE)

    def test_lower_unknown_does_not_override_decisive_higher_allow(self):
        result = evaluate_governance(
            governance_input(
                policy_facts=(
                    policy_fact(
                        PrecedenceLevel.APPROVED_RUNTIME_POLICY,
                        PolicyFactValue.UNKNOWN,
                        "runtime:policy:unknown",
                    ),
                    policy_fact(
                        PrecedenceLevel.ACCEPTED_CONSTITUTION,
                        PolicyFactValue.ALLOW,
                        "constitution:allow",
                    ),
                )
            )
        )

        self.assertEqual(result.decision.outcome, GovernanceOutcome.FAIL_CLOSED)
        self.assertEqual(result.decision.decision_reason_class, DecisionReasonClass.FAIL_CLOSED_DEFAULT)

    def test_fact_ordering_does_not_change_precedence_result(self):
        lower_block = policy_fact(
            PrecedenceLevel.PROVIDER_OUTPUT_OR_INFERENCE,
            PolicyFactValue.BLOCK,
            "provider:inference:block",
        )
        higher_allow = policy_fact(
            PrecedenceLevel.ACCEPTED_CONSTITUTION,
            PolicyFactValue.ALLOW,
            "constitution:allow",
        )

        first = evaluate_governance(governance_input(policy_facts=(lower_block, higher_allow)))
        second = evaluate_governance(governance_input(policy_facts=(higher_allow, lower_block)))

        self.assertEqual(first, second)
        self.assertEqual(first.decision.outcome, GovernanceOutcome.FAIL_CLOSED)
        self.assertEqual(first.decision.decision_reason_class, DecisionReasonClass.FAIL_CLOSED_DEFAULT)

    def test_bounded_evidence_contains_required_metadata(self):
        result = evaluate_governance(governance_input())
        evidence = result.evidence

        self.assertEqual(evidence.evidence_type, "governance_decision")
        self.assertEqual(evidence.requirement_references, (requirement(),))
        self.assertEqual(evidence.timestamp, TIMESTAMP)
        self.assertEqual(evidence.minimization_class, "metadata_only")
        self.assertEqual(evidence.retention_class, "governance_record")
        self.assertEqual(evidence.integrity.source_system, "astra_ai:governance")
        self.assertEqual(evidence.correction.evidence_version, "1.0.0")
        self.assertEqual(result.decision.evidence_references, (evidence.evidence_id,))

    def test_evidence_contains_no_secret_or_prompt_payloads(self):
        with self.assertRaises(ValidationError):
            governance_input(
                policy_facts=(
                    GovernancePolicyFact(
                        precedence_level=PrecedenceLevel.USER_INTENT,
                        fact_value=PolicyFactValue.ALLOW,
                        fact_reference="user:intent:secret",
                        summary="raw prompt token=abc123",
                    ),
                )
            )

        payload = evaluate_governance(governance_input()).model_dump_json().lower()
        self.assertNotIn("token=", payload)
        self.assertNotIn("raw prompt", payload)
        self.assertNotIn("hidden_reasoning", payload)
        self.assertNotIn("full_private_payload", payload)

    def test_no_persistent_audit_write_occurs(self):
        with patch("app.modules.audit.service.write_audit_log") as write_audit_log:
            evaluate_governance(governance_input())

        write_audit_log.assert_not_called()

    def test_caller_mutation_does_not_change_authoritative_configuration(self):
        loaded = get_astra_configuration()
        loaded.configuration.feature_enabled = True

        result = evaluate_governance(governance_input(provider_use_requested=True))

        self.assertEqual(result.decision.outcome, GovernanceOutcome.FAIL_CLOSED)
        self.assertFalse(get_astra_configuration().configuration.feature_enabled)

    def test_configuration_identity_mismatch_fails_closed(self):
        result = evaluate_governance(governance_input(configuration_version="9.9.9"))

        self.assertEqual(result.decision.outcome, GovernanceOutcome.FAIL_CLOSED)
        self.assertEqual(result.decision.decision_reason_class, DecisionReasonClass.CONSTITUTIONAL_PRECEDENCE)


if __name__ == "__main__":
    unittest.main()
