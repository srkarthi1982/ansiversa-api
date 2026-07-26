# ASTRA-IMP-007 Constitution-To-Code Mapping

**Status:** Implemented / Corrections Applied / Pending Astra Re-review
**Task:** ASTRA-IMP-007
**Production Authorization:** Not approved
**Production:** Unchanged

---

# Mapping

| Source | Requirement area | Code support | Evidence/test support |
|---|---|---|---|
| ASTRA-001 | Runtime identity and ownership | Runtime owns and registers the Capability Discovery Engine | `test_runtime_registers_exactly_one_capability_discovery_engine` |
| ASTRA-002 | Governed behavior | discovery emits Runtime-governed evidence, records governance outcome, and releases metadata only for `allow` | `test_runtime_owned_discovery_is_deterministic_and_structural`; `test_fail_closed_discovery_returns_no_capabilities_but_records_evidence`; `test_non_allow_outcomes_cannot_expose_metadata` |
| ASTRA-003 | Bounded exposure | conversation-scoped discovery verifies certified engine ownership, runtime ownership, snapshot freshness, and eligible lifecycle before returning metadata | `test_conversation_discovery_integration_is_informational_only`; `test_conversation_from_another_runtime_is_rejected`; `test_fabricated_conversation_snapshot_is_rejected`; `test_same_runtime_unregistered_conversation_snapshot_is_rejected`; `test_closed_conversation_snapshot_is_rejected` |
| ASTRA-004 | Capability boundary | immutable capability metadata and sealed registry define capability existence without execution | `test_capability_model_is_immutable_metadata_only`; `test_registry_registration_and_discovery_order_are_deterministic` |
| ASTRA-005 | Planning separation | discovery exposes no planning surface | `test_module_does_not_import_unauthorized_surfaces` |
| ASTRA-006 | Execution separation | discovery stores no executable handlers and exposes no execution method | `test_capability_model_is_immutable_metadata_only`; `test_conversation_discovery_integration_is_informational_only` |
| ASTRA-007 | Provider independence | module imports no provider SDK and performs no provider interaction | `test_module_does_not_import_unauthorized_surfaces` |
| ASTRA-008 | Memory boundary | discovery stores no memory payloads or retrieval state | `test_module_does_not_import_unauthorized_surfaces` |
| ASTRA-009 | Adaptation boundary | discovery records no learning or adaptation data | `test_module_does_not_import_unauthorized_surfaces` |
| ASTRA-010 | Constitutional enforcement | duplicate and unknown capabilities fail deterministically; request context cannot broaden visibility; evidence append succeeds before result release | `test_registry_rejects_duplicates_and_unknown_lookup`; `test_allowed_unknown_capability_lookup_fails_after_governed_evidence`; `test_public_and_authenticated_contexts_cannot_self_select_internal_visibility`; `test_internal_visibility_requires_trusted_runtime_ownership`; `test_no_result_is_released_before_successful_evidence_append_and_sequence_commit` |
| ASTRA-IR-001 | Implementation roadmap | implements the next runtime-owned capability layer after Conversation Context | `tests/test_astra_capability_discovery_engine.py` |
| ASTRA-IMP-001 | Contracts | uses certified requirement and governance evidence contracts | `test_discovery_emits_bounded_evidence_without_execution` |
| ASTRA-IMP-002 | Configuration | discovery governance uses certified configuration identity | `test_runtime_owned_discovery_is_deterministic_and_structural` |
| ASTRA-IMP-003 | Governance | emits evidence through `runtime.evaluate_governance()` | `test_discovery_emits_bounded_evidence_without_execution` |
| ASTRA-IMP-004 | Evidence | appends evidence through `runtime.append_evidence()` | `test_discovery_emits_bounded_evidence_without_execution` |
| ASTRA-IMP-005 | Runtime | requires Runtime ownership and ready-state operation | `test_runtime_lifecycle_controls_capability_discovery_handles`; `test_engine_requires_runtime_ownership` |
| ASTRA-IMP-006 | Conversation | supports conversation-scoped informational discovery | `test_conversation_discovery_integration_is_informational_only` |

---

# Boundary Confirmation

ASTRA-IMP-007 introduces no tool execution, planning, provider integration,
prompt, model invocation, Tool Executor change, long-term memory, learning,
embedding, vector database, API, route, frontend, database, migration,
deployment, production configuration, production authorization, or production
behavior.
