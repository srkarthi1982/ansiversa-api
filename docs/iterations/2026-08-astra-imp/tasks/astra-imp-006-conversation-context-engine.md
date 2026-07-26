# ASTRA-IMP-006 — Conversation Context Engine

**Status:** Implemented / Pending Astra Source Review
**Parent Constitution:** ASTRA-001 through ASTRA-010 Accepted / Frozen
**Parent Readiness:** ASTRA-IR-001 Accepted / Frozen
**Parent Implementations:** ASTRA-IMP-001 through ASTRA-IMP-005 Certified / Approved
**Implementation Authorization:** Approved
**Implementation Scope:** Conversation Context Engine
**Production Authorization:** Not approved
**Production:** Unchanged
**ASTRA-IMP-007:** Not authorized

---

# Objective

Implement a provider-independent Conversation Context Engine owned by the
certified Runtime Core.

The engine represents bounded current-session conversation context only.

---

# Deliverables

- immutable conversation metadata;
- explicit lifecycle states;
- current-turn metadata model;
- bounded short-context history;
- runtime ownership enforcement;
- governance evidence emission through Runtime Core;
- structural health snapshot;
- focused tests;
- implementation review package;
- lifecycle documentation;
- context model documentation;
- Constitution-to-code mapping;
- AGENTS and iteration tracking.

---

# Boundary

Explicitly not included:

- LLM providers;
- prompts;
- model invocation;
- planning;
- execution;
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
- modification of certified ASTRA-IMP-001 through ASTRA-IMP-005 behavior.

---

# Final Draft State

```text
ASTRA-IMP-006               Implemented
Implementation Scope        Conversation Context Engine
Implementation Direction    Pending Astra Source Review
Constitutional Conformance  Pending
Product Owner Approval      Pending
Certification               Pending

Production Authorization    Not approved
Production                  Unchanged

ASTRA-IMP-007               Not authorized
Requires separate authorization
```
