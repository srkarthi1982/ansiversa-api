# Astra AI Conversation And Context Architecture

**Status:** Proposed
**Task:** ASTRA-003
**Parent:** ASTRA-001 Vision And Core Architecture
**Parent:** ASTRA-002 Platform Intelligence Architecture
**Created:** 2026-07-24
**Documentation Authorization:** Approved
**Architecture Authorization:** Approved
**Scope:** Documentation, specification, and architecture review only
**Implementation:** Not authorized
**Production:** Unchanged

---

# Purpose

ASTRA-003 defines how Astra AI manages conversation and context throughout the
governed intelligence pipeline.

ASTRA-003 answers:

```text
How does Astra manage conversation and context throughout the intelligence pipeline?
```

It does not define what Astra is. That belongs to ASTRA-001. It does not
redefine how Astra thinks. That belongs to ASTRA-002.

---

# Parent Architecture

ASTRA-003 inherits the frozen parent architectures:

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
```

ASTRA-003 must not redefine:

- ASTRA-001 Astra identity;
- ASTRA-001 ownership and non-ownership boundaries;
- ASTRA-001 provider boundaries;
- ASTRA-001 execution authority;
- ASTRA-001 production safety rules;
- ASTRA-002 intelligence pipeline;
- ASTRA-002 Intelligence Decision Matrix;
- ASTRA-002 external-intelligence law;
- ASTRA-002 decision-evidence model; or
- the fixed 100-solution-app platform boundary.

If this document conflicts with ASTRA-001 or ASTRA-002, the accepted parent
architecture wins.

---

# Scope Boundary

Allowed:

- define conversation and context concepts;
- define conversation lifecycle;
- define context classification;
- define conversation state model;
- define context assembly model;
- define context provider coordination;
- define context isolation and expiration rules;
- define clarification-cycle representation;
- define privacy, failure, and security boundaries;
- define future implementation notes;
- propose an ADR;
- update iteration planning records; and
- update the AGENTS task log.

Not allowed:

- implementation;
- runtime route changes;
- public API exposure;
- routes;
- provider integration;
- prompt implementation;
- model invocation;
- tool execution changes;
- app integration;
- app database access;
- database changes;
- migrations;
- frontend changes;
- generated artifacts;
- deployment changes; or
- production behavior changes.

---

# Engineering Principles

- Conversation does not equal memory.
- Memory does not equal Knowledge.
- Context must be minimized.
- Context must be purpose-bound.
- Context loading must be need-driven.
- Private context is never loaded for public questions.
- App-owned context remains owned by app services.
- Astra coordinates context but never becomes the owner.
- Context providers remain authoritative for their owned facts.
- Context must remain explainable.
- Context decisions should be reviewable.
- Conversation history must never silently override current user intent.

---

# Engineering Laws

## Law 1 - Conversation State Is Transient By Default

Conversation state is transient unless an independently governed architecture
explicitly defines persistence.

## Law 2 - Context Is Need-Driven

Context is loaded because it is required, not because it is available.

## Law 3 - Smallest Sufficient Context

The smallest sufficient context is the preferred context.

---

# Conversation Lifecycle

```text
Conversation Start
        |
        v
Request Received
        |
        v
Conversation State Read
        |
        v
Context Need Determined
        |
        v
Approved Context Assembled
        |
        v
Pipeline Decision Made
        |
        v
Response / Clarification / Refusal / Proposal
        |
        v
Bounded Evidence Recorded
        |
        v
Conversation State Expires Or Continues
```

A conversation is a bounded interaction sequence between a user and an Astra
surface. It may contain one message, a clarification exchange, or a longer
thread. A conversation is not automatically a durable memory record.

Conversation state exists to help Astra interpret the current request safely.
It must not become an ungoverned store of user preferences, records, secrets,
or hidden behavioral history.

---

# Context Classification

Context is any information Astra uses to interpret, decide, plan, or respond.

| Class | Owner | Examples | Default handling |
|---|---|---|---|
| Request context | User | Current request text, selected language, explicit constraints | Transient and untrusted |
| Conversation context | Astra surface | Current turn, prior clarification, active conversation ID | Transient by default |
| Platform context | Knowledge | app catalog, categories, routes, readiness, public docs | Governed public source |
| User context | Auth/user-context providers | authenticated identity summary, current route, recent apps, preferences summary | Need-driven and minimized |
| App-owned context | App services | app summaries, record previews, workflow state | App-owned contracts only |
| Capability context | Tool Registry | available tool metadata, side-effect class, owner service | Registry-owned metadata |
| Provider context | Astra policy envelope | minimized model input approved for an external provider | Optional and purpose-bound |
| Evidence context | Astra evidence layer | reason codes, source markers, context omissions, decision metadata | Bounded and reviewable |

Private context includes user context, app-owned context, provider-bound
sensitive input, and any data that could identify, expose, or affect a user's
records or rights. Private context must never be loaded for public questions.

---

# Conversation State Model

Conversation state should represent only what is needed to continue a safe
interaction.

Allowed state categories:

- conversation identifier;
- current surface;
- current turn summary;
- prior clarification question and answer;
- active unresolved intent;
- user-visible constraints explicitly supplied in the conversation;
- approved context-source references;
- context expiration markers;
- refusal or escalation state; and
- bounded decision-evidence references.

Disallowed by default:

- raw secrets;
- credentials;
- raw app records;
- hidden prompts;
- unrestricted message history;
- cross-user references;
- inferred long-term preferences;
- provider transcripts retained without approval;
- application database snapshots; and
- silent durable memory.

Conversation state must not override the current user request. If prior
conversation state conflicts with the current request, Astra should ask for
clarification or prefer the current explicit request unless a higher-priority
policy blocks it.

---

# Context Assembly Model

Context assembly follows ASTRA-002 and remains need-driven.

```text
Current Request
        |
        v
Context Need Classification
        |
        v
Public Platform Context Check
        |
        v
User Context Need Check
        |
        v
App-Owned Context Need Check
        |
        v
Provider Envelope Need Check
        |
        v
Smallest Sufficient Context Envelope
```

Assembly rules:

1. Start with the current request and platform Knowledge.
2. Use conversation state only to resolve continuity, not to replace intent.
3. Load user context only when the request cannot be handled publicly.
4. Load app-owned context only through app-owned contracts.
5. Exclude context that is merely available but not required.
6. Attach source, owner, sensitivity, expiration, and omission metadata.
7. Preserve enough evidence to explain why context was loaded or omitted.

The output of assembly is a context envelope. The envelope is an input to
permission evaluation, planning, provider-envelope decisions, and response
construction. It is not an authorization grant.

---

# Context Provider Coordination

Context providers are authoritative for their owned context. Astra coordinates
provider requests; it does not become the source of truth.

| Provider type | Authority | Astra responsibility |
|---|---|---|
| Knowledge provider | Public platform facts | Request approved public context and preserve source markers |
| User context provider | User-scoped summaries | Request minimized context after need is established |
| Auth provider | Identity state | Consume backend-owned identity truth; fail closed if unavailable |
| Authorization provider | Permission and ownership truth | Consume decisions; never infer permission from text |
| App service provider | App-owned summaries or records | Request only approved app contracts; never query app DB directly |
| Tool Registry | Capability metadata | Discover approved capabilities without fabrication |
| Provider-envelope builder | External model input boundary | Build only minimized, purpose-bound, policy-approved envelopes |

Provider coordination must support unavailable, stale, contradictory, denied,
or partial context without forcing execution or provider use.

---

# Context Isolation Rules

Context isolation is mandatory.

Rules:

- each conversation belongs to exactly one authenticated user or anonymous
  public session;
- anonymous conversation context must not become authenticated user context
  unless a separately approved handoff model exists;
- one user's context must never enter another user's conversation;
- app-owned context must remain scoped to the app owner and app contract;
- platform context must remain separate from private context;
- provider envelopes must include only approved context for the current
  purpose;
- concurrent conversations must have independent state and evidence;
- frontend hints cannot merge conversations or grant authority; and
- stale conversation identifiers must not resurrect expired context.

If isolation cannot be verified, Astra must fail closed, ask for
clarification, or answer with public platform context only.

---

# Context Expiration Rules

Every context envelope needs an expiration position.

Expiration can be:

- immediate, for request-only context;
- turn-bound, for one response;
- clarification-bound, for a single clarification cycle;
- conversation-bound, for the active conversation only;
- session-bound, only when separately approved by surface policy; or
- persistent, only when a future accepted architecture explicitly authorizes
  memory persistence.

Default rule:

```text
Conversation context expires unless there is an approved reason to keep it.
```

Expired context must not influence decisions. If stale context may matter,
Astra should reload from the owning provider, ask for clarification, or
disclose that it cannot verify the current state.

---

# Clarification Cycle

Clarification is a governed conversation state, not an implementation failure.

```text
Ambiguous Request
        |
        v
Clarification Question
        |
        v
User Answer
        |
        v
Intent Re-evaluation
        |
        v
Context Need Re-evaluation
        |
        v
Governed Response
```

Clarification state may include:

- unresolved intent;
- ambiguity reason;
- question asked;
- allowed answer scope;
- context withheld until clarification;
- user answer summary; and
- expiration marker.

Clarification must not be used to pressure the user into sharing private data.
If the request can be answered safely without private context, Astra should
prefer the less invasive path.

---

# Privacy Model

Privacy is enforced through minimization, ownership, isolation, purpose, and
expiration.

Privacy rules:

- do not load private context for public questions;
- do not retain conversation history as memory by default;
- do not send original user text to providers unless the provider envelope
  allows it;
- do not store raw prompts, credentials, secrets, or raw app records in
  decision evidence;
- do not let previous conversation turns silently expand current context;
- do not mix anonymous and authenticated context without approved handoff;
- do not use app-owned context outside the app-owned contract purpose; and
- do not keep provider outputs as memory without a future approved memory
  architecture.

Privacy violations must block context use and may require refusal or
escalation.

---

# Failure Behaviour

Astra must handle context failures explicitly.

| Failure | Required behavior |
|---|---|
| Missing conversation state | Continue from current request or ask clarification |
| Expired context | Reload from owner, ask clarification, or omit |
| Missing platform context | State limitation or escalate rather than invent |
| Missing user context | Answer publicly, ask sign-in, clarify, or refuse |
| Missing app-owned context | Explain that the app-owned information is unavailable |
| Authorization unavailable | Fail closed |
| Provider context not approved | Use local path, clarify, or refuse |
| Conflicting context | Ask clarification or prefer authoritative owner source |
| Cross-user risk | Refuse or fail closed |

Failure behavior must be visible enough for review without exposing sensitive
internals.

---

# Security Considerations

Conversation and context architecture must protect against:

- prompt injection through user text;
- previous-turn instruction override;
- context smuggling through frontend hints;
- cross-user context leakage;
- app-database overreach;
- provider-envelope expansion;
- hidden durable memory;
- stale context influencing current decisions;
- unbounded conversation history;
- unclear ownership for app facts;
- context evidence leaking secrets; and
- voice, search, chat, or multimodal surfaces bypassing the same rules.

All future interfaces must use the same context governance model. A voice,
search, chat, notification, or multimodal surface may change input format, but
it must not change ownership, authorization, minimization, or evidence rules.

---

# Future Implementation Notes

Future implementation must separately define:

- conversation identifiers and lifecycle state;
- request and context envelope schemas;
- context sensitivity labels;
- owner and source metadata;
- expiration and stale-context checks;
- clarification state schema;
- provider coordination interfaces;
- evidence envelope fields;
- context omission reason codes;
- concurrent conversation isolation tests;
- no-private-context-for-public-question tests;
- no-cross-user-context tests;
- no-silent-memory tests; and
- disabled-by-default production gates.

Future implementation may support chat, voice, search, contextual UI, and
multimodal interfaces only when those surfaces consume the same approved
conversation and context contracts.

No implementation is authorized by ASTRA-003.

---

# ADR

The proposed ADR for ASTRA-003 is:

```text
docs/architecture/decisions/astra-ai-conversation-context-architecture.md
```

The ADR remains Proposed until Astra architecture review is complete and
Product Owner approval is explicitly recorded.

---

# Risks

| Risk | Level | Mitigation |
|---|---|---|
| Conversation history becomes hidden memory | Critical | Conversation state is transient unless a separate memory architecture authorizes persistence |
| Available context is loaded without need | Critical | Context loading is need-driven and smallest sufficient context is preferred |
| Private context leaks into public answers | Critical | Public questions must not trigger private context loading |
| Prior turns override current user intent | High | Current explicit request wins unless clarification or policy blocks it |
| Context providers lose ownership | High | Providers remain authoritative and Astra only coordinates context |
| App-owned facts bypass app services | Critical | App context enters only through app-owned contracts |
| Stale context causes wrong decisions | High | Expiration markers and stale-context handling are required |
| Concurrent conversations mix context | Critical | Conversation state and evidence are isolated by conversation and user/session |
| Provider envelopes expand silently | Critical | Provider context remains optional, minimized, purpose-bound, and policy-approved |
| Evidence leaks sensitive context | High | Evidence uses bounded metadata and omission markers, not raw secrets or records |

---

# Validation Strategy

ASTRA-003 validation is documentation-only.

Required evidence:

- ASTRA-003 inherits ASTRA-001 and ASTRA-002 explicitly;
- required sections are present;
- conversation is separated from memory;
- memory is separated from Knowledge;
- context classes have owners;
- private context is forbidden for public questions;
- context loading is need-driven and minimized;
- app-owned context remains app-owned;
- provider context remains optional and envelope-bound;
- context expiration rules are documented;
- clarification cycle is documented;
- concurrent conversation isolation is documented;
- failure behavior is explicit;
- future implementation remains unauthorized; and
- no non-documentation files are modified.

Validation commands:

```bash
git diff --check
git diff --name-only
test "$(git diff --name-only | grep -Ev '^(AGENTS.md|docs/)' | wc -l)" = "0"
```

No tests, compile checks, migrations, OpenAPI generation, frontend builds, or
runtime verification are required because ASTRA-003 is documentation-only.

---

# Status Boundary

```text
ASTRA-003               Proposed
Parent                  ASTRA-001 Accepted
Parent                  ASTRA-002 Accepted
Documentation Auth      Approved
Architecture Auth       Approved
Discovery               Complete
Specification           Complete
Architecture Review     Pending Astra Review
Product Owner Approval  Pending
ADR                     Proposed
Implementation          Not authorized
Production              Unchanged
```
