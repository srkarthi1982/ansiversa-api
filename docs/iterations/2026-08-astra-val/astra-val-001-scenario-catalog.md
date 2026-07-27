# ASTRA-VAL-001 Scenario and Expected-Outcome Matrix

| Scenario | Expected certified outcome |
|---|---|
| `certified_default_fail_closed` | intent invalid; plan governance-blocked and empty |
| `unknown_capability` | fail closed |
| `forged_intent_binding` | rejected |
| `stale_turn` | rejected |
| `foreign_runtime` | rejected |
| `read_authorization_unavailable` | no decision released |
| `health_degraded` | degraded |
| `shutdown_invalidation` | captured interface invalidated |
| `evidence_capacity_failure` | no successful operation released |
| `production_boundaries` | all prohibitions preserved |

Ordering is the table order and is stable. All scenarios are certified-default scenarios; there are no fixture authorities or capabilities.

Expired/copied authority-proof evaluation is not reachable in the certified-default assembly because no certified proof issuer exists and the request contract rejects an empty proof set. Existing ASTRA-IMP-010 unit regressions continue to verify exact-object and expiration behavior; this harness does not fabricate a proof to repeat it.
