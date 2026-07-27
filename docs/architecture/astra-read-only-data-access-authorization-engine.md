# ASTRA-IMP-010 — Read-Only Data Access Authorization Engine

ASTRA-IMP-010 adds a Runtime-owned deterministic metadata authorization boundary for future app-owned reads. It does not connect to a database, generate or execute SQL, retrieve records, or authorize production reads. The strongest result, `authorized_metadata_only`, means only that a bounded named read request is eligible for submission to a future authoritative app-owned adapter.

Named capabilities declare the owner, fixed purposes, sensitivity, subject/tenant/record scopes, allowed and required fields, filters, aggregations, row/time limits, cross-app policy, governance references, and unapproved production state. Requests carry bounded references and exact owner-issued proof objects, never records, credentials, query language, unrestricted expressions, or executable references. The sealed registry is deterministic, bounded, immutable, and duplicate-rejecting. Its default is empty because no app read capability is certified.

Identifiers are never authority. The bounded proof issuer validates the exact immutable object it issued, same Runtime and issuer, known proof ID, and current expiration. Copies, reconstructions, foreign, altered, unknown, and expired proofs fail. Required issuers are currently unavailable, so default health is truthfully degraded and authorization fails closed.

Purpose must be allowed. Fields must be explicit allowed subsets and retain required fields; wildcards fail. Row/time limits and aggregations stay within bounds. Cross-app access is prohibited by default. Owner acceptance requires an exact owner-issued proof. Governance ALLOW never bypasses scope, minimization, acceptance, or production authorization.

The order is validation, proof validation, metadata resolution, governance, scope/minimization, immutable decision preparation, evidence append, then release. Append failure releases no decision or sequence advancement. Runtime owns exactly one lifecycle-bound component and health contains structural metadata only.

```text
database_connection_state  not_authorized
sql_execution_state        not_authorized
data_retrieval_state       not_performed
data_mutation_state        prohibited
schema_mutation_state      prohibited
production_read_state      not_approved
```

Adapters, persistence, production access, providers, prompts, models, memory, learning, execution, APIs, routes, frontend, and deployment remain outside scope.
