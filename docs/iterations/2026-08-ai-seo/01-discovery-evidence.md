# Iteration 2 AI SEO Discovery Evidence

**Status:** Repository evidence collected
**Date:** 2026-07-23

---

# Repositories Reviewed

- `ansiversa-api`
- `ansiversa`

No production mutation or external provider submission was performed.

---

# Knowledge Coverage

Backend module-document inventory:

| Document | Modules found |
|---|---:|
| `market-study.md` | 100 |
| `destination.md` | 100 |
| `marketing.md` | 100 |
| `story.md` | At least all 100 app modules; additional platform/shared stories also exist |

The parent platform also maintains the four-document lifecycle.

---

# Current Compiler Inputs

The Canonical AI Knowledge Registry currently derives app knowledge from:

- frontend `APP_OVERVIEW_APPS` identity and routes;
- backend overview JSON;
- backend app `story.md`;
- backend app `destination.md`;
- platform story/content sources; and
- explicit aliases and category normalization.

`market-study.md` and `marketing.md` are not current compiler inputs.

This is a meaningful governance boundary. Adding either source requires an
approved field-level contract, conflict policy, visibility rules, and truth
validation.

---

# Existing Publishing Surface

Generated artifacts:

```text
robots.txt
llms.txt
llms-full.txt
ai-sitemap.xml
public-ai-knowledge.json
public-ai-jsonld.json
public-ai-metadata.json
```

They are served through backend root routes and public knowledge API routes.
The frontend host rewrites canonical public paths to the backend.

Validation currently checks:

- status and content type;
- SPA fallback rejection;
- canonical HTTPS URLs;
- 100 apps and 14 categories;
- JSON/XML/JSON-LD shape;
- forbidden content; and
- representative catalog identity.

---

# Frontend Page Evidence

The frontend uses one `index.html` containing:

- one platform title;
- one platform description;
- one platform Open Graph set; and
- no canonical link or route-specific JSON-LD.

The application shell changes `document.title` after route navigation. No
route-level metadata framework was found.

Consequences:

- initial HTML for different public routes is materially the same;
- route-specific descriptions and canonicals are absent from initial HTML;
- standalone JSON-LD is not colocated with visible page truth; and
- crawler success depends more heavily on JavaScript execution and separate
  artifacts than a standards-first architecture should require.

---

# Search And Discovery Evidence

Primary-source findings:

- Google states that ordinary crawlability, text content, canonical URLs,
  sitemaps, robots directives, and supported structured data remain relevant
  to AI features in Search.
- OpenAI distinguishes `OAI-SearchBot` discovery from `GPTBot` training
  controls.
- Perplexity distinguishes its search crawler from user-triggered retrieval and
  publishes crawler/IP guidance.
- Microsoft states that sitemaps remain foundational for Bing/Copilot and that
  IndexNow can notify supported engines of changed URLs.
- No mechanism guarantees indexing, ranking, citation, or answer inclusion.

Primary references:

- [Google: AI search guidance](https://developers.google.com/search/blog/2025/05/succeeding-in-ai-search)
- [Google: sitemap guidance](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap)
- [Google: robots meta controls](https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag)
- [OpenAI: publisher and developer FAQ](https://help.openai.com/en/articles/12627856-publishers-and-developers-faq)
- [Perplexity crawler guidance](https://docs.perplexity.ai/docs/resources/perplexity-crawlers)
- [Bing: sitemaps in AI-powered search](https://blogs.bing.com/webmaster/July-2025/Keeping-Content-Discoverable-with-Sitemaps-in-AI-Powered-Search)

---

# Evidence Conclusions

1. Reuse the existing knowledge registry and publisher.
2. Prioritize route-specific crawlable HTML and canonical metadata.
3. Treat standalone machine artifacts as projections, not substitutes for
   public pages.
4. Keep market research and future direction out of public current claims.
5. Integrate `marketing.md` only through approved, typed fields.
6. Separate search discovery, training permission, and user-triggered fetching.
7. Maintain provider rules as reviewed operational policy because crawler
   behavior changes.
8. Measure reach and factual accuracy without promising results.
