# ASTRA-VAL-001 Scenario and Expected-Outcome Matrix

| Scenario | Expected certified outcome |
|---|---|
| `certified_default_fail_closed` | intent invalid; plan governance-blocked and empty |
| `unknown_capability` | fail closed |
| `forged_intent_binding` | rejected |
| `stale_turn` | rejected |
| `foreign_runtime` | rejected |
| `read_request_without_proofs` | rejected at request-contract boundary; engine not reached |
| `health_degraded` | degraded |
| `shutdown_invalidation` | captured interface invalidated |
| `current_turn_evidence_atomicity` | failed current-turn append commits no mutation |
| `production_boundaries` | all prohibitions preserved |

Ordering is the table order and is stable. All scenarios are certified-default scenarios; there are no fixture authorities or capabilities.

The empty-proof scenario proves only request-contract rejection and records `read_authorization_status=not_reached` plus `failure_reference=proofs_required_by_contract`. Engine-level authorization is unavailable by certified design because no capability or issuer exists. Expired/copied proof evaluation is likewise unreachable. ASTRA-IMP-010 unit regressions cover exact-object and expiration behavior without this harness fabricating authority.
