# Astra Minimal Configuration Foundation

**Status:** Implemented
**Task:** ASTRA-IMP-002
**Parent Constitution:** ASTRA-001 through ASTRA-010 Accepted / Frozen
**Parent Readiness:** ASTRA-IR-001 Accepted / Frozen
**Parent Implementation:** ASTRA-IMP-001 Certified / Approved
**Implementation Scope:** Minimal Configuration Foundation
**Implementation Direction:** Pending Astra Source Review
**Constitutional Conformance:** Pending
**Product Owner Approval:** Pending
**Certification:** Pending
**Production Authorization:** Not approved
**Production:** Unchanged

---

# Purpose

ASTRA-IMP-002 implements the Stage 1 Minimal Configuration Foundation from
ASTRA-IR-001.

It provides a static, validated, disabled-by-default internal configuration
surface future Astra components can consume after separate authorization.

It does not enable runtime Astra behavior, provider usage, memory, adaptation,
planning, execution handoff, APIs, routes, databases, migrations, frontend
changes, deployment changes, production configuration, or production behavior.

---

# Discovery Findings

Codex inspected the existing configuration and Astra foundations before
implementation:

- `app/core/config.py` is the authoritative application settings system and
  uses `pydantic-settings`.
- `app/core/config.py` already exposes `APP_ENV`, `VERCEL_ENV`, provider
  settings, and `ASTRA_PERSONAL_DATA_TOOLS_ENABLED`.
- Existing Astra package settings live at `app/modules/astra_ai/settings.py`
  and keep the isolated Astra platform disabled by default.
- ASTRA-IMP-001 certified `AstraConfigurationContract` defines the governance
  contract used by this configuration foundation.
- Existing Assistant, Knowledge, Tool Framework, Tool Registry, auth, audit,
  and app-owned services remain authoritative for their own surfaces.

One blocking compatibility issue was found: the certified
`ImplementationPhase` enum only included `astra_imp_001`. ASTRA-IMP-002
requires validated configuration to identify the Stage 1 implementation phase.
Codex applied the minimal contract extension by adding `astra_imp_002` without
changing the existing ASTRA-IMP-001 default or validation behavior.

No frozen constitutional document or ASTRA-IR-001 document was changed.

---

# Placement And Ownership

The implementation lives at:

```text
app/modules/astra_ai/configuration.py
```

Ownership:

- `app/core/config.py` remains the authoritative repository settings loader.
- `app/modules/astra_ai/configuration.py` owns only the validated Astra
  internal configuration projection.
- `AstraConfigurationContract` from ASTRA-IMP-001 remains the typed
  configuration contract.
- The loader consumes only environment identity fields needed for scope
  selection: `APP_ENV` and `VERCEL_ENV`.
- The loader does not read or expose provider keys, model settings, raw
  secrets, or unrelated environment values.

---

# Configuration Defaults

Every environment loads with:

```text
feature_enabled                 false
implementation_phase            astra_imp_002
production_authorization_state  not_approved
provider_use                    disabled
memory_use                      disabled
adaptation_use                  disabled
execution_handoff               disabled
audit_evidence_behavior         metadata_only
fail_closed_default             true
configuration_version           1.0.0
```

Supported environment scopes:

```text
local
development
qa
staging
production
```

Environment selection does not create authority. Production scope still records
production authorization as `not_approved`.

---

# Provenance

Loaded configuration includes bounded provenance:

- configuration identifier;
- configuration version;
- environment scope;
- source class;
- timezone-aware load timestamp;
- validation result.

The provenance record contains no raw secret values and no unrelated
environment dump.

---

# Safe Access

`get_astra_configuration()` returns a copy-safe validated
`LoadedAstraConfiguration`.

Callers cannot mutate the authoritative cached configuration to expand
authority. No API, route, runtime hook, startup registration, or production
configuration is created.

---

# Validation Boundaries

The loader rejects:

- unknown fields;
- invalid enum values;
- feature activation;
- provider, memory, adaptation, or execution enablement;
- inferred or explicit production authorization;
- non-fail-closed configuration;
- malformed identifiers;
- malformed versions;
- naive load timestamps.

---

# Final Implementation State

```text
ASTRA-IMP-002               Implemented
Implementation Scope        Minimal Configuration Foundation
Implementation Direction    Pending Astra Source Review
Constitutional Conformance  Pending
Product Owner Approval      Pending
Certification               Pending

Production Authorization    Not approved
Production                  Unchanged

ASTRA-IMP-003               Not authorized
```
