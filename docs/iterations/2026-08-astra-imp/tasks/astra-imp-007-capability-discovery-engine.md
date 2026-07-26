# ASTRA-IMP-007 — Capability Discovery Engine

**Status:** Implemented / Pending Astra Source Review
**Parent Constitution:** ASTRA-001 through ASTRA-010 Accepted / Frozen
**Parent Readiness:** ASTRA-IR-001 Accepted / Frozen
**Parent Implementations:** ASTRA-IMP-001 through ASTRA-IMP-006 Certified / Approved
**Implementation Authorization:** Approved
**Implementation Scope:** Capability Discovery Engine
**Production Authorization:** Not approved
**Production:** Unchanged
**ASTRA-IMP-008:** Not authorized

---

# Objective

Implement a provider-independent Capability Discovery Engine owned by the
certified Runtime Core.

The engine discovers capability metadata only. It does not execute
capabilities or create plans.

---

# Deliverables

- immutable capability metadata model;
- sealed internal registry;
- deterministic discovery ordering;
- duplicate capability rejection;
- unknown capability rejection;
- Runtime-owned component registration;
- governance evidence emission through Runtime Core;
- conversation-scoped informational discovery;
- structural capability health;
- focused tests;
- implementation review package;
- capability model documentation;
- registry diagram;
- Constitution-to-code mapping;
- AGENTS and iteration tracking.

---

# Boundary

Explicitly not included:

- tool execution;
- planning;
- providers;
- prompts;
- model invocation;
- Tool Executor;
- long-term memory;
- learning;
- embeddings;
- vector databases;
- APIs;
- routes;
- frontend changes;
- databases;
- migrations;
- deployment;
- production activation;
- edits to ASTRA-001 through ASTRA-010;
- edits to ASTRA-IR-001;
- weakening certified ASTRA-IMP-001 through ASTRA-IMP-006 behavior.

---

# Final Draft State

```text
ASTRA-IMP-007               Implemented
Implementation Scope        Capability Discovery Engine
Implementation Direction    Pending Astra Source Review
Constitutional Conformance  Pending
Product Owner Approval      Pending
Certification               Pending

Production Authorization    Not approved
Production                  Unchanged

ASTRA-IMP-008               Not authorized
Requires separate authorization
```
