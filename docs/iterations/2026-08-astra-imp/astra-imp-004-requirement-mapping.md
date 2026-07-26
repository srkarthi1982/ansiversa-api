# ASTRA-IMP-004 Constitution-To-Code Mapping

**Status:** Implemented; Pending Astra Source Review
**Task:** ASTRA-IMP-004
**Production Authorization:** Not approved
**Production:** Unchanged

---

# Mapping

| Constitutional source | Requirement area | Code support | Evidence/test support |
|---|---|---|---|
| ASTRA-003 | Context minimization boundaries | sink accepts only certified `BoundedEvidence` and no raw context payloads | `test_secret_bearing_evidence_input_is_rejected`; `test_malformed_evidence_is_rejected` |
| ASTRA-010 | Evidence integrity | evidence is revalidated before storage, duplicate IDs fail, insertion order is deterministic | `test_append_success_returns_copy_and_tracks_count`; `test_duplicate_evidence_identifier_is_rejected`; `test_retrieval_preserves_deterministic_insertion_order` |
| ASTRA-010 | Audit minimization | sink stores only metadata-only bounded evidence in memory and does not call audit storage | `test_no_persistent_audit_database_or_route_side_effects` |
| ASTRA-010 | Non-destructive correction | correction metadata is preserved through append and retrieval | `test_correction_chain_is_preserved` |
| ASTRA-010 | No silent mutation or backdating | retrieval returns copy-safe snapshots rather than mutable internal records | `test_retrieval_is_immutable_copy_safe` |
| ASTRA-IR-001 | Stage 3 Minimal Evidence Sink | `InMemoryEvidenceSink` receives bounded evidence without authority | `tests/test_astra_evidence_sink.py` |
| ASTRA-IMP-001 | Certified evidence contracts | sink accepts only `BoundedEvidence` and revalidates through the contract | `test_malformed_evidence_is_rejected` |
| ASTRA-IMP-002 | Certified configuration | sink consumes `get_astra_configuration()` and verifies disabled metadata-only boundaries | `test_configuration_remains_disabled_and_collection_does_not_authorize_runtime` |
| ASTRA-IMP-003 | Governance evidence output | tests append evidence emitted by `evaluate_governance()` | `governance_evidence()` helper in `tests/test_astra_evidence_sink.py` |

---

# Boundary Confirmation

ASTRA-IMP-004 does not introduce:

- Audit Engine;
- persistent audit or evidence storage;
- database changes;
- migrations;
- event bus or streaming;
- observability platform;
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
