# ASTRA-APP-001 Requirement Traceability

| Requirement | Implementation |
| --- | --- |
| One app only | Scope limited to `app.modules.subscription_manager`. |
| Read-only mode | Adapter exposes only list/aggregate reads and mutation-surface scan. |
| App-owned business logic | Capability code lives inside Subscription Manager and reuses app repository/service semantics. |
| Authenticated user ownership | Records are loaded with `repository.list_subscriptions(db, authenticated_user.id)` and rechecked against `owner_id`. |
| Fixed named capabilities | Ten fixed `subscription.*` capability IDs are versioned at `1.0.0`. |
| No arbitrary SQL | Request contract has no SQL/table/column/predicate fields and forbids extra fields. |
| Bounded parameters | Only `days`, `status`, and `category` parameter names are structurally valid; each capability allowlists the subset it accepts. |
| Duplicate parameter denial | Request validator rejects duplicate parameter names. |
| Excessive limit denial | Request validator caps requested results at 50 and each capability also records its maximum. |
| Stale authorization denial | Authorization references older than 15 minutes are rejected. |
| Foreign app denial | Authorization app scope must be `app:subscription_manager`. |
| Production not approved | Request/result contracts require `production_authorization_state = not_approved`. |
| Currency grouping | Totals are grouped by currency with no FX conversion. |
| Monthly estimate | Uses existing app frequency semantics and decimal rounding. |
| Renewal date determinism | Uses injected `observed_at` and deterministic date-window helpers. |
| Deterministic answer contract | `deterministic_answer()` returns structured dictionaries only, not LLM prose. |
| No frontend/API/schema/provider changes | No frontend files, routers, migrations, settings, or provider/model modules changed. |
| Local validation | `validation.astra_app_001.cli` provides list, single scenario, and all-scenario commands. |
| Runtime execution boundary | Documentation records certified Runtime read execution as unavailable until a separate read executor phase. |
| Evidence boundary | Documentation records app-read evidence integration as unavailable; no fabricated evidence is emitted. |
