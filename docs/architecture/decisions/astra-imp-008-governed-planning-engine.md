# ADR: ASTRA-IMP-008 Governed Planning Engine

Status: proposed for Astra source review. Date: 2026-07-27.

## Decision

Place one stateless-except-for-success-sequence `AstraPlanningEngine` under `app/modules/astra_ai`, owned and lifecycle-gated by `AstraRuntime`. Require a current certified runtime-owned conversation. Consume metadata only through governed Capability Discovery using runtime-issued authority. Validate the caller-supplied ordered shape, evaluate governance, append bounded evidence, and release an immutable advisory plan.

Non-ALLOW outcomes return no steps. Visibility, governance allow, approval metadata, and owner-acceptance metadata never become execution authority. All plans remain execution-not-authorized and production-not-approved.

## Consequences

This preserves planning/approval, execution separation, provider independence, and fail-closed precedence while reusing certified foundations. Planning without a current conversation is unsupported. No execution, provider, persistence, API, deployment, production activation, memory, or adaptation surface is added. ASTRA-IMP-009 remains unauthorized.
