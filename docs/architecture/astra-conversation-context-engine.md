# Astra Conversation Context Engine

**Status:** Implemented / Corrections Applied / Pending Astra Re-review
**Task:** ASTRA-IMP-006
**Parent Constitution:** ASTRA-001 through ASTRA-010 Accepted / Frozen
**Parent Readiness:** ASTRA-IR-001 Accepted / Frozen
**Parent Implementations:** ASTRA-IMP-001 through ASTRA-IMP-005 Certified / Approved
**Implementation Scope:** Conversation Context Engine
**Production Authorization:** Not approved
**Production:** Unchanged
**ASTRA-IMP-007:** Not authorized

---

# Purpose

ASTRA-IMP-006 implements a provider-independent Conversation Context Engine
owned by the certified Astra Runtime Core.

The engine represents bounded conversation and session context. It does not
perform intelligence, call models, create prompts, plan, execute, retrieve
memory, learn, expose APIs, persist data, or activate production behavior.

---

# Placement

The implementation lives at:

```text
app/modules/astra_ai/conversation_context.py
```

It is placed beside the certified Astra foundations and consumes the Runtime
Core through runtime-bound methods only.

---

# Conversation Model

Conversation metadata is immutable and bounded:

- conversation id;
- runtime instance id;
- creation timestamp;
- last activity timestamp;
- conversation version;
- implementation reference;
- lifecycle state.

Current-turn context stores only bounded request metadata:

- turn id;
- received timestamp;
- request reference;
- turn kind;
- optional route reference;
- bounded context references.

It does not store raw user messages, prompts, provider payloads, hidden
reasoning, memory payloads, or private records.

Short-context history is a bounded rolling session history. When the configured
limit is exceeded, the oldest entries are evicted deterministically. It is not
long-term memory.

---

# Runtime Ownership

`AstraConversationContextEngine` requires a ready `AstraRuntime` owner.

Conversation sessions are created with a runtime ownership token and include
the runtime startup instance id. Conversation sessions are not valid as
standalone runtime objects.

The production-facing engine returns immutable `AstraConversationSnapshot`
objects for observation. It does not expose mutable conversation sessions or
direct mutator handles. Conversation creation, lifecycle transitions, and
current-turn recording must pass through `AstraConversationContextEngine`,
which checks the owning `AstraRuntime` state at operation time.

The engine uses:

- `runtime.evaluate_governance(...)`;
- `runtime.append_evidence(...)`;
- `runtime.retrieve_evidence()`;
- `runtime.evidence_count()`.

It does not mutate Runtime Core authority or register new runtime foundation
components.

---

# Operation Atomicity

Conversation mutations are prepared before state is changed. The engine emits
governance evidence through the Runtime Core and commits the proposed
conversation registry, lifecycle, current-turn, short-context, and operation
sequence changes only after evidence append succeeds.

If evidence emission or append fails, the operation fails without partially
mutating conversation state. Conversation creation does not register a
conversation until evidence append succeeds.

Lifecycle transition timestamps and current-turn timestamps must be
timezone-aware and monotonic relative to the conversation's last activity.
Backdated transitions or turns fail before evidence emission and before state
mutation.

---

# Final Draft State

```text
ASTRA-IMP-006               Implemented
Implementation Scope        Conversation Context Engine
Implementation Direction    Approved
Astra Re-review             Pending
Constitutional Conformance  Pending
Product Owner Approval      Pending
Certification               Pending

Production Authorization    Not approved
Production                  Unchanged

ASTRA-IMP-007               Not authorized
Requires separate authorization
```
