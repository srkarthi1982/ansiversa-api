# Astra AI Execution Planning And Action Governance

**Status:** Proposed
**Task:** ASTRA-005
**Parent:** ASTRA-001 Vision And Core Architecture
**Parent:** ASTRA-002 Platform Intelligence Architecture
**Parent:** ASTRA-003 Conversation And Context Architecture
**Parent:** ASTRA-004 Capability Discovery And Tool Architecture
**Created:** 2026-07-25
**Documentation Authorization:** Approved
**Architecture Authorization:** Approved
**Architecture Review:** Pending Astra Review
**Product Owner Approval:** Pending
**ADR:** Proposed
**Scope:** Documentation, specification, and architecture review only
**Implementation:** Not authorized
**Production:** Unchanged

---

# Purpose

ASTRA-005 defines how Astra AI transforms an approved discovered capability
into a governed execution plan while remaining a planner rather than an
executor.

ASTRA-005 answers:

- What is an execution plan?
- What is an action?
- What is an execution step?
- How are multi-step plans represented?
- How are execution dependencies represented?
- When is user confirmation mandatory?
- When is execution prohibited?
- How are read-only, proposal, and write actions separated?
- How are approval gates represented?
- How are retries represented?
- How are rollback and compensation represented?
- How are cancellations represented?
- How are long-running operations represented?
- How are execution failures represented?
- How are partial successes represented?
- How is execution evidence represented?
- How is execution delegated?
- How are execution boundaries preserved?
- How does Astra remain planner rather than executor?

ASTRA-005 does not define how tools execute. Tool execution architecture belongs
to ASTRA-006. ASTRA-005 defines the declarative plan that may later be handed
to an owning service or Tool Executor after required governance gates are
satisfied.

---

# Parent Architecture

ASTRA-005 inherits the frozen parent architectures:

```text
ASTRA-001
Vision And Core Architecture
        |
        v
ASTRA-002
Platform Intelligence Architecture
        |
        v
ASTRA-003
Conversation And Context Architecture
        |
        v
ASTRA-004
Capability Discovery And Tool Architecture
        |
        v
ASTRA-005
Execution Planning And Action Governance
```

ASTRA-005 must not redefine:

- ASTRA-001 Astra identity;
- ASTRA-001 ownership and non-ownership boundaries;
- ASTRA-001 provider boundaries;
- ASTRA-001 execution authority;
- ASTRA-001 production safety rules;
- ASTRA-002 intelligence pipeline;
- ASTRA-002 Intelligence Decision Matrix;
- ASTRA-002 external-intelligence law;
- ASTRA-002 decision-evidence model;
- ASTRA-003 conversation and context model;
- ASTRA-003 context ownership and authority-resolution rules;
- ASTRA-004 capability and tool separation;
- ASTRA-004 registry-backed capability authority;
- ASTRA-004 tool ownership boundaries;
- ASTRA-004 live authorization separation; or
- the fixed 100-solution-app platform boundary.

If this document conflicts with ASTRA-001, ASTRA-002, ASTRA-003, or ASTRA-004,
the accepted parent architecture wins.

---

# Scope Boundary

Allowed:

- define execution plan concepts;
- define action and execution-step models;
- define planning pipeline;
- define execution state model;
- define approval and confirmation model;
- define retry, rollback, and compensation representation;
- define cancellation representation;
- define delegation representation;
- define execution evidence representation;
- define failure behavior;
- define security considerations;
- define future implementation guidance;
- propose an ADR;
- update iteration planning records; and
- update the AGENTS task log.

Not allowed:

- implementation;
- runtime changes;
- APIs;
- routes;
- Tool Executor changes;
- provider integration;
- prompt implementation;
- model invocation;
- app integration;
- database access;
- database changes;
- migrations;
- frontend changes;
- generated artifacts;
- deployment changes; or
- production behavior changes.

---

# Engineering Principles

- Planning precedes execution.
- Execution plans are declarative.
- Planning never mutates application state.
- Execution authority belongs to the owning service.
- Every execution plan is explainable.
- Every execution plan is reviewable.
- Every execution plan is reproducible.
- Confirmation precedes high-impact actions.
- Compensation is preferred over silent recovery.
- Unknown execution risk fails closed.

---

# Engineering Laws

## Law 1 - Planning Never Performs Execution

Planning may describe intended work, required gates, owner boundaries, risks,
and evidence requirements. Planning must not call tools, mutate records, invoke
providers for execution, write files, enqueue jobs, update databases, send
messages, or perform side effects.

## Law 2 - Execution Authority Remains With The Owning Service

Astra may prepare a plan, but the service that owns the capability, data,
business rules, and authorization remains the authority for execution.

## Law 3 - Every State-Changing Action Requires A Governed Execution Step

Any state-changing action must be represented as an explicit execution step
with owner, impact, confirmation, authorization, failure, evidence, and
compensation metadata.

## Law 4 - Execution Plans Are Deterministic, Explainable, And Reviewable

Given the same approved capability, context, constraints, and user intent,
Astra should construct the same plan or the same governed refusal.

## Law 5 - Approval Requirements Must Survive Replanning

If Astra replans after a failure, cancellation, dependency change, or
clarification, required approvals cannot be silently downgraded or removed.
Approval requirements survive replanning. Approval grants do not survive
material plan or step changes unless an approved governance policy proves the
change is non-material and preserves the exact approved scope.

---

# Execution Plan Model

An execution plan is a declarative, reviewable structure that describes a
possible sequence of governed actions. It is not execution and does not grant
execution authority.

An execution plan should include:

- stable plan identifier;
- originating conversation or request reference;
- selected capability identifier from ASTRA-004;
- selected tool candidate or owning-service reference when known;
- plan purpose;
- user-visible summary;
- execution boundary statement;
- ordered execution steps;
- step dependencies;
- action classes;
- approval gates;
- confirmation requirements;
- approval and confirmation binding requirements;
- authorization requirements;
- expected inputs;
- expected outputs;
- data-sensitivity classification;
- side-effect classification;
- estimated impact;
- retry policy;
- rollback or compensation policy;
- cancellation policy;
- long-running operation markers;
- evidence requirements;
- failure representation;
- partial-success representation;
- expiration or staleness marker;
- plan version; and
- plan digest or equivalent stable version proof when supported; and
- deterministic planning evidence.

Execution plans are declarative because they describe work that may be
performed later. A future executor may reject, partially execute, or request a
new plan if authorization, ownership, state, inputs, or policy checks fail.

---

# Action Model

An action is a user-meaningful unit of intended work. It may be read-only,
proposal-only, state-changing, external, administrative, or prohibited.

Action classes:

| Action class | Meaning | Execution planning behavior |
|---|---|---|
| Read-only | Retrieves or summarizes authorized information without mutation | May be planned without write confirmation, but still requires authorization and minimization |
| Proposal | Produces a draft, recommendation, or plan without mutation | May be planned as non-mutating output |
| Write | Creates, updates, deletes, sends, imports, exports, schedules, or otherwise changes state | Requires explicit governed execution step and confirmation policy |
| External side effect | Sends data or action outside Ansiversa boundaries | Requires high-impact review unless separately classified lower by approved policy |
| Administrative | Changes permissions, configuration, billing, production, deployment, security, or governance state | Requires strict approval and may be prohibited for Astra |
| Prohibited | Violates policy, ownership, safety, authorization, or scope | Must not be planned for execution |

Unknown action class must be treated as write/action risk and fail closed until
an authoritative owner classifies it.

---

# Planning Pipeline

```text
Approved Capability Candidate
        |
        v
Intent And Context Constraint Review
        |
        v
Action Classification
        |
        v
Owner And Authorization Boundary Mapping
        |
        v
Step Construction
        |
        v
Dependency Mapping
        |
        v
Approval And Confirmation Gate Assignment
        |
        v
Retry / Compensation / Cancellation Policy Assignment
        |
        v
Evidence Requirement Assignment
        |
        v
Plan Validation
        |
        v
Plan Proposal / Clarification / Refusal
```

The planning pipeline may produce:

- a complete proposed execution plan;
- a partial plan requiring user clarification;
- a plan requiring owner or policy approval before execution;
- a refusal because execution is prohibited;
- an unavailable result because a dependency, owner, capability, or
  authorization boundary cannot be established; or
- a no-action response when planning is unnecessary.

Planning must never skip from capability discovery to execution.

---

# Execution State Model

ASTRA-005 defines states for representing planned or future delegated work. It
does not create runtime execution state.

Execution state values should include:

| State | Meaning |
|---|---|
| Draft | Plan is being constructed and is not ready for review |
| Proposed | Plan is complete enough for user or governance review |
| Needs clarification | Required intent, input, owner, or risk information is missing |
| Awaiting approval | Plan or step requires approval before execution |
| Approved for delegation | Required approvals are satisfied and the plan may be handed to an executor in a future authorized architecture |
| Delegated | A future executor or owning service accepted responsibility |
| Running | Future execution is in progress under executor ownership |
| Waiting | Future execution is blocked on dependency, long-running operation, or external completion |
| Partially succeeded | Some steps completed and others failed, were cancelled, or remain pending |
| Succeeded | All required steps completed under executor ownership |
| Failed | One or more required steps failed without complete compensation |
| Cancelled | Execution or planned execution was stopped by user, policy, owner, or system |
| Compensated | Completed side effects were offset by approved compensation steps |
| Expired | Plan is stale and must be revalidated or replanned |
| Prohibited | Plan cannot proceed under governance rules |

Astra may describe these states for architecture and evidence. Future runtime
ownership belongs to ASTRA-006 and the owning executor/service.

---

# Approval And Confirmation Model

Approval gates determine whether a plan or step may proceed to a future
executor. Confirmation gates determine whether the user explicitly agrees to a
specific action before it is performed.

## Approval And Confirmation Binding

Every approval and confirmation must be bound to:

- plan identifier;
- plan version or digest;
- affected step identifiers;
- action class;
- owning service;
- affected scope;
- material inputs;
- user-visible impact; and
- expiration or validity window.

A materially changed plan or step invalidates prior confirmation unless an
approved governance policy proves the change is non-material and preserves the
exact approved scope.

Replanning may preserve required approval classes, but it must not
automatically preserve previously granted approval. The architecture separates
the two rules:

```text
Approval requirements survive replanning.
Approval grants do not survive material change.
```

Any future implementation must be able to determine which plan version, step
set, action class, owner, scope, inputs, impact, and validity window were
approved. If that binding cannot be proven, the plan or step must return to
the appropriate approval or confirmation gate before delegation.

Mandatory confirmation is required when a plan or step:

- creates, updates, deletes, archives, restores, sends, schedules, imports, or
  exports user data;
- changes permissions, identity, account, security, billing, production,
  deployment, governance, or notification behavior;
- triggers external communication or external data transfer;
- uses sensitive, regulated, or private personal context;
- affects long-lived user records;
- could be difficult or impossible to undo;
- has unclear impact;
- has unknown side effects;
- was produced after replanning from a previously approved plan; or
- is classified by the owning service as confirmation-required.

Confirmation must be specific to the action, impact, owner, affected scope, and
meaningful user-visible consequence. Broad historical approval cannot silently
authorize a newly created or materially changed step.

Execution is prohibited when:

- capability authority cannot be proven;
- live authorization cannot be verified by the owning service or authority;
- the action violates parent architecture laws;
- the action requires an implementation or production capability not
  authorized;
- the action would cross app ownership boundaries without an approved contract;
- required confirmation is refused, absent, stale, or ambiguous;
- dependency or owner identity cannot be established;
- compensation is required but unavailable for a high-impact action; or
- policy requires fail-closed behavior.

---

# Execution Step Identity

Every execution step must be identifiable. Every state-changing execution step
must define:

- stable step identifier;
- plan identifier and version;
- owning service;
- action identity;
- idempotency classification;
- idempotency key or owner-controlled equivalent when supported;
- duplicate-detection expectation;
- retry scope;
- terminal-result reference; and
- behavior when execution status is unknown.

Step identity is part of safe delegation. It allows a future executor or owning
service to determine whether a requested step is new, already running, already
completed, failed, cancelled, or in an unknown terminal state.

A retry must never assume that a timed-out step did not execute. If completion
status is uncertain, the executor or owning service must reconcile the original
step identity before any retry. Unknown idempotency fails closed for
state-changing actions.

ASTRA-005 does not define how the future executor performs reconciliation.
That belongs to ASTRA-006 and the owning service. ASTRA-005 requires only that
the plan contain enough stable identity and idempotency information for safe
delegation later.

---

# Retry, Rollback And Compensation

Retries, rollback, and compensation must be represented before execution, not
invented silently after failure.

Retry policy should describe:

- retry eligibility;
- maximum attempts;
- retryable failure classes;
- non-retryable failure classes;
- idempotency requirement;
- step identity requirement;
- duplicate-detection expectation;
- backoff or delay expectation;
- owner responsible for retry decision; and
- whether retry requires renewed confirmation.

A retry may be planned only inside the retry scope defined for the original
step identity. Retrying with a new state-changing identity is a new step and
must pass approval, confirmation, authorization, and compensation gates as a new
action.

Rollback means reversing a change by restoring previous state when the owning
service supports that operation.

Compensation means applying a new approved action that offsets a previous
effect when true rollback is impossible or not owned by the same service.

Compensation policy should describe:

- whether rollback is available;
- whether compensation is available;
- required compensation steps;
- compensation owner;
- user confirmation requirement;
- known residual effects;
- evidence required to prove compensation was attempted or completed; and
- behavior when compensation fails.

Silent recovery is prohibited for state-changing actions. A plan may recommend
compensation, but future execution remains owned by the authorized executor or
owning service.

---

# Cancellation Model

Plans must define when cancellation is possible and what cancellation means.

Cancellation states:

- before approval;
- after approval but before delegation;
- after delegation but before execution begins;
- during execution;
- after partial completion; and
- after completion.

Cancellation policy should describe:

- who may cancel;
- cancellation deadline or point of no return;
- which steps are cancellable;
- which steps are already committed;
- whether cancellation requires compensation;
- whether cancellation creates residual state;
- how cancellation evidence is recorded; and
- how the user is informed.

Cancellation is not rollback. Cancelling future or in-flight work may stop
additional side effects, but completed side effects require rollback or
compensation rules.

---

# Delegation Model

Delegation is the handoff of an approved plan or step to a future Tool Executor
or owning service. Delegation does not transfer ownership of business rules to
Astra.

A delegation record should include:

- plan identifier;
- step identifier;
- owning service;
- target executor or owner boundary;
- capability and tool reference;
- approved input envelope;
- authorization evidence reference;
- confirmation evidence reference;
- expected response contract;
- timeout policy;
- retry policy;
- cancellation policy;
- compensation policy;
- evidence requirements; and
- execution boundary statement.

Future executors may reject delegated work if live authorization, input
validation, ownership, dependency, policy, or state checks fail. Rejection must
not be treated as executor error by default; it may mean the plan was no longer
valid.

Delegation of a state-changing step must include stable step identity and
idempotency scope. If the future executor cannot determine whether the step has
already executed, it must reconcile with the owning service before attempting a
retry or replacement action.

---

# Execution Evidence Model

Execution evidence is bounded metadata that explains how a plan was constructed,
approved, delegated, and later completed or failed. Evidence must be sufficient
for review without leaking secrets or private record payloads.

Planning evidence should include:

- parent architecture versions;
- capability identifier;
- registry proof reference;
- action classification;
- owner boundary;
- approval requirements;
- approval and confirmation binding markers;
- confirmation requirements;
- dependency map;
- risk classification;
- prohibited-action checks;
- retry and compensation policy summary;
- cancellation policy summary;
- plan version; and
- step identity and idempotency markers for state-changing steps; and
- deterministic planning decision markers.

Future execution evidence may include:

- executor or owning-service response code;
- start and completion timestamps;
- terminal state;
- step outcome;
- retry count;
- duplicate-detection or idempotency outcome when applicable;
- compensation state;
- cancellation state;
- bounded error category;
- evidence reference; and
- user-visible summary.

Evidence must not include raw prompts, tokens, secrets, stack traces, SQL,
large payloads, private record bodies, provider hidden reasoning, or unrelated
user data.

---

# Failure Behaviour

Failure is a governed outcome, not an exception to hide.

Failure classes:

- planning failure;
- missing capability authority;
- missing owner authority;
- missing live authorization;
- missing or ambiguous confirmation;
- prohibited action;
- dependency unavailable;
- input validation failure;
- executor rejection;
- timeout;
- partial success;
- compensation failure;
- cancellation failure;
- stale plan;
- unknown risk.

Failure behavior:

- fail closed for unknown execution risk;
- preserve approval requirements after replanning;
- avoid retries when idempotency is unknown;
- avoid compensation claims without owner evidence;
- return clarification when user intent materially affects safety or ownership;
- expose partial success without overstating completion;
- record bounded evidence;
- never represent a planned action as completed; and
- never silently replace a failed step with a different state-changing step.

---

# Security Considerations

ASTRA-005 preserves security by keeping planning declarative and by requiring
explicit gates before future execution.

Security rules:

- no caller-controlled identity;
- no provider-controlled authorization;
- no capability fabricated from user text or provider output;
- no execution inside planning;
- no direct app database access by central Astra planning;
- no hidden writes;
- no approval downgrades during replanning;
- no raw secrets or private payloads in evidence;
- no external transfer without explicit classification and approval;
- no use of stale plans for state-changing execution;
- no high-impact action without confirmation;
- no execution when ownership is ambiguous; and
- no production-impacting action unless separately authorized by Product Owner
  governance.

---

# Future Implementation Notes

Future implementation may create plan schemas, planning validators, plan
serialization, review UI contracts, executor handoff contracts, or audit
storage only after separate Product Owner authorization.

Future implementation should:

- keep planning pure and side-effect free;
- make plan construction deterministic;
- validate plan shape before review;
- store approval requirements with the plan;
- require revalidation before delegation;
- reject stale or owner-mismatched plans;
- preserve owner-scoped authorization checks;
- route execution only through ASTRA-006-governed executor contracts;
- test failure, partial success, cancellation, and compensation paths; and
- prove that no planning code mutates application state.

Future implementation must not use this document as authorization to build
runtime execution, Tool Executor integration, provider invocation, routes, app
integration, migrations, frontend changes, or production behavior.

---

# ADR

The proposed ADR is:

```text
docs/architecture/decisions/astra-ai-execution-planning-action-governance.md
```

Decision proposed:

Adopt ASTRA-005 as the documentation-only architecture for how Astra AI
constructs deterministic, declarative, reviewable execution plans from approved
capabilities while preserving the permanent boundary that planning never
executes and execution authority remains with the owning service.

---

# Risks

| Risk | Level | Mitigation |
|---|---|---|
| Planning is mistaken for execution authority | Critical | Law 1 and Law 2 keep plans declarative and owner-owned |
| Approval gates are lost during replanning | Critical | Law 5 requires approval requirements to survive replanning |
| Unknown side effects are treated as safe | Critical | Unknown execution risk fails closed |
| Partial success is overstated as success | High | State model includes partial success and compensation states |
| Compensation is invented after failure | High | Compensation must be represented before execution |
| Cancellation is confused with rollback | Medium | Cancellation model separates stopping work from reversing effects |
| Evidence leaks sensitive data | High | Evidence model allows bounded metadata only |
| Executor rejection is treated as runtime bug | Medium | Delegation model allows owner/executor rejection when plan is stale or invalid |

---

# Validation Strategy

Documentation validation:

```bash
git diff --check
git diff --name-only
test "$(git diff --name-only | grep -Ev '^(AGENTS.md|docs/)' | wc -l)" = "0"
```

Required validation outcomes:

- documentation-only boundary verified;
- parent inheritance verified;
- required sections present;
- no implementation leakage;
- no runtime changes;
- no production changes;
- AGENTS/docs-only boundary verified; and
- ASTRA-005 recorded as Proposed with Astra review and Product Owner approval
  pending.
