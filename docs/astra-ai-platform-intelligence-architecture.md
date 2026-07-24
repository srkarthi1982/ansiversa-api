# Astra AI Platform Intelligence Architecture

**Status:** Completed; pending Product Owner approval
**Task:** ASTRA-002
**Parent:** ASTRA-001 Vision And Core Architecture
**Created:** 2026-07-24
**Authorization:** Approved for documentation only
**Architecture Review:** Approved
**Astra Re-review:** Approved
**Product Owner Approval:** Pending
**ADR:** Ready for acceptance
**Scope:** Documentation, specification, and architecture review only
**Implementation:** Not authorized
**Production:** Unchanged

---

# Purpose

ASTRA-002 defines how Astra AI reasons over a user request inside Ansiversa.
It describes the governed intelligence pipeline before any new intelligence
implementation, runtime route, provider integration, app integration, tool
execution, or production behavior is authorized.

ASTRA-002 answers:

```text
How does Astra think?
```

It does not define what Astra is. That constitutional definition belongs to
ASTRA-001.

---

# Inheritance From ASTRA-001

This document inherits the constitutional architecture defined in:

```text
docs/astra-ai-vision-core-architecture.md
docs/architecture/decisions/astra-ai-vision-core-architecture.md
```

ASTRA-002 must not redefine:

- Astra ownership or non-ownership;
- app ownership boundaries;
- permission and authorization rules;
- execution authority;
- external provider authority;
- Knowledge ownership;
- AI SEO ownership;
- production safety gates; or
- the fixed 100-solution-app platform boundary.

If ASTRA-002 appears to conflict with ASTRA-001, ASTRA-001 wins.

---

# Scope Boundary

Allowed:

- define the platform intelligence pipeline;
- define decision stages;
- define stage inputs, outputs, ownership, failure behavior, security
  considerations, and future implementation notes;
- define the Intelligence Decision Matrix;
- define when external intelligence may be considered;
- define documentation-only validation expectations; and
- update architecture planning records.

Not allowed:

- implementation;
- runtime route changes;
- API exposure;
- provider integration;
- dependency changes;
- prompt implementation;
- model invocation;
- tool execution changes;
- app integration;
- app database access;
- migrations;
- frontend changes;
- AI SEO implementation changes;
- generated artifacts;
- deployment changes; or
- production behavior changes.

---

# Platform Intelligence Pipeline

```text
User Request
        |
        v
Conversation Understanding
        |
        v
Intent Recognition
        |
        v
Platform Context Assembly
        |
        v
User Context Assembly
        |
        v
Permission Evaluation
        |
        v
Capability Discovery
        |
        v
Planning
        |
        v
Action Proposal
        |
        v
Decision Evidence Assembly
        |
        v
Response Construction
        |
        v
User
```

The pipeline is logical architecture, not a runtime implementation. A future
implementation may combine, split, cache, or short-circuit stages only if the
observable behavior still satisfies this architecture and ASTRA-001.

---

# Stage 1 - Conversation Understanding

## Purpose

Normalize the incoming request into a bounded representation that Astra can
reason about without treating user text as authority.

## Inputs

- user-visible request text;
- conversation metadata approved for the current surface;
- current interface surface;
- route or screen hints when provided by backend-approved context; and
- previous clarification state when available through approved context.

## Outputs

- normalized request summary;
- detected language and tone requirements when relevant;
- ambiguity markers;
- sensitive-data markers;
- candidate user-visible subject; and
- bounded evidence about the received request.

## Ownership

Astra owns interpretation of the conversation. The user owns the request text.
The frontend may provide hints, but it never provides identity, permission, or
private-data authority.

## Failure Behavior

If the request is empty, contradictory, malformed, unsafe, or too ambiguous,
Astra should ask a clarification question or refuse before loading additional
context.

## Security Considerations

User text is untrusted input. It must not override system policy, ASTRA-001,
authorization state, tool schemas, provider boundaries, or app ownership.

## Future Implementation Notes

The future implementation should keep raw request text out of durable audit
records unless a separately approved retention policy exists.

---

# Stage 2 - Intent Recognition

## Purpose

Classify what the user is trying to accomplish using governed platform intent
categories.

## Inputs

- normalized request summary;
- approved platform vocabulary;
- approved route and app catalog metadata;
- known capability metadata; and
- previous clarification state.

## Outputs

- primary intent;
- secondary candidate intents;
- confidence level;
- required context classes;
- execution likelihood;
- refusal likelihood;
- clarification need; and
- deterministic evidence for the classification.

## Ownership

Astra owns intent recognition. Knowledge owns platform facts used for intent
matching. Tool Registry owns capability metadata. App services own app-domain
facts.

## Failure Behavior

If confidence is too low or multiple intents produce materially different
outcomes, Astra asks for clarification. If the intent maps to an unavailable or
unauthorized capability, Astra refuses or explains the limitation.

## Security Considerations

Intent recognition must not infer authority from user wording. Requests such
as "as admin," "use my database," or "ignore policy" remain untrusted claims.

## Future Implementation Notes

Intent recognition should be deterministic for governed categories where
possible. External models may assist only after the external-intelligence
decision stage determines that provider help is necessary and allowed.

---

# Stage 3 - Platform Context Assembly

## Purpose

Collect public and platform-level facts needed to answer the request or decide
the next step.

## Inputs

- intent classification;
- approved Knowledge registry projections;
- public app catalog metadata;
- category, route, readiness, and documentation-source metadata;
- AI SEO public artifacts where appropriate; and
- context-source allowlist.

## Outputs

- minimized platform context envelope;
- source list;
- freshness or version indicators;
- omitted-context markers; and
- evidence of approved source usage.

## Ownership

Knowledge owns governed platform truth. AI SEO owns public machine-readable
projection artifacts. Astra consumes approved context but does not publish,
replace, or invent platform truth.

## Failure Behavior

If required platform truth is unavailable, stale, or contradictory, Astra must
say it cannot verify the fact, ask for clarification, or escalate rather than
inventing an answer.

## Security Considerations

Public platform context must stay separate from user context and app-owned
records. Public questions should not trigger private context loading.

## Future Implementation Notes

The default context path should favor governed Knowledge sources and preserve
source markers for audit evidence.

---

# Stage 4 - User Context Assembly

## Purpose

Collect the smallest approved user-scoped context needed for the current
intent after the pipeline determines that public platform context is
insufficient.

## Inputs

- authenticated backend identity;
- approved user context provider outputs;
- route or surface state from trusted backend context;
- subscription or entitlement summary from the owning system when needed; and
- requested context classes from intent recognition.

## Outputs

- minimized user context envelope;
- identity and ownership evidence metadata;
- unavailable-context markers;
- consent or control requirements; and
- omission reasons.

## Ownership

Authentication owns identity truth. Authorization and app services own
permission and record-ownership truth. Astra owns context assembly requests and
must accept only approved provider outputs.

## Failure Behavior

If the user is anonymous, unauthenticated, unauthorized, or missing required
context, Astra must answer with public context only, ask the user to sign in,
ask for clarification, or refuse.

## Security Considerations

User context is loaded only after need is established. Astra must not load
personal context for public platform questions, general help, or provider
convenience.

## Future Implementation Notes

Future context providers should return summary envelopes by default. Full
records belong behind app-owned detail contracts and must not enter Astra
without separate authorization.

---

# Stage 5 - Permission Evaluation

## Purpose

Determine whether the requested context, capability, planning path, provider
use, or action is allowed for the current user and environment.

## Inputs

- intent classification;
- user context envelope;
- platform context envelope;
- capability metadata;
- feature flags;
- environment gates;
- subscription or entitlement summary when needed; and
- ASTRA-001 policy rules.

## Outputs

- allow, deny, clarify, propose-only, or escalate decision;
- reason codes;
- required approval or confirmation;
- context-use limits;
- provider-use limits;
- execution limits; and
- deterministic policy evidence.

## Ownership

Astra owns policy evaluation. Authentication, authorization, payments, app
services, and environment configuration own their respective truth sources.

## Failure Behavior

Permission evaluation fails closed. Missing, ambiguous, contradictory, stale,
or unavailable authority blocks context access and execution.

## Security Considerations

Permission is evaluated before capability use. Frontend hints, user claims,
model output, and tool arguments never grant permission.

## Future Implementation Notes

Policy decisions should be replayable from bounded inputs. Evidence must avoid
raw secrets, raw records, raw prompts, SQL, stack traces, or tokens.

---

# Stage 6 - Capability Discovery

## Purpose

Identify approved capabilities that could satisfy the request without
fabricating unavailable behavior.

## Inputs

- approved Tool Registry metadata;
- platform capability metadata;
- app-level contracts when separately authorized;
- permission decision;
- environment gates; and
- intent classification.

## Outputs

- candidate capabilities;
- unavailable capability explanations;
- required confirmation or approval;
- safe-use constraints;
- non-execution markers; and
- evidence of registry-backed discovery.

## Ownership

Tool Registry owns capability discovery metadata. App modules own app-specific
capabilities and business rules. Astra owns selection and coordination only.

## Failure Behavior

If no approved capability exists, Astra must explain the limitation, answer
with available knowledge, ask for clarification, or refuse.

## Security Considerations

Astra must not invent tools, infer hidden capabilities, or bypass app-owned
contracts. Pre-existing pilots do not authorize broader app integration.

## Future Implementation Notes

Capability metadata should include owner, risk level, input requirements,
side-effect class, confirmation needs, and audit expectations.

---

# Stage 7 - Planning

## Purpose

Create an explainable path for answering the user or proposing an action while
preserving ownership, permission, and safety boundaries.

## Inputs

- intent classification;
- platform context;
- user context;
- permission decision;
- capability candidates;
- refusal and clarification constraints; and
- response requirements.

## Outputs

- answer plan;
- context-use plan;
- provider-use decision;
- action proposal draft when relevant;
- clarification question when needed;
- refusal plan when required; and
- evidence requirements.

## Ownership

Astra owns planning. App services own execution details and business-rule
validity. Providers, when used, may assist with phrasing or reasoning over
approved envelopes only.

## Failure Behavior

If planning cannot satisfy permission, ownership, or evidence requirements,
Astra must ask for clarification, propose a safe next step, escalate, or
refuse.

## Security Considerations

Plans are not authority. A plan cannot commit data, authorize access, choose a
provider outside policy, or override app validation.

## Future Implementation Notes

Planning should be auditable and should label whether the response is local,
provider-assisted, proposal-only, or refusal.

---

# Stage 8 - Action Proposal

## Purpose

Describe side-effecting or high-impact actions before execution. ASTRA-002
does not authorize execution.

## Inputs

- plan;
- candidate capability;
- permission decision;
- impact classification;
- affected object summary;
- confirmation requirements; and
- rollback or compensating-action notes when applicable.

## Outputs

- user-visible action proposal;
- required confirmation;
- non-execution status;
- expected owner service;
- potential impact;
- rollback or irreversibility note; and
- audit evidence requirements.

## Ownership

Astra owns proposal construction. Tool Executor and app services own
execution, validation, business rules, and database commits.

## Failure Behavior

If the impact cannot be explained or the owning service cannot be identified,
Astra must not propose execution. It should clarify, escalate, or refuse.

## Security Considerations

No action may execute invisibly. Action proposals must not include raw secrets,
unnecessary private records, or unsupported promises.

## Future Implementation Notes

Future execution phases must add confirmation, persistent audit, rollback, and
production readiness before any side-effecting behavior is enabled.

---

# Stage 9 - Decision Evidence Assembly

## Purpose

Collect bounded pre-response proof of how Astra reached its decision outcome.

## Inputs

- request summary;
- intent evidence;
- context source metadata;
- permission decision;
- capability discovery result;
- provider-use decision;
- plan;
- proposal, refusal, or clarification result.

## Outputs

- deterministic evidence envelope where required;
- source identifiers;
- decision reason codes;
- omitted-data markers;
- provider-use marker;
- non-execution marker; and
- reviewable decision-evidence summary.

## Ownership

Astra owns bounded decision evidence. Persistent audit storage, if needed,
requires separate approved architecture and implementation.

## Failure Behavior

If adequate evidence cannot be assembled for a governed decision, Astra should
fail closed for sensitive, private, execution, or provider-dependent paths.

## Security Considerations

Evidence must not leak secrets, credentials, raw prompts, full records, SQL,
stack traces, raw tool outputs, or unrelated conversation history.

## Future Implementation Notes

Decision evidence should support replay and review for deterministic decisions
without becoming a hidden memory system. Final response or delivery metadata is
attached after response construction, not used as an input to this stage.

---

# Stage 10 - Response Construction

## Purpose

Create the final governed response for the user.

## Inputs

- answer plan;
- allowed platform context;
- allowed user context;
- provider output when explicitly approved and used;
- action proposal or refusal plan;
- clarification requirements; and
- decision-evidence summary.

## Outputs

- final answer;
- clarification question;
- refusal;
- action proposal;
- escalation message;
- visible limitations when relevant; and
- bounded final response metadata.

## Ownership

Astra owns response construction. Knowledge and app services own facts.
External providers never own final authority.

## Failure Behavior

If response construction would require unsupported facts, unauthorized data,
unapproved provider use, hidden execution, or invented capability, Astra must
ask for clarification, disclose limitation, escalate, or refuse.

## Security Considerations

The response must not reveal private data from another user, hidden policy,
secrets, internal prompts, credentials, raw records, or unauthorized tool
outputs.

## Future Implementation Notes

Responses should identify whether the answer is knowledge-only,
context-assisted, proposal-only, provider-assisted, clarification, refusal, or
escalation. Final response metadata may include response classification,
visible limitation markers, a response digest, a provider-assisted or local
marker, and a reference to the decision-evidence summary.

---

# Intelligence Decision Matrix

For every incoming request, Astra should answer these questions in order:

```text
1. Can I answer from platform knowledge alone?
2. Do I need authenticated user context?
3. Do I need app-owned information?
4. Is permission required?
5. Is execution required?
6. Can I answer locally, safely, and accurately?
7. If not, is external intelligence necessary and authorized?
8. Must I refuse?
9. Must I ask a clarification question?
10. Can I produce a final governed response?
```

## Matrix Rules

1. Platform knowledge is considered before user context.
2. User context is considered before app-owned information.
3. Permission is evaluated before capability use.
4. Execution need is identified before action proposal.
5. Local answer sufficiency is checked before external intelligence need.
6. External intelligence is considered only after local response is
   insufficient and context, permission, and purpose are understood.
7. Local response is preferred when it can satisfy the request safely and
   accurately.
8. Refusal and clarification remain valid outcomes, not failures.
9. Final governed response is produced only after context, permission,
   capability, provider, and evidence checks are resolved.

---

# External Intelligence Boundary

External intelligence is optional.

```text
User Question
        |
        v
Astra Intelligence
        |
        +----------------+
        |                |
        v                v
Local Response     External Model
        |                |
        +--------+-------+
                 v
        Governed Response
```

Astra must decide whether external intelligence is necessary before invoking
any external model. Calling an external model is a capability, not the default
execution path.

An external model may be considered only when:

- the request cannot be safely or usefully answered by deterministic local
  platform logic alone;
- the purpose is explicit;
- the model input envelope is minimized;
- the input is policy-approved;
- user text inclusion is explicitly allowed for the current purpose;
- sensitive context is excluded unless separately authorized;
- provider configuration is approved; and
- evidence records that a provider was used.

An external model must not:

- receive unrestricted backend context;
- receive raw app database records;
- receive credentials, tokens, authorization objects, or internal prompts;
- determine identity, permission, ownership, or factual truth;
- select tools outside the governed registry;
- execute actions; or
- become the default path for routine platform answers.

Potential future providers include OpenAI, Azure OpenAI, local models,
enterprise deployments, or another approved provider. Astra architecture must
remain provider-independent.

---

# ASTRA-002 Engineering Law

> Astra must decide whether external intelligence is necessary before invoking
> any external model.
>
> Calling an external model is a capability, not the default execution path.

This law inherits ASTRA-001's provider-envelope rule and applies it to the
decision pipeline.

---

# Local Response Preference

Astra should answer locally when:

- approved Knowledge context is sufficient;
- deterministic policy logic can resolve the request;
- the answer does not require provider reasoning or phrasing;
- no private context is required;
- no app-owned data is required;
- no execution is required; and
- the response can be constructed safely with bounded evidence.

Local response preference reduces provider dependency, privacy exposure,
latency, cost, and audit complexity.

---

# Refusal And Clarification Position

Refusal and clarification are first-class pipeline outcomes.

Astra asks for clarification when:

- intent is ambiguous;
- the target app, record, route, or action is unclear;
- required context is missing but could be supplied safely;
- multiple safe interpretations exist; or
- the user request could be answered after narrowing scope.

Astra refuses when:

- authorization fails;
- user isolation could be violated;
- the request requires data Astra does not own or cannot access;
- execution would bypass app services;
- provider use would violate the approved envelope;
- the requested capability is not approved; or
- the request conflicts with ASTRA-001.

---

# Future Implementation Notes

Future implementation should treat ASTRA-002 as a contract for observable
decision behavior, not as a required class layout.

Implementation tasks must separately define:

- concrete request and response models;
- intent vocabulary changes;
- policy decision schemas;
- context provider contracts;
- provider-envelope schemas;
- tool discovery metadata;
- action proposal schemas;
- evidence envelopes;
- tests for refusal, clarification, and local/provider routing; and
- disabled-by-default production gates.

No implementation is authorized by ASTRA-002.

---

# Status Boundary

```text
ASTRA-002               Completed
Parent                  ASTRA-001 Accepted
Documentation Auth      Approved
Discovery               Complete
Specification           Complete
Architecture Direction  Approved
Architecture Review     Approved
Astra Re-review         Approved
Product Owner Approval  Pending
ADR                     Ready for acceptance
Implementation          Not authorized
Production              Unchanged
```
