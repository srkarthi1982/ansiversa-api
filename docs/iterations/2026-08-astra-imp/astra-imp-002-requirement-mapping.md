# ASTRA-IMP-002 Constitution-To-Code Mapping

**Status:** Implemented; Pending Astra Source Review
**Task:** ASTRA-IMP-002
**Production Authorization:** Not approved
**Production:** Unchanged

---

# Mapping

| Constitutional source | Requirement area | Code support | Evidence/test support |
|---|---|---|---|
| ASTRA-006 | Execution boundaries | `AstraConfigurationContract.execution_handoff` remains `disabled` in `load_astra_configuration` | `test_default_configuration_is_disabled_and_fail_closed`; `test_provider_memory_adaptation_and_execution_cannot_be_enabled` |
| ASTRA-007 | Provider-use boundaries | `provider_use` remains `disabled`; no provider keys or model settings are introduced | `test_default_configuration_is_disabled_and_fail_closed`; `test_provenance_is_bounded_and_contains_no_raw_secret_values` |
| ASTRA-008 | Memory-use boundaries | `memory_use` remains `disabled`; no memory store or retrieval behavior is introduced | `test_provider_memory_adaptation_and_execution_cannot_be_enabled` |
| ASTRA-009 | Adaptation boundaries | `adaptation_use` remains `disabled`; no learning or adaptation behavior is introduced | `test_provider_memory_adaptation_and_execution_cannot_be_enabled` |
| ASTRA-010 | Implementation and production separation | production scope still records `production_authorization_state=not_approved` | `test_production_environment_does_not_infer_authorization`; `test_production_authorization_cannot_be_inferred_or_overridden` |
| ASTRA-010 | Fail-closed behavior | `fail_closed_default` is true and non-fail-closed overrides fail | `test_default_configuration_is_disabled_and_fail_closed`; `test_non_fail_closed_configuration_fails` |
| ASTRA-010 | Configuration and rollout safety | unknown fields, invalid enum values, malformed identifiers, and malformed versions fail | `test_unknown_fields_fail`; `test_invalid_enum_values_fail`; `test_malformed_identifiers_and_versions_fail` |
| ASTRA-010 | Evidence minimization by configuration provenance | provenance includes bounded metadata only and no raw secret values | `test_provenance_is_bounded_and_contains_no_raw_secret_values` |
| ASTRA-IR-001 | Stage 1 bootstrap model | `app/modules/astra_ai/configuration.py` provides the Minimal Configuration Foundation after Stage 0 contracts | `test_every_supported_environment_loads_disabled` |
| ASTRA-IMP-001 | Certified configuration contract | loader creates `AstraConfigurationContract` and extends `ImplementationPhase` with `astra_imp_002` | `test_default_configuration_is_disabled_and_fail_closed`; `tests/test_astra_constitutional_contracts.py` |

---

# Boundary Confirmation

ASTRA-IMP-002 does not introduce:

- runtime Governance Kernel;
- persistent Audit Engine or evidence storage;
- providers or provider SDKs;
- provider keys or model configuration;
- prompts;
- model invocation;
- conversation runtime;
- context retrieval;
- capability selection;
- planning;
- execution handoff behavior;
- Tool Executor changes;
- memory storage or retrieval;
- embeddings;
- vector databases;
- learning or adaptation;
- APIs;
- routes;
- database changes;
- migrations;
- frontend changes;
- deployment changes;
- production configuration changes;
- production activation.
