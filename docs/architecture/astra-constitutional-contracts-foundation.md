# Astra Constitutional Contracts Foundation

**Status:** Implemented
**Task:** ASTRA-IMP-001
**Parent Constitution:** ASTRA-001 through ASTRA-010 Accepted / Frozen
**Parent Readiness:** ASTRA-IR-001 Accepted / Frozen
**Implementation Scope:** Constitutional Contracts Foundation
**Constitutional Conformance:** Pending Astra Source Review
**Product Owner Approval:** Pending
**Certification:** Pending
**Production Authorization:** Not approved
**Production:** Unchanged

---

# Purpose

ASTRA-IMP-001 implements the Stage 0 contract foundation required by
ASTRA-IR-001 before any runtime intelligence, provider invocation, memory,
learning, planning, execution, route, database, migration, frontend, deployment,
or production behavior is introduced.

The foundation defines stable implementation-facing contracts for:

- constitutional requirement identifiers;
- bounded governance decisions;
- bounded evidence metadata;
- disabled-by-default Astra configuration; and
- deterministic contract serialization and validation.

These contracts do not create authority. They describe implementation evidence
and validation shapes future Astra components must satisfy after separate
authorization.

---

# Discovery Findings

Existing foundations were inspected before modification:

- `app/modules/astra_ai` already exists as a disabled-by-default isolated Astra
  package and is not mounted as a FastAPI route.
- `app/modules/astra_ai/contracts.py` contains Phase 1 assistant, context,
  intent, response, and audit metadata models.
- `app/modules/astra_ai/settings.py` keeps Astra platform behavior disabled by
  default.
- `app/modules/astra_ai/audit.py` already performs bounded deterministic audit
  metadata creation and secret scanning for the existing Phase 1 package.
- `app/modules/assistant/tools.py` contains the existing Assistant Tool
  Framework contracts, registry metadata, executor validation, and safe audit
  metadata.
- `app/modules/knowledge` remains the governed Knowledge Registry foundation.
- `app/modules/auth` remains the authoritative authentication foundation.
- `app/modules/audit` remains the existing persisted audit-log module.
- `app/core/config.py` remains the existing environment/settings foundation.

No constitutional conflict was found.

---

# Placement And Ownership

The new Stage 0 contract layer is placed at:

```text
app/modules/astra_ai/constitutional_contracts.py
```

Ownership:

- Astra AI owns the constitutional contract definitions.
- Existing Assistant, Knowledge, Tool Framework, Tool Registry, User Context
  Provider, auth, audit, and configuration foundations remain authoritative for
  their current runtime responsibilities.
- The new module does not replace or duplicate existing runtime foundations.
- The new module is not mounted as a route and does not alter startup behavior.

---

# Reused Foundations

Reused:

- Pydantic model validation pattern from existing backend schemas.
- `StrEnum` enum style already used by `app/modules/astra_ai/contracts.py`.
- Disabled-by-default Astra package boundary from `app/modules/astra_ai`.
- Existing secret-pattern approach from Astra audit metadata.
- Existing test style using focused pytest/unittest modules.

New:

- `ConstitutionalRequirement`
- `ConstitutionalRequirementReference`
- `GovernanceDecision`
- `BoundedEvidence`
- `EvidenceIntegrityMetadata`
- `EvidenceCorrectionMetadata`
- `AstraConfigurationContract`
- deterministic `canonical_contract_json`

---

# Implemented Boundaries

The contract validators reject:

- unknown mandatory enum values;
- missing requirement references for governed decisions and evidence;
- invalid coverage states;
- malformed requirement IDs, evidence IDs, versions, and stable identifiers;
- allow decisions that bypass required, pending, or denied approval;
- unknown safety classifications being allowed;
- prohibited safety classifications being allowed;
- private-write or high-impact allow decisions without explicit approval;
- fail-closed outcomes without fail-closed posture;
- evidence metadata containing secret, credential, raw prompt, hidden
  reasoning, full private payload, or unrelated-user-data markers;
- correction metadata without a superseded evidence identifier;
- evidence corrections that omit correcting authority, timestamp, replacement
  reference, retention treatment, or privacy treatment;
- evidence corrections with naive timestamps or secret-bearing metadata;
- restricted evidence without redaction or no-payload minimization;
- Stage 0 configuration that enables Astra runtime behavior;
- Stage 0 configuration that records production authorization; and
- Stage 0 configuration that disables fail-closed defaults.

`SafetyClassification` uses the frozen ASTRA-010 safety classes:

```text
public
private_read
private_write
high_impact
cross_owner
external_exposure
constitutional
prohibited
unknown
```

Stage 0 does not introduce a second safety taxonomy.

---

# Disabled By Default

`AstraConfigurationContract` defaults to:

```text
feature_enabled                 false
provider_use                    disabled
memory_use                      disabled
adaptation_use                  disabled
execution_handoff               disabled
audit_evidence_behavior         metadata_only
fail_closed_default             true
production_authorization_state  not_approved
```

Passing contract validation does not authorize runtime use, implementation
expansion, production configuration, or production behavior.

---

# Constitutional Requirement Mapping

| Source | Requirement | Implemented support |
|---|---|---|
| ASTRA-002 | Local sufficiency and governed decision evidence | `GovernanceDecision` can reference local-sufficiency requirements and bounded evidence. |
| ASTRA-003 | Context minimization | `BoundedEvidence` supports metadata-only, redacted-reference, summary-only, and no-payload minimization classes. |
| ASTRA-005 | Plan/version and approval evidence boundaries | Governance decisions carry requirement references, approval state, reason class, failure posture, and version markers. |
| ASTRA-006 | Execution authority boundaries | Execution-related decisions can be represented as approval-required or execution-boundary decisions without executing. |
| ASTRA-007 | Provider eligibility and advisory-response boundaries | Provider eligibility and advisory-response reason classes exist without provider routing or SDK integration. |
| ASTRA-008 | Memory ownership and retrieval authorization | Memory ownership and retrieval-authorization reason classes exist without memory storage or retrieval. |
| ASTRA-009 | Adaptation activation boundaries | Adaptation activation reason class exists without learning, fine-tuning, or adaptation behavior. |
| ASTRA-010 | Precedence, fail-closed behavior, evidence minimization, implementation/production separation, audit integrity | Contract validation enforces fail-closed consistency, evidence minimization, production authorization separation, and integrity metadata. |
| ASTRA-IR-001 | Stage 0 bootstrap and conformance-matrix requirements | Stable requirement references, governance decisions, bounded evidence, and disabled configuration are now implemented. |

---

# Validation

Focused tests live at:

```text
tests/test_astra_constitutional_contracts.py
```

They cover valid contract creation, invalid contract rejection, every
ASTRA-010 safety class, unknown/prohibited safety allow rejection,
private-write/high-impact approval gates, fail-closed defaults,
disabled-by-default configuration, production authorization separation,
evidence minimization, prohibited evidence categories, non-destructive
evidence-correction metadata, stable serialization, and extension-safe strict
schema behavior.

---

# Final Implementation State

```text
ASTRA-IMP-001               Implemented
Implementation Scope        Constitutional Contracts Foundation
Constitutional Conformance  Pending Astra Source Review
Product Owner Approval      Pending
Certification               Pending
Production Authorization    Not approved
Production                  Unchanged
```
