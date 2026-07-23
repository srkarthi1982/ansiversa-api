# Architecture Decision: Astra Persistent Audit Storage

**Status:** Accepted
**Created:** 2026-07-23
**Accepted:** 2026-07-23
**Task:** I1-024
**Decision Owner:** Karthikeyan Ramalingam
**Architecture Reviewer:** Astra
**Evidence Agent:** Codex

This repository had no existing ADR directory, numbering sequence, template, or
filename convention when this draft was created. The record therefore uses a
descriptive filename and does not claim an ADR number.

Option B is the accepted architecture. Implementation remains unauthorized.

---

# Decision To Make

Where should Astra persist mandatory personal-data tool audit events?

The formal decision must answer:

> Can the existing parent-owned `AuditLogs` system satisfy G03 through a
> bounded, backward-compatible extension without violating separation of
> concerns?

The options under review are:

1. reuse `AuditLogs` without schema changes;
2. extend `AuditLogs` while preserving one parent-owned audit system; or
3. create a dedicated Astra audit store.

“Reuse first” is an evaluation principle, not a predetermined conclusion.

The detailed Option B evidence dossier is:

```text
docs/iterations/2026-07-next/i1-024-option-b-evidence.md
```

The six-decision architecture review recommendation is:

```text
docs/iterations/2026-07-next/i1-024-architecture-decision-review.md
```

---

# Decision Principle

## Astra Engineering Law #7

> Every implementation must explicitly resolve the decisions that would be
> expensive to reverse later.

Audit persistence is such a decision because it determines schema ownership,
retention enforcement, access control, incident evidence, deployment behavior,
and the long-term operational boundary for every Astra personal-data
capability.

---

# Status Boundary

```text
Repository evidence       Collected
Target environment evidence Required during implementation and verification
Architecture decision     Option B accepted
I1-024 status             Frozen
Implementation            Not authorized
Production enablement     Disabled
Production authorization  Not granted
```

Acceptance freezes the architecture and validation plan. It does not authorize
implementation or assert that implementation evidence exists.

---

# Governing Requirements

The selected design must satisfy G03 in
`docs/astra-operational-readiness-specification.md`.

Every personal-data tool attempt must durably record bounded metadata for:

- allowed;
- denied;
- failed; and
- unavailable outcomes.

Required event concepts:

- event ID
- timestamp
- authenticated user reference
- request or session correlation reference
- capability
- tool name
- source application
- input classification
- output classification
- OpenAI personal-context category, when used
- outcome
- bounded reason code
- duration bucket
- deployed version

The sink must not store:

- raw prompts;
- raw Assistant responses;
- raw personal records;
- authentication tokens, cookies, or claims;
- SQL;
- secrets;
- stack traces; or
- unrestricted arbitrary metadata.

It must also support restricted operational access, integrity, 365-day default
retention, observable failure, and fail-closed behavior when mandatory
persistence cannot be confirmed.

---

# Repository Evidence

## Existing Audit Model

Location:

```text
app/modules/audit/models.py
```

`AuditLog` is a parent-database model mapped to `AuditLogs`.

Current fields:

| Field | Current Purpose | G03 Observation |
|---|---|---|
| `id` | UUID event identifier | Reusable |
| `actorUserId` | Optional authenticated actor FK | Potentially reusable; deletion semantics need review |
| `actorEmail` | Optional actor email snapshot | Unnecessary personal duplication for Astra and potentially conflicts with minimization |
| `action` | Bounded action string | Could encode an Astra event family |
| `entityType` | Bounded entity type | Could represent capability/source, but semantics need definition |
| `entityId` | Optional entity reference | Raw app record IDs must not be used for Astra |
| `entityLabel` | Optional label | Personal labels should be prohibited for Astra audit events |
| `metadataJson` | Arbitrary serialized metadata | Does not currently enforce the G03 allowlist |
| `ipAddress` | Optional request IP | Security value and privacy/retention implications require explicit classification |
| `userAgent` | Optional user agent | Security value and privacy/retention implications require explicit classification |
| `createdAt` | Server timestamp | Reusable |

Existing indexes:

- `actorUserId, createdAt`
- `entityType, entityId`

Missing or unproven for G03:

- correlation lookup;
- capability/tool/outcome/time lookup;
- retention deletion by timestamp at expected scale;
- explicit event schema version;
- deployed-version lookup;
- bounded outcome/reason fields;
- immutable/integrity controls beyond ordinary database permissions.

## Existing Audit Writer

Location:

```text
app/modules/audit/service.py
```

`write_audit_log(...)`:

- writes to the parent database;
- accepts an authenticated actor;
- records action/entity fields;
- serializes arbitrary metadata;
- optionally captures request IP and user agent;
- commits immediately;
- rolls back and returns `None` on SQLAlchemy failure by default; and
- re-raises when `required=True`.

G03 implications:

- `required=True` provides a useful fail-closed primitive;
- arbitrary metadata needs a dedicated validated Astra contract;
- independent commit behavior requires transaction-boundary analysis;
- actor email, IP address, and user agent must not be included by default
  without an approved classification and purpose;
- failure handling must produce bounded application behavior;
- the generic writer alone does not prove complete Astra audit coverage.

## Existing Migration

Location:

```text
migrations/parent/versions/29cde1832712_add_audit_logs_table.py
```

The migration creates the parent-compatible `AuditLogs` table and its two
indexes. It contains no Astra fields, retention mechanism, partitioning, or
archive/delete process.

## Existing Uses

The writer is used by approved admin write services for:

- applications;
- categories; and
- FAQs.

This proves that `AuditLogs` is already a shared parent operational audit
capability rather than an Astra-owned store.

It also means an incompatible Astra-specific reinterpretation of generic
columns could affect established admin audit semantics.

## Existing Access Surface

Repository documentation states that audit-log listing remains deferred.

Current evidence does not identify:

- a protected audit-listing API;
- a permissions registry for audit readers;
- administrative audit access logging;
- a retention execution job; or
- an Astra-specific operational review surface.

Absence of a user-facing listing API is not itself a G03 failure, but restricted
operational access and retention enforcement must be designed and proven.

## Existing Test Evidence

No focused tests referencing `AuditLog` or `write_audit_log` were found under
`tests/` during I1-024 evidence collection.

Existing admin tests may indirectly exercise writers, but that is not sufficient
evidence for G03 event completeness, minimization, failure behavior, retention,
or owner isolation.

## Activity Timeline Boundary

The Activity module and platform story explicitly state that Activity Timeline
is not an audit log and is separate from operational `AuditLogs`.

Therefore Activity Timeline is not a candidate persistent audit sink for
I1-024.

---

# Evaluation Criteria

Each option must be scored through evidence against:

| Criterion | Question |
|---|---|
| G03 completeness | Can it represent every mandatory event and field safely? |
| Separation of concerns | Does ownership remain parent/global without mixing product activity and security audit semantics? |
| Data minimization | Can Astra fields be allowlisted without storing raw payloads or unnecessary personal data? |
| Fail-closed behavior | Can mandatory audit failure block personal-data execution safely? |
| Integrity | Can unauthorized mutation/deletion be prevented and operational access recorded? |
| Retention | Can 365-day retention be enforced and verified without harming other audit classes? |
| Queryability | Can operational investigations find events by user, correlation, capability, tool, outcome, and time? |
| Migration impact | What schema/index/data migration is required? |
| Transaction behavior | Can audit durability be guaranteed without unsafe partial application behavior? |
| Operational complexity | What deployment, monitoring, cleanup, and incident burden is added? |
| Compatibility | Does it preserve existing admin audit behavior and parent database boundaries? |
| Testability | Can deterministic success/failure/retention/isolation tests prove the design? |
| Long-term maintenance | Does the design avoid duplicated audit frameworks and divergent policy? |
| Portability | Does it remain compatible with the supported Turso/libSQL and future database direction? |

---

# Option A — Reuse `AuditLogs` Without Schema Changes

## Shape

Use the current table and indexes. Add a validated Astra-specific service that
maps G03 concepts into the existing `action`, `entityType`, and
`metadataJson` fields.

## Advantages

- no new table;
- no schema migration;
- immediate reuse of a parent-owned audit capability;
- one operational audit location;
- existing `required=True` failure primitive;
- lowest infrastructure expansion.

## Disadvantages

- mandatory fields would remain embedded in JSON;
- database constraints cannot enforce outcome or schema version;
- existing arbitrary metadata writer remains unsafe for direct Astra use;
- correlation, capability, tool, outcome, and retention queries may be
  inefficient without new indexes;
- `actorEmail`, `entityLabel`, IP, and user-agent defaults could undermine
  minimization;
- generic field semantics may become overloaded;
- 365-day Astra retention may conflict with admin-audit retention if both share
  undifferentiated rows;
- integrity and restricted-read controls remain unresolved.

## Separation Of Concerns

Potentially acceptable if Astra events are a clearly namespaced class within a
general parent audit system and are written only through a validated Astra
adapter.

Potentially unacceptable if generic columns become undocumented Astra schema
surrogates or if Astra retention affects unrelated admin events.

## Migration Impact

No table migration, but a data/index migration may still become necessary after
performance evidence. Claiming “no migration” before query-plan evidence would
be premature.

## Operational Complexity

Lowest initial storage complexity, but JSON-only querying and mixed retention
could move complexity into application code and operations.

## Current Evidence Assessment

The existing infrastructure does **not** satisfy G03 as-is. Mandatory fields
would remain arbitrary JSON, retention scans are unaddressed, and access,
integrity, compatibility, and focused test evidence are missing.

Option A is rejected in principle. This does not select Option B.

---

# Option B — Extend `AuditLogs`

## Shape

Preserve one parent-owned audit system while adding explicit audit-class and
operational fields/indexes needed for Astra and future platform audits.

Possible concepts to evaluate—not approved schema:

- audit class/domain;
- correlation reference;
- capability/tool;
- outcome/reason code;
- input/output classification;
- provider-context category;
- duration bucket;
- deployed version;
- schema version; and
- retention class or expiry timestamp.

## Advantages

- retains one backend-owned audit system;
- makes mandatory G03 fields queryable and constrainable;
- supports explicit retention classes;
- can improve future security and platform audits beyond Astra;
- avoids a parallel Astra audit framework;
- preserves parent/global ownership.

## Disadvantages

- requires a parent migration;
- risks making `AuditLogs` a broad catch-all table;
- existing admin writers and schemas need compatibility review;
- nullable additions may weaken enforcement unless event-class constraints are
  carefully designed;
- shared-table retention and access rules become more complex;
- Turso/libSQL constraint and index behavior must be verified.

## Separation Of Concerns

Strong if `AuditLogs` is formally defined as the platform operational audit
system with typed event classes and controlled adapters.

Weak if the extension mixes product analytics, Activity Timeline, raw
observability, and security evidence in one undifferentiated model.

## Migration Impact

Requires a separately approved parent migration and backward-compatible model
changes. Existing rows and writers must continue to function.

## Operational Complexity

Moderate. One store remains, but schema evolution, retention classes, access,
and query patterns require deliberate governance.

## Current Evidence Assessment

Option B appears capable of closing more G03 gaps than unchanged reuse while
preserving one audit system. Repository evidence now proposes a bounded event
contract, prohibited fields, compatibility conditions, retention shape,
access/integrity requirements, fail-closed behavior, investigation queries,
candidate indexes, platform constraints, and a focused test strategy.

Production-shaped volume, target Turso query plans, migration rehearsal,
runtime dependency compatibility, operational access, retention execution, and
deployment evidence remain unproven. No acceptance or rejection is recorded.

---

# Option C — Dedicated Astra Audit Store

## Shape

Create a separate parent-owned table or isolated database/store dedicated to
Astra personal-data execution audit events.

## Advantages

- exact G03 schema and constraints;
- independent retention and access policy;
- clear Astra event semantics;
- focused indexes and operational queries;
- reduced risk of changing established admin audit behavior;
- potential isolation of high-value security evidence.

## Disadvantages

- duplicates audit storage, services, retention, access, and monitoring
  concerns;
- introduces new migration and operational infrastructure;
- risks divergent policy between platform and Astra audits;
- complicates investigations that span admin and Astra events;
- increases maintenance and future consolidation cost;
- may violate “build infrastructure once” without strong evidence.

## Separation Of Concerns

Strong only if Astra audit requirements are materially incompatible with the
platform audit domain or require isolation that `AuditLogs` cannot provide.

Weak if it merely avoids extending an existing shared capability.

## Migration Impact

Requires a new table or database, indexes, service, retention process, access
surface, monitoring, and deployment verification.

## Operational Complexity

Highest of the three options.

## Current Evidence Assessment

No current repository evidence proves that a dedicated store is necessary.
Option C must not be selected unless Options A and B are shown unable to satisfy
G03 safely.

No final rejection is recorded because architecture evidence collection is not
complete.

---

# Comparative Evidence Matrix

Scores are deliberately not assigned until the open evidence is collected.

| Criterion | Option A: Reuse | Option B: Extend | Option C: Dedicated |
|---|---|---|---|
| G03 completeness | Fails as-is | Logical contract proposed; target proof pending | Unproven |
| Separation of concerns | Generic reuse would overload fields | Coherent in principle under typed parent-audit boundary | Unproven |
| Data minimization | Arbitrary metadata and identity fields fail current requirement | Prohibited-field contract proposed; implementation proof pending | Unproven |
| Fail-closed behavior | Partial primitive exists | Partial primitive exists | New design required |
| Integrity | Unproven | Requirements defined; control proof pending | Unproven |
| 365-day retention | Missing | New design required | New design required |
| Queryability | Local plans show retention scan and missing lookups | Candidate indexes validated synthetically; target proof pending | Can be designed |
| Migration impact | Lowest | Moderate | Highest |
| Existing compatibility | Highest potential | Requires proof | Separate but duplicative |
| Operational complexity | Lowest storage count | Moderate | Highest |
| Focused test evidence | Missing | Missing | Missing |
| Long-term maintenance | Risk of JSON complexity | Risk of catch-all model | Risk of duplicated infrastructure |

---

# Evidence Lifecycle

The architecture review recommendation resolves the pre-freeze design:

- event cardinality, schema, and reason taxonomy;
- prohibited fields;
- retention mechanism and execution owner;
- operational-reader and integrity boundaries;
- fail-closed response handling;
- candidate indexes;
- migration and rollback strategy; and
- implementation validation matrix.

The following are implementation and verification evidence, not circular
preconditions for architecture selection:

- production-shaped audit volume and retention performance;
- migration and application-rollback rehearsal;
- target Turso/libSQL query plans;
- deployed-driver write and failure behavior;
- real retention execution, concurrency, and missed-run handling;
- governed deployment and dependency compatibility;
- backup/point-in-time recovery rehearsal; and
- proof that the production flag remains safely disabled.

---

# Decision Conditions

## Select Option A only if

- all G03 concepts can be safely and deterministically represented;
- a validated adapter prohibits arbitrary/raw metadata;
- query plans meet the approved objective without schema/index changes;
- Astra retention can be enforced without harming other event classes;
- access and integrity controls are proven; and
- existing admin audit semantics remain unchanged.

## Select Option B only if

- explicit schema/index extensions materially improve G03 enforcement;
- one platform audit system remains a coherent responsibility;
- existing writers and rows remain backward compatible;
- retention classes and access policies can coexist safely; and
- migration/runtime compatibility is proven.

## Select Option C only if

- evidence proves the shared audit system cannot satisfy G03 safely;
- required isolation or lifecycle rules are materially incompatible;
- duplicated infrastructure is explicitly accepted;
- cross-audit investigation and governance are designed; and
- operational ownership is funded and assigned.

---

# Decision

```text
Option A — Unchanged reuse          Rejected in principle
Option B — Bounded extension        ACCEPTED
Option C — Dedicated Astra store    Rejected; not justified by evidence

Final architecture decision         OPTION B
```

Option A is rejected because the unchanged schema, arbitrary metadata writer,
retention behavior, access/integrity model, queryability, and focused test
evidence do not satisfy G03.

The Architecture Reviewer approved all six design decisions. Karthikeyan
Ramalingam accepted Option B as Product Owner on 2026-07-23.

Option A is rejected because unchanged reuse cannot satisfy G03. Option C is
rejected because no evidence establishes that a separate store is necessary;
it would duplicate platform audit infrastructure and operational policy.
Implementation and verification evidence is not a circular precondition for
architecture freeze.

---

# Consequences

`AuditLogs` remains the parent-owned operational audit system. Astra must use a
dedicated validated adapter and the frozen typed event contract. Activity
Timeline, analytics, raw observability, conversations, and application records
remain outside this store.

No migration, service change, framework integration, retention job, access API,
feature-flag change, or production enablement is authorized by this record.

---

# Review Checklist

- [x] Exact G03 logical event schema proposed for review
- [x] Prohibited metadata rules approved
- [x] Retention design approved
- [x] Access and integrity model approved
- [x] Fail-closed transaction behavior proposed for review
- [x] Local and synthetic query-plan evidence collected
- [x] Primary Turso/libSQL compatibility constraints documented
- [x] Migration and rollback strategy approved
- [x] Test strategy approved
- [x] One option selected with evidence
- [x] Rejected options receive explicit rationale
- [x] I1-024 frozen only after ADR acceptance
