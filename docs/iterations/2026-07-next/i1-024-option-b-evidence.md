# I1-024 Option B Evidence

**Status:** Repository evidence approved; Option B accepted
**Created:** 2026-07-23
**Task:** I1-024
**Option:** Bounded, backward-compatible extension of parent-owned `AuditLogs`
**Architecture Decision:** Pending

This document completes the repository-level evidence that can be collected
without changing runtime code, querying production, or implementing I1-024.

This dossier supplied the evidence used to accept Option B. It does not
authorize implementation or claim that implementation evidence has passed.

---

# Formal Architecture Question

> Can the existing parent-owned `AuditLogs` system satisfy G03 through a
> bounded, backward-compatible extension without violating separation of
> concerns?

Current disposition:

```text
Option A — Unchanged reuse          Rejected in principle
Option B — Bounded extension        Accepted
Option C — Dedicated Astra store    Rejected; not justified by evidence
```

---

# Evidence Sources

Repository evidence:

- `app/modules/audit/models.py`
- `app/modules/audit/service.py`
- `app/modules/audit/schemas.py`
- `migrations/parent/versions/29cde1832712_add_audit_logs_table.py`
- admin app, category, and FAQ audit integrations
- local read-only `ansiversa_api.db` schema and query plans
- I1-023 G03 requirements

Primary platform references:

- [Turso SQLAlchemy integration](https://docs.turso.tech/sdk/python/orm/sqlalchemy)
- [Turso ALTER TABLE reference](https://docs.turso.tech/sql-reference/statements/alter-table)
- [Turso point-in-time recovery](https://docs.turso.tech/features/point-in-time-recovery)
- [SQLite CREATE TABLE and constraints](https://sqlite.org/lang_createtable.html)
- [SQLite ALTER TABLE](https://sqlite.org/lang_altertable.html)
- [SQLite partial indexes](https://sqlite.org/partialindex.html)
- [Vercel Cron Jobs](https://vercel.com/docs/cron-jobs)
- [Vercel Cron Job management](https://vercel.com/docs/cron-jobs/manage-cron-jobs)
- [Vercel FastAPI deployment guide](https://vercel.com/kb/guide/ship-a-fastapi-app-on-vercel)

No production query or mutation was performed.

---

# 1. Exact Bounded Astra Event Schema

The following is a proposed logical contract for evaluation. It is not an
approved migration.

## Existing Reusable Fields

| Logical Field | Existing Column | Astra Rule |
|---|---|---|
| event ID | `id` | Required UUID |
| authenticated user reference | `actorUserId` | Required for authenticated personal-data attempts; backend supplied only |
| event action | `action` | Fixed namespaced value such as `astra.personal_data.tool_attempt` |
| event type | `entityType` | Fixed value such as `AstraToolExecution`; never an app record type |
| created timestamp | `createdAt` | Required server timestamp |

## Proposed Extension Fields

| Proposed Column | Type / Bound | Required For Astra | Purpose |
|---|---|---:|---|
| `auditClass` | string, 40 | Yes | Namespaces `astra_personal_data` from existing admin events |
| `correlationId` | string, 80 | Yes | One backend-issued request/session correlation reference |
| `capability` | string, 120 | Yes | Registered capability intent |
| `toolName` | string, 120 | Yes when a tool was selected | Registered tool name |
| `sourceApp` | string, 80 | Yes when app-owned | Registry owning-app key |
| `inputClassification` | string, 80 | Yes | Bounded classification, never prompt text |
| `outputClassification` | string, 80 | Yes | Bounded classification, never response text |
| `providerContextCategory` | string, 80 | No | Approved OpenAI context category or null |
| `outcome` | string, 24 | Yes | `allowed`, `denied`, `failed`, or `unavailable` |
| `reasonCode` | string, 120 | Conditional | Bounded allowlisted reason code |
| `durationBucket` | string, 24 | Yes | Bounded bucket rather than precise profiling telemetry |
| `deploymentVersion` | string, 120 | Yes | Deployed artifact/version reference |
| `eventSchemaVersion` | integer | Yes | Enables controlled event evolution |
| `expiresAt` | timestamp | Yes | Default `createdAt + 365 days`, subject to approved hold rules |

## Existing Fields Prohibited For Astra Events

| Existing Column | Astra Treatment | Reason |
|---|---|---|
| `actorEmail` | Null | Duplicates personal identity and complicates deletion/minimization |
| `entityId` | Null | App-owned record IDs must not enter operational audit |
| `entityLabel` | Null | Could contain personal record titles or names |
| `ipAddress` | Null by default | Not required by G03; separate security-purpose approval needed |
| `userAgent` | Null by default | Not required by G03; separate security-purpose approval needed |
| `metadataJson` | Null or validated bounded supplemental object only | Existing arbitrary serializer cannot be used directly |

The schema must never contain prompt text, response text, raw tool arguments,
raw tool results, owner IDs supplied by callers, app record IDs, SQL, tokens,
cookies, secrets, or stack traces.

---

# 2. Backward Compatibility

Current known writers use the generic audit helper after committing admin
application, category, or FAQ mutations.

A bounded extension can preserve those writers if:

- new columns are nullable for legacy/admin event classes or have safe constant
  defaults;
- existing column meanings are not changed;
- existing indexes remain available;
- the generic writer remains compatible;
- Astra uses a separate validated adapter rather than passing arbitrary
  metadata to the generic writer; and
- retention targets only the `astra_personal_data` class.

SQLite and Turso support adding columns, but restrictions apply to new
`NOT NULL`, `UNIQUE`, generated, default, and `CHECK` definitions. Because
existing production row count and contents have not been inspected, a migration
cannot safely assume the table is empty.

Evidence still required:

- read-only production row count and action-class inventory;
- current admin-audit retention obligation;
- migration rehearsal against a production-shaped copy;
- old writer/new schema and new writer/old row compatibility tests; and
- deployment rollback rehearsal.

---

# 3. Retention Mechanism

G03 requires 365-day default retention for Astra personal-data audit metadata.

Proposed evaluation shape:

1. set `expiresAt` deterministically when writing each Astra event;
2. run a separately governed idempotent cleanup operation;
3. delete only rows where:

   ```text
   auditClass = astra_personal_data
   AND expiresAt < current UTC time
   AND no approved hold applies
   ```

4. process bounded batches;
5. persist cleanup operational evidence without recursively producing one audit
   event per deleted audit row;
6. monitor failures and retry safely; and
7. prove admin audit rows are unaffected.

The current table has no standalone `createdAt` or expiry index. A local
read-only query plan for:

```sql
SELECT id
FROM AuditLogs
WHERE createdAt < datetime('now', '-365 days');
```

reported a full table scan.

The local database contains zero `AuditLogs` rows. This proves schema/index
behavior only; it does not prove production volume, cleanup latency, or lock
impact.

Architecture review recommendation:

- store `expiresAt` and optional `holdUntil`;
- execute daily through a `CRON_SECRET`-protected FastAPI route registered as a
  Vercel Cron Job;
- make bounded deletion idempotent and safe under duplicate or overlapping
  invocations;
- alert on failure because Vercel does not retry failed cron invocations; and
- emit one bounded cleanup summary without recursively auditing every deletion.

Batch size, duration budget, concurrency control, missed-run alert, and the
production performance objective must be implemented and proven against the
approved validation matrix.

---

# 4. Restricted Reader Access And Integrity

No audit-listing route currently exists. That prevents accidental public
listing, but it does not by itself prove an operational access model.

Minimum proposed access rules:

- no user-facing or general authenticated audit endpoint;
- no access through Activity Timeline;
- a separately approved operational reader permission;
- default-deny authorization;
- bounded filtering and pagination;
- no raw `metadataJson` response;
- no actor email, IP, user agent, or internal identifiers unless separately
  approved for the reader's purpose;
- administrative reads themselves recorded as security audit events;
- no update endpoint;
- no routine delete endpoint;
- retention and approved incident procedures are the only deletion paths; and
- database credentials remain least-privileged and server-owned.

Integrity evidence must distinguish:

- database structural integrity;
- authorization against application-level mutation;
- operational credential control;
- backup/recovery capability; and
- tamper evidence.

SQLite `CHECK`, `NOT NULL`, and uniqueness constraints can reject invalid writes,
but `CHECK` enforcement is not a complete tamper-control system. Turso
point-in-time recovery can restore a database to a prior point by creating a new
database; it is recovery evidence, not immutability or tamper evidence.

Open decisions:

- named operational reader role;
- whether the existing admin model is sufficiently narrow;
- whether read-access audit events share the same sink;
- database-token permissions available in the deployed environment;
- incident hold and recovery procedure; and
- whether additional append-only or tamper-evident controls are required.

---

# 5. Fail-Closed Transaction Behavior

## Current Behavior

`write_audit_log(..., required=True)` re-raises SQLAlchemy persistence errors.
That is a useful primitive.

The current helper also:

- adds the row;
- commits immediately;
- rolls back the session on failure; and
- refreshes after commit.

Existing admin services commit their domain mutation first and then write the
audit event. This means an audit failure cannot roll back the already committed
admin change.

## Astra Read-Only Difference

Phase 1 Astra tools are read-only. There is no app-domain mutation to make
atomic with the audit insert.

Proposed fail-closed sequence for evaluation:

```text
Authenticate and authorize
    ↓
Resolve bounded intent/tool plan
    ↓
Execute owner-scoped read-only tool
    ↓
Build bounded result classification
    ↓
Persist mandatory audit event
    ↓
Only after durable success, return the personal answer
```

If persistence fails:

- roll back the audit session;
- discard the personal answer;
- return bounded unavailable behavior;
- emit non-personal operational failure telemetry;
- do not fall back to an unaudited personal-data path; and
- do not allow OpenAI to receive the personal result.

Denied/unavailable attempts also require durable events. The architecture must
define safe behavior if even the denial event cannot be persisted. The minimum
safe response remains non-personal and unavailable, with external operational
alerting that contains no personal payload.

## Transaction Conclusion

The existing immediate-commit writer should not be called directly from Astra.
A validated Astra adapter may reuse the parent session/writer foundation, but
its event construction and fail-closed response boundary must be explicit.

No cross-database transaction is required for the current read-only tools.
Future write tools would require a new atomicity decision and are outside
I1-024.

---

# 6. Required Indexes And Investigation Queries

Required investigation patterns:

| Query | Purpose |
|---|---|
| user + descending time | Investigate one authenticated user's Astra access |
| correlation ID | Trace one Assistant request/tool plan |
| audit class + outcome + time | Find denied/failed/unavailable trends |
| capability/tool + time | Investigate one registered capability |
| expiry cutoff | Run bounded retention cleanup |

Existing evidence:

- `actorUserId, createdAt` supports the user/time pattern;
- no correlation lookup exists;
- no outcome/capability/tool lookup exists;
- retention currently scans the table.

Candidate indexes for evaluation—not approved:

```text
UNIQUE (correlationId) WHERE correlationId IS NOT NULL
(auditClass, outcome, createdAt DESC)
(auditClass, expiresAt)
(auditClass, capability, toolName, createdAt DESC)
```

One request may execute more than one tool, so correlation ID may not be unique
per event if each tool attempt is a separate row. Before choosing a unique
index, the event model must decide between:

- one request event with bounded tool summaries;
- one request event plus child/tool-attempt events; or
- multiple tool-attempt events sharing a correlation ID.

Therefore uniqueness remains unresolved.

## Synthetic Query-Plan Evidence

An in-memory SQLite model with 100,000 synthetic rows (25,000 Astra-class rows)
was used only to compare query plans.

After candidate indexes:

- correlation lookup used its index and returned one synthetic row;
- class/outcome/time lookup used the composite index without a temporary sort;
- actor/time lookup used the existing-equivalent composite index;
- retention used an available class index in the first experiment;
- a focused second experiment confirmed both a partial expiry index and
  `(auditClass, expiresAt)` can produce indexed expiry searches after `ANALYZE`.

Illustrative timings were sub-15 ms on the local in-memory experiment, but they
are not production performance evidence and must not become an SLO.

Required next evidence:

- exact event cardinality model;
- production volume estimate;
- target Turso query plans;
- write-amplification assessment;
- cleanup batch plans;
- concurrency/lock behavior; and
- measured latency in a production-shaped governed environment.

---

# 7. Turso / libSQL And Deployment Compatibility

Confirmed from primary documentation:

- the repository's remote SQLAlchemy URL pattern is supported by Turso's
  SQLAlchemy guidance;
- Turso supports `ALTER TABLE` rename/add/drop forms;
- adding constrained columns has compatibility restrictions;
- SQLite/libSQL supports indexes and partial indexes;
- transactions are supported;
- write transactions can serialize/lock, so retention batching and index cost
  need target-environment measurement; and
- Turso point-in-time recovery creates a new database and requires application
  connection changes, so rollback cannot be described as an in-place rewind.

Repository-specific unresolved issue:

```text
The current Windows/Python 3.13 environment cannot install
libsql-experimental==0.0.55 from a compatible wheel and source build requires
the MSVC linker.
```

This does not reject Option B, but G10 remains open until the supported
deployment/runtime matrix installs and runs reproducibly.

Required compatibility evidence:

- clean installation in the actual deployment image;
- migration rehearsal against Turso/libSQL;
- index creation and query plans on the target engine;
- audit write/commit/failure behavior through `sqlalchemy-libsql`;
- retention batching under concurrent application traffic;
- backup/PITR rehearsal;
- Vercel deployment and rollback proof; and
- safe default feature-gate verification.

---

# 8. Complete Focused Test Strategy

## Event Contract

- accepts every required allowed value;
- rejects unknown outcome, classification, reason, duration, and audit class;
- enforces field lengths;
- rejects raw prompts, responses, arguments, results, record IDs, SQL, secrets,
  and unrestricted metadata;
- omits actor email, entity label/ID, IP, and user agent for Astra events;
- applies schema version and expiry deterministically.

## Coverage

- allowed attempt creates one correct durable event;
- denied attempt creates one correct durable event;
- failed attempt creates one correct durable event;
- unavailable attempt creates one correct durable event;
- Quiz, Course Tracker, and Learning Intelligence plans are covered;
- maximum two-tool composition produces the approved event cardinality;
- no public/identity/safety question creates unnecessary personal-data events.

## Authentication And Isolation

- unauthenticated requests fail closed;
- backend identity is authoritative;
- caller/model owner IDs are rejected or ignored before execution;
- two users create isolated audit references;
- audit readers cannot select unauthorized users;
- account switching and logout do not reuse stale identity.

## Failure Behavior

- insert failure discards the personal answer;
- commit failure rolls back and returns bounded unavailable behavior;
- refresh/readback failure is classified safely;
- audit database timeout does not fall through to unaudited execution;
- logging/monitoring excludes personal payloads;
- OpenAI receives no personal result after audit failure.

## Backward Compatibility

- existing admin writers still persist unchanged events;
- legacy rows remain readable;
- new Astra constraints do not reject legacy event creation;
- Astra retention never deletes non-Astra rows;
- existing indexes and admin behavior remain stable.

## Retention

- exactly expired Astra rows are selected;
- unexpired rows remain;
- admin rows remain;
- approved holds remain;
- batching is deterministic and idempotent;
- partial failure retries safely;
- cleanup evidence is bounded;
- 365-day boundary uses UTC consistently.

## Access And Integrity

- public and ordinary authenticated access is absent/denied;
- only approved operational role can read;
- reads are bounded and paginated;
- prohibited columns are never serialized;
- no update or routine-delete API exists;
- audit-reader access is itself observable;
- integrity/recovery checks follow the approved runbook.

## Migration And Performance

- upgrade from production-shaped legacy schema;
- downgrade/rollback behavior according to approved migration policy;
- legacy data preservation;
- required indexes exist;
- target query plans use intended indexes;
- write and investigation latency meet approved objectives;
- retention batching does not exceed approved lock/latency objectives.

## Deployment

- clean target-runtime dependency installation;
- migration in governed environment;
- safe default flag remains false;
- audit failure monitoring works;
- deployment rollback works;
- no production enablement occurs during I1-024 implementation validation.

---

# 9. Separation-Of-Concerns Assessment

Option B can preserve separation of concerns only if:

- `AuditLogs` is formally the parent/global operational audit system;
- Activity Timeline remains product journey history;
- app databases remain sources of app facts;
- Astra contributes a typed event adapter, not a parallel audit framework;
- generic admin audit behavior remains compatible;
- event classes have explicit retention and access rules;
- the sink stores operational evidence, not analytics or raw observability; and
- audit reads and lifecycle operations remain backend-owned.

Option B violates separation of concerns if the extension turns `AuditLogs` into
an undifferentiated store for Activity, analytics, raw logs, conversations,
model payloads, or app-owned history.

Current assessment:

```text
Bounded extension can be coherent in principle.
Repository and platform evidence are not yet sufficient for acceptance.
```

---

# 10. Evidence Conclusion

Repository-level evidence supports these conclusions:

1. unchanged reuse cannot satisfy G03;
2. a bounded extension has a credible separation-of-concerns model;
3. backward compatibility is possible in principle through nullable/classed
   additions and a dedicated validated Astra adapter;
4. the current writer cannot be used directly for Astra;
5. a retention/index/access/integrity design is mandatory;
6. local query-plan evidence supports indexed investigation patterns but does
   not prove target performance;
7. current evidence does not justify a dedicated store; and
8. Option B remains unproven until production-shaped volume, target-runtime,
   migration, transaction, access, and operational evidence is reviewed.

Architecture decision:

```text
OPTION B ACCEPTED
```

Target deployment, migration, performance, retention, failure, and recovery
evidence remains required during implementation and verification.
