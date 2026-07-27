# Ansiversa Three-Level Code Review Rule

**Status:** Permanent Engineering Governance Rule  
**Adopted:** 2026-07-24  
**Scope:** All Ansiversa repositories  
**Required:** Before final approval and before production impact

---

## Purpose

Ansiversa must not rely on a single review layer for implementation acceptance.

Every meaningful code change must pass three distinct review levels before it
may be approved, frozen, promoted, deployed, or allowed to affect production.

This rule is intended to prevent:

- hidden implementation defects;
- architecture drift;
- governance violations;
- incomplete validation;
- security or privacy leaks;
- accidental runtime activation; and
- unexpected production behavior.

---

## Ownership

| Stage | Owner | Responsibility |
| --- | --- | --- |
| Development | Codex | Implement the approved scope |
| Technical Self-Review | Codex | Verify implementation, tests, validation, and repository boundaries |
| Product Review | Karthikeyan | Verify business intent, workflow, usability, and acceptance |
| Final Technical Review | Astra | Independently review the committed source against architecture and governance |
| Production Authorization | Karthikeyan | Decide whether the approved implementation may proceed toward production |

Approval responsibility belongs to the named owner at each stage. Passing one
stage does not transfer, replace, or imply approval at another stage.

---

## Approval Cannot Be Delegated

> **Approval cannot be delegated.**
>
> A commit is not considered finally approved until Astra completes the
> independent source-level review. Automated tests, Codex self-review, or
> Product Owner acceptance do not replace this final technical review.

Each reviewer provides a distinct and necessary perspective:

- **Codex:** “Did I implement this correctly?”
- **Karthikeyan:** “Is this what we wanted to build?”
- **Astra:** “Does this implementation truly satisfy the architecture and
  governance we have already approved?”

These questions are not interchangeable. All three must be answered before
final approval.

---

## Level 1 — Codex Implementation Review

After development is complete, Codex must review its own implementation before
committing and pushing.

Codex must verify:

- the requested scope was implemented;
- prohibited scope was not introduced;
- applicable `AGENTS.md` and governance rules were followed;
- code quality and repository conventions were respected;
- focused and regression tests pass;
- compile, lint, type, build, validation, and drift checks appropriate to the
  change pass;
- generated artifacts are intentional;
- production-impact boundaries are respected; and
- the final diff contains only intended files.

Codex must provide a clear implementation report containing:

- files changed;
- behavior implemented;
- tests and validation commands;
- known limitations;
- commit hash;
- push result; and
- production-impact confirmation.

Codex review does not constitute final approval.

---

## Level 2 — Product Owner Review

Karthikeyan, as Product Owner, must review the completed work from the product
and operational perspective.

The Product Owner review should verify:

- the delivered behavior matches the intended requirement;
- the scope is complete;
- user-facing behavior is acceptable;
- workflows and business rules are correct;
- no unintended product change was introduced;
- screenshots, manual checks, or functional evidence are satisfactory where
  applicable; and
- the implementation is ready for final technical review.

Product Owner acceptance does not replace source-level technical review.

---

## Level 3 — Astra Final Code Review

Astra is the mandatory final code reviewer.

Astra must review the actual committed source code, diff, tests, and relevant
repository evidence before final approval.

Whenever repository access is available, Astra must inspect the GitHub commit or
exact changed files directly rather than relying only on summaries.

Astra must verify:

- implementation matches the approved architecture;
- contracts and governance rules are respected;
- no hidden scope expansion exists;
- failure behavior is safe;
- validation is fail-closed where required;
- deterministic behavior is genuinely deterministic;
- security, privacy, and secret-handling boundaries are respected;
- rollback and recovery claims are evidence-based;
- internal data cannot leak into public output;
- tests cover important success and failure paths;
- production behavior is unchanged unless explicitly authorized; and
- no false-ready, false-pass, or unsafe promotion path exists.

Astra may:

- approve the implementation;
- approve with non-blocking recommendations;
- request narrowly scoped corrections; or
- block approval when source-level evidence is insufficient.

Final approval must not be recorded until Astra's review passes.

---

## Mandatory Approval Sequence

```text
Development
    ↓
Codex self-review
    ↓
Commit and push
    ↓
Product Owner review
    ↓
Astra source-level review
    ↓
Corrections, if required
    ↓
Astra re-review
    ↓
Final approval
    ↓
Freeze / promotion / deployment / production authorization
```

---

## No-Bypass Rule

The three-level review process must not be bypassed because:

- tests passed;
- the change appears small;
- Codex reports success;
- the implementation is documentation-backed;
- the deadline is urgent;
- the change is already committed;
- the implementation is disabled by default; or
- production has not yet changed.

For trivial documentation-only corrections, Astra may perform a proportionate
review, but final-review accountability still remains.

---

## Production Protection Rule

No implementation may affect production until:

```text
Codex Review             Passed
Product Owner Review     Passed
Astra Final Review       Passed
Production Authorization Explicit
```

A successful commit or push is not production approval.

A successful automated test run is not production approval.

A successful Product Owner check is not final technical approval.

Astra's source-level approval is mandatory before the change can be frozen or
promoted.

---

## Correction Workflow

When Astra identifies issues:

1. The implementation remains unapproved.
2. The phase or task remains unfrozen.
3. Codex receives a narrowly scoped correction task.
4. Codex implements, validates, commits, and pushes the correction.
5. Astra performs source-level re-review.
6. Approval and freeze occur only after the findings are resolved.

---

## Permanent Governance Statement

```text
Ansiversa requires three levels of code review:

1. Codex reviews the implementation after development.
2. The Product Owner reviews the completed behavior.
3. Astra performs mandatory final source-level review before approval.

A change cannot be frozen, promoted, deployed, or enabled in production until
all three review levels pass.
```

This rule applies permanently across:

- `ansiversa-api`;
- `ansiversa`;
- shared platform code;
- mini-app implementations;
- AI systems;
- payment integrations;
- authentication;
- migrations;
- deployment configuration;
- generated artifacts;
- production promotions; and
- future Ansiversa repositories.

The rule preserves the distinct responsibilities of all three roles: Codex
validates execution, the Product Owner validates product intent, and Astra
independently validates the actual source before final approval.

---

## Established Engineering Precedent

The AI SEO implementation demonstrated the value of the three-level review
process before any production change:

- Phase 2 corrected fail-closed validation gaps.
- Phase 3 corrected semantic parity and adapter consistency issues.
- Phase 4 removed information leakage through failure evidence.
- Phase 5 closed false-ready paths in readiness validation.
- Phase 6 operational validation was confirmed against the committed
  implementation.

These findings and corrections occurred before production impact. They establish
the permanent Ansiversa standard:

> No meaningful code reaches the next stage until it has passed three
> independent reviews.
