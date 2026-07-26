# Astra Runtime Core

**Status:** Certified / Approved
**Task:** ASTRA-IMP-005
**Parent Constitution:** ASTRA-001 through ASTRA-010 Accepted / Frozen
**Parent Readiness:** ASTRA-IR-001 Accepted / Frozen
**Parent Implementations:** ASTRA-IMP-001 through ASTRA-IMP-004 Certified / Approved
**Implementation Scope:** Astra Runtime Core
**Production Authorization:** Not approved
**Production:** Unchanged
**ASTRA-IMP-006:** Not authorized

---

# Purpose

ASTRA-IMP-005 implements the minimal internal runtime owner for the certified
Astra foundations.

The runtime supplies static identity, startup-bound configuration metadata,
lifecycle, bounded component registration, runtime-bound component operations,
and structural health. It owns components; it does not become those components.

---

# Runtime Surface

The implementation lives at:

```text
app/modules/astra_ai/runtime.py
```

The runtime owns only:

- certified authoritative configuration access from ASTRA-IMP-002;
- certified Minimal Governance Kernel reference from ASTRA-IMP-003;
- one certified Minimal Evidence Sink instance from ASTRA-IMP-004;
- runtime identity metadata;
- runtime state;
- startup and shutdown;
- structural health snapshots;
- startup metadata from the exact validated startup configuration.

---

# Runtime Identity And Startup Metadata

Runtime identity is static, immutable, and bounded:

- runtime id;
- runtime name;
- runtime version;
- constitutional baseline;
- implementation phase and revision;
- startup instance id;
- creation timestamp.

Startup metadata is immutable and created only after successful configuration
loading and validation during `startup()`:

- configuration id;
- configuration version;
- startup timestamp;
- environment scope;
- production authorization state.

Neither identity nor startup metadata includes secrets, prompts, provider keys,
user data, database records, private payloads, raw environment variables, or
mutable authorization state.

---

# Runtime-Bound Operations

The runtime does not expose raw operational component handles. Governance and
evidence access use runtime-bound methods or lifecycle-aware interfaces:

```text
evaluate_governance(input)
append_evidence(evidence)
retrieve_evidence()
evidence_count()
```

Handles obtained while ready re-check runtime state at operation time. After
shutdown, stopped runtimes reject later governance and evidence operations.

---

# Boundary

ASTRA-IMP-005 does not introduce:

- conversation handling;
- memory retrieval;
- learning or adaptation;
- provider selection or SDK integration;
- prompts;
- model invocation;
- planning;
- execution;
- Tool Executor changes;
- APIs or routes;
- databases or migrations;
- frontend changes;
- deployment changes;
- production configuration changes;
- production activation.

The runtime coordinates certified foundations only. It does not authorize
production.

---

# Final State

```text
ASTRA-IMP-005               Certified / Approved
Implementation Scope        Astra Runtime Core
Implementation Direction    Approved
Astra Re-review             Approved
Constitutional Conformance  Approved
Product Owner Approval      Approved
Certification               Passed

Production Authorization    Not approved
Production                  Unchanged

ASTRA-IMP-006               Not authorized
Requires separate authorization
```
