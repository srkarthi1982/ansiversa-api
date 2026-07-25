# ASTRA-007 - External Intelligence And Provider Architecture

**Status:** Proposed
**Created:** 2026-07-25
**Owner:** Karthikeyan Ramalingam
**Parent:** ASTRA-001 Vision And Core Architecture
**Parent:** ASTRA-002 Platform Intelligence Architecture
**Parent:** ASTRA-003 Conversation And Context Architecture
**Parent:** ASTRA-004 Capability Discovery And Tool Architecture
**Parent:** ASTRA-005 Execution Planning And Action Governance
**Parent:** ASTRA-006 Tool Execution Architecture
**Authorization:** Approved for documentation and architecture only
**Architecture Review:** Pending Astra Review
**Product Owner Approval:** Pending
**ADR:** Proposed
**Implementation Agent:** Codex
**Implementation:** Not authorized
**Production:** Unchanged

---

# Objective

Create the documentation-only architecture for how Astra determines whether
external intelligence is necessary, constructs governed provider input
envelopes, selects eligible providers, validates provider responses, controls
cost and privacy risk, records bounded evidence, and remains
provider-independent.

---

# Deliverables

- `docs/astra-ai-external-intelligence-provider-architecture.md`
- `docs/architecture/decisions/astra-ai-external-intelligence-provider-architecture.md`
- `docs/iterations/2026-08-astra-ai/astra-007-architecture-review.md`
- `docs/iterations/2026-08-astra-ai/tasks/astra-007-external-intelligence-provider-architecture.md`
- updates to the Astra AI iteration overview, backlog, dependencies, risks,
  validation strategy, iteration index, and task log.

---

# Scope

Allowed:

- documentation;
- specification;
- external intelligence model;
- provider model;
- external-intelligence necessity model;
- provider capability classification;
- provider eligibility and routing;
- provider input envelope;
- prompt governance;
- response validation;
- hallucination boundaries;
- cost and token governance;
- privacy and data minimization;
- provider failure behavior;
- provider evidence model;
- multi-provider independence;
- security considerations;
- ADR proposal;
- task-log update.

Not allowed:

- implementation;
- `app/` changes;
- tests;
- runtime provider integration;
- OpenAI integration;
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
- generated artifacts;
- deployment changes;
- production behavior changes; or
- provider authorization.

---

# Required Sections

1. Purpose
2. Parent Architecture
3. Scope Boundary
4. External Intelligence Model
5. Provider Model
6. External Intelligence Necessity Model
7. Provider Capability Classification
8. Provider Eligibility And Routing
9. Provider Input Envelope
10. Prompt Governance
11. Response Validation
12. Hallucination Boundaries
13. Cost And Token Governance
14. Privacy And Data Minimization
15. Provider Failure Behaviour
16. Provider Evidence Model
17. Multi-Provider Independence
18. Security Considerations
19. Future Implementation Notes
20. ADR
21. Risks
22. Validation Strategy

---

# Required Engineering Laws

```text
Law 1
External intelligence extends Astra. It never replaces Astra.

Law 2
Astra must decide whether external intelligence is necessary before selecting a
provider.

Law 3
If Astra can answer correctly through local reasoning, governed Knowledge,
registered capabilities, approved context, or deterministic planning, it must
not call an external provider.

Law 4
Providers may assist with language, analysis, transformation, or generation,
but they do not own platform truth, identity, authorization, capability
existence, execution authority, or final decisions.

Law 5
External providers receive only policy-approved, minimized, purpose-bound input
envelopes. Raw internal context must not be sent by default.
```

---

# Final ASTRA-007 Draft Status

```text
ASTRA-007               Proposed
Parent                  ASTRA-001 Accepted
Parent                  ASTRA-002 Accepted
Parent                  ASTRA-003 Accepted
Parent                  ASTRA-004 Accepted
Parent                  ASTRA-005 Accepted
Parent                  ASTRA-006 Accepted
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

