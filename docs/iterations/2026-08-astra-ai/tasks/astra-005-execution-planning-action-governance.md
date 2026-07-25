# ASTRA-005 - Execution Planning And Action Governance

**Status:** Frozen
**Created:** 2026-07-25
**Owner:** Karthikeyan Ramalingam
**Parent:** ASTRA-001 Vision And Core Architecture
**Parent:** ASTRA-002 Platform Intelligence Architecture
**Parent:** ASTRA-003 Conversation And Context Architecture
**Parent:** ASTRA-004 Capability Discovery And Tool Architecture
**Authorization:** Approved for documentation and architecture only
**Architecture Direction:** Approved
**Astra Re-review:** Approved
**Product Owner Approval:** Approved
**ADR:** Accepted
**Implementation Agent:** Codex
**Implementation:** Not authorized
**Production:** Unchanged

---

# Objective

Create the documentation-only architecture for how Astra AI transforms an
approved discovered capability into a governed execution plan while remaining a
planner rather than the executor.

ASTRA-005 defines execution plan and action models, planning pipeline,
execution state representation, approval and confirmation gates, retry,
rollback, compensation, cancellation, delegation, execution evidence, failure
behavior, security considerations, and future implementation notes.

Astra source-level review of commit `680f7218` approved the architecture
direction and required two targeted documentation refinements before freeze:

- bind approval and confirmation to exact plan version, affected steps, scope,
  material inputs, impact, and validity window; and
- define stable execution-step identity, idempotency, duplicate detection, and
  uncertain-outcome handling for state-changing execution steps.

---

# Deliverables

- `docs/astra-ai-execution-planning-action-governance.md`
- `docs/architecture/decisions/astra-ai-execution-planning-action-governance.md`
- `docs/iterations/2026-08-astra-ai/astra-005-architecture-review.md`
- `docs/iterations/2026-08-astra-ai/tasks/astra-005-execution-planning-action-governance.md`
- updates to the Astra AI iteration overview, backlog, dependencies, risks,
  validation strategy, iteration index, and task log.

---

# Scope

Allowed:

- documentation;
- specification;
- execution plan model;
- action model;
- planning pipeline;
- execution state model;
- approval and confirmation model;
- retry, rollback, and compensation representation;
- cancellation representation;
- delegation representation;
- execution evidence model;
- failure behavior;
- security considerations;
- ADR proposal;
- task-log update.

Not allowed:

- implementation;
- `app/` changes;
- tests;
- runtime changes;
- APIs;
- routes;
- Tool Executor changes;
- AI provider or dependency changes;
- prompt implementation;
- model invocation;
- migrations;
- frontend changes;
- individual app integration;
- app database access;
- database changes;
- AI SEO implementation changes;
- generated artifacts;
- deployment changes;
- production behavior changes; or
- execution authorization.

---

# Required Sections

1. Purpose
2. Parent Architecture
3. Scope Boundary
4. Execution Plan Model
5. Action Model
6. Planning Pipeline
7. Execution State Model
8. Approval And Confirmation Model
9. Execution Step Identity
10. Retry, Rollback And Compensation
11. Cancellation Model
12. Delegation Model
13. Execution Evidence Model
14. Failure Behaviour
15. Security Considerations
16. Future Implementation Notes
17. ADR
18. Risks
19. Validation Strategy

---

# Required Engineering Laws

```text
Law 1
Planning never performs execution.

Law 2
Execution authority remains with the owning service.

Law 3
Every state-changing action requires an explicit governed execution step.

Law 4
Execution plans are deterministic, explainable, and reviewable.

Law 5
Approval requirements must survive replanning.
```

Required Astra review refinements:

- Bind approvals and confirmations to the exact plan version, step scope,
  material inputs, impact, and validity window.
- Define stable execution-step identity, idempotency, duplicate detection, and
  uncertain-outcome handling.

---

# Final ASTRA-005 Status

```text
ASTRA-005               Approved / Frozen
Parent                  ASTRA-001 Accepted
Parent                  ASTRA-002 Accepted
Parent                  ASTRA-003 Accepted
Parent                  ASTRA-004 Accepted
Documentation Auth      Approved
Architecture Auth       Approved
Architecture Direction  Approved
Discovery               Complete
Specification           Complete
Astra Re-review         Approved
Product Owner Approval  Approved
ADR                     Accepted
Implementation          Not authorized
Production              Unchanged
ASTRA-006               Documentation only next; requires separate authorization
```
