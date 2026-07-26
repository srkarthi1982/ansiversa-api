# ASTRA-IR-001 Implementation Risk Register

**Status:** Approved and Frozen
**Parent Constitution:** ASTRA-001 through ASTRA-010 Accepted / Frozen
**Implementation:** Not authorized
**Production:** Unchanged

---

# Risks

| ID | Risk | Level | Mitigation |
|---|---|---|---|
| IR-R01 | Engineers treat Constitution as advisory | Critical | Require rule-to-component conformance map |
| IR-R02 | Implementation begins from readiness docs | Critical | State that readiness does not authorize implementation |
| IR-R03 | Production activation follows implementation automatically | Critical | Preserve separate production authorization gate |
| IR-R04 | Component contracts leak authority | Critical | Define owner, authority, allowed inputs, outputs, and prohibited fields |
| IR-R05 | Governance Engine is built after behavior | Critical | Build governance foundation before high-impact behavior |
| IR-R06 | Audit evidence over-retains sensitive data | Critical | Require minimization, redaction, integrity, deletion, and export rules |
| IR-R07 | Provider path becomes default | Critical | Require local sufficiency and provider necessity before provider work |
| IR-R08 | Memory becomes app datastore | Critical | Require ownership and retrieval authorization gates |
| IR-R09 | Learning creates hidden drift | High | Require activation, conflict, drift, and user-control gates |
| IR-R10 | Execution bypasses owner services | Critical | Require owner-service acceptance and live authorization |
| IR-R11 | Existing Assistant implementation is treated as final Astra design | High | Treat existing systems as inputs and migration surfaces only |
| IR-R12 | Too many components ship together | High | Split work into separately authorized phases |
| IR-R13 | Tests focus on happy path only | High | Require failure, refusal, isolation, and negative conformance tests |
| IR-R14 | Observability leaks private data | High | Require redaction and evidence minimization |
| IR-R15 | Configuration enables production behavior accidentally | Critical | Require disabled-by-default controls and production gates |

---

# Blockers Before Implementation

- missing implementation scope;
- missing non-goals;
- missing component ownership;
- missing interface contracts;
- missing conformance map;
- missing certification gates;
- missing rollback or disablement expectations;
- missing source-level review package;
- missing Product Owner implementation authorization.
