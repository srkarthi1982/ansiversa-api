# ASTRA-003 - Conversation And Context Architecture

**Status:** Frozen
**Created:** 2026-07-24
**Owner:** Karthikeyan Ramalingam
**Parent:** ASTRA-001 Vision And Core Architecture
**Parent:** ASTRA-002 Platform Intelligence Architecture
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

Create the documentation-only architecture for how Astra AI manages
conversation and context throughout the complete intelligence pipeline.

ASTRA-003 defines conversation lifecycle, context classification,
conversation state, context assembly, provider coordination, context
isolation, context expiration, clarification cycles, privacy, failure
behavior, security considerations, and future implementation notes.

---

# Deliverables

- `docs/astra-ai-conversation-context-architecture.md`
- `docs/architecture/decisions/astra-ai-conversation-context-architecture.md`
- `docs/iterations/2026-08-astra-ai/astra-003-architecture-review.md`
- `docs/iterations/2026-08-astra-ai/tasks/astra-003-conversation-context-architecture.md`
- updates to the Astra AI iteration overview, backlog, dependencies, risks,
  validation strategy, iteration index, and task log.

---

# Scope

Allowed:

- documentation;
- specification;
- architecture options;
- conversation lifecycle;
- context classification;
- conversation state model;
- context assembly model;
- context provider coordination;
- context isolation and expiration rules;
- clarification cycle;
- privacy model;
- ADR proposal;
- task-log update.

Not allowed:

- implementation;
- `app/` changes;
- tests;
- runtime route changes;
- public API exposure;
- routes;
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
- action execution authorization.

---

# Required Sections

1. Purpose
2. Parent Architecture
3. Scope Boundary
4. Conversation Lifecycle
5. Context Classification
6. Conversation State Model
7. Context Assembly Model
8. Context Provider Coordination
9. Context Authority Resolution
10. Context Isolation Rules
11. Context Expiration Rules
12. Clarification Cycle
13. Privacy Model
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
Conversation state is transient unless an independently governed architecture
explicitly defines persistence.

Law 2
Context is loaded because it is required, not because it is available.

Law 3
The smallest sufficient context is the preferred context.
```

---

# Final ASTRA-003 Status

```text
ASTRA-003               Approved
Parent                  ASTRA-001 Accepted
Parent                  ASTRA-002 Accepted
Documentation Auth      Approved
Architecture Auth       Approved
Discovery               Complete
Specification           Complete
Architecture Direction  Approved
Astra Re-review         Approved
Product Owner Approval  Approved
ADR                     Accepted
ASTRA-003 Freeze        Approved
Implementation          Not authorized
Production              Unchanged
ASTRA-004               Documentation only next; requires separate authorization
```
