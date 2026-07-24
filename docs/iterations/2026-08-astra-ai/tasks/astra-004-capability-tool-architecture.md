# ASTRA-004 - Capability Discovery And Tool Architecture

**Status:** Proposed
**Created:** 2026-07-24
**Owner:** Karthikeyan Ramalingam
**Parent:** ASTRA-001 Vision And Core Architecture
**Parent:** ASTRA-002 Platform Intelligence Architecture
**Parent:** ASTRA-003 Conversation And Context Architecture
**Authorization:** Approved for documentation and architecture only
**Architecture Direction:** Approved
**Architecture Review:** Minor revisions applied; pending Astra re-review
**Product Owner Approval:** Pending
**ADR:** Proposed
**Implementation Agent:** Codex
**Implementation:** Not authorized
**Production:** Unchanged

---

# Objective

Create the documentation-only architecture for how Astra AI discovers,
evaluates, classifies, selects, and governs platform capabilities and tools
without obtaining execution authority.

ASTRA-004 defines capability and tool models, registry authority, discovery
pipeline, ownership, availability states, selection rules, evidence, failure
behavior, security considerations, and future implementation notes.

---

# Deliverables

- `docs/astra-ai-capability-tool-architecture.md`
- `docs/architecture/decisions/astra-ai-capability-tool-architecture.md`
- `docs/iterations/2026-08-astra-ai/astra-004-architecture-review.md`
- `docs/iterations/2026-08-astra-ai/tasks/astra-004-capability-tool-architecture.md`
- updates to the Astra AI iteration overview, backlog, dependencies, risks,
  validation strategy, iteration index, and task log.

---

# Scope

Allowed:

- documentation;
- specification;
- architecture options;
- capability model;
- tool model;
- capability discovery pipeline;
- Tool Registry architecture;
- capability classification;
- tool classification;
- capability ownership;
- capability availability states;
- capability selection rules;
- capability evidence model;
- failure behavior;
- security considerations;
- ADR proposal;
- task-log update.

Not allowed:

- implementation;
- `app/` changes;
- tests;
- runtime route changes;
- public API exposure;
- routes;
- tool execution;
- AI provider or dependency changes;
- prompt implementation;
- model invocation;
- migrations;
- frontend changes;
- individual app integration;
- app database access;
- database changes;
- AI SEO implementation changes;
- generated artifacts;
- deployment changes;
- production behavior changes; or
- execution authorization.

---

# Required Sections

1. Purpose
2. Parent Architecture
3. Scope Boundary
4. Capability Model
5. Tool Model
6. Capability Discovery Pipeline
7. Tool Registry Architecture
8. Capability Classification
9. Tool Classification
10. Capability Ownership
11. Capability Availability States
12. Capability Selection Rules
13. Capability Evidence Model
14. Failure Behaviour
15. Security Considerations
16. Future Implementation Notes
17. ADR
18. Risks
19. Validation Strategy

---

# Required Engineering Laws

```text
Law 1
A capability is unavailable until an authoritative registry proves otherwise.

Law 2
Discovery never grants execution authority.

Law 3
Astra may discover capabilities, but only the owning service defines their
behavior.

Law 4
Capability selection must remain deterministic, explainable, and reviewable.
```

Required Astra review refinements:

- Separate registry permission requirements metadata from live user
  authorization truth.
- Define deterministic candidate precedence and ambiguity handling.

---

# Final ASTRA-004 Draft Status

```text
ASTRA-004               Proposed
Parent                  ASTRA-001 Accepted
Parent                  ASTRA-002 Accepted
Parent                  ASTRA-003 Accepted
Documentation Auth      Approved
Architecture Auth       Approved
Discovery               Complete
Specification           Complete
Architecture Direction  Approved
Architecture Review     Minor revisions applied; pending Astra re-review
Product Owner Approval  Pending
ADR                     Proposed
Implementation          Not authorized
Production              Unchanged
```
