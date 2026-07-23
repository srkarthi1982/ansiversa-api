# Astra Operational Readiness Specification

**Status:** Frozen v1.0
**Created:** 2026-07-23
**Owner:** Karthikeyan Ramalingam
**Architecture Review:** Astra
**Specification Agent:** Codex
**Task:** I1-023

The purpose of this specification is not to authorize Astra for production.

The purpose of this specification is to define the evidence required before
production authorization can even be considered.

> Operational readiness is not about proving that Astra can answer.
>
> It is about proving that Astra can be trusted when it answers.

---

# 1. Purpose

This specification defines the permanent operational-readiness gates for Astra
capabilities that use authenticated personal data.

It separates four decisions:

```text
Implementation complete
    does not imply
Runtime verification approved
    does not imply
Operational readiness approved
    does not imply
Production launch authorized
```

This document creates no runtime capability and grants no production
permission.

---

# 2. Operational Readiness Philosophy

## Astra Engineering Law #6

> Verification does not imply release.

Release is a business decision informed by engineering evidence, not an
engineering decision made because tests passed.

Engineering produces evidence. Architecture, control owners, and the Product
Owner review that evidence. The Product Owner decides whether to accept the
remaining operational risk and authorize production.

Readiness must be demonstrated through reproducible evidence. Confidence,
schedule pressure, implementation momentum, and a passing fixture test are not
substitutes for evidence.

The safe default is:

```text
ASTRA_PERSONAL_DATA_TOOLS_ENABLED=false
```

An absent, incomplete, stale, contradictory, or unowned gate is a failed gate.

---

# 3. Scope And Current Boundary

This specification applies to:

- the Platform User Context Provider
- registered personal-data tools
- Quiz Astra tools
- Course Tracker Astra tools
- Learning Intelligence composition
- personal context sent to OpenAI, when separately allowed
- audit, consent, retention, deletion, export, verification, enablement, and
  rollback controls for those capabilities

Current state:

```text
Architecture                          Approved
Deterministic runtime verification   Approved
Operational readiness                Not yet proven
Production personal-data execution   Disabled
Production launch                    Not authorized
```

This specification does not approve persistent memory, write tools, proactive
or scheduled personal-data use, unrestricted data export, sensitive-category
expansion, autonomous workflows, or additional app onboarding.

---

# 4. Readiness Gates

All gates are mandatory unless this specification explicitly marks them
deferred. Deferred items must remain outside the launch scope.

| Gate | Control Owner | Required Evidence | Pass Condition | Failure Condition |
|---|---|---|---|---|
| G01 Governance baseline | Architecture Reviewer | Approved contracts, scope map, resolved cross-references | Applicable governance is consistent and frozen | Conflict, missing approval, or ambiguous scope |
| G02 Personal-data classification | Product Owner and Architecture Reviewer | Field/category inventory for every enabled capability | Every input, output, log field, and OpenAI category is classified | Unclassified or prohibited data can enter the path |
| G03 Persistent audit | Backend Control Owner | Audit design, implementation evidence, migration evidence, retention job, access controls, tests | Every allowed, denied, failed, and unavailable personal-data execution produces bounded durable metadata | Missing events, raw payload logging, mutable/unprotected audit data, or untested retention |
| G04 Consent and user control | Product Owner | Approved user journey, copy, preference behavior, revocation tests | Initiated use and controls match the approved consent model | Passive use, unclear disclosure, ineffective revocation, or missing owner |
| G05 Retention | Data Control Owner | Data inventory, retention schedule, automated/manual enforcement evidence | Every persisted Astra data class has an approved and tested lifetime | Undefined, unenforced, or contradictory retention |
| G06 Deletion | Data Control Owner | Deletion/anonymization workflow and tests | In-scope data is removed or anonymized within policy without retaining app-record copies | Deleted app data remains usable by Astra or deletion SLA is unproven |
| G07 Export | Data Control Owner | Export scope, authentication, authorization, redaction, and test evidence | Any required export is owner-scoped, minimized, and approved, or explicitly excluded from launch with approval | Unapproved omission, cross-user export, or excessive disclosure |
| G08 Governed environment | Verification Owner | Environment record, isolation proof, access list, reset procedure | Verification cannot touch uncontrolled customer data | Real customer data, unclear isolation, or untracked access |
| G09 Governed accounts and fixtures | Verification Owner | Synthetic account manifest and deterministic fixture inventory | Accounts are synthetic, owner-explicit, resettable, and non-admin unless required | Copied customer data, shared ownership, unstable fixtures, or real secrets |
| G10 Dependency compatibility | Runtime Owner | Supported runtime matrix, clean install, startup, test, and deploy logs | All production and verification targets install and start reproducibly | Unsupported interpreter/driver combination or environment-only workaround |
| G11 Deployment compatibility | Runtime Owner | Preview/staging deployment evidence and configuration diff | Target deployment matches the approved runtime and secret/configuration contract | Configuration drift, missing controls, or unverifiable artifact |
| G12 Owner isolation | Security Verification Owner | Two-user positive/negative tests at service, API, and Assistant paths | No request, prompt, tool argument, model output, or action can select another owner | Any cross-user access or caller-controlled identity |
| G13 Privacy and minimization | Privacy Control Owner | Payload captures/redacted traces, schema review, prohibited-field tests | Only approved bounded fields cross each boundary | Raw records, restricted fields, secrets, internal IDs, or excessive context |
| G14 Safe failure behavior | Runtime and Security Owners | Timeout, dependency failure, disabled-tool, malformed-result, and provider-failure tests | Failures are bounded, non-leaking, observable, and fail closed | Fact invention, data leakage, unsafe fallback, or silent bypass |
| G15 Controlled enablement | Release Operator | Approved runbook, named window, exact target, approvals, monitoring plan | Enablement is time-bound, environment-specific, observed, and reversible | Broad, permanent, unapproved, or unmonitored enablement |
| G16 Rollback and flag restoration | Release Operator | Rehearsed rollback, restoration proof, post-check evidence | Safe state is restored within the approved objective and verified | Rollback cannot complete, state is uncertain, or the flag remains enabled unintentionally |
| G17 Evidence package | Readiness Review Chair | Immutable evidence index with dates, versions, owners, results, and exceptions | Evidence is complete, current, reproducible, and reviewable | Self-attestation without artifacts, stale evidence, or missing provenance |
| G18 Production Readiness Review | Product Owner | Signed decision record covering all gates and residual risks | Every required gate passes and residual risk disposition is explicit | Any blocking gate fails or approval authority is absent |

No single person should silently act as every control owner. If Ansiversa has
not assigned a named person to a role, the Product Owner must assign that role
in the readiness record before the gate can pass.

---

# 5. Gate Owners

The permanent accountability model is:

| Role | Accountability |
|---|---|
| Product Owner | Scope, user promise, business risk acceptance, and final launch authority |
| Architecture Reviewer | Contract consistency, boundary preservation, and architecture recommendation |
| Backend Control Owner | Audit and backend enforcement evidence |
| Runtime Owner | Dependency, build, deployment, and environment compatibility |
| Data Control Owner | Retention, deletion, and export behavior |
| Privacy Control Owner | Classification, minimization, disclosure, and OpenAI allowlist compliance |
| Security Verification Owner | Authentication, authorization, owner isolation, abuse, and fail-closed tests |
| Verification Owner | Governed fixtures, test execution, evidence capture, and reproducibility |
| Release Operator | Controlled flag change, monitoring, restoration, and rollback |
| Readiness Review Chair | Evidence completeness, meeting record, decisions, and unresolved actions |

One person may hold more than one role in a small team, but each role must still
be named independently in the evidence package. The Product Owner cannot waive
the technical fact of a failed critical control; the only safe disposition is
to remediate, reduce launch scope, or defer launch.

---

# 6. Required Evidence

Each evidence item must record:

- evidence ID
- gate ID
- owner
- date and time in UTC
- environment
- repository and commit
- deployed version or artifact identifier
- exact command, procedure, or test case
- expected result
- actual result
- pass, fail, or blocked status
- artifact location
- reviewer
- expiry or revalidation trigger

Acceptable evidence includes versioned specifications, test output, deployment
logs, redacted request/response traces, migration verification, screenshots,
audit-event samples, runbook rehearsal records, and signed decision records.

Statements such as “works locally,” “tests passed,” or “reviewed by the team”
without artifact provenance are not sufficient.

Secrets, tokens, raw personal records, full personal prompts, and full model
responses containing personal data must never be included in the evidence
package.

---

# 7. Pass / Fail Criteria

A gate passes only when:

1. its owner is named;
2. its evidence is complete and current;
3. the evidence matches the intended target environment and artifact;
4. all required tests pass;
5. no contradictory evidence remains unresolved; and
6. its reviewer records approval.

A gate fails when any required condition is false.

`Blocked` is a temporary evidence status, not a readiness approval. A blocked
mandatory gate prevents the Production Readiness Review from passing.

Critical automatic launch blockers include:

- cross-user data access
- caller- or model-controlled user identity
- raw secrets or prohibited personal data crossing a boundary
- missing durable personal-data audit events
- audit logs containing raw personal payloads
- inability to revoke consent or restore the safe flag state
- use of real customer data in verification
- unsupported or irreproducible production dependencies
- unapproved sensitive-category use
- any material difference between the verified artifact and launch artifact

---

# 8. Audit Requirements

Every personal-data tool attempt must create durable, backend-owned audit
metadata for allowed, denied, failed, and unavailable outcomes.

The minimum event contract remains:

- event ID
- timestamp
- authenticated user reference
- request/session correlation reference
- capability and tool name
- source application
- input classification, not raw prompt
- output classification, not raw response
- OpenAI personal-context category, if any
- outcome and bounded reason code
- duration bucket
- deployed version

The audit sink must:

- be separate from Activity Timeline product history;
- deny user control over security audit records;
- restrict read access to approved operational roles;
- protect integrity and record administrative access;
- support the approved retention/deletion behavior;
- avoid raw prompts, responses, records, SQL, tokens, cookies, and stack traces;
- remain available when the model provider is unavailable; and
- fail closed or disable personal-data execution if mandatory audit persistence
  cannot be confirmed.

Framework console or application logging alone is not a persistent audit sink.

---

# 9. Consent Requirements

Phase 1 permits personal context only after an authenticated user initiates a
question or workflow that clearly requires their own data.

Before production consideration, evidence must prove:

- the user is told when Astra may use their Ansiversa data;
- source apps are identified in personal answers;
- the control state is understandable and accessible;
- revocation prevents subsequent personal-data tool execution;
- consent is not inferred from unrelated Assistant use;
- passive, proactive, background, or scheduled access remains disabled;
- OpenAI receives personal context only when its category is allowlisted; and
- restricted categories require their separate approvals.

The server must enforce the effective control state. A frontend-only toggle is
not sufficient.

---

# 10. Retention Policy

This specification preserves the existing policy:

- no long-term Astra memory is introduced by Phase 1;
- transient conversation context must not become undeclared persistence;
- personal-data audit metadata defaults to 365 days;
- longer retention requires Product Owner approval and architecture review;
- investigation or legal holds must be documented, access-controlled, and
  time-bounded where possible; and
- all other persisted Astra data classes require an explicit approved lifetime
  before production use.

The implementation evidence must prove enforcement, not merely configuration.

---

# 11. Deletion Policy

User-requested deletion must remove or anonymize persisted Astra
personal-context records within 30 days.

Additional requirements:

- app-owned deletion remains authoritative;
- Astra must not retain independent copies of deleted app records;
- later answers must not use deleted records;
- caches and derived stores must honor the owning app's deletion;
- security audit metadata may remain through its approved retention window only
  when it contains no raw personal payload; and
- deletion failures must be observable, retryable, and included in operational
  evidence.

---

# 12. Export Policy

Export is not automatically authorized by this specification.

Before launch, the Product Owner and Data Control Owner must decide whether an
Astra-specific export is legally, contractually, or product-required for the
launch scope.

If required, it must be:

- strongly authenticated and owner-scoped;
- limited to user-visible conversation or approved audit metadata;
- free of internal security fields, other users' data, secrets, and raw model
  provider payloads;
- generated through a bounded, observable process; and
- covered by authorization, expiry, download, and abuse tests.

If not required for the approved launch scope, the evidence package must record
that decision and confirm that no undisclosed Astra persistence requires export.

---

# 13. Personal Data Classification

Every field crossing an Astra boundary must use one classification:

| Class | Meaning | Phase 1 Treatment |
|---|---|---|
| Public | Published platform/app information | Allowed through public knowledge controls |
| Internal operational | Non-secret runtime metadata | Bounded and role-restricted |
| Personal approved | Owner-scoped data explicitly approved by contract | Minimized, audited, purpose-bound, and read-only |
| Personal restricted | Sensitive or high-context data requiring separate approval | Prohibited unless app documentation, Product Owner, privacy, and architecture approvals exist |
| Secret | Tokens, credentials, session material, keys | Never available to Astra/model/evidence |
| Prohibited | Other-user, deleted, admin-only, raw record, or disallowed category | Must be rejected before tool/model boundaries |

The classification inventory must cover tool inputs, app-service outputs,
Assistant responses, actions, logs, audit events, caches, provider context, test
fixtures, exports, and evidence artifacts.

---

# 14. Governed Test Environment

The controlled verification environment must:

- have an explicit name, purpose, owner, and lifetime;
- be isolated from uncontrolled customer records;
- match production architecture closely enough to validate deployment behavior;
- use environment-specific secrets stored through approved secret management;
- restrict access to named operators;
- record configuration without exposing secret values;
- support deterministic reset;
- produce durable audit evidence;
- support monitoring and rollback rehearsal; and
- prohibit use for unrelated development or demonstrations during the window.

Production verification, if approved, may use only the governed smoke-test
account and synthetic records. It must not enable all-user production access.

---

# 15. Test Account Rules

At least two synthetic authenticated users are required:

- primary verification user with known Quiz and Course Tracker records;
- isolation user with distinct records that the primary user must never access.

The fixture manifest must include:

- account purpose and owner
- creation method
- non-secret account reference
- app-owned records and expected summaries
- expected Quiz recommendation
- expected Course Tracker recommendation
- expected combined Learning Intelligence answer
- empty and partial-data cases
- reset and cleanup procedure

Test accounts must not use copied customer records, real personal data, shared
owner identifiers, undocumented admin permissions, or credentials committed to
the repository.

---

# 16. Dependency Verification

The runtime owner must publish and verify a compatibility matrix covering:

- Python version
- operating system/build image
- `libsql-experimental`
- `sqlalchemy-libsql`
- SQLAlchemy
- Turso/libSQL connectivity
- Vercel build/runtime target
- local, QA, controlled-verification, and production parity

Known issue to resolve or formally isolate:

```text
On Windows with the current Python 3.13 environment,
libsql-experimental==0.0.55 does not install from an available wheel and a
source build requires the MSVC linker.
```

A local SQLite override proves deterministic application logic but does not
prove production libSQL deployment compatibility.

Gate evidence requires a clean environment installation and startup using the
same supported dependency path as the target deployment. Undocumented manual
machine state is a failure.

---

# 17. Deployment Compatibility

Evidence must prove:

- the verified commit is the deployed commit;
- runtime and migration dependencies install cleanly;
- all required databases remain isolated and reachable;
- configuration names match the documented contract;
- personal-data tools default to disabled in a fresh deployment;
- secret values are present only in the approved platform secret store;
- CORS, authentication cookies, and backend identity work in the target;
- audit persistence and monitoring work in the target; and
- deployment rollback restores the previous artifact and safe flag state.

No production database migration may be inferred from this specification.
Migration work requires a separately approved implementation task.

---

# 18. Owner Isolation Verification

Owner isolation must be proven at:

1. app service boundary;
2. registered tool executor;
3. Assistant API;
4. Learning Intelligence composition;
5. OpenAI context boundary, if used;
6. audit event boundary; and
7. export boundary, if implemented.

Required negative cases include:

- unauthenticated request;
- primary user attempting to reference the isolation user;
- prompt containing another user or fabricated owner ID;
- tool arguments containing user/owner identifiers;
- manipulated frontend context;
- stale session after logout or account switch;
- concurrent requests from both users;
- malformed or oversized arguments;
- model text requesting broader access; and
- direct disabled/deprecated tool execution.

Any cross-user result is release-blocking.

---

# 19. Privacy Verification

Privacy evidence must verify that responses, logs, audit events, provider
context, and evidence artifacts exclude:

- owner/user IDs from user-visible or model-facing data;
- authentication claims, tokens, cookies, and secrets;
- internal database identifiers;
- raw SQL and schema details;
- Quiz question text, options, answer keys, explanations, and raw responses;
- Course Tracker goals, notes, progress summaries/reflections, and internal IDs;
- full personal records;
- deleted or other-user records; and
- categories outside the approved OpenAI allowlist.

Payload inspection must use synthetic data and redact evidence without hiding
whether a prohibited field was present.

---

# 20. Controlled Enablement Procedure

Controlled enablement is a verification operation, not a launch.

Before the window:

1. identify exact environment, artifact, accounts, operator, and reviewers;
2. confirm G01 through G14 have passed for the verification scope;
3. confirm the current flag is `false`;
4. capture a redacted configuration baseline;
5. verify monitoring, durable audit, rollback, and communication channels;
6. record start/end time and abort criteria; and
7. obtain Product Owner and Release Operator approval.

During the window:

1. enable `ASTRA_PERSONAL_DATA_TOOLS_ENABLED=true` only in the named target;
2. confirm all-user access has not been enabled unintentionally;
3. run the approved Quiz, Course Tracker, Learning Intelligence, partial-data,
   no-data, failure, privacy, and two-user isolation cases;
4. inspect bounded audit events and operational health;
5. stop immediately on a critical blocker; and
6. make no unrelated changes.

After the window:

1. restore the flag to `false`;
2. verify personal-data questions return the bounded unavailable behavior;
3. verify no test mutation or unintended customer access occurred;
4. preserve redacted evidence and record all deviations;
5. clean or reset synthetic fixtures according to the runbook; and
6. close the window with operator and reviewer sign-off.

---

# 21. Rollback Procedure

Rollback must be initiated when:

- owner isolation fails;
- prohibited data is exposed;
- audit persistence fails;
- consent/revocation enforcement fails;
- latency or failure rate exceeds the approved objective;
- deployed state differs from the verified artifact;
- the flag scope is broader than approved; or
- an operator cannot determine whether the system is safe.

Rollback order:

```text
Set personal-data flag false
    ↓
Verify bounded disabled behavior
    ↓
Stop affected verification traffic
    ↓
Restore prior artifact/configuration if required
    ↓
Preserve bounded audit and incident evidence
    ↓
Assess data exposure and required notification
    ↓
Record failed gate and remediation owner
```

Rollback must not delete security evidence or conceal a failed verification.

---

# 22. Flag Restoration

Unless a separate Production Launch Decision explicitly authorizes continued
operation, every controlled verification ends with:

```text
ASTRA_PERSONAL_DATA_TOOLS_ENABLED=false
```

Restoration evidence must include:

- timestamp
- target environment
- operator
- configuration/version reference
- post-restoration request showing bounded unavailable behavior
- audit/monitoring confirmation
- reviewer sign-off

An enabled flag after the verification window is a failed G16 gate.

---

# 23. Production Readiness Review

The review package must contain:

- executive summary
- exact proposed launch scope
- gate matrix and evidence index
- named owners and reviewers
- dependency and deployment matrix
- privacy and owner-isolation results
- controlled enablement and rollback rehearsal
- open defects and deferred scope
- residual risk register
- launch, limited launch, defer, or reject recommendation
- explicit statement that recommendation is not launch authorization

Possible outcomes:

- `READY FOR PRODUCT DECISION`
- `READY FOR LIMITED PRODUCT DECISION`
- `NOT READY`
- `REVIEW BLOCKED`

The review must never silently convert into enablement.

---

# 24. Launch Authority

Only Karthikeyan Ramalingam, as Product Owner, may authorize production launch.

Launch authorization requires:

- a passed Production Readiness Review;
- architecture recommendation;
- all mandatory control-owner approvals;
- explicit accepted scope and residual risks;
- named operator, window, monitoring, and rollback plan; and
- a separate dated decision record.

Codex may implement approved tasks and produce evidence but cannot authorize
launch. Astra may review architecture and governance but cannot authorize
launch. Passing tests cannot authorize launch.

---

# 25. Failure Handling

When a gate fails:

1. keep or restore personal-data execution to disabled;
2. record the failed gate and evidence;
3. classify severity and possible exposure;
4. assign remediation owner and target review;
5. preserve bounded audit/incident evidence;
6. notify the Product Owner when critical data, identity, or control boundaries
   may have failed;
7. require new evidence after remediation; and
8. rerun all dependent gates, not only the failed assertion.

Failure must not be converted to pass through wording changes, test deletion,
reduced assertions, or undocumented environment exceptions.

---

# 26. Risk Acceptance

Residual risk acceptance belongs to the Product Owner and must be documented.

Risk acceptance may not override:

- cross-user exposure;
- caller/model-controlled identity;
- secrets or prohibited-data exposure;
- missing mandatory audit persistence;
- inability to restore the safe state;
- uncontrolled real-customer verification data; or
- legal or contractual requirements.

For non-critical residual risk, the decision record must state:

- risk
- affected scope
- evidence
- compensating control
- owner
- expiry/review date
- rollback implication
- accepting authority

Silence is not risk acceptance.

---

# 27. Deferred Items

The following remain outside this specification's authorized implementation
scope:

- persistent Astra memory
- write tools
- proactive or scheduled personal-data use
- autonomous workflows
- sensitive app-category expansion
- unrestricted conversation or context export
- all-app intelligence
- permanent production enablement
- additional Astra app onboarding
- migrations or new runtime services
- framework, registry, context-provider, or app behavior changes

Each requires a separately approved task and must inherit these readiness gates
where personal data is involved.

---

# 28. Evidence Package Template

The future readiness implementation must create an evidence index using this
minimum shape:

| Evidence ID | Gate | Owner | Environment | Commit / Artifact | Result | Date | Artifact | Reviewer |
|---|---|---|---|---|---|---|---|---|
| OR-E001 | G01 | TBD | Documentation | TBD | TBD | TBD | TBD | TBD |

The evidence package must also record:

```text
Flag before verification: false
Flag during approved window: true
Flag after verification: false
Production launch authorized: no, unless a separate decision record exists
```

---

# 29. Specification Validation

I1-023 is complete when:

- all required operational-readiness subjects are defined;
- existing Astra governance is preserved;
- task, backlog, dependencies, README, and AGENTS references resolve;
- Markdown remains readable;
- `git diff --check` passes;
- only Markdown files change in `ansiversa-api`;
- runtime code and configuration remain unchanged; and
- production personal-data execution remains disabled.

---

# 30. Explicit Non-Authorization

This specification:

- does not enable personal-data tools;
- does not modify runtime behavior;
- does not modify the Tool Framework;
- does not modify the Tool Registry;
- does not modify the User Context Provider;
- does not modify Quiz or Course Tracker;
- does not change architecture;
- does not create an audit sink, consent control, export, fixture, migration, or
  deployment;
- does not approve operational readiness; and
- does not grant production authorization.

The next phase may begin only through separately approved and frozen
implementation tasks.
