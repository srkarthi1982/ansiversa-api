# ASTRA-VAL-002 Scenario Catalog

The runner order is fixed and shared by pytest and CLI.

| Order | Scenario | Group | Fixed expected outcome |
|---:|---|---|---|
| 1 | `deterministic_projection` | determinism | `deterministic_distinct_postures` |
| 2 | `authority_tamper_resistance` | authority | `all_rejected` |
| 3 | `correlation_integrity` | correlation | `explicit_only` |
| 4 | `evidence_integrity` | evidence | `structural_not_reproducible` |
| 5 | `strict_redaction_no_leak` | privacy | `strict_no_leak` |
| 6 | `completeness_precedence` | completeness | `precedence_preserved` |
| 7 | `timeline_bounds` | timeline | `bounded_deterministic` |
| 8 | `evidence_atomicity` | atomicity | `append_failure_atomic` |
| 9 | `lifecycle_health` | lifecycle | `shutdown_invalidated` |
| 10 | `exposure_boundaries` | exposure | `internal_only` |

Each scenario aggregates related assertions from the authorization package but
returns only the bounded result contract. Scenario logic exists only in
`validation.astra_val_002.runner`.
