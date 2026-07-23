# I1-024 Architecture Decision Review

**Status:** Approved
**Created:** 2026-07-23
**Task:** I1-024
**Decision Owner:** Karthikeyan Ramalingam
**Architecture Reviewer:** Astra
**Evidence Agent:** Codex

This review resolved the six design questions required before I1-024 could be
frozen. The Architecture Reviewer approved all six decisions, and Karthikeyan
Ramalingam recorded Product Owner approval on 2026-07-23. The approval accepts
the ADR and freezes I1-024. It does not authorize implementation, satisfy G03,
or authorize production.

---

# Review Recommendation

```text
Option A — Unchanged AuditLogs reuse    Rejected
Option B — Bounded AuditLogs extension  Approved
Option C — Dedicated Astra store        Rejected

ADR status                              Accepted
I1-024 status                           Frozen
Implementation authorization            No
Production flag                         false
Production authorization                No
G03                                     Not passed
```

Option B preserves one parent-owned operational audit system while giving
Astra a typed, minimized, queryable event contract. The existing generic writer
must not become the Astra contract. Astra must use a dedicated validated adapter
over the shared audit store.

Option C remains available if implementation evidence disproves a frozen Option
B assumption. It is not justified by current evidence.

---

# Decision 1 — Storage Architecture

Recommend **Option B: bounded, backward-compatible extension of `AuditLogs`**.

Separation of concerns is preserved by defining:

- `AuditLogs` as the parent/global operational audit system;
- Astra as the owner of one typed event adapter and event taxonomy;
- Activity Timeline as product journey history, never operational audit;
- application databases as sources of application facts; and
- raw conversations, analytics, observability payloads, and app records as
  prohibited audit content.

---

# Decision 2 — Cardinality, Schema, And Reasons

## Event Cardinality

The unit of evidence is **one durable row per personal-data tool attempt**.

- A single-tool request produces one attempt row.
- A composed request produces one row for each attempted tool.
- All attempts from one Assistant request share one backend-issued
  `correlationId`.
- A denial or unavailability before tool selection produces one request-level
  event with `toolName` and `sourceApp` null.
- Public, identity, and safety paths that do not attempt personal-data access do
  not produce personal-data audit events.

`correlationId` is therefore required but not unique.

## Frozen Logical Schema

Existing fields:

| Field | Astra rule |
|---|---|
| `id` | Required backend UUID; unique event ID |
| `actorUserId` | Required for authenticated attempts; null only when authentication itself was denied |
| `action` | Fixed `astra.personal_data.tool_attempt` or `astra.personal_data.request_denied` |
| `entityType` | Fixed `AstraPersonalDataAudit` |
| `createdAt` | Required server UTC timestamp |

Extension fields:

| Field | Type / bound | Rule |
|---|---|---|
| `auditClass` | string, 40 | Required; fixed `astra_personal_data` |
| `correlationId` | string, 80 | Required; backend-issued and non-unique |
| `capability` | string, 120 | Required when resolved; otherwise null |
| `toolName` | string, 120 | Required when a tool was selected |
| `sourceApp` | string, 80 | Required for app-owned tools |
| `inputClassification` | string, 80 | Required allowlisted classification |
| `outputClassification` | string, 80 | Required allowlisted classification |
| `providerContextCategory` | string, 80 | Approved category or null |
| `outcome` | string, 24 | `allowed`, `denied`, `failed`, or `unavailable` |
| `reasonCode` | string, 120 | Required allowlisted reason |
| `durationBucket` | string, 24 | Required bounded bucket |
| `deploymentVersion` | string, 120 | Required deployed artifact identifier |
| `eventSchemaVersion` | integer | Required; initial value `1` |
| `expiresAt` | timestamp | Required UTC value, normally `createdAt + 365 days` |
| `holdUntil` | timestamp | Null unless an approved incident hold applies |

New columns remain nullable at the physical shared-table level for backward
compatibility. The Astra adapter enforces the conditional required fields.

Deployment version resolves from the immutable deployed commit/artifact
identifier and may fall back to the application version only outside governed
deployment verification.

## Reason-Code Taxonomy

Allowed:

- `completed`
- `completed_no_data`

Denied:

- `authentication_required`
- `personal_data_disabled`
- `consent_required`
- `permission_denied`
- `owner_scope_rejected`
- `argument_rejected`

Failed:

- `context_resolution_failed`
- `tool_execution_failed`
- `tool_timeout`
- `result_validation_failed`

Unavailable:

- `capability_disabled`
- `capability_deprecated`
- `capability_unregistered`
- `dependency_unavailable`
- `no_supported_tool`

An audit persistence failure cannot durably record its own failed event. It
must instead produce safe external operational telemetry, discard the personal
result, and return bounded unavailable behavior.

---

# Decision 3 — Prohibited-Field Contract

For `astra_personal_data` rows:

- `actorEmail`, `entityId`, `entityLabel`, `ipAddress`, `userAgent`, and
  `metadataJson` are null;
- raw prompts, responses, tool arguments, tool results, personal records, app
  record IDs, caller-supplied owner IDs, SQL, tokens, cookies, claims, secrets,
  and stack traces are prohibited;
- arbitrary supplemental metadata is not allowed in schema version 1; and
- only backend-derived registry identifiers and bounded enums may populate the
  typed fields.

The adapter must reject unknown fields, unknown enum values, and values over
their bounds before persistence.

---

# Decision 4 — Retention, Access, And Integrity

## Retention

- `expiresAt` is set at write time to 365 days after `createdAt`.
- `holdUntil` prevents deletion while a separately approved incident hold is
  active.
- A daily Vercel Cron Job invokes a FastAPI cleanup route in the production
  deployment.
- The route requires `Authorization: Bearer <CRON_SECRET>` and fails closed
  when the secret is absent or invalid.
- Cleanup deletes bounded batches matching:

  ```text
  auditClass = astra_personal_data
  AND expiresAt < current UTC time
  AND (holdUntil IS NULL OR holdUntil < current UTC time)
  ```

- Repeated or overlapping invocations must be safe and idempotent.
- Failure is alerted because Vercel does not retry a failed cron invocation.
- Cleanup emits one bounded operational summary, not one recursive audit event
  per deleted row.
- Non-Astra rows are never selected by this retention job.

The implementation must define and verify the batch size, duration budget,
concurrency control, missed-run alert, and recovery runbook.

## Access

- No public, user-facing, or ordinary authenticated audit endpoint is created.
- Phase 1 operational reads require an active parent administrator through a
  dedicated `require_audit_reader` authorization boundary.
- The boundary initially delegates to the existing administrator role but is
  named separately so a future permission registry can narrow it without
  changing callers.
- Reads are filtered, paginated, and field-allowlisted.
- Audit reads themselves create bounded security audit events.
- No update endpoint or routine delete endpoint exists.

## Integrity

Integrity means:

- append-only application behavior;
- no Astra update/delete service outside governed retention;
- server-owned least-privilege database credentials;
- strict adapter validation;
- observable write failures;
- restricted and audited reads; and
- tested backup/point-in-time recovery procedures.

Cryptographic immutability is not required for I1-024. Turso point-in-time
recovery is recovery evidence, not tamper evidence.

---

# Decision 5 — Fail-Closed And Migration Strategies

## Fail-Closed Boundary

```text
Authenticate and authorize
    ↓
Resolve bounded intent and tool plan
    ↓
Execute owner-scoped read-only tool
    ↓
Construct bounded audit event
    ↓
Persist and commit every required attempt event
    ↓
Only then expose the personal result to OpenAI or the user
```

If any required event cannot be committed:

- roll back the audit session;
- discard all personal results for the request;
- do not send those results to OpenAI;
- return bounded unavailable behavior; and
- emit non-personal failure telemetry and an operational alert.

For a composed request, the response is withheld until every required attempt
event is durable. Future write tools require a separate atomicity decision and
are outside I1-024.

## Migration

- Create one new parent Alembic revision from current parent head
  `20260720_0003`.
- Add nullable columns so legacy rows and existing admin writers remain valid.
- Preserve the meanings of every existing column and index.
- Add non-unique indexes for:

  ```text
  (correlationId)
  (auditClass, actorUserId, createdAt DESC)
  (auditClass, outcome, createdAt DESC)
  (auditClass, capability, toolName, createdAt DESC)
  (auditClass, expiresAt)
  ```

- Do not rewrite legacy metadata or classify historical rows during migration.
- Deploy the compatible schema before code that writes Astra version-1 events.
- Roll application code back independently while the additive nullable schema
  remains in place.
- Do not use an automatic destructive production downgrade. Column removal
  requires a later governed cleanup after the rollback window.
- Rehearse upgrade, old-writer compatibility, application rollback, and
  separately approved database recovery in the governed environment.

---

# Decision 6 — Implementation Validation Matrix

Implementation may be verified only against the complete matrix in
`i1-024-option-b-evidence.md`, including:

- event contract and prohibited-field enforcement;
- all four outcomes and approved cardinality;
- authentication, owner isolation, and correlation behavior;
- audit-write failure before OpenAI/user disclosure;
- legacy writer and row compatibility;
- retention boundaries, holds, idempotency, concurrency, and non-Astra safety;
- restricted/audited reader access and absent mutation APIs;
- migration upgrade and application rollback;
- target Turso/libSQL indexes and query plans;
- production-shaped latency and cleanup behavior;
- clean deployment-runtime dependency installation; and
- safe-default flag and production-disabled assertions.

Architecture freeze approves this executable validation plan. It does not claim
that any validation item has passed.

---

# Evidence Boundary

Required before architecture freeze:

- cardinality, schema, and reason taxonomy;
- prohibited fields;
- retention owner and mechanism;
- access and integrity model;
- fail-closed response boundary;
- indexes;
- migration and rollback strategy;
- supported deployment compatibility plan; and
- executable validation matrix.

Required during implementation and verification:

- migration and rollback rehearsals;
- target Turso/libSQL query plans;
- real cleanup execution and concurrency evidence;
- deployed-driver write-failure tests;
- governed deployment evidence;
- production-shaped performance; and
- recovery rehearsal.

This distinction prevents implementation evidence from becoming a circular
precondition for authorizing implementation.

---

# Product Owner Decision

The six decisions were approved on 2026-07-23:

```text
ADR status                   Accepted
I1-024 status                Frozen
Architecture                 Option B selected
Implementation authorization Separate decision; not implied
Production flag              false
Production authorization     No
G03                          Not passed
```

This architecture approval is complete. Implementation remains pending a
separate, explicit Product Owner authorization.
