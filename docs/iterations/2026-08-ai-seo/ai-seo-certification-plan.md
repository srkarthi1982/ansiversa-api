# AI SEO Certification Plan

**Status:** Complete
**Created:** 2026-07-23
**Scope:** Certification planning only
**Implementation:** Authorized
**Production:** Unchanged

---

# Certification Purpose

Certification proves that approved AI SEO architecture was implemented without
drift, private-data exposure, frontend instability, or production rollback
risk.

Certification is required before production behavior changes.

---

# Required Evidence

| Area | Evidence |
|---|---|
| Source inventory | allowlisted files, revisions, authority roles, reviewed dates |
| Parsing | deterministic parser fixtures for every source type |
| Normalization | no invented claims, no silent source-order override |
| Validation | severity report, conflict report, visibility report |
| Entity resolution | stable IDs, fixed 100-app boundary, no App #101 |
| Graph | SEO-004 profile validation and duplicate `@id` checks |
| Manifest | release ID, rollback base release ID, backend/frontend revisions, digests |
| Frontend | raw HTML, canonical links, metadata, visible parity, hydration parity |
| Deployment | smoke checks, headers, non-HTML machine artifacts, rollback rehearsal |
| Security | secret scan, private-content scan, no user-data reads |

---

# Automated Checks

Minimum future implementation checks:

```bash
python -m compileall app/modules/knowledge
python -m app.modules.knowledge.check_registry
python -m app.modules.knowledge.check_public
python -m app.modules.knowledge.verify_public_deployment --base-url https://ansiversa.com --api-base-url https://api.ansiversa.com
```

Future SEO-005 commands may be added only when implementation is authorized.

Frontend implementation certification should include:

```bash
npm run typecheck
npm run lint
npm run build
```

Playwright or equivalent browser verification is required for rendered route
behavior before approval.

---

# Manual Review

Astra review must verify:

- architecture boundaries were followed;
- no implementation invented new architecture;
- frontend is a consumer only;
- backend owns compiler output;
- production remains unchanged until approval;
- rollback evidence is complete.

Partner review must verify:

- implementation authorization was explicit;
- first app rollout is acceptable;
- visible public truth is correct;
- no production behavior changed before approval.

---

# App Certification

Each app rollout requires:

- source package approved;
- entity validation passed;
- graph bundle validated;
- page bundle validated;
- shadow comparison report reviewed where applicable;
- canonical route verified;
- visible copy matches approved current truth;
- page-local JSON-LD matches visible content;
- public render manifest compatibility passed;
- rollback evidence recorded.

No app is approved by implication.

---

# Certification Decision

Certification can approve production behavior only after an implementation
phase is complete, Astra review passes, and Karthik separately authorizes
promotion.

Current status:

```text
AI SEO Architecture     Complete
Implementation Review   Complete
Implementation          Authorized
Production              Unchanged
```
