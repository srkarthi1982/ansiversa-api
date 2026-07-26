# ADR: ASTRA-IMP-005 Astra Runtime Core

**Status:** Proposed
**Date:** 2026-07-26
**Task:** ASTRA-IMP-005
**Production Authorization:** Not approved
**Production:** Unchanged

---

# Context

ASTRA-IMP-001 through ASTRA-IMP-004 certified the constitutional contracts,
configuration foundation, governance kernel, and evidence sink. Those
foundations remained independent components.

Before conversation, capability discovery, planning, providers, memory, or
execution are implemented, Astra needs a minimal runtime owner that establishes
identity and lifecycle without adding intelligence or production behavior.

---

# Decision

Implement `AstraRuntime` as an internal runtime owner under
`app/modules/astra_ai/runtime.py`.

The runtime:

- exposes immutable runtime identity metadata;
- manages explicit lifecycle states;
- starts from certified configuration;
- registers only configuration, governance, and evidence sink components;
- exposes read-only component access while ready;
- emits structural health snapshots;
- records bounded fault metadata;
- fails closed on invalid transitions or startup failures.

---

# Consequences

Future Astra implementation phases can integrate with a single internal runtime
owner instead of constructing direct lifecycle dependencies between higher
components.

The runtime remains non-authorizing. It does not create providers, prompts,
memory, planning, execution, APIs, routes, persistence, deployment, production
configuration, or production behavior.

---

# Review State

```text
ASTRA-IMP-005               Implemented
Implementation Direction    Pending Astra Source Review
Constitutional Conformance  Pending
Product Owner Approval      Pending
Certification               Pending
Production Authorization    Not approved
Production                  Unchanged
ASTRA-IMP-006               Not authorized
```
