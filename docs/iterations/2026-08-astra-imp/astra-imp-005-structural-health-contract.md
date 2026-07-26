# ASTRA-IMP-005 Structural Health Contract

**Status:** Implemented / Pending Astra Source Review
**Production Authorization:** Not approved

---

# Health Snapshot Fields

Structural health reports only bounded runtime metadata:

- runtime state;
- runtime identity;
- configuration loaded;
- configuration valid;
- governance available;
- evidence sink available;
- registered component identifiers;
- production authorization state;
- health outcome;
- bounded fault information when present;
- health timestamp.

---

# Health Outcomes

| Outcome | Condition |
|---|---|
| `healthy` | runtime is `ready`, certified components are available, configuration is valid, and registry is complete |
| `initializing` | runtime is in startup |
| `stopped` | runtime is `uninitialized`, `stopping`, or `stopped` |
| `degraded` | runtime is `ready` but a structural foundation is missing or invalid |
| `faulted` | runtime failed closed with bounded fault metadata |

---

# Excluded Health Data

Health does not include provider state, model state, conversation data, memory
contents, execution data, database state, network status, user data, prompts,
credentials, raw environment variables, hidden reasoning, or private payloads.
