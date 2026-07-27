# ASTRA-API-VAL-001 — Authenticated Diagnostics API Validation

Status: Implemented / Pending Astra Review.

This validation verifies the authenticated non-production diagnostics API
contracts after ASTRA-API-001-COR-001 certification.

Run all scenarios:

```text
python -m validation.astra_api_val_001.cli --all --format text
python -m validation.astra_api_val_001.cli --all --format json
```

Run pytest coverage:

```text
python -m pytest -q tests/test_astra_api_val_001_diagnostics_api_validation.py
```

Output is ephemeral stdout-only text/JSON. Generated report files, telemetry,
persistence, database writes, API mutations, frontend changes, deployment
changes, and production activation are not authorized.
