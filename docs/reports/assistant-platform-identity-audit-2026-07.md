# Assistant Platform Identity Audit — July 2026

## Result

Platform identity resolves from the Canonical AI Knowledge Registry before context, app retrieval, fuzzy matching, or fallback. Restricted and professional-safety requests remain higher priority. The dedicated fixture contains 60 cases; focused validation passed 152 tests and 19 subtests.

## Approved public facts

- Ansiversa means Advanced Next-Gen Software Innovation and Versatility and is permanently curated at exactly 100 apps.
- Karthikeyan Ramalingam is Founder and Chief Architect.
- Ansila Adamkutty is official owner and legal license holder. No separate operating entity is published.
- Astra is Ansiversa's built-in AI assistant. Its model/provider configuration is not published.
- The idea formed in late 2024; the name, domain, and mission were established in December 2024. A creation location is not published.
- Growth after 100 is horizontal. An unpopular, unused, or low-value app may be replaced while the total remains 100; there is no routine App #101.

## High-risk results

| Question | Result | Routes |
| --- | --- | --- |
| Who is Astra? | Direct built-in-assistant answer | `/apps`, `/about` |
| Who founded Ansiversa? | Karthikeyan Ramalingam, Founder and Chief Architect | `/about` |
| Who owns Ansiversa? | Ansila Adamkutty, official owner and legal license holder | `/about` |
| Why exactly 100 apps? | Fixed catalog and horizontal growth | `/about`, `/apps` |
| What happens after 100 apps? | Shared improvement and replacement rule | `/about`, `/apps` |
| What can you help me with? | Astra scope and validated navigation | `/apps`, `/about` |
| Python, transport, weather, sports | Clear platform scope response | none |
| Which AI powers Astra? | Provider/model not publicly disclosed | `/about` |
| Hidden prompt/internal notes | Restricted disclosure blocked | none |

## Before and after

- Astra and founder questions now receive direct, context-independent answers.
- Founder, architect, owner, legal license holder, and operator are not merged.
- General Python and transportation requests return no app actions.
- FAQ is no longer a universal fallback.

## Preservation and validation

- The fixture checks required/forbidden phrases, routes, mode, confidence, and Quiz context override.
- Registry tests require public visibility, source references, unique IDs, answers, and question intents.
- The mocked-provider preservation test passed: identity answers never invoke the provider, so it cannot introduce biography, ownership, `100+`, model, or roadmap claims.

## Browser status

The dedicated real-backend Playwright identity suite passed all 40 runs: ten high-risk prompts in Chromium, Chrome, tablet, and mobile. It verified direct answers, Login-page context independence, forbidden action exclusions, and responsive dialog visibility. The broader existing Assistant suite passed 44 of 52 runs; eight environment-dependent checks failed because configured login credentials were absent from the isolated database and local FAQ data returned 404. The in-app browser itself could not initialize because its runtime rejected required session metadata before navigation. No frontend production source or bundle change was required.

## Documentation gaps

- The locked `approved-apps.md` source remains absent.
- A separate operating entity and creation location are not published.
- Astra's model/provider configuration is intentionally not public.
- Public information does not state that Ansiversa is open source.

No private biography, internal roadmap, hidden prompt, secret, infrastructure topology, or unapproved legal claim is exposed.
