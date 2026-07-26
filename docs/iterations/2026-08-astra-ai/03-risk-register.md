# Astra AI Architecture Risk Register

**Status:** Accepted for ASTRA-001, ASTRA-002, ASTRA-003, ASTRA-004, ASTRA-005, ASTRA-006, and ASTRA-007; ASTRA-008 proposed; future implementation risks remain open

| ID | Risk | Level | Mitigation | Status |
|---|---|---|---|---|
| ASTRA-R01 | Overlap with existing Assistant creates confusing ownership | High | Define Assistant as current runtime surface and Astra AI as governed intelligence layer | Open |
| ASTRA-R02 | Duplicate orchestration layers drift | High | Reuse existing foundations and migrate in authorized stages | Open |
| ASTRA-R03 | External provider coupling bypasses governance | Critical | Providers receive only policy-approved, minimized, purpose-bound model input envelopes and never own identity, permission, facts, actions, or authority | Open |
| ASTRA-R04 | Permission bypass through prompt, frontend hints, or tool args | Critical | Backend-owned auth, fail-closed policy, no caller-controlled identity | Open |
| ASTRA-R05 | App database overreach | Critical | App modules own queries; central Astra never queries app DBs directly | Open |
| ASTRA-R06 | Hidden execution | Critical | Action proposal, confirmation, audit, and readiness gates before execution | Open |
| ASTRA-R07 | Long-term memory stores data silently | High | No silent retention; require purpose, consent, deletion, export, retention | Open |
| ASTRA-R08 | Cross-user leakage | Critical | Owner-scoped contracts and negative isolation tests | Open |
| ASTRA-R09 | Capability hallucination | High | Registry-backed capability discovery only | Open |
| ASTRA-R10 | Audit evidence leaks secrets or private records | High | Bounded metadata; no raw prompts, SQL, records, tokens, or stack traces | Open |
| ASTRA-R11 | Excessive centralization weakens app ownership | High | Applications own capabilities and business rules | Open |
| ASTRA-R12 | Production activation before readiness | Critical | Separate operational readiness and Product Owner launch approval | Open |
| ASTRA-R13 | Astra AI confused with AI SEO | Medium | AI SEO publishes public truth; Astra consumes/orchestrates | Open |
| ASTRA-R14 | Frontend coupling too early | Medium | Interface contracts after architecture; frontend hints are not authority | Open |
| ASTRA-R15 | App #101 or uncontrolled app expansion appears through AI roadmap | High | Preserve fixed 100-app catalog boundary | Open |
| ASTRA-R16 | External model becomes default reasoning path | Critical | ASTRA-002 requires an explicit external-intelligence necessity decision before provider invocation | Open |
| ASTRA-R17 | User context loads before need is established | High | ASTRA-002 orders platform context before user context and requires minimized context assembly | Open |
| ASTRA-R18 | Pipeline treats refusal or clarification as implementation failure | Medium | ASTRA-002 defines refusal and clarification as first-class governed outcomes | Open |
| ASTRA-R19 | Planning is mistaken for execution authority | Critical | ASTRA-002 keeps action proposal separate from Tool Executor and app-owned execution | Open |
| ASTRA-R20 | Conversation state becomes silent memory | Critical | ASTRA-003 makes conversation state transient unless separate memory architecture authorizes persistence | Open |
| ASTRA-R21 | Context is loaded because it is available | Critical | ASTRA-003 requires need-driven loading and smallest sufficient context | Open |
| ASTRA-R22 | Private context loads for public questions | Critical | ASTRA-003 forbids private context for public questions | Open |
| ASTRA-R23 | Concurrent conversations mix context | Critical | ASTRA-003 requires user/session and conversation isolation | Open |
| ASTRA-R24 | Stale context influences current decisions | High | ASTRA-003 requires expiration markers and stale-context behavior | Open |
| ASTRA-R25 | Contradictory provider facts are reconciled by Astra | Critical | ASTRA-003 requires authoritative-owner precedence, clarification, fail-closed behavior, or visible limitation rather than manufactured consensus | Open |
| ASTRA-R26 | Astra fabricates capabilities from user text or provider output | Critical | ASTRA-004 requires authoritative registry proof before a capability is available | Open |
| ASTRA-R27 | Capability discovery is mistaken for execution authority | Critical | ASTRA-004 states discovery never grants execution authority | Open |
| ASTRA-R28 | Tool ownership is centralized inside Astra | Critical | ASTRA-004 keeps tool behavior owned by the owning service | Open |
| ASTRA-R29 | Unknown side effects are treated as safe | Critical | ASTRA-004 treats unknown side effects as write/action risk and fails closed | Open |
| ASTRA-R30 | Deprecated or experimental capabilities are selected silently | High | ASTRA-004 requires explicit availability states and authorization handling | Open |
| ASTRA-R31 | Registry permission metadata is mistaken for live user authorization | Critical | ASTRA-004 separates permission requirements metadata from authorization-provider or owning-service live decisions | Open |
| ASTRA-R32 | Equal candidates are selected by accidental ordering | High | ASTRA-004 requires governed deterministic precedence or clarification for user-significant ambiguity | Open |
| ASTRA-R33 | Execution planning is mistaken for execution authority | Critical | ASTRA-005 makes planning declarative and prohibits execution during planning | Open |
| ASTRA-R34 | Approval gates are lost during replanning | Critical | ASTRA-005 requires approval requirements to survive replanning | Open |
| ASTRA-R35 | State-changing work is hidden inside a broad action | Critical | ASTRA-005 requires every state-changing action to have an explicit governed execution step | Open |
| ASTRA-R36 | Partial success is represented as full success | High | ASTRA-005 adds partial-success, failure, compensation, and cancellation states | Open |
| ASTRA-R37 | Compensation is invented silently after failure | High | ASTRA-005 requires retry, rollback, and compensation policy before execution | Open |
| ASTRA-R38 | Execution evidence leaks sensitive data | High | ASTRA-005 limits evidence to bounded metadata and prohibits raw private payloads, secrets, prompts, SQL, and stack traces | Open |
| ASTRA-R39 | Prior approval is reused after a material plan or step change | Critical | ASTRA-005 binds approval and confirmation grants to exact plan version, affected steps, scope, material inputs, impact, and validity window | Open |
| ASTRA-R40 | A timed-out state-changing step executes twice after retry | Critical | ASTRA-005 requires stable step identity, idempotency classification, duplicate detection, retry scope, and uncertain-outcome reconciliation | Open |
| ASTRA-R41 | Execution request is mistaken for execution authority | Critical | ASTRA-006 requires executor and owning-service acceptance before execution | Open |
| ASTRA-R42 | Executor bypasses owning-service validation | Critical | ASTRA-006 requires owner-service validation before execution | Open |
| ASTRA-R43 | Live authorization is assumed from planning evidence | Critical | ASTRA-006 requires live authorization recheck before execution | Open |
| ASTRA-R44 | Timeout causes duplicate state-changing execution | Critical | ASTRA-006 treats timeout as uncertain outcome and requires reconciliation before retry | Open |
| ASTRA-R45 | Stale plan executes after scope, approval, or validity changes | Critical | ASTRA-006 requires plan version, digest, approval binding, confirmation binding, and validity window checks | Open |
| ASTRA-R46 | Partial success is hidden by executor reporting | High | ASTRA-006 makes partial success and compensation reporting explicit | Open |
| ASTRA-R47 | Executor admission is mistaken for owning-service acceptance | Critical | ASTRA-006 separates executor admission from owner acceptance and prohibits execution until owner acceptance succeeds | Open |
| ASTRA-R48 | Multi-owner execution is treated as one atomic transaction | Critical | ASTRA-006 requires independent per-step owner authority and partial-success or residual-effect disclosure | Open |
| ASTRA-R49 | Provider becomes Astra's default brain | Critical | ASTRA-007 requires local sufficiency and external-intelligence necessity before provider selection | Open |
| ASTRA-R50 | Provider output becomes platform truth | Critical | ASTRA-007 treats provider responses as untrusted until validated | Open |
| ASTRA-R51 | Sensitive data leaves Ansiversa unnecessarily | Critical | ASTRA-007 requires minimized, purpose-bound, sensitivity-classified input envelopes | Open |
| ASTRA-R52 | One provider becomes a constitutional dependency | High | ASTRA-007 requires provider-neutral capability, envelope, validation, failure, and routing concepts | Open |
| ASTRA-R53 | Prompt bypasses parent architecture | Critical | ASTRA-007 defines prompt governance as subordinate to parent architecture | Open |
| ASTRA-R54 | Provider costs grow silently | High | ASTRA-007 requires token and cost governance before provider use | Open |
| ASTRA-R55 | Provider selection occurs before eligibility is governed | Critical | ASTRA-007 separates provider eligibility from provider selection and restricts selection to eligible providers | Open |
| ASTRA-R56 | Unvalidated provider output becomes authoritative truth | Critical | ASTRA-007 classifies provider output as advisory until validated by Astra and authoritative owners | Open |
| ASTRA-R57 | Memory becomes silent surveillance | Critical | ASTRA-008 requires approved memory class, purpose, retention, and user controls before memory use | Open |
| ASTRA-R58 | Memory becomes an unauthorized cross-app datastore | Critical | ASTRA-008 keeps app-owned data out of Astra memory and preserves owning-service authority | Open |
| ASTRA-R59 | Memory bypasses authorization or execution governance | Critical | ASTRA-008 states memory cannot determine identity, authorization, capability existence, execution authority, app facts, or production truth | Open |
| ASTRA-R60 | User cannot forget retained data | Critical | ASTRA-008 makes forgetting, deletion, export, and retention mandatory governance | Open |
| ASTRA-R61 | Provider output becomes durable memory truth | Critical | ASTRA-008 prohibits provider output from becoming memory by default and requires validation plus memory eligibility | Open |
| ASTRA-R62 | Stale memory overrides current authoritative facts | High | ASTRA-008 requires authoritative sources to win and stale or conflicting memory to be ignored, clarified, or deleted | Open |
| ASTRA-R63 | Memory retrieval over-collects private context | High | ASTRA-008 requires need-driven, minimized, purpose-bound retrieval | Open |
| ASTRA-R64 | Memory references transfer ownership silently | Critical | ASTRA-008 separates Astra-owned memory from governed references and states references do not transfer ownership or create a second datastore | Open |
| ASTRA-R65 | Memory existence is treated as retrieval permission | Critical | ASTRA-008 requires separate retrieval authorization before memory can be retrieved | Open |

---

# Future Release Blockers

- unresolved ownership conflicts;
- missing authorization model;
- missing audit persistence for personal-data execution;
- any direct app database access by central Astra code;
- hidden execution path;
- provider-selected identity or capability;
- unrestricted backend context sent to an external model provider;
- external model invocation by default rather than governed necessity decision;
- cross-user data access;
- production enablement without readiness review; and
- conversation persistence without approved memory architecture;
- context loading without established need;
- provider fact reconciliation without authoritative ownership;
- capability selection without authoritative registry proof;
- live authorization inferred from registry permission metadata;
- candidate tie resolution based on accidental ordering;
- tool selection that implies execution authority;
- execution plan creation that mutates application state;
- state-changing actions without explicit governed execution steps;
- replanning that removes approval requirements;
- material plan or step changes that reuse stale approval grants;
- retries that assume an uncertain state-changing step did not execute;
- execution requests treated as execution authority;
- executor path that bypasses owning-service validation;
- executor admission treated as business authorization;
- multi-owner execution treated as atomic commit or distributed rollback;
- execution without live authorization recheck;
- stale plan execution after approval, scope, or validity changes;
- executor reporting that hides partial success or compensation needs;
- provider-first reasoning;
- provider selection before external-intelligence necessity;
- provider selection before provider eligibility;
- provider output treated as authoritative platform truth;
- unvalidated provider output mutating state, granting authorization, or
  overriding ownership;
- raw internal context sent to providers by default;
- prompt architecture that overrides parent architecture;
- provider calls without token and cost governance;
- runtime memory before ASTRA-008 approval and freeze;
- memory stored without approved class, purpose, retention, deletion, export,
  and user controls;
- memory references that transfer ownership or become alternate record truth;
- memory retrieval based only on memory existence;
- app-owned records copied into Astra memory;
- memory used as identity, authorization, capability, execution, app, or
  production truth;
- provider output stored as durable memory truth by default;
- unknown execution risk treated as safe;
- implementation before approved scope.
