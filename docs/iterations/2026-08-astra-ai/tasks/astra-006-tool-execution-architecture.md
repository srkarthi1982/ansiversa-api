# ASTRA-006 - Tool Execution Architecture

**Status:** Frozen
**Created:** 2026-07-25
**Owner:** Karthikeyan Ramalingam
**Parent:** ASTRA-001 Vision And Core Architecture
**Parent:** ASTRA-002 Platform Intelligence Architecture
**Parent:** ASTRA-003 Conversation And Context Architecture
**Parent:** ASTRA-004 Capability Discovery And Tool Architecture
**Parent:** ASTRA-005 Execution Planning And Action Governance
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

Create the documentation-only architecture for how an approved ASTRA-005
execution plan is handed to a future executor, validated, accepted or rejected,
executed by the owning service, monitored, reconciled, and reported without
transferring business-rule or authorization ownership to Astra.

ASTRA-006 defines executor and execution-request models, acceptance and
rejection behavior, pre-execution validation, live authorization recheck, step
identity and idempotency enforcement, progress states, timeout and
uncertain-outcome reconciliation, retry and cancellation governance, partial
success and compensation reporting, executor health and availability, bounded
execution evidence, failure behavior, security considerations, and future
implementation notes.

Astra source-level review of commit `4cb6bef3` approved the architecture
direction and required two targeted documentation refinements before freeze:

- separate executor admission from explicit owning-service acceptance; and
- define per-step authority and non-atomic behavior for multi-owner execution.

---

# Deliverables

- `docs/astra-ai-tool-execution-architecture.md`
- `docs/architecture/decisions/astra-ai-tool-execution-architecture.md`
- `docs/iterations/2026-08-astra-ai/astra-006-architecture-review.md`
- `docs/iterations/2026-08-astra-ai/tasks/astra-006-tool-execution-architecture.md`
- updates to the Astra AI iteration overview, backlog, dependencies, risks,
  validation strategy, iteration index, and task log.

---

# Scope

Allowed:

- documentation;
- specification;
- executor model;
- execution request model;
- acceptance and rejection model;
- pre-execution validation;
- live authorization recheck;
- step identity and idempotency enforcement;
- execution state and progress model;
- timeout and uncertain-outcome reconciliation;
- retry model;
- cancellation model;
- partial success and compensation reporting;
- executor health and availability;
- execution evidence model;
- failure behavior;
- security considerations;
- ADR proposal;
- task-log update.

Not allowed:

- implementation;
- `app/` changes;
- tests;
- runtime integration;
- Tool Executor code changes;
- APIs;
- routes;
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
4. Executor Model
5. Execution Request Model
6. Acceptance And Rejection Model
7. Cross-Owner Execution Boundary
8. Pre-execution Validation
9. Live Authorization Recheck
10. Step Identity And Idempotency
11. Execution State And Progress Model
12. Timeout And Uncertain Outcome Reconciliation
13. Retry Model
14. Cancellation Model
15. Partial Success And Compensation Reporting
16. Executor Health And Availability
17. Execution Evidence Model
18. Failure Behaviour
19. Security Considerations
20. Future Implementation Notes
21. ADR
22. Risks
23. Validation Strategy

---

# Required Engineering Laws

```text
Law 1
An execution request is not execution authority until the executor and owning
service accept it.

Law 2
Every state-changing step must be reconciled by stable identity before retry.

Law 3
A timeout does not prove that execution did not occur.

Law 4
The executor must recheck live authorization, ownership, plan validity, and
approval binding before execution.

Law 5
The executor may reject stale, invalid, unauthorized, duplicate,
owner-mismatched, or policy-violating work.
```

Required Astra review refinements:

- Separate executor admission from explicit owning-service acceptance.
- Define per-step authority and non-atomic behavior for multi-owner execution.

---

# Final ASTRA-006 Status

```text
ASTRA-006               Approved / Frozen
Parent                  ASTRA-001 Accepted
Parent                  ASTRA-002 Accepted
Parent                  ASTRA-003 Accepted
Parent                  ASTRA-004 Accepted
Parent                  ASTRA-005 Accepted
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
ASTRA-007               Documentation only next; requires separate authorization
```
