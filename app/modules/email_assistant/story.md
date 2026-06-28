# Email Assistant Backend Story

## Purpose

Email Assistant owns the persistent records that support email planning and drafting: projects, drafts, templates, and history items. The backend exists to keep email work owner-scoped, structured, editable, and lightweight for list screens while preserving full draft and template content for detail workflows.

## Workflow

The backend supports a Projects -> Drafts -> Templates -> History workflow. Projects are the main planning records. Drafts belong to projects and may reference templates. Templates are owner-scoped reusable content patterns. History items can link to a project and optionally to a draft.

## User Journey

An authenticated user creates an email project with audience, goal, tone, and status. The user creates drafts with subject and body content, uses templates for reusable patterns, and records history events such as drafted, edited, sent, archived, or reviewed. The dashboard returns the user's email workspace plus counts for active projects, ready drafts, and templates.

## Database Design

The module uses four persistent tables:

* `EmailAssistantProjects` stores project title, audience, goal, tone, and status.
* `EmailAssistantDrafts` stores project-linked subject, body, optional template link, tone, and status.
* `EmailAssistantTemplates` stores reusable title, category, subject pattern, body pattern, and tone.
* `EmailAssistantHistory` stores action history with optional project and draft links, title, action type, and notes.

`ownerId` indexes support user-owned dashboard and list queries. `projectId`, `templateId`, and `draftId` indexes support parent lookups and detail navigation. Long body, body pattern, goal, and notes fields are not indexed because V1 does not provide text search.

## API Design

The router exposes `/api/v1/email-assistant/dashboard`, project CRUD, draft create/detail/update/delete, template create/detail/update/delete, and history create/detail/update/delete routes. Dashboard responses return projects plus lightweight draft, template, and history list items with previews. Detail endpoints return full draft body, template body pattern, and history notes only when the frontend opens the edit workflow.

## Shared Components Used

The module uses the shared FastAPI module pattern: isolated database dependency, SQLAlchemy models, Pydantic schemas, thin routes, service-owned business logic, current-user authentication, owner-scoped access checks, and generated OpenAPI contracts for the frontend.

## Performance Considerations

The dashboard avoids bloated payloads by using `bodyPreview`, `bodyPatternPreview`, and `notesPreview` for long content. Full content is fetched by detail endpoint only on demand. Indexes match current owner-list, project-child, template lookup, draft lookup, status-count, and detail-navigation query paths.

## Current Status

The backend implementation is live at version `1.0.0`. The parent Apps catalog stores Email Assistant as `active` with `launchStatus = live`.

## Known Limitations

V1 stores email planning and drafting records only. It does not send email, connect mailboxes, import contacts, automate campaigns, track opens/clicks, or generate AI-written drafts.

## Future Enhancements

Future versions may add AI drafting, mailbox integrations, contact imports, delivery tracking, scheduled follow-ups, CRM-style workflows, and cross-app handoff from professional mini apps.

## Current Implementation

Current version: `1.0.0`

Implemented:

* Isolated Email Assistant backend module
* `EmailAssistantProjects` persistence
* `EmailAssistantDrafts` persistence
* `EmailAssistantTemplates` persistence
* `EmailAssistantHistory` persistence
* Dashboard route with preview responses and counters
* Project CRUD routes
* Draft create, detail, update, and delete routes
* Template create, detail, update, and delete routes
* History create, detail, update, and delete routes
* Owner-scoped service access
* Query-pattern indexes for owner, project, template, and draft lookups
* Current-state story documentation
