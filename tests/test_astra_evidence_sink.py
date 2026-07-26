from __future__ import annotations

import inspect
import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from app.modules.astra_ai.configuration import ASTRA_CONFIGURATION_ID, ASTRA_CONFIGURATION_VERSION, get_astra_configuration
from app.modules.astra_ai.constitutional_contracts import (
    ActorOrServiceClass,
    ApprovalState,
    AuthorityClass,
    BoundedEvidence,
    ConstitutionalRequirementReference,
    CorrectionPrivacyTreatment,
    EvidenceCorrectionMetadata,
    EvidenceIntegrityMetadata,
    EvidenceType,
    MinimizationClass,
    ProductionAuthorizationState,
    RedactionStatus,
    RetentionClass,
    SafetyClassification,
    SensitivityClass,
)
from app.modules.astra_ai import evidence_sink
from app.modules.astra_ai.evidence_sink import AstraEvidenceSinkError, InMemoryEvidenceSink
from app.modules.astra_ai.governance import GovernanceEvaluationInput, evaluate_governance


TIMESTAMP = datetime(2026, 7, 26, 12, 0, tzinfo=timezone.utc)


def requirement():
    return ConstitutionalRequirementReference(
        constitutional_source="ASTRA-010",
        requirement_id="AIR-EV-004",
        requirement_version="1.0.0",
    )


def governance_input(evaluation_id="GOV-EVAL-001"):
    return GovernanceEvaluationInput(
        evaluation_id=evaluation_id,
        requirement_references=(requirement(),),
        requested_authority_class=AuthorityClass.READ_ONLY,
        safety_classification=SafetyClassification.PUBLIC,
        approval_state=ApprovalState.NOT_REQUIRED,
        configuration_id=ASTRA_CONFIGURATION_ID,
        configuration_version=ASTRA_CONFIGURATION_VERSION,
        production_authorization_state=ProductionAuthorizationState.NOT_APPROVED,
        evaluation_timestamp=TIMESTAMP,
    )


def governance_evidence(evaluation_id="GOV-EVAL-001"):
    return evaluate_governance(governance_input(evaluation_id)).evidence


def correction_evidence():
    return BoundedEvidence(
        evidence_id="evd_correction_0001",
        evidence_type=EvidenceType.AUDIT_INTEGRITY,
        requirement_references=(requirement(),),
        actor_or_service_class=ActorOrServiceClass.ASTRA_REVIEW,
        decision_or_operation_reference="GOV-EVAL-002",
        timestamp=TIMESTAMP,
        sensitivity_class=SensitivityClass.INTERNAL,
        minimization_class=MinimizationClass.METADATA_ONLY,
        retention_class=RetentionClass.GOVERNANCE_RECORD,
        integrity=EvidenceIntegrityMetadata(
            source_system="astra_ai:evidence_sink",
            provenance_reference="correction:review:0001",
            content_digest="sha256:" + "a" * 64,
        ),
        correction=EvidenceCorrectionMetadata(
            evidence_version="1.0.0",
            supersedes_evidence_id=governance_evidence("GOV-EVAL-002").evidence_id,
            correction_reason="Corrected bounded governance evidence reference.",
            correcting_actor_or_service_class=ActorOrServiceClass.ASTRA_REVIEW,
            correction_timestamp=TIMESTAMP,
            replacement_reference="correction:replacement:0001",
            retention_treatment=RetentionClass.GOVERNANCE_RECORD,
            privacy_treatment=CorrectionPrivacyTreatment.METADATA_ONLY,
        ),
        redaction_status=RedactionStatus.NOT_REQUIRED,
    )


class AstraEvidenceSinkTests(unittest.TestCase):
    def test_append_success_returns_copy_and_tracks_count(self):
        sink = InMemoryEvidenceSink(capacity=2)
        evidence = governance_evidence()

        returned = sink.append(evidence)

        self.assertEqual(returned, evidence)
        self.assertIsNot(returned, evidence)
        self.assertEqual(sink.count(), 1)

    def test_retrieval_preserves_deterministic_insertion_order(self):
        sink = InMemoryEvidenceSink(capacity=3)
        first = governance_evidence("GOV-EVAL-001")
        second = governance_evidence("GOV-EVAL-002")

        sink.append(first)
        sink.append(second)

        self.assertEqual(tuple(item.evidence_id for item in sink.retrieve()), (first.evidence_id, second.evidence_id))

    def test_duplicate_evidence_identifier_is_rejected(self):
        sink = InMemoryEvidenceSink(capacity=2)
        evidence = governance_evidence()
        sink.append(evidence)

        with self.assertRaises(AstraEvidenceSinkError):
            sink.append(evidence)

    def test_malformed_evidence_is_rejected(self):
        sink = InMemoryEvidenceSink()

        with self.assertRaises(AstraEvidenceSinkError):
            sink.append({"evidence_id": "evd_not_certified"})  # type: ignore[arg-type]

    def test_secret_bearing_evidence_input_is_rejected(self):
        sink = InMemoryEvidenceSink()

        with self.assertRaises(AstraEvidenceSinkError):
            sink.append({"evidence_id": "evd_secret", "metadata": "api_key:abc123"})  # type: ignore[arg-type]

    def test_capacity_is_bounded_and_does_not_discard(self):
        sink = InMemoryEvidenceSink(capacity=1)
        first = governance_evidence("GOV-EVAL-001")
        second = governance_evidence("GOV-EVAL-002")
        sink.append(first)

        with self.assertRaises(AstraEvidenceSinkError):
            sink.append(second)

        self.assertEqual(sink.retrieve(), (first,))

    def test_retrieval_is_immutable_copy_safe(self):
        sink = InMemoryEvidenceSink()
        original = governance_evidence()
        sink.append(original)

        retrieved = sink.retrieve()
        retrieved[0].decision_or_operation_reference = "MUTATED-001"

        self.assertEqual(sink.retrieve()[0].decision_or_operation_reference, original.decision_or_operation_reference)

    def test_correction_chain_is_preserved(self):
        sink = InMemoryEvidenceSink()
        evidence = correction_evidence()

        sink.append(evidence)
        stored = sink.retrieve()[0]

        self.assertEqual(stored.correction.supersedes_evidence_id, governance_evidence("GOV-EVAL-002").evidence_id)
        self.assertEqual(stored.correction.correction_reason, "Corrected bounded governance evidence reference.")
        self.assertEqual(stored.correction.correcting_actor_or_service_class, ActorOrServiceClass.ASTRA_REVIEW)

    def test_clear_for_test_removes_in_memory_records_only(self):
        sink = InMemoryEvidenceSink()
        sink.append(governance_evidence())

        sink.clear_for_test()

        self.assertEqual(sink.count(), 0)
        self.assertEqual(sink.retrieve(), ())

    def test_no_persistent_audit_database_or_route_side_effects(self):
        sink = InMemoryEvidenceSink()
        with patch("app.modules.audit.service.write_audit_log") as write_audit_log:
            sink.append(governance_evidence())

        write_audit_log.assert_not_called()
        source = inspect.getsource(evidence_sink)
        self.assertNotIn("sqlalchemy", source)
        self.assertNotIn("fastapi", source)
        self.assertNotIn("app.modules.audit", source)
        self.assertNotIn("write_audit_log", source)

    def test_configuration_remains_disabled_and_collection_does_not_authorize_runtime(self):
        sink = InMemoryEvidenceSink()
        sink.append(governance_evidence())
        configuration = get_astra_configuration().configuration

        self.assertFalse(configuration.feature_enabled)
        self.assertEqual(configuration.production_authorization_state, ProductionAuthorizationState.NOT_APPROVED)


if __name__ == "__main__":
    unittest.main()
