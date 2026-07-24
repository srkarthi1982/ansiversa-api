# Astra AI Vision And Core Architecture

**Status:** Approved and Frozen
**Task:** ASTRA-001
**Created:** 2026-07-24
**Approved:** 2026-07-24
**Frozen:** 2026-07-24
**Scope:** Documentation, discovery, specification, and architecture review only
**Architecture Review:** Approved
**Product Owner Approval:** Approved
**ADR:** Accepted
**Implementation:** Not authorized
**Production:** Unchanged

---

# Purpose

ASTRA-001 defines the constitutional architecture for Astra AI before any
Phase 2 implementation, conversation redesign, memory expansion, tool
selection, planning, execution, or app rollout begins.

This document defines what Astra AI is, what it owns, what it must never own,
how it fits inside Ansiversa, and how it may mature through separately
authorized stages.

---

# Product Owner Vision

Astra AI is all of the following:

- a conversational assistant;
- a platform assistant;
- the intelligent operating layer of Ansiversa;
- a workflow orchestrator;
- a trusted digital employee; and
- the future operating intelligence of the Ansiversa ecosystem.

A chatbot is only one interface. Astra AI may eventually be accessed through
chat, voice, search, contextual assistance, notifications, approved automation,
workflow interfaces, and future governed APIs.

The long-term product direction is therefore not "add a chat box." The
direction is to create a governed intelligence layer that can understand the
platform, explain it, coordinate approved capabilities, and eventually help
operate workflows without violating ownership, consent, or safety boundaries.

---

# Current State Findings

Astra AI is not starting from zero. The repository already contains:

- the existing `/api/v1/assistant` user-facing Assistant route and service;
- deterministic Assistant retrieval over the governed Knowledge registry;
- the frozen Astra AI Platform Phase 1 foundation under `app/modules/astra_ai`;
- the Astra Tool Framework and Tool Registry;
- the Platform User Context Provider;
- Astra user-data awareness and app-integration governance contracts;
- limited Quiz and Course Tracker pilot tools, still gated by
  `ASTRA_PERSONAL_DATA_TOOLS_ENABLED=false`;
- the Canonical AI Knowledge Registry with 100 public apps and 14 categories;
- public Knowledge publishing and AI SEO artifacts;
- AI SEO compiler architecture and frozen implementation phases; and
- operational-readiness gates for personal-data execution.

Architectural gaps remain:

- no accepted constitutional definition of Astra AI existed before ASTRA-001;
- the relationship between the existing Assistant and future Astra AI needed a
  durable boundary;
- the maturity path from platform guidance to digital-employee behavior needed
  explicit review gates;
- action execution, memory, external providers, and app integrations needed
  permanent non-default boundaries;
- risk ownership across Knowledge, AI SEO, tools, auth, app services, and
  frontend interfaces needed a single map; and
- Phase 1 needed reconciliation with the long-term architecture without
  reopening its frozen code.

The fixed 100-solution-app catalog boundary remains permanent. ASTRA-001 does
not authorize App #101, app replacement, or app-level Astra rollout.

Existing Quiz and Course Tracker pilots are pre-existing evidence and remain
under their existing disabled/gated governance. Their existence does not
authorize new app integration, Stage 3 tool selection, Stage 5 execution, or
broader rollout.

---

# Identity

Astra AI is a platform intelligence layer for Ansiversa.

It is simultaneously:

- a product capability experienced by users;
- an assistant interface when accessed through chat or similar UI;
- an orchestration layer over approved platform context and capabilities;
- a policy-governed planning layer for future action proposals;
- a coordination layer for approved tools and app-owned services; and
- a long-term operating intelligence for the Ansiversa ecosystem.

Astra AI is not merely an external chatbot. It is also not a replacement for
the existing Assistant route, Knowledge registry, AI SEO compiler,
authentication system, authorization system, app APIs, or app databases.

## Permanent Responsibilities

Astra AI permanently owns:

- conversation interpretation;
- platform intent resolution;
- context assembly from approved sources;
- safety and policy evaluation;
- capability discovery;
- planning and response shaping;
- action proposal contracts;
- tool coordination lifecycle;
- audit evidence;
- refusal, clarification, and escalation behavior; and
- governed responses.

## Future Evolution

Astra AI may later evolve into:

- context-aware assistance across platform workflows;
- governed capability and tool selection;
- action planning with user-visible explanations;
- controlled execution under explicit authorization;
- cross-app orchestration through app-owned contracts;
- voice and contextual UI assistance;
- internal operator support; and
- trusted digital-employee behavior.

Every evolution requires explicit Product Owner authorization and Astra
architecture review before implementation.

## Relationship To Existing Assistant

The existing Assistant is the current user-facing entry point and runtime
surface. Astra AI is the broader governed intelligence architecture that should
eventually organize and constrain Assistant behavior.

The recommended path is not to discard the existing Assistant. The path is to
evolve it into a consumer of Astra AI's governed contracts, context,
orchestration, policy, and evidence layers through separately authorized
implementation phases.

---

# Ownership Boundary

## Astra AI Owns

| Area | Astra AI responsibility |
|---|---|
| Conversation interpretation | Normalize user requests into bounded platform or capability intents. |
| Platform intent resolution | Classify platform, account, navigation, pricing, policy, and capability requests. |
| Context assembly | Request only approved platform/user/app summaries through governed providers. |
| Policy evaluation | Fail closed before private data access, execution, provider calls, or tool use. |
| Capability discovery | Discover approved tools and capability metadata without inventing capabilities. |
| Planning | Produce explainable plans and action proposals before execution. |
| Action proposals | Describe proposed actions, required authority, impact, and execution status. |
| Tool coordination | Select and coordinate approved tools through the registry/executor boundary. |
| Audit evidence | Record deterministic, bounded decision evidence without raw secrets or records. |
| Governed responses | Assemble answers, clarifications, refusals, and escalation messages. |

Coordination ownership is not execution authority. Astra AI may select,
propose, sequence, and observe approved tools. The Tool Executor and app-owned
service remain responsible for validating tool arguments, rechecking
authorization, enforcing app business rules, executing the operation,
committing data, and returning bounded results. An Astra plan is never
execution authority.

## Astra AI Does Not Own

Astra AI does not own:

- user application records;
- application databases;
- authentication truth;
- authorization truth;
- payment truth;
- app business rules;
- app calculations;
- app validation;
- Knowledge publishing;
- AI SEO publishing;
- production deployment;
- arbitrary long-term user data;
- hidden memory stores;
- app-specific UI ownership; or
- production enablement.

Permanent rule:

```text
Refuse to store, access, or mutate what Astra AI does not own.
```

---

# Architectural Position

```text
User Interfaces
        ↓
Astra AI
        ↓
Platform Context / Knowledge / Policies / Capabilities
        ↓
Governed Tools and Services
        ↓
Platform and Solution Apps
```

Astra AI consumes Knowledge. It may consume AI SEO artifacts where appropriate
for public platform truth and machine-readable public projections. It uses
platform APIs and governed tools. It does not replace the Knowledge system,
replace AI SEO, directly own app databases, or bypass app contracts.

The correct dependency direction is:

```text
Knowledge and app-owned services provide approved facts.
Astra AI interprets, plans, coordinates, and explains.
Execution remains gated by policy, ownership, consent, and authorization.
```

---

# Core Engineering Laws

## Law 1 - Permission Before Capability

Astra AI may only use capabilities that are approved, registered, enabled,
authorized for the current user, and appropriate for the current intent.

## Law 2 - Ownership Is Explicit

Every fact, tool, action, memory, and output must have a named owner. Astra AI
must not take ownership by convenience.

## Law 3 - Authorization Fails Closed

Missing, ambiguous, stale, contradictory, or unavailable authorization blocks
access and execution.

## Law 4 - No Hidden Execution

Astra AI must never create, update, delete, send, schedule, pay, publish, or
trigger workflow changes invisibly.

## Law 5 - Proposals Must Be Explainable

Every action proposal must explain the intended action, source capability,
required permission, affected scope, execution status, and confirmation need.

## Law 6 - Evidence Is Deterministic Where Required

Policy decisions, intent decisions, context-source use, refusals,
clarifications, and action proposals must be auditable through bounded evidence
that can be reproduced for the same governed inputs where determinism is
required.

## Law 7 - Human Approval For High-Impact Actions

High-impact or irreversible actions require explicit confirmation and may
require Product Owner, operator, or administrative approval.

## Law 8 - User Isolation Is Non-Negotiable

Astra AI must never allow prompts, tool arguments, model output, frontend
context, or inferred identity to cross user boundaries.

## Law 9 - Least Privilege Context

Astra AI receives the smallest approved context needed for the current intent.
It must not load personal context for public, identity, or safety answers.

## Law 10 - No Fabricated Capabilities

Astra AI must not claim it can use, execute, schedule, integrate, or automate a
capability unless that capability is approved and discoverable through governed
metadata.

## Law 11 - No Silent Data Retention

Astra AI must not silently retain prompts, records, tool outputs, profile data,
or long-term memory. Any persistence requires approved purpose, retention,
deletion, export, and audit controls.

## Law 12 - Production Safety Is Separate

Implemented, tested, reviewed, and even frozen architecture does not authorize
production activation. Production launch requires separate readiness and
Product Owner authorization.

## Law 13 - Decisions Are Auditable

Allowed, denied, failed, unavailable, clarified, proposed, and executed
outcomes require bounded decision evidence appropriate to their risk level.

## Law 14 - Reversibility Before Execution

Any execution path must define cancellation, rollback, or compensating behavior
before production use, unless the Product Owner explicitly accepts the
irreversibility risk.

## Law 15 - External Model Input Is A Governed Envelope

Astra AI must never send unrestricted platform context, database records,
credentials, authorization objects, internal prompts, raw tool outputs, or
unrelated conversation history to an external model provider.

External provider input must be:

- purpose-bound;
- minimized;
- owner-authorized;
- policy-approved;
- classified for sensitivity;
- auditable; and
- removable from the request when not required.

The provider may interpret or phrase approved information. It may not
independently retrieve Ansiversa data or determine factual truth. Sending the
user's original text to a provider is a deliberate data-processing decision
governed by privacy, retention, provider configuration, and disclosure. It is
not an automatic assumption.

---

# Capability Evolution

| Stage | Maturity | Description | Authorization gate |
|---|---|---|---|
| 1 | Platform guidance | Public platform, catalog, category, route, policy, and help guidance. | Frozen Phase 1 foundation plus approved runtime scope. |
| 2 | Context-aware assistance | Minimal/personalized platform context such as current route, recent apps, activity, and notifications. | Context contract, privacy review, and user-control review. |
| 3 | Capability and tool selection | Select approved tools from registry metadata. | Tool registry review, tool docs, and execution gate review. |
| 4 | Action planning | Produce explainable plans and proposed actions without execution. | Planning contract, impact model, and confirmation policy. |
| 5 | Controlled execution | Execute approved low-risk actions through governed tools. | Persistent audit, consent, readiness, rollback, and production approval. |
| 6 | Cross-app orchestration | Coordinate multiple app-owned capabilities without centralizing app data. | Per-app contracts, owner isolation, conflict policy, and certification. |
| 7 | Trusted digital employee behavior | Act as an accountable digital operator under strict scopes and supervision. | Operational controls, delegation model, monitoring, escalation, and Product Owner authorization. |

Every stage requires explicit review and authorization. No stage implies
approval for the next one.

---

# User Model

## Anonymous Visitor

May receive public platform, catalog, category, pricing, policy, help, and
navigation guidance. Must not receive private account, subscription, app
record, or personalized context.

## Authenticated User

May receive approved owner-scoped context only through backend-authenticated
identity and governed providers. Authentication proves identity; it does not
automatically authorize every data category or action.

## Subscribed User

May receive capabilities allowed by the subscription system only when
subscription status is provided by the payment/subscription source of truth.
Astra AI must not infer subscription rights.

## Administrative Or Internal User

May later receive operator-only assistance only through explicit admin
authorization, audit, and role-scoped controls. ASTRA-001 does not authorize an
admin Astra surface.

## Future Delegated Actor

Delegated access requires a separate tenant/delegation model, explicit
authority, revocation, audit, and Product Owner approval. Astra AI must not
infer delegated rights from natural-language claims.

Authentication and authorization remain external sources of truth.

---

# App Boundary

Approved current decision:

```text
Platform-level Astra AI is the immediate focus.

Individual integration with the 100 solution apps is deferred.

No app-level Astra AI rollout is authorized by ASTRA-001.
```

Future app integrations must be governed by:

- app-owned `astra-ai.md` contracts;
- app-owned tools and service methods;
- owner-scoped authentication;
- minimal response contracts;
- explicit privacy exclusions;
- focused tests for cross-user denial;
- tool registry metadata;
- disabled-by-default production gates;
- persistent audit readiness before personal-data production use; and
- one-app-at-a-time authorization.

The central Astra layer must never import app models or query app databases
directly to compensate for missing app contracts.

---

# Human Control

Astra AI must ask for clarification when:

- the intent is ambiguous;
- the requested object, app, user, or action target is unclear;
- multiple capabilities could apply with different outcomes;
- context is stale, unavailable, or contradictory; or
- the user asks for a capability that is not safely mapped.

Astra AI must propose instead of execute when:

- action execution is not authorized;
- the action is future scope;
- the action has side effects;
- the impact cannot be fully verified;
- the app contract supports planning but not execution; or
- confirmation or approval is required.

Astra AI must request confirmation when:

- any mutation may occur;
- a notification, message, payment, schedule, deletion, publication, or sharing
  action is possible;
- sensitive or regulated context is involved; or
- an action cannot be fully undone.

Astra AI must refuse when:

- authorization fails;
- the request crosses user boundaries;
- the request requires data Astra does not own or cannot access;
- the request conflicts with higher-priority instructions;
- a user asks for secrets, internal prompts, credentials, or private records;
- a capability is fabricated or unavailable; or
- execution would bypass app contracts.

Astra AI must escalate when:

- Product Owner approval is required;
- operator review is required;
- policy conflict cannot be resolved automatically;
- a high-impact action is requested; or
- safety, legal, medical, financial, or security boundaries require human
  review.

Astra AI must remain read-only until a specific execution stage is approved and
the relevant operational-readiness gates pass.

---

# Success Definition

Astra AI success is not measured only by response fluency.

Success means:

- correct answers grounded in approved platform truth;
- useful guidance that reduces user effort;
- consistent policy compliance;
- user trust through transparency and predictable behavior;
- explainable action proposals;
- safe execution only when separately authorized;
- platform consistency across interfaces;
- low false-action and false-capability rate;
- no unauthorized access;
- no cross-user leakage;
- minimized and bounded context use;
- traceable decisions;
- reversible or approved irreversible action handling; and
- production behavior matching reviewed architecture.

---

# Relationship To Existing Systems

| System | Relationship |
|---|---|
| Existing Assistant routes and services | Current runtime entry point. Future Astra implementation should evolve this surface rather than create a competing assistant without approval. |
| Assistant tools and tool registry | Approved capability discovery and execution metadata source. Astra AI coordinates through this boundary, not raw function calls. |
| Knowledge registry and public Knowledge | Governed platform truth source. Astra consumes it; it does not publish or replace it. |
| Authentication and authorization | External truth. Astra receives backend-owned context and must fail closed when authority is missing. |
| AI SEO compiler and artifacts | Public-truth projection and machine-readable discovery layer. Astra may consume approved public artifacts but must not replace AI SEO publishing. |
| Search and command palette | Potential future UI surfaces. They should call governed Astra contracts rather than invent separate intent logic. |
| App APIs | Approved access path for app-owned capabilities when app contracts authorize it. |
| App databases | Out of scope for direct Astra access. App modules own queries, models, and records. |
| Frontend | Interface layer only. Frontend may provide validated hints but never identity, permission, or private data authority. |
| Audit and logging | Astra produces bounded evidence. Persistent personal-data audit remains a readiness gate. |
| Future external model providers | Explanation or reasoning providers only inside a policy-approved model input envelope. Providers never receive unrestricted backend context and never determine identity, permission, ownership, factual truth, or final authority. |

---

# Phase 1 Reconciliation

Frozen Astra AI Platform Phase 1 already satisfies these ASTRA-001 principles:

- disabled-by-default foundation;
- no runtime route or startup registration;
- no public API exposure;
- governed Knowledge registry-derived platform context;
- internal request/response contracts;
- platform intent vocabulary;
- fail-closed policy layer;
- clarification/refusal behavior;
- action proposal without execution;
- deterministic audit evidence;
- no app database access;
- no external AI provider dependency;
- no frontend, migration, deployment, or production behavior change.

Provisional Phase 1 areas:

- the internal package is not yet wired to the existing Assistant runtime;
- action proposals are contract-level only;
- audit evidence is internal and not persisted;
- context is platform-level, not app-record-aware;
- matching and policy are V1 scaffolding, not a complete mature policy engine;
- external provider boundaries are not expanded beyond existing Assistant work.

Potential later alignment work:

- decide how the existing Assistant route consumes Astra AI contracts;
- reconcile duplicate intent terminology between Assistant service and
  `app/modules/astra_ai`;
- define persistent audit storage before any personal-data execution;
- formalize capability metadata needed for planning and execution stages;
- define interface contracts for chat, search, voice, and contextual UI; and
- update app-integration governance before any new app rollout.

ASTRA-001 does not reopen or modify frozen Phase 1 code.

---

# Architecture Options

## Option 1 - Extend The Existing Assistant Incrementally Without Separate Architecture

Benefits:

- fastest path to visible improvements;
- reuses current route and service;
- avoids new package boundaries in the short term.

Risks:

- policy, planning, tool selection, memory, and execution could accrete inside
  one service;
- difficult to separate interface behavior from platform intelligence;
- long-term governance may depend on code conventions rather than architecture.

Duplication:

- low immediate duplication, but high risk of hidden duplication as features
  expand.

Migration impact:

- low initially; harder later if the Assistant becomes too broad.

Governance implications:

- weak constitutional boundary; high review burden per feature.

Maintainability:

- acceptable for small assistant features, risky for operating-intelligence
  evolution.

## Option 2 - Create An Entirely Independent Astra AI Subsystem

Benefits:

- clean conceptual separation;
- easier to design ideal contracts;
- avoids legacy Assistant constraints.

Risks:

- duplicates existing Assistant, Knowledge, tool, auth, and context work;
- may create competing runtime surfaces;
- migration complexity increases;
- user experience may fragment.

Duplication:

- high.

Migration impact:

- high; would require careful cutover or parallel behavior.

Governance implications:

- strong boundary but poor reuse discipline.

Maintainability:

- risky because two intelligence paths may drift.

## Option 3 - Governed Intelligence Layer Over Existing Foundations

Benefits:

- reuses Assistant, Knowledge, auth, user context, tool registry, AI SEO, and
  app-service foundations;
- creates a durable constitutional layer;
- supports staged evolution;
- reduces duplication while preserving governance;
- keeps production behavior unchanged until authorized.

Risks:

- requires careful migration from current Assistant internals;
- needs clear naming so "Assistant" and "Astra AI" are not confused;
- coordination across many existing systems requires disciplined reviews.

Duplication:

- low if implementation follows the dependency direction.

Migration impact:

- moderate and controllable through staged adoption.

Governance implications:

- strongest balance of reuse, reviewability, and long-term control.

Maintainability:

- recommended. This option lets Astra AI mature without bypassing existing
  ownership boundaries.

## Option 4 - External Provider-Driven Chatbot

Benefits:

- fastest apparent AI capability;
- provider handles much language behavior;
- lower initial backend design effort.

Risks:

- provider coupling;
- weak ownership and policy boundaries;
- possible prompt-driven permission bypass;
- poor auditability;
- capability hallucination;
- risk of exposing context before governance is ready.

Duplication:

- medium to high, because provider prompts duplicate platform rules.

Migration impact:

- high if later replaced by governed platform architecture.

Governance implications:

- unacceptable for Ansiversa operating intelligence.

Maintainability:

- poor.

## Option 5 - Defer Architecture And Evolve Through Implementation

Benefits:

- avoids upfront architecture time;
- lets code experiments reveal needs.

Risks:

- repeats expensive governance corrections later;
- encourages opportunistic app integrations;
- may blur AI SEO, Knowledge, Assistant, and Astra responsibilities;
- hidden execution or memory may appear before policy is ready.

Duplication:

- unpredictable and likely.

Migration impact:

- high because boundaries would be retrofitted.

Governance implications:

- unacceptable after Phase 1 freeze.

Maintainability:

- poor.

## Recommendation

Adopt Option 3: a governed Astra AI intelligence layer over existing Assistant,
Knowledge, tool, authentication, and platform foundations, evolving in
controlled stages.

This recommendation is accepted as the ASTRA-001 constitutional architecture
for Astra AI. Later architecture documents must inherit these boundaries rather
than redefine them.

---

# Risks

| Risk | Level | Mitigation |
|---|---|---|
| Overlap with existing Assistant | High | Define Assistant as current runtime surface and Astra AI as governed intelligence layer. |
| Duplicate orchestration layers | High | Migrate by staged adoption; avoid parallel runtime paths without approval. |
| Uncontrolled AI-provider coupling | Critical | Providers receive only policy-approved, minimized, purpose-bound model input envelopes and never own identity, permission, facts, actions, or final authority. |
| Permission bypass | Critical | Backend-owned auth context, fail-closed policy, and tool executor gates. |
| App-database overreach | Critical | App modules own all app records and queries. |
| Hidden execution | Critical | Action proposal and confirmation laws before any execution. |
| Long-term memory risk | High | No silent retention; persistence requires approved controls. |
| Cross-user leakage | Critical | Owner-scoped contracts, no caller-controlled identity, negative tests. |
| Capability hallucination | High | Registry-backed capability discovery only. |
| Audit-data leakage | High | Bounded metadata; no raw prompts, records, secrets, SQL, or stack traces. |
| Excessive centralization | High | Applications own capabilities and business rules. |
| Production activation before readiness | Critical | Separate readiness review and Product Owner production authorization. |
| Confusing Astra AI with AI SEO | Medium | Knowledge/AI SEO publish truth; Astra consumes and orchestrates. |
| Frontend coupling too early | Medium | Interface contracts follow architecture; frontend hints are not authority. |

---

# Unresolved Questions

- Which existing Assistant internals should be first to consume Astra AI
  contracts in a future authorized phase?
- What persistent audit sink should be used before personal-data execution?
- What user controls are required for contextual assistance and memory?
- Which interfaces should be prioritized after chat: search, contextual UI, or
  notifications?
- What exact threshold separates low-risk from high-impact execution?
- How should subscribed-user entitlements be represented to Astra without
  coupling to payment internals?
- What operational role model is needed for future internal/operator Astra
  assistance?

---

# Status Boundary

```text
ASTRA-001               Approved
Discovery               Complete
Specification           Complete
Architecture Review     Approved
Product Owner Approval  Approved
ADR                     Accepted
ASTRA-001 Freeze        Approved
Implementation          Not authorized
Production              Unchanged
Phase 2                 Documentation only next; requires separate authorization
```
