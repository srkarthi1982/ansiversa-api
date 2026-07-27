# ASTRA-VAL-002 Requirement Traceability

| Authorization requirement | Scenario/evidence |
|---|---|
| deterministic semantic comparison | `deterministic_projection`, `semantic_projection()` |
| exact authority and tamper rejection | `authority_tamper_resistance` |
| explicit links only; no inference | `correlation_integrity` |
| owning-sink structural integrity | `evidence_integrity` |
| digest not overstated | `evidence_integrity` |
| recursive privacy and strict matrix | `strict_redaction_no_leak` |
| inspector detects controlled leaks | negative inspector fixtures in authoritative pytest |
| completeness/state precedence | `completeness_precedence` |
| deterministic fixed 50 timeline | `timeline_bounds` |
| evidence-before-release atomicity | `evidence_atomicity` |
| lifecycle and health truthfulness | `lifecycle_health` |
| internal-only/forbidden surfaces | `exposure_boundaries` and source scans |
| shared pytest/CLI logic | `run_scenario()`, `run_all()`, CLI tests |
| runner/text/JSON semantic equivalence | independent CLI semantic parser test |
| ephemeral reports | stdout-only CLI and no-report test |
| frozen parent and VAL-001 | repository diff validation |

Implementation: `validation/astra_val_002/`.

Authoritative tests: `tests/test_astra_val_002_projection_validation.py`.
