# Architecture Decision: Astra AI Execution Planning And Action Governance

**Status:** Proposed
**Created:** 2026-07-25
**Task:** ASTRA-005
**Parent:** ASTRA-001 Vision And Core Architecture
**Parent:** ASTRA-002 Platform Intelligence Architecture
**Parent:** ASTRA-003 Conversation And Context Architecture
**Parent:** ASTRA-004 Capability Discovery And Tool Architecture
**Decision Owner:** Karthikeyan Ramalingam
**Documentation Authorization:** Approved
**Architecture Authorization:** Approved
**Architecture Direction:** Approved
**Architecture Review:** Minor revisions applied; pending Astra re-review
**Product Owner Approval:** Pending
**Implementation:** Not authorized
**Production:** Unchanged

---

# Decision

Should Ansiversa define a governed execution planning and action governance
architecture for Astra AI before implementing execution plans, Tool Executor
handoff, provider-backed action planning, write actions, cancellation,
compensation, or app-service execution?

Decision:

Propose ASTRA-005 as the documentation-only architecture for how Astra AI
constructs deterministic, declarative, explainable, and reviewable execution
plans from approved capabilities while preserving the boundary that planning
never executes and execution authority remains with the owning service. The
revised proposal binds approvals and confirmations to exact plan and step scope
and requires stable execution-step identity, idempotency classification,
duplicate detection, and uncertain-outcome handling for state-changing steps.

Canonical proposed specification:

```text
docs/astra-ai-execution-planning-action-governance.md
```

---

# Parent Architecture

ASTRA-005 inherits ASTRA-001, ASTRA-002, ASTRA-003, and ASTRA-004. It does not
redefine Astra identity, ownership, execution authority, provider philosophy,
production safety, the intelligence pipeline, the decision matrix, the
conversation/context model, context authority resolution, capability discovery,
tool ownership, live authorization separation, or the fixed 100-solution-app
platform boundary.

---

# Options Considered

## Option 1 - Let Planning Execute Directly

Recommendation: Reject.

This would collapse the planner/executor boundary and give Astra hidden
execution authority. It conflicts with ASTRA-001, ASTRA-002, and ASTRA-004.

## Option 2 - Let Each Tool Define Its Own Plan Shape

Recommendation: Reject.

Owning services should own business behavior and execution validation, but Astra
needs one governed plan model so approval, confirmation, retry, compensation,
cancellation, evidence, and boundary rules are consistent.

## Option 3 - Treat Confirmation As A UI Concern Only

Recommendation: Reject.

Confirmation is governance, not presentation. Approval and confirmation
requirements must be represented in the plan so they survive replanning,
delegation, and future executor handoff.

## Option 4 - Declarative Governed Execution Plans

Recommendation: Accept if approved after Astra review.

This preserves Astra as planner, keeps execution authority with owning
services, makes high-impact actions reviewable, requires approval gates before
execution, and provides bounded evidence for future audit without mutating
runtime state.

---

# Proposed Engineering Laws

## Law 1

> Planning never performs execution.

## Law 2

> Execution authority remains with the owning service.

## Law 3

> Every state-changing action requires an explicit governed execution step.

## Law 4

> Execution plans are deterministic, explainable, and reviewable.

## Law 5

> Approval requirements must survive replanning.

Approval requirements survive replanning. Approval grants do not survive
material plan or step changes unless an approved governance policy proves the
change is non-material and preserves the exact approved scope.

---

# Consequences If Accepted

- Execution plans become declarative architecture objects.
- Planning remains side-effect free.
- Action classes are separated into read-only, proposal, write, external,
  administrative, and prohibited actions.
- Every state-changing action requires a governed execution step.
- Approval and confirmation gates are represented before execution.
- Approval and confirmation grants are bound to plan identifier, version or
  digest, affected steps, action class, owner, scope, material inputs, impact,
  and validity window.
- Materially changed plans or steps invalidate prior confirmation unless
  approved governance proves the change is non-material and scope-preserving.
- Unknown execution risk fails closed.
- State-changing execution steps carry stable identity and idempotency scope.
- Retries must reconcile uncertain execution status before repeating
  state-changing work.
- Retry, rollback, compensation, cancellation, and long-running operation
  behavior are represented before delegation.
- Partial success and failure are first-class outcomes.
- Delegation remains separate from execution.
- Future executors may reject stale, unauthorized, invalid, or owner-mismatched
  plans.
- Evidence remains bounded and reviewable.
- Implementation remains separately unauthorized.
- Production remains unchanged.

---

# Acceptance Checklist

- [ ] Astra architecture review completed.
- [ ] Product Owner approval recorded.
- [ ] ADR accepted.
- [ ] ASTRA-005 frozen.
- [ ] Future implementation phase separately scoped.
- [x] Astra architecture direction approved with targeted documentation
  refinements recorded.
- [x] Approval and confirmation binding refinement applied.
- [x] Execution-step identity and duplicate-execution refinement applied.

---

# Current Status

```text
ADR                     Proposed
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
Implementation          Not authorized
Production              Unchanged
```
