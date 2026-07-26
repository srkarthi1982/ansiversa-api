# ASTRA-IMP-003 Deterministic Rule Matrix

**Status:** Implemented; Pending Astra Source Review
**Task:** ASTRA-IMP-003
**Production Authorization:** Not approved
**Production:** Unchanged

---

# Rule Matrix

| Order | Condition | Outcome | Reason class | Failure posture |
|---|---|---|---|---|
| 1 | Configuration does not fail closed | `fail_closed` | `fail_closed_default` | `fail_closed` |
| 2 | Configuration ID/version mismatch | `fail_closed` | `constitutional_precedence` | `fail_closed` |
| 3 | Configuration feature is enabled | `fail_closed` | `fail_closed_default` | `fail_closed` |
| 4 | Constitutional compliance is unknown or conflicted | `fail_closed` | `fail_closed_default` | `fail_closed` |
| 5 | Safety is `unknown` or `prohibited` | `fail_closed` | `constitutional_precedence` | `fail_closed` |
| 6 | Approval is required, pending, or denied | `fail_closed` | `constitutional_precedence` | `fail_closed` |
| 7 | Consent is required, pending, or denied | `fail_closed` | `constitutional_precedence` | `fail_closed` |
| 8 | Owner authority is unverified, denied, or conflicted | `fail_closed` | `constitutional_precedence` | `fail_closed` |
| 9 | Production boundary lacks production approval | `fail_closed` | `constitutional_precedence` | `fail_closed` |
| 10 | Private-write or high-impact lacks explicit approval | `fail_closed` | `constitutional_precedence` | `fail_closed` |
| 11 | Provider use requested | `fail_closed` | `provider_eligibility` | `fail_closed` |
| 12 | Memory use requested | `fail_closed` | `memory_retrieval_authorization` | `fail_closed` |
| 13 | Adaptation use requested | `fail_closed` | `adaptation_activation` | `fail_closed` |
| 14 | Execution handoff requested | `fail_closed` | `execution_authority_boundary` | `fail_closed` |
| 15 | Bounded precedence fact blocks or is unknown | `fail_closed` | `constitutional_precedence` | `fail_closed` |
| 16 | Execution or production authority requested | `fail_closed` | `execution_authority_boundary` | `fail_closed` |
| 17 | External exposure requested | `defer` | `provider_eligibility` | `defer` |
| 18 | Public/private-read advisory or read-only request is otherwise valid | `allow` | `local_sufficiency` | requested failure posture |
| 19 | No deterministic allow path applies | `clarify` | `constitutional_precedence` | `clarify` |

---

# Precedence Model

The bounded fact model represents the accepted ASTRA-010 precedence order:

```text
1. Binding legal, regulatory, privacy, and security constraints
2. Accepted Astra Constitution
3. Product Owner-approved platform governance within the Constitution
4. Owning-service business and authorization truth
5. Accepted subordinate architecture and ADR contracts
6. Approved runtime policy
7. User intent and preference
8. Provider output or inferred behavior
```

ASTRA-IMP-003 does not implement a dynamic policy engine. It only evaluates
bounded deterministic facts supplied through the strict input contract.
