# Astra AI Capability Discovery And Tool Architecture

**Status:** Approved and Frozen
**Task:** ASTRA-004
**Parent:** ASTRA-001 Vision And Core Architecture
**Parent:** ASTRA-002 Platform Intelligence Architecture
**Parent:** ASTRA-003 Conversation And Context Architecture
**Created:** 2026-07-24
**Approved:** 2026-07-24
**Frozen:** 2026-07-24
**Documentation Authorization:** Approved
**Architecture Authorization:** Approved
**Architecture Direction:** Approved
**Astra Re-review:** Approved
**Product Owner Approval:** Approved
**ADR:** Accepted
**Scope:** Documentation, specification, and architecture review only
**Implementation:** Not authorized
**Production:** Unchanged

---

# Purpose

ASTRA-004 defines how Astra AI discovers, evaluates, classifies, selects, and
governs platform capabilities and tools without obtaining execution authority.

ASTRA-004 answers:

```text
What is Astra actually capable of coordinating?
```

It does not define what Astra is. That belongs to ASTRA-001. It does not
redefine how Astra reasons. That belongs to ASTRA-002. It does not redefine
conversation or context management. That belongs to ASTRA-003.

---

# Parent Architecture

ASTRA-004 inherits the frozen parent architectures:

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
```

ASTRA-004 must not redefine:

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
- ASTRA-003 context ownership and authority-resolution rules; or
- the fixed 100-solution-app platform boundary.

If this document conflicts with ASTRA-001, ASTRA-002, or ASTRA-003, the
accepted parent architecture wins.

---

# Scope Boundary

Allowed:

- define capability and tool concepts;
- define capability discovery;
- define tool registry responsibilities;
- define capability and tool classification;
- define capability ownership;
- define availability states;
- define selection rules;
- define capability evidence;
- define failure, security, and future implementation guidance;
- propose an ADR;
- update iteration planning records; and
- update the AGENTS task log.

Not allowed:

- implementation;
- runtime route changes;
- public API exposure;
- routes;
- tool execution;
- provider integration;
- prompt implementation;
- model invocation;
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

- Capability discovery precedes tool selection.
- Tool selection precedes execution planning.
- Capability existence must be verified.
- Astra never fabricates capabilities.
- Registry metadata is authoritative for capability discovery.
- Tool ownership remains with the owning service.
- Capability discovery does not authorize execution.
- Discovery is deterministic and explainable.
- Discovery remains provider-independent.
- Discovery must fail closed when capability authority cannot be established.
- Permission metadata does not equal live authorization.
- Equal candidates must resolve through governed deterministic precedence or
  clarification.

---

# Engineering Laws

## Law 1 - Capability Requires Authority

A capability is unavailable until an authoritative registry proves otherwise.

## Law 2 - Discovery Is Not Execution

Discovery never grants execution authority.

## Law 3 - Owners Define Behavior

Astra may discover capabilities, but only the owning service defines their
behavior.

## Law 4 - Selection Must Be Reviewable

Capability selection must remain deterministic, explainable, and reviewable.

---

# Capability Model

A capability is a registered platform ability that Astra may consider while
planning a governed response. A capability describes what can be coordinated,
not how execution is performed.

A capability record should describe:

- stable capability identifier;
- human-readable name;
- owning service;
- owning product or platform boundary;
- supported intents;
- supported context classes;
- read/write/side-effect classification;
- permission requirements;
- live authorization source reference;
- confirmation requirements;
- dependency requirements;
- availability state;
- deprecation state;
- experimental state;
- failure representation;
- evidence markers; and
- version or contract marker.

Capabilities are not inferred from provider output, user wording, frontend
hints, route names, app slugs, or historical conversation text. A future
implementation may use those signals only to search the authoritative registry.

---

# Tool Model

A tool is a callable interface owned by a platform service, app service, or
approved provider boundary. A tool may implement one or more capabilities, but
the capability and the tool are not the same thing.

```text
Capability
    Describes what can be coordinated.

Tool
    Provides an owned callable mechanism that may satisfy a capability.
```

Tool records should describe:

- stable tool identifier;
- owning service;
- callable contract reference;
- capability identifiers served;
- input contract reference;
- output contract reference;
- authentication and authorization requirements;
- live authorization owner reference;
- side-effect class;
- approval class;
- data-sensitivity class;
- dependency list;
- availability state;
- rollback or compensating-action marker when applicable;
- failure codes; and
- audit evidence markers.

Astra may select a tool candidate for planning. Astra does not own the tool's
business behavior, validation rules, permission checks, data access, side
effects, or final execution.

---

# Capability Discovery Pipeline

```text
Intent And Context Need
        |
        v
Capability Query Construction
        |
        v
Authoritative Registry Lookup
        |
        v
Capability Existence Verification
        |
        v
Ownership And Availability Evaluation
        |
        v
Risk And Permission Metadata Review
        |
        v
Candidate Capability Set
        |
        v
Tool Candidate Mapping
        |
        v
Selection / Clarification / Refusal / Unavailable Result
        |
        v
Capability Evidence Recorded
```

Discovery starts only after ASTRA-002 has recognized intent and ASTRA-003 has
assembled the smallest sufficient context required to determine whether a
capability is needed.

Discovery must not jump directly from user text to tool choice. The registry
must prove that the capability exists, is available, belongs to an
authoritative owner, and is suitable for the current context and permission
state.

Permission state in this pipeline has two separate meanings:

```text
Permission Metadata
    Defines what authorization a capability requires.

Live Authorization Decision
    Determines whether this user may use it now.
```

Registry metadata may declare required permissions, scopes, roles,
entitlements, confirmations, and approval classes. It never declares that the
current user is authorized. Current authorization must come from the
authoritative authorization provider or owning service and must be rechecked
again by the executor before any future action.

---

# Tool Registry Architecture

The Tool Registry is the authoritative source for discoverable capability and
tool metadata. It is a governance boundary, not an execution engine.

The registry owns:

- capability identifiers;
- capability-to-tool mappings;
- owner references;
- availability states;
- supported intent mappings;
- side-effect classifications;
- permission and approval metadata;
- dependency metadata;
- sensitivity metadata;
- deprecation and experimental markers; and
- evidence source markers.

The registry does not own:

- user identity;
- authorization truth;
- app records;
- app business rules;
- tool execution;
- provider reasoning;
- conversation state;
- Knowledge publishing; or
- production activation.

The registry may describe what permission is required. It does not own live
authorization truth for the current user, current organization, current app
record, or current request. A capability can be operationally available and
still unauthorized for the current user.

If registry metadata conflicts with an owning service's authoritative contract,
the owner contract wins and discovery must fail closed or surface the mismatch
for governance review.

---

# Capability Classification

Capabilities should be classified before any tool is selected.

| Classification | Meaning | Default handling |
|---|---|---|
| Informational | Can support response construction without side effects | May be considered after permission and context checks |
| Read capability | Reads owned information through an approved owner contract | Requires owner, scope, and permission metadata |
| Write capability | Creates, updates, deletes, sends, purchases, or commits state | Requires explicit approval metadata and later execution planning |
| Proposal capability | Produces a plan, draft, recommendation, or preview | Does not commit data |
| External-provider capability | Uses an approved provider boundary | Optional and governed by ASTRA-002 provider rules |
| Administrative capability | Affects platform administration or privileged records | Requires elevated governance and fail-closed handling |
| Experimental capability | Registered but not generally available | Must be clearly marked and blocked unless explicitly authorized |

Classification is part of discovery evidence. If a capability cannot be
classified, it is unavailable.

---

# Tool Classification

Tools should be classified by side effect, sensitivity, and approval need.

| Tool class | Side effect | Approval expectation |
|---|---|---|
| Metadata read | Reads public or registry metadata | No execution authority granted |
| User-context read | Reads minimized user context | Requires authenticated context and purpose |
| App read | Reads app-owned data through app service contracts | Requires owner permission and app contract |
| Draft/proposal | Produces a non-committed artifact | Requires evidence that no state is committed |
| Write/action | Mutates state or performs an external action | Requires later ASTRA-005 execution planning and confirmation |
| External provider | Sends approved input envelope to a provider | Requires provider necessity and policy approval |
| Admin | Affects privileged platform data | Requires explicit administrative authorization |

Tool classification must be conservative. Unknown side effects are treated as
write/action risk until the owning service proves otherwise.

---

# Capability Ownership

Every capability and tool must have exactly one authoritative owner.

Examples:

| Capability area | Authoritative owner |
|---|---|
| Platform app catalog discovery | Knowledge Registry |
| User identity summary | Authentication or user-context provider |
| User permission state | Authorization provider or app service |
| App record summary | Owning app service |
| App record mutation | Owning app service |
| Public SEO artifact lookup | AI SEO or Knowledge publisher |
| External model invocation | Astra provider policy boundary |
| Tool metadata | Tool Registry |

Astra coordinates capability discovery. It never becomes the owner of app
behavior, permissions, records, external provider behavior, or execution.

---

# Capability Availability States

Capability discovery must represent availability explicitly. Availability
describes whether a capability is generally discoverable and operational. It
does not mean the current user is authorized to use it.

| State | Meaning | Required behavior |
|---|---|---|
| Available | Registry and owner metadata confirm the capability is generally discoverable and operational | May become a candidate, subject to live authorization |
| Unavailable | Capability is absent, disabled, unsupported, or blocked | Must not be selected |
| Authorization required | Capability is operationally available but live user authorization is missing, denied, or unknown | Ask, refuse, or route through authoritative authorization evaluation |
| Needs clarification | Capability choice depends on missing user intent or scope | Ask a clarification question |
| Deprecated | Capability exists but should not be selected for new planning | Use replacement if authoritative metadata provides one |
| Experimental | Capability exists but requires explicit authorization | Block unless authorized |
| Owner mismatch | Registry and owner contract disagree | Fail closed and record evidence |
| Dependency unavailable | A required capability, provider, or owner contract is unavailable | Fail closed or propose a lower-risk alternative |

Unavailable capabilities should be represented honestly. Astra may explain that
the capability is not available, but it must not imply hidden support.

Operational availability and user authorization must remain separate:

```text
Operationally available
        |
        v
Live authorization required
        |
        v
Authorized / unauthorized / unknown for this user
```

---

# Capability Selection Rules

Capability selection is the governed process of choosing a candidate capability
or declining to choose one.

Selection rules:

1. Use the recognized intent from ASTRA-002.
2. Use only context allowed by ASTRA-003.
3. Query only authoritative registry metadata.
4. Verify capability existence before considering tools.
5. Verify owner, availability, side-effect, permission metadata, dependency
   metadata, and live authorization source separately.
6. Prefer the smallest sufficient capability.
7. Prefer read-only or proposal capabilities before write/action capabilities
   when they satisfy the request.
8. Treat unknown side effects, owners, or permissions as blockers.
9. Select no capability when the request can be answered without one.
10. Record evidence for selected, rejected, unavailable, and ambiguous
    capabilities.

Tool selection may identify a candidate tool for a future plan. It does not
authorize execution. Execution planning belongs to ASTRA-005 and remains
separate.

When multiple candidates remain equally suitable, Astra must use explicit
registry-governed precedence.

Precedence may include:

1. exact intent match;
2. lower side-effect class;
3. narrower context requirement;
4. fewer dependencies;
5. stable approved priority; and
6. stable capability or tool identifier as the final tie-breaker.

Registry priority must be governed metadata. It must not be caller-controlled,
provider-generated, inferred from database ordering, inferred from registry
iteration order, or inferred from historical conversation order.

If no approved precedence resolves the choice and the difference is
user-significant, Astra must ask for clarification or return an
ambiguous-capability result rather than choose arbitrarily.

---

# Capability Evidence Model

Capability evidence should be bounded, deterministic, and reviewable.

Evidence may include:

- request intent reference;
- context-source references used for discovery;
- registry source marker;
- capability identifier;
- tool identifier when selected;
- owner identifier;
- availability state;
- side-effect class;
- permission metadata markers;
- live authorization source and decision markers;
- approval markers;
- dependency markers;
- precedence and tie-break markers;
- rejection reason codes;
- clarification reason codes;
- unavailable capability reason codes; and
- timestamp or version marker when required by the registry.

Evidence must not include raw secrets, raw app records, unrestricted prompts,
provider transcripts, database queries, credentials, or unnecessary user data.

---

# Failure Behaviour

Discovery fails closed when:

- the registry is unavailable;
- capability metadata is missing;
- ownership cannot be established;
- side-effect class is unknown;
- permission requirements are unknown;
- live authorization source is unknown when user-specific authorization is
  required;
- dependencies are unavailable;
- the capability is deprecated without an approved replacement;
- an experimental capability lacks explicit authorization;
- the owner contract contradicts registry metadata; or
- the request requires execution that has not been authorized.

Valid outcomes include:

- answer without capability use;
- ask for clarification;
- explain capability unavailability;
- propose a non-executing alternative;
- refuse unsafe or unauthorized assistance; or
- escalate to governance review.

---

# Security Considerations

- User text is not evidence that a capability exists.
- Provider output is not evidence that a capability exists.
- Frontend hints are not authority for capability existence or permission.
- Registry metadata must be treated as authoritative only within its governed
  scope.
- Registry permission metadata must not be treated as live authorization for
  the current user.
- App services remain authoritative for app behavior and app data.
- Authorization providers and owning services remain authoritative for live
  authorization decisions.
- Unknown write risk must be handled as write risk.
- Discovery must not leak private context into evidence.
- Discovery must not expose unavailable internal tools as promised features.
- Capability metadata must not allow caller-controlled owner, permission, or
  side-effect claims.
- Discovery must preserve the ASTRA-002 local-response-before-external-model
  rule.

---

# Future Implementation Notes

Future implementation should:

- use stable capability and tool identifiers;
- keep registry lookups deterministic;
- keep registry precedence explicit and stable;
- test negative cases for fabricated, deprecated, experimental, and ownerless
  capabilities;
- test equal-candidate tie resolution and ambiguous-capability outcomes;
- test that registry permission requirements never become live authorization;
- test that a future executor rechecks authorization before action;
- test that discovery never invokes tools;
- test that write/action tools cannot be selected as execution without
  separate execution planning;
- test provider-independent discovery;
- expose bounded evidence for review;
- avoid storing raw user text or private records in discovery evidence;
- preserve app-owned service contracts; and
- keep ASTRA-004 isolated until a later implementation phase is authorized.

---

# ADR

The accepted ADR for ASTRA-004 is:

```text
docs/architecture/decisions/astra-ai-capability-tool-architecture.md
```

The ADR is accepted. ASTRA-004 is Frozen as the capability discovery and tool
architecture foundation for Astra AI.

---

# Risks

| Risk | Level | Mitigation |
|---|---|---|
| Astra fabricates capabilities from user wording | Critical | Capability is unavailable until registry authority proves otherwise |
| Discovery is mistaken for execution authority | Critical | Discovery never grants execution authority |
| Tool behavior is redefined centrally | Critical | Owning service defines behavior and contracts |
| Unknown side effects are treated as safe | Critical | Unknown side effects are handled as write/action risk |
| Deprecated or experimental tools are selected silently | High | Availability states must be explicit and enforced |
| Provider output invents tool options | High | Discovery remains registry-backed and provider-independent |
| Permission metadata is confused with live authorization | Critical | Registry declares requirements only; authorization providers or owning services decide whether this user may use the capability now |
| Permission metadata is absent or stale | High | Unknown permission requirements fail closed |
| Equal capability candidates are selected arbitrarily | High | Registry-governed precedence and stable identifiers resolve ties, otherwise Astra asks for clarification |
| Capability evidence leaks private context | High | Evidence uses bounded metadata and omission markers |
| Capability dependencies are ignored | Medium | Dependency metadata is required before selection |

---

# Validation Strategy

ASTRA-004 validation is documentation-only.

Required evidence:

- ASTRA-004 inherits ASTRA-001, ASTRA-002, and ASTRA-003 explicitly;
- required sections are present;
- capability and tool concepts are separated;
- Tool Registry authority is defined;
- capability discovery precedes tool selection;
- tool selection precedes execution planning;
- capability existence must be verified;
- fabricated capabilities are prohibited;
- capability ownership and availability states are documented;
- permission metadata is separated from live authorization;
- read/write/side-effect classifications are documented;
- deterministic candidate precedence and ambiguity handling are documented;
- approval and dependency metadata are represented;
- capability evidence is bounded and reviewable;
- failure behavior is fail-closed;
- future implementation remains unauthorized; and
- no non-documentation files are modified.

Validation commands:

```bash
git diff --check
git diff --name-only
test "$(git diff --name-only | grep -Ev '^(AGENTS.md|docs/)' | wc -l)" = "0"
```

No tests, compile checks, migrations, OpenAPI generation, frontend builds, or
runtime verification are required because ASTRA-004 is documentation-only.

---

# Status Boundary

```text
ASTRA-004               Approved
Parent                  ASTRA-001 Accepted
Parent                  ASTRA-002 Accepted
Parent                  ASTRA-003 Accepted
Documentation Auth      Approved
Architecture Auth       Approved
Discovery               Complete
Specification           Complete
Architecture Direction  Approved
Astra Re-review         Approved
Product Owner Approval  Approved
ADR                     Accepted
ASTRA-004 Freeze        Approved
Implementation          Not authorized
Production              Unchanged
ASTRA-005               Documentation only next; requires separate authorization
```
