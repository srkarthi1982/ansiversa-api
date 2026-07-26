# Astra AI Memory Architecture

**Status:** Proposed
**Task:** ASTRA-008
**Parent:** ASTRA-001 Vision And Core Architecture
**Parent:** ASTRA-002 Platform Intelligence Architecture
**Parent:** ASTRA-003 Conversation And Context Architecture
**Parent:** ASTRA-004 Capability Discovery And Tool Architecture
**Parent:** ASTRA-005 Execution Planning And Action Governance
**Parent:** ASTRA-006 Tool Execution Architecture
**Parent:** ASTRA-007 External Intelligence And Provider Architecture
**Created:** 2026-07-26
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

ASTRA-008 defines what Astra may remember, what it must forget, how memory is
classified, owned, retrieved, retained, deleted, exported, audited, and
prevented from becoming an unauthorized cross-app datastore.

ASTRA-008 answers:

- What is Astra allowed to remember?
- What must Astra forget?
- What is conversation memory?
- What is working memory?
- What is long-term user memory?
- What is a user preference?
- What remains app-owned data rather than Astra memory?
- How is memory retrieved?
- How is memory used without bypassing authorization?
- How are privacy, retention, deletion, and export governed?
- How is memory evidence recorded?
- How does memory interact with external providers?
- How does Astra avoid becoming a hidden data warehouse?

ASTRA-008 does not implement memory storage, retrieval, persistence, APIs,
routes, prompts, provider calls, database tables, migrations, frontend changes,
or production behavior.

---

# Parent Architecture

ASTRA-008 inherits the frozen parent architectures:

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
        |
        v
ASTRA-007
External Intelligence And Provider Architecture
        |
        v
ASTRA-008
Memory Architecture
```

ASTRA-008 must not redefine:

- ASTRA-001 Astra identity;
- ASTRA-001 ownership and non-ownership boundaries;
- ASTRA-001 production safety rules;
- ASTRA-002 intelligence pipeline;
- ASTRA-002 local-first reasoning and decision evidence model;
- ASTRA-003 conversation and context ownership;
- ASTRA-003 context minimization, isolation, and privacy rules;
- ASTRA-004 capability and tool ownership;
- ASTRA-005 planning authority and approval binding;
- ASTRA-006 executor and owning-service authority;
- ASTRA-007 provider necessity, provider input, and provider authority rules;
  or
- the fixed 100-solution-app platform boundary.

If this document conflicts with ASTRA-001 through ASTRA-007, the accepted
parent architecture wins.

---

# Scope Boundary

Allowed:

- define memory concepts;
- define memory classification;
- define memory ownership;
- define memory eligibility rules;
- define memory writing governance;
- define memory retrieval governance;
- define memory use in the intelligence pipeline;
- define preference memory boundaries;
- define app-data boundary rules;
- define forgetting, deletion, export, and retention governance;
- define memory audit evidence;
- define memory privacy and security boundaries;
- define provider interaction boundaries;
- define future implementation guidance;
- propose an ADR;
- update iteration planning records; and
- update the AGENTS task log.

Not allowed:

- implementation;
- runtime memory;
- memory storage;
- memory retrieval code;
- vector database integration;
- embeddings;
- provider SDK or dependency changes;
- prompt implementation;
- model invocation;
- APIs;
- routes;
- Tool Executor changes;
- app integration;
- app database access;
- database changes;
- migrations;
- frontend changes;
- tests;
- generated artifacts;
- deployment changes; or
- production behavior changes.

---

# Engineering Principles

- Memory must be explicit, governed, and purpose-bound.
- Memory must never become a hidden authorization source.
- Memory must never replace app-owned records.
- Memory retrieval must be need-driven and minimized.
- Conversation state is not automatically long-term memory.
- User preferences are memory only when approved and revocable.
- Forgetting is a constitutional capability, not cleanup.
- Memory must be exportable, deletable, and auditable before production use.
- External providers do not own memory.
- Memory must not create App #101, duplicate app databases, or centralize
  mini-app data.

---

# Engineering Laws

## Law 1 - Memory Requires Permission And Purpose

Astra may remember only approved memory classes for an explicit purpose.

## Law 2 - Forgetting Is Mandatory

Astra must forget memory that is expired, revoked, deleted, superseded, or no
longer authorized.

## Law 3 - App Data Remains App-Owned

Astra memory must not copy, replace, summarize into permanence, or become the
authority for app-owned records.

## Law 4 - Retrieval Is Need-Driven

Astra may retrieve memory only when the current request needs that memory and
the user, purpose, scope, and authorization permit it.

## Law 5 - Memory Is Not Authority

Memory may inform personalization and continuity, but it cannot determine
identity, authorization, capability existence, execution authority, app facts,
or production truth.

---

# Memory Model

Memory is governed retained information that may influence future Astra
reasoning after the original conversation turn or workflow moment has passed.

Memory is separate from:

- transient conversation state;
- current request context;
- governed Knowledge;
- app-owned records;
- authorization state;
- tool results;
- execution evidence;
- provider responses; and
- audit logs.

Memory may support:

- user continuity;
- user preferences;
- repeated clarification avoidance;
- personalization of tone and workflow defaults;
- safe reminders about user-stated non-sensitive preferences;
- consented long-term context; and
- explainable adaptation in future ASTRA-009 learning architecture.

Memory must not support:

- hidden profiling;
- cross-user inference;
- unauthorized cross-app aggregation;
- shadow copies of app databases;
- bypassing app services;
- permission decisions;
- execution approval;
- provider prompt expansion without policy approval;
- permanent retention of raw conversations by default; or
- production governance decisions.

---

# Memory Classification

Memory classes:

| Class | Meaning | Default |
|---|---|---|
| Conversation state | Temporary state needed for an active conversation | Transient |
| Working memory | Short-lived task state needed to complete the current workflow | Transient |
| Preference memory | User-approved preferences that personalize future interaction | Optional |
| Long-term user memory | User-approved durable information for future continuity | Restricted |
| Governance memory | Approved metadata about consent, retention, deletion, export, and policy state | Required before memory use |
| App-owned data | Records owned by mini apps or parent services | Not Astra memory |
| Knowledge | Governed platform/public truth | Not memory |
| Audit evidence | Bounded evidence about Astra decisions | Not personalization memory |
| Provider output | Advisory external intelligence | Not memory unless separately validated and approved |

Unknown memory classes are prohibited until classified by approved
architecture.

---

# Conversation State And Working Memory

Conversation state supports the active user interaction. It may include:

- current user request;
- active clarification questions;
- selected route or workflow context;
- current plan draft;
- pending approval state;
- current tool or provider evidence references; and
- transient response-planning state.

Working memory supports a bounded task. It may include:

- in-progress form intent;
- temporary comparison criteria;
- current draft options;
- short-lived workflow choices;
- pending execution-plan references; and
- active task constraints.

Conversation state and working memory:

- are transient by default;
- expire when the conversation, session, or task scope ends;
- must not silently become long-term memory;
- must not be used across unrelated conversations without approval; and
- must be excluded from provider envelopes unless ASTRA-007 input-envelope
  rules permit the minimized content.

---

# Long-Term Memory And Preferences

Long-term memory is durable memory retained beyond the active conversation or
task. It requires explicit approved memory class, purpose, retention rule, and
user control before implementation.

Preference memory may include:

- preferred language;
- preferred tone or level of detail;
- preferred workflow defaults;
- accessibility preferences;
- recurring non-sensitive formatting preferences; and
- explicit user instructions that are safe, revocable, and allowed by policy.

Long-term memory must not include by default:

- raw conversation history;
- secrets;
- credentials;
- tokens;
- sensitive personal data;
- app record bodies;
- private documents;
- health, financial, legal, or safety-sensitive details;
- inferred attributes;
- cross-app behavioral profiles;
- provider hidden reasoning;
- raw prompts;
- SQL;
- stack traces; or
- data the user did not approve for retention.

Sensitive long-term memory requires explicit policy approval, user controls,
retention limits, deletion/export behavior, and audit evidence before
production use.

---

# App-Owned Data Boundary

Applications own app records. Astra memory does not own app facts.

Astra must not store:

- copies of mini-app records as memory;
- summaries of app records that become alternate record truth;
- app-derived user profiles unless separately approved;
- app database snapshots;
- cross-app rollups that bypass app services;
- owner IDs or internal record IDs unless required as bounded evidence; or
- stale app facts that could conflict with the owning service.

When Astra needs app information, it must use approved app capabilities,
context providers, or owning-service APIs according to ASTRA-003, ASTRA-004,
ASTRA-005, and ASTRA-006. Memory may store a reference or bounded evidence only
when approved and safe, but the owning service remains authoritative.

---

# Memory Eligibility

Before writing memory, Astra must determine whether memory is eligible.

Eligibility should evaluate:

- memory class;
- user consent or Product Owner-approved policy;
- purpose;
- data sensitivity;
- source authority;
- owner scope;
- tenant scope where applicable;
- retention window;
- deletion and export support;
- audit requirement;
- provider exposure restriction;
- app-data boundary;
- conflict with existing memory;
- risk of becoming authorization or record truth; and
- user-visible control requirements.

If eligibility cannot be established, Astra must not write memory.

---

# Memory Writing Governance

Memory writing is a governed action. Future implementation must define whether
a memory write is automatic, proposed, user-confirmed, or prohibited.

Memory writes should record:

- memory class;
- purpose;
- source;
- owner scope;
- retention rule;
- sensitivity class;
- consent or policy basis;
- deletion/export eligibility;
- provider exposure restriction;
- validation status;
- created time;
- expiry time when applicable; and
- bounded evidence reference.

Memory writes must not:

- happen silently for restricted classes;
- persist raw conversation by default;
- store app-owned record truth;
- create or modify app data;
- store provider output as truth without validation;
- bypass user controls;
- bypass retention policy; or
- become execution, authorization, or production evidence.

---

# Memory Retrieval Governance

Memory retrieval must be need-driven, minimized, and purpose-bound.

Retrieval should evaluate:

- current user identity from backend auth;
- current request purpose;
- memory class;
- owner scope;
- consent and retention status;
- freshness;
- sensitivity;
- conflict state;
- provider exposure restrictions;
- relevance;
- smallest sufficient memory set; and
- whether clarification is safer than retrieval.

Retrieved memory may inform:

- personalization;
- continuity;
- clarification reduction;
- response style;
- safe default selection; and
- user-reviewable suggestions.

Retrieved memory must not determine:

- identity;
- authorization;
- app record truth;
- capability existence;
- execution approval;
- provider eligibility;
- production governance; or
- final high-impact decisions.

---

# Forgetting, Deletion, Export, And Retention

Forgetting is mandatory governance.

Memory must be forgotten when:

- the user revokes it;
- the user deletes it;
- the retention period expires;
- the memory is superseded;
- the memory is invalidated by authoritative source conflict;
- the memory class is no longer authorized;
- the account, tenant, or policy state requires removal; or
- Product Owner-approved governance requires removal.

Deletion must remove memory from active retrieval. Export must expose approved
user-visible memory in an understandable form. Retention must be defined before
production memory is enabled.

Audit evidence may retain bounded deletion metadata only when approved by
governance and must not preserve deleted memory content as a workaround.

---

# Memory Conflict And Freshness

Memory may become stale, contradicted, or ambiguous.

Conflict handling:

- authoritative app or platform source wins over memory;
- stale memory must be ignored, refreshed, clarified, or deleted;
- contradictory memory must not be merged into manufactured consensus;
- user clarification is required when conflict affects a user-visible outcome;
- sensitive conflict must fail closed; and
- memory freshness must be visible in evidence where relevant.

Memory cannot override Knowledge, app services, authorization providers,
capability registries, execution results, or Product Owner governance.

---

# Provider Interaction Boundary

External providers do not own memory.

Memory may be included in a provider input envelope only when:

- local sufficiency fails under ASTRA-007;
- external intelligence is necessary;
- the memory class permits provider exposure;
- the memory is minimized and purpose-bound;
- sensitivity and retention policies permit exposure;
- user or governance approval exists where required; and
- the provider response can be validated before use.

Provider output must not become memory by default. Provider output may become a
memory candidate only after validation, eligibility review, user control
requirements, retention rules, and audit evidence are satisfied.

---

# Memory Evidence Model

Memory evidence explains why memory was written, retrieved, ignored, deleted,
or exported. It must be reviewable without leaking private data.

Evidence should include:

- memory decision type;
- memory class;
- purpose;
- owner scope;
- consent or policy basis;
- sensitivity class;
- retention marker;
- deletion/export status;
- retrieval reason;
- conflict or freshness status;
- provider exposure marker;
- validation result;
- final authority source; and
- failure category when applicable.

Evidence must not include raw memory content by default, secrets, tokens, full
private records, raw prompts, provider hidden reasoning, SQL, stack traces, or
unrelated user data.

---

# Privacy And Security

Memory privacy and security rules:

- no memory without approved purpose;
- no hidden long-term retention;
- no cross-user memory access;
- no app-data centralization;
- no secrets in memory;
- no raw conversation persistence by default;
- no sensitive memory without explicit approval and controls;
- no provider exposure without ASTRA-007 envelope governance;
- no memory used as authorization or execution authority;
- no implementation before deletion/export/retention governance is approved;
  and
- no production behavior change from this document.

---

# Future Implementation Notes

Future implementation may define memory schemas, storage, retrieval,
classification, consent controls, deletion/export tools, retention jobs,
conflict handling, memory evidence, and UI controls only after separate
Product Owner authorization.

Future implementation should:

- keep memory disabled until readiness gates are satisfied;
- classify memory before storage;
- make memory write decisions explicit;
- minimize retrieval;
- preserve app ownership;
- support deletion, export, and retention;
- record bounded evidence;
- prevent provider-owned memory;
- prevent memory from authorizing execution; and
- prove cross-user isolation.

Future implementation must not use this document as authorization to add
runtime memory, vector databases, embeddings, provider SDKs, prompts, model
invocation, routes, APIs, Tool Executor changes, app integration, database
access, migrations, frontend changes, tests, deployment, generated artifacts,
production configuration, or production behavior.

---

# ADR

The proposed ADR is:

```text
docs/architecture/decisions/astra-ai-memory-architecture.md
```

Decision proposed:

Adopt ASTRA-008 as the documentation-only architecture for what Astra may
remember, what it must forget, and how memory is classified, owned, retrieved,
retained, deleted, exported, audited, and prevented from becoming an
unauthorized cross-app datastore.

---

# Risks

| Risk | Level | Mitigation |
|---|---|---|
| Memory becomes silent surveillance | Critical | Memory requires approved class, purpose, retention, and user controls |
| Memory becomes an unauthorized app-data store | Critical | App records remain app-owned and are not copied into Astra memory |
| Memory bypasses authorization | Critical | Memory is not identity, authorization, capability, execution, or app truth |
| User cannot forget retained data | Critical | Forgetting, deletion, export, and retention are mandatory governance |
| Provider output becomes memory truth | Critical | Provider output is not memory unless validated and memory-eligible |
| Stale memory overrides current facts | High | Authoritative sources win; stale or conflicting memory is ignored, clarified, or deleted |
| Retrieval over-collects private context | High | Retrieval is need-driven, minimized, and purpose-bound |
| Cross-user leakage | Critical | Owner scope and backend identity govern every memory decision |

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
- no runtime memory;
- no vector database or embeddings;
- no provider dependency changes;
- no prompt implementation;
- no model invocation;
- no APIs or routes;
- no Tool Executor, app, database, migration, frontend, test, deployment,
  generated artifact, production configuration, or production behavior changes;
- AGENTS/docs-only boundary verified; and
- ASTRA-008 recorded as Proposed with Astra review and Product Owner approval
  pending.
