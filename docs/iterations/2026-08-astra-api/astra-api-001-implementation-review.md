# ASTRA-API-001 Implementation Review Package

## Discovery Findings

FastAPI route registration is centralized in `app/main.py`.

Authentication is owned by `app/modules/auth/service.py` through
`get_current_user`.

Administrator authorization is already provided by
`app/modules/auth/dependencies.py` through `require_admin_user`.

Environment identity is already represented by `APP_ENV` and `VERCEL_ENV`.

Certified ASTRA-IMP-011 projection creation is available through
`AstraRuntime.diagnostic_projection.issue_request()` and `.project()`.

No existing developer/staff permission framework beyond admin authorization was
found.

## Implemented Design

The API is registered only when `ASTRA_DIAGNOSTICS_API_ENABLED=true` and the
environment resolves to local, development, test, qa, preview, or staging.
Production and unknown environments do not register the route and endpoint
checks also fail closed.

The diagnostics service owns a process-local Runtime for non-production
diagnostics only. It starts after authentication, admin authorization,
diagnostics enablement, and environment checks pass.

Response payloads wrap certified projection DTOs without changing projection
semantics. Transport adds only envelope metadata and redaction policy metadata.

## Security Test Matrix

| Case | Coverage |
| --- | --- |
| anonymous caller rejected | `test_anonymous_caller_is_rejected_before_diagnostics_access` |
| authenticated non-admin rejected | `test_authenticated_non_admin_cannot_self_authorize_with_payload_role` |
| disabled flag rejected | `test_disabled_production_and_unknown_environment_fail_closed` |
| production rejected | `test_disabled_production_and_unknown_environment_fail_closed` |
| unknown environment rejected | `test_disabled_production_and_unknown_environment_fail_closed` |
| production route not registered | `test_main_app_does_not_register_diagnostics_in_production` |
| strict projection default | `test_runtime_projection_uses_strict_certified_projection_transport` |
| metadata-only denied | `test_metadata_only_redaction_is_not_authorized` |
| duplicate evidence references rejected | `test_evidence_projection_rejects_duplicates_and_preserves_missing_state` |
| missing evidence remains missing | `test_evidence_projection_rejects_duplicates_and_preserves_missing_state` |
| request diagnostic unavailable | `test_request_diagnostic_endpoint_is_bounded_unavailable` |
| component fixed allowlist | `test_component_health_projection_uses_fixed_allowlist_and_strict_output` |
| recursive leak scan | `_assert_no_private_material` |

## Validation Status

Focused ASTRA-API-001 tests passed locally with `.venv/bin/python -m pytest`.

Broader ASTRA-IMP and ASTRA-VAL regressions remain required before commit and
push.

## Source Review Corrections

After Astra source review of commit `f7594b48`, two corrections were applied.

The diagnostics Runtime remains lazy-started, but application shutdown now calls
`runtime_service.shutdown()` when the internal diagnostics router is registered.
Tests verify enabled non-production app shutdown, captured interface
invalidation, issued projection request invalidation, disabled/production
non-startup, repeated app lifecycle isolation, and idempotent shutdown.

The diagnostics service now wraps full operations with a deterministic error
boundary. The boundary covers Runtime access, Runtime health generation,
component health generation, projection request issuance, projection creation,
and unexpected failures. Runtime failures map to `runtime_unavailable`,
projection request failures map to `projection_request_invalid`, projection
creation failures map to `projection_unavailable`, and unexpected failures map
to `internal_diagnostic_failure`.
