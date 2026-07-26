# ASTRA-IMP-005 Component Registration Matrix

**Status:** Certified / Approved
**Production Authorization:** Not approved

---

# Authorized Components

| Component id | Owner | Source phase | Runtime role | Replacement allowed |
|---|---|---|---|---|
| `configuration` | ASTRA-IMP-002 | `get_astra_configuration()` | authoritative disabled configuration reference | No |
| `governance` | ASTRA-IMP-003 | runtime-bound `evaluate_governance` operation | deterministic governance evaluation while runtime is ready | No |
| `evidence_sink` | ASTRA-IMP-004 | runtime-bound evidence operations over `InMemoryEvidenceSink` | bounded in-memory evidence receive/retrieve/count while runtime is ready | No |

---

# Registry Rules

- unknown component identifiers are rejected;
- duplicate registration is rejected;
- incomplete registry sealing is rejected;
- registry order is deterministic;
- registry metadata is immutable;
- the registry is sealed after startup;
- the registry is not a plugin registry, service locator, provider manager,
  app registry, route registry, or execution framework.
