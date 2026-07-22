# Ansiversa Iteration 1

# Risk Register

This document records known risks for the iteration together with mitigation strategies.

The objective is to identify risks before implementation begins and reduce their impact through planning.

---

# Risk Levels

| Level | Meaning |
|---------|---------|
| Low | Minimal impact |
| Medium | Manageable impact |
| High | Significant impact |
| Critical | May block release |

---

# Risk Status

| Status | Meaning |
|---------|---------|
| Open | Requires monitoring |
| Mitigated | Risk reduced |
| Accepted | Risk acknowledged |
| Closed | No longer applicable |

---

# Risk Register

| ID | Risk | Impact | Likelihood | Level | Mitigation | Status |
|----|------|---------|------------|--------|------------|--------|
| R-001 | Astra accesses another user's data | High | Low | Critical | Backend-owned tool context, authenticated user injection, caller-controlled identity rejection, and app-owned owner-scoped services | Mitigated |
| R-002 | AI generates non-deterministic answers for platform identity | Medium | Medium | High | Deterministic identity responses | Mitigated |
| R-003 | User context queries become slow | Medium | Medium | Medium | Query optimization and indexing | Open |
| R-004 | Prompt injection attempts | High | Medium | High | Intent validation, safety filters, restricted-request priority, allowlisted tools, and argument validation | Mitigated |
| R-005 | Excessive OpenAI usage | Medium | Medium | Medium | Prefer deterministic backend responses | Open |
| R-006 | Regression in existing Assistant behavior | High | Low | High | Full regression suite before release | Open |
| R-007 | Unauthorized SQL execution | High | Low | Critical | No model-generated SQL, no database schemas, no raw SQL tool arguments, and app-owned service execution only | Mitigated |
| R-008 | Personal-data tools go live before persistent audit/user-control gates | High | Low | High | I1-002 keeps personal-data tools disabled by default with `ASTRA_PERSONAL_DATA_TOOLS_ENABLED=false`; persisted audit sink, consent/user controls, deletion/export, and seeded verification setup remain release gates | Open |
| R-009 | Platform user context leaks excessive personal data | High | Low | Critical | I1-003 uses profile-based lazy loading, backend-owned identity, canonical route validation, owner-scoped existing services, bounded summaries, and OpenAI-safe serialization without backend user IDs, emails, raw activity metadata, or notification bodies | Mitigated |
| R-010 | Quiz Astra tools expose question-bank or cross-user data | High | Low | Critical | I1-004 keeps Quiz tools inside the Quiz module, owner-scopes every query to backend-authenticated user context, returns summaries only, excludes question text/options/answer keys/explanations/raw responses/internal IDs, and keeps production execution behind the personal-data tool gate | Mitigated |

---

# Release Blockers

The following risks must be mitigated before release:

- Cross-user data access
- Permission bypass
- SQL execution vulnerabilities
- Platform identity corruption
- AI safety violations

---

# Notes

The Risk Register should be reviewed before implementation begins and before production release.

New risks identified during implementation must be added here.
