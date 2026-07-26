# ASTRA-IMP-001 Constitution-To-Code Mapping

**Status:** Implemented; Pending Astra Source Review
**Task:** ASTRA-IMP-001
**Production Authorization:** Not approved
**Production:** Unchanged

---

# Mapping

| Constitutional source | Requirement area | Code support | Evidence/test support |
|---|---|---|---|
| ASTRA-002 | Local sufficiency and governed decision evidence | `DecisionReasonClass.LOCAL_SUFFICIENCY`; `GovernanceDecision.requirement_references`; `GovernanceDecision.evidence_references` | `test_governance_decision_supports_fail_closed_outcome` |
| ASTRA-003 | Context minimization | `MinimizationClass`; `BoundedEvidence.minimization_class`; restricted-evidence redaction rule | `test_bounded_evidence_accepts_metadata_only_review_evidence`; `test_restricted_evidence_requires_redaction_or_no_payload` |
| ASTRA-005 | Plan/version and approval evidence boundaries | `DecisionReasonClass.PLAN_VERSION_BOUNDARY`; `GovernanceDecision.version_marker`; `ApprovalState` validation | `test_governance_allow_cannot_bypass_pending_approval` |
| ASTRA-006 | Execution authority boundaries | `AuthorityClass.EXECUTION_BOUNDARY`; `DecisionReasonClass.EXECUTION_AUTHORITY_BOUNDARY`; disabled `execution_handoff` configuration | `test_configuration_is_disabled_by_default_and_fail_closed` |
| ASTRA-007 | Provider eligibility and advisory-response boundaries | `DecisionReasonClass.PROVIDER_ELIGIBILITY`; `DecisionReasonClass.PROVIDER_ADVISORY_RESPONSE`; disabled `provider_use` configuration | `test_configuration_is_disabled_by_default_and_fail_closed` |
| ASTRA-008 | Memory ownership and retrieval authorization | `DecisionReasonClass.MEMORY_OWNERSHIP`; `DecisionReasonClass.MEMORY_RETRIEVAL_AUTHORIZATION`; disabled `memory_use` configuration | `test_configuration_is_disabled_by_default_and_fail_closed` |
| ASTRA-009 | Adaptation activation boundaries | `DecisionReasonClass.ADAPTATION_ACTIVATION`; disabled `adaptation_use` configuration | `test_configuration_is_disabled_by_default_and_fail_closed` |
| ASTRA-010 | Constitutional precedence and fail-closed behavior | `DecisionReasonClass.CONSTITUTIONAL_PRECEDENCE`; `DecisionReasonClass.FAIL_CLOSED_DEFAULT`; fail-closed decision validation | `test_governance_decision_supports_fail_closed_outcome` |
| ASTRA-010 | Evidence minimization and audit integrity | `EvidenceIntegrityMetadata`; `EvidenceCorrectionMetadata`; `BoundedEvidence`; prohibited-material scanning | `test_evidence_rejects_secret_bearing_metadata_and_hidden_reasoning` |
| ASTRA-010 | Implementation and production separation | `ProductionAuthorizationState`; Stage 0 configuration validator | `test_configuration_rejects_runtime_or_production_authorization_inference` |
| ASTRA-IR-001 | Stage 0 bootstrap and conformance matrix | `ConstitutionalRequirement`; `ConstitutionalRequirementReference`; `ConstitutionalCoverageState` | `test_valid_contract_creation_and_requirement_reference`; `test_invalid_coverage_state_is_rejected` |

---

# Stable Requirement IDs

The Stage 0 implementation supports the initial ASTRA-IR-001 matrix IDs:

```text
AIR-CM-001
AIR-CM-002
AIR-CM-004
AIR-CM-005
AIR-CM-006
AIR-CM-007
AIR-CM-008
AIR-CM-009
AIR-CM-010
```

`AIR-CM-003` remains supported indirectly through future capability metadata
contracts and existing Assistant Tool Registry metadata. ASTRA-IMP-001 does not
change capability discovery behavior.
