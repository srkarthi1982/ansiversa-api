# Portfolio Creator Backend Story

## Purpose

Portfolio Creator owns the persistent records required to build and publish a professional portfolio: profiles, projects, skills, and publish settings. The backend exists to keep portfolio content structured around user-owned profiles while allowing users to manage multiple portfolio variants.

## Workflow

The backend supports a Profiles -> Projects -> Skills -> Publish Settings workflow. Profiles are the parent records. Projects, skills, and publish settings belong to a profile and are also owner-scoped so access checks can protect both direct and child-record operations.

## User Journey

An authenticated user creates a portfolio profile, adds project highlights, records skills with categories and proficiency, and configures publish settings with visibility, slug, theme, and published state. The dashboard returns all records and counts needed by the frontend to show draft, published, featured, and public-facing readiness indicators.

## Database Design

The module uses four persistent tables:

* `PortfolioProfiles` stores display name, headline, summary, location, website, and profile status.
* `PortfolioProjects` stores project title, description, URL, role, position, and status under a profile.
* `PortfolioSkills` stores skill name, category, proficiency, and position under a profile.
* `PortfolioPublishSettings` stores visibility, slug, theme, and published state under a profile.

`ownerId` indexes support user-owned dashboard and list queries. `profileId` indexes support parent lookups for projects, skills, and publish settings. Position fields support user-facing ordering without indexing large text fields.

## API Design

The router exposes `/api/v1/portfolio-creator/dashboard` plus CRUD routes for profiles, projects, skills, and publish settings. Create schemas require parent `profileId` for child records. Update schemas allow editable fields and current status/publish changes, while service logic verifies ownership before changing records. Response models include display fields, parent profile names, counts, and publish state needed by the current frontend.

## Shared Components Used

The module uses the shared FastAPI module pattern: isolated database dependency, SQLAlchemy models, Pydantic schemas, thin routes, service-owned business logic, current-user authentication, owner-scoped access checks, and generated OpenAPI contracts for the frontend.

## Performance Considerations

The dashboard returns profile-centered portfolio data in one request because the frontend keeps a selected profile and needs coordinated project, skill, and publish state. Indexes match owner and profile-child query paths. Summary and description text fields are not indexed because V1 does not expose portfolio text search.

## Current Status

The backend implementation is live at version `1.0.0`. The parent Apps catalog stores Portfolio Creator as `active` with `launchStatus = live`.

## Known Limitations

V1 stores portfolio content and publish configuration only. It does not render public hosted portfolio pages, manage custom domains, upload media assets, track analytics, or import records from other career apps.

## Future Enhancements

Future versions may add public portfolio rendering, template previews, custom domains, media storage, Resume Builder import, analytics, and shareable portfolio URLs.

## Current Implementation

Current version: `1.0.0`

Implemented:

* Isolated Portfolio Creator backend module
* `PortfolioProfiles` persistence
* `PortfolioProjects` persistence
* `PortfolioSkills` persistence
* `PortfolioPublishSettings` persistence
* Dashboard route with portfolio counters
* Profile CRUD routes
* Project CRUD routes
* Skill CRUD routes
* Publish setting CRUD routes
* Owner-scoped service access
* Query-pattern indexes for owner and profile lookups
* Current-state story documentation
