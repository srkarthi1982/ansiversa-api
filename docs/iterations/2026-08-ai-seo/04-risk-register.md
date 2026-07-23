# Iteration 2 AI SEO Risk Register

| ID | Risk | Level | Mitigation | Status |
|---|---|---|---|---|
| SEO-R01 | Public structured data claims capabilities users cannot see | Critical | Human/machine parity and current-truth validation | Open |
| SEO-R02 | Internal, personal, restricted, or future information is published | Critical | Visibility default-deny, allowlisted fields, secret/privacy scans | Open |
| SEO-R03 | A second knowledge pipeline creates drift | High | Existing registry remains the sole compiler/publisher source | Mitigated by architecture |
| SEO-R04 | SPA routes are weakly understood by non-rendering crawlers | High | Canonical rendering ADR before metadata implementation | Open |
| SEO-R05 | Duplicate web/API/artifact URLs split canonical signals | High | One canonical public URL per entity; API artifacts treated as projections | Open |
| SEO-R06 | `llms.txt` is treated as a universal standard | Medium | Label emerging status; standards-first acceptance criteria | Mitigated by architecture |
| SEO-R07 | Search-crawler permission silently authorizes model training | High | Separate search, training, and user-fetch policy | Open |
| SEO-R08 | Generated pages become thin or repetitive | High | Unique visible purpose/workflow/limitations; no mass keyword pages | Open |
| SEO-R09 | Stale marketing wording outruns implementation | Critical | Story/overview truth precedence, conflict failure, review dates | Open |
| SEO-R10 | Structured data is valid syntactically but unsupported/misleading | Medium | Approved schema profile plus vendor validators and visible-content parity | Open |
| SEO-R11 | IndexNow or provider submission leaks non-public URLs | High | Canonical public allowlist and dry-run evidence | Open |
| SEO-R12 | Ranking/citation claims are mistaken for engineering guarantees | High | Evidence tiers and explicit non-guarantee language | Mitigated by architecture |
| SEO-R13 | Crawler rules become stale | Medium | Versioned policy registry, primary sources, scheduled review | Open |
| SEO-R14 | AI answer monitoring violates provider terms or becomes brittle | High | Official tools, referral analytics, and governed manual sampling only | Open |
| SEO-R15 | AI SEO work changes Astra or App #101 boundaries | High | Separate iteration scope and regression assertions | Mitigated by architecture |
| SEO-R16 | Global source order silently overrides field authority | Critical | Field-specific authority matrix and compilation failure | Mitigated by SEO-002 proposal |
| SEO-R17 | One source reference masks mixed-origin list claims | High | Item-level provenance for every publishable claim list | Mitigated in Contract V1 candidate |
| SEO-R18 | Freshness timestamps imply review that never occurred | High | Review dates come from governed approval, never file modification time | Mitigated in Contract V1 candidate |
| SEO-R19 | Governance source paths leak into public projections | High | Only approved role/review date may be public; internal actors, paths, hashes, and notes remain governance-only | Mitigated in Contract V1 candidate |
| SEO-R20 | Invalid app handling either republishes bad truth or blocks unrelated safe updates | High | Separate entity/release validity with critical release blockers and approved optional-field isolation only | Mitigated in Contract V1 candidate |

---

# Release Blockers For Future Implementation

- personal/restricted/future content exposure;
- unsupported capability claims;
- absent canonical rendering decision;
- canonical URL conflicts;
- crawler policy without Product Owner approval;
- unvalidated schema or sitemap output;
- missing rollback;
- production changes without separate authorization; and
- claims that validation guarantees search or AI inclusion.
