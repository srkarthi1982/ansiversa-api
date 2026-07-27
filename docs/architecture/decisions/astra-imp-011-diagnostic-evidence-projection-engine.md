# ADR — ASTRA-IMP-011 Diagnostic Evidence Projection Engine

Status: Implemented; pending Astra source review.

Decision: introduce one Runtime-owned internal projection component using Option A correlation—explicit certified links only. Projections are partial when intent-to-plan or other relationships are unproven. Evidence integrity is structural by default, digest recomputation is not claimed, timelines are bounded at 50 without pagination, and every output remains internal and externally unauthorized.

This implements existing constitutional minimization, privacy, evidence, lifecycle, ownership, and fail-closed requirements. It does not amend ASTRA-001 through ASTRA-010 or reinterpret ASTRA-IR-001.
