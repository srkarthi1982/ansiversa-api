# ASTRA-APP-001 Requirement Traceability

Status: Certified / Approved for implementation commit `c0bde31ddd8032ff21a0996787e6012068e7d3f9`.

Product Owner approval is recorded. Certification passed. Production authorization is not approved and production remains unchanged.

| Requirement | Implementation |
| --- | --- |
| One app only | Scope limited to `app.modules.subscription_manager`. |
| Read-only mode | Adapter exposes only list/aggregate reads and mutation-surface scan. |
| App-owned business logic | Capability code lives inside Subscription Manager and reuses app repository/service semantics. |
| Authenticated user ownership | Records are loaded with `repository.list_subscriptions(db, authenticated_user.id)` and rechecked against `owner_id`. |
| Metadata is not execution authority | `SubscriptionAstraAuthorizationReference` is supporting metadata only and cannot be passed to `execute_read_capability`. |
| App-owned read grant required | `SubscriptionAstraReadGrant` must be issued by the Subscription Manager grant issuer and validated by exact object identity. |
| Grant user binding | Grant principal and authenticated user ID must match before repository access. |
| Grant tamper/reuse denial | Caller-created, copied, reconstructed, tampered, foreign, expired, and reused grants fail closed. |
| Execution-clock authority | Production execution uses the app-owned UTC clock with no deterministic clock factory, trusted test-clock registry, or caller-selectable timestamp; deterministic tests patch the private app clock inside the isolated test process, and ordinary timestamp overrides fail closed. |
| Fixed named capabilities | Ten fixed `subscription.*` capability IDs are versioned at `1.0.0`. |
| No arbitrary SQL | Request contract has no SQL/table/column/predicate fields and forbids extra fields. |
| Bounded parameters | Only `days`, `status`, and `category` parameter names are structurally valid; each capability allowlists the subset it accepts. |
| Duplicate parameter denial | Request validator rejects duplicate parameter names. |
| Excessive limit denial | Request validator caps requested results at 50 and each capability also records its maximum. |
| Stale authorization denial | Authorization references older than 15 minutes are rejected. |
| Foreign app denial | Authorization app scope must be `app:subscription_manager`. |
| Production not approved | Request/result contracts require `production_authorization_state = not_approved`. |
| Highest-cost currency boundary | Highest-cost results are grouped by currency with `within_currency_only_no_fx`; no cross-currency numeric winner is selected. |
| Raw recurring totals | `subscription.total_recurring_cost` preserves currency plus billing-frequency buckets. |
| Monthly estimate | `subscription.monthly_cost_estimate` uses existing app frequency semantics and decimal rounding by currency. |
| Renewal date determinism | Uses injected `observed_at` and deterministic date-window helpers. |
| Deterministic answer contract | `deterministic_answer()` returns structured dictionaries only, not LLM prose. |
| No frontend/API/schema/provider changes | No frontend files, routers, migrations, settings, or provider/model modules changed. |
| Local validation | `validation.astra_app_001.cli` provides list, single scenario, and all-scenario commands. |
| Runtime execution boundary | Documentation records certified Runtime read execution as unavailable until a separate read executor phase. |
| Evidence boundary | Documentation records app-read evidence integration as unavailable; no fabricated evidence is emitted. |

## Unauthorized Follow-On Work

```text
ASTRA-APP-VAL-001           Not authorized
ASTRA-READ-EXEC-001         Not authorized
ASTRA-CHAT-001              Not authorized
Frontend / Chat             Not authorized
Provider / Model            Not authorized
Production Authorization    Not approved
Production                  Unchanged
```
