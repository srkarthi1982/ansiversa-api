# Astra Minimal Governance Kernel

**Status:** Certified / Approved
**Task:** ASTRA-IMP-003
**Parent Constitution:** ASTRA-001 through ASTRA-010 Accepted / Frozen
**Parent Readiness:** ASTRA-IR-001 Accepted / Frozen
**Parent Implementations:** ASTRA-IMP-001 and ASTRA-IMP-002 Certified / Approved
**Implementation Scope:** Minimal Governance Kernel
**Implementation Direction:** Approved
**Astra Re-review:** Approved
**Constitutional Conformance:** Approved
**Product Owner Approval:** Approved
**Certification:** Passed
**Production Authorization:** Not approved
**Production:** Unchanged
**ASTRA-IMP-004:** Not authorized

---

# Purpose

ASTRA-IMP-003 implements the Stage 2 Minimal Governance Kernel from
ASTRA-IR-001.

The kernel deterministically evaluates bounded governance inputs and returns a
certified `GovernanceDecision` plus bounded in-memory evidence metadata.

It decides only. It does not plan, execute, call providers, retrieve memory,
invoke prompts, expose APIs, write audit records, access databases, or change
production behavior.

---

# Discovery Findings

Codex inspected the certified contracts and configuration foundations plus
existing auth, authorization, Assistant, Knowledge, Tool Registry, User Context,
audit, and app-owned service surfaces.

Findings:

- `app/modules/astra_ai/constitutional_contracts.py` provides the certified
  `GovernanceDecision`, `BoundedEvidence`, requirement references, safety,
  authority, approval, failure posture, and runtime-use contracts.
- `app/modules/astra_ai/configuration.py` provides the certified authoritative
  disabled-by-default Astra configuration access.
- `app/modules/astra_ai/policy.py` contains existing deterministic Assistant
  policy classification, but it is assistant-runtime-specific and remains
  separate.
- `app/modules/assistant/tools.py` contains Tool Registry and Tool Executor
  contracts. ASTRA-IMP-003 does not import or modify them.
- `app/modules/audit` contains persisted audit storage. ASTRA-IMP-003 does not
  import or write to persistent audit storage.
- Auth and app-owned services remain authoritative for identity, ownership, and
  business truth. The kernel represents bounded facts only.

No constitutional or readiness conflict was found.

---

# Placement And Ownership

The implementation lives at:

```text
app/modules/astra_ai/governance.py
```

Ownership:

- Astra AI owns the internal governance input, policy fact, result, and
  deterministic evaluator.
- ASTRA-IMP-001 owns the certified output and evidence contracts.
- ASTRA-IMP-002 owns authoritative configuration access.
- Existing auth, Assistant, Knowledge, Tool Registry, audit, and app-owned
  services remain authoritative for their own domains.

---

# Deterministic Rule Matrix

Rules are evaluated in this order:

| Order | Rule | Outcome |
|---|---|---|
| 1 | Configuration does not fail closed | `fail_closed` |
| 2 | Input configuration ID/version differs from authoritative configuration | `fail_closed` |
| 3 | Configuration feature state is enabled through a future uncertified path | `fail_closed` |
| 4 | Constitutional compliance is unknown or conflicted | `fail_closed` |
| 5 | Safety class is `unknown` or `prohibited` | `fail_closed` |
| 6 | Approval is required, pending, or denied | `fail_closed` |
| 7 | Consent is required, pending, or denied | `fail_closed` |
| 8 | Owner authority is unverified, denied, or conflicted | `fail_closed` |
| 9 | Production boundary lacks production approval | `fail_closed` |
| 10 | Private-write or high-impact safety lacks explicit approval | `fail_closed` |
| 11 | Provider, memory, adaptation, or execution use is requested while disabled | `fail_closed` |
| 12 | Highest-authority bounded precedence facts block, conflict, or remain unknown | `fail_closed` |
| 13 | Execution or production authority is requested | `fail_closed` |
| 14 | External exposure is requested | `defer` |
| 15 | Authoritative Astra feature state is disabled | `fail_closed` |
| 16 | Public/private-read advisory or read-only request is otherwise valid under an enabled certified configuration | `allow` |
| 17 | No deterministic allow path applies | `clarify` |

Bounded precedence facts are grouped by authority level. The highest-authority
level containing facts governs. Same-level allow/block conflicts and unknown
decisive facts fail closed. A resolved higher-precedence allow cannot be
overridden by lower-precedence user, provider, inference, or runtime facts.

The certified ASTRA-IMP-002 configuration remains disabled. While disabled, the
kernel may perform deterministic governance assessment, but it must not return
`GovernanceOutcome.ALLOW`.

---

# Evidence

The kernel returns in-memory `BoundedEvidence` for each decision.

Evidence includes:

- governance decision reference;
- governing constitutional requirements;
- safety classification;
- authority class;
- approval state;
- outcome;
- failure posture;
- configuration identifier and version reference;
- timestamp supplied by the bounded input;
- bounded provenance digest.

Evidence contains no raw prompts, hidden reasoning, provider responses, full
private payloads, credentials, secrets, app records, unrelated user data, or
audit-storage side effects.

---

# Final Implementation State

```text
ASTRA-IMP-003               Certified / Approved
Implementation Scope        Minimal Governance Kernel
Implementation Direction    Approved
Astra Re-review             Approved
Constitutional Conformance  Approved
Product Owner Approval      Approved
Certification               Passed

Production Authorization    Not approved
Production                  Unchanged

ASTRA-IMP-004               Not authorized
Requires separate authorization
```
