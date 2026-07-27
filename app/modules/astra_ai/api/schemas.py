from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


ASTRA_DIAGNOSTICS_API_VERSION = "1.0.0"
MAX_API_EVIDENCE_REFERENCES = 50
MAX_API_TIMELINE_ENTRIES = 50


class AstraDiagnosticsErrorCode(StrEnum):
    DIAGNOSTICS_DISABLED = "astra_diagnostics_disabled"
    NON_PRODUCTION_REQUIRED = "non_production_required"
    AUTHENTICATION_REQUIRED = "authentication_required"
    DEVELOPER_AUTHORIZATION_REQUIRED = "developer_authorization_required"
    RUNTIME_UNAVAILABLE = "runtime_unavailable"
    PROJECTION_UNAVAILABLE = "projection_unavailable"
    PROJECTION_REQUEST_INVALID = "projection_request_invalid"
    PROJECTION_REQUEST_EXPIRED = "projection_request_expired"
    EVIDENCE_REFERENCE_INVALID = "evidence_reference_invalid"
    EVIDENCE_REFERENCE_MISSING = "evidence_reference_missing"
    UNSUPPORTED_PROJECTION_KIND = "unsupported_projection_kind"
    UNSUPPORTED_SECTION = "unsupported_section"
    METADATA_ONLY_NOT_AUTHORIZED = "metadata_only_not_authorized"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    INTERNAL_DIAGNOSTIC_FAILURE = "internal_diagnostic_failure"


class AstraDiagnosticsError(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    code: AstraDiagnosticsErrorCode
    message: str = Field(min_length=8, max_length=180)


class AstraDiagnosticsEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    request_id: str = Field(pattern=r"^api_diag_[a-f0-9]{24}$")
    status: Literal["ok", "unavailable", "error"]
    data: dict[str, Any] | None
    error: AstraDiagnosticsError | None
    observed_at: datetime
    api_version: str = ASTRA_DIAGNOSTICS_API_VERSION


class AstraRuntimeProjectionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    requested_sections: tuple[Literal["runtime", "evidence"], ...] = Field(
        default=("runtime",),
        min_length=1,
        max_length=2,
    )
    maximum_timeline_entries: int = Field(
        default=10,
        ge=1,
        le=MAX_API_TIMELINE_ENTRIES,
    )
    redaction_posture: Literal["strict", "metadata_only"] = "strict"
    client_request_reference: str | None = Field(
        default=None,
        min_length=1,
        max_length=120,
        pattern=r"^[A-Za-z0-9][A-Za-z0-9:._/-]{0,119}$",
    )

    @field_validator("requested_sections")
    @classmethod
    def validate_unique_sections(cls, value):
        if len(value) != len(set(value)):
            raise ValueError("Requested sections must be unique.")
        return value


class AstraEvidenceProjectionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    evidence_references: tuple[str, ...] = Field(
        min_length=1,
        max_length=MAX_API_EVIDENCE_REFERENCES,
    )
    maximum_timeline_entries: int = Field(
        default=10,
        ge=1,
        le=MAX_API_TIMELINE_ENTRIES,
    )
    redaction_posture: Literal["strict", "metadata_only"] = "strict"
    client_request_reference: str | None = Field(
        default=None,
        min_length=1,
        max_length=120,
        pattern=r"^[A-Za-z0-9][A-Za-z0-9:._/-]{0,119}$",
    )

    @field_validator("evidence_references")
    @classmethod
    def validate_evidence_references(cls, value):
        if len(value) != len(set(value)):
            raise ValueError("Evidence references must be unique.")
        for reference in value:
            if not isinstance(reference, str) or not reference.startswith("evd_"):
                raise ValueError("Evidence references must use certified evidence IDs.")
            if len(reference) > 124 or not reference.replace("_", "").replace("-", "").isalnum():
                raise ValueError("Evidence references must use certified evidence IDs.")
        return value


class AstraRequestDiagnosticRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    client_request_reference: str | None = Field(
        default=None,
        min_length=1,
        max_length=120,
        pattern=r"^[A-Za-z0-9][A-Za-z0-9:._/-]{0,119}$",
    )


class AstraComponentHealthProjectionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    components: tuple[
        Literal[
            "runtime",
            "capability_discovery",
            "intent_resolution",
            "planning",
            "read_access_authorization",
        ],
        ...,
    ] = Field(
        default=(
            "runtime",
            "capability_discovery",
            "intent_resolution",
            "planning",
            "read_access_authorization",
        ),
        min_length=1,
        max_length=5,
    )
    maximum_timeline_entries: int = Field(
        default=10,
        ge=1,
        le=MAX_API_TIMELINE_ENTRIES,
    )
    redaction_posture: Literal["strict", "metadata_only"] = "strict"
    client_request_reference: str | None = Field(
        default=None,
        min_length=1,
        max_length=120,
        pattern=r"^[A-Za-z0-9][A-Za-z0-9:._/-]{0,119}$",
    )

    @field_validator("components")
    @classmethod
    def validate_unique_components(cls, value):
        if len(value) != len(set(value)):
            raise ValueError("Components must be unique.")
        return value
