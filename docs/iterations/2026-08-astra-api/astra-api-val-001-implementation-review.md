# ASTRA-API-VAL-001 Implementation Review Package

Status: Implemented / Pending Astra Re-review.

Validated parent: ASTRA-API-001 Certified / Approved with
ASTRA-API-001-COR-001 Certified / Approved.

## Implemented Design

ASTRA-API-VAL-001 provides one deterministic observational runner under
`validation/astra_api_val_001`. The runner is the single source for both pytest
coverage and the local CLI.

The CLI supports:

```text
python -m validation.astra_api_val_001.cli --list
python -m validation.astra_api_val_001.cli --scenario <name>
python -m validation.astra_api_val_001.cli --all --format text
python -m validation.astra_api_val_001.cli --all --format json
```

Output is ephemeral stdout-only text or JSON. No report file, telemetry sink,
database write, API mutation, or production behavior is introduced.

## Security Boundary

The validation harness verifies the certified diagnostics API from the outside:

- route registration and environment gates;
- authentication and admin authorization;
- disabled and production fail-closed behavior;
- strict redaction;
- explicit evidence references only;
- bounded request diagnostics;
- sanitized diagnostics validation errors;
- exact diagnostics validation route scope;
- component-health allowlist after ASTRA-API-001-COR-001;
- deterministic bounded error mapping;
- lifecycle cleanup;
- absence of forbidden surfaces.

The harness does not modify Runtime, diagnostics API implementation,
authentication, authorization, validation handler, component contracts,
projection engine, configuration, routes, database, SQL, frontend, deployment,
production configuration, ASTRA-IMP-001 through ASTRA-IMP-011, ASTRA-VAL-001,
or ASTRA-VAL-002.

## Review Focus

Reviewers should inspect:

- `AstraApiVal001ScenarioResult` bounded immutable result contract;
- fixed `SCENARIO_NAMES` ordering;
- recursive privacy leak inspector;
- semantic HTTP comparison variable-field exclusions;
- direct-router and `create_app()` route/environment checks;
- diagnostics validation handler registration in direct-router test apps;
- exact route-scope scenario for diagnostics root, diagnostics child,
  diagnostics-other, and diagnostics2;
- component-health expectations aligned to the certified correction.

## Validation

Focused ASTRA-API-VAL-001 pytest coverage passed locally.

```text
tests/test_astra_api_val_001_diagnostics_api_validation.py
12 passed
```

The validation phase is implemented and awaits Astra source/security review,
Product Owner approval, and certification.

## Source Review Correction

After Astra source/security review of commit `597ebc72`, two validator
corrections were applied.

Semantic HTTP comparison now preserves response structure. It no longer deletes
the full `evidence_references` field. It preserves field presence, list count,
ordering, empty versus populated state, redacted markers, and meaningful
structure while normalizing only opaque evidence IDs proven to be variable
issuance metadata. Scalar transport metadata such as request IDs and timestamps
is normalized by value rather than removed, so field presence remains
meaningful.

The focused tests prove:

- zero evidence references and one evidence reference are semantically
  different;
- same structure with different opaque issued evidence IDs is semantically
  equal;
- order differences remain semantically different;
- scalar identity field presence is preserved.

CLI text equivalence is now independently parsed and compared against runner
and JSON output. The comparison covers every field rendered by the text
contract for one successful strict projection scenario and one bounded
unavailable scenario.
