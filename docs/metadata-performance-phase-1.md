# Metadata Performance Phase 1

Date: 2026-06-19

## Scope

Phase 1 improves metadata delivery without changing database storage. It does not
introduce JSON-to-BLOB storage, database gzip compression, or schema changes.

## API Changes

- HTTP compression is enabled globally with FastAPI `GZipMiddleware` and
  `minimum_size=1000`.
- Public metadata GET responses include:
  - `Cache-Control: public, max-age=3600`
  - weak ETags generated from stable JSON response content
- Requests with a matching `If-None-Match` receive `304 Not Modified`.
- Metadata content reads use a process-local in-memory cache:
  - key: metadata key, such as `home` or `overview:resume-builder`
  - TTL: 300 seconds
  - metadata PUT/DELETE updates invalidate or refresh the affected cached key

ETags are weak because the hash is calculated from the JSON content before any
HTTP transfer encoding, while compression middleware may alter the byte-level
wire representation.

## Frontend Changes

The existing Zustand stores already reused metadata during route navigation.
They now also persist content metadata and overview metadata in `sessionStorage`
for the current browser tab. Cached entries expire after one hour, matching the
API `Cache-Control` max-age.

## Measurement

Measurements used a local FastAPI test client with seeded
`overview:resume-builder` metadata. This avoids variability from the configured
database while preserving the route, response serialization, middleware, and
service cache behavior.

| Metric | Before | After |
| --- | ---: | ---: |
| Decoded payload size | 4,735 bytes | 4,735 bytes |
| Gzip transfer size | n/a | 1,766 bytes |
| Content-Encoding with `Accept-Encoding: gzip, br` | none | gzip |
| Cache-Control | none | public, max-age=3600 |
| ETag | none | weak SHA-256 ETag |
| 304 response payload | n/a | 0 bytes |
| First request duration | 45.932 ms | 21.750 ms |
| Repeated request duration | 2.498 ms | 2.959 ms |
| `If-None-Match` request duration | n/a | 1.941 ms |
| DB lookups across three after requests | n/a | 1 |

The representative compressed transfer was 62.7% smaller than the decoded JSON
payload. Route-level cache reuse also removed repeated database lookups inside
the five-minute API cache window.
