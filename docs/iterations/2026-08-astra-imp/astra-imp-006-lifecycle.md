# ASTRA-IMP-006 Conversation Lifecycle

**Status:** Implemented / Corrections Applied / Pending Astra Re-review
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
- transition timestamps must be monotonic relative to the conversation's last
  activity timestamp;
- lifecycle changes are prepared first and committed only after bounded
  governance evidence is appended through Runtime Core;
- failed evidence append leaves lifecycle state and history unchanged;
- lifecycle does not authorize planning, execution, providers, memory, or
  learning.
