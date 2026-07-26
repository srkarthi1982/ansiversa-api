# ASTRA-IMP-006 Constitution-To-Code Mapping

**Status:** Implemented / Corrections Applied / Pending Astra Re-review
**Task:** ASTRA-IMP-006
**Production Authorization:** Not approved
**Production:** Unchanged

---

# Mapping

| Source | Requirement area | Code support | Evidence/test support |
|---|---|---|---|
| ASTRA-001 | Runtime identity and ownership | conversation metadata records the Runtime startup instance id, internal sessions require a runtime ownership token, and external callers receive immutable snapshots rather than mutators | `test_conversation_creation_is_deterministic_and_runtime_owned`; `test_conversation_cannot_exist_without_runtime_ownership_token`; `test_snapshot_obtained_before_shutdown_cannot_mutate_conversation` |
| ASTRA-002 | Governed behavior | engine uses Runtime-bound governance evidence and performs no intelligence | `test_evidence_is_emitted_through_runtime_core`; `test_module_does_not_import_unauthorized_surfaces` |
| ASTRA-003 | Bounded conversation/context | current-turn and short-context models store bounded metadata only, with monotonic timestamps | `test_current_turn_context_is_bounded_metadata_only`; `test_short_context_history_is_bounded_and_evicts_oldest`; `test_backdated_transitions_and_turns_fail` |
| ASTRA-004 | Capability boundary | engine performs no capability discovery or selection | `test_module_does_not_import_unauthorized_surfaces` |
| ASTRA-005 | Planning separation | engine does not create plans or action proposals | `test_module_does_not_import_unauthorized_surfaces` |
| ASTRA-006 | Execution separation | engine has no execution or Tool Executor surface | `test_module_does_not_import_unauthorized_surfaces` |
| ASTRA-007 | Provider independence | engine imports no provider SDK and stores no provider payloads | `test_module_does_not_import_unauthorized_surfaces` |
| ASTRA-008 | Memory boundary | short context is bounded session state and not long-term memory | `test_short_context_history_is_bounded_and_evicts_oldest` |
| ASTRA-009 | Adaptation boundary | engine records no learning or adaptation data | `test_module_does_not_import_unauthorized_surfaces` |
| ASTRA-010 | Constitutional enforcement | invalid lifecycle transitions, unsafe timestamps, stale mutable handles, and failed evidence append fail deterministically before state mutation | `test_invalid_lifecycle_transition_is_rejected`; `test_context_models_reject_naive_timestamps`; `test_snapshot_obtained_before_shutdown_cannot_mutate_conversation`; `test_evidence_failure_does_not_change_lifecycle_current_turn_or_history` |
| ASTRA-IR-001 | Implementation roadmap | implements the next runtime-owned conversation layer after Runtime Core | `tests/test_astra_conversation_context_engine.py` |
| ASTRA-IMP-001 | Contracts | uses certified bounded requirement and governance evidence contracts | `test_evidence_is_emitted_through_runtime_core` |
| ASTRA-IMP-002 | Configuration | governance evidence uses certified configuration identity | `test_evidence_is_emitted_through_runtime_core` |
| ASTRA-IMP-003 | Governance | emits governance evidence through `runtime.evaluate_governance()` | `test_governance_integration_fails_if_runtime_stops` |
| ASTRA-IMP-004 | Evidence | appends evidence through `runtime.append_evidence()` before committing conversation mutations | `test_evidence_is_emitted_through_runtime_core`; `test_evidence_capacity_failure_does_not_create_conversation`; `test_successful_operations_commit_exactly_one_evidence_record_together` |
| ASTRA-IMP-005 | Runtime | requires a ready `AstraRuntime` owner and integrates structural health | `test_engine_requires_ready_runtime_owner`; `test_health_integrates_runtime_status_without_runtime_authority_change` |

---

# Boundary Confirmation

ASTRA-IMP-006 introduces no provider, prompt, model invocation, planning,
execution, Tool Executor change, long-term memory, learning, embedding, vector
database, API, route, frontend, database, migration, deployment, production
configuration, production authorization, or production behavior.
