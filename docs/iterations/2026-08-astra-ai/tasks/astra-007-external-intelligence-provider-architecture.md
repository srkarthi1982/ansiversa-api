# ASTRA-007 - External Intelligence And Provider Architecture

**Status:** Frozen
**Created:** 2026-07-25
**Owner:** Karthikeyan Ramalingam
**Parent:** ASTRA-001 Vision And Core Architecture
**Parent:** ASTRA-002 Platform Intelligence Architecture
**Parent:** ASTRA-003 Conversation And Context Architecture
**Parent:** ASTRA-004 Capability Discovery And Tool Architecture
**Parent:** ASTRA-005 Execution Planning And Action Governance
**Parent:** ASTRA-006 Tool Execution Architecture
**Authorization:** Approved for documentation and architecture only
**Architecture Direction:** Approved
**Astra Re-review:** Approved
**Product Owner Approval:** Approved
**ADR:** Accepted
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

Astra source-level review of commit `ad3340e` approved the architecture
direction and required two targeted documentation refinements before freeze:

- separate provider eligibility from provider selection; and
- define provider response authority, making provider output advisory until
  validated by Astra and authoritative owners.

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
8. Provider Eligibility
9. Provider Selection And Routing
10. Provider Input Envelope
11. Prompt Governance
12. Response Validation
13. Hallucination Boundaries
14. Cost And Token Governance
15. Privacy And Data Minimization
16. Provider Failure Behaviour
17. Provider Evidence Model
18. Multi-Provider Independence
19. Security Considerations
20. Future Implementation Notes
21. ADR
22. Risks
23. Validation Strategy

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

Required Astra review refinements:

- Separate provider eligibility from provider selection.
- Define provider response authority so provider output remains advisory until
  validated by Astra and authoritative owners.

---

# Final ASTRA-007 Status

```text
ASTRA-007               Approved / Frozen
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
Astra Re-review         Approved
Product Owner Approval  Approved
ADR                     Accepted
Implementation          Not authorized
Production              Unchanged
ASTRA-008               Documentation only next; requires separate authorization
```
