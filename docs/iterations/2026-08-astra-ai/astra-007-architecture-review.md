# ASTRA-007 Architecture Review Package

**Status:** Proposed
**Created:** 2026-07-25
**ADR:** Proposed
**Product Owner Authorization:** Approved for documentation and architecture only
**Architecture Direction:** Approved
**Architecture Review:** Minor revisions applied; pending Astra re-review
**Product Owner Approval:** Pending
**Implementation:** Not authorized
**Production:** Unchanged

---

# Review Subject

ASTRA-007 proposes the External Intelligence and Provider Architecture for
Astra AI:

```text
docs/astra-ai-external-intelligence-provider-architecture.md
docs/architecture/decisions/astra-ai-external-intelligence-provider-architecture.md
```

---

# Proposed Decision

Adopt a governed External Intelligence and Provider Architecture that inherits
ASTRA-001 through ASTRA-006 and defines when Astra may use external
intelligence, how provider input envelopes are minimized, how providers are
selected, how responses are validated, how cost and privacy are governed, and
how Astra remains provider-independent.

This revision applies Astra's required refinements after source-level review of
commit `ad3340e`:

- provider eligibility is separated from provider selection, with eligibility
  treated as the governed provider set for the request; and
- provider responses are classified as advisory intelligence until validated by
  Astra and authoritative owners.

---

# Review Questions

1. Does ASTRA-007 inherit ASTRA-001 through ASTRA-006 without reopening them?
2. Is external intelligence clearly a capability rather than the default path?
3. Does local sufficiency precede provider selection?
4. Are deterministic tasks excluded from provider use?
5. Are provider capabilities classified conservatively?
6. Are provider eligibility and routing rules provider-independent?
7. Are provider input envelopes minimized and purpose-bound?
8. Does prompt governance avoid overriding parent architecture?
9. Are provider responses treated as untrusted until validated?
10. Are hallucination boundaries explicit?
11. Are cost and token budgets governed?
12. Are privacy and data minimization requirements explicit?
13. Are provider failures represented without breaking local behavior?
14. Is bounded provider evidence defined?
15. Does multi-provider support avoid constitutional vendor dependency?
16. Is the documentation-only boundary complete?
17. Is provider eligibility clearly evaluated before provider selection?
18. Does provider selection occur only within the eligible provider set?
19. Are provider responses explicitly advisory until validated?
20. Is unvalidated provider output prohibited from mutating state, granting
    authorization, overriding ownership, or establishing platform truth?

---

# Current Codex Self-Review

```text
ASTRA-007               Proposed
Parent                  ASTRA-001 Accepted
Parent                  ASTRA-002 Accepted
Parent                  ASTRA-003 Accepted
Parent                  ASTRA-004 Accepted
Parent                  ASTRA-005 Accepted
Parent                  ASTRA-006 Accepted
Documentation Auth      Approved
Architecture Auth       Approved
Architecture Direction  Approved
Discovery               Complete
Specification           Complete
Architecture Review     Pending Astra Re-review
Product Owner Approval  Pending
ADR                     Proposed
Implementation          Not authorized
Production              Unchanged
```

Codex confirms ASTRA-007 makes no implementation changes and does not reopen
ASTRA-001 through ASTRA-006 or the frozen Astra AI Platform Phase 1 code.

---

# Review Boundary

This package is for architecture review only. It does not approve runtime
provider integration, OpenAI integration, provider SDKs, prompt implementation,
model invocation, APIs, routes, Tool Executor changes, app integration,
database access, migrations, frontend changes, tests, generated artifacts,
deployment, or production behavior.

---

# Astra Review Outcome

Astra reviewed commit `ad3340e` and approved the architecture direction with
two targeted documentation refinements required before ASTRA-007 can be frozen:

- separate provider eligibility from provider selection; and
- define provider response authority, making provider output advisory until
  validated by Astra and authoritative owners.

Those refinements are now applied. ASTRA-007 remains Proposed and is ready for
Astra re-review.

Implementation remains unauthorized. Production remains unchanged.
