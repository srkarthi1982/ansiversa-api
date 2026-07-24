# Astra AI Architecture Risk Register

**Status:** Accepted for ASTRA-001 and ASTRA-002; ASTRA-003 minor revision applied

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
- implementation before approved scope.
