# Architecture Decision: Astra AI External Intelligence And Provider Architecture

**Status:** Accepted
**Created:** 2026-07-25
**Accepted:** 2026-07-26
**Frozen:** 2026-07-26
**Task:** ASTRA-007
**Parent:** ASTRA-001 Vision And Core Architecture
**Parent:** ASTRA-002 Platform Intelligence Architecture
**Parent:** ASTRA-003 Conversation And Context Architecture
**Parent:** ASTRA-004 Capability Discovery And Tool Architecture
**Parent:** ASTRA-005 Execution Planning And Action Governance
**Parent:** ASTRA-006 Tool Execution Architecture
**Decision Owner:** Karthikeyan Ramalingam
**Documentation Authorization:** Approved
**Architecture Authorization:** Approved
**Architecture Direction:** Approved
**Astra Re-review:** Approved
**Product Owner Approval:** Approved
**Implementation:** Not authorized
**Production:** Unchanged

---

# Decision

Should Ansiversa define a governed External Intelligence and Provider
Architecture for Astra AI before implementing OpenAI calls, prompt templates,
provider routing, model invocation, provider SDKs, local model integration, or
production AI behavior?

Decision:

Adopt ASTRA-007 as the documentation-only architecture for how Astra
determines whether external intelligence is necessary, constructs governed
provider input envelopes, selects eligible providers, validates provider
responses, controls cost and privacy risk, records bounded evidence, and
remains provider-independent. The revised proposal separates provider
eligibility from provider selection and classifies provider output as advisory
intelligence until validated by Astra and authoritative owners.

Canonical accepted specification:

```text
docs/astra-ai-external-intelligence-provider-architecture.md
```

---

# Parent Architecture

ASTRA-007 inherits ASTRA-001 through ASTRA-006. It does not redefine Astra
identity, local-first reasoning, conversation/context ownership, capability
authority, planning authority, execution governance, owning-service authority,
or the fixed 100-solution-app platform boundary.

---

# Options Considered

## Option 1 - Provider-First Intelligence

Recommendation: Reject.

Sending user requests to a model by default would make the provider the
practical first reasoning layer and would weaken the frozen Astra constitution.

## Option 2 - OpenAI-Specific Architecture

Recommendation: Reject.

OpenAI may become an approved provider, but one provider must not become a
constitutional dependency.

## Option 3 - Local-First Provider-Governed Architecture

Recommendation: Accept.

This keeps Astra self-defined, requires local sufficiency checks before
provider selection, treats external intelligence as a governed capability,
minimizes provider inputs, validates provider output, controls cost and privacy
risk, and preserves provider independence.

---

# Accepted Engineering Laws

## Law 1

> External intelligence extends Astra. It never replaces Astra.

## Law 2

> Astra must decide whether external intelligence is necessary before selecting
> a provider.

## Law 3

> If Astra can answer correctly through local reasoning, governed Knowledge,
> registered capabilities, approved context, or deterministic planning, it must
> not call an external provider.

## Law 4

> Providers may assist with language, analysis, transformation, or generation,
> but they do not own platform truth, identity, authorization, capability
> existence, execution authority, or final decisions.

## Law 5

> External providers receive only policy-approved, minimized, purpose-bound
> input envelopes. Raw internal context must not be sent by default.

---

# Consequences

- External intelligence becomes a governed capability, not the default path.
- Provider eligibility is evaluated before provider selection.
- Provider selection occurs only after external-intelligence necessity is
  established.
- Provider selection occurs only within the eligible provider set.
- Local sufficiency prevents unnecessary provider calls.
- Provider input envelopes are minimized and policy-approved.
- Prompt governance is defined without implementing prompts.
- Provider responses are untrusted until validated.
- Provider output remains advisory intelligence until validated against Astra's
  constitutional governance and authoritative owners.
- Hallucination boundaries are explicit.
- Cost and token governance become architecture requirements.
- Privacy and data minimization govern all provider requests.
- Multiple providers can be supported without making one provider
  constitutional.
- Implementation remains separately unauthorized.
- Production remains unchanged.

---

# Acceptance Checklist

- [x] Astra architecture review completed.
- [x] Product Owner approval recorded.
- [x] ADR accepted.
- [x] ASTRA-007 frozen.
- [x] Future implementation phase separately scoped.
- [x] Astra architecture direction approved with targeted documentation
  refinements recorded.
- [x] Provider eligibility and provider selection refinement applied.
- [x] Provider response authority refinement applied.
- [x] Astra re-review approved.

---

# Current Status

```text
ADR                     Accepted
ASTRA-007               Approved and Frozen
Parent                  ASTRA-001 Accepted
Parent                  ASTRA-002 Accepted
Parent                  ASTRA-003 Accepted
Parent                  ASTRA-004 Accepted
Parent                  ASTRA-005 Accepted
Parent                  ASTRA-006 Accepted
Documentation Auth      Approved
Architecture Auth       Approved
Architecture Direction  Approved
Discovery               Complete
Specification           Complete
Architecture Review     Approved
Astra Re-review         Approved
Product Owner Approval  Approved
Implementation          Not authorized
Production              Unchanged
ASTRA-008               Documentation only next; requires separate authorization
```
