# ASTRA-004 Architecture Review Package

**Status:** Approved
**Created:** 2026-07-24
**ADR:** Accepted
**Product Owner Authorization:** Approved for documentation and architecture only
**Architecture Direction:** Approved
**Astra Re-review:** Approved
**Product Owner Approval:** Approved
**Implementation:** Not authorized
**Production:** Unchanged

---

# Review Subject

ASTRA-004 proposes the Capability Discovery and Tool Architecture for Astra AI:

```text
docs/astra-ai-capability-tool-architecture.md
docs/architecture/decisions/astra-ai-capability-tool-architecture.md
```

---

# Accepted Decision

Adopt a governed capability discovery and tool architecture that inherits
ASTRA-001, ASTRA-002, and ASTRA-003 and defines how Astra discovers registered
capabilities, classifies tools, evaluates ownership and side-effect metadata,
selects or rejects tool candidates, prevents capability fabrication, records
bounded discovery evidence, and preserves the separation between discovery and
execution authority. The current revision also separates registry permission
metadata from live authorization and defines deterministic candidate precedence
with clarification or ambiguous-capability fallback.

---

# Review Questions

1. Does ASTRA-004 inherit ASTRA-001, ASTRA-002, and ASTRA-003 without reopening
   them?
2. Is a capability clearly separated from a tool?
3. Is the Tool Registry authoritative for discovery metadata without becoming
   an execution engine?
4. Does capability discovery always precede tool selection?
5. Does tool selection remain separate from execution planning?
6. Are fabricated capabilities impossible under the architecture?
7. Are unavailable, deprecated, experimental, permission-required, and
   owner-mismatch states represented?
8. Are read-only, proposal, write/action, external-provider, and admin tools
   classified conservatively?
9. Are ownership boundaries preserved for app services, Knowledge, auth,
   authorization, AI SEO, providers, and the registry?
10. Is discovery deterministic, explainable, provider-independent, and
    reviewable?
11. Does failure behavior fail closed when capability authority cannot be
    established?
12. Is the documentation-only boundary complete?
13. Does ASTRA-004 separate permission requirements metadata from live
    authorization truth?
14. Does ASTRA-004 define deterministic tie resolution without relying on
    registry iteration order, provider suggestions, or accidental ordering?

---

# Current Codex Self-Review

```text
ASTRA-004               Approved
Parent                  ASTRA-001 Accepted
Parent                  ASTRA-002 Accepted
Parent                  ASTRA-003 Accepted
Documentation Auth      Approved
Architecture Auth       Approved
Discovery               Complete
Specification           Complete
Architecture Direction  Approved
Astra Re-review         Approved
Product Owner Approval  Approved
ADR                     Accepted
ASTRA-004 Freeze        Approved
Implementation          Not authorized
Production              Unchanged
ASTRA-005               Documentation only next; requires separate authorization
```

Codex confirms ASTRA-004 makes no implementation changes and does not reopen
ASTRA-001, ASTRA-002, ASTRA-003, or the frozen Astra AI Platform Phase 1 code.

---

# Review Boundary

This package is for architecture review only. It does not approve runtime
capability lookup, registry schemas, tool execution, app integration, external
provider integration, prompts, APIs, migrations, frontend changes, deployment,
or production behavior.

---

# Astra Review Outcome

Astra reviewed commit `862816d` and approved the architecture direction with
two targeted documentation refinements required before ASTRA-004 can be frozen.
This package now records those refinements:

- Permission metadata is separated from live authorization. The Tool Registry
  may declare required permissions, scopes, roles, entitlements, confirmations,
  and approval classes, but it never declares the current user authorized. Live
  authorization remains owned by the authorization provider or owning service
  and must be rechecked by any future executor.
- Deterministic candidate precedence is defined. Equal candidates resolve by
  governed registry precedence such as exact intent match, lower side-effect
  class, narrower context need, fewer dependencies, stable approved priority,
  and stable capability/tool identifier. If no approved precedence resolves a
  user-significant difference, Astra asks for clarification or returns an
  ambiguous-capability result.

Astra re-reviewed commit `5e60cc4` and approved ASTRA-004. Product Owner
approval is recorded, the ADR is accepted, and ASTRA-004 is Frozen.

Implementation remains unauthorized. Production remains unchanged. ASTRA-005 is
the next documentation-only phase and requires separate authorization.
