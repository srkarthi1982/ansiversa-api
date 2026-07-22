# I1-010 — Astra Conversation Context

**Iteration:** 2026-07-next
**Priority:** Medium
**Status:** Frozen
**Depends On:** I1-003 — Platform User Context Provider
**Depends On:** I1-004 — Quiz Astra AI Integration
**Primary Repository:** `ansiversa-api`
**Supporting Repository:** `ansiversa`

---

# Objective

Enable Astra AI to understand follow-up questions within the current conversation without requiring the user to repeat previous information.

Conversation context should improve usability while remaining bounded, predictable, and privacy-safe.

---

# Existing System Touchpoints

Extend the existing Assistant request context, frontend Assistant conversation
state, Assistant routing, and response handling. Do not introduce persistent
memory or replace current response modes.

---

# Vision

Users should be able to have a natural conversation with Astra.

Example:

User:
> Which Quiz platforms have I completed?

Astra:
> You have completed Soft Skills and Communication Skills.

User:
> Which one took me the longest?

Astra should understand that "one" refers to the previously returned completed Quiz platforms.

---

# Scope

Phase 1 supports only short-lived conversation context.

Context exists only during the active conversation.

No permanent learning or long-term memory is introduced.

---

# Supported Follow-Up Examples

- Which one?
- Tell me more.
- Why?
- Continue.
- Show details.
- What about the other one?
- Which is better?
- When did I complete it?
- Open it.
- Explain that.

---

# Context Rules

Conversation context should contain only the minimum information necessary.

Examples:

- last intent
- last application
- last tool results
- selected entity
- selected recommendation
- previous actions

Do not retain raw database records unnecessarily.

---

# Context Lifetime

Context should expire:

- when the conversation is reset
- after inactivity timeout
- after explicit "Start Over"
- after logout

A new conversation begins with an empty context.

---

# Ownership

Conversation context belongs only to the authenticated user.

It must never be shared across users or sessions.

---

# Privacy

Do not store:

- passwords
- authentication tokens
- raw SQL
- hidden tool payloads
- sensitive database fields
- another user's information

Only store references needed for follow-up resolution.

---

# Resolution Rules

When a follow-up question is received:

1. Attempt to resolve against current conversation context.
2. If ambiguous, ask a clarification question.
3. Never guess between multiple valid entities.

Example:

User:
> Open it.

If multiple valid targets exist:

Astra:

> Which one would you like to open?
> • Soft Skills
> • Communication Skills

---

# Response Behavior

Conversation context must never change factual data.

It only resolves references such as:

- it
- that
- the other one
- continue
- previous result

Business logic remains inside the application.

---

# Performance

Requirements:

- lightweight context object
- bounded size
- automatic cleanup
- no unnecessary database reads
- no cross-session persistence

---

# Tests

Include tests for:

- single follow-up
- multiple follow-ups
- ambiguous references
- expired context
- logout
- conversation reset
- context after tool failure
- context after unsupported question

---

# Browser Verification

Verify:

- follow-up questions work naturally
- reset clears context
- logout clears context
- mobile behavior
- desktop behavior

---

# Acceptance Criteria

The task is complete when:

- Astra resolves follow-up questions correctly.
- Context remains bounded.
- Context expires correctly.
- Cross-user isolation is proven.
- Privacy rules are preserved.
- Browser verification passes.

---

# Success Criteria

A user should be able to talk naturally with Astra without repeating every previous answer, while the system remains deterministic, secure, and predictable.

---

# Future Scope

Not included:

- long-term memory
- proactive memory
- learning user preferences
- cross-session memory
- permanent profile learning

---

# Delivery

After implementation, report:

- context architecture
- lifetime rules
- storage mechanism
- ambiguity handling
- browser verification
- backend verification
- known limitations
- repository status

Confirm explicitly:

- Context is conversation-scoped.
- Context never crosses user boundaries.
- Business logic remains application-owned.
- No long-term memory was introduced.
- Existing Astra behavior remains unchanged.
- Exactly 100 apps remain.
- No App #101 was introduced.
- All repositories are clean and aligned with `origin/main`.
