from __future__ import annotations

from copy import deepcopy

from pydantic import ValidationError

from app.modules.astra_ai.configuration import get_astra_configuration
from app.modules.astra_ai.constitutional_contracts import (
    AuditEvidenceBehavior,
    BoundedEvidence,
    ContractValidationError,
    ProductionAuthorizationState,
    assert_no_prohibited_contract_material,
)


DEFAULT_EVIDENCE_SINK_CAPACITY = 100


class AstraEvidenceSinkError(ValueError):
    """Raised when bounded evidence cannot be received by the minimal sink."""


class InMemoryEvidenceSink:
    """Bounded in-memory receiver for certified Astra evidence.

    The sink receives evidence only. It does not decide, authorize, persist,
    emit events, call audit storage, or expose a runtime integration surface.
    """

    def __init__(self, *, capacity: int = DEFAULT_EVIDENCE_SINK_CAPACITY) -> None:
        if capacity < 1:
            raise AstraEvidenceSinkError("Evidence sink capacity must be at least one.")
        self._configuration = get_astra_configuration()
        self._validate_configuration_boundary()
        self._capacity = capacity
        self._records: list[BoundedEvidence] = []
        self._evidence_ids: set[str] = set()

    @property
    def capacity(self) -> int:
        return self._capacity

    def append(self, evidence: BoundedEvidence) -> BoundedEvidence:
        normalized = self._validate_evidence(evidence)
        if normalized.evidence_id in self._evidence_ids:
            raise AstraEvidenceSinkError("Evidence sink rejects duplicate evidence identifiers.")
        if len(self._records) >= self._capacity:
            raise AstraEvidenceSinkError("Evidence sink capacity exceeded.")
        self._validate_correction_chain(normalized)

        self._records.append(normalized)
        self._evidence_ids.add(normalized.evidence_id)
        return deepcopy(normalized)

    def retrieve(self) -> tuple[BoundedEvidence, ...]:
        return tuple(deepcopy(self._records))

    def count(self) -> int:
        return len(self._records)

    def _validate_configuration_boundary(self) -> None:
        configuration = self._configuration.configuration
        if not configuration.fail_closed_default:
            raise AstraEvidenceSinkError("Evidence sink requires fail-closed configuration.")
        if configuration.feature_enabled:
            raise AstraEvidenceSinkError("Evidence sink cannot run with enabled Astra runtime configuration.")
        if configuration.production_authorization_state is ProductionAuthorizationState.APPROVED:
            raise AstraEvidenceSinkError("Evidence sink cannot receive production-authorized configuration.")
        if configuration.audit_evidence_behavior is not AuditEvidenceBehavior.METADATA_ONLY:
            raise AstraEvidenceSinkError("Evidence sink requires metadata-only audit evidence behavior.")

    def _validate_evidence(self, evidence: BoundedEvidence) -> BoundedEvidence:
        try:
            assert_no_prohibited_contract_material(evidence)
        except ContractValidationError as exc:
            raise AstraEvidenceSinkError("Evidence sink rejected prohibited evidence material.") from exc
        if not isinstance(evidence, BoundedEvidence):
            raise AstraEvidenceSinkError("Evidence sink accepts only certified BoundedEvidence objects.")
        try:
            normalized = BoundedEvidence.model_validate(evidence.model_dump(mode="json"))
        except (ContractValidationError, ValidationError, ValueError) as exc:
            raise AstraEvidenceSinkError("Evidence sink rejected malformed evidence.") from exc
        assert_no_prohibited_contract_material(normalized.model_dump(mode="json"))
        return normalized

    def _validate_correction_chain(self, evidence: BoundedEvidence) -> None:
        superseded_id = evidence.correction.supersedes_evidence_id
        if superseded_id is None:
            return
        if evidence.evidence_id == superseded_id:
            raise AstraEvidenceSinkError("Evidence correction cannot supersede itself.")
        if superseded_id not in self._evidence_ids:
            raise AstraEvidenceSinkError("Evidence correction must reference an existing stored record.")
        if self._creates_correction_cycle(evidence.evidence_id, superseded_id):
            raise AstraEvidenceSinkError("Evidence correction cannot create a correction cycle.")

    def _creates_correction_cycle(self, evidence_id: str, superseded_id: str) -> bool:
        current_id = superseded_id
        visited: set[str] = set()
        while current_id is not None:
            if current_id == evidence_id:
                return True
            if current_id in visited:
                return True
            visited.add(current_id)
            current = self._record_by_id(current_id)
            if current is None:
                return False
            current_id = current.correction.supersedes_evidence_id
        return False

    def _record_by_id(self, evidence_id: str) -> BoundedEvidence | None:
        for record in self._records:
            if record.evidence_id == evidence_id:
                return record
        return None
