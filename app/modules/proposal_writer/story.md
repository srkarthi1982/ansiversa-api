# Proposal Writer Backend Story

## Purpose

Proposal Writer gives authenticated users a focused workspace for turning client
opportunities into structured proposal content. The backend owns proposal
projects, reusable proposal sections, full proposal drafts, and proposal
activity history for the `proposal-writer` mini app without sharing a database
with other mini apps.

## Workflow

The API supports a Project -> Sections -> Drafts -> History workflow. Users
create a proposal project for a client, break the proposal into ordered
sections, assemble full drafts, and record important review or submission
events.

## User Journey

A user starts from the overview Explore CTA at `/proposal-writer/projects`,
creates a project with client context, writes sections such as scope and
pricing, creates a draft proposal, then tracks review/submission activity.
Detail endpoints return full editable content only when the user opens a saved
record.

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
create DTOs and do not accept create-only parent IDs. History creation validates
that a selected draft belongs to the selected project, and draft-linked history
infers the project when no explicit project is supplied.

## Shared Components Used

The backend follows the shared Ansiversa FastAPI module structure: isolated DB
session, SQLAlchemy models, Pydantic schemas, thin routes, service-owned logic,
current-user auth, and owner-scoped access checks.

## Performance Considerations

The initial migration includes indexes for owner list queries, status filters,
parent lookups, createdAt history ordering, updatedAt dashboard/list ordering,
and section sort ordering. Large text columns are not indexed.

## Current Status

The backend implementation is approved live at version `1.0.0`. The parent
Apps catalog stores Proposal Writer as `active` with `launchStatus = live`.
Overview metadata uses `Explore` as the CTA label and targets
`/proposal-writer/projects` as the first working workflow route.

## Known Limitations

V1 does not generate AI content, export PDF/DOCX files, or send proposals. Users
manually author and manage proposal content.

## Future Enhancements

Future versions may add AI drafting, reusable proposal templates, client-side
exports, approval workflows, and integrations with CRM or invoicing modules.

## Version History

V1 is the current implementation. It contains the isolated database, protected
API contracts, initial query-pattern indexes, routes, services, migration, and
current-state story documentation.
