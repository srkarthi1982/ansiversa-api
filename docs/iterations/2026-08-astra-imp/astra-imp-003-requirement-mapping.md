# ASTRA-IMP-003 Constitution-To-Code Mapping

**Status:** Certified / Approved
**Task:** ASTRA-IMP-003
**Production Authorization:** Not approved
**Production:** Unchanged

---

# Mapping

| Constitutional source | Requirement area | Code support | Evidence/test support |
|---|---|---|---|
| ASTRA-002 | Governed reasoning and local deterministic behavior | `evaluate_governance()` returns deterministic `GovernanceDecision` for bounded input | `test_disabled_configuration_keeps_public_read_only_evaluation_non_authorizing` |
| ASTRA-003 | Context minimization boundaries | `GovernanceEvaluationInput` excludes raw prompts, private payloads, and unrelated user data; evidence is metadata-only | `test_evidence_contains_no_secret_or_prompt_payloads` |
| ASTRA-004 | Capability authority boundaries | Kernel does not discover or select capabilities; authority is represented only by `AuthorityClass` | `test_disabled_configuration_cannot_authorize_runtime_behavior` |
| ASTRA-005 | Approval and planning boundaries | approval states required/pending/denied cannot allow; kernel does not plan | `test_required_pending_or_denied_approval_cannot_allow` |
| ASTRA-006 | Execution authority and owner acceptance | execution handoff request fails closed; owner authority conflicts fail closed | `test_disabled_configuration_cannot_authorize_runtime_behavior`; `test_contradictory_facts_fail_closed` |
| ASTRA-007 | Provider advisory and eligibility | provider use and external exposure do not authorize provider calls | `test_disabled_configuration_cannot_authorize_runtime_behavior` |
| ASTRA-008 | Memory authorization | memory-use requests fail closed while configuration disables memory | `test_disabled_configuration_cannot_authorize_runtime_behavior` |
| ASTRA-009 | Adaptation activation | adaptation-use requests fail closed while configuration disables adaptation | `test_disabled_configuration_cannot_authorize_runtime_behavior` |
| ASTRA-010 | Precedence and fail-closed behavior | unknown compliance, unknown/prohibited safety, highest-authority precedence conflicts, and config mismatches fail closed | `test_unknown_compliance_fails_closed`; `test_unknown_and_prohibited_safety_cannot_allow`; `test_binding_block_overrides_lower_allow`; `test_fact_ordering_does_not_change_precedence_result` |
| ASTRA-010 | Safety classification | certified safety classes drive deterministic outcomes | `test_private_write_and_high_impact_require_explicit_approval` |
| ASTRA-010 | Evidence minimization | decisions return in-memory `BoundedEvidence` with metadata-only minimization and integrity digest | `test_bounded_evidence_contains_required_metadata`; `test_no_persistent_audit_write_occurs` |
| ASTRA-010 | Implementation and production separation | production boundary and production authorization do not allow production behavior | `test_production_boundary_requires_explicit_production_approval`; `test_environment_scope_does_not_create_authority` |
| ASTRA-IR-001 | Stage 2 Minimal Governance Kernel | `app/modules/astra_ai/governance.py` implements the Stage 2 internal evaluator | `tests/test_astra_governance_kernel.py` |
| ASTRA-IMP-001 | Certified contracts | output uses certified `GovernanceDecision` and `BoundedEvidence` | `tests/test_astra_constitutional_contracts.py` |
| ASTRA-IMP-002 | Certified configuration | evaluator consumes `get_astra_configuration()` only | `tests/test_astra_configuration_foundation.py`; `test_caller_mutation_does_not_change_authoritative_configuration` |

---

# Boundary Confirmation

ASTRA-IMP-003 does not introduce:

- dynamic policy engine;
- persistent audit or evidence storage;
- database changes;
- migrations;
- providers or provider SDKs;
- provider keys;
- prompts;
- model invocation;
- conversation runtime;
- context retrieval;
- capability discovery or selection;
- planning;
- execution handoff behavior;
- Tool Executor changes;
- app-owned business execution;
- memory storage or retrieval;
- embeddings;
- vector databases;
- learning or adaptation;
- APIs;
- routes;
- frontend changes;
- deployment changes;
- production configuration changes;
- production activation.
