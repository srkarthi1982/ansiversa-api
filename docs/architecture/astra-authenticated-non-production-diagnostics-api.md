# Astra Authenticated Non-Production Diagnostics API

## Purpose

The diagnostics API exposes a narrow, authenticated, non-production-only
transport over certified ASTRA-IMP-011 diagnostic projections. It does not
interpret Runtime state, fabricate projections, query application data, or
authorize operational Astra behavior.

## Authentication And Authorization

The API reuses the existing parent authentication system and the existing
`require_admin_user` dependency. Authentication is mandatory and admin access is
the explicit developer authorization proof for ASTRA-API-001. Request payloads
do not accept user IDs, emails, role names, tokens, proof objects, or authority
objects.

If a future staff/developer permission framework is approved, this API can be
reviewed to use that framework. ASTRA-API-001 does not introduce one.

## Environment Boundary

`ASTRA_DIAGNOSTICS_API_ENABLED` is disabled by default. Routes are registered
only when the flag is enabled and the resolved environment is an approved
non-production value.

Allowed environment values are:

```text
local
development
test
qa
preview
staging
```

Production and unknown environment values fail closed. Endpoint access also
validates the existing Astra authoritative configuration and requires
`production_authorization_state=not_approved`.

## Runtime Lifecycle

`AstraDiagnosticsRuntimeService` owns one process-local diagnostics Runtime.
The service starts the Runtime only after authentication, admin authorization,
environment validation, diagnostics enablement, and Astra configuration boundary
checks pass. Shutdown clears the Runtime. The Runtime object is never returned
from dependency injection or API responses.

## Endpoint Catalog

`GET /health` returns a bounded operational summary: API availability,
Runtime state, projection health, disabled authoritative configuration,
fail-closed operational status, production authorization not approved, and
database/SQL/data retrieval not authorized.

`POST /projections/runtime` issues a Runtime-owned `runtime_summary` projection
from a Runtime-produced health snapshot.

`POST /projections/evidence` issues an `evidence_summary` projection for an
explicit bounded list of evidence references. The endpoint does not list,
search, or enumerate evidence.

`POST /projections/components` issues a `component_health_summary` projection
from fixed Runtime-produced component health snapshots.

`POST /projections/request` returns bounded unavailable until an approved
Runtime-owned correlation lookup service exists.

## Contracts And Redaction

The API envelope contains `request_id`, `status`, `data`, `error`,
`observed_at`, and `api_version`. Projection payloads are serialized from the
certified projection model with transport-only wrapping.

Strict redaction is the only authorized posture. Metadata-only requests are
rejected with `metadata_only_not_authorized`.

## Error Taxonomy

Errors use fixed bounded codes:

```text
astra_diagnostics_disabled
non_production_required
authentication_required
developer_authorization_required
runtime_unavailable
projection_unavailable
projection_request_invalid
projection_request_expired
evidence_reference_invalid
evidence_reference_missing
unsupported_projection_kind
unsupported_section
metadata_only_not_authorized
rate_limit_exceeded
internal_diagnostic_failure
```

Responses do not expose raw exception text, stack traces, secrets, tokens,
authority objects, Runtime handles, SQL, provider payloads, prompts, or private
module paths.

## OpenAPI, CORS, Logging, And Audit

Routes are marked `include_in_schema=False`; documentation hiding is not a
security boundary. No CORS origins are added. ASTRA-API-001 does not add
database audit persistence or write API access evidence into Astra Evidence
Sink. Projection-operation evidence remains owned by ASTRA-IMP-011.

## Threat Model

Primary threats are anonymous access, authenticated non-developer access,
production activation, caller-supplied authority, Runtime reflection, global
enumeration, response leakage, metadata-only overexposure, and accidental
database/provider/execution expansion. The implementation mitigates these with
existing auth, admin authorization, strict environment parsing, disabled default
configuration, fixed endpoints, strict redaction, bounded inputs, no frontend
client, no CORS change, and no persistence.

