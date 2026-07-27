from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any

from app.core.config import Settings, settings
from app.modules.astra_ai.api.schemas import (
    ASTRA_DIAGNOSTICS_API_VERSION,
    AstraComponentHealthProjectionRequest,
    AstraDiagnosticsEnvelope,
    AstraDiagnosticsError,
    AstraDiagnosticsErrorCode,
    AstraEvidenceProjectionRequest,
    AstraRequestDiagnosticRequest,
    AstraRuntimeProjectionRequest,
)
from app.modules.astra_ai.configuration import AstraConfigurationError, load_astra_configuration
from app.modules.astra_ai.constitutional_contracts import (
    EnvironmentScope,
    ProductionAuthorizationState,
)
from app.modules.astra_ai.diagnostic_projection import (
    AstraDiagnosticProjectionError,
    AstraDiagnosticProjectionKind,
    AstraDiagnosticRedactionPosture,
    AstraDiagnosticSection,
)
from app.modules.astra_ai.runtime import AstraRuntime, AstraRuntimeError, AstraRuntimeState


ALLOWED_DIAGNOSTICS_ENVIRONMENTS = {
    "local",
    "development",
    "test",
    "qa",
    "preview",
    "staging",
}
PRODUCTION_ENVIRONMENTS = {"production"}
REQUEST_DIAGNOSTIC_UNAVAILABLE = (
    "Request diagnostics require an authoritative Runtime-owned correlation lookup service."
)


class AstraDiagnosticsApiError(ValueError):
    def __init__(self, code: AstraDiagnosticsErrorCode, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


class AstraDiagnosticsRuntimeService:
    """Application-owned non-production Runtime lifecycle for diagnostics only."""

    def __init__(self) -> None:
        self._runtime: AstraRuntime | None = None

    def startup(self) -> None:
        if self._runtime is not None and self._runtime.state is AstraRuntimeState.READY:
            return
        runtime = AstraRuntime()
        runtime.startup()
        self._runtime = runtime

    def shutdown(self) -> None:
        if self._runtime is None:
            return
        if self._runtime.state in {AstraRuntimeState.READY, AstraRuntimeState.FAULTED}:
            self._runtime.shutdown()
        self._runtime = None

    def require_runtime(self) -> AstraRuntime:
        if self._runtime is None or self._runtime.state is not AstraRuntimeState.READY:
            raise AstraDiagnosticsApiError(
                AstraDiagnosticsErrorCode.RUNTIME_UNAVAILABLE,
                "Astra diagnostics Runtime is unavailable.",
            )
        return self._runtime


class AstraDiagnosticsService:
    def __init__(
        self,
        *,
        runtime_service: AstraDiagnosticsRuntimeService,
        app_settings: Settings = settings,
    ) -> None:
        self._runtime_service = runtime_service
        self._settings = app_settings

    def validate_access(self) -> None:
        environment = diagnostics_environment(self._settings)
        if environment is None:
            raise AstraDiagnosticsApiError(
                AstraDiagnosticsErrorCode.NON_PRODUCTION_REQUIRED,
                "Astra diagnostics require a known non-production environment.",
            )
        if environment in PRODUCTION_ENVIRONMENTS:
            raise AstraDiagnosticsApiError(
                AstraDiagnosticsErrorCode.NON_PRODUCTION_REQUIRED,
                "Astra diagnostics are not available in production.",
            )
        if environment not in ALLOWED_DIAGNOSTICS_ENVIRONMENTS:
            raise AstraDiagnosticsApiError(
                AstraDiagnosticsErrorCode.NON_PRODUCTION_REQUIRED,
                "Astra diagnostics require an approved non-production environment.",
            )
        if not self._settings.ASTRA_DIAGNOSTICS_API_ENABLED:
            raise AstraDiagnosticsApiError(
                AstraDiagnosticsErrorCode.DIAGNOSTICS_DISABLED,
                "Astra diagnostics API is disabled.",
            )

        try:
            loaded = load_astra_configuration(app_settings=self._settings)
        except AstraConfigurationError as exc:
            raise AstraDiagnosticsApiError(
                AstraDiagnosticsErrorCode.NON_PRODUCTION_REQUIRED,
                "Astra diagnostics require a valid Astra environment boundary.",
            ) from exc
        if loaded.configuration.environment_scope is EnvironmentScope.PRODUCTION:
            raise AstraDiagnosticsApiError(
                AstraDiagnosticsErrorCode.NON_PRODUCTION_REQUIRED,
                "Astra diagnostics are not available in production.",
            )
        if loaded.configuration.production_authorization_state is not ProductionAuthorizationState.NOT_APPROVED:
            raise AstraDiagnosticsApiError(
                AstraDiagnosticsErrorCode.NON_PRODUCTION_REQUIRED,
                "Astra production authorization is not approved for diagnostics.",
            )

        try:
            self._runtime_service.startup()
        except AstraRuntimeError as exc:
            raise AstraDiagnosticsApiError(
                AstraDiagnosticsErrorCode.RUNTIME_UNAVAILABLE,
                "Astra diagnostics Runtime startup failed closed.",
            ) from exc

    def health(self) -> AstraDiagnosticsEnvelope:
        return self._run_operation(self._health)

    def runtime_projection(
        self,
        payload: AstraRuntimeProjectionRequest,
    ) -> AstraDiagnosticsEnvelope:
        return self._run_operation(lambda: self._runtime_projection(payload))

    def evidence_projection(
        self,
        payload: AstraEvidenceProjectionRequest,
    ) -> AstraDiagnosticsEnvelope:
        return self._run_operation(lambda: self._evidence_projection(payload))

    def request_diagnostic(
        self,
        payload: AstraRequestDiagnosticRequest,
    ) -> AstraDiagnosticsEnvelope:
        _ = payload
        observed_at = _now()
        return _unavailable(
            code=AstraDiagnosticsErrorCode.PROJECTION_UNAVAILABLE,
            message=REQUEST_DIAGNOSTIC_UNAVAILABLE,
            observed_at=observed_at,
        )

    def component_health_projection(
        self,
        payload: AstraComponentHealthProjectionRequest,
    ) -> AstraDiagnosticsEnvelope:
        return self._run_operation(lambda: self._component_health_projection(payload))

    def _run_operation(self, operation):
        try:
            return operation()
        except AstraDiagnosticsApiError:
            raise
        except AstraRuntimeError as exc:
            raise AstraDiagnosticsApiError(
                AstraDiagnosticsErrorCode.RUNTIME_UNAVAILABLE,
                "Astra diagnostics Runtime operation is unavailable.",
            ) from exc
        except AstraDiagnosticProjectionError as exc:
            raise AstraDiagnosticsApiError(
                AstraDiagnosticsErrorCode.PROJECTION_REQUEST_INVALID,
                "Astra diagnostics projection request is invalid.",
            ) from exc
        except Exception as exc:
            raise AstraDiagnosticsApiError(
                AstraDiagnosticsErrorCode.INTERNAL_DIAGNOSTIC_FAILURE,
                "Astra diagnostics operation failed closed.",
            ) from exc

    def _health(self) -> AstraDiagnosticsEnvelope:
        observed_at = _now()
        runtime = self._runtime_service.require_runtime()
        runtime_health = runtime.health(observed_at=observed_at)
        projection_health = runtime.diagnostic_projection_health(observed_at=observed_at)
        return _ok(
            data={
                "api_status": "available_non_production",
                "runtime_state": runtime_health.runtime_state.value,
                "projection_health": projection_health.projection_health_outcome.value,
                "authoritative_configuration": (
                    "disabled" if runtime_health.configuration_valid else "unavailable"
                ),
                "operational_astra_status": "fail_closed",
                "production_authorization": "not_approved",
                "database_connection": "not_authorized",
                "sql_execution": "not_authorized",
                "data_retrieval": "not_performed",
            },
            observed_at=observed_at,
        )

    def _runtime_projection(
        self,
        payload: AstraRuntimeProjectionRequest,
    ) -> AstraDiagnosticsEnvelope:
        observed_at = _now()
        _require_strict(payload.redaction_posture)
        runtime = self._runtime_service.require_runtime()
        runtime_health = runtime.health(observed_at=observed_at)
        request = runtime.diagnostic_projection.issue_request(
            projection_request_id=_projection_request_id("runtime", observed_at),
            projection_kind=AstraDiagnosticProjectionKind.RUNTIME_SUMMARY,
            requested_sections=tuple(_section(section) for section in payload.requested_sections),
            maximum_timeline_entries=payload.maximum_timeline_entries,
            requested_redaction_posture=AstraDiagnosticRedactionPosture.STRICT,
            requested_at=observed_at,
            runtime_health=runtime_health,
        )
        return _projection_envelope(runtime, request, observed_at=observed_at)

    def _evidence_projection(
        self,
        payload: AstraEvidenceProjectionRequest,
    ) -> AstraDiagnosticsEnvelope:
        observed_at = _now()
        _require_strict(payload.redaction_posture)
        runtime = self._runtime_service.require_runtime()
        request = runtime.diagnostic_projection.issue_request(
            projection_request_id=_projection_request_id("evidence", observed_at),
            projection_kind=AstraDiagnosticProjectionKind.EVIDENCE_SUMMARY,
            requested_sections=(AstraDiagnosticSection.EVIDENCE,),
            maximum_timeline_entries=payload.maximum_timeline_entries,
            requested_redaction_posture=AstraDiagnosticRedactionPosture.STRICT,
            requested_at=observed_at,
            evidence_references=payload.evidence_references,
        )
        return _projection_envelope(runtime, request, observed_at=observed_at)

    def _component_health_projection(
        self,
        payload: AstraComponentHealthProjectionRequest,
    ) -> AstraDiagnosticsEnvelope:
        observed_at = _now()
        _require_strict(payload.redaction_posture)
        runtime = self._runtime_service.require_runtime()
        component_snapshots: list[Any] = []
        sections = [AstraDiagnosticSection.COMPONENT_HEALTH]
        runtime_health = None
        if "runtime" in payload.components:
            runtime_health = runtime.health(observed_at=observed_at)
            sections.insert(0, AstraDiagnosticSection.RUNTIME)
        if "capability_discovery" in payload.components:
            component_snapshots.append(runtime.capability_discovery_health(observed_at=observed_at))
        if "intent_resolution" in payload.components:
            component_snapshots.append(runtime.intent_resolution_health(observed_at=observed_at))
        if "planning" in payload.components:
            component_snapshots.append(runtime.planning_health(observed_at=observed_at))
        if "read_access_authorization" in payload.components:
            component_snapshots.append(runtime.read_access_authorization_health(observed_at=observed_at))

        request = runtime.diagnostic_projection.issue_request(
            projection_request_id=_projection_request_id("components", observed_at),
            projection_kind=AstraDiagnosticProjectionKind.COMPONENT_HEALTH_SUMMARY,
            requested_sections=tuple(sections),
            maximum_timeline_entries=payload.maximum_timeline_entries,
            requested_redaction_posture=AstraDiagnosticRedactionPosture.STRICT,
            requested_at=observed_at,
            runtime_health=runtime_health,
            component_health_snapshots=tuple(component_snapshots),
        )
        return _projection_envelope(runtime, request, observed_at=observed_at)


runtime_service = AstraDiagnosticsRuntimeService()
diagnostics_service = AstraDiagnosticsService(runtime_service=runtime_service)


def diagnostics_environment(app_settings: Settings = settings) -> str | None:
    app_env = app_settings.APP_ENV.strip().lower()
    vercel_env = (app_settings.VERCEL_ENV or "").strip().lower()
    if app_env in PRODUCTION_ENVIRONMENTS or vercel_env in PRODUCTION_ENVIRONMENTS:
        return "production"
    if vercel_env:
        return vercel_env if vercel_env in ALLOWED_DIAGNOSTICS_ENVIRONMENTS else None
    return app_env if app_env in ALLOWED_DIAGNOSTICS_ENVIRONMENTS else None


def should_register_diagnostics_routes(app_settings: Settings = settings) -> bool:
    environment = diagnostics_environment(app_settings)
    return bool(
        app_settings.ASTRA_DIAGNOSTICS_API_ENABLED
        and environment in ALLOWED_DIAGNOSTICS_ENVIRONMENTS
    )


def _projection_envelope(
    runtime: AstraRuntime,
    request,
    *,
    observed_at: datetime,
) -> AstraDiagnosticsEnvelope:
    try:
        projection = runtime.diagnostic_projection.project(request, created_at=observed_at)
    except AstraDiagnosticProjectionError as exc:
        raise AstraDiagnosticsApiError(
            AstraDiagnosticsErrorCode.PROJECTION_UNAVAILABLE,
            "Astra certified diagnostic projection is unavailable.",
        ) from exc
    return _ok(
        data={
            "projection": projection.model_dump(mode="json"),
            "transport": {
                "redaction_posture": "strict",
                "transport_minimization": "api_envelope_only",
            },
        },
        observed_at=observed_at,
    )


def _require_strict(redaction_posture: str) -> None:
    if redaction_posture != "strict":
        raise AstraDiagnosticsApiError(
            AstraDiagnosticsErrorCode.METADATA_ONLY_NOT_AUTHORIZED,
            "Metadata-only diagnostics are not authorized by ASTRA-API-001.",
        )


def _section(value: str) -> AstraDiagnosticSection:
    try:
        return AstraDiagnosticSection(value)
    except ValueError as exc:
        raise AstraDiagnosticsApiError(
            AstraDiagnosticsErrorCode.UNSUPPORTED_SECTION,
            "Requested diagnostic section is not supported.",
        ) from exc


def _ok(*, data: dict[str, Any], observed_at: datetime) -> AstraDiagnosticsEnvelope:
    return AstraDiagnosticsEnvelope(
        request_id=_api_request_id(observed_at),
        status="ok",
        data=data,
        error=None,
        observed_at=observed_at,
        api_version=ASTRA_DIAGNOSTICS_API_VERSION,
    )


def _unavailable(
    *,
    code: AstraDiagnosticsErrorCode,
    message: str,
    observed_at: datetime,
) -> AstraDiagnosticsEnvelope:
    return AstraDiagnosticsEnvelope(
        request_id=_api_request_id(observed_at),
        status="unavailable",
        data=None,
        error=AstraDiagnosticsError(code=code, message=message),
        observed_at=observed_at,
        api_version=ASTRA_DIAGNOSTICS_API_VERSION,
    )


def _projection_request_id(kind: str, observed_at: datetime) -> str:
    digest = hashlib.sha256(f"{kind}:{observed_at.isoformat()}".encode()).hexdigest()
    return f"diag_req_api_{kind}_{digest[:24]}"


def _api_request_id(observed_at: datetime) -> str:
    digest = hashlib.sha256(observed_at.isoformat().encode()).hexdigest()
    return f"api_diag_{digest[:24]}"


def _now() -> datetime:
    return datetime.now(timezone.utc)
