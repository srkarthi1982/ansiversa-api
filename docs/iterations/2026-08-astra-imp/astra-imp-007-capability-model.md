# ASTRA-IMP-007 Capability Model

**Status:** Implemented / Pending Astra Source Review
**Production Authorization:** Not approved

---

# Metadata Fields

Each capability record contains:

- `capability_id`;
- `capability_name`;
- `capability_type`;
- `owning_module`;
- `version`;
- `status`;
- `visibility`;
- `governance_reference`;
- `execution_authority`;
- `description`.

All fields are immutable after model construction.

---

# Capability Types

Current supported types:

- `platform_metadata`;
- `conversation_context`;
- `governance_metadata`;
- `evidence_metadata`.

These types describe metadata categories only.

---

# Status And Visibility

Status values:

- `available`;
- `disabled`;
- `deprecated`.

Visibility values:

- `public`;
- `authenticated`;
- `internal`.

Discovery excludes disabled and deprecated records by default.

---

# Execution Authority

`execution_authority` is metadata only.

Supported values:

- `none`;
- `metadata_only`;
- `owner_service_required`.

No value grants execution, planning, provider access, memory retrieval, or
production authority.
