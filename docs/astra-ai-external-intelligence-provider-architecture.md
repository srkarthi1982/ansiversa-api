# Astra AI External Intelligence And Provider Architecture

**Status:** Proposed
**Task:** ASTRA-007
**Parent:** ASTRA-001 Vision And Core Architecture
**Parent:** ASTRA-002 Platform Intelligence Architecture
**Parent:** ASTRA-003 Conversation And Context Architecture
**Parent:** ASTRA-004 Capability Discovery And Tool Architecture
**Parent:** ASTRA-005 Execution Planning And Action Governance
**Parent:** ASTRA-006 Tool Execution Architecture
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

ASTRA-007 defines how Astra AI may use external intelligence providers without
allowing any provider to define Astra identity, reasoning authority, context
ownership, capability authority, planning authority, execution authority, or
production behavior.

ASTRA-007 answers:

- When is external intelligence necessary?
- When must Astra answer locally?
- What is an external intelligence provider?
- What is a provider capability?
- How are providers selected?
- What information may leave Ansiversa?
- How are provider input envelopes minimized?
- How are prompts governed?
- How are provider responses validated?
- How are hallucination boundaries enforced?
- How are provider failures represented?
- How are cost and token budgets governed?
- How is privacy preserved?
- How are multiple providers supported?
- How is provider evidence recorded?
- How does Astra remain provider-independent?

ASTRA-007 does not implement provider calls. It defines the constitutional
provider boundary for future authorized implementation.

---

# Parent Architecture

ASTRA-007 inherits the frozen parent architectures:

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
```

ASTRA-007 must not redefine:

- ASTRA-001 Astra identity;
- ASTRA-001 ownership and non-ownership boundaries;
- ASTRA-001 production safety rules;
- ASTRA-002 intelligence pipeline;
- ASTRA-002 local-first and external-intelligence necessity rules;
- ASTRA-002 decision evidence model;
- ASTRA-003 conversation and context ownership;
- ASTRA-003 context minimization and privacy rules;
- ASTRA-004 capability authority;
- ASTRA-004 tool ownership boundaries;
- ASTRA-005 planning authority and approval binding;
- ASTRA-006 executor and owning-service authority; or
- the fixed 100-solution-app platform boundary.

If this document conflicts with ASTRA-001 through ASTRA-006, the accepted
parent architecture wins.

---

# Scope Boundary

Allowed:

- define external intelligence and provider concepts;
- define local-first decision policy;
- define provider eligibility rules;
- define provider capability classification;
- define provider input envelope rules;
- define information minimization;
- define prompt governance;
- define provider routing policy;
- define response validation;
- define hallucination boundaries;
- define provider failure behavior;
- define cost and token governance;
- define privacy and data minimization;
- define provider evidence model;
- define multi-provider abstraction;
- define future implementation guidance;
- propose an ADR;
- update iteration planning records; and
- update the AGENTS task log.

Not allowed:

- implementation;
- runtime provider integration;
- OpenAI integration;
- Anthropic integration;
- Gemini integration;
- local model integration;
- provider SDK or dependency changes;
- prompt implementation;
- model invocation;
- APIs;
- routes;
- Tool Executor changes;
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

- External intelligence extends Astra.
- External intelligence never replaces Astra.
- Local reasoning precedes external intelligence.
- Provider selection happens only after external intelligence is necessary.
- Deterministic problems should have deterministic solutions.
- Language problems may use language models when governed necessity is proven.
- Providers do not own identity, authorization, facts, capabilities, planning,
  execution, or final authority.
- Provider inputs are minimized, purpose-bound, and policy-approved.
- Provider responses are untrusted until validated.
- Provider failures must not break local deterministic behavior.
- Cost and token use are governed architecture concerns.
- One provider must never become a constitutional dependency.

---

# Engineering Laws

## Law 1 - External Intelligence Extends Astra

External intelligence extends Astra. It never replaces Astra.

## Law 2 - Necessity Before Provider Selection

Astra must decide whether external intelligence is necessary before selecting a
provider.

## Law 3 - Local Sufficiency Wins

If Astra can answer correctly through local reasoning, governed Knowledge,
registered capabilities, approved context, or deterministic planning, it must
not call an external provider.

## Law 4 - Providers Are Not Authorities

Providers may assist with language, analysis, transformation, or generation,
but they do not own platform truth, identity, authorization, capability
existence, execution authority, or final decisions.

## Law 5 - Provider Inputs Are Governed Envelopes

External providers receive only policy-approved, minimized, purpose-bound input
envelopes. Raw internal context must not be sent by default.

---

# External Intelligence Model

External intelligence is a governed capability Astra may use when local
deterministic reasoning is insufficient for the user need.

External intelligence is appropriate for:

- natural-language summarization;
- rewriting or drafting;
- explanation;
- classification where deterministic rules are insufficient;
- semantic comparison;
- ambiguity resolution support;
- language translation;
- extraction from user-provided text when approved;
- reasoning over already-approved bounded context; and
- generating user-reviewable proposals.

External intelligence is not required for:

- opening known routes;
- finding registered apps;
- checking known platform facts;
- deterministic calculations;
- registry-backed capability discovery;
- authorization checks;
- execution planning gates;
- executor handoff;
- owner-service validation;
- simple command routing;
- fixed policy decisions; or
- production governance decisions.

External intelligence may propose. Astra governs. Owning services remain
authoritative.

---

# Provider Model

An external intelligence provider is a model or model-serving boundary that may
process a governed input envelope and return an untrusted response for Astra to
validate.

Provider examples may include:

- OpenAI;
- Anthropic Claude;
- Google Gemini;
- approved local models;
- future model providers; and
- future specialized intelligence services.

A provider record should describe:

- stable provider identifier;
- provider owner or vendor;
- model family or model class;
- supported capability classes;
- input modality support;
- output modality support;
- data retention policy reference;
- privacy policy reference;
- regional or residency constraints;
- cost and token characteristics;
- maximum input and output limits;
- reliability and health state;
- supported safety controls;
- provider failure classes;
- evidence support;
- version marker; and
- deprecation or experimental state.

Provider records are metadata for governance. They do not authorize invocation.

---

# External Intelligence Necessity Model

Astra must evaluate local sufficiency before external intelligence.

Decision sequence:

```text
User Request
        |
        v
Local Reasoning
        |
        v
Local Capability Discovery
        |
        v
Local Planning
        |
        v
Can Astra answer locally?
        |
   Yes  +----> Respond locally
        |
        No
        v
Should external intelligence be used?
        |
        v
If authorized, construct governed provider request
```

External intelligence may be necessary when:

- the user asks for language generation or transformation;
- the task requires semantic interpretation beyond deterministic rules;
- the approved local answer would be incomplete without language reasoning;
- the user requests summarization over approved bounded context;
- the user requests explanation of approved local evidence;
- ambiguity remains after local clarification options are exhausted; or
- an approved future workflow classifies the task as provider-eligible.

External intelligence is prohibited when:

- local deterministic answer is sufficient;
- required context is unauthorized;
- required data minimization cannot be achieved;
- provider policy is unavailable or disallowed;
- sensitive data would leave Ansiversa without approval;
- the request asks the provider to decide authorization, identity, capability
  existence, execution authority, or production governance;
- cost or token limits would be exceeded;
- provider output cannot be validated enough for the user-visible action; or
- parent architecture requires fail-closed behavior.

---

# Provider Capability Classification

Provider capabilities must be classified before use.

Provider capability classes:

| Class | Meaning | Governance |
|---|---|---|
| Language generation | Draft, rewrite, explain, translate, or summarize | Requires bounded input and user-reviewable output |
| Semantic analysis | Compare, cluster, classify, or infer from text | Requires validation against approved evidence |
| Extraction | Extract structured information from approved user-provided content | Requires schema and confidence boundaries |
| Planning support | Suggest options for Astra to evaluate | Cannot create execution authority |
| Multimodal interpretation | Interpret approved image, audio, or document inputs | Requires modality-specific privacy rules |
| Unsafe authority | Identity, authorization, capability existence, execution, or production decisions | Prohibited |

Unknown provider capabilities are unavailable until classified by approved
architecture.

---

# Provider Eligibility

Before provider selection, Astra determines the governed set of providers
eligible for the specific request.

Provider eligibility should evaluate:

- governance policy;
- privacy policy;
- approved provider status;
- allowed provider list;
- prohibited provider list;
- supported capability class;
- data sensitivity compatibility;
- retention and privacy compatibility;
- region or residency requirements;
- jurisdiction;
- tenant restrictions;
- cost and token budget;
- expected reliability;
- output validation needs;
- modality requirements;
- latency tolerance;
- failure behavior; and
- Product Owner or governance restrictions.

Provider eligibility is a constitutional governance decision. Provider
selection is an operational routing decision inside the eligible provider set.
If no provider is eligible, external intelligence is unavailable for the
request.

Provider eligibility must not be inferred from provider marketing claims,
provider output, prompt text, accidental ordering, or user preference alone.

---

# Provider Selection And Routing

Provider selection occurs only after:

- local sufficiency fails;
- external intelligence necessity is established;
- provider eligibility is evaluated; and
- at least one provider is eligible for the request.

Provider selection occurs only within the eligible provider set.

Routing must not be based on provider marketing claims, provider suggestions,
prompt text alone, accidental ordering, or cheapest-provider selection without
fitness checks.

When multiple providers are eligible, deterministic precedence should be based
on approved routing policy. If provider choice affects privacy, cost, quality,
or user-visible behavior in a meaningful way and no policy resolves it, Astra
must ask for clarification or fail closed.

---

# Provider Input Envelope

A provider input envelope is the only information an external provider may
receive. It is purpose-bound, minimized, and policy-approved.

An input envelope should include:

- request purpose;
- allowed task type;
- bounded user instruction;
- approved context excerpts;
- source evidence references;
- data sensitivity classification;
- excluded data classes;
- output format requirement;
- refusal and uncertainty instruction;
- token or size budget;
- retention policy marker;
- provider capability class;
- validation requirement; and
- evidence marker.

The envelope must not include by default:

- raw conversation history;
- raw internal context;
- secrets;
- tokens;
- credentials;
- private records unrelated to the task;
- full database records when summaries suffice;
- hidden policy internals not needed by the provider;
- authorization rules that the provider could reinterpret;
- execution authority;
- raw SQL;
- stack traces; or
- unrelated user data.

---

# Prompt Governance

Prompts are governed instructions inside the provider input envelope. They are
not architecture authority and must not override parent architecture.

Prompt governance should define:

- prompt purpose;
- allowed provider capability class;
- required input minimization;
- prohibited data classes;
- output format;
- refusal behavior;
- uncertainty behavior;
- citation or evidence expectations;
- no-authority reminders;
- token budget;
- version marker; and
- validation requirement.

Prompts must not:

- authorize execution;
- ask providers to determine permissions;
- ask providers to invent capabilities;
- ask providers to override Knowledge;
- ask providers to decide production governance;
- expose secrets;
- include unnecessary private data; or
- bypass local sufficiency checks.

---

# Response Validation

Provider responses are untrusted until validated by Astra or the owning
service.

## Provider Response Authority

Provider responses are advisory intelligence.

They never become authoritative platform truth until validated against Astra's
constitutional governance and authoritative owners.

Unvalidated provider output must not:

- mutate platform state;
- grant authorization;
- override ownership;
- establish factual authority over governed platform resources;
- create capabilities;
- approve execution;
- replace Knowledge;
- replace app-owned records;
- replace owner-service validation; or
- become business truth, authorization truth, record truth, workflow truth, or
  production truth.

Provider output may inform a governed Astra decision only after validation.

Validation should check:

- response shape;
- requested output format;
- whether the response stayed within task scope;
- whether claims are supported by approved evidence;
- whether unknowns are disclosed;
- whether prohibited authority claims appear;
- whether sensitive data was echoed unnecessarily;
- whether instructions conflict with parent architecture;
- whether hallucination risk is acceptable for the use case;
- whether user review is required; and
- whether the result can be used locally without execution.

Provider output may be used as:

- advisory intelligence;
- user-facing explanation;
- draft text;
- summary;
- suggestion;
- classification input;
- extraction candidate; or
- planning support evidence.

Provider output must not be used as:

- identity truth;
- authorization truth;
- capability truth;
- app data truth;
- execution result;
- production approval;
- final legal, medical, financial, or safety decision without appropriate
  product governance; or
- replacement for owning-service validation.

---

# Hallucination Boundaries

Hallucination risk is always present when using language models.

Astra must prevent hallucination from becoming platform truth by:

- preferring local authoritative sources;
- sending bounded source evidence;
- requiring uncertainty disclosure;
- validating claims against approved evidence when claims matter;
- refusing unsupported claims;
- treating generated text as draft or explanation unless validated;
- preventing providers from inventing apps, routes, capabilities, permissions,
  prices, policies, or execution outcomes; and
- keeping Knowledge, registries, app services, authorization, planners, and
  executors authoritative.

If provider output conflicts with authoritative Ansiversa sources, the
authoritative source wins.

---

# Cost And Token Governance

Cost and token use are architecture concerns because provider calls are not the
default execution path.

Cost governance should include:

- local-first decision checks;
- provider necessity evidence;
- token budget per task class;
- maximum input envelope size;
- maximum output size;
- retry limits;
- provider routing cost awareness;
- high-cost action approval requirements;
- budget exhaustion behavior;
- user-visible degradation behavior; and
- aggregate future reporting requirements.

If local answer is sufficient, provider cost is unjustified.

If token budget is insufficient for a safe answer, Astra must summarize
approved local context, ask for narrowing, degrade to a bounded local response,
or refuse rather than send excessive context.

---

# Privacy And Data Minimization

Privacy is preserved by minimizing what leaves Ansiversa.

Provider requests must be:

- purpose-bound;
- need-driven;
- smallest sufficient context;
- sensitivity-classified;
- retention-policy aware;
- user-scope aware;
- tenant-scope aware where applicable;
- stripped of secrets;
- stripped of unrelated private records; and
- auditable through bounded metadata.

Sensitive or regulated data requires explicit policy approval before provider
use. If privacy rules cannot be satisfied, external intelligence is
unavailable for that request.

---

# Provider Failure Behaviour

Provider failure is a governed outcome. It must not break Astra's local
deterministic behavior.

Failure classes:

- provider unavailable;
- provider timeout;
- provider rate limit;
- provider quota exhausted;
- provider policy rejection;
- input envelope rejected;
- output invalid;
- output unsafe;
- output unsupported by evidence;
- token budget exceeded;
- cost budget exceeded;
- provider mismatch;
- provider deprecated;
- provider retention policy incompatible; and
- unknown provider state.

Failure behavior:

- prefer local fallback when sufficient;
- disclose limitation when user-visible;
- avoid hidden provider retries that exceed budget;
- fail closed for sensitive or high-impact tasks;
- do not substitute another provider if privacy, cost, or behavior would
  materially change without approved routing;
- do not treat provider output absence as evidence; and
- record bounded failure evidence.

---

# Provider Evidence Model

Provider evidence explains why Astra used or did not use external intelligence.
It must be reviewable without leaking private data.

Evidence should include:

- local sufficiency decision;
- external intelligence necessity decision;
- provider eligibility result;
- selected provider identifier when used;
- provider capability class;
- input envelope version or digest;
- data sensitivity class;
- token budget class;
- cost budget class;
- retention policy marker;
- response validation result;
- failure category when applicable;
- fallback behavior;
- user-visible limitation when applicable; and
- final authority source.

Evidence must not include raw prompts by default, secrets, tokens, full private
records, raw provider hidden reasoning, or unrelated user data.

---

# Multi-Provider Independence

Astra must remain provider-independent.

Provider independence requires:

- provider-neutral capability classes;
- provider-neutral input envelope concepts;
- provider-neutral response validation;
- provider-neutral failure classes;
- routing policy independent of one vendor;
- no provider-specific prompt assumptions in constitutional architecture;
- no provider-owned authority;
- no provider-specific production dependency; and
- replacement or addition of providers through approved governance.

OpenAI, Claude, Gemini, local models, and future providers are possible
provider implementations. None is Astra.

---

# Security Considerations

Security rules:

- no provider-controlled identity;
- no provider-controlled authorization;
- no provider-controlled capability existence;
- no provider-controlled execution;
- no provider-controlled production approval;
- no secrets in provider envelopes;
- no raw internal context by default;
- no prompt that overrides parent architecture;
- no hidden provider call when local answer is sufficient;
- no use of provider output without validation;
- no provider call when data minimization cannot be satisfied;
- no ASTRA-007 implementation without a separate approved implementation
  phase; and
- no production behavior change from this document.

---

# Future Implementation Notes

Future implementation may define provider registries, provider routing
contracts, prompt templates, input-envelope builders, response validators,
budget controls, provider evidence storage, and provider health checks only
after separate Product Owner authorization.

Future implementation should:

- keep local sufficiency checks before provider routing;
- make external-intelligence necessity explicit;
- build provider-neutral request/response envelopes;
- minimize context before provider calls;
- enforce token and cost budgets;
- validate provider output before use;
- preserve authoritative local sources;
- support provider failure fallback;
- record bounded evidence; and
- prove providers cannot authorize execution or override ownership.

Future implementation must not use this document as authorization to add
provider SDKs, prompts, model invocation, routes, APIs, Tool Executor changes,
app integration, database access, migrations, frontend changes, tests,
deployment, generated artifacts, production configuration, or production
behavior.

---

# ADR

The proposed ADR is:

```text
docs/architecture/decisions/astra-ai-external-intelligence-provider-architecture.md
```

Decision proposed:

Adopt ASTRA-007 as the documentation-only architecture for how Astra determines
whether external intelligence is necessary, constructs governed provider input
envelopes, selects eligible providers, validates provider responses, controls
cost and privacy risk, records bounded evidence, and remains
provider-independent.

---

# Risks

| Risk | Level | Mitigation |
|---|---|---|
| Provider becomes Astra's default brain | Critical | Local sufficiency and necessity checks precede provider selection |
| Provider output becomes platform truth | Critical | Providers are not authorities and responses require validation |
| Sensitive data leaves Ansiversa unnecessarily | Critical | Input envelopes are minimized, purpose-bound, and sensitivity-classified |
| Provider choice creates vendor lock-in | High | Provider-neutral capability, envelope, validation, and failure models |
| Prompt bypasses architecture | Critical | Prompt governance cannot override parent architecture |
| Provider costs grow silently | High | Token and cost budgets are governed architecture concerns |
| Hallucination becomes action | Critical | Provider output cannot authorize capability, planning, or execution |
| Provider failure breaks local behavior | High | Local fallback and fail-closed behavior are first-class |

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
- no runtime provider integration;
- no provider dependency changes;
- no prompt implementation;
- no model invocation;
- no APIs or routes;
- no Tool Executor, app, database, migration, frontend, test, deployment,
  generated artifact, production configuration, or production behavior changes;
- AGENTS/docs-only boundary verified; and
- ASTRA-007 recorded as Proposed with Astra review and Product Owner approval
  pending.
