# LinkedIn Bio Optimizer

## Purpose

LinkedIn Bio Optimizer helps professionals manage LinkedIn profile inputs, reusable bio templates, and saved optimized bio versions for different career goals.

## Workflow

The V1 workflow moves through profiles, templates, and versions. Profiles store the user's professional context, current headline, current bio, optimized bio, keywords, tone, and language. Templates provide reusable structures by industry and career level. Versions preserve optimized headlines and bios with change summaries.

## User Journey

A signed-in user creates a LinkedIn profile workspace, records the current bio and career target, adds reusable templates, and saves optimized versions as the bio evolves.

## Database Design

The app uses an isolated `LINKEDIN_BIO_OPTIMIZER_DATABASE_URL` database. Tables are `LinkedInProfiles`, `BioTemplates`, and `BioVersions`. All records include `ownerId` and `platformId`. Versions use an indexed `profileId` foreign key so history remains attached to the profile workspace.

## API Design

The module is mounted at `/api/v1/linkedin-bio-optimizer`. Dashboard and list endpoints return lightweight summaries. Detail endpoints return complete editable records. Create and update DTOs are separate for profiles and templates. Versions support create, list/detail, and delete because they represent immutable saved history snapshots in V1.

## Shared Components Used

The backend follows shared FastAPI routing, auth dependency, SQLAlchemy session timing, Pydantic schema, and isolated Alembic migration patterns used by Ansiversa mini apps.

## Performance Considerations

Phase-1 indexes cover owner-scoped profile lists, template filters by industry and career level, profile-linked version history, and recent-update ordering. Large bio and template text fields are excluded from text indexes.

## Current Status

The backend V1 foundation is approved live at version `1.0.0`. The parent Apps catalog export stores LinkedIn Bio Optimizer as `active` with `launchStatus = live`.

## Known Limitations

The backend stores manual optimization records only. Bio versions are intentionally immutable in V1: users create a new version instead of editing an existing snapshot. The backend does not generate AI bio text, score LinkedIn profiles, or publish changes to LinkedIn.

## Future Enhancements

Future versions may revisit editable versions if business requirements change, and may add AI-assisted bio generation, keyword scoring, headline suggestions, profile import, and exportable bio variants.

## Current Implementation

Current implementation includes isolated database configuration, models, schemas, service functions, authenticated routes, migration files, overview metadata, and module story documentation.
