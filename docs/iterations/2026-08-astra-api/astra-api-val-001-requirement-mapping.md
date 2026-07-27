# ASTRA-API-VAL-001 Requirement Mapping

Status: Implemented / Pending Astra Review.

| Requirement | Validation |
| --- | --- |
| Diagnostics disabled by default | `flag_disabled_routes_absent`, `activation_does_not_enable_operational_astra` |
| Non-production route registration only | `allowed_non_production_routes_registered_hidden`, `production_routes_absent`, `unknown_environment_fails_closed` |
| Production unchanged | `production_routes_absent`, `security_forbidden_surfaces_absent` |
| Anonymous rejected | `anonymous_rejected` |
| Invalid bearer token rejected | `invalid_token_rejected` |
| Authenticated non-admin rejected | `authenticated_member_rejected` |
| Admin accepted only in non-production | `admin_accepted_non_production` |
| Caller body cannot self-authorize | `caller_supplied_identity_cannot_authorize` |
| Health response bounded | `health_endpoint_bounded` |
| Runtime projection strict/redacted | `strict_runtime_projection`, `runtime_projection_input_validation` |
| Evidence projection explicit references only | `evidence_projection_validation` |
| Request diagnostics bounded unavailable | `request_diagnostic_bounded_unavailable` |
| Component diagnostics fixed allowlist | `component_health_validation` |
| Runtime diagnostics dedicated endpoint only | `component_health_validation`, `strict_runtime_projection` |
| Diagnostics validation errors sanitized | `runtime_projection_input_validation`, `evidence_projection_validation`, `component_health_validation` |
| Diagnostics route scope exact | `diagnostics_validation_route_scope` |
| Response contracts stable | `response_contract_integrity` |
| Privacy leak detection | `privacy_inspector_controls`, `health_endpoint_bounded`, projection scenarios |
| Error taxonomy bounded | `error_taxonomy_declared_reachability` |
| Runtime/projection/API/unexpected failures mapped | `runtime_failure_boundary`, `projection_request_failure_boundary`, `existing_api_error_boundary`, `unexpected_failure_boundary`, `component_failure_boundary` |
| Unauthorized requests do not start Runtime | `unauthorized_requests_do_not_start_runtime` |
| Runtime lifecycle cleanup | `runtime_lifecycle` |
| Deterministic semantic HTTP | `deterministic_semantic_http`, `test_semantic_http_preserves_meaningful_evidence_reference_structure` |
| CLI text/JSON/runner equivalence | `test_runner_and_cli_outputs_are_semantically_equivalent` |
| CORS unchanged semantically | `cors_configuration_unchanged` |
| Forbidden surfaces absent | `security_forbidden_surfaces_absent` |

The runner intentionally treats variable transport fields such as request IDs,
projection IDs, timestamps, runtime instance IDs, and redacted evidence
references as nondeterministic transport metadata for semantic comparison.
