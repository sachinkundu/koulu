# Leaderboards — Technical Design Document

**Feature:** Leaderboards
**Module:** Gamification
**Status:** Draft
**Version:** 1.0
**Last Updated:** February 18, 2026
**Bounded Context:** Gamification

---

## 1. Overview

### 1.1 Summary

Leaderboards add a competitive social dimension to the existing Points & Levels system. They rank community members by points earned across three time horizons — 7-day, 30-day, and all-time — displayed as three side-by-side panels on a dedicated page. A compact sidebar widget on the Community feed surfaces 30-day rankings without navigation. Each leaderboard shows the top 10 members (with medals for the top 3) and reveals the current member's own rank if they fall outside that list.

This feature is a **read-only extension** of the Gamification context. It introduces no new write operations — all data derives from the existing `member_points` and `point_transactions` tables. The primary engineering challenge is computing rolling-window aggregations efficiently against the transaction log.

### 1.2 Goals

- Rank members by net points earned in rolling 7-day and 30-day windows, and by total accumulated points for all-time
- Display three leaderboard panels simultaneously on a dedicated page at `/leaderboards`
- Show the current member's own rank if they are outside the top 10 for any period
- Provide a compact 30-day top-5 widget in the Community feed sidebar
- Deliver all three leaderboards in a single API call under 400ms (p95)

### 1.3 Non-Goals

- Leaderboard caching or scheduled materialization (MVP computes on demand)
- Period tabs on mobile (MVP stacks panels vertically)
- Rank change deltas (e.g., "↑3 from last week")
- Admin ability to reset, freeze, or feature leaderboards
- Pagination beyond top 10 (no "load more" or full ranked list)
- Real-time updates (WebSocket push)
- Custom leaderboard periods or category-scoped leaderboards

---

## 2. Architecture

### 2.1 System Context

Leaderboards is a **read-only query layer** within the existing Gamification bounded context. It consumes data already written by the Points & Levels feature — no new event handlers or commands are needed.

```
┌──────────────────────────────────────────────────────────┐
│                   GAMIFICATION CONTEXT                     │
│                                                            │
│   ┌──────────────┐    ┌──────────────┐                     │
│   │ MemberPoints │    │  Level       │                     │
│   │ (existing)   │    │  Config      │                     │
│   │              │    │  (existing)  │                     │
│   │ - total_pts  │    │              │                     │
│   │ - level      │    │              │                     │
│   └──────┬───────┘    └──────────────┘                     │
│          │                                                 │
│          │ owns                                            │
│          ▼                                                 │
│   ┌──────────────┐         ┌─────────────────────────┐     │
│   │ Point        │─ read ─▶│ LEADERBOARD QUERIES     │     │
│   │ Transactions │         │ (NEW)                   │     │
│   │ (existing)   │         │                         │     │
│   └──────────────┘         │ - GetLeaderboards       │     │
│                            │ - GetLeaderboardWidget  │     │
│                            └──────────┬──────────────┘     │
│                                       │                    │
└───────────────────────────────────────┼────────────────────┘
                                        │ HTTP API
                                        ▼
                            ┌──────────────────────┐
                            │  Frontend Consumers   │
                            │  - LeaderboardsPage   │
                            │  - SidebarWidget      │
                            └──────────────────────┘
```

### 2.2 Component Architecture

The leaderboard feature adds a thin query layer within the existing Gamification hexagonal architecture. No new aggregates, entities, or domain events are introduced.

```
src/gamification/
├── domain/
│   └── repositories/
│       └── member_points_repository.py   # Add leaderboard query methods
├── application/
│   └── queries/
│       ├── get_leaderboards.py           # NEW — all three periods + your rank
│       └── get_leaderboard_widget.py     # NEW — 30-day top 5
├── infrastructure/
│   ├── persistence/
│   │   └── member_points_repository.py   # Implement leaderboard queries
│   └── api/
│       └── schemas.py                    # Add leaderboard response schemas
└── interface/
    └── api/
        ├── gamification_controller.py    # Add leaderboard endpoints
        └── dependencies.py              # Add handler factories
```

### 2.3 Design Decision: No New Aggregate

Leaderboards are a **derived read model**, not a domain concept with its own consistency rules. Ranking is a computation over existing data, not a business operation. Therefore:

- **No `Leaderboard` aggregate** — rankings are computed on the fly from existing `MemberPoints` and `PointTransaction` data
- **No new database tables** — queries aggregate over `member_points` and `point_transactions` using SQL
- **No new domain events** — leaderboard reads have no side effects

**Alternative considered:** A materialized `leaderboard_rankings` table updated periodically or via events. Rejected for MVP because:
- The source tables are small (one `member_points` row per member, transactions grow linearly)
- SQL aggregation over indexed transaction timestamps is well within performance targets for communities up to ~10K members
- A materialized view adds operational complexity (staleness, refresh scheduling, cache invalidation) not justified at MVP scale

This can be reconsidered in Phase 2 if performance targets are missed (see Section 15).

### 2.4 Integration Points

**Inbound:** None — Leaderboards adds no event subscriptions. All data comes from the existing points system.

**Cross-context read dependency (Identity):** Leaderboard entries need `display_name` and `avatar_url` from the `profiles` table (Identity context). Two approaches:

- **Option A (chosen): SQL JOIN at query time** — the leaderboard repository query JOINs `member_points` → `profiles` to fetch display data in a single roundtrip. This is a read-only cross-context JOIN, acceptable because leaderboard queries are in the infrastructure layer (not domain) and the profiles table is a stable, read-only dependency.

- **Option B (rejected): Separate API call to Identity** — call Identity's profile API for each leaderboard entry. Rejected because: N+1 HTTP calls for 10 entries, adds latency, adds coupling to Identity's API availability.

The JOIN violates strict bounded context table isolation but is the pragmatic choice for a read-only query. The domain layer remains clean — only the infrastructure query implementation touches the profiles table.

---

## 3. Technology Stack

### 3.1 Backend

No new dependencies. Uses existing stack:

- **SQLAlchemy (async)** — for leaderboard aggregation queries
- **FastAPI** — two new endpoints
- **Pydantic** — response schemas

### 3.2 Frontend

No new dependencies. Uses existing:

- **React + TypeScript + TailwindCSS** — component framework and styling
- **@tanstack/react-query** — data fetching hooks (established pattern in `useGamification.ts`)
- **react-router-dom** — `<Link>` for "See all leaderboards" navigation

### 3.3 Infrastructure

- **PostgreSQL** — no new tables; queries over existing `member_points`, `point_transactions`, and `profiles` tables
- No Redis caching in MVP

### 3.4 Date Formatting

The "Last updated" timestamp needs human-readable formatting (e.g., "Feb 15th 2026 2:11pm"). The frontend already has `date-fns` or `Intl.DateTimeFormat` available. If `date-fns` is not present, use `Intl.DateTimeFormat` (built-in, no dependency needed).

---

## 4. Data Model

### 4.1 No New Tables

Leaderboards derives all data from existing tables:

| Table | Owner | Used For |
|---|---|---|
| `member_points` | Gamification | `total_points`, `current_level`, `community_id`, `user_id` |
| `point_transactions` | Gamification | Period aggregation (sum points within rolling window) |
| `profiles` | Identity | `display_name`, `avatar_url` for each entry |
| `level_configurations` | Gamification | Level names for badge display |

### 4.2 Query Strategy

**Period leaderboards (7-day, 30-day):**

The core query pattern for rolling-window ranking:

1. JOIN `member_points` with `point_transactions` filtered by `created_at >= NOW() - interval`
2. SUM `point_transactions.points` per member (net points in period)
3. Apply GREATEST(0, sum) to floor negative net at zero
4. ORDER BY net points DESC, then display_name ASC (tie-breaker)
5. LIMIT 10 for top entries
6. Separately compute the current user's rank using a window function or subquery

**All-time leaderboard:**

Simpler — uses the materialized `total_points` column on `member_points` directly:

1. SELECT from `member_points` WHERE `community_id` = X
2. ORDER BY `total_points` DESC, `display_name` ASC
3. LIMIT 10

**Your rank computation:**

Use `ROW_NUMBER() OVER (ORDER BY ...)` window function to assign rank numbers to all members, then filter for the current user's row. This avoids a second full sort.

### 4.3 Index Usage

| Query | Index Used | Notes |
|---|---|---|
| All-time top 10 | `ix_member_points_community_total` | Already exists — `(community_id, total_points DESC)` |
| Period aggregation | `ix_point_transactions_member_created` | Already exists — `(member_points_id, created_at DESC)` |
| Community membership filter | `uq_member_points_community_user` | Already exists |

**No new indexes needed.** The existing index on `point_transactions(member_points_id, created_at DESC)` supports the time-windowed SUM efficiently.

### 4.4 Design Decision: Compute vs. Materialize

**Chosen: On-demand computation** — every leaderboard request runs the aggregation query.

**Rationale:**
- The `point_transactions` table grows linearly with community activity. For a community with 1,000 members averaging 5 actions/day, that's ~5,000 transactions/day or ~150K for a 30-day window. PostgreSQL handles this easily with the existing index.
- Eliminates cache invalidation complexity — results are always fresh
- The "Last updated" timestamp equals the query time (always "now")

**Tradeoff:** If communities grow to 50K+ members or transaction volume exceeds 1M/month, query times may exceed the 400ms target. At that point, introduce a materialized view refreshed on a schedule (see Section 15).

---

## 5. API Design

### 5.1 Endpoint Overview

| Method | Path | Auth | Purpose |
|---|---|---|---|
| GET | `/api/community/leaderboards` | Member | All three leaderboards + your rank |
| GET | `/api/community/leaderboards/widget` | Member | 30-day top 5 for sidebar widget |

Both endpoints use the auto-resolving `/community/` prefix (no `community_id` in URL), matching the established pattern in the existing gamification controller.

Explicit-community variants (`/communities/{id}/leaderboards`) are also registered for consistency with the existing dual-router pattern.

### 5.2 Request/Response Contracts

**GET `/api/community/leaderboards`**

Response:
```json
{
  "seven_day": {
    "entries": [
      {
        "rank": 1,
        "user_id": "uuid",
        "display_name": "Alice Admin",
        "avatar_url": "https://...",
        "level": 3,
        "points": 15
      }
    ],
    "your_rank": {
      "rank": 12,
      "user_id": "uuid",
      "display_name": "Current User",
      "avatar_url": "https://...",
      "level": 2,
      "points": 3
    }
  },
  "thirty_day": { ... },
  "all_time": { ... },
  "last_updated": "2026-02-18T14:16:00Z"
}
```

- `entries`: Array of up to 10 ranked members, ordered by rank
- `your_rank`: The current user's rank entry, or `null` if the user is already in the top 10 for that period
- `points`: Net points for period boards (7/30-day), total accumulated for all-time. Floored at 0 for period boards.
- `last_updated`: ISO 8601 UTC timestamp of when the data was computed (effectively "now" since computation is on demand)

**GET `/api/community/leaderboards/widget`**

Response:
```json
{
  "entries": [
    {
      "rank": 1,
      "user_id": "uuid",
      "display_name": "Alice Admin",
      "avatar_url": "https://...",
      "level": 3,
      "points": 60
    }
  ]
}
```

- Fixed to 30-day period, top 5 entries
- No `your_rank` (widget doesn't show it per PRD §3.7)
- No `last_updated` (widget doesn't show it)

### 5.3 Authentication & Authorization

All endpoints require authenticated session (existing JWT middleware). Community membership verified by the query itself — only members who belong to the community have `member_points` rows, and the current user must have one to compute their rank.

Non-members receive an empty response rather than 403 — the query simply returns no results for a user who isn't in the community's `member_points` table. This is a pragmatic choice: the community pages themselves are already gated.

### 5.4 Error Handling

| Error | HTTP Status | Handling |
|---|---|---|
| Not authenticated | 401 | Existing auth middleware |
| Community not found | 500 | Same as existing `_get_default_community_id` |
| Database query failure | 500 | Standard error response, logged |

No 403 for cross-community access because the auto-resolving `/community/` prefix always resolves to the user's own community. The explicit `/communities/{id}/leaderboards` variant should verify membership — follow the existing pattern used by other gamification endpoints.

### 5.5 API Design Decisions

**Single endpoint for all three periods vs. three separate endpoints:**

Chose a single endpoint returning all three leaderboards because:
- The page displays all three simultaneously — three parallel requests add latency and complexity
- The backend can batch the queries in a single database connection/transaction
- The response is small (~10 entries × 3 periods = 30 entries max)

**Separate widget endpoint vs. deriving from the full response:**

Chose a separate `/widget` endpoint because:
- The sidebar widget loads independently of the leaderboard page
- Widget callers should not pay for computing 7-day and all-time data they don't need
- The widget returns only 5 entries (not 10) and has no `your_rank`

---

## 6. Domain Model

### 6.1 No New Domain Objects

Leaderboards introduces no new aggregates, entities, value objects, or domain events. It is purely a query over existing domain data.

### 6.2 Extended Repository Interface

The `IMemberPointsRepository` interface gains two new query methods:

**`get_leaderboard(community_id, period, limit, current_user_id)`**
- Returns: top N entries for the period + the current user's rank entry (or None)
- Period is one of: `7day`, `30day`, `alltime`
- Each entry contains: rank, user_id, display_name, avatar_url, level, points

**`get_leaderboard_widget(community_id, limit)`**
- Returns: top N entries for the 30-day period
- Simplified version with no `your_rank` computation

These are read-only repository methods — they do not mutate state and do not produce domain events. They logically belong on the member points repository because they query the `member_points` and `point_transactions` tables that the repository already manages.

### 6.3 Design Decision: Repository vs. Dedicated Read Model

**Chosen:** Add query methods to the existing `IMemberPointsRepository`.

**Alternative considered:** A separate `ILeaderboardReadModel` interface implemented by a dedicated repository class. This would be more "pure" DDD (separating read models from aggregate repositories) but adds unnecessary indirection for two query methods that operate on the exact same tables. If leaderboard queries grow significantly more complex (e.g., materialized views, caching), extracting to a dedicated read model class would be warranted.

### 6.4 Leaderboard Period Enum

A new value object `LeaderboardPeriod` is useful to type-check the period parameter:

- `SEVEN_DAY` — 7 × 24 hours rolling window
- `THIRTY_DAY` — 30 × 24 hours rolling window
- `ALL_TIME` — total accumulated (no time filter)

Each variant knows its corresponding SQL interval (or `None` for all-time). This is a simple enum, not a full domain entity.

### 6.5 Invariants

Business rules enforced by the query logic:

1. **Net points floor at zero:** Period aggregations use `GREATEST(0, SUM(points))` — negative net never displayed
2. **Tie-breaking by display_name:** `ORDER BY points DESC, display_name ASC` ensures deterministic, alphabetical tie-breaking
3. **Sequential ranks:** `ROW_NUMBER()` (not `RANK()` or `DENSE_RANK()`) assigns unique sequential positions — no ties share a rank number
4. **Your rank exclusion:** `your_rank` is `null` when the user appears in the top N entries

---

## 7. Application Layer

### 7.1 Queries

**GetLeaderboardsQuery**
- Input: `community_id`, `current_user_id`
- Output: Three period results (each with entries + your_rank) + `last_updated` timestamp
- Orchestration: Calls the repository's `get_leaderboard()` three times (7-day, 30-day, all-time) and assembles the response. These three calls can be issued sequentially within a single database session — the overhead is minimal since they share the connection.

**GetLeaderboardWidgetQuery**
- Input: `community_id`
- Output: 5 entries for the 30-day period
- Orchestration: Single call to `get_leaderboard_widget()`

### 7.2 Query Flow

```
Browser → GET /community/leaderboards
             │
             ▼
      gamification_controller.py
             │
             ▼
      GetLeaderboardsHandler.handle()
             │
             ├─► repo.get_leaderboard(community_id, SEVEN_DAY, 10, user_id)
             ├─► repo.get_leaderboard(community_id, THIRTY_DAY, 10, user_id)
             ├─► repo.get_leaderboard(community_id, ALL_TIME, 10, user_id)
             │
             ▼
      Assemble LeaderboardsResult
             │
             ▼
      Return LeaderboardsResponse (JSON)
```

### 7.3 No Commands, No Event Handlers

Leaderboards is read-only. No commands to process, no events to handle, no state to write.

---

## 8. Integration Strategy

### 8.1 Cross-Context Read (Identity → Gamification)

The leaderboard query JOINs to the `profiles` table (Identity context) to get `display_name` and `avatar_url`. This is a **read-only infrastructure-level dependency** — the domain layer remains unaware of the Identity context.

The JOIN is in the SQL query executed by `SqlAlchemyMemberPointsRepository`, not in domain code. This is an explicit, documented deviation from strict context isolation, justified by:
- Avoiding N+1 API calls (10 entries × 3 periods = 30 profile lookups)
- The profiles table is stable (schema rarely changes)
- The dependency is one-directional and read-only

### 8.2 Frontend Integration

**LeaderboardsPage** — fetches from `/community/leaderboards` via a new `useLeaderboards()` hook, following the `react-query` pattern established by `useMemberLevel()` and `useLevelDefinitions()`.

**CommunitySidebar** — renders `LeaderboardSidebarWidget`, which fetches from `/community/leaderboards/widget` via a `useLeaderboardWidget()` hook. The widget handles its own loading/error states and renders nothing on failure (fail-silent to not disrupt the feed).

### 8.3 Failure Modes

| Failure | Impact | Handling |
|---|---|---|
| Leaderboard query slow (>400ms) | Degraded UX | Log warning, consider materialization in Phase 2 |
| Query returns no results | Empty leaderboard | Display "No rankings yet" message in panel |
| Widget API fails | Sidebar widget empty | Widget renders null — feed unaffected |
| Profile data missing (user has no profile row) | Entry shows null display name | Use fallback: `display_name` defaults to "Member" in query via `COALESCE` |

---

## 9. Security Design

### 9.1 Authentication

All leaderboard endpoints require valid JWT token (existing middleware). The BDD spec includes two security scenarios verifying 401 for unauthenticated access.

### 9.2 Authorization

Leaderboard data (member name, level, points) is considered public within the community. All authenticated community members can view all leaderboards. No admin-specific leaderboard features in MVP.

**Cross-community isolation:** The query is always scoped by `community_id` (derived from the authenticated user's community). A member cannot view another community's leaderboards. The BDD spec includes a scenario verifying 403 for cross-community access.

### 9.3 Query Safety

- All queries use SQLAlchemy parameterized statements — no SQL injection risk
- Time-range calculations (`NOW() - INTERVAL`) use server-side timestamps — client cannot manipulate the rolling window
- The `user_id` for "your rank" comes from the JWT token, not from request parameters — users cannot impersonate others

### 9.4 Data Exposure

The leaderboard response exposes: user_id, display_name, avatar_url, level, points. These are all considered public within the community (already visible on profiles and in the feed). No new sensitive data is exposed.

---

## 10. Performance & Scalability

### 10.1 Performance Targets

| Operation | Target (p95) | Justification |
|---|---|---|
| Full leaderboards API (3 periods) | < 400ms | PRD §8.3 |
| Sidebar widget API | < 200ms | PRD §8.3 |

### 10.2 Query Performance Analysis

**All-time query:** Single-table ORDER BY on `member_points.total_points DESC` using the existing `ix_member_points_community_total` index. Effectively an index scan + LIMIT 10. Expected: < 10ms for communities up to 100K members.

**Period queries (7/30-day):** JOIN `member_points` ↔ `point_transactions` with a `WHERE created_at >= NOW() - interval` filter. The `ix_point_transactions_member_created` index supports the time filter efficiently. The SUM aggregation groups by member_points_id. For a community with 1,000 members and 5,000 transactions/day:
- 30-day window: ~150K transactions scanned
- Expected: ~50-100ms with index support

**Your rank computation:** Uses `ROW_NUMBER()` window function over the same aggregation result set. PostgreSQL computes this in a single pass — no extra table scan.

**Total for full API call:** Three sequential queries × ~100ms = ~300ms. Comfortably within the 400ms target.

### 10.3 Optimization: Single vs. Three Queries

The three period queries could potentially be combined into a single query using conditional aggregation (`FILTER (WHERE ...)` on different intervals). However, this would:
- Make the query significantly more complex and harder to debug
- Scan the full transaction table for each row (no interval-specific index pruning)
- Be harder to optimize independently per period

Keeping three separate queries is simpler and allows PostgreSQL to use index-optimized scans per interval.

### 10.4 Caching Strategy

**MVP: No caching.** Each request computes fresh results.

**Future Phase 2 options if performance degrades:**
1. **Response-level caching** — Cache the full API response per community in Redis with a short TTL (30-60 seconds). Simple, effective, but introduces staleness.
2. **Materialized view** — A PostgreSQL materialized view refreshed every N minutes. Eliminates aggregation cost but adds infrastructure complexity.
3. **Application-level periodic refresh** — A background task computes leaderboard snapshots every 5 minutes and stores them in a dedicated table. Combines freshness control with fast reads.

### 10.5 Scalability Boundary

The current approach works well for communities up to ~10K members with moderate activity. Beyond that:
- Transaction volume in a 30-day window may exceed 1M rows
- The SUM aggregation becomes expensive even with indexes
- At that point, materialization (option 2 or 3 above) is recommended

---

## 11. Error Handling

### 11.1 Error Taxonomy

Leaderboards introduces no new domain exceptions. All errors are operational:

| Error | HTTP Status | User Message |
|---|---|---|
| Not authenticated | 401 | Redirect to login |
| Cross-community access | 403 | "You don't have permission" |
| Database error | 500 | "Failed to load leaderboard. Please try again." |
| No community found | 500 | Existing handler |

### 11.2 User Feedback

- **Loading:** Skeleton shimmer rows (5 per panel)
- **Empty:** "No rankings yet — be the first to earn points!" inside each panel
- **Error (leaderboard page):** Error message inside panel cards, page remains navigable
- **Error (sidebar widget):** Widget renders nothing — feed page continues normally

---

## 12. Testing Strategy

### 12.1 BDD Tests

The BDD spec (`tests/features/gamification/leaderboards.feature`) covers 17 scenarios:

| Category | Count | Scenarios |
|---|---|---|
| Happy path — 7-day leaderboard | 2 | Ranked members, point values with + prefix |
| Happy path — 30-day leaderboard | 1 | Rolled-up period points |
| Happy path — all-time leaderboard | 1 | Total accumulated points |
| Happy path — your rank | 3 | Outside top 10, inside top 10, zero points |
| Happy path — sidebar widget | 1 | 30-day top 5 |
| Edge cases | 6 | <10 members, ties, negative net, rolling window, all-time inclusion, zero points rank |
| Security | 3 | Unauthenticated (×2), cross-community access |

### 12.2 Unit Tests

Domain logic requiring unit coverage:
- `LeaderboardPeriod` value object — interval calculation, string representation
- Net points floor at zero — ensure GREATEST(0, sum) behavior

### 12.3 Integration Tests

- **Repository query tests** — verify ranking order, tie-breaking, rolling window boundaries, your rank calculation, negative net flooring
- **API endpoint tests** — response shape, authentication, authorization, empty community
- **Widget endpoint tests** — 5-entry limit, no your_rank, error silence

### 12.4 Frontend Tests

- **Component tests (Vitest):** LeaderboardPanel, LeaderboardRow, RankMedal, YourRankSection, LeaderboardSidebarWidget
- **Hook tests:** useLeaderboards, useLeaderboardWidget (mock API responses)

---

## 13. Observability

### 13.1 Logging (structlog)

| Event | Level | Fields |
|---|---|---|
| Leaderboard query completed | INFO | community_id, periods, duration_ms |
| Widget query completed | DEBUG | community_id, duration_ms |
| Leaderboard query slow (>300ms) | WARNING | community_id, duration_ms, period |

### 13.2 Metrics

| Metric | Type | Purpose |
|---|---|---|
| `gamification.leaderboard.query_duration` | Histogram | Track query performance by period |
| `gamification.leaderboard.request_count` | Counter | Track usage frequency |
| `gamification.leaderboard.widget_request_count` | Counter | Widget popularity |

### 13.3 Tracing (OpenTelemetry)

- Span: `gamification.get_leaderboards` — traces full API call including all three period queries
- Span: `gamification.get_leaderboard_widget` — traces widget API call
- Child spans: One per period query within the parent leaderboard span

---

## 14. Deployment Strategy

### 14.1 Migration Plan

No database migration needed. Leaderboards queries existing tables with existing indexes.

Deployment order:
1. Deploy backend with new query handlers and API endpoints
2. Deploy frontend with enhanced LeaderboardsPage, new components, and sidebar widget

### 14.2 Rollback Plan

Remove the two new API endpoints and revert the frontend to the current stub LeaderboardsPage (which only shows LevelDefinitionsGrid). No data cleanup needed — leaderboards is read-only with no persistent state.

### 14.3 Feature Flags

Not needed. The feature is additive:
- The `/leaderboards` page already exists (currently shows only level definitions)
- The sidebar widget is a new card added to `CommunitySidebar` — removing it restores the previous state
- No existing behavior is modified

---

## 15. Future Considerations

### 15.1 Phase 2 Enhancements

- **Leaderboard caching** — Redis or materialized views with configurable refresh interval. The current on-demand approach can be replaced transparently by changing the repository implementation.
- **Rank change delta** — "↑3 from last week" requires storing periodic snapshots of rank positions. Adds a new table.
- **Mobile period tabs** — Replace vertical stacking with tab navigation on mobile for a more compact view.

### 15.2 Known Limitations

- **No real-time updates** — Leaderboard data reflects the state at query time. A member who just earned points won't see the leaderboard update until the next page load/refresh.
- **Cross-context JOIN** — The profiles table JOIN is a pragmatic shortcut. If Identity's schema changes display_name or avatar_url columns, the leaderboard query breaks. This is documented and accepted as low-risk (profile schema is stable).
- **Sequential period queries** — The three period queries are executed sequentially. Parallel execution (using asyncio.gather) is possible but adds complexity for marginal gain (~100ms savings).

### 15.3 Technical Debt

- **No query abstraction** — The raw SQL query for period aggregation is in the repository. If leaderboard query patterns multiply (by category, by role, etc.), extracting a query builder would be warranted.
- **Display name fallback** — If a member has no profile row, `COALESCE` returns "Member" as a fallback. This is a band-aid — ideally all members have profiles.

---

## 16. Alignment Verification

See `docs/features/gamification/ALIGNMENT_VERIFICATION.md` for the complete PRD → BDD → TDD coverage mapping.

---

## 17. Appendices

### 17.1 File Checklist

**Backend — New files:**

```
src/gamification/
├── domain/
│   └── value_objects/
│       └── leaderboard_period.py                  # LeaderboardPeriod enum
├── application/
│   └── queries/
│       ├── get_leaderboards.py                    # GetLeaderboardsQuery + Handler
│       └── get_leaderboard_widget.py              # GetLeaderboardWidgetQuery + Handler
```

**Backend — Modified files:**

```
src/gamification/
├── domain/
│   └── repositories/
│       └── member_points_repository.py            # Add leaderboard query methods to interface
├── infrastructure/
│   ├── persistence/
│   │   └── member_points_repository.py            # Implement leaderboard SQL queries
│   └── api/
│       └── schemas.py                             # Add leaderboard response Pydantic schemas
└── interface/
    └── api/
        ├── gamification_controller.py             # Add GET leaderboards + widget endpoints
        └── dependencies.py                        # Add handler DI factories
```

**Frontend — New files:**

```
frontend/src/features/gamification/
├── components/
│   ├── LeaderboardPanel.tsx                       # Ranking card for one period
│   ├── LeaderboardPanel.test.tsx
│   ├── LeaderboardRow.tsx                         # Single ranked member row
│   ├── LeaderboardRow.test.tsx
│   ├── LeaderboardRowSkeleton.tsx                 # Shimmer placeholder
│   ├── RankMedal.tsx                              # Gold/silver/bronze emoji medal
│   ├── RankMedal.test.tsx
│   ├── YourRankSection.tsx                        # Divider + highlighted rank row
│   ├── YourRankSection.test.tsx
│   ├── LeaderboardSidebarWidget.tsx               # Compact 5-row widget
│   ├── LeaderboardSidebarWidget.test.tsx
│   ├── LeaderboardProfileCard.tsx                 # Profile card for page top
│   └── LeaderboardProfileCard.test.tsx
├── hooks/
│   ├── useLeaderboards.ts                         # Fetch all three periods
│   └── useLeaderboardWidget.ts                    # Fetch 30-day top 5
└── types/
    └── index.ts                                   # Add leaderboard TypeScript interfaces
```

**Frontend — Modified files:**

```
frontend/src/
├── pages/
│   └── LeaderboardsPage.tsx                       # Full layout with 3 panels + profile card
├── features/
│   ├── gamification/
│   │   ├── api/
│   │   │   ├── gamificationApi.ts                 # Add getLeaderboards(), getLeaderboardWidget()
│   │   │   └── index.ts                           # Re-export new API functions
│   │   └── hooks/
│   │       └── index.ts                           # Re-export new hooks
│   └── community/
│       └── components/
│           └── CommunitySidebar.tsx                # Add LeaderboardSidebarWidget
```

### 17.2 Dependencies

No new Python or JavaScript packages required.

### 17.3 References

- PRD: `docs/features/gamification/leaderboards-prd.md`
- BDD: `tests/features/gamification/leaderboards.feature`
- UI_SPEC: `docs/features/gamification/leaderboards-ui-spec.md`
- Points TDD: `docs/features/gamification/points-tdd.md`
- Context Map: `docs/architecture/CONTEXT_MAP.md`
- Domain Glossary: `docs/domain/GLOSSARY.md`
- Existing gamification controller: `src/gamification/interface/api/gamification_controller.py`
- Existing gamification models: `src/gamification/infrastructure/persistence/models.py`
- Existing repository: `src/gamification/infrastructure/persistence/member_points_repository.py`

---

## Approval

**Product Owner:** _________________
**Engineering Lead:** _________________
**Design Lead:** _________________

**Status:** Draft — Pending Review
