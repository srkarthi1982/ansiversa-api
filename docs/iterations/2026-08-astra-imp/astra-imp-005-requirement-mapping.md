# ASTRA-IMP-005 Constitution-To-Code Mapping

**Status:** Implemented / Pending Astra Source Review
**Task:** ASTRA-IMP-005
**Production Authorization:** Not approved
**Production:** Unchanged

---

# Mapping

| Constitutional source | Requirement area | Code support | Evidence/test support |
|---|---|---|---|
| ASTRA-001 | Runtime identity | immutable `AstraRuntimeIdentity` records runtime id, version, constitutional baseline, implementation phase, environment scope, and production authorization state | `test_runtime_starts_uninitialized_with_immutable_safe_identity` |
| ASTRA-002 | Governed intelligence boundary | runtime owns certified foundations but performs no reasoning, provider call, prompt invocation, or conversation behavior | `test_runtime_module_does_not_import_external_surfaces` |
| ASTRA-006 | Execution governance | runtime has no execution surface and cannot authorize production or tool handoff | `test_configuration_remains_disabled_and_non_production_authorized` |
| ASTRA-010 | Constitutional enforcement and safety | invalid lifecycle transitions fail deterministically, startup failure fails closed, bounded fault data excludes secrets | `test_invalid_lifecycle_transition_is_rejected`; `test_startup_failure_fails_closed_without_partial_ready_or_secret_fault` |
| ASTRA-010 | Audit evidence integrity | runtime owns an append-only in-memory evidence sink but does not become an Audit Engine | `test_evidence_sink_is_runtime_owned_and_receives_bounded_evidence` |
| ASTRA-IR-001 | Runtime owner for foundations | `AstraRuntime` registers configuration, governance, and evidence sink only | `test_startup_registers_only_authorized_foundation_components` |
| ASTRA-IMP-002 | Configuration foundation | runtime loads the certified disabled authoritative configuration and returns copy-safe access | `test_configuration_access_is_copy_safe_and_cannot_mutate_authority` |
| ASTRA-IMP-003 | Governance kernel | runtime exposes the certified governance evaluation reference only while ready | `test_governance_component_decides_but_disabled_configuration_does_not_allow` |
| ASTRA-IMP-004 | Evidence sink | each runtime creates an isolated in-memory evidence sink | `test_multiple_runtimes_have_isolated_evidence_sinks` |

---

# Boundary Confirmation

ASTRA-IMP-005 introduces no provider, prompt, model invocation, conversation
engine, context retrieval, capability discovery, planning, execution, Tool
Executor change, memory, learning, API, route, database, migration, frontend,
deployment, production configuration, production authorization, or production
behavior.
