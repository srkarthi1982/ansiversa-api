# ASTRA-API-001 Requirement Mapping

| Requirement | Implementation |
| --- | --- |
| Backend-only diagnostics API | `app/modules/astra_ai/api/diagnostics.py` |
| Disabled by default | `ASTRA_DIAGNOSTICS_API_ENABLED=False` |
| Non-production only | `diagnostics_environment()` and endpoint validation |
| Existing authentication reused | `require_admin_user` dependency |
| Developer authorization required | existing admin role requirement |
| No caller authority | request DTOs forbid extra fields and authority values |
| Runtime-owned projection issuance | `AstraDiagnosticsService` calls Runtime public diagnostic interface |
| Strict default redaction | request DTO default and service enforcement |
| Metadata-only denied | `metadata_only_not_authorized` |
| Runtime summary projection | `/projections/runtime` |
| Evidence references bounded | max 50, duplicate rejection |
| No global evidence enumeration | no list/search endpoint |
| Request diagnostic unavailable | `/projections/request` bounded unavailable response |
| Component health fixed allowlist | `/projections/components` schema literals |
| Stable envelope | `AstraDiagnosticsEnvelope` |
| Bounded errors | `AstraDiagnosticsErrorCode` |
| Hidden OpenAPI | router `include_in_schema=False` |
| No CORS change | `app/main.py` middleware unchanged |
| No database, SQL, provider, execution | no imports or code paths added |
| Production route absence | `should_register_diagnostics_routes()` |
| Focused tests | `tests/test_astra_diagnostics_api.py` |

