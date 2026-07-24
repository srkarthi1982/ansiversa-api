# Iteration 3 - Astra AI Architecture

**Status:** ASTRA-001 Frozen; ASTRA-002 ready for Product Owner approval
**Created:** 2026-07-24
**Implementation:** Not authorized
**Production:** Unchanged

---

# Objective

Define the constitutional architecture for Astra AI before expanding beyond
the frozen Phase 1 foundation.

This iteration establishes what Astra AI is, what it owns, how it relates to
the existing Assistant and platform systems, and how future capabilities must
be reviewed before implementation.

---

# Deliverables

- [Astra AI Vision And Core Architecture](../../astra-ai-vision-core-architecture.md)
- [Astra AI Vision And Core Architecture ADR](../../architecture/decisions/astra-ai-vision-core-architecture.md)
- [ASTRA-001 discovery](astra-001-discovery.md)
- [ASTRA-001 architecture review package](astra-001-architecture-review.md)
- [ASTRA-001 task record](tasks/astra-001-vision-core-architecture.md)
- [Astra AI Platform Intelligence Architecture](../../astra-ai-platform-intelligence-architecture.md)
- [Astra AI Platform Intelligence Architecture ADR](../../architecture/decisions/astra-ai-platform-intelligence-architecture.md)
- [ASTRA-002 architecture review package](astra-002-architecture-review.md)
- [ASTRA-002 task record](tasks/astra-002-platform-intelligence-architecture.md)
- [Priority backlog](01-priority-backlog.md)
- [Dependencies](02-dependencies.md)
- [Risk register](03-risk-register.md)
- [Validation strategy](04-validation-strategy.md)

---

# Lifecycle

```text
Discovery
    ↓
Architecture proposal
    ↓
Astra architecture review
    ↓
Product Owner approval
    ↓
Task freeze
    ↓
Separate implementation authorization
```

ASTRA-001 is approved and Frozen after Astra re-review and Product Owner
approval. The ADR is accepted. ASTRA-001 does not authorize Phase 2
implementation, runtime changes, app integration, providers, APIs, migrations,
frontend changes, deployment changes, or production behavior. Phase 2 is
documentation-only next and requires separate authorization before work begins.

ASTRA-002 Platform Intelligence Architecture is authorized for documentation
only. Astra approved the architecture direction, requested two minor ordering
corrections, and approved the corrected source-level re-review for commit
`01d2c55`. ASTRA-002 is ready for Product Owner approval, ADR acceptance, and
freeze. ASTRA-002 inherits ASTRA-001 and defines how Astra AI reasons over user
requests before any new intelligence implementation is written.

---

# Current Foundation

Astra AI Platform Phase 1 is completed and Frozen. It provides an isolated
disabled-by-default backend package with internal contracts, governed platform
context, platform intents, policy decisions, response planning, action
proposals, and deterministic audit evidence.

Existing Assistant, Knowledge, user context, tool registry, AI SEO, auth, and
app-service foundations remain the systems Astra AI should consume rather than
duplicate.

ASTRA-002 documents the logical pipeline from user request through
conversation understanding, intent recognition, context assembly, permission
evaluation, capability discovery, planning, action proposal, decision evidence
assembly, and governed response construction.

---

# Success Criteria

ASTRA-001 succeeds when:

- current implementation and gaps are accurately inventoried;
- Product Owner vision is recorded;
- ownership boundaries are explicit;
- architecture options are critically evaluated;
- a recommended architecture is proposed;
- relationship to Assistant, Knowledge, AI SEO, tools, auth, app APIs, app
  databases, frontend, audit, and providers is defined;
- Phase 1 is reconciled without reopening code;
- risks and validation strategy are documented;
- no implementation occurs; and
- production remains unchanged.

ASTRA-002 succeeds when:

- ASTRA-001 inheritance is explicit;
- the full platform intelligence pipeline is documented;
- each pipeline stage defines purpose, inputs, outputs, ownership, failure
  behavior, security considerations, and future implementation notes;
- the Intelligence Decision Matrix is recorded;
- external intelligence is optional rather than default;
- local response preference is defined;
- refusal and clarification are first-class outcomes;
- no implementation occurs; and
- production remains unchanged.

---

# Non-Goals

- Phase 2 implementation;
- runtime route changes;
- public API exposure;
- app integration;
- app database access;
- tool execution expansion;
- provider dependency changes;
- migrations;
- frontend changes;
- deployment changes;
- AI SEO implementation changes;
- production authorization; and
- implementation before separate authorization.
