# ADR — ASTRA-IMP-010 Read-Only Data Access Authorization

Status: Certified / Approved.

Implementation direction, Astra re-review of `1ec3bf8b`, constitutional conformance, Product Owner approval, and certification are approved/passed.

Decision: add a metadata-only authorization engine before any future app-owned adapter. Named capabilities replace arbitrary query construction. Exact owner-issued proofs replace identifier trust. Owner acceptance and production authorization remain independent.

Runtime remains degraded for this component because authoritative issuers and app-owned capabilities do not exist. This is intentional fail-closed behavior. No database or query surface is added.
