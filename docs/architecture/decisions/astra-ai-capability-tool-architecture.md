# Architecture Decision: Astra AI Capability Discovery And Tool Architecture

**Status:** Proposed
**Created:** 2026-07-24
**Task:** ASTRA-004
**Parent:** ASTRA-001 Vision And Core Architecture
**Parent:** ASTRA-002 Platform Intelligence Architecture
**Parent:** ASTRA-003 Conversation And Context Architecture
**Decision Owner:** Karthikeyan Ramalingam
**Documentation Authorization:** Approved
**Architecture Authorization:** Approved
**Architecture Direction:** Approved
**Architecture Review:** Minor revisions applied; pending Astra re-review
**Product Owner Approval:** Pending
**Implementation:** Not authorized
**Production:** Unchanged

---

# Decision

Should Ansiversa define a governed capability discovery and tool architecture
for Astra AI before implementing capability lookup, tool selection, execution
planning, provider-backed tool suggestions, or app-service coordination?

Recommendation:

Adopt ASTRA-004 as the documentation-only architecture for how Astra AI
discovers registered capabilities, distinguishes capabilities from tools,
evaluates ownership and risk metadata, selects or rejects tool candidates,
prevents capability fabrication, records discovery evidence, and preserves the
separation between discovery and execution authority. The architecture also
separates registry permission metadata from live user authorization and
requires deterministic precedence or clarification when multiple candidates are
equally suitable.

Canonical proposed specification:

```text
docs/astra-ai-capability-tool-architecture.md
```

---

# Parent Architecture

ASTRA-004 inherits ASTRA-001, ASTRA-002, and ASTRA-003. It does not redefine
Astra identity, ownership, execution authority, provider philosophy,
production safety, the intelligence pipeline, the decision matrix, the
conversation/context model, context authority resolution, or the fixed
100-solution-app platform boundary.

---

# Options Considered

## Option 1 - Infer Capabilities From User Requests

Recommendation: Reject.

User wording is untrusted input and cannot prove that a capability exists. This
would allow fabricated tools, unsafe promises, and provider-influenced
capability claims.

## Option 2 - Let External Models Decide Available Tools

Recommendation: Reject.

External models are optional capabilities under ASTRA-002. They cannot become
the authority for what Ansiversa can do, what tools exist, or which services
own execution.

## Option 3 - Let Each App Define Discovery Independently

Recommendation: Reject.

App services own behavior and data, but Astra needs one governed discovery
model to prevent cross-app drift, capability fabrication, and inconsistent
side-effect classification.

## Option 4 - Registry-Governed Discovery

Recommendation: Accept if approved.

This creates a shared architecture where capabilities are unavailable until an
authoritative registry proves otherwise, tool owners remain authoritative,
discovery stays deterministic and provider-independent, and execution planning
remains separate.

---

# Proposed Engineering Laws

## Law 1

> A capability is unavailable until an authoritative registry proves otherwise.

## Law 2

> Discovery never grants execution authority.

## Law 3

> Astra may discover capabilities, but only the owning service defines their
> behavior.

## Law 4

> Capability selection must remain deterministic, explainable, and reviewable.

---

# Consequences If Accepted

- Capabilities and tools become separate architectural concepts.
- Capability discovery is registry-backed instead of inferred.
- User text, provider output, and frontend hints cannot fabricate capabilities.
- Capability ownership remains explicit.
- Tool behavior remains owned by the owning service.
- Availability, deprecation, experimental state, side effects, permissions,
  approvals, and dependencies become discovery metadata.
- Registry permission requirements remain separate from live authorization
  decisions.
- Read/proposal capabilities are distinguishable from write/action
  capabilities.
- Tool selection remains separate from execution planning.
- Equal candidates are resolved through governed precedence or clarification.
- Discovery evidence is bounded and reviewable.
- Implementation remains separately unauthorized.
- Production remains unchanged.

---

# Acceptance Checklist

- [ ] Astra architecture review completed.
- [ ] Product Owner approval recorded.
- [ ] ADR accepted.
- [ ] ASTRA-004 frozen.
- [ ] Future implementation phase separately scoped.

---

# Current Status

```text
ADR                     Proposed
ASTRA-004               Proposed
Parent                  ASTRA-001 Accepted
Parent                  ASTRA-002 Accepted
Parent                  ASTRA-003 Accepted
Documentation Auth      Approved
Architecture Auth       Approved
Architecture Direction  Approved
Architecture Review     Minor revisions applied; pending Astra re-review
Product Owner Approval  Pending
Implementation          Not authorized
Production              Unchanged
```
