# ASTRA-APP-001 Iteration Overview

## Title

Subscription Manager Governed Read Capability

## Status

Implementation Direction: Approved

Security Review: Pending final re-review

Data Ownership Review: Corrections applied

Constitutional Conformance: Pending final re-review

Product Owner Approval: Pending

Certification: Pending

## Scope

ASTRA-APP-001 creates the first app-owned, read-only Application Intelligence Layer capability pattern for Subscription Manager.

The implementation is backend-only and local/test-only. It does not create a public API route, frontend chat surface, provider/model call, database migration, execution framework, deployment, or production activation.

Authoritative app identity:

```text
Subscription Manager
App #071
slug: subscription-manager
module: subscription_manager
```

## Discovery Findings

- Subscription Manager data lives in the isolated `subscription_manager` backend module and database configured by `SUBSCRIPTION_MANAGER_DATABASE_URL`.
- Authenticated ownership is represented by `SubscriptionRecord.owner_id`, mapped to database column `userId`.
- Existing app reads use `repository.list_subscriptions(db, owner_id)` with owner filtering.
- Active subscriptions are currently statuses `active` and `trial`.
- There is no archived flag in the current Subscription Manager schema. Deleted records are physically removed by existing service behavior.
- Renewal date semantics use the string field `next_billing_date`; the adapter parses the ISO date prefix deterministically.
- Currency totals are grouped by `currency_code`; no FX conversion is performed.
- Existing monthly normalization is reused from app semantics: weekly `amount * 52 / 12`, monthly `amount`, quarterly `amount / 3`, semiannual `amount / 6`, annual `amount / 12`, custom `amount`.
- App #071 is authoritative for ASTRA-APP-001 documentation. No catalog or production identity metadata change was required.
- Certified Astra read authorization metadata is supporting metadata only. Actual app-owned read execution requires an exact-object Subscription Manager read grant issued by the app-owned grant issuer.

## Runtime Reachability

The certified Astra Runtime currently exposes capability discovery, intent resolution, planning, and read authorization metadata. It does not expose a certified read executor. The default Runtime read registry is empty, and direct app read execution through Runtime is unavailable by certified design.

ASTRA-APP-001 therefore certifies the app-owned adapter independently and records full Runtime execution as pending a separately authorized read executor phase.
