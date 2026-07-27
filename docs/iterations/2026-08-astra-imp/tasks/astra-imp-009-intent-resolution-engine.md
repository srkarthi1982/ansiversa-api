# ASTRA-IMP-009 Intent Resolution Engine

| Field | State |
|---|---|
| ASTRA-IMP-009 | Implemented |
| Scope | Intent Resolution Engine |
| Implementation direction | Approved |
| Astra re-review | Pending after exact-binding correction |
| Constitutional conformance | Pending |
| Product Owner approval | Pending |
| Certification | Pending |
| Production authorization | Not approved |
| Production | Unchanged |
| ASTRA-IMP-010 | Not authorized |

Reused certified Runtime lifecycle, Conversation current-turn snapshots, Capability Discovery authority/metadata, Governance Kernel, Evidence Sink, and Planning structural availability. No certified parent behavior was weakened and no frozen constitutional/readiness document changed.

Deliverables include immutable contracts, fixed taxonomy/matching table, governance mapping, evidence atomicity, runtime integration, truthful health, tests, architecture/ADR/review/mapping, iteration, and AGENTS records.

Source review of `ff02ed46` approved implementation direction and required one correction. Declared meaning is now bound to the exact current turn through an opaque same-engine-issued binding; forged, foreign, stale, reused, and mismatched bindings fail before downstream processing.

Re-review of `d536a263` required exact-issued tamper resistance. A bounded private registry now validates binding ID plus issued-object identity, so copied/reconstructed bindings cannot reuse a valid token.
