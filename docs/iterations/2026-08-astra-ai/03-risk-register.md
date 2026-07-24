# Astra AI Architecture Risk Register

**Status:** Accepted for ASTRA-001; future implementation risks remain open

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

---

# Future Release Blockers

- unresolved ownership conflicts;
- missing authorization model;
- missing audit persistence for personal-data execution;
- any direct app database access by central Astra code;
- hidden execution path;
- provider-selected identity or capability;
- unrestricted backend context sent to an external model provider;
- cross-user data access;
- production enablement without readiness review; and
- implementation before approved scope.
