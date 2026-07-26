# Astra Minimal Evidence Sink

**Status:** Implemented
**Task:** ASTRA-IMP-004
**Parent Constitution:** ASTRA-001 through ASTRA-010 Accepted / Frozen
**Parent Readiness:** ASTRA-IR-001 Accepted / Frozen
**Parent Implementations:** ASTRA-IMP-001, ASTRA-IMP-002, and ASTRA-IMP-003 Certified / Approved
**Implementation Scope:** Minimal Evidence Sink
**Implementation Direction:** Pending Astra Source Review
**Constitutional Conformance:** Pending
**Product Owner Approval:** Pending
**Certification:** Pending
**Production Authorization:** Not approved
**Production:** Unchanged
**ASTRA-IMP-005:** Not authorized

---

# Purpose

ASTRA-IMP-004 implements the Stage 3 Minimal Evidence Sink from ASTRA-IR-001.

The sink receives certified `BoundedEvidence` emitted by prior Astra
foundations and keeps it in a bounded in-memory collection for deterministic
inspection.

It receives only. It does not decide, authorize, execute, persist, publish
events, expose APIs, write audit records, access databases, or change production
behavior.

---

# Discovery Findings

Codex inspected:

- `app/modules/astra_ai/constitutional_contracts.py`, which provides certified
  `BoundedEvidence`, evidence integrity, correction metadata, minimization,
  retention, redaction, and prohibited-material validation.
- `app/modules/astra_ai/configuration.py`, which provides the certified
  disabled authoritative Astra configuration.
- `app/modules/astra_ai/governance.py`, which emits bounded governance
  evidence from the certified Minimal Governance Kernel.
- `app/modules/audit/service.py`, which is database-backed persistent audit
  storage and is not imported or reused by ASTRA-IMP-004.

No frozen constitutional decision needed to change.

---

# Placement And Ownership

The implementation lives at:

```text
app/modules/astra_ai/evidence_sink.py
```

Ownership:

- ASTRA-IMP-004 owns only the in-memory evidence receiver.
- ASTRA-IMP-001 owns the evidence contracts.
- ASTRA-IMP-002 owns authoritative configuration.
- ASTRA-IMP-003 owns governance decisions and evidence emission.
- Existing audit storage remains separate and is not used by this sink.

---

# Evidence Sink Surface

The sink exposes only internal methods:

```text
append(evidence)
retrieve()
count()
```

Rules:

- append accepts only certified `BoundedEvidence`;
- evidence is revalidated before storage;
- duplicate evidence identifiers are rejected;
- capacity overflow fails deterministically;
- retrieval returns an immutable tuple of copy-safe evidence objects;
- insertion order is preserved;
- correction metadata is preserved;
- correction links require an existing predecessor;
- self-superseding corrections are rejected;
- cyclic correction chains are rejected;
- original evidence remains unchanged and retrievable.

---

# Boundary

ASTRA-IMP-004 does not introduce:

- Audit Engine;
- persistent evidence storage;
- database access;
- migrations;
- event streaming;
- observability platform;
- providers or provider SDKs;
- provider keys;
- prompts;
- model invocation;
- planning;
- execution;
- Tool Executor changes;
- memory;
- learning;
- APIs;
- routes;
- frontend changes;
- deployment changes;
- production configuration changes;
- production activation.

Receiving evidence never authorizes action.

---

# Final Implementation State

```text
ASTRA-IMP-004               Implemented
Implementation Scope        Minimal Evidence Sink
Implementation Direction    Pending Astra Source Review
Constitutional Conformance  Pending
Product Owner Approval      Pending
Certification               Pending

Production Authorization    Not approved
Production                  Unchanged

ASTRA-IMP-005               Not authorized
```
