# Proposal Writer Backend Story

## Purpose

Proposal Writer gives authenticated users a focused workspace for turning client
opportunities into structured proposal content. The backend owns proposal
projects, reusable proposal sections, full proposal drafts, and proposal
activity history for the `proposal-writer` mini app.

## Workflow

The API supports a Project -> Sections -> Drafts -> History workflow. Users
create a proposal project for a client, break the proposal into ordered
sections, assemble full drafts, and record important review or submission
events.

## User Journey

A user starts with a project, adds the business context, writes sections such
as scope and pricing, creates a draft proposal, then tracks review/submission
activity. Detail endpoints return full editable content only when the user
opens a saved record.

## Database Design

Proposal Writer uses an isolated mini-app database with four tables:

* `ProposalWriterProjects`
* `ProposalWriterSections`
* `ProposalWriterDrafts`
* `ProposalWriterHistory`

Every table is owner-scoped with `ownerId`. Child tables use parent foreign
keys, and long text fields stay out of summary responses.

## API Design

The router is mounted at `/api/v1/proposal-writer`. Dashboard/list responses
return summaries and previews only. Project, section, and draft detail
endpoints return the complete editable record. Update DTOs are separate from
create DTOs and do not accept create-only parent IDs.

## Shared Components Used

The backend follows the shared Ansiversa FastAPI module structure: isolated DB
session, SQLAlchemy models, Pydantic schemas, thin routes, service-owned logic,
current-user auth, and owner-scoped access checks.

## Performance Considerations

The initial migration includes indexes for owner list queries, status filters,
parent lookups, createdAt history ordering, updatedAt dashboard/list ordering,
and section sort ordering. Large text columns are not indexed.

## Current Status

V1 backend foundation is implemented for Astra review. The app remains
`comingSoon` and must not be promoted until review, manual verification, and
Partner approval are complete.

## Known Limitations

V1 does not generate AI content, export PDF/DOCX files, or send proposals. Users
manually author and manage proposal content.

## Future Enhancements

Future versions may add AI drafting, reusable proposal templates, client-side
exports, approval workflows, and integrations with CRM or invoicing modules.

## Version History

* 2026-06-28 - Created Proposal Writer V1 backend POC with isolated database,
  API contracts, indexes, routes, services, migration, and story documentation.
