# Quiz API Migration Plan

Date: 2026-06-07

Purpose: map the current `Ansiversa-workspace/quiz` implementation to future
`ansiversa-api` routes before building the Quiz API module.

This is a documentation-only inspection pass. The existing Quiz Astro actions,
Astro DB, pages, and integrations remain the source of truth until
Astra/Karthikeyan approve each migration phase and cutover.

## Repositories Reviewed

- `Ansiversa-workspace/quiz/AGENTS.md`
- `Ansiversa-workspace/quiz/db/tables.ts`
- `Ansiversa-workspace/quiz/src/actions/*`
- `Ansiversa-workspace/quiz/src/stores/*`
- `Ansiversa-workspace/quiz/src/pages/*`
- `Ansiversa-workspace/quiz/src/pages/api/*`
- `Ansiversa-workspace/quiz/docs/app-spec.md`
- `Ansiversa-workspace/quiz/docs/dashboard-summary.md`

## Ownership Boundary

Quiz is a mini-app domain. Its data must remain isolated from the parent/global
database.

The future API module should follow this structure:

```text
app/modules/quiz/
  routes.py
  schemas.py
  service.py
  db.py
  models.py
```

Quiz-owned data:

- `Platform`
- `Subject`
- `Topic`
- `Roadmap`
- `Question`
- `QuestionVerification`
- `Result`
- `Bookmark`

Parent/global services that Quiz must reuse rather than duplicate:

- Authentication and current-user resolution
- Admin role checks
- User plans and entitlement decisions
- Notifications
- Parent dashboard/activity records
- Public and admin FAQs
- AI gateway
- Audit logs for API admin writes

The local Quiz `Faq` table and FAQ JSON routes should not be migrated into the
Quiz API module. Use the existing parent/global FAQ endpoints with
`appKey=quiz`.

## Current Quiz Data Flows

```text
Astro pages / Alpine stores
↓
Astro actions and local JSON endpoints
↓
Quiz Astro DB
```

Current protected user operations:

- List platforms, subjects, topics, and roadmaps.
- Fetch ten random questions for a selected taxonomy and difficulty.
- Save a completed result.
- List and toggle platform bookmarks.
- List enriched result history.
- Build a user-scoped Quiz dashboard summary.
- Search Quiz taxonomy and questions for FlashNote integration.

Current admin operations:

- List/create/update/delete platforms.
- List/create/update/delete subjects.
- List/create/update/delete topics.
- List/create/update/delete roadmaps.
- List/create/update/delete questions.
- Run AI-assisted question verification.

Current public operations:

- Read landing-page counts.
- Read top Academy and Professional platforms.

## Required User And Public Routes

All protected routes must reuse the existing API current-user dependency, which
accepts the approved cookie or bearer token. Clients must never send or select a
`userId`.

| Priority | Route | Auth | Current source | Purpose |
| --- | --- | --- | --- | --- |
| Phase 1 | `GET /api/v1/quiz/platforms` | User | `fetchPlatforms` | Paginated platform list with search, type, question-count, status, and sort filters. |
| Phase 1 | `GET /api/v1/quiz/subjects` | User | `fetchSubjects` | Paginated subject list filtered by platform, name, question count, and status. |
| Phase 1 | `GET /api/v1/quiz/topics` | User | `fetchTopics` | Paginated topic list filtered by platform, subject, name, question count, and status. |
| Phase 1 | `GET /api/v1/quiz/roadmaps` | User | `fetchRoadmaps` | Paginated roadmap list filtered by platform, subject, topic, name, question count, and status. |
| Phase 1 | `POST /api/v1/quiz/questions/random` | User | `fetchRandomQuestions` | Compatibility route that selects ten random questions for the requested taxonomy/level and optional excluded IDs. See the security decision below. |
| Phase 1 | `POST /api/v1/quiz/results` | User | `saveResult` | Compatibility route that stores the current user's result. See the security decision below. |
| Phase 1 | `GET /api/v1/quiz/results` | User | `/results` direct DB reads | Paginated current-user result history, newest first, enriched with taxonomy names and answer-review details. |
| Phase 1 | `GET /api/v1/quiz/results/{result_id}` | User | `/results` direct DB reads | Current-user-owned result detail with full answer review. Return `404` for missing or non-owned results. |
| Phase 1 | `GET /api/v1/quiz/bookmarks` | User | `listBookmarks` | List the current user's Quiz platform bookmarks. |
| Phase 1 | `PUT /api/v1/quiz/bookmarks/platforms/{platform_id}` | User | `toggleBookmark`, bookmark JSON route | Idempotently create a platform bookmark. |
| Phase 1 | `DELETE /api/v1/quiz/bookmarks/platforms/{platform_id}` | User | `toggleBookmark`, bookmark JSON route | Idempotently remove a platform bookmark. |
| Phase 1 | `GET /api/v1/quiz/dashboard-summary` | User | `fetchDashboardSummary` | Return the existing versioned `QuizDashboardSummaryV1` contract for the current user. |
| Phase 2 | `GET /api/v1/quiz/overview` | Public | `/` direct DB reads | Landing-page counts plus top Academy and Professional platforms. Do not return question content. |
| Phase 2 | `GET /api/v1/quiz/integrations/flashnote/sources` | User | `/api/flashnote/sources` | Search active roadmaps, topics, subjects, and platforms for FlashNote. |
| Phase 2 | `GET /api/v1/quiz/integrations/flashnote/questions` | User | `/api/flashnote/questions` | Return active Quiz questions in the FlashNote source contract, filtered by roadmap/topic/subject/platform and capped by limit. |

### Common List Query Contract

Taxonomy and admin list routes should use normal query parameters rather than
nested Astro action payloads:

```text
page
pageSize
q
status=all|active|inactive
sort
dir=asc|desc
platformId
subjectId
topicId
roadmapId
level=E|M|D
minQuestions
maxQuestions
type
```

Each list response should use one stable paginated shape:

```json
{
  "items": [],
  "total": 0,
  "page": 1,
  "pageSize": 10
}
```

## Recommended Secure Attempt Contract

The current compatibility flow has two issues:

1. `fetchRandomQuestions` returns the stored answer key, resolved answer, and
   explanation before the user submits.
2. `saveResult` accepts and stores a client-provided `mark`.

Before Quiz becomes a mobile-ready or untrusted-public-client API, replace the
compatibility question/result routes with a server-graded attempt lifecycle:

| Route | Auth | Purpose |
| --- | --- | --- |
| `POST /api/v1/quiz/attempts` | User | Validate taxonomy and entitlement, select questions, create an attempt, and return question text/options without answers. |
| `GET /api/v1/quiz/attempts/{attempt_id}` | User | Resume a current-user-owned incomplete attempt without exposing answers. |
| `POST /api/v1/quiz/attempts/{attempt_id}/submit` | User | Validate submitted selections, calculate the mark server-side, persist the result, and return answer review. |

Do not permanently support both contracts. Astra/Karthikeyan must approve
whether Quiz Integration V1 begins with compatibility routes or moves directly
to the secure attempt contract.

## Required Admin Routes

All admin routes must reuse `require_admin_user`, remain inside the Quiz module,
write Quiz-owned data only, and emit central audit events for writes.

| Entity | Routes | Current source |
| --- | --- | --- |
| Platforms | `GET/POST /api/v1/admin/quiz/platforms`, `GET/PATCH/DELETE /api/v1/admin/quiz/platforms/{platform_id}` | `platform.ts`, admin Platforms page/store |
| Subjects | `GET/POST /api/v1/admin/quiz/subjects`, `GET/PATCH/DELETE /api/v1/admin/quiz/subjects/{subject_id}` | `subject.ts`, admin Subjects page/store |
| Topics | `GET/POST /api/v1/admin/quiz/topics`, `GET/PATCH/DELETE /api/v1/admin/quiz/topics/{topic_id}` | `topic.ts`, admin Topics page/store |
| Roadmaps | `GET/POST /api/v1/admin/quiz/roadmaps`, `GET/PATCH/DELETE /api/v1/admin/quiz/roadmaps/{roadmap_id}` | `roadmap.ts`, admin Roadmaps page/store |
| Questions | `GET/POST /api/v1/admin/quiz/questions`, `GET/PATCH/DELETE /api/v1/admin/quiz/questions/{question_id}` | `question.ts`, admin Questions page/store |
| Verification | `POST /api/v1/admin/quiz/questions/verify` | `/api/quiz/verify-questions.json` |

Admin list routes require the same filtering and sorting currently used by the
admin stores. Admin create/update routes must validate the full hierarchy:

```text
Subject belongs to Platform
Topic belongs to Platform + Subject
Roadmap belongs to Platform + Subject + Topic
Question belongs to Platform + Subject + Topic + Roadmap
```

Deletion behavior must be explicitly approved. The API must return a clean
conflict response when dependent rows prevent deletion; it must not add
unapproved cascading deletes.

Question verification must be admin-only in the API. The current Quiz JSON
endpoint validates only an authenticated session, which is too broad for a
question-bank mutation workflow.

## Data Models And Storage

The Quiz API should connect to the Quiz-owned database through isolated
configuration such as:

```text
QUIZ_DATABASE_URL
TURSO_AUTH_TOKEN
```

Do not add Quiz tables to `ParentBase.metadata` or the parent/global Alembic
context.

Before implementation, choose and document an isolated Quiz migration strategy.
The existing production Quiz database contains approximately:

- 46 platforms
- 260 subjects
- 1,182 topics
- 13,386 roadmaps
- 1,448,521 deduplicated questions

The API must initially read/write the existing Quiz database in place. Do not
copy the question bank into the parent/global database.

Model compatibility requirements:

- Preserve current table names and numeric IDs.
- Preserve `Question` compact storage fields (`q`, `o`, `a`, `e`, `l`) at the
  database boundary unless a separately approved migration changes them.
- Expose descriptive API schema names such as `questionText`, `options`,
  `answerKey`, `explanation`, and `level`.
- Preserve result response JSON compatibility during migration.
- Preserve `qCount` as manual/informational in V1.
- Preserve version `1` of the existing dashboard summary response.

## Parent/Global Routes To Reuse

Do not create Quiz-owned replacements for these existing or planned parent API
capabilities:

| Quiz need | Use |
| --- | --- |
| Current user and session | Existing auth dependency and `/api/v1/auth/me` |
| Admin authorization | Existing `require_admin_user` dependency |
| Public Quiz FAQ | `GET /api/v1/faqs?appKey=quiz` |
| Admin Quiz FAQ | Existing `/api/v1/admin/faqs` routes with `appKey=quiz` |
| Notification reads | Existing `/api/v1/me/notifications...` routes |
| Parent dashboard activity | Approved parent dashboard/activity write contract when available |
| Notification creation | Approved central notification write/webhook contract when available |
| AI suggestions | Future approved central AI gateway; do not place provider logic in Quiz |
| Billing/plan changes | Parent/global billing and entitlement services |

## Entitlement And Security Rules

- Every protected route derives the user from the API auth dependency.
- Every result, attempt, bookmark, and summary read is scoped to the current
  user.
- Hard/difficult (`D`) question access must be checked server-side.
- The API must not trust client `isPaid`, plan, role, user ID, or mark values.
- Admin writes require `roleId = 1`.
- Random/attempt question responses must not expose answer keys before
  submission once the secure attempt contract is adopted.
- Result detail must not permit cross-user reads.
- Integration limits must be capped; FlashNote currently caps questions at 200.
- Question verification must cap batch size and retain verification history.
- Use explicit `400`, `401`, `402`, `403`, `404`, `409`, and `422` responses as
  appropriate.

## Integration And Side-Effect Rules

Saving a successful result currently triggers:

- Quiz activity push to the parent dashboard.
- "Quiz completed" notification.
- "Results saved" notification.

These side effects are best-effort today. During API migration:

- Result persistence must succeed or fail independently and transactionally.
- Notification/activity failures must not invalidate an already-saved result.
- Do not call legacy parent Astro endpoints from the final API design.
- Use approved API-owned service helpers or internal contracts when those
  parent write foundations exist.

## Proposed Implementation Phases

### Phase 0: Quiz Database Foundation

- Add isolated Quiz settings, engine/session, models, and migration strategy.
- Confirm API connectivity to the existing Quiz production database.
- Verify table counts and representative records without writes.
- Add module-specific OpenAPI extraction guidance for Quiz clients.

### Isolated Attempt Table Setup

The secure attempt lifecycle adds Quiz-owned `QuizAttempt` and
`QuizAttemptQuestion` tables. They are intentionally excluded from
`ParentBase.metadata` and parent Alembic. Quiz migrations use their own
`quiz_alembic.ini`, `quiz_alembic/` migration chain, and
`quiz_alembic_version` table. Autogeneration is restricted to the approved
API-managed attempt tables and must not propose changes to legacy Quiz tables.

After reviewing the target `QUIZ_DATABASE_URL`, apply the idempotent isolated
setup command:

```bash
alembic -c quiz_alembic.ini upgrade head
```

`QuizAttempt` stores current-user ownership, selected taxonomy, level, status,
two-hour configurable expiry, submission timestamp, and compatible result ID.
`QuizAttemptQuestion` stores the server-selected question IDs and their stable
order. Existing `Question` and `Result` tables remain compatible and in place.

### Phase 1: Core Quiz Integration V1

- Add protected taxonomy list routes.
- Add the approved question/attempt flow.
- Add result save/list/detail.
- Add Quiz bookmarks.
- Add Quiz dashboard summary.
- Keep existing Quiz Astro actions unchanged during parity verification.

### Phase 2: Public And Cross-App Reads

- Add public Quiz overview.
- Add FlashNote source and question integration routes.
- Move Quiz FAQ reads to the parent/global FAQ API.

### Phase 3: Admin Quiz API

- Add admin taxonomy CRUD.
- Add admin question CRUD.
- Add hierarchy validation, conflict handling, and audit events.
- Keep current admin Astro actions until API parity is manually verified.

### Phase 4: Verification And Parent Side Effects

- Add admin-only question verification after the central AI gateway contract is
  approved.
- Add approved central notification and dashboard activity writes.
- Remove legacy mini-app proxy/webhook calls only after parity is proven.

## Cutover Verification

Before replacing any Quiz Astro action, verify:

1. Platform, subject, topic, and roadmap lists match current filters, sorting,
   pagination, active status, and counts.
2. Quiz selection returns the expected ten-question pool.
3. Difficult level remains blocked for non-entitled users.
4. Empty question pools return a clean response.
5. Results are current-user scoped and preserve answer-review behavior.
6. Result history pagination and detail enrichment match the current Results
   page.
7. Bookmarks are current-user scoped and idempotent.
8. Dashboard summary matches `QuizDashboardSummaryV1`.
9. Admin hierarchy validation prevents inconsistent taxonomy/question writes.
10. Admin writes emit audit events.
11. FlashNote integration contracts remain compatible.
12. No Quiz route duplicates parent auth, FAQ, notification-read, AI, or billing
    ownership.
13. OpenAPI includes stable operation IDs and clean generated schemas.
14. Existing Quiz Astro actions remain available until the approved cutover.

## Open Decisions Requiring Approval

1. Use compatibility question/result routes first, or move directly to the
   secure attempt lifecycle.
2. Choose the isolated migration tool/context for the existing Quiz database.
3. Confirm whether taxonomy list routes remain authenticated or selected active
   taxonomy reads become public.
4. Confirm whether Quiz bookmarks remain Quiz-owned or later merge into a
   generic parent saved-items model.
5. Approve the parent notification/activity write contracts before moving side
   effects.
6. Approve the central AI gateway contract before migrating verification.

## Recommended First Implementation Task

Start with Phase 0 and read-only Phase 1 foundations:

```text
Quiz isolated database connection
Quiz SQLAlchemy models matching the existing schema
GET /api/v1/quiz/platforms
GET /api/v1/quiz/subjects
GET /api/v1/quiz/topics
GET /api/v1/quiz/roadmaps
```

This establishes the domain boundary and generated API contracts before
introducing question selection, result writes, or admin mutations.
