# ASTRA-IMP-006 Conversation Lifecycle

**Status:** Implemented / Pending Astra Source Review
**Production Authorization:** Not approved

---

# Lifecycle States

| State | Meaning | Authorized outbound transitions |
|---|---|---|
| `created` | Conversation metadata exists and is owned by Runtime | `active`, `closing`, `faulted` |
| `active` | Current session context can receive bounded turns | `idle`, `closing`, `faulted` |
| `idle` | Session remains open but inactive | `active`, `closing`, `faulted` |
| `closing` | Session is ending and no new turns should be recorded | `closed`, `faulted` |
| `closed` | Session is complete | none |
| `faulted` | Session failed closed | `closing` |

---

# Rules

- invalid transitions raise `AstraConversationContextError`;
- current turns cannot be recorded after `closing`, `closed`, or `faulted`;
- lifecycle changes update immutable metadata through a new metadata instance;
- lifecycle entries are recorded in bounded short-context history;
- lifecycle does not authorize planning, execution, providers, memory, or
  learning.
