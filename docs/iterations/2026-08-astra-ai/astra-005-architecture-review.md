# ASTRA-005 Architecture Review Package

**Status:** Proposed
**Created:** 2026-07-25
**ADR:** Proposed
**Product Owner Authorization:** Approved for documentation and architecture only
**Architecture Direction:** Approved
**Architecture Review:** Minor revisions applied; pending Astra re-review
**Product Owner Approval:** Pending
**Implementation:** Not authorized
**Production:** Unchanged

---

# Review Subject

ASTRA-005 proposes the Execution Planning and Action Governance architecture
for Astra AI:

```text
docs/astra-ai-execution-planning-action-governance.md
docs/architecture/decisions/astra-ai-execution-planning-action-governance.md
```

---

# Proposed Decision

Adopt a governed execution planning and action governance architecture that
inherits ASTRA-001, ASTRA-002, ASTRA-003, and ASTRA-004 and defines how Astra
constructs deterministic, declarative, explainable, and reviewable execution
plans from approved capabilities while preserving the permanent boundary that
planning never executes and execution authority remains with the owning
service.

This revision applies Astra's required refinements after source-level review of
commit `680f7218`:

- approvals and confirmations are bound to exact plan identifier, plan version
  or digest, affected step identifiers, action class, owning service, affected
  scope, material inputs, user-visible impact, and validity window;
- approval requirements survive replanning, but approval grants do not survive
  material plan or step changes unless approved governance proves the change is
  non-material and scope-preserving; and
- state-changing execution steps require stable step identity, idempotency
  classification, duplicate-detection expectations, retry scope,
  terminal-result reference, and uncertain-outcome handling.

---

# Review Questions

1. Does ASTRA-005 inherit ASTRA-001, ASTRA-002, ASTRA-003, and ASTRA-004
   without reopening them?
2. Is an execution plan clearly declarative rather than executable?
3. Is planning separated from Tool Executor and owning-service execution?
4. Are actions and execution steps clearly separated?
5. Are read-only, proposal, write, external, administrative, and prohibited
   actions classified conservatively?
6. Does every state-changing action require a governed execution step?
7. Are approval and confirmation requirements represented before execution?
8. Are mandatory-confirmation conditions clear?
9. Are prohibited-execution conditions clear?
10. Are retry, rollback, compensation, and cancellation represented without
    authorizing runtime behavior?
11. Are long-running operations and partial success represented?
12. Does delegation preserve owning-service execution authority?
13. Is execution evidence bounded and safe?
14. Does failure behavior fail closed for unknown execution risk?
15. Does replanning preserve approval requirements?
16. Is the documentation-only boundary complete?
17. Are approvals and confirmations bound to exact plan version, affected
    steps, scope, material inputs, impact, and validity window?
18. Does the architecture clearly distinguish approval requirements surviving
    replanning from approval grants surviving material change?
19. Do state-changing steps carry stable execution identity, idempotency scope,
    duplicate-detection expectations, and uncertain-outcome behavior?

---

# Current Codex Self-Review

```text
ASTRA-005               Proposed
Parent                  ASTRA-001 Accepted
Parent                  ASTRA-002 Accepted
Parent                  ASTRA-003 Accepted
Parent                  ASTRA-004 Accepted
Documentation Auth      Approved
Architecture Auth       Approved
Architecture Direction  Approved
Discovery               Complete
Specification           Complete
Architecture Review     Pending Astra Re-review
Product Owner Approval  Pending
ADR                     Proposed
Implementation          Not authorized
Production              Unchanged
```

Codex confirms ASTRA-005 makes no implementation changes and does not reopen
ASTRA-001, ASTRA-002, ASTRA-003, ASTRA-004, or the frozen Astra AI Platform
Phase 1 code.

---

# Review Boundary

This package is for architecture review only. It does not approve runtime
execution planning, Tool Executor handoff, tool execution, app integration,
external provider integration, prompts, APIs, routes, migrations, frontend
changes, deployment, or production behavior.

---

# Astra Review Outcome

Astra reviewed commit `680f7218` and approved the architecture direction with
two targeted documentation refinements required before ASTRA-005 can be frozen:

- bind approval and confirmation to exact plan version, affected steps, scope,
  material inputs, impact, and validity window; and
- define stable execution-step identity, idempotency, duplicate detection, and
  uncertain-outcome handling.

Those refinements are now applied. ASTRA-005 remains Proposed and is ready for
Astra re-review.

Implementation remains unauthorized. Production remains unchanged.
