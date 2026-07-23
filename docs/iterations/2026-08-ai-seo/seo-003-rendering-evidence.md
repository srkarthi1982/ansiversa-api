# SEO-003 Canonical Public Rendering Evidence

**Status:** Evidence collected
**Review date:** 2026-07-23
**Decision:** Not yet accepted
**Implementation:** Not authorized

---

# Decision Question

Where should Ansiversa generate canonical public HTML so that visible content,
metadata, structured data, canonical identity, and machine projections remain
faithful to the same approved public knowledge?

SEO-003 evaluates architecture. It does not authorize or implement rendering.

---

# Repository Evidence

## Current frontend

The `ansiversa` repository uses React 19, React Router 7, Vite 8,
`createRoot`, `createBrowserRouter`, and a client-only Vite build. Its single
`index.html` contains platform-wide metadata. Vercel sends ordinary routes to
that shell, and the application updates `document.title` after loading.

All 100 overview routes are registered from `APP_OVERVIEW_APPS`. The overview
page loads content in `useEffect` from
`/api/v1/content/metadata/overview/{app_key}` and renders nothing until that
request completes. Initial HTML therefore lacks route-specific overview truth.

The shell contains browser-dependent authentication, navigation, and document
behavior. Some guards exist, but the application has no server/pre-render entry
point.

## Current backend

The `ansiversa-api` repository already owns the Canonical AI Knowledge Registry,
public publisher, JSON and JSON-LD projections, metadata, `llms.txt`,
`llms-full.txt`, `ai-sitemap.xml`, robots hints, and deterministic validation.
It remains the compiler boundary. A frontend design must consume a governed
public projection; it must not parse lifecycle documents or import the internal
registry.

## Deployment topology

Frontend and backend are separate Vercel deployments and repositories. Machine
artifacts on the web domain are rewritten to the API domain, while ordinary web
routes fall back to the SPA shell.

A mutable build-time fetch from the latest production API is unsafe as the sole
handoff because it can silently combine unrelated revisions. The handoff must
be immutable and revision-pinned.

---

# External Primary Evidence

- [Vite SSR](https://vite.dev/guide/ssr) supports client and server builds but
  describes a low-level API and recommends higher-level tooling for production.
- [Vite production builds](https://vite.dev/guide/build.html) support static
  multi-page output; this repository currently builds one SPA entry.
- [React Router pre-rendering](https://reactrouter.com/how-to/pre-rendering)
  supports enumerated static paths, SPA fallback, and hybrid pre-render/SSR in
  Framework Mode.
- [React Router rendering strategies](https://reactrouter.com/start/framework/rendering)
  distinguish client rendering, pre-rendering, and server rendering.
- [Vercel Vite guidance](https://vercel.com/docs/frameworks/frontend/vite)
  documents SPA rewrites and multi-page deployment.
- [Vercel React Router guidance](https://vercel.com/docs/frameworks/frontend/react-router)
  documents supported React Router deployment.
- [Vercel Vite with Nitro](https://vercel.com/docs/frameworks/full-stack/vite-with-nitro)
  shows SSR and incremental regeneration are possible but add runtime
  architecture.

These sources establish feasibility, not suitability.

---

# Alternatives

| Option | Initial HTML | Private workflows | Operational cost | Evidence result |
|---|---|---|---|---|
| Client rendering only | Not canonical | Strong fit | Low | Reject candidate |
| Static generation for every route | Canonical | Poor fit | Low runtime | Reject candidate |
| Runtime SSR for every route | Canonical | Possible | High | Not preferred |
| Incremental regeneration | Canonical | Possible | Medium/high | Not justified now |
| Hybrid public pre-render + private CSR | Canonical where required | Strong fit | Bounded | Preferred candidate |

Client rendering does not satisfy raw-HTML validation. Static generation for
every route blurs public and authenticated boundaries. Runtime SSR adds a
renderer, caching, server-safe refactoring, and failure surface even though
public truth is not request-specific. Incremental regeneration adds invalidation
and staleness complexity without evidence that the fixed, approval-driven
catalog needs it.

Hybrid pre-rendering closes the public HTML gap while retaining client rendering
for private workflows. It still requires a deliberate build/router adaptation,
immutable artifact transport, route allowlisting, and hydration parity.

---

# Preferred Candidate

Use a hybrid architecture:

1. the backend compiler emits one immutable, versioned Public Rendering
   Manifest derived from Contract V1;
2. deployment orchestration supplies that exact artifact to the frontend build;
3. the frontend pre-renders only approved public routes;
4. visible content, head metadata, canonical URLs, and embedded structured
   projections read the same entity record during one build;
5. private and interactive routes retain client rendering; and
6. missing, stale, incompatible, or revision-mismatched input fails closed.

The manifest is a projection, not a second source. It carries a schema version,
registry/entity revision, generated-at value, route allowlist, and content
digest. A build must not silently consume mutable “latest” output.

An immutable CI artifact handoff is preferred. A committed generated snapshot
is acceptable only as a transitional transport with revision and drift checks.

---

# Required Controls

- One Contract V1 entity drives visible content and all projections.
- Presentation may not invent or enrich claims.
- Metadata and JSON-LD may not exceed visible approved truth.
- Hydration uses the revision that generated the HTML.
- Only manifest-allowlisted public routes are pre-rendered.
- Authenticated, personalized, internal, preview, and workflow routes are
  excluded.
- Critical contract, revision, route, schema, or digest failure blocks release.
- A failed release preserves the last approved deployment.
- Rollback restores the prior immutable HTML and manifest pair.
- Crawler, schema.org, redirect, archival, and sitemap policies remain owned by
  later tasks.

---

# Validation Matrix

| Area | Required evidence |
|---|---|
| Raw HTML | Unique title, description, canonical, H1, and approved truth without JavaScript |
| Parity | Visible content, metadata, JSON-LD, and machine artifacts share one revision |
| Coverage | Approved platform, category, and 100 app routes generated exactly once |
| Isolation | No private route or personal data enters the manifest or HTML |
| Hydration | No content mismatch or route-specific hydration warning |
| Failure | Missing/stale/incompatible input and compiler conflicts fail closed |
| Deployment | Cache topology and rollback preserve the HTML/manifest pair |
| Scale | Build time and artifact size remain bounded at production-shaped volume |

Actual migration, target deployment, performance, and rollback rehearsal belong
to implementation and verification.

---

# Conclusion

Hybrid governed pre-rendering is the preferred candidate. It is not accepted.

```text
Evidence                       Collected
Preferred candidate            Hybrid governed pre-rendering
Architecture decision          Proposed
SEO-003                        Discussing
Implementation                 Not authorized
Production                     Unchanged
```
