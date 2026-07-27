# ADR: ASTRA-IMP-009 Intent Resolution Engine

Status: proposed for Astra source review. Date: 2026-07-27.

Implement one runtime-owned deterministic resolver between certified current-turn context and planning eligibility. Input is a declared action/subject/target/reference signal, not raw text. Fixed exact rules and governed discovered metadata produce immutable intent metadata. Ambiguity clarifies; unsupported signals do not guess.

The component does not create a planning request, plan, execution authority, owner authority, capability authority, or production authority. Planning eligibility is advisory metadata. No providers, prompts, models, memory, learning, API, persistence, frontend, deployment, or production activation is introduced.
