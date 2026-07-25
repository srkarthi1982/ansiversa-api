# Astra AI Tool Execution Architecture

**Status:** Proposed
**Task:** ASTRA-006
**Parent:** ASTRA-001 Vision And Core Architecture
**Parent:** ASTRA-002 Platform Intelligence Architecture
**Parent:** ASTRA-003 Conversation And Context Architecture
**Parent:** ASTRA-004 Capability Discovery And Tool Architecture
**Parent:** ASTRA-005 Execution Planning And Action Governance
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

ASTRA-006 defines how an approved ASTRA-005 execution plan is handed to a
future executor, validated, accepted or rejected, executed by the owning
service, monitored, reconciled, and reported without transferring business-rule
or authorization ownership to Astra.

ASTRA-006 answers:

- What is an execution request?
- What is an executor?
- What is an execution acceptance decision?
- What is an executor rejection?
- How is live authorization rechecked?
- How is owning-service validation performed?
- How are plan version and approval bindings verified?
- How are stable step identity and idempotency enforced?
- How are duplicate requests detected?
- How are uncertain outcomes reconciled?
- How are timeouts handled?
- How are retries governed?
- How are cancellations governed?
- How are long-running operations monitored?
- How are progress states represented?
- How are partial success and compensation reported?
- How are stale plans rejected?
- How are executor health and availability represented?
- How is bounded execution evidence produced?
- How does Astra observe execution without becoming the executor?

ASTRA-006 does not implement execution. It defines the architecture contract
for a future executor boundary.

---

# Parent Architecture

ASTRA-006 inherits the frozen parent architectures:

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
        |
        v
ASTRA-006
Tool Execution Architecture
```

ASTRA-006 must not redefine:

- ASTRA-001 Astra identity;
- ASTRA-001 ownership and non-ownership boundaries;
- ASTRA-001 provider boundaries;
- ASTRA-001 production safety rules;
- ASTRA-002 intelligence pipeline;
- ASTRA-002 Intelligence Decision Matrix;
- ASTRA-002 external-intelligence law;
- ASTRA-003 conversation and context model;
- ASTRA-003 context ownership and authority-resolution rules;
- ASTRA-004 capability and tool separation;
- ASTRA-004 registry-backed capability authority;
- ASTRA-004 tool ownership boundaries;
- ASTRA-004 live authorization separation;
- ASTRA-005 declarative execution plan model;
- ASTRA-005 approval and confirmation binding;
- ASTRA-005 stable execution-step identity and idempotency requirements; or
- the fixed 100-solution-app platform boundary.

If this document conflicts with ASTRA-001, ASTRA-002, ASTRA-003, ASTRA-004, or
ASTRA-005, the accepted parent architecture wins.

---

# Scope Boundary

Allowed:

- define executor concepts;
- define execution request and response concepts;
- define acceptance and rejection rules;
- define pre-execution validation;
- define live authorization recheck requirements;
- define step identity and idempotency enforcement;
- define execution state and progress representation;
- define timeout and uncertain-outcome reconciliation;
- define retry and cancellation governance;
- define partial-success and compensation reporting;
- define executor health and availability concepts;
- define bounded execution evidence;
- define failure behavior;
- define security considerations;
- define future implementation guidance;
- propose an ADR;
- update iteration planning records; and
- update the AGENTS task log.

Not allowed:

- implementation;
- runtime integration;
- Tool Executor code changes;
- APIs;
- routes;
- provider integration;
- prompt implementation;
- model invocation;
- app integration;
- database access;
- database changes;
- migrations;
- frontend changes;
- tests;
- generated artifacts;
- deployment changes; or
- production behavior changes.

---

# Engineering Principles

- The planner never executes.
- The executor never redefines the plan silently.
- The owning service remains authoritative for business rules and data.
- Live authorization is rechecked before execution.
- Approval and confirmation bindings are verified before execution.
- State-changing steps require stable identity and idempotency protection.
- Timeout never proves non-execution.
- Retries require outcome reconciliation.
- Executor rejection is a governed result, not automatically a system error.
- Execution evidence is bounded, explainable, and reviewable.
- Unknown execution state fails closed.

---

# Engineering Laws

## Law 1 - Request Is Not Authority

An execution request is not execution authority until the executor and owning
service accept it.

## Law 2 - Retry Requires Step Reconciliation

Every state-changing step must be reconciled by stable identity before retry.

## Law 3 - Timeout Does Not Prove Non-Execution

A timeout does not prove that execution did not occur.

## Law 4 - Execution Requires Recheck

The executor must recheck live authorization, ownership, plan validity, and
approval binding before execution.

## Law 5 - Rejection Is Governed

The executor may reject stale, invalid, unauthorized, duplicate,
owner-mismatched, or policy-violating work.

---

# Executor Model

An executor is a future authorized runtime boundary that receives an approved
ASTRA-005 execution request, validates the request, coordinates with the
owning service, and reports bounded execution outcome evidence.

An executor is not:

- Astra;
- the planner;
- an external model provider;
- the owner of app business rules;
- the owner of app data;
- the owner of user authorization;
- a registry authority for capabilities; or
- a bypass around owning-service validation.

An executor record should describe:

- stable executor identifier;
- owning platform service;
- supported execution request contract;
- supported response contract;
- capability and tool classes it may accept;
- owning-service delegation requirements;
- live authorization recheck requirements;
- idempotency support;
- duplicate-detection support;
- timeout policy;
- retry policy;
- cancellation support;
- progress reporting support;
- compensation-reporting support;
- health and availability state;
- evidence contract; and
- version or compatibility marker.

The executor may coordinate execution, but the owning service remains
authoritative for whether the requested step is valid, authorized, and
permitted.

---

# Execution Request Model

An execution request is the governed handoff envelope from an approved
ASTRA-005 plan to a future executor. It asks an executor to validate and
possibly execute one or more approved steps. It is not itself authority to
execute.

An execution request should include:

- stable request identifier;
- originating plan identifier;
- plan version or digest;
- approved plan reference;
- affected step identifiers;
- action class for each step;
- owning service for each step;
- capability and tool reference;
- approval and confirmation binding evidence;
- live authorization recheck requirement;
- owner-service validation requirement;
- material input envelope;
- affected scope;
- user-visible impact summary;
- step identity and idempotency metadata;
- duplicate-detection expectation;
- retry scope;
- cancellation policy;
- timeout policy;
- progress-reporting requirement;
- compensation-reporting requirement;
- evidence requirement;
- request expiration or validity window;
- caller or planner evidence reference; and
- execution boundary statement.

The request must preserve the approved plan's relevant scope. It must not add
new state-changing work, broaden affected scope, downgrade approvals, change
material inputs, or reinterpret user confirmation.

---

# Acceptance And Rejection Model

Execution acceptance has two distinct stages. Executor admission confirms that
the request is eligible to be presented to the owning service. Owning-service
acceptance confirms that execution may proceed inside the owner boundary.

Executor admission is not execution authorization.

## Stage 1 - Executor Admission

The executor confirms that the request:

- is structurally valid;
- uses a supported contract;
- is within executor capability;
- is still bound to an approved plan;
- preserves approved plan scope;
- contains required approval and confirmation binding evidence;
- contains required step identity and idempotency metadata; and
- is eligible for owning-service validation.

Executor admission must not begin state-changing execution. After admission,
the request is ready for owning-service validation; execution remains
prohibited until owning-service acceptance succeeds.

## Stage 2 - Owning-Service Acceptance

The owning service confirms:

- current authorization;
- resource ownership;
- business-rule validity;
- current state;
- input validity;
- side-effect eligibility;
- idempotency and duplicate state;
- policy permission to execute now; and
- owner-specific execution constraints.

Only owning-service acceptance may authorize execution inside the owner
boundary.

Acceptance must not bypass:

- live authorization;
- owning-service validation;
- plan-version verification;
- approval and confirmation binding verification;
- step identity and idempotency checks;
- duplicate-detection checks;
- policy checks; or
- stale-plan checks.

Executor rejection is a governed result. It is not automatically a system
error.

Rejection reasons should include:

- malformed request;
- unsupported executor contract;
- unsupported capability or tool class;
- stale plan;
- expired request;
- plan version mismatch;
- approval binding missing or invalid;
- confirmation binding missing or invalid;
- live authorization unavailable or denied;
- owning-service validation failed;
- owner mismatch;
- duplicate request;
- step already completed;
- step already running;
- uncertain prior outcome requiring reconciliation;
- idempotency missing for state-changing step;
- policy violation;
- executor unavailable;
- dependency unavailable; and
- unknown execution state.

Rejected work must not be executed. A rejected request may require replanning,
renewed approval, clarification, cancellation, reconciliation, or no action.

---

# Cross-Owner Execution Boundary

A request may contain multiple steps, and each step may belong to a different
owning service. A multi-step or multi-owner request is not one atomic
transaction unless an owning architecture explicitly proves otherwise.

Each execution step must be independently:

- admitted by the executor;
- accepted by its authoritative owning service;
- live-authorized;
- validated;
- identified;
- reconciled; and
- reported.

Acceptance by one owner never authorizes another owner's step.

A multi-step or multi-owner plan must not imply:

- shared authorization;
- shared transaction ownership;
- atomic commit;
- automatic rollback across owners; or
- global success from partial owner success.

When atomicity cannot be guaranteed, the plan and execution evidence must
disclose partial-success and residual-effect risk.

Cross-owner recovery uses separately approved compensation. Astra and the
executor must not manufacture distributed rollback.

---

# Pre-execution Validation

Before execution, the executor and owning service must validate:

- request shape;
- request expiration;
- plan identifier;
- plan version or digest;
- affected step identifiers;
- approved action class;
- owning service;
- capability and tool reference;
- material inputs;
- affected scope;
- user-visible impact;
- approval and confirmation binding;
- live authorization requirement;
- owner-service validation result;
- owning-service acceptance result;
- step identity;
- idempotency metadata;
- duplicate-detection state;
- retry eligibility;
- cancellation eligibility;
- policy gates; and
- executor health.

Pre-execution validation may produce acceptance, rejection, clarification need,
reconciliation need, cancellation acknowledgement, or unavailable status.

Pre-execution validation must not rewrite the plan silently. If requested work
needs a materially different plan, the executor must reject or return a
replanning-required result.

For multi-owner work, pre-execution validation is evaluated per step and per
owning service. A validation pass for one owner does not validate or authorize
another owner's step.

---

# Live Authorization Recheck

Live authorization must be rechecked before execution because registry
metadata, planning evidence, and prior approval do not prove current user
authorization.

The recheck should verify:

- authenticated user or service identity;
- owner scope;
- role, permission, entitlement, or policy requirement;
- record or resource ownership;
- owning-service-specific constraints;
- sensitive-action policy;
- account or tenant status;
- request validity window; and
- whether authorization changed after planning.

Authorization denial, ambiguity, stale authorization evidence, missing identity,
or unavailable authorization authority must fail closed.

Astra may observe the authorization result as bounded evidence. Astra does not
become the authorization authority.

---

# Step Identity And Idempotency

Every state-changing step must carry stable execution identity from ASTRA-005
through request, acceptance, execution, retry, cancellation, reconciliation,
and reporting.

State-changing execution identity should include:

- stable step identifier;
- plan identifier;
- plan version or digest;
- request identifier;
- owning service;
- action identity;
- material input digest or owner-controlled equivalent;
- affected scope;
- idempotency classification;
- idempotency key or owner-controlled equivalent when supported;
- duplicate-detection expectation;
- retry scope;
- terminal-result reference; and
- uncertain-outcome behavior.

Duplicate detection should distinguish:

- new step;
- accepted but not started;
- running;
- completed successfully;
- completed with partial success;
- failed before side effect;
- failed after side effect;
- cancelled before side effect;
- cancelled after side effect;
- compensated;
- rejected; and
- unknown.

Unknown idempotency fails closed for state-changing actions. A retry must never
assume that a timed-out or disconnected request did not execute.

---

# Execution State And Progress Model

Execution state belongs to the executor and owning service, not to Astra. Astra
may observe bounded state transitions when authorized.

Execution states should include:

| State | Meaning |
|---|---|
| Received | Executor received the request |
| Rejected | Executor or owner rejected the request |
| Accepted | Executor accepted the request for validation or execution |
| Validating | Pre-execution validation is running |
| Waiting | Execution is waiting on dependency, owner, user, or external completion |
| Running | Execution is in progress |
| Reconciliation required | Prior outcome is uncertain and must be resolved before continuing |
| Cancellation requested | Cancellation was requested and is being evaluated |
| Cancelling | Executor or owner is attempting cancellation |
| Cancelled | Execution stopped according to cancellation policy |
| Partially succeeded | Some steps completed and others did not |
| Succeeded | Required execution completed |
| Failed | Required execution failed |
| Compensation required | Completed side effects require compensation review |
| Compensating | Approved compensation is in progress |
| Compensated | Compensation completed as reported by owner |
| Expired | Request or plan is no longer valid |
| Unknown | Executor cannot determine current outcome |

Progress reports for long-running operations should be bounded and
non-sensitive. They may include state, percent or stage when meaningful,
current owner boundary, expected next check, user-visible summary, and evidence
reference.

---

# Timeout And Uncertain Outcome Reconciliation

Timeouts are communication or waiting failures. They are not proof that work
did not happen.

Timeout handling should distinguish:

- request not accepted before timeout;
- request accepted but execution not started;
- execution started but no terminal result received;
- owner service returned uncertain outcome;
- executor lost connection after dispatch;
- progress polling expired; and
- terminal result unavailable.

Uncertain outcome reconciliation must use original step identity and
owner-service evidence before retry, replacement, cancellation, compensation,
or success reporting.

Reconciliation results should include:

- not accepted;
- accepted only;
- running;
- completed successfully;
- completed partially;
- failed before side effect;
- failed after side effect;
- cancelled;
- compensated;
- owner evidence unavailable;
- still uncertain; and
- policy prohibits retry.

If outcome remains uncertain for a state-changing step, the system must fail
closed and avoid duplicate execution.

---

# Retry Model

Retries are governed follow-up attempts inside the original retry scope. They
are not new hidden execution authority.

A retry may proceed only when:

- the original step identity is known;
- the original outcome has been reconciled;
- the step is retry-eligible;
- idempotency is supported or owner-controlled duplicate prevention is
  available;
- live authorization still passes;
- plan validity and approval binding still pass;
- the retry remains inside the approved scope;
- retry count and timing policy permit it; and
- the owning service accepts the retry.

A retry must not:

- broaden affected scope;
- change material inputs;
- use stale approval after material change;
- create a new state-changing identity without fresh governance gates;
- assume non-execution from timeout;
- bypass owner validation; or
- hide partial success.

If retry would require a materially different action, the executor must reject
and request replanning.

---

# Cancellation Model

Cancellation handling is executor and owner-service governed. Astra may request
or observe cancellation through approved future contracts but does not cancel
work directly.

Cancellation handling should verify:

- request identity;
- step identity;
- current execution state;
- cancellation eligibility;
- point of no return;
- owner-service cancellation support;
- live authorization for cancellation;
- approval or confirmation requirement when cancellation has side effects;
- whether completed side effects require compensation; and
- cancellation evidence requirements.

Cancellation outcomes should include:

- cancellation accepted;
- cancellation rejected;
- not cancellable;
- already completed;
- already failed;
- already cancelled;
- cancellation in progress;
- cancellation completed;
- cancellation uncertain;
- compensation required; and
- owner unavailable.

Cancellation is not rollback. Completed effects require rollback or
compensation reporting under the owning service's rules.

---

# Partial Success And Compensation Reporting

Partial success must be reported explicitly. It must not be collapsed into
success or failure without detail.

Partial success reporting should include:

- completed steps;
- failed steps;
- cancelled steps;
- uncertain steps;
- owning service for each reported step;
- side effects already committed;
- side effects not started;
- compensation required;
- compensation unavailable;
- residual effects;
- user-visible consequence;
- owner-service evidence reference; and
- recommended next governed action.

For multi-owner execution, partial success must make clear which owners
accepted, rejected, completed, failed, cancelled, or require compensation.
Global success must not be reported from partial owner success.

Compensation reporting should include:

- compensation request identity;
- original step identity;
- compensation owner;
- compensation status;
- whether compensation fully restored state;
- residual effects;
- failure category when compensation fails;
- evidence reference; and
- whether further user approval is required.

Compensation must not be presented as full restoration when residual effects
remain.

---

# Executor Health And Availability

Executor health describes whether the future executor is able to accept,
validate, execute, monitor, reconcile, and report work.

Health states should include:

- available;
- degraded;
- read-only or observe-only;
- rejecting new work;
- reconciliation-only;
- unavailable;
- disabled by policy;
- unsupported contract version; and
- unknown.

Executor availability must be checked before accepting work. If health is
unknown or incompatible with the request, state-changing work must fail closed.

Executor health does not prove owning-service health. Owning-service
availability remains a separate validation concern.

---

# Execution Evidence Model

Execution evidence is bounded metadata that explains how a request was
accepted, rejected, executed, reconciled, retried, cancelled, compensated, or
completed. It must be sufficient for review without leaking secrets or private
record payloads.

Evidence should include:

- execution request identifier;
- plan identifier;
- plan version or digest;
- affected step identifiers;
- executor identifier;
- owning service;
- capability and tool reference;
- acceptance or rejection decision;
- validation result;
- live authorization result category;
- approval and confirmation binding result;
- idempotency and duplicate-detection result;
- execution state;
- progress state when applicable;
- timeout category when applicable;
- reconciliation result when applicable;
- retry count and retry outcome;
- cancellation state when applicable;
- partial-success summary when applicable;
- compensation state when applicable;
- bounded failure category;
- terminal result reference; and
- user-visible outcome summary.

Evidence must not include raw prompts, tokens, secrets, stack traces, SQL,
large payloads, private record bodies, provider hidden reasoning, or unrelated
user data.

---

# Failure Behaviour

Failure is a governed outcome and must be represented without hidden retries or
silent recovery.

Failure classes:

- request validation failure;
- executor unavailable;
- unsupported contract;
- stale plan;
- expired request;
- plan version mismatch;
- approval binding failure;
- confirmation binding failure;
- live authorization denied;
- owner-service validation failure;
- owner mismatch;
- duplicate request;
- idempotency missing;
- timeout;
- uncertain outcome;
- retry prohibited;
- cancellation failure;
- partial success;
- compensation failure;
- evidence unavailable; and
- unknown execution state.

Failure behavior:

- fail closed for unknown execution state;
- do not execute rejected work;
- do not retry uncertain state-changing work without reconciliation;
- do not treat timeout as non-execution;
- do not claim success without owner evidence;
- do not hide partial success;
- do not downgrade approval or confirmation requirements;
- return bounded evidence; and
- preserve planner, executor, and owning-service boundaries.

---

# Security Considerations

ASTRA-006 preserves security by requiring executor and owner-service validation
before execution.

Security rules:

- no caller-controlled identity;
- no provider-controlled authorization;
- no execution from planning alone;
- no execution from registry metadata alone;
- no execution from prior approval without binding verification;
- no state-changing execution without stable step identity;
- no retry without outcome reconciliation;
- no duplicate execution when idempotency is unknown;
- no owner-service bypass;
- no stale-plan execution;
- no hidden writes;
- no raw secrets or private payloads in evidence;
- no production-impacting action unless separately authorized by Product Owner
  governance; and
- no ASTRA-006 implementation without a separate approved implementation
  phase.

---

# Future Implementation Notes

Future implementation may define concrete executor interfaces, request schemas,
response schemas, health checks, progress monitoring, reconciliation services,
retry orchestration, cancellation contracts, compensation reporting, and audit
storage only after separate Product Owner authorization.

Future implementation should:

- keep planner and executor code separated;
- validate plan version and approval binding before execution;
- recheck live authorization before execution;
- require owner-service validation before state changes;
- preserve stable step identity across retries and reconciliation;
- use owner-controlled idempotency where possible;
- treat timeout as uncertain outcome;
- expose partial success truthfully;
- produce bounded execution evidence;
- fail closed for unknown execution state; and
- include tests proving no executor path bypasses owner authority.

Future implementation must not use this document as authorization to build
runtime integration, Tool Executor code, APIs, routes, provider calls, prompt
implementation, model invocation, app integration, database access, migrations,
frontend changes, deployment, or production behavior.

---

# ADR

The proposed ADR is:

```text
docs/architecture/decisions/astra-ai-tool-execution-architecture.md
```

Decision proposed:

Adopt ASTRA-006 as the documentation-only architecture for how approved
ASTRA-005 execution plans are handed to a future executor, validated, accepted
or rejected, monitored, reconciled, and reported while preserving the permanent
boundary that Astra plans, the executor executes, and the owning service
remains authoritative.

---

# Risks

| Risk | Level | Mitigation |
|---|---|---|
| Execution request is mistaken for execution authority | Critical | Law 1 requires executor and owner acceptance before execution |
| Executor bypasses owning-service validation | Critical | Pre-execution validation requires owner-service validation |
| Executor admission is mistaken for owner acceptance | Critical | Acceptance is split into executor admission and owning-service acceptance |
| Multi-owner execution is treated as atomic | Critical | Cross-owner execution boundary requires per-step authority and partial-success disclosure |
| Live authorization is assumed from planning evidence | Critical | Live authorization is rechecked before execution |
| Timeout causes duplicate state-changing execution | Critical | Timeout is uncertain outcome and retry requires reconciliation |
| Stale plan executes after approval expires or scope changes | Critical | Plan version, digest, approval binding, and validity window are rechecked |
| Executor silently changes the plan | Critical | Materially different work requires rejection and replanning |
| Partial success is hidden | High | Partial success and compensation reporting are first-class |
| Execution evidence leaks sensitive data | High | Evidence is bounded metadata only |
| Executor health is conflated with owner-service health | Medium | Executor and owner availability are separate validation concerns |

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
- no Tool Executor code changes;
- no APIs or routes;
- no provider, prompt, model, app, database, migration, frontend, deployment,
  generated artifact, or production changes;
- AGENTS/docs-only boundary verified; and
- ASTRA-006 recorded as Proposed with Astra review and Product Owner approval
  pending.
