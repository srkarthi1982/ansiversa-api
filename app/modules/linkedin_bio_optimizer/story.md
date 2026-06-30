# LinkedIn Bio Optimizer

## Status

- Key: `linkedin-bio-optimizer`
- Slug: `linkedin-bio-optimizer`
- Launch status: `comingSoon`
- Version: `null`

## Purpose

LinkedIn Bio Optimizer helps professionals manage LinkedIn profile inputs, reusable bio templates, and saved optimized bio versions for different career goals.

## V1 Backend Foundation

- Dedicated isolated database: `LINKEDIN_BIO_OPTIMIZER_DATABASE_URL`
- Tables:
  - `LinkedInProfiles`
  - `BioTemplates`
  - `BioVersions`
- Authenticated CRUD endpoints under `/api/v1/linkedin-bio-optimizer`
- Summary/detail response split for large bio and template text
- Owner-scoped service operations using `ownerId`

## Notes

- `platformId` is stored on profile, template, and version records for LinkedIn-specific identity/context.
- The app remains in `comingSoon` until Partner approval.
