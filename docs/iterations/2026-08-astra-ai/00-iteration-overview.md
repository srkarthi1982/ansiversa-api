# Iteration 3 - Astra AI Architecture

**Status:** ASTRA-001 Frozen; ASTRA-002 Frozen; ASTRA-003 Proposed
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
- [Astra AI Conversation And Context Architecture](../../astra-ai-conversation-context-architecture.md)
- [Astra AI Conversation And Context Architecture ADR](../../architecture/decisions/astra-ai-conversation-context-architecture.md)
- [ASTRA-003 architecture review package](astra-003-architecture-review.md)
- [ASTRA-003 task record](tasks/astra-003-conversation-context-architecture.md)
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

ASTRA-002 Platform Intelligence Architecture is approved and Frozen. Astra
approved the architecture direction, requested two minor ordering corrections,
approved the corrected source-level re-review for commit `01d2c55`, and
Product Owner approval is recorded. The ADR is accepted. ASTRA-002 inherits
ASTRA-001 and defines how Astra AI reasons over user requests before any new
intelligence implementation is written.

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

ASTRA-003 Conversation and Context Architecture is authorized for documentation
and architecture only and proposed for Astra review. ASTRA-003 inherits
ASTRA-001 and ASTRA-002 and defines how Astra manages conversation state and
context throughout the intelligence pipeline without creating ungoverned
memory, provider context, app data access, or production behavior.

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

ASTRA-003 succeeds when:

- ASTRA-001 and ASTRA-002 inheritance is explicit;
- conversation is separated from memory;
- memory is separated from Knowledge;
- context classes and owners are documented;
- conversation state is transient by default;
- context loading is need-driven, minimized, purpose-bound, and isolated;
- context provider authority is preserved;
- context expiration and stale-context behavior are documented;
- clarification cycles are governed;
- privacy and concurrent conversation isolation are documented;
- future interface support remains governed by the same context model;
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
