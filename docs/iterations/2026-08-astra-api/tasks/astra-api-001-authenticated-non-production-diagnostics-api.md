# ASTRA-API-001 Authenticated Non-Production Diagnostics API

Status: Certified / Approved

Implementation Direction: Approved

Astra Re-review: Approved

Security Review: Approved

Constitutional Conformance: Approved

Product Owner Approval: Approved

Certification: Passed

## Final Certified State

```text
ASTRA-API-001               Certified / Approved
Implementation Scope        Authenticated Non-Production Diagnostics API

Implementation Direction    Approved
Astra Re-review             Approved
Security Review             Approved
Constitutional Conformance  Approved
Product Owner Approval      Approved
Certification               Passed

Authentication              Required
Developer Authorization     Required
Environment                 Non-production only
Default Redaction           Strict
Projection Authority        ASTRA-IMP-011 only

Frontend Integration        Not authorized
Database / SQL              Not authorized
Production Authorization    Not approved
Production                  Unchanged

ASTRA-API-VAL-001           Not authorized
ASTRA-UI-001                Not authorized
```

## Correction Status

The source-review corrections after commit `f7594b48` have been applied:

1. The diagnostics Runtime is bound to FastAPI application shutdown whenever
   the diagnostics router is registered. Lazy startup remains preserved.
2. Diagnostics operations now use a service-level bounded error boundary around
   Runtime access, health generation, projection request issuance, component
   health generation, projection creation, and unexpected failures.

Product Owner approval was granted after Astra final source-level and
security-boundary re-review of commit `b8989dbb`.

## Scope

ASTRA-API-001 adds a backend-only internal diagnostics API for authenticated
administrator access in approved non-production environments. The API is a
transport boundary over immutable diagnostic projections created by the
certified ASTRA-IMP-011 Diagnostic Projection Engine.

## Authorized Surface

Route prefix:

```text
/internal/astra/diagnostics
```

Endpoints:

```text
GET  /health
POST /projections/runtime
POST /projections/request
POST /projections/evidence
POST /projections/components
```

The request diagnostic endpoint returns a bounded unavailable response because
there is no certified Runtime-owned correlation lookup service for arbitrary
request objects.

## Explicit Non-Goals

No frontend integration, ASTRA-UI-001, user chat, public endpoint, production
diagnostics, anonymous access, caller-selected authority, custom authentication,
global enumeration, Runtime reflection, persistence, database access, SQL,
provider invocation, prompts, model calls, Tool Executor, telemetry exporter,
CORS expansion, migration, deployment change, or production activation is
included.
