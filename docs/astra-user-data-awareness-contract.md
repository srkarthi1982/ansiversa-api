# Astra User Data Awareness Contract

**Status:** Frozen v1.0
**Created:** 2026-07-22
**Owner:** Karthikeyan Ramalingam
**Architecture Review:** Astra
**Implementation Agent:** Codex

This document defines the Phase 1 governance boundary for allowing Astra to
understand an authenticated user's own Ansiversa data.

It implements Iteration 1 task
`I1-001 — Astra AI User Data Awareness — Phase 1`.

---

# Purpose

Astra may eventually answer questions using a user's own Ansiversa records, but
only through governed, authenticated, owner-scoped, app-owned contracts.

This contract defines what Astra is allowed to know.

It does not define or implement how Astra retrieves that data at runtime.

---

# Scope

I1-001 establishes governance for:

- User identity
- Data ownership
- Privacy policy
- OpenAI personal-context allowlist
- Audit policy
- Retention and deletion policy
- Seeded authenticated verification environments

I1-001 is documentation-only.

---

# Core Rule

```text
Backend identity is authoritative.
Applications own user data.
Astra receives only approved, minimized context.
OpenAI never determines identity, ownership, or permissions.
```

---

# User Identity

The authenticated backend user is the only authoritative user identity for
Astra user-data awareness.

Astra must use identity already established by the backend authentication layer.

OpenAI must never:

- Choose the user
- Infer the user
- Override the user
- Select a tenant
- Select an owner ID
- Receive authentication tokens or claims
- Receive password hashes, session secrets, or cookie values

Identity propagation rules:

- The backend receives the authenticated user from existing auth middleware and
  route dependencies.
- Astra runtime tasks may receive only a backend-issued user context object.
- Application services must verify ownership using their existing owner-scoped
  logic.
- Tool requests must fail closed when no authenticated user exists.
- Guest Assistant behavior remains limited to public platform knowledge.

Tenant boundaries:

- Current Phase 1 assumes one authenticated user owner boundary.
- If tenant or team ownership is introduced later, Product Owner approval and
  Astra architecture review are required before Astra can use tenant-scoped
  context.

---

# Data Ownership

Applications remain the source of truth for their own data.

Astra does not own application data.

Astra must not:

- Query application databases directly
- Bypass application service methods
- Reimplement application business rules
- Merge records across users
- Store app-owned records as Astra-owned records
- Treat OpenAI output as authoritative application state

Application modules own:

- Database sessions
- Models
- Repositories
- Services
- Validation
- Calculations
- Filtering
- Sorting
- Archive/delete behavior
- Privacy exclusions
- User-facing response shape

Astra may consume only approved structured summaries produced through
app-owned contracts.

---

# Privacy Policy

Astra user-data awareness follows least privilege.

Permitted personal context must be:

- Authenticated
- Owner-scoped
- Purpose-bound to the user's current question
- Minimized to fields required for the answer
- Bounded by count, time range, and payload size
- Read-only in Phase 1
- Documented in the app's `astra-ai.md`

Prohibited personal context includes:

- Authentication secrets
- Passwords or password hashes
- Session tokens
- Raw JWT claims
- Payment credentials
- Government identifier values
- Health details beyond approved app summaries
- Legal documents or legal advice payloads
- Financial account numbers or payment instrument data
- Raw uploaded files, binary blobs, transcripts, OCR output, or full document
  bodies unless separately approved
- Deleted records
- Admin-only data
- Another user's records

User visibility:

- Future user controls must make Astra data usage understandable to the user.
- User-facing responses should describe the source app when personal context is
  used.
- If Astra cannot access a data category because it is not approved, it should
  say that the capability is unavailable instead of guessing.

Consent:

- Phase 1 consent is based on authenticated user initiation: Astra may use
  approved personal context only when the signed-in user asks a question or
  invokes an Assistant workflow that clearly requires their own data.
- Passive, background, proactive, or scheduled personal-data use requires a
  later explicit user-control implementation and separate approval.
- Before any personal context is sent to OpenAI, the category must be present in
  the OpenAI allowlist in this contract and in the app's `astra-ai.md`.
- Sensitive categories require explicit Product Owner approval and Astra review
  before use.

---

# OpenAI Personal-Context Allowlist

OpenAI may receive only minimized, structured context needed to explain an
answer. Deterministic backend logic remains authoritative.

## Allowed In Phase 1

These categories may be sent to OpenAI after backend minimization and
owner-scoped retrieval:

- App name and route label
- User-facing record title or name when required for the answer
- Status values such as completed, overdue, active, archived, paid, unpaid, or
  due soon
- Dates and relative date buckets needed for the answer
- Counts and summary metrics
- Progress percentages
- Category labels created by the user when not sensitive by nature
- Short previews already displayed in the current frontend workflow
- Deterministic recommendations generated by backend services

## Restricted

These categories require app-level documentation in `astra-ai.md`, Product
Owner approval, and Astra review before they may be sent to OpenAI:

- Free-form user notes
- Long text fields
- File-derived text
- OCR output
- Uploaded document metadata beyond title/status/date
- Health, medicine, vaccination, doctor, or medical-adjacent details
- Financial transaction descriptions beyond summarized categories and totals
- Legal, immigration, tax, employment, or regulated-document details
- Contact details for people other than the authenticated user
- Location details more precise than what the answer requires
- Child, family, school, or household member details

Restricted context should be summarized deterministically before OpenAI sees it
whenever practical.

## Never Allowed

These categories must not be sent to OpenAI in Phase 1:

- Passwords
- Password hashes
- Authentication tokens
- Session identifiers
- API keys
- Secrets
- Raw cookie values
- Raw JWTs or claims payloads
- Database schemas
- SQL queries
- Internal service stack traces
- Full raw records
- Full document bodies
- Binary files
- Payment card, bank account, or payment credential values
- Government identifier values
- Deleted records
- Records owned by another user
- Admin-only records

---

# Audit Policy

Every future Astra personal-data access must be auditable.

I1-001 defines the audit model only. It does not implement runtime logging.

Minimum audit event fields:

- Event ID
- Timestamp
- Authenticated user ID
- Capability requested
- Assistant session ID or request correlation ID
- Application or platform source
- Tool or provider name when available
- Input classification, not raw prompt text
- Output classification, not raw response body
- OpenAI personal-context category used, if any
- Outcome: allowed, denied, failed, or unavailable
- Denial or failure reason code
- Request duration bucket

Audit logs must not store:

- Raw personal records
- Full prompts containing personal data
- Full model responses containing personal data
- Authentication secrets
- Tokens or cookie values
- Raw SQL
- Stack traces intended for developers

Audit sink decision:

- The permanent audit sink should be a backend-owned parent/global audit
  capability.
- Runtime implementation is deferred to the task that first implements personal
  data tool execution.
- Until the audit sink exists, personal-data tools must not go live.
- Runtime personal-data tools must also remain disabled by default until
  consent/user controls, deletion/export handling, and seeded verification
  gates are approved and implemented. I1-002 enforces this with the
  backend-owned `ASTRA_PERSONAL_DATA_TOOLS_ENABLED=false` default.

---

# Retention And Deletion

Conversation retention:

- Phase 1 must not introduce long-term Astra memory.
- Assistant conversation context may be transient unless a later approved task
  explicitly adds persistence.
- Persistent memory remains deferred and governed by I1-011 or a later approved
  task.

Audit retention:

- Personal-data access audit metadata is retained for 365 days by default.
- After 365 days, audit metadata should be deleted or anonymized unless a
  security investigation, abuse investigation, or legal requirement requires
  longer retention.
- Retention longer than 365 days requires Product Owner approval and Astra
  architecture review.
- Audit records should store classifications and metadata, not raw personal
  payloads.

Deletion:

- User-requested deletion must remove or anonymize persisted Astra
  personal-context records within 30 days.
- App-owned records remain deleted through the owning app's existing deletion
  behavior.
- Astra must not keep separate copies of deleted app-owned records.
- If a user deletes an app-owned record, future Astra answers must not use that
  deleted record.
- Security audit metadata may remain until the audit retention window ends, but
  it must not contain raw personal payloads.

Future export:

- A future export capability may expose the user's Assistant conversation and
  audit metadata after privacy and product review.
- Export is not implemented by I1-001.

---

# Seeded Authenticated Verification Environment

Astra user-data features require stable authenticated test users before runtime
tools go live.

Seeded verification users must be:

- Clearly marked as test accounts
- Created through approved environment-specific seed scripts or admin setup
- Isolated from real customer data
- Stable enough for Playwright and browser verification
- Resettable without affecting production users
- Documented with owned records per app under test

Required environments:

- Local development: deterministic seeded test user and app records.
- QA: authenticated test user with realistic but synthetic data.
- Production verification: approved smoke-test account only, with synthetic
  records and Product Owner approval.

Seed data rules:

- Do not use real personal data.
- Do not use copied customer records.
- Do not store real secrets in seed files.
- Do not grant admin permissions unless the verification scenario requires it
  and is separately approved.
- Keep test account ownership explicit in verification docs.

I1-001 does not create runtime fixtures, users, or seed scripts. It defines the
governance those future fixtures must follow.

Personal-data tools may be enabled only in explicitly governed test or
non-production verification contexts until this seeded verification model is in
place.

---

# Existing System Alignment

This contract extends existing architecture.

It does not redesign:

- Authentication
- Authorization
- Assistant retrieval
- Knowledge Registry
- Activity
- Notifications
- Dashboard
- Application ownership
- Mini-app database isolation
- API response contracts

Runtime implementation tasks must preserve existing Assistant identity answers,
platform knowledge answers, deterministic app recommendations, route-safe
actions, and public-knowledge behavior.

---

# Explicit Non-Goals

I1-001 does not implement:

- Tool execution
- Runtime tool registry
- OpenAI orchestration
- Application queries
- Quiz integration
- Course Tracker integration
- Database access layers
- AI memory
- Recommendations
- Runtime audit logging
- Runtime consent controls
- Runtime deletion/export controls
- Seed fixtures or test accounts
- Migrations
- App #101

---

# Validation

For I1-001, validation is documentation-only:

- Markdown files must remain readable.
- I1-001 documentation must reference I1-009 as its prerequisite.
- Cross references must resolve where they point to iteration package files.
- Governance decisions must not contradict the Astra Integration Contract.
- `git diff --check` must pass.
- Repositories must remain clean after commit and push.

Runtime, browser, backend, and frontend build validation begin when a frozen
task changes runtime code.
