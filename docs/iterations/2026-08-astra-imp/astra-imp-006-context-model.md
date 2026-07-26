# ASTRA-IMP-006 Context Model

**Status:** Implemented / Pending Astra Source Review
**Production Authorization:** Not approved

---

# Conversation Metadata

Conversation metadata contains only:

- conversation id;
- runtime instance id;
- created timestamp;
- last activity timestamp;
- conversation version;
- implementation reference;
- lifecycle state.

---

# Current Turn

Current-turn context contains only bounded request metadata:

- turn id;
- received timestamp;
- request reference;
- turn kind;
- optional route reference;
- bounded context references.

It does not contain raw user messages, prompts, hidden reasoning, provider
payloads, model parameters, app records, database rows, memory contents,
learning data, or execution payloads.

---

# Short Context

Short context is a bounded rolling history for the current session.

Rules:

- maximum size is configured at engine construction;
- allowed range is one to fifty entries;
- new entries append deterministically;
- overflow evicts oldest entries first;
- retrieval returns copy-safe immutable entries;
- short context is not long-term memory.
