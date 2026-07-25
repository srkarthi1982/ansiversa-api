# ASTRA-006 Architecture Review Package

**Status:** Approved
**Created:** 2026-07-25
**ADR:** Accepted
**Product Owner Authorization:** Approved for documentation and architecture only
**Architecture Direction:** Approved
**Astra Re-review:** Approved
**Product Owner Approval:** Approved
**Implementation:** Not authorized
**Production:** Unchanged

---

# Review Subject

ASTRA-006 proposes the Tool Execution Architecture for Astra AI:

```text
docs/astra-ai-tool-execution-architecture.md
docs/architecture/decisions/astra-ai-tool-execution-architecture.md
```

---

# Accepted Decision

Adopt a governed Tool Execution Architecture that inherits ASTRA-001 through
ASTRA-005 and defines how approved ASTRA-005 execution plans are handed to a
future executor, validated, accepted or rejected, monitored, reconciled, and
reported while preserving the permanent boundary that Astra plans, the executor
executes, and the owning service remains authoritative.

This revision applies Astra's required refinements after source-level review of
commit `4cb6bef3`:

- executor admission is separated from owning-service acceptance, and executor
  admission is explicitly not execution authorization;
- execution remains prohibited until owning-service acceptance succeeds; and
- multi-owner execution is not treated as atomic, with each step requiring
  independent owner authority, validation, reconciliation, reporting, and
  partial-success or residual-effect disclosure.

---

# Review Questions

1. Does ASTRA-006 inherit ASTRA-001 through ASTRA-005 without reopening them?
2. Is the executor clearly separated from Astra and the planner?
3. Is an execution request clearly not execution authority by itself?
4. Are executor acceptance and rejection represented as governed results?
5. Does live authorization recheck remain mandatory before execution?
6. Does owning-service validation remain authoritative?
7. Are plan version, digest, approval binding, and confirmation binding checked
   before execution?
8. Are stable step identity and idempotency required for state-changing steps?
9. Are duplicate requests detected before execution?
10. Does timeout produce uncertain outcome rather than non-execution?
11. Are retries blocked until uncertain outcomes are reconciled?
12. Is cancellation governed without being confused with rollback?
13. Are long-running progress states represented?
14. Are partial success and compensation reporting explicit?
15. Are stale plans rejected?
16. Are executor health and owner-service availability separated?
17. Is execution evidence bounded and safe?
18. Does unknown execution state fail closed?
19. Is the documentation-only boundary complete?
20. Is executor admission clearly separated from owning-service acceptance?
21. Does the architecture state that only owning-service acceptance may
    authorize execution inside the owner boundary?
22. Are multi-owner requests explicitly non-atomic unless an owning architecture
    proves otherwise?
23. Does cross-owner execution require per-step authority and prohibit global
    success from partial owner success?

---

# Current Codex Self-Review

```text
ASTRA-006               Approved
Parent                  ASTRA-001 Accepted
Parent                  ASTRA-002 Accepted
Parent                  ASTRA-003 Accepted
Parent                  ASTRA-004 Accepted
Parent                  ASTRA-005 Accepted
Documentation Auth      Approved
Architecture Auth       Approved
Architecture Direction  Approved
Discovery               Complete
Specification           Complete
Astra Re-review         Approved
Product Owner Approval  Approved
ADR                     Accepted
Implementation          Not authorized
Production              Unchanged
ASTRA-007               Documentation only next; requires separate authorization
```

Codex confirms ASTRA-006 makes no implementation changes and does not reopen
ASTRA-001, ASTRA-002, ASTRA-003, ASTRA-004, ASTRA-005, or the frozen Astra AI
Platform Phase 1 code.

---

# Review Boundary

This package is for architecture review only. It does not approve runtime
integration, Tool Executor code changes, tool execution, app integration,
external provider integration, prompts, APIs, routes, database access,
migrations, frontend changes, tests, deployment, generated artifacts, or
production behavior.

---

# Astra Review Outcome

Astra reviewed commit `4cb6bef3` and approved the architecture direction with
two targeted documentation refinements required before ASTRA-006 can be frozen:

- separate executor admission from explicit owning-service acceptance; and
- define per-step authority and non-atomic behavior for multi-owner execution.

Astra re-reviewed commit `0d01e3f8` and approved ASTRA-006. Product Owner
approval is recorded, the ADR is accepted, and ASTRA-006 is Frozen.

ASTRA-007 External Intelligence And Provider Architecture is documentation-only
next and requires separate Product Owner authorization before work begins.

Implementation remains unauthorized. Production remains unchanged.
