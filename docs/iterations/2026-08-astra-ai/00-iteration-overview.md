# Iteration 3 - Astra AI Architecture

**Status:** ASTRA-001 Frozen; ASTRA-002 Frozen; ASTRA-003 Frozen; ASTRA-004 Frozen; ASTRA-005 Frozen; ASTRA-006 Frozen; ASTRA-007 Frozen; ASTRA-008 Frozen; ASTRA-009 Proposed
**Created:** 2026-07-24
**Implementation:** Not authorized
**Production:** Unchanged

---

# Objective

Define the constitutional architecture for Astra AI before expanding beyond
the frozen Phase 1 foundation.

This iteration establishes what Astra AI is, what it owns, how it relates to
the existing Assistant and platform systems, and how future capabilities must
be reviewed before implementation.

---

# Deliverables

- [Astra AI Vision And Core Architecture](../../astra-ai-vision-core-architecture.md)
- [Astra AI Vision And Core Architecture ADR](../../architecture/decisions/astra-ai-vision-core-architecture.md)
- [ASTRA-001 discovery](astra-001-discovery.md)
- [ASTRA-001 architecture review package](astra-001-architecture-review.md)
- [ASTRA-001 task record](tasks/astra-001-vision-core-architecture.md)
- [Astra AI Platform Intelligence Architecture](../../astra-ai-platform-intelligence-architecture.md)
- [Astra AI Platform Intelligence Architecture ADR](../../architecture/decisions/astra-ai-platform-intelligence-architecture.md)
- [ASTRA-002 architecture review package](astra-002-architecture-review.md)
- [ASTRA-002 task record](tasks/astra-002-platform-intelligence-architecture.md)
- [Astra AI Conversation And Context Architecture](../../astra-ai-conversation-context-architecture.md)
- [Astra AI Conversation And Context Architecture ADR](../../architecture/decisions/astra-ai-conversation-context-architecture.md)
- [ASTRA-003 architecture review package](astra-003-architecture-review.md)
- [ASTRA-003 task record](tasks/astra-003-conversation-context-architecture.md)
- [Astra AI Capability Discovery And Tool Architecture](../../astra-ai-capability-tool-architecture.md)
- [Astra AI Capability Discovery And Tool Architecture ADR](../../architecture/decisions/astra-ai-capability-tool-architecture.md)
- [ASTRA-004 architecture review package](astra-004-architecture-review.md)
- [ASTRA-004 task record](tasks/astra-004-capability-tool-architecture.md)
- [Astra AI Execution Planning And Action Governance](../../astra-ai-execution-planning-action-governance.md)
- [Astra AI Execution Planning And Action Governance ADR](../../architecture/decisions/astra-ai-execution-planning-action-governance.md)
- [ASTRA-005 architecture review package](astra-005-architecture-review.md)
- [ASTRA-005 task record](tasks/astra-005-execution-planning-action-governance.md)
- [Astra AI Tool Execution Architecture](../../astra-ai-tool-execution-architecture.md)
- [Astra AI Tool Execution Architecture ADR](../../architecture/decisions/astra-ai-tool-execution-architecture.md)
- [ASTRA-006 architecture review package](astra-006-architecture-review.md)
- [ASTRA-006 task record](tasks/astra-006-tool-execution-architecture.md)
- [Astra AI External Intelligence And Provider Architecture](../../astra-ai-external-intelligence-provider-architecture.md)
- [Astra AI External Intelligence And Provider Architecture ADR](../../architecture/decisions/astra-ai-external-intelligence-provider-architecture.md)
- [ASTRA-007 architecture review package](astra-007-architecture-review.md)
- [ASTRA-007 task record](tasks/astra-007-external-intelligence-provider-architecture.md)
- [Astra AI Memory Architecture](../../astra-ai-memory-architecture.md)
- [Astra AI Memory Architecture ADR](../../architecture/decisions/astra-ai-memory-architecture.md)
- [ASTRA-008 architecture review package](astra-008-architecture-review.md)
- [ASTRA-008 task record](tasks/astra-008-memory-architecture.md)
- [Astra AI Learning And Adaptation Architecture](../../astra-ai-learning-adaptation-architecture.md)
- [Astra AI Learning And Adaptation Architecture ADR](../../architecture/decisions/astra-ai-learning-adaptation-architecture.md)
- [ASTRA-009 architecture review package](astra-009-architecture-review.md)
- [ASTRA-009 task record](tasks/astra-009-learning-adaptation-architecture.md)
- [Priority backlog](01-priority-backlog.md)
- [Dependencies](02-dependencies.md)
- [Risk register](03-risk-register.md)
- [Validation strategy](04-validation-strategy.md)

---

# Lifecycle

```text
Discovery
    ↓
Architecture proposal
    ↓
Astra architecture review
    ↓
Product Owner approval
    ↓
Task freeze
    ↓
Separate implementation authorization
```

ASTRA-001 is approved and Frozen after Astra re-review and Product Owner
approval. The ADR is accepted. ASTRA-001 does not authorize Phase 2
implementation, runtime changes, app integration, providers, APIs, migrations,
frontend changes, deployment changes, or production behavior. Phase 2 is
documentation-only next and requires separate authorization before work begins.

ASTRA-002 Platform Intelligence Architecture is approved and Frozen. Astra
approved the architecture direction, requested two minor ordering corrections,
approved the corrected source-level re-review for commit `01d2c55`, and
Product Owner approval is recorded. The ADR is accepted. ASTRA-002 inherits
ASTRA-001 and defines how Astra AI reasons over user requests before any new
intelligence implementation is written.

---

# Current Foundation

Astra AI Platform Phase 1 is completed and Frozen. It provides an isolated
disabled-by-default backend package with internal contracts, governed platform
context, platform intents, policy decisions, response planning, action
proposals, and deterministic audit evidence.

Existing Assistant, Knowledge, user context, tool registry, AI SEO, auth, and
app-service foundations remain the systems Astra AI should consume rather than
duplicate.

ASTRA-002 documents the logical pipeline from user request through
conversation understanding, intent recognition, context assembly, permission
evaluation, capability discovery, planning, action proposal, decision evidence
assembly, and governed response construction.

ASTRA-003 Conversation and Context Architecture is approved and Frozen. Astra
approved the architecture direction, requested one minor Context Authority
Resolution refinement, approved the corrected source-level re-review for commit
`2e7fed4`, and Product Owner approval is recorded. The ADR is accepted.
ASTRA-003 inherits ASTRA-001 and ASTRA-002 and defines how Astra manages
conversation state and context throughout the intelligence pipeline without
creating ungoverned memory, provider context, app data access, or production
behavior. ASTRA-004 is documentation-only next and requires separate
authorization before work begins.

ASTRA-004 Capability Discovery and Tool Architecture is approved and Frozen.
Astra approved the architecture direction for commit `862816d`, requested two
targeted refinements, and approved the corrected source-level re-review for
commit `5e60cc4`. Product Owner approval is recorded. The ADR is accepted. The
accepted architecture separates registry permission metadata from live
authorization and defines deterministic candidate precedence with ambiguity
handling. ASTRA-004 inherits ASTRA-001, ASTRA-002, and ASTRA-003 and defines
how Astra discovers registered capabilities, classifies tools, verifies
capability existence, preserves tool ownership, records bounded evidence, and
prevents capability fabrication without granting execution authority. ASTRA-005
was authorized for documentation and architecture only on 2026-07-25.

ASTRA-005 Execution Planning and Action Governance is approved and Frozen.
Astra approved the architecture direction for commit `680f7218`, requested two
targeted documentation refinements, and approved the corrected source-level
re-review for commit `ffe6710`. Product Owner approval is recorded. The ADR is
accepted. ASTRA-005 inherits ASTRA-001, ASTRA-002, ASTRA-003, and ASTRA-004 and
defines how Astra transforms an approved discovered capability into a
deterministic, declarative, explainable, and reviewable execution plan while
remaining planner rather than executor. The accepted architecture binds
approval and confirmation to exact plan version, step scope, material inputs,
impact, and validity window, and defines stable execution-step identity,
idempotency, duplicate detection, and uncertain-outcome handling.
Implementation and production changes remain unauthorized. ASTRA-006 Tool
Execution Architecture was authorized for documentation and architecture only
on 2026-07-25.

ASTRA-006 Tool Execution Architecture is approved and Frozen. Astra approved
the architecture direction for commit `4cb6bef3`, requested two targeted
documentation refinements, and approved the corrected source-level re-review
for commit `0d01e3f8`. Product Owner approval is recorded. The ADR is
accepted. ASTRA-006 inherits ASTRA-001, ASTRA-002, ASTRA-003, ASTRA-004, and
ASTRA-005 and defines how an approved ASTRA-005 execution plan is handed to a
future executor, validated, accepted or rejected, executed by the owning
service, monitored, reconciled, and reported without transferring business-rule
or authorization ownership to Astra. The accepted architecture separates
executor admission from owning-service acceptance and defines per-step
authority with non-atomic behavior for multi-owner execution. Implementation
and production changes remain unauthorized. ASTRA-007 External Intelligence And
Provider Architecture was authorized for documentation and architecture only on
2026-07-25.

ASTRA-007 External Intelligence and Provider Architecture is approved and
Frozen. Astra approved the architecture direction for commit `ad3340e`,
requested two targeted documentation refinements, and approved the corrected
source-level re-review for commit `fa0c6919`. Product Owner approval is
recorded. The ADR is accepted. ASTRA-007 inherits ASTRA-001, ASTRA-002,
ASTRA-003, ASTRA-004, ASTRA-005, and ASTRA-006 and defines how Astra
determines whether external intelligence is necessary, constructs governed
provider input envelopes, selects eligible providers, validates provider
responses, controls cost and privacy risk, records bounded evidence, and
remains provider-independent. The accepted architecture separates provider
eligibility from provider selection and defines provider response authority so
provider output remains advisory until validated by Astra and authoritative
owners. Implementation and production changes remain unauthorized. ASTRA-008
Memory Architecture is documentation-only next and requires separate
authorization before work begins.

ASTRA-008 Memory Architecture is approved and Frozen. Astra approved the
architecture direction for commit `dcc0ec3`, requested two targeted
documentation refinements, and approved the corrected source-level re-review
for commit `ce14300`. Product Owner approval is recorded. The ADR is accepted.
ASTRA-008 inherits ASTRA-001, ASTRA-002, ASTRA-003, ASTRA-004, ASTRA-005,
ASTRA-006, and ASTRA-007 and defines what Astra may remember, what it must
forget, how memory is classified, owned, retrieved, retained, deleted,
exported, audited, and prevented from becoming an unauthorized cross-app
datastore. The accepted architecture separates conversation state, working
memory, long-term user memory, preference memory, app-owned data, Knowledge,
provider output, and audit evidence. It makes forgetting, deletion, export,
retention, owner scope, memory ownership, memory references, retrieval
authorization, and memory evidence first-class governance requirements.
Implementation and production changes remain unauthorized. ASTRA-009 Learning
And Adaptation Architecture is documentation-only next and requires separate
authorization before work begins.

ASTRA-009 Learning And Adaptation Architecture is Proposed. ASTRA-009 inherits
ASTRA-001, ASTRA-002, ASTRA-003, ASTRA-004, ASTRA-005, ASTRA-006, ASTRA-007,
and ASTRA-008 and defines how Astra may adapt behavior, preferences,
explanations, and workflow assistance over time without becoming opaque,
unpredictable, provider-defined, or constitutionally mutable. The proposed
architecture separates learning from memory, makes correction and feedback
classification explicit, requires adaptation eligibility, activation,
conflict resolution, confidence, evidence, explainability, user controls,
drift prevention, reset/revocation, cross-app boundaries, provider/model
boundaries, and preserves the permanent rule that Astra may adapt behavior but
may never silently rewrite its constitution. Astra approved the architecture
direction for commit `b7163d5` and requested two targeted documentation
refinements before freeze. The current revision separates adaptation
eligibility from adaptation activation and defines adaptation conflict
resolution by constitutional precedence, with unresolved conflicts disabled or
held for clarification. Implementation and production changes remain
unauthorized.

---

# Success Criteria

ASTRA-001 succeeds when:

- current implementation and gaps are accurately inventoried;
- Product Owner vision is recorded;
- ownership boundaries are explicit;
- architecture options are critically evaluated;
- a recommended architecture is proposed;
- relationship to Assistant, Knowledge, AI SEO, tools, auth, app APIs, app
  databases, frontend, audit, and providers is defined;
- Phase 1 is reconciled without reopening code;
- risks and validation strategy are documented;
- no implementation occurs; and
- production remains unchanged.

ASTRA-002 succeeds when:

- ASTRA-001 inheritance is explicit;
- the full platform intelligence pipeline is documented;
- each pipeline stage defines purpose, inputs, outputs, ownership, failure
  behavior, security considerations, and future implementation notes;
- the Intelligence Decision Matrix is recorded;
- external intelligence is optional rather than default;
- local response preference is defined;
- refusal and clarification are first-class outcomes;
- no implementation occurs; and
- production remains unchanged.

ASTRA-003 succeeds when:

- ASTRA-001 and ASTRA-002 inheritance is explicit;
- conversation is separated from memory;
- memory is separated from Knowledge;
- context classes and owners are documented;
- conversation state is transient by default;
- context loading is need-driven, minimized, purpose-bound, and isolated;
- context provider authority is preserved;
- contradictory provider context cannot be merged into manufactured consensus;
- context expiration and stale-context behavior are documented;
- clarification cycles are governed;
- privacy and concurrent conversation isolation are documented;
- future interface support remains governed by the same context model;
- no implementation occurs; and
- production remains unchanged.

ASTRA-004 succeeds when:

- ASTRA-001, ASTRA-002, and ASTRA-003 inheritance is explicit;
- capability and tool concepts are separated;
- Tool Registry authority is documented;
- discovery precedes tool selection;
- tool selection precedes execution planning;
- capability existence must be verified before use;
- fabricated capabilities are prohibited;
- capability and tool ownership boundaries are explicit;
- availability, deprecation, experimental, permission-required, and
  owner-mismatch states are documented;
- side-effect, read/write, approval, and dependency metadata are documented;
- permission metadata is separated from live authorization;
- deterministic candidate precedence and ambiguity handling are documented;
- discovery evidence is bounded and reviewable;
- discovery remains provider-independent;
- failure behavior fails closed when capability authority cannot be
  established;
- no implementation occurs; and
- production remains unchanged.

ASTRA-005 succeeds when:

- ASTRA-001, ASTRA-002, ASTRA-003, and ASTRA-004 inheritance is explicit;
- execution plans are declarative and do not execute;
- planner and executor boundaries are preserved;
- action and execution-step concepts are separated;
- read-only, proposal, write, external, administrative, and prohibited actions
  are classified conservatively;
- every state-changing action requires a governed execution step;
- approval and confirmation gates are represented before execution;
- approval requirements survive replanning;
- approval grants do not survive material plan or step change unless approved
  governance proves the change is non-material and scope-preserving;
- state-changing execution steps include stable identity and idempotency
  protection;
- retry, rollback, compensation, cancellation, long-running operation, failure,
  and partial-success states are documented;
- delegation preserves owning-service execution authority;
- execution evidence is bounded and reviewable;
- unknown execution risk fails closed;
- no implementation occurs; and
- production remains unchanged.

ASTRA-006 succeeds when:

- ASTRA-001, ASTRA-002, ASTRA-003, ASTRA-004, and ASTRA-005 inheritance is
  explicit;
- executor and planner boundaries are preserved;
- execution requests are not treated as execution authority;
- executor acceptance and rejection are governed outcomes;
- executor admission is separated from owning-service acceptance;
- execution remains prohibited until owning-service acceptance succeeds;
- live authorization is rechecked before execution;
- owning-service validation remains authoritative;
- plan version, approval binding, and confirmation binding are verified before
  execution;
- stable step identity and idempotency are enforced for state-changing steps;
- timeout is treated as uncertain outcome rather than non-execution;
- retries require outcome reconciliation;
- cancellation handling is governed;
- long-running progress states are represented;
- partial success and compensation reporting are explicit;
- multi-owner execution is non-atomic unless an owning architecture proves
  otherwise;
- stale plans are rejected;
- executor health and owner-service availability are represented separately;
- execution evidence is bounded and reviewable;
- unknown execution state fails closed;
- no implementation occurs; and
- production remains unchanged.

ASTRA-007 succeeds when:

- ASTRA-001 through ASTRA-006 inheritance is explicit;
- external intelligence extends Astra and never replaces Astra;
- local sufficiency is checked before provider selection;
- deterministic tasks are excluded from provider use;
- provider capability classes are documented;
- provider eligibility and routing are provider-independent;
- provider eligibility is separated from provider selection;
- provider selection occurs only within the eligible provider set;
- provider input envelopes are minimized, purpose-bound, and policy-approved;
- prompt governance cannot override parent architecture;
- provider responses are untrusted until validated;
- provider output is advisory intelligence until validated by Astra and
  authoritative owners;
- hallucination boundaries are documented;
- cost and token governance are documented;
- privacy and data minimization are documented;
- provider failure behavior preserves local deterministic behavior;
- provider evidence is bounded and reviewable;
- multi-provider support avoids constitutional vendor dependency;
- no implementation occurs; and
- production remains unchanged.

ASTRA-008 succeeds when:

- ASTRA-001 through ASTRA-007 inheritance is explicit;
- memory is separated from conversation state;
- memory is separated from Knowledge;
- memory is separated from app-owned data;
- conversation state and working memory are transient by default;
- long-term memory and preference memory require approved class, purpose,
  retention, and controls;
- unknown memory classes are prohibited until classified;
- memory ownership is separated from governed references to information owned
  elsewhere;
- memory references cannot transfer ownership or create a second authoritative
  datastore;
- memory eligibility is checked before memory writes;
- memory writes are governed actions rather than silent persistence;
- memory retrieval authorization is separated from memory existence;
- memory retrieval is need-driven, minimized, and purpose-bound;
- memory cannot determine identity, authorization, capability existence,
  execution authority, app facts, or production truth;
- app-owned record copies and shadow summaries are prohibited;
- forgetting, deletion, export, and retention are first-class governance;
- stale or conflicting memory is subordinate to authoritative sources;
- provider interaction inherits ASTRA-007 envelope and authority rules;
- memory evidence is bounded and reviewable;
- privacy and security boundaries are documented;
- no implementation occurs; and
- production remains unchanged.

ASTRA-009 succeeds when:

- ASTRA-001 through ASTRA-008 inheritance is explicit;
- learning is separated from memory;
- adaptation is separated from authority;
- personalization is bounded and explainable;
- user correction outranks inferred preference;
- explicit feedback outranks implicit behavior;
- feedback classes are defined conservatively;
- correction handling preserves authoritative ownership;
- preference evolution is governed;
- adaptation eligibility is checked before behavior changes;
- adaptation eligibility is separated from adaptation activation;
- eligibility alone never activates adaptation;
- adaptation conflict resolution follows constitutional precedence;
- unresolved conflicts are clarified or disabled rather than selected by
  hidden ordering;
- confidence and evidence are represented;
- users can inspect, correct, disable, reset, export, and remove adaptations;
- behavioral drift is detected and prevented;
- reset, revocation, export, and expiration are first-class governance;
- cross-app adaptation boundaries are explicit;
- provider and model boundaries are explicit;
- private-data training is prohibited without separate governance;
- the constitution cannot be learned or silently rewritten;
- unknown adaptation risk fails closed;
- no implementation occurs; and
- production remains unchanged.

---

# Non-Goals

- Phase 2 implementation;
- runtime route changes;
- public API exposure;
- app integration;
- app database access;
- tool execution expansion;
- provider dependency changes;
- migrations;
- frontend changes;
- deployment changes;
- AI SEO implementation changes;
- production authorization; and
- implementation before separate authorization.
