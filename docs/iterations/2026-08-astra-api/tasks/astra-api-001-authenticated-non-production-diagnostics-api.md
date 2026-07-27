# ASTRA-API-001 Authenticated Non-Production Diagnostics API

Status: Implemented

Implementation Direction: Pending Astra Source Review

Security Review: Pending

Constitutional Conformance: Pending

Product Owner Approval: Pending

Certification: Pending

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

