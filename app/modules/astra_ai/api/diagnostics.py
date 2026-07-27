from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request, status
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.modules.astra_ai.api.schemas import (
    AstraComponentHealthProjectionRequest,
    AstraDiagnosticsEnvelope,
    AstraDiagnosticsErrorCode,
    AstraEvidenceProjectionRequest,
    AstraRequestDiagnosticRequest,
    AstraRuntimeProjectionRequest,
)
from app.modules.astra_ai.api.service import AstraDiagnosticsApiError, diagnostics_service
from app.modules.auth.dependencies import require_admin_user
from app.modules.auth.models import User


router = APIRouter(include_in_schema=False)
DIAGNOSTICS_ROUTE_PREFIX = "/internal/astra/diagnostics"
DIAGNOSTICS_VALIDATION_ERROR_MESSAGE = "Astra diagnostics request validation failed."


def register_astra_diagnostics_validation_handler(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def astra_diagnostics_validation_handler(
        request: Request,
        exc: RequestValidationError,
    ):
        if not _is_astra_diagnostics_path(request.url.path):
            return await request_validation_exception_handler(request, exc)

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": {
                    "code": AstraDiagnosticsErrorCode.PROJECTION_REQUEST_INVALID.value,
                    "message": DIAGNOSTICS_VALIDATION_ERROR_MESSAGE,
                }
            },
        )


def _is_astra_diagnostics_path(path: str) -> bool:
    return path == DIAGNOSTICS_ROUTE_PREFIX or path.startswith(f"{DIAGNOSTICS_ROUTE_PREFIX}/")


def require_astra_diagnostics_access(
    current_admin: Annotated[User, Depends(require_admin_user)],
) -> User:
    try:
        diagnostics_service.validate_access()
    except AstraDiagnosticsApiError as exc:
        raise HTTPException(
            status_code=_status_for_error(exc.code.value),
            detail={"code": exc.code.value, "message": exc.message},
        ) from exc
    return current_admin


@router.get("/health", response_model=AstraDiagnosticsEnvelope)
def get_diagnostics_health(
    _current_admin: Annotated[User, Depends(require_astra_diagnostics_access)],
) -> AstraDiagnosticsEnvelope:
    return _call_service(diagnostics_service.health)


@router.post("/projections/runtime", response_model=AstraDiagnosticsEnvelope)
def create_runtime_projection(
    payload: AstraRuntimeProjectionRequest,
    _current_admin: Annotated[User, Depends(require_astra_diagnostics_access)],
) -> AstraDiagnosticsEnvelope:
    return _call_service(lambda: diagnostics_service.runtime_projection(payload))


@router.post("/projections/request", response_model=AstraDiagnosticsEnvelope)
def create_request_projection(
    payload: AstraRequestDiagnosticRequest,
    _current_admin: Annotated[User, Depends(require_astra_diagnostics_access)],
) -> AstraDiagnosticsEnvelope:
    return _call_service(lambda: diagnostics_service.request_diagnostic(payload))


@router.post("/projections/evidence", response_model=AstraDiagnosticsEnvelope)
def create_evidence_projection(
    payload: AstraEvidenceProjectionRequest,
    _current_admin: Annotated[User, Depends(require_astra_diagnostics_access)],
) -> AstraDiagnosticsEnvelope:
    return _call_service(lambda: diagnostics_service.evidence_projection(payload))


@router.post("/projections/components", response_model=AstraDiagnosticsEnvelope)
def create_component_health_projection(
    payload: AstraComponentHealthProjectionRequest,
    _current_admin: Annotated[User, Depends(require_astra_diagnostics_access)],
) -> AstraDiagnosticsEnvelope:
    return _call_service(lambda: diagnostics_service.component_health_projection(payload))


def _call_service(operation):
    try:
        return operation()
    except AstraDiagnosticsApiError as exc:
        raise HTTPException(
            status_code=_status_for_error(exc.code.value),
            detail={"code": exc.code.value, "message": exc.message},
        ) from exc


def _status_for_error(code: str) -> int:
    if code == "astra_diagnostics_disabled":
        return status.HTTP_404_NOT_FOUND
    if code in {"authentication_required", "developer_authorization_required"}:
        return status.HTTP_403_FORBIDDEN
    return status.HTTP_403_FORBIDDEN
