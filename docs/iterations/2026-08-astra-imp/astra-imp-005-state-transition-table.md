# ASTRA-IMP-005 State Transition Table

**Status:** Certified / Approved
**Production Authorization:** Not approved

---

# Runtime States

| State | Meaning | Authorized outbound transition |
|---|---|---|
| `uninitialized` | Runtime object exists but certified foundations are not registered | `initializing` |
| `initializing` | Startup is loading and validating certified foundations | `ready`, `faulted` |
| `ready` | Certified foundations are registered and available | `stopping` |
| `stopping` | Runtime is releasing owned in-memory references | `stopped`, `faulted` |
| `stopped` | Runtime has released owned component references | none |
| `faulted` | Startup or shutdown failed closed with bounded fault metadata | `stopping` |

---

# Rules

- startup is allowed only from `uninitialized`;
- shutdown is allowed only from `ready` or `faulted`;
- stopped runtime cannot restart in ASTRA-IMP-005;
- repeated startup is rejected;
- invalid transitions raise `AstraRuntimeError`;
- startup failure clears partial component references and enters `faulted`;
- shutdown from `faulted` is allowed only for safe cleanup.
