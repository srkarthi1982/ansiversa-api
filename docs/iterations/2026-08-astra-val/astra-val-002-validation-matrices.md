# ASTRA-VAL-002 Validation Matrices

## Authority and tamper resistance

| Input | Expected |
|---|---|
| exact Runtime-issued request/output | accepted |
| caller-created/reconstructed request | rejected |
| copied/altered/expired request | rejected |
| foreign Runtime request/output | rejected |
| copied intent/plan | rejected |
| fabricated read decision | rejected |
| unsupported output registration surface | unavailable |
| captured interface after shutdown | rejected |

## Integrity terminology

| Condition | Reference | Contract | Provenance | Digest | Overall |
|---|---|---|---|---|---|
| owning-sink valid record | resolved | valid | valid_structural | not_reproducible | resolved_structural |
| absent/foreign reference | missing | unavailable | unavailable | unavailable | missing |

`verified` is prohibited without a certified producer-owned reproducible
verification contract. Digest format alone is not verification. A contract-invalid
record cannot enter the certified Evidence Sink through public append; the
harness verifies contract rejection and does not mutate private storage merely
to manufacture an otherwise unreachable stored-invalid state.

## Completeness and states

| Condition | Result |
|---|---|
| fully available structural summary | complete |
| optional evidence/correlation missing | partial |
| required evidence missing/invalid | unavailable |
| strict protected-data omission | redacted unless required invalidity is stronger |
| unrequested stage | not_applicable stage only |
| incompatible explicit references | conflicting |

## Timeline

| Condition | Expected |
|---|---|
| equal timestamps | reference then stage ordering |
| up to 50 eligible entries | not truncated |
| more than 50 | first 50, truncated, remainder unavailable, partial |
| missing relationship | no synthetic entry |
| pagination/continuation/global enumeration | absent |

## Exposure and forbidden surfaces

All projections remain internal-only with API, UI, public, and production
exposure false. The validation package contains no API, UI, telemetry,
persistence, database, SQL, provider, execution, deployment, or production
surface.
