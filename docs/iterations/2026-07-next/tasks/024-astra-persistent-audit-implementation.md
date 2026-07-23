# I1-024 — Astra Persistent Audit Implementation

**Iteration:** 2026-07-next
**Priority:** Critical
**Status:** Frozen
**Depends On:** I1-023
**Primary Repository:** `ansiversa-api`
**Current Authorization:** Evidence collection and ADR drafting only

---

# Objective

Define, review, freeze, implement, and verify the durable backend-owned audit
control required by G03 before Astra personal-data tools may be considered for
production.

The current phase is planning only.

Architecture and scope are frozen. Implementation is not authorized.

---

# Expensive-To-Reverse Decision

I1-024 must first decide:

> Where is the permanent audit sink for Astra personal-data tool execution?

The evidence-driven architecture draft is:

```text
docs/architecture/decisions/astra-persistent-audit-storage.md
```

The Option B evidence dossier is:

```text
docs/iterations/2026-07-next/i1-024-option-b-evidence.md
```

The repository had no prior ADR directory or numbering convention. The draft
therefore uses a descriptive filename and does not claim `ADR-001`.

---

# Options Under Review

## Option A

Reuse existing `AuditLogs` without schema changes.

## Option B

Extend `AuditLogs` while preserving one parent-owned operational audit system.

## Option C

Create a dedicated Astra audit store only if evidence proves the shared audit
system cannot satisfy G03 safely.

Option B is selected through the accepted architecture decision.

---

# Questions To Resolve

1. Can the parent-owned `AuditLogs` system satisfy G03 through a bounded,
   backward-compatible extension?
2. What metadata must be stored?
3. What must never be stored?
4. How is audit integrity protected?
5. What happens when mandatory persistence fails?
6. How is 365-day retention enforced?
7. What migration is required, if any?
8. How is the selected design tested?

Additional evidence must resolve access control, actor deletion semantics,
transaction boundaries, query patterns, runtime compatibility, monitoring, and
existing admin-audit compatibility.

---

# Current Repository Evidence

The existing foundation provides:

- parent-owned `AuditLogs`;
- UUID event IDs;
- actor/action/entity/timestamp fields;
- arbitrary JSON metadata;
- optional IP and user agent;
- two indexes;
- reusable `write_audit_log(...)`;
- optional `required=True` exception behavior; and
- existing admin app/category/FAQ writer integrations.

Current G03 gaps include:

- no validated Astra event contract;
- no required correlation, capability, tool, outcome, classification, reason,
  duration, or deployed-version fields;
- arbitrary metadata serialization;
- no proven 365-day retention enforcement;
- no focused audit test coverage;
- deferred audit listing/access model;
- unproven integrity and reader-access controls;
- unproven investigation-query performance; and
- unproven fail-closed Assistant behavior.

Activity Timeline is explicitly not an audit log and is not a candidate sink.

Repository-level Option B evidence now defines:

- a proposed exact logical event schema;
- existing fields prohibited for Astra events;
- backward-compatibility conditions;
- a 365-day retention shape;
- restricted reader and integrity requirements;
- fail-closed transaction behavior;
- investigation queries and candidate indexes;
- local and synthetic query-plan evidence;
- Turso/libSQL compatibility constraints; and
- a complete focused test strategy.

This evidence supports the accepted Option B architecture. Production-shaped
volume, target Turso query plans, migration rehearsal, runtime dependency
compatibility, operational-access implementation, retention execution, and
deployment evidence remain pending for implementation and verification.

---

# Planning Deliverables

Before freeze:

- accepted architecture decision record;
- approved six-decision architecture review;
- exact bounded event schema;
- field classification and prohibited-data contract;
- writer and transaction behavior;
- access and integrity model;
- retention mechanism;
- migration decision;
- query/index evidence plan;
- monitoring and failure behavior;
- compatibility assessment; and
- complete validation matrix.

---

# Potential Implementation Scope

This section is provisional and does not authorize work.

When separately authorized for implementation, I1-024 may include only:

- the accepted persistent audit model;
- a validated Astra audit event contract;
- durable writer integration around personal-data tool attempts;
- mandatory fail-closed behavior;
- approved migration/index changes;
- 365-day retention enforcement;
- restricted operational access required by G03;
- monitoring for persistence failure;
- focused unit, integration, isolation, failure, and retention tests; and
- evidence documentation.

---

# Non-Goals

I1-024 does not include:

- consent or preference UI;
- general retention/deletion/export implementation outside audit metadata;
- persistent Astra memory;
- write tools;
- proactive personal-data use;
- governed test-account creation;
- controlled production enablement;
- production launch;
- new app onboarding;
- Activity Timeline changes; or
- App #101.

---

# Freeze Criteria

I1-024 moved from `Discussing` to `Frozen` after:

- the ADR is accepted;
- the selected/rejected option rationale is complete;
- exact schema and prohibited fields are approved;
- retention and access behavior are approved;
- fail-closed semantics are approved;
- migration and compatibility impact are understood;
- validation requirements are executable;
- Product Owner authorizes implementation; and
- architecture review approves the frozen boundary.

---

# Current Status

```text
Planning                    Completed
Repository evidence         Approved
ADR                         Accepted
Architecture review         Approved
Frozen scope                Yes
Implementation authorized   No
Production flag             false
Production authorization    No
```

No runtime behavior, schema, configuration, deployment, or production state is
changed by the current I1-024 planning phase.
