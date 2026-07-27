# Astra Intent Resolution Engine

Status: ASTRA-IMP-009 implemented; source review pending. Production authorization is not approved and production is unchanged.

The runtime owns one lifecycle-bound `intent_resolution` component. It resolves an explicit bounded declared signal from the certified current turn; it never parses natural language, guesses hidden meaning, plans, executes, invokes providers, or creates authority.

## Contracts and deterministic rules

`AstraIntentRequest`, parameters, `AstraIntentResolution`, and structural health are frozen, extra-forbidden metadata contracts. Declared meaning must carry an immutable `AstraDeclaredIntentBinding` issued by the exact certified Conversation Context Engine. Its opaque token and stable ID are backed by a bounded private issuance registry; only the exact object issued by that engine is valid. Copies or reconstructions cannot reuse the token, while runtime/conversation/turn/request identity and declared fields are still checked before discovery. The action vocabulary is fixed:

| Declared action | Category | Planning candidate |
|---|---|---|
| `get_information` | information request | no |
| `lookup_capability` | capability lookup | no |
| `request_plan` | planning request | yes |
| `clarify` | clarification response | no |
| `administer` | administrative request | no |
| `system_request` | system request | no |
| unknown | unsupported | no |

Missing subject is ambiguous and requires clarification. Capability/planning categories require an exact discovered capability ID target. Planning eligibility is metadata only, never approval or authority.

## Flow and evidence

```text
validated declared signal -> current owned turn -> governed discovery
-> exact fixed rule -> plan-independent governance -> append governance evidence
-> immutable resolution -> append intent evidence -> bind dependency/sequence -> release
```

Non-ALLOW mapping is CLARIFY/clarification, DEFER/deferred, REFUSE/refused, CONTAIN/governance-blocked, FAIL_CLOSED/invalid. Evidence failure releases no resolution, does not bind the conversation dependency, and does not advance sequence.

Health begins degraded until a certified same-runtime conversation engine completes a successful resolution. It checks configuration, conversation, discovery, governance, planning availability, and evidence structurally, with no content/provider/execution metrics.
