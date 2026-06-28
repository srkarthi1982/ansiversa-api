# Resume Builder Backend Story

## Purpose

Resume Builder gives authenticated users a persistent resume authoring workflow
around projects, sections, section items, preview, and readiness review. The
backend owns the resume structure and item payloads while preserving the
existing production resume table shape.

## Workflow

The API supports a Projects -> Sections -> Items -> Preview -> Review workflow.
Projects select a template and default status. Sections belong to projects and
define ordered resume areas. Items belong to sections and store flexible JSON
payload data. Preview assembles a selected or default project with enabled
sections and items. Review summarizes readiness across the user's resume data.

## User Journey

A user creates a resume project, adds or enables sections, adds ordered items
inside those sections, opens preview to inspect the assembled resume, and opens
review to check completion and readiness metrics.

## Database Design

Resume Builder uses the existing isolated resume database tables:

* `ResumeProject`
* `ResumeSection`
* `ResumeItem`

`ResumeProject` is owner-scoped with `userId`. `ResumeSection` belongs to a
project and stores section key, order, and enabled state. `ResumeItem` belongs
to a section and stores ordered JSON data. Deleting a project cascades sections
and items.

## API Design

The router is mounted at `/api/v1/resume-builder`. Dashboard returns projects,
sections, items, preview, and review in one startup payload. Dedicated endpoints
support project, section, and item CRUD. Preview accepts optional `projectId`;
when omitted, the backend chooses the default/latest project. Review returns
counts, completion rate, ready project count, and recent items.

Create and update schemas are separate. Section and item create payloads carry
their parent IDs, while update payloads only include fields the backend permits
changing.

## Shared Components Used

The backend follows the shared Ansiversa FastAPI module pattern: isolated
database session, SQLAlchemy models, Pydantic schemas, thin routes,
service-owned logic, current-user auth, and owner-scoped access checks.

## Performance Considerations

The main query patterns are owner-scoped project lists, project-to-section
lookups, section-to-item lookups, preview assembly, and review summaries.
Project, section, and item parent columns are indexed. Flexible item JSON is
stored as text and is not indexed.

## Current Status

The backend implementation is approved live at version `1.0.0`. The parent
Apps catalog stores Resume Builder as `active` with `launchStatus = live`.

## Known Limitations

V1 stores structured resume content and preview data. It does not generate AI
rewrites, export PDFs, manage file uploads, or provide job-specific scoring.

## Future Enhancements

Future versions may add AI rewriting, PDF export, job-tailored variants,
template expansion, and Portfolio Creator integration.

## Current Implementation

Current version: `1.0.0`

Implemented:

* Owner-scoped resume projects
* Ordered resume sections
* Ordered resume items with flexible data payloads
* Dashboard, preview, and review APIs
* Project, section, and item create/update/delete workflow
* Current-state story documentation
