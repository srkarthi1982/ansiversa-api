from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Callable, Mapping
from datetime import datetime, timedelta, timezone
from enum import StrEnum
from types import MappingProxyType
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlalchemy.orm import Session

from app.modules.astra_ai.constitutional_contracts import (
    ActorOrServiceClass,
    BoundedEvidence,
    ConstitutionalRequirementReference,
    EvidenceCorrectionMetadata,
    EvidenceIntegrityMetadata,
    EvidenceType,
    MinimizationClass,
    RedactionStatus,
    RetentionClass,
    SensitivityClass,
)
from app.modules.astra_ai.read_access_authorization import (
    AstraReadAuthorizationDecision,
    AstraReadDecisionStatus,
)
from app.modules.subscription_manager import astra_read_capabilities as subscription_reads
from app.modules.subscription_manager.astra_read_capabilities import (
    APP_ID as SUBSCRIPTION_MANAGER_APP_ID,
    APP_SCOPE as SUBSCRIPTION_MANAGER_APP_SCOPE,
    CAPABILITY_VERSION as SUBSCRIPTION_MANAGER_CAPABILITY_VERSION,
    SubscriptionAstraCapabilityError,
    SubscriptionAstraReadGrant,
    SubscriptionAstraReadResult,
)


READ_EXECUTION_VERSION = "1.0.0"
READ_EXECUTION_IMPLEMENTATION_REFERENCE = "ASTRA-READ-EXEC-001"
READ_EXECUTION_REQUEST_TTL_SECONDS = 300
READ_OPERATION = "read"

_REFERENCE_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9:._/-]{2,180}$"
_RUNTIME_ID_PATTERN = r"^astra_rt_[a-f0-9]{32}$"
_REQUEST_ID_PATTERN = r"^read_exec_req_[a-z0-9][a-z0-9_-]{7,120}$"
_EXECUTION_RESULT_ID_PATTERN = r"^read_exec_result_[a-f0-9]{24}$"
_APP_ID_PATTERN = r"^[a-z][a-z0-9_.-]{2,80}$"
_VERSION_PATTERN = r"^\d+\.\d+\.\d+$"
_SUBSCRIPTION_CAPABILITY_PATTERN = r"^subscription\.[a-z][a-z0-9_]{2,80}$"

_PROHIBITED_KEYS = {
    "api_key",
    "apikey",
    "authorization_header",
    "authority_material",
    "bearer",
    "callback",
    "connection",
    "cookie",
    "credential",
    "handler",
    "password",
    "private_key",
    "provider_payload",
    "raw_input",
    "raw_prompt",
    "runtime_handle",
    "secret",
    "session",
    "sql",
    "stacktrace",
    "token",
    "traceback",
}
_PROHIBITED_VALUE_PATTERNS = (
    re.compile(r"authorization\s*:\s*bearer\s+\S+", re.IGNORECASE),
    re.compile(r"(api[_-]?key|token|password|secret|credential)\s*[:=]", re.IGNORECASE),
    re.compile(r"(postgres(?:ql)?|mysql|libsql)://", re.IGNORECASE),
    re.compile(r"\b(select|insert|update|delete|drop|alter)\s+.+\b(from|into|table|where)\b", re.IGNORECASE),
    re.compile(r"\bapp\.modules\.[A-Za-z0-9_.]+", re.IGNORECASE),
    re.compile(r"\b/Users/[^ \t\r\n]+", re.IGNORECASE),
    re.compile(r"\btraceback\b", re.IGNORECASE),
    re.compile(r"\b(provider[_ -]?payload|raw[_ -]?prompt|hidden[_ -]?reasoning)\b", re.IGNORECASE),
)


class AstraReadExecutionError(ValueError):
    """Raised when governed read execution cannot satisfy the certified boundary."""


class AstraReadExecutionStatus(StrEnum):
    OK = "ok"
    EMPTY = "empty"


class AstraReadExecutionRequest(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid", frozen=True)

    execution_request_id: str = Field(pattern=_REQUEST_ID_PATTERN)
    runtime_instance_id: str = Field(pattern=_RUNTIME_ID_PATTERN)
    authorization_decision_id: str = Field(min_length=8, max_length=160)
    read_capability_id: str = Field(min_length=8, max_length=160)
    owning_app_id: str = Field(pattern=_APP_ID_PATTERN)
    adapter_capability_id: str = Field(pattern=_SUBSCRIPTION_CAPABILITY_PATTERN)
    adapter_capability_version: str = Field(pattern=_VERSION_PATTERN)
    operation: str = Field(pattern=r"^read$")
    authenticated_principal_reference: str = Field(pattern=_REFERENCE_PATTERN)
    request_reference: str = Field(pattern=_REFERENCE_PATTERN)
    execution_context_reference: str = Field(pattern=_REFERENCE_PATTERN)
    requested_maximum_result_count: int = Field(ge=1, le=50)
    requested_at: datetime
    expires_at: datetime
    read_authorization_decision: AstraReadAuthorizationDecision = Field(exclude=True)
    app_read_grant: Any = Field(exclude=True)
    authority_token: Any = Field(exclude=True)
    version: str = Field(default=READ_EXECUTION_VERSION, pattern=_VERSION_PATTERN)

    @model_validator(mode="after")
    def validate_request(self) -> "AstraReadExecutionRequest":
        _ensure_aware(self.requested_at, "Read execution request")
        _ensure_aware(self.expires_at, "Read execution expiration")
        if self.expires_at <= self.requested_at:
            raise AstraReadExecutionError("Read execution request expiration must follow issuance.")
        _validate_no_prohibited_payload(self.model_dump(mode="json"))
        return self


class AstraReadExecutionResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    execution_result_id: str = Field(pattern=_EXECUTION_RESULT_ID_PATTERN)
    execution_request_id: str = Field(pattern=_REQUEST_ID_PATTERN)
    runtime_instance_id: str = Field(pattern=_RUNTIME_ID_PATTERN)
    authorization_decision_id: str = Field(min_length=8, max_length=160)
    read_capability_id: str = Field(min_length=8, max_length=160)
    owning_app_id: str = Field(pattern=_APP_ID_PATTERN)
    adapter_capability_id: str = Field(pattern=_SUBSCRIPTION_CAPABILITY_PATTERN)
    adapter_capability_version: str = Field(pattern=_VERSION_PATTERN)
    operation: str = Field(pattern=r"^read$")
    status: AstraReadExecutionStatus
    result_kind: str = Field(min_length=2, max_length=80)
    records: tuple[dict[str, Any], ...] = Field(default_factory=tuple, max_length=50)
    summary: dict[str, Any] = Field(default_factory=dict)
    record_count: int = Field(ge=0)
    returned_count: int = Field(ge=0, le=50)
    truncated: bool
    reason_codes: tuple[str, ...] = Field(min_length=1, max_length=20)
    redaction_posture: str = Field(default="strict", pattern=r"^strict$")
    user_scope_state: str = Field(default="authenticated_user_only", pattern=r"^authenticated_user_only$")
    authorization_state: str = Field(default="authorized_metadata_only", pattern=r"^authorized_metadata_only$")
    production_authorization_state: str = Field(default="not_approved", pattern=r"^not_approved$")
    data_mutation_state: str = Field(default="prohibited", pattern=r"^prohibited$")
    schema_mutation_state: str = Field(default="prohibited", pattern=r"^prohibited$")
    evidence_references: tuple[str, ...] = Field(default_factory=tuple, max_length=10)
    observed_at: datetime
    version: str = Field(default=READ_EXECUTION_VERSION, pattern=_VERSION_PATTERN)

    @model_validator(mode="after")
    def validate_result(self) -> "AstraReadExecutionResult":
        _ensure_aware(self.observed_at, "Read execution result")
        if self.returned_count != len(self.records):
            raise AstraReadExecutionError("Read execution returned count does not match returned records.")
        if self.returned_count > self.record_count:
            raise AstraReadExecutionError("Read execution returned count exceeds record count.")
        _validate_no_prohibited_payload(self.model_dump(mode="json"))
        return self


class AstraReadAdapterDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    owning_app_id: str = Field(pattern=_APP_ID_PATTERN)
    adapter_capability_id: str = Field(pattern=_SUBSCRIPTION_CAPABILITY_PATTERN)
    adapter_capability_version: str = Field(pattern=_VERSION_PATTERN)
    operation: str = Field(pattern=r"^read$")
    implementation_reference: str = Field(pattern=r"^ASTRA-READ-EXEC-001$")


class AstraReadAdapterInvocationContext(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid", frozen=True)

    request: AstraReadExecutionRequest
    db: Session = Field(exclude=True)
    authenticated_user: Any = Field(exclude=True)
    app_read_grant: Any = Field(exclude=True)


ReadAdapter = Callable[[AstraReadAdapterInvocationContext], Any]


class AstraReadAdapterRegistry:
    def __init__(self, adapters: tuple[tuple[AstraReadAdapterDefinition, ReadAdapter], ...]) -> None:
        items: dict[tuple[str, str, str, str], tuple[AstraReadAdapterDefinition, ReadAdapter]] = {}
        for definition, adapter in adapters:
            if definition.owning_app_id != SUBSCRIPTION_MANAGER_APP_ID:
                raise AstraReadExecutionError("Only certified Subscription Manager read adapters are authorized.")
            if not callable(adapter):
                raise AstraReadExecutionError("Read adapter must be callable.")
            key = _adapter_key(definition)
            if key in items:
                raise AstraReadExecutionError("Duplicate read adapter registration is prohibited.")
            items[key] = (definition, adapter)
        self._items: Mapping[tuple[str, str, str, str], tuple[AstraReadAdapterDefinition, ReadAdapter]] = (
            MappingProxyType(items)
        )

    @property
    def adapter_keys(self) -> tuple[tuple[str, str, str, str], ...]:
        return tuple(sorted(self._items))

    def get(
        self,
        *,
        owning_app_id: str,
        adapter_capability_id: str,
        adapter_capability_version: str,
        operation: str,
    ) -> tuple[AstraReadAdapterDefinition, ReadAdapter]:
        try:
            return self._items[(owning_app_id, adapter_capability_id, adapter_capability_version, operation)]
        except KeyError as exc:
            raise AstraReadExecutionError("Requested read adapter is not registered.") from exc


class AstraReadExecutionBridge:
    def __init__(
        self,
        *,
        runtime: Any,
        registration_authority: object,
        request_authority: object,
        registry: AstraReadAdapterRegistry | None = None,
    ) -> None:
        self._runtime = runtime
        self._runtime_instance_id = runtime.identity.startup_instance_id
        self._registration_authority = registration_authority
        self._request_authority = request_authority
        self._registry = registry or default_read_adapter_registry()
        self._authorization_decisions: dict[str, AstraReadAuthorizationDecision] = {}
        self._requests: dict[str, AstraReadExecutionRequest] = {}
        self._consumed_requests: set[str] = set()

    @property
    def registry(self) -> AstraReadAdapterRegistry:
        return self._registry

    def register_read_authorization_decision(
        self,
        decision: AstraReadAuthorizationDecision,
        *,
        registration_authority: object,
    ) -> None:
        self._require_ready()
        if registration_authority is not self._registration_authority:
            raise AstraReadExecutionError("Read authorization registration requires Runtime authority.")
        self._validate_authorized_decision(decision)
        self._authorization_decisions[decision.authorization_decision_id] = decision

    def issue_request(
        self,
        *,
        execution_request_id: str,
        read_authorization_decision: AstraReadAuthorizationDecision,
        app_read_grant: Any,
        authenticated_principal_reference: str,
        request_reference: str,
        requested_maximum_result_count: int,
        requested_at: datetime,
        adapter_capability_id: str,
        adapter_capability_version: str,
    ) -> AstraReadExecutionRequest:
        self._require_ready()
        _ensure_aware(requested_at, "Read execution request")
        self._validate_registered_authorization(read_authorization_decision)
        self._validate_grant_contract(
            decision=read_authorization_decision,
            grant=app_read_grant,
            authenticated_principal_reference=authenticated_principal_reference,
            request_reference=request_reference,
            requested_maximum_result_count=requested_maximum_result_count,
            adapter_capability_id=adapter_capability_id,
            adapter_capability_version=adapter_capability_version,
            observed_at=requested_at,
        )
        self._registry.get(
            owning_app_id=read_authorization_decision.owning_app_id,
            adapter_capability_id=adapter_capability_id,
            adapter_capability_version=adapter_capability_version,
            operation=READ_OPERATION,
        )
        request = AstraReadExecutionRequest(
            execution_request_id=execution_request_id,
            runtime_instance_id=self._runtime_instance_id,
            authorization_decision_id=read_authorization_decision.authorization_decision_id,
            read_capability_id=read_authorization_decision.read_capability_id,
            owning_app_id=read_authorization_decision.owning_app_id,
            adapter_capability_id=adapter_capability_id,
            adapter_capability_version=adapter_capability_version,
            operation=READ_OPERATION,
            authenticated_principal_reference=authenticated_principal_reference,
            request_reference=request_reference,
            execution_context_reference=_execution_context_reference(read_authorization_decision, app_read_grant),
            requested_maximum_result_count=requested_maximum_result_count,
            requested_at=requested_at,
            expires_at=min(app_read_grant.expires_at, requested_at + timedelta(seconds=READ_EXECUTION_REQUEST_TTL_SECONDS)),
            read_authorization_decision=read_authorization_decision,
            app_read_grant=app_read_grant,
            authority_token=self._request_authority,
        )
        if request.execution_request_id in self._requests:
            raise AstraReadExecutionError("Duplicate read execution request identifier is prohibited.")
        self._requests[request.execution_request_id] = request
        return request

    def execute(self, request: AstraReadExecutionRequest, *, db: Session, authenticated_user: Any) -> AstraReadExecutionResult:
        self._require_ready()
        observed_at = _utc_now()
        self._validate_request_authority(request, observed_at=observed_at)
        decision = request.read_authorization_decision
        grant = request.app_read_grant
        self._validate_registered_authorization(decision)
        self._validate_grant_contract(
            decision=decision,
            grant=grant,
            authenticated_principal_reference=request.authenticated_principal_reference,
            request_reference=request.request_reference,
            requested_maximum_result_count=request.requested_maximum_result_count,
            adapter_capability_id=request.adapter_capability_id,
            adapter_capability_version=request.adapter_capability_version,
            observed_at=observed_at,
        )
        if getattr(authenticated_user, "id", None) != grant.authenticated_user_id:
            raise AstraReadExecutionError("Read execution authenticated subject does not match the authorized grant.")
        definition, adapter = self._registry.get(
            owning_app_id=request.owning_app_id,
            adapter_capability_id=request.adapter_capability_id,
            adapter_capability_version=request.adapter_capability_version,
            operation=request.operation,
        )
        context = AstraReadAdapterInvocationContext(
            request=request,
            db=db,
            authenticated_user=authenticated_user,
            app_read_grant=grant,
        )
        try:
            app_result = adapter(context)
        except SubscriptionAstraCapabilityError:
            self._record_failure(request, observed_at=observed_at)
            raise AstraReadExecutionError("App-owned read adapter rejected the governed request.") from None
        except Exception:
            self._record_failure(request, observed_at=observed_at)
            raise AstraReadExecutionError("App-owned read adapter failed closed.") from None
        if not isinstance(app_result, SubscriptionAstraReadResult):
            self._record_failure(request, observed_at=observed_at)
            raise AstraReadExecutionError("App-owned read adapter returned an invalid contract.")
        result = self._result_from_app_result(request, definition, app_result, observed_at=observed_at)
        self._requests.pop(request.execution_request_id, None)
        self._consumed_requests.add(request.execution_request_id)
        return result

    def _validate_request_authority(self, request: Any, *, observed_at: datetime) -> None:
        if not isinstance(request, AstraReadExecutionRequest):
            raise AstraReadExecutionError("Read execution requires a Runtime-issued request.")
        if request.authority_token is not self._request_authority:
            raise AstraReadExecutionError("Read execution requires Runtime request authority.")
        if self._requests.get(request.execution_request_id) is not request:
            raise AstraReadExecutionError("Read execution requires the exact Runtime-issued request.")
        if request.execution_request_id in self._consumed_requests:
            raise AstraReadExecutionError("Read execution request was already consumed.")
        if request.runtime_instance_id != self._runtime_instance_id:
            raise AstraReadExecutionError("Read execution request belongs to a different Runtime.")
        if request.expires_at <= observed_at:
            raise AstraReadExecutionError("Read execution request is expired.")
        if request.operation != READ_OPERATION:
            raise AstraReadExecutionError("Only read operations are authorized.")
        if request.execution_context_reference != _execution_context_reference(
            request.read_authorization_decision,
            request.app_read_grant,
        ):
            raise AstraReadExecutionError("Read execution context does not match the authorized grant.")

    def _validate_registered_authorization(self, decision: Any) -> None:
        self._validate_authorized_decision(decision)
        if self._authorization_decisions.get(decision.authorization_decision_id) is not decision:
            raise AstraReadExecutionError("Read execution requires exact Runtime-registered read authorization.")

    def _validate_authorized_decision(self, decision: Any) -> None:
        if not isinstance(decision, AstraReadAuthorizationDecision):
            raise AstraReadExecutionError("Read execution requires certified read authorization.")
        if decision.decision_status is not AstraReadDecisionStatus.AUTHORIZED_METADATA_ONLY:
            raise AstraReadExecutionError("Read execution requires authorized metadata-only status.")
        if decision.production_read_state != "not_approved":
            raise AstraReadExecutionError("Production read execution is not approved.")
        if decision.database_connection_state != "not_authorized":
            raise AstraReadExecutionError("Astra-owned database access is not authorized.")
        if decision.sql_execution_state != "not_authorized":
            raise AstraReadExecutionError("Astra-owned SQL execution is not authorized.")
        if decision.data_mutation_state != "prohibited" or decision.schema_mutation_state != "prohibited":
            raise AstraReadExecutionError("Read execution cannot authorize mutation.")
        if decision.owning_app_id != SUBSCRIPTION_MANAGER_APP_ID:
            raise AstraReadExecutionError("Only Subscription Manager read execution is authorized.")

    def _validate_grant_contract(
        self,
        *,
        decision: AstraReadAuthorizationDecision,
        grant: Any,
        authenticated_principal_reference: str,
        request_reference: str,
        requested_maximum_result_count: int,
        adapter_capability_id: str,
        adapter_capability_version: str,
        observed_at: datetime,
    ) -> None:
        if not isinstance(grant, SubscriptionAstraReadGrant):
            raise AstraReadExecutionError("Read execution requires an app-owned read grant.")
        if grant.app_scope != SUBSCRIPTION_MANAGER_APP_SCOPE:
            raise AstraReadExecutionError("Read execution grant app scope is unsupported.")
        if grant.capability_id != adapter_capability_id or grant.capability_version != adapter_capability_version:
            raise AstraReadExecutionError("Read execution grant does not match the requested adapter capability.")
        if adapter_capability_version != SUBSCRIPTION_MANAGER_CAPABILITY_VERSION:
            raise AstraReadExecutionError("Read execution adapter version is unsupported.")
        if grant.astra_authorization_reference.authorization_id != decision.authorization_decision_id:
            raise AstraReadExecutionError("Read execution grant does not match the read authorization decision.")
        if grant.astra_authorization_reference.decision_status != decision.decision_status.value:
            raise AstraReadExecutionError("Read execution grant authorization status does not match.")
        if grant.astra_authorization_reference.authenticated_principal_reference != authenticated_principal_reference:
            raise AstraReadExecutionError("Read execution principal does not match the authorized grant.")
        if grant.request_reference != request_reference:
            raise AstraReadExecutionError("Read execution request reference does not match the authorized grant.")
        if grant.maximum_result_count != requested_maximum_result_count:
            raise AstraReadExecutionError("Read execution result limit does not match the authorized grant.")
        if grant.expires_at <= observed_at:
            raise AstraReadExecutionError("Read execution grant is expired.")
        if observed_at < grant.issued_at or observed_at < grant.observed_at:
            raise AstraReadExecutionError("Read execution request predates the authorized grant.")
        if grant.production_authorization_state != "not_approved":
            raise AstraReadExecutionError("Production read execution is not approved.")
        if grant.astra_authorization_reference.production_authorization_state != "not_approved":
            raise AstraReadExecutionError("Production read execution is not approved.")

    def _result_from_app_result(
        self,
        request: AstraReadExecutionRequest,
        definition: AstraReadAdapterDefinition,
        app_result: SubscriptionAstraReadResult,
        *,
        observed_at: datetime,
    ) -> AstraReadExecutionResult:
        if app_result.capability_id != definition.adapter_capability_id:
            raise AstraReadExecutionError("App-owned read result capability mismatch.")
        if app_result.capability_version != definition.adapter_capability_version:
            raise AstraReadExecutionError("App-owned read result version mismatch.")
        if app_result.app_scope != SUBSCRIPTION_MANAGER_APP_SCOPE:
            raise AstraReadExecutionError("App-owned read result scope mismatch.")
        if app_result.authorization_state != "authorized_metadata_only":
            raise AstraReadExecutionError("App-owned read result authorization mismatch.")
        if app_result.production_authorization_state != "not_approved":
            raise AstraReadExecutionError("Production read execution is not approved.")
        if app_result.user_scope_state != "authenticated_user_only":
            raise AstraReadExecutionError("App-owned read result user scope mismatch.")
        payload = app_result.model_dump(mode="json")
        _validate_no_prohibited_payload(payload)
        evidence_id = _evidence_id(request, app_result, observed_at)
        evidence = _execution_evidence(request, app_result, evidence_id=evidence_id, observed_at=observed_at)
        self._runtime.append_evidence(evidence)
        result = AstraReadExecutionResult(
            execution_result_id=_result_id(request, app_result, observed_at),
            execution_request_id=request.execution_request_id,
            runtime_instance_id=request.runtime_instance_id,
            authorization_decision_id=request.authorization_decision_id,
            read_capability_id=request.read_capability_id,
            owning_app_id=request.owning_app_id,
            adapter_capability_id=request.adapter_capability_id,
            adapter_capability_version=request.adapter_capability_version,
            operation=request.operation,
            status=(
                AstraReadExecutionStatus.EMPTY
                if app_result.status.value == "empty"
                else AstraReadExecutionStatus.OK
            ),
            result_kind=app_result.result_kind.value,
            records=tuple(dict(record) for record in app_result.records),
            summary=dict(app_result.summary),
            record_count=app_result.record_count,
            returned_count=app_result.returned_count,
            truncated=app_result.truncated,
            reason_codes=(*app_result.reason_codes, "governed_read_execution_bridge"),
            evidence_references=(evidence_id,),
            observed_at=observed_at,
        )
        return result

    def _record_failure(self, request: AstraReadExecutionRequest, *, observed_at: datetime) -> None:
        evidence_id = f"evd_read_exec_{hashlib.sha256(f'{request.execution_request_id}:failure'.encode()).hexdigest()[:20]}"
        evidence = BoundedEvidence(
            evidence_id=evidence_id,
            evidence_type=EvidenceType.AUDIT_INTEGRITY,
            requirement_references=_requirement_references(),
            actor_or_service_class=ActorOrServiceClass.COMPONENT,
            decision_or_operation_reference=f"read-exec/{request.execution_request_id}",
            timestamp=observed_at,
            sensitivity_class=SensitivityClass.INTERNAL,
            minimization_class=MinimizationClass.METADATA_ONLY,
            retention_class=RetentionClass.GOVERNANCE_RECORD,
            integrity=EvidenceIntegrityMetadata(
                source_system="astra_ai:read_execution",
                provenance_reference=f"{READ_EXECUTION_IMPLEMENTATION_REFERENCE}:{READ_EXECUTION_VERSION}",
                content_digest=f"sha256:{hashlib.sha256(request.execution_request_id.encode()).hexdigest()}",
            ),
            correction=EvidenceCorrectionMetadata(evidence_version=READ_EXECUTION_VERSION),
            redaction_status=RedactionStatus.NOT_REQUIRED,
        )
        self._runtime.append_evidence(evidence)

    def _require_ready(self) -> None:
        if getattr(self._runtime.state, "value", None) != "ready":
            raise AstraReadExecutionError("Read execution requires ready Runtime.")


def default_read_adapter_registry() -> AstraReadAdapterRegistry:
    return AstraReadAdapterRegistry(
        tuple(
            (
                AstraReadAdapterDefinition(
                    owning_app_id=SUBSCRIPTION_MANAGER_APP_ID,
                    adapter_capability_id=definition.capability_id,
                    adapter_capability_version=definition.capability_version,
                    operation=READ_OPERATION,
                    implementation_reference=READ_EXECUTION_IMPLEMENTATION_REFERENCE,
                ),
                _subscription_manager_adapter,
            )
            for definition in subscription_reads.capability_catalog()
        )
    )


def _subscription_manager_adapter(context: AstraReadAdapterInvocationContext) -> SubscriptionAstraReadResult:
    return subscription_reads.execute_read_capability(
        context.db,
        context.authenticated_user,
        context.app_read_grant,
    )


def _adapter_key(definition: AstraReadAdapterDefinition) -> tuple[str, str, str, str]:
    return (
        definition.owning_app_id,
        definition.adapter_capability_id,
        definition.adapter_capability_version,
        definition.operation,
    )


def _execution_context_reference(
    decision: AstraReadAuthorizationDecision,
    grant: SubscriptionAstraReadGrant,
) -> str:
    return f"read-exec/{decision.authorization_decision_id}/{grant.grant_id}/{grant.request_reference}"


def _result_id(
    request: AstraReadExecutionRequest,
    app_result: SubscriptionAstraReadResult,
    observed_at: datetime,
) -> str:
    payload = _canonical(
        {
            "request": request.execution_request_id,
            "grant": request.app_read_grant.grant_id,
            "result": app_result.model_dump(mode="json"),
            "observed_at": observed_at.isoformat(),
        }
    )
    return f"read_exec_result_{hashlib.sha256(payload.encode()).hexdigest()[:24]}"


def _evidence_id(
    request: AstraReadExecutionRequest,
    app_result: SubscriptionAstraReadResult,
    observed_at: datetime,
) -> str:
    payload = f"{request.execution_request_id}:{app_result.capability_id}:{observed_at.isoformat()}"
    return f"evd_read_exec_{hashlib.sha256(payload.encode()).hexdigest()[:20]}"


def _execution_evidence(
    request: AstraReadExecutionRequest,
    app_result: SubscriptionAstraReadResult,
    *,
    evidence_id: str,
    observed_at: datetime,
) -> BoundedEvidence:
    digest = hashlib.sha256(
        _canonical(
            {
                "execution_request_id": request.execution_request_id,
                "authorization_decision_id": request.authorization_decision_id,
                "adapter_capability_id": app_result.capability_id,
                "status": app_result.status.value,
                "record_count": app_result.record_count,
                "returned_count": app_result.returned_count,
                "truncated": app_result.truncated,
            }
        ).encode()
    ).hexdigest()
    return BoundedEvidence(
        evidence_id=evidence_id,
        evidence_type=EvidenceType.AUDIT_INTEGRITY,
        requirement_references=_requirement_references(),
        actor_or_service_class=ActorOrServiceClass.COMPONENT,
        decision_or_operation_reference=f"read-exec/{request.execution_request_id}",
        timestamp=observed_at,
        sensitivity_class=SensitivityClass.INTERNAL,
        minimization_class=MinimizationClass.METADATA_ONLY,
        retention_class=RetentionClass.GOVERNANCE_RECORD,
        integrity=EvidenceIntegrityMetadata(
            source_system="astra_ai:read_execution",
            provenance_reference=f"{READ_EXECUTION_IMPLEMENTATION_REFERENCE}:{READ_EXECUTION_VERSION}",
            content_digest=f"sha256:{digest}",
        ),
        correction=EvidenceCorrectionMetadata(evidence_version=READ_EXECUTION_VERSION),
        redaction_status=RedactionStatus.NOT_REQUIRED,
    )


def _requirement_references() -> tuple[ConstitutionalRequirementReference, ...]:
    return (
        ConstitutionalRequirementReference(
            constitutional_source="ASTRA-010",
            requirement_id="AIR-CM-009",
            requirement_version="1.0.0",
        ),
    )


def _validate_no_prohibited_payload(value: Any) -> None:
    for key, item in _walk(value):
        if key and _key_prohibited(key):
            raise AstraReadExecutionError("Read execution payload contains prohibited private material.")
        if isinstance(item, str):
            for pattern in _PROHIBITED_VALUE_PATTERNS:
                if pattern.search(item):
                    raise AstraReadExecutionError("Read execution payload contains prohibited private material.")


def _key_prohibited(key: str) -> bool:
    normalized = key.lower().replace("-", "_")
    return normalized in _PROHIBITED_KEYS or normalized.endswith("_token")


def _walk(value: Any, *, key: str | None = None):
    if isinstance(value, Mapping):
        for item_key, item_value in value.items():
            yield str(item_key), item_value
            yield from _walk(item_value, key=str(item_key))
    elif isinstance(value, (tuple, list)):
        for item in value:
            yield from _walk(item, key=key)


def _ensure_aware(value: datetime, label: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise AstraReadExecutionError(f"{label} timestamp must be timezone-aware.")


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _canonical(value: Any) -> str:
    return json.dumps(value, default=str, sort_keys=True, separators=(",", ":"))
