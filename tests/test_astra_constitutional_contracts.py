from __future__ import annotations

import unittest
from datetime import datetime, timezone

from pydantic import ValidationError

from app.modules.astra_ai import ASTRA_AI_PLATFORM_ENABLED
from app.modules.astra_ai.constitutional_contracts import (
    ActorOrServiceClass,
    ApprovalState,
    AstraConfigurationContract,
    AuditEvidenceBehavior,
    AuthorityClass,
    BoundedEvidence,
    ConstitutionalCoverageState,
    ConstitutionalRequirement,
    CorrectionPrivacyTreatment,
    ContractValidationError,
    DecisionReasonClass,
    EnvironmentScope,
    EvidenceCorrectionMetadata,
    EvidenceIntegrityMetadata,
    EvidenceType,
    FailurePosture,
    GovernanceDecision,
    GovernanceOutcome,
    MinimizationClass,
    ProductionAuthorizationState,
    RedactionStatus,
    RetentionClass,
    RuntimeUseState,
    SafetyClassification,
    SensitivityClass,
    canonical_contract_json,
)


def requirement(source: str = "ASTRA-010", requirement_id: str = "AIR-CM-009"):
    return ConstitutionalRequirement(
        constitutional_source=source,
        requirement_id=requirement_id,
        requirement_version="1.0.0",
        requirement_summary="Unknown constitutional compliance fails closed.",
        accountable_component="Governance Engine",
        coverage_state=ConstitutionalCoverageState.MAPPED,
    )


def integrity():
    return EvidenceIntegrityMetadata(
        source_system="astra_ai:contracts",
        provenance_reference="ASTRA-IMP-001",
        content_digest="sha256:" + "a" * 64,
    )


def complete_correction():
    return EvidenceCorrectionMetadata(
        evidence_version="1.0.1",
        supersedes_evidence_id="evd_contract_001",
        correction_reason="Corrected bounded metadata reference.",
        correcting_actor_or_service_class=ActorOrServiceClass.ASTRA_REVIEW,
        correction_timestamp=datetime(2026, 7, 26, 12, 0, tzinfo=timezone.utc),
        replacement_reference="ASTRA-IMP-001:correction-001",
        retention_treatment=RetentionClass.GOVERNANCE_RECORD,
        privacy_treatment=CorrectionPrivacyTreatment.METADATA_ONLY,
    )


class AstraConstitutionalContractsTests(unittest.TestCase):
    def test_valid_contract_creation_and_requirement_reference(self):
        req = requirement()

        self.assertEqual(req.coverage_state, ConstitutionalCoverageState.MAPPED)
        self.assertEqual(req.reference().constitutional_source, "ASTRA-010")
        self.assertEqual(req.reference().requirement_id, "AIR-CM-009")

    def test_invalid_coverage_state_is_rejected(self):
        with self.assertRaises(ValidationError):
            ConstitutionalRequirement(
                constitutional_source="ASTRA-010",
                requirement_id="AIR-CM-009",
                requirement_version="1.0.0",
                requirement_summary="Unknown constitutional compliance fails closed.",
                accountable_component="Governance Engine",
                coverage_state="covered",
            )

    def test_governance_decision_supports_fail_closed_outcome(self):
        decision = GovernanceDecision(
            decision_id="GOV-DEC-001",
            outcome=GovernanceOutcome.FAIL_CLOSED,
            requirement_references=(requirement().reference(),),
            safety_classification=SafetyClassification.UNKNOWN,
            authority_class=AuthorityClass.CONSTITUTIONAL,
            decision_reason_class=DecisionReasonClass.FAIL_CLOSED_DEFAULT,
            required_approval_state=ApprovalState.NOT_REQUIRED,
            evidence_references=("evd_fail_closed_001",),
            failure_posture=FailurePosture.FAIL_CLOSED,
            version_marker="1.0.0",
        )

        self.assertEqual(decision.outcome, GovernanceOutcome.FAIL_CLOSED)
        self.assertEqual(decision.failure_posture, FailurePosture.FAIL_CLOSED)

    def test_governance_allow_cannot_bypass_pending_approval(self):
        with self.assertRaises(ValidationError):
            GovernanceDecision(
                decision_id="GOV-DEC-002",
                outcome=GovernanceOutcome.ALLOW,
                requirement_references=(requirement().reference(),),
                safety_classification=SafetyClassification.PRIVATE_WRITE,
                authority_class=AuthorityClass.APPROVAL_REQUIRED,
                decision_reason_class=DecisionReasonClass.EXECUTION_AUTHORITY_BOUNDARY,
                required_approval_state=ApprovalState.PENDING,
                failure_posture=FailurePosture.FAIL_CLOSED,
                version_marker="1.0.0",
            )

    def test_missing_requirement_reference_is_rejected_for_governance_decisions(self):
        with self.assertRaises(ValidationError):
            GovernanceDecision(
                decision_id="GOV-DEC-003",
                outcome=GovernanceOutcome.REFUSE,
                requirement_references=(),
                safety_classification=SafetyClassification.CONSTITUTIONAL,
                authority_class=AuthorityClass.CONSTITUTIONAL,
                decision_reason_class=DecisionReasonClass.CONSTITUTIONAL_PRECEDENCE,
                required_approval_state=ApprovalState.NOT_REQUIRED,
                failure_posture=FailurePosture.REFUSE,
                version_marker="1.0.0",
            )

    def test_bounded_evidence_accepts_metadata_only_review_evidence(self):
        evidence = BoundedEvidence(
            evidence_id="evd_contract_001",
            evidence_type=EvidenceType.CONTRACT_VALIDATION,
            requirement_references=(requirement().reference(),),
            actor_or_service_class=ActorOrServiceClass.CODEX,
            decision_or_operation_reference="ASTRA-IMP-001",
            timestamp=datetime(2026, 7, 26, tzinfo=timezone.utc),
            sensitivity_class=SensitivityClass.INTERNAL,
            minimization_class=MinimizationClass.METADATA_ONLY,
            retention_class=RetentionClass.GOVERNANCE_RECORD,
            integrity=integrity(),
            correction=EvidenceCorrectionMetadata(evidence_version="1.0.0"),
            redaction_status=RedactionStatus.NOT_REQUIRED,
        )

        self.assertEqual(evidence.evidence_type, EvidenceType.CONTRACT_VALIDATION)
        self.assertEqual(evidence.integrity.content_digest, "sha256:" + "a" * 64)

    def test_every_astra_010_safety_class_serializes_correctly(self):
        expected = {
            "public",
            "private_read",
            "private_write",
            "high_impact",
            "cross_owner",
            "external_exposure",
            "constitutional",
            "prohibited",
            "unknown",
        }

        self.assertEqual({item.value for item in SafetyClassification}, expected)

    def test_unknown_and_prohibited_safety_cannot_be_allowed(self):
        for safety_classification in (SafetyClassification.UNKNOWN, SafetyClassification.PROHIBITED):
            with self.subTest(safety_classification=safety_classification):
                with self.assertRaises(ValidationError):
                    GovernanceDecision(
                        decision_id="GOV-DEC-004",
                        outcome=GovernanceOutcome.ALLOW,
                        requirement_references=(requirement().reference(),),
                        safety_classification=safety_classification,
                        authority_class=AuthorityClass.CONSTITUTIONAL,
                        decision_reason_class=DecisionReasonClass.CONSTITUTIONAL_PRECEDENCE,
                        required_approval_state=ApprovalState.NOT_REQUIRED,
                        failure_posture=FailurePosture.FAIL_CLOSED,
                        version_marker="1.0.0",
                    )

    def test_high_impact_and_private_write_allow_require_explicit_approval(self):
        for safety_classification in (SafetyClassification.HIGH_IMPACT, SafetyClassification.PRIVATE_WRITE):
            with self.subTest(safety_classification=safety_classification):
                with self.assertRaises(ValidationError):
                    GovernanceDecision(
                        decision_id="GOV-DEC-005",
                        outcome=GovernanceOutcome.ALLOW,
                        requirement_references=(requirement().reference(),),
                        safety_classification=safety_classification,
                        authority_class=AuthorityClass.APPROVAL_REQUIRED,
                        decision_reason_class=DecisionReasonClass.EXECUTION_AUTHORITY_BOUNDARY,
                        required_approval_state=ApprovalState.NOT_REQUIRED,
                        failure_posture=FailurePosture.FAIL_CLOSED,
                        version_marker="1.0.0",
                    )

                approved = GovernanceDecision(
                    decision_id="GOV-DEC-006",
                    outcome=GovernanceOutcome.ALLOW,
                    requirement_references=(requirement().reference(),),
                    safety_classification=safety_classification,
                    authority_class=AuthorityClass.APPROVAL_REQUIRED,
                    decision_reason_class=DecisionReasonClass.EXECUTION_AUTHORITY_BOUNDARY,
                    required_approval_state=ApprovalState.APPROVED,
                    failure_posture=FailurePosture.FAIL_CLOSED,
                    version_marker="1.0.0",
                )
                self.assertEqual(approved.required_approval_state, ApprovalState.APPROVED)

    def test_evidence_rejects_secret_bearing_metadata_and_hidden_reasoning(self):
        with self.assertRaises(ValidationError):
            EvidenceIntegrityMetadata(
                source_system="astra_ai:contracts",
                provenance_reference="hidden_reasoning",
                content_digest="sha256:" + "a" * 64,
            )

        with self.assertRaises(ValidationError):
            EvidenceIntegrityMetadata(
                source_system="astra_ai:contracts",
                provenance_reference="token=abc123",
                content_digest="sha256:" + "a" * 64,
            )

    def test_restricted_evidence_requires_redaction_or_no_payload(self):
        with self.assertRaises(ValidationError):
            BoundedEvidence(
                evidence_id="evd_contract_002",
                evidence_type=EvidenceType.AUDIT_INTEGRITY,
                requirement_references=(requirement().reference(),),
                actor_or_service_class=ActorOrServiceClass.SYSTEM,
                decision_or_operation_reference="ASTRA-IMP-001",
                timestamp=datetime(2026, 7, 26, tzinfo=timezone.utc),
                sensitivity_class=SensitivityClass.RESTRICTED,
                minimization_class=MinimizationClass.METADATA_ONLY,
                retention_class=RetentionClass.GOVERNANCE_RECORD,
                integrity=integrity(),
                correction=EvidenceCorrectionMetadata(evidence_version="1.0.0"),
                redaction_status=RedactionStatus.NOT_REQUIRED,
            )

    def test_complete_non_destructive_correction_succeeds(self):
        correction = complete_correction()

        self.assertEqual(correction.supersedes_evidence_id, "evd_contract_001")
        self.assertEqual(correction.correcting_actor_or_service_class, ActorOrServiceClass.ASTRA_REVIEW)
        self.assertEqual(correction.retention_treatment, RetentionClass.GOVERNANCE_RECORD)
        self.assertEqual(correction.privacy_treatment, CorrectionPrivacyTreatment.METADATA_ONLY)

    def test_correction_without_authority_or_timestamp_fails(self):
        with self.assertRaises(ValidationError):
            EvidenceCorrectionMetadata(
                evidence_version="1.0.1",
                supersedes_evidence_id="evd_contract_001",
                correction_reason="Corrected bounded metadata reference.",
                correction_timestamp=datetime(2026, 7, 26, 12, 0, tzinfo=timezone.utc),
                replacement_reference="ASTRA-IMP-001:correction-001",
                retention_treatment=RetentionClass.GOVERNANCE_RECORD,
                privacy_treatment=CorrectionPrivacyTreatment.METADATA_ONLY,
            )

        with self.assertRaises(ValidationError):
            EvidenceCorrectionMetadata(
                evidence_version="1.0.1",
                supersedes_evidence_id="evd_contract_001",
                correction_reason="Corrected bounded metadata reference.",
                correcting_actor_or_service_class=ActorOrServiceClass.ASTRA_REVIEW,
                replacement_reference="ASTRA-IMP-001:correction-001",
                retention_treatment=RetentionClass.GOVERNANCE_RECORD,
                privacy_treatment=CorrectionPrivacyTreatment.METADATA_ONLY,
            )

    def test_correction_reason_without_superseded_evidence_id_fails(self):
        with self.assertRaises(ValidationError):
            EvidenceCorrectionMetadata(
                evidence_version="1.0.1",
                correction_reason="Corrected bounded metadata reference.",
            )

    def test_naive_correction_timestamp_fails(self):
        with self.assertRaises(ValidationError):
            EvidenceCorrectionMetadata(
                evidence_version="1.0.1",
                supersedes_evidence_id="evd_contract_001",
                correction_reason="Corrected bounded metadata reference.",
                correcting_actor_or_service_class=ActorOrServiceClass.ASTRA_REVIEW,
                correction_timestamp=datetime(2026, 7, 26, 12, 0),
                replacement_reference="ASTRA-IMP-001:correction-001",
                retention_treatment=RetentionClass.GOVERNANCE_RECORD,
                privacy_treatment=CorrectionPrivacyTreatment.METADATA_ONLY,
            )

    def test_secret_bearing_correction_metadata_fails(self):
        with self.assertRaises(ValidationError):
            EvidenceCorrectionMetadata(
                evidence_version="1.0.1",
                supersedes_evidence_id="evd_contract_001",
                correction_reason="Corrected bounded metadata reference.",
                correcting_actor_or_service_class=ActorOrServiceClass.ASTRA_REVIEW,
                correction_timestamp=datetime(2026, 7, 26, 12, 0, tzinfo=timezone.utc),
                replacement_reference="token=abc123",
                retention_treatment=RetentionClass.GOVERNANCE_RECORD,
                privacy_treatment=CorrectionPrivacyTreatment.METADATA_ONLY,
            )

    def test_configuration_is_disabled_by_default_and_fail_closed(self):
        config = AstraConfigurationContract(
            configuration_id="ASTRA-CONFIG-001",
            environment_scope=EnvironmentScope.QA,
            configuration_version="1.0.0",
        )

        self.assertFalse(ASTRA_AI_PLATFORM_ENABLED)
        self.assertFalse(config.feature_enabled)
        self.assertEqual(config.provider_use, RuntimeUseState.DISABLED)
        self.assertEqual(config.memory_use, RuntimeUseState.DISABLED)
        self.assertEqual(config.adaptation_use, RuntimeUseState.DISABLED)
        self.assertEqual(config.execution_handoff, RuntimeUseState.DISABLED)
        self.assertEqual(config.audit_evidence_behavior, AuditEvidenceBehavior.METADATA_ONLY)
        self.assertTrue(config.fail_closed_default)
        self.assertEqual(config.production_authorization_state, ProductionAuthorizationState.NOT_APPROVED)

    def test_configuration_rejects_runtime_or_production_authorization_inference(self):
        with self.assertRaises(ValidationError):
            AstraConfigurationContract(
                configuration_id="ASTRA-CONFIG-002",
                feature_enabled=True,
                environment_scope=EnvironmentScope.QA,
                configuration_version="1.0.0",
            )

        with self.assertRaises(ValidationError):
            AstraConfigurationContract(
                configuration_id="ASTRA-CONFIG-003",
                environment_scope=EnvironmentScope.PRODUCTION,
                production_authorization_state=ProductionAuthorizationState.APPROVED,
                configuration_version="1.0.0",
            )

        with self.assertRaises(ValidationError):
            AstraConfigurationContract(
                configuration_id="ASTRA-CONFIG-004",
                environment_scope=EnvironmentScope.QA,
                fail_closed_default=False,
                configuration_version="1.0.0",
            )

    def test_malformed_versions_and_identifiers_are_rejected(self):
        with self.assertRaises(ValidationError):
            requirement(requirement_id="AIR-9")

        with self.assertRaises(ValidationError):
            AstraConfigurationContract(
                configuration_id="bad config",
                environment_scope=EnvironmentScope.QA,
                configuration_version="1",
            )

    def test_canonical_serialization_is_stable(self):
        config = AstraConfigurationContract(
            configuration_id="ASTRA-CONFIG-001",
            environment_scope=EnvironmentScope.QA,
            configuration_version="1.0.0",
        )

        first = canonical_contract_json(config)
        second = canonical_contract_json(config)

        self.assertEqual(first, second)
        self.assertIn('"feature_enabled":false', first)
        self.assertLess(first.index('"configuration_id"'), first.index('"configuration_version"'))

    def test_canonical_serialization_preserves_correction_provenance(self):
        correction = complete_correction()

        payload = canonical_contract_json(correction)

        self.assertIn('"correcting_actor_or_service_class":"astra_review"', payload)
        self.assertIn('"correction_timestamp":"2026-07-26T12:00:00Z"', payload)
        self.assertIn('"replacement_reference":"ASTRA-IMP-001:correction-001"', payload)
        self.assertIn('"supersedes_evidence_id":"evd_contract_001"', payload)

    def test_extra_fields_cannot_expand_contract_authority(self):
        with self.assertRaises(ValidationError):
            AstraConfigurationContract(
                configuration_id="ASTRA-CONFIG-005",
                environment_scope=EnvironmentScope.QA,
                configuration_version="1.0.0",
                provider_model="gpt-x",
            )


if __name__ == "__main__":
    unittest.main()
