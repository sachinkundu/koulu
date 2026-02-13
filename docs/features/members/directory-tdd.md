# Member Directory - Technical Design Document

**Version:** 1.0
**Status:** Draft
**Last Updated:** February 13, 2026
**Bounded Context:** Community (with cross-context profile aggregation from Identity)
**Related Documents:**
- PRD: `docs/features/members/directory-prd.md`
- BDD Spec: `tests/features/members/directory.feature`
- Context Map: `docs/architecture/CONTEXT_MAP.md`

---

## 1. Overview

### 1.1 Summary

The Member Directory provides a browsable, searchable, filterable list of all active members within a community. It aggregates **membership data** (role, join date, active status) from the Community context with **profile data** (display name, avatar, bio) from the Identity context into a unified view. This is the first feature that requires cross-context data aggregation at query time.

### 1.2 Goals

- Provide a paginated, searchable directory of community members
- Support filtering by role and sorting by join date or name
- Aggregate Community membership and Identity profile data efficiently
- Follow established cursor-based pagination patterns (consistent with the feed)
- Enable discovery and navigation to existing profile pages

### 1.3 Non-Goals

- Online status indicators (requires WebSocket presence — Phase 2)
- Gamification data (points, levels, badges — depends on unbuilt Gamification context)
- "Most active" sorting (requires activity aggregation — Phase 2)
- Follow/unfollow from directory (separate feature)
- Direct message from directory (depends on unbuilt DM feature)
- Admin member management tools (separate admin feature)
- Real-time updates when members join/leave

---

## 2. Architecture

### 2.1 System Context Diagram

```
┌─────────────────────────────────────────────────────────┐
│                      Frontend                            │
│            MembersPage → useMembers hook                │
└──────────────────────┬──────────────────────────────────┘
                       │ GET /community/members
                       ▼
┌─────────────────────────────────────────────────────────┐
│                  Community Context                       │
│  ┌──────────────────────────────────────────────────┐   │
│  │            Member Directory Query                 │   │
│  │                                                    │   │
│  │  1. Verify requester membership                   │   │
│  │  2. Query community_members (filter, sort, page)  │   │
│  │  3. Fetch profiles for matched member user_ids    │   │
│  │  4. Merge membership + profile into response      │   │
│  └──────────┬────────────────────────┬──────────────┘   │
│             │                        │                   │
│             ▼                        ▼                   │
│  ┌──────────────────┐    ┌──────────────────────────┐   │
│  │ community_members │    │   Identity Context       │   │
│  │     (table)       │    │   (profile read access)  │   │
│  └──────────────────┘    └──────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### 2.2 Component Architecture

**Hexagonal Architecture Layers:**

```
┌─────────────────────────────────────────────────────┐
│                   Interface Layer                    │
│  member_controller.py (new endpoint)                │
│  schemas.py (request/response models)               │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│                 Application Layer                    │
│  ListMembersQuery (query object)                    │
│  ListMembersHandler (orchestration)                 │
│  MemberDirectoryEntry (result DTO)                  │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│                   Domain Layer                       │
│  CommunityMember (existing entity)                  │
│  IMemberRepository (extended interface)             │
│  MemberRole (existing value object)                 │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│               Infrastructure Layer                   │
│  SqlAlchemyMemberRepository (extended impl)         │
│  Cross-context profile query (JOIN at infra level)  │
└─────────────────────────────────────────────────────┘
```

### 2.3 DDD Design

**Aggregate:** CommunityMember (existing, owned by Community context)

The directory is a **read-only query** — it does not create or modify any aggregates. It reads from the CommunityMember aggregate and enriches with data from the Identity context's Profile.

**Cross-Context Strategy:**
The key architectural decision is how to join membership data with profile data.

- **Option A: Application-level join** — Query members, then batch-fetch profiles via Identity service
- **Option B: Infrastructure-level SQL JOIN** — Join `community_members` and `profiles` tables directly
- **Chosen: Option B** — Both tables live in the same PostgreSQL database. A SQL JOIN is simpler, more performant, and avoids N+1 queries. This is acceptable because it's a read-only query and both contexts share the same database in our monolithic deployment. The JOIN happens in the infrastructure layer only — the domain layer remains unaware.

**Design Decision: Why infrastructure JOIN is acceptable here**
- This is a query (read), not a command (write) — no invariant violations
- Both contexts share the same database (single deployment)
- The alternative (application-level join) would require fetching all profiles in-memory, making search-by-name impossible at the database level
- Name search MUST happen in SQL for performance (ILIKE on profiles.display_name)
- The repository method returns a flat DTO, not domain entities from another context

### 2.4 Integration Points

| Integration | Direction | Mechanism |
|------------|-----------|-----------|
| Identity Context (Profile) | Read | SQL JOIN at infrastructure layer |
| Frontend | Inbound | REST API (GET /community/members) |
| Existing Profile Page | Navigation | Frontend link to /profile/:userId |

---

## 3. Technology Stack

### 3.1 Backend

No new dependencies. Uses existing stack:

| Technology | Purpose | Already in Project |
|-----------|---------|-------------------|
| FastAPI | REST API endpoint | Yes |
| SQLAlchemy (async) | Database queries with JOIN | Yes |
| Pydantic v2 | Request/response schemas | Yes |
| structlog | Structured logging | Yes |

### 3.2 Frontend

No new dependencies. Uses existing stack:

| Technology | Purpose | Already in Project |
|-----------|---------|-------------------|
| React 18 | UI components | Yes |
| TanStack Query (React Query) | Data fetching, infinite scroll | Yes |
| TailwindCSS | Styling | Yes |
| react-router-dom | Navigation, new /members route | Yes |

### 3.3 Justification

No new libraries needed. The existing stack fully supports:
- Cursor-based pagination (pattern established in feed)
- Infinite scroll (TanStack Query `useInfiniteQuery` used in feed)
- Responsive list layout (TailwindCSS)
- Cross-table queries (SQLAlchemy JOINs)

---

## 4. Data Model

### 4.1 Conceptual Schema

The directory reads from two existing tables — no new tables are created.

```
┌──────────────────────────┐       ┌──────────────────────────┐
│   community_members      │       │       profiles           │
├──────────────────────────┤       ├──────────────────────────┤
│ user_id (PK, FK)         │───────│ user_id (PK, FK)         │
│ community_id (PK, FK)    │       │ display_name             │
│ role                     │       │ avatar_url               │
│ joined_at                │       │ bio                      │
│ is_active                │       │ location_city            │
└──────────────────────────┘       │ location_country         │
                                   │ is_complete              │
                                   └──────────────────────────┘
```

**Join Key:** `community_members.user_id = profiles.user_id`

### 4.2 Query Design

The directory query combines:
- **From community_members:** user_id, role, joined_at, is_active
- **From profiles:** display_name, avatar_url, bio

**Filtering logic:**
- `is_active = true` (always applied — deactivated members hidden)
- `community_id = :community_id` (scoped to requesting community)
- `role = :role` (optional — when role filter is applied)
- `display_name ILIKE '%:search%'` (optional — when name search is applied)

**Sorting logic:**
- "most_recent" → `community_members.joined_at DESC` (default)
- "alphabetical" → `profiles.display_name ASC` (nulls last)

### 4.3 Indexes

Existing indexes that serve this query:
- `community_members` composite PK on `(user_id, community_id)` — membership lookup
- `profiles` PK on `user_id` — profile JOIN

**New indexes to consider (if performance requires):**
- `community_members(community_id, is_active, joined_at DESC)` — optimizes the default sorted listing
- `profiles(display_name)` with `gin_trgm_ops` — optimizes ILIKE search

**Design Decision:** Start without additional indexes. The member directory serves communities of up to 10,000 members. PostgreSQL handles ILIKE on 10k rows efficiently. Add indexes only if p95 latency exceeds the 200ms target.

### 4.4 Pagination

**Cursor-based pagination** (consistent with existing feed):
- Encode `{"offset": N}` as base64 JSON cursor
- Request `limit + 1` rows to determine `has_more`
- Return `cursor` and `has_more` in response
- Default page size: 20

### 4.5 Total Count

The response includes `total_count` (total active members matching current filters). This:
- Powers the "Members (42)" badge in the navigation tab
- Uses `SELECT COUNT(*)` as a separate query (avoids impacting main query performance)
- Is acceptable for communities up to 10k members

---

## 5. API Design

### 5.1 Endpoint Overview

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/community/members` | List community members with search, filter, sort, pagination |

Single endpoint — all functionality via query parameters.

### 5.2 Request Contract

```
GET /community/members?search=alice&role=admin&sort=alphabetical&limit=20&cursor=eyJvZmZzZXQiOjIwfQ==
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| search | string (optional) | — | Case-insensitive partial match on display_name |
| role | string (optional) | — | Filter by role: "admin", "moderator", "member" |
| sort | string | "most_recent" | Sort order: "most_recent" or "alphabetical" |
| limit | integer | 20 | Page size (1–100) |
| cursor | string (optional) | — | Base64-encoded pagination cursor |

### 5.3 Response Contract

**Success (200 OK):**

```json
{
  "items": [
    {
      "user_id": "uuid",
      "display_name": "Alice Admin",
      "avatar_url": "https://...",
      "role": "admin",
      "bio": "Community founder and coach",
      "joined_at": "2025-11-15T10:00:00Z"
    }
  ],
  "total_count": 42,
  "cursor": "eyJvZmZzZXQiOjIwfQ==",
  "has_more": true
}
```

**Field details:**

| Field | Type | Notes |
|-------|------|-------|
| user_id | UUID | Member's user ID (for navigation to /profile/:userId) |
| display_name | string or null | From profile; null if profile incomplete |
| avatar_url | string or null | From profile; null if not set |
| role | string | "admin", "moderator", or "member" |
| bio | string or null | From profile; null if not set |
| joined_at | datetime (ISO 8601) | When the member joined the community |
| total_count | integer | Total members matching current filters |
| cursor | string or null | Pagination cursor; null if no more pages |
| has_more | boolean | Whether more members exist beyond this page |

### 5.4 Error Responses

| Status | Condition | Body |
|--------|-----------|------|
| 401 Unauthorized | No valid auth token | `{"detail": "Not authenticated"}` |
| 403 Forbidden | Authenticated but not a community member | `{"detail": "Not a member of this community"}` |
| 422 Unprocessable Entity | Invalid query params (bad role value, limit out of range) | Standard FastAPI validation error |

### 5.5 Design Decisions

**Why a single flat endpoint (not nested)?**
- Consistent with the existing `/community/posts` pattern (flat list with query params)
- All filtering is via query parameters, keeping the URL clean
- Avoids premature nesting (no `/community/{id}/members` yet — single-community MVP)

**Why `total_count` in every response?**
- Required for the "Members (42)" badge in the navigation tab
- Negligible cost for communities under 10k members
- Avoids a separate endpoint just for the count

**Why not offset-based pagination?**
- Cursor pagination is the established pattern (feed uses it)
- More resilient to concurrent member additions/removals between page loads

---

## 6. Domain Model

### 6.1 Aggregates

**CommunityMember** (existing — no changes to the aggregate)
- Consistency boundary: A user's membership in a specific community
- The directory only reads this aggregate; it does not modify it

### 6.2 Value Objects

**MemberRole** (existing)
- Enum: ADMIN, MODERATOR, MEMBER
- Used for filtering in the directory query
- Role badges on cards derived from this value

No new domain value objects needed. The directory is a pure read concern.

### 6.3 Domain Events

No domain events produced or consumed. The directory is a read-only query — it doesn't trigger side effects.

### 6.4 Invariants

- Only active members are visible (`is_active = true`)
- Members can only view directories of communities they belong to
- Private profile data (email, settings) is never exposed

### 6.5 Design Patterns

**CQRS (Query Side):** The directory is a query handler — no commands, no state changes. This aligns with the CQRS-lite approach used by the feed (GetFeedHandler is query-only, CreatePostHandler is command-only).

**DTO Projection:** The query returns a flat DTO (MemberDirectoryEntry) that combines fields from two contexts. This is NOT a domain entity — it's a read model projection for the API layer.

---

## 7. Application Layer

### 7.1 Query

**ListMembersQuery** — Represents the user's intent to browse the directory.

Fields:
- `community_id` — Which community to list
- `requester_id` — Who is making the request (for authorization)
- `search` — Optional name search term
- `role` — Optional role filter
- `sort` — Sort strategy ("most_recent" or "alphabetical")
- `limit` — Page size
- `cursor` — Pagination cursor

### 7.2 Handler

**ListMembersHandler** — Orchestrates the directory query.

Responsibilities:
1. Verify the requester is an active member of the community (authorization)
2. Delegate to the repository for the filtered, sorted, paginated query
3. Build cursor for next page
4. Return a result object with items, total count, cursor, and has_more flag

### 7.3 Result

**MemberDirectoryResult** — Returned by the handler.

Fields:
- `items: list[MemberDirectoryEntry]` — Flat DTOs with merged membership + profile data
- `total_count: int` — Total matching members
- `cursor: str | None` — Next page cursor
- `has_more: bool` — Whether more pages exist

**MemberDirectoryEntry** — Individual member DTO.

Fields:
- `user_id`, `display_name`, `avatar_url`, `role`, `bio`, `joined_at`

### 7.4 Flow

```
Controller → ListMembersQuery → ListMembersHandler
    │                                    │
    │                          1. Check membership
    │                          2. Call repository.list_directory(...)
    │                          3. Call repository.count_directory(...)
    │                          4. Build cursor, determine has_more
    │                                    │
    │                          ◄─ MemberDirectoryResult
    │
    ◄── Serialize to JSON response
```

---

## 8. Integration Strategy

### 8.1 Cross-Context Communication

**Pattern: Infrastructure-level JOIN (Query Side Only)**

The Community context needs profile data (display_name, avatar_url, bio) from the Identity context. Options considered:

| Option | Pros | Cons |
|--------|------|------|
| A: Application-level batch fetch | Clean context separation | N+1 risk, can't search by name in SQL, complex |
| B: Infrastructure SQL JOIN | Simple, performant, enables ILIKE search | Couples at DB level |
| C: Materialized view | Best read performance | Operational complexity, staleness |

**Chosen: Option B** — Infrastructure SQL JOIN.

Rationale:
- Single PostgreSQL database (monolith) — no network boundary to cross
- Name search requires database-level ILIKE — impossible with app-level join
- The JOIN is confined to the repository implementation (infrastructure layer)
- Domain layer never imports from Identity — the boundary is respected at the conceptual level
- If contexts are split into separate databases later, this is the ONE repository method to refactor

### 8.2 External Services

None. No external services needed for the directory MVP.

### 8.3 Anti-Corruption Layer

Not needed at this stage. The infrastructure JOIN returns a flat DTO that maps directly to the API response. If contexts are later separated into microservices, an ACL would translate the Identity service's profile response into the Community context's expected shape.

### 8.4 Failure Modes

| Failure | Impact | Handling |
|---------|--------|----------|
| Database connection failure | Directory unavailable | Return 500; frontend shows error with retry button |
| Profile table missing data | Member shown with null display_name/avatar/bio | LEFT JOIN ensures members always appear; frontend renders placeholders |
| Invalid cursor | Pagination breaks | Catch decode error, fall back to offset 0 |

---

## 9. Security Design

### 9.1 Authentication

- All directory requests require a valid JWT token (existing `CurrentUserIdDep`)
- Expired/invalid tokens return 401 Unauthorized
- Consistent with all other Community endpoints

### 9.2 Authorization

- The requester must be an active member of the community
- Checked via `IMemberRepository.get_by_user_and_community()` (existing method)
- Non-members receive 403 Forbidden

### 9.3 Input Validation

| Parameter | Validation |
|-----------|------------|
| search | Max 100 characters; stripped of leading/trailing whitespace |
| role | Must be one of: "admin", "moderator", "member" (or omitted) |
| sort | Must be one of: "most_recent", "alphabetical" |
| limit | Integer between 1 and 100 |
| cursor | Base64-encoded string; gracefully falls back on decode failure |

### 9.4 Data Protection

**Exposed fields (public):**
- display_name, avatar_url, bio, role, joined_at, user_id

**Never exposed:**
- email, password hash, private settings, location (not in directory MVP), social links
- The query only SELECTs the specific columns needed — no wildcard SELECT

### 9.5 Threat Model

| Threat | Mitigation |
|--------|------------|
| Enumeration (scraping all members) | Rate limiting on the endpoint (existing middleware); pagination limits batch size |
| SQL injection via search param | Parameterized queries (SQLAlchemy handles this) |
| Unauthorized access to private communities | Membership check before any data is returned |
| Information disclosure | Only public profile fields are SELECTed and returned |

---

## 10. Performance & Scalability

### 10.1 Performance Targets

| Metric | Target |
|--------|--------|
| API response time (p95) | < 200ms |
| First page render (frontend) | < 1 second |
| Subsequent page loads (infinite scroll) | < 500ms |

### 10.2 Caching Strategy

**No caching for MVP.** Rationale:
- Target response time (<200ms) is achievable with direct SQL queries for communities up to 10k members
- Member data changes infrequently but unpredictably (profile updates, new members)
- Cache invalidation complexity isn't worth it at this scale

**Phase 2 consideration:** If communities exceed 10k members or latency targets are missed, add:
- Redis cache for total_count (invalidated on member join/leave)
- Query result caching with short TTL (30s) for popular pages

### 10.3 Query Optimization

**Main listing query:**
- JOIN `community_members` and `profiles` on `user_id`
- WHERE clause filters reduce row set early
- ORDER BY uses indexed columns (joined_at is part of the table, display_name on profiles)
- LIMIT + 1 pattern for has_more detection (no separate COUNT for pagination)

**Count query:**
- Separate `SELECT COUNT(*)` with same WHERE filters
- Runs in parallel with the main query (or could be combined via window function if needed)

### 10.4 Scalability Considerations

| Scale | Approach |
|-------|----------|
| < 1k members | No optimization needed |
| 1k–10k members | Current design handles this well |
| 10k–100k members | Add composite index on `(community_id, is_active, joined_at)` and trigram index for ILIKE search |
| 100k+ members | Consider materialized view or denormalized read model |

---

## 11. Error Handling

### 11.1 Error Taxonomy

| Error | Type | HTTP Status |
|-------|------|-------------|
| Not authenticated | Infrastructure (auth) | 401 |
| Not a community member | Domain (authorization) | 403 |
| Invalid query parameters | Validation | 422 |
| Database failure | Infrastructure | 500 |
| Invalid cursor format | Validation (graceful) | 200 (fallback to page 1) |

### 11.2 User-Facing Messages

| Error | Frontend Display |
|-------|-----------------|
| 401 | Redirect to /login |
| 403 | "You don't have permission to view this directory." |
| 422 | Should not occur (frontend sends valid params) |
| 500 | "Failed to load members. Please try again." with retry button |

### 11.3 Error Recovery

- Invalid cursor: Silently reset to offset 0 (server-side)
- Network error: Frontend shows error with retry; previously loaded members remain visible
- Empty results: Show "No members found. Try adjusting your search or filters."

---

## 12. Testing Strategy

### 12.1 BDD Tests

The BDD spec (`tests/features/members/directory.feature`) covers 18 scenarios:
- 13 happy path: browsing, search, filter, sort, pagination, combined filters
- 2 validation/error: no results for search, no results for filter
- 3 edge cases: deactivated members excluded, incomplete profiles, empty search, single member
- 3 security: unauthenticated access, non-member access, no private data exposed

### 12.2 Unit Tests

| Area | What to Test |
|------|-------------|
| ListMembersHandler | Authorization check, delegation to repository, cursor building, has_more logic |
| Query validation | Invalid role values, limit bounds, cursor decode |
| MemberRole filtering | Correct enum mapping from string params |

### 12.3 Integration Tests

| Area | What to Test |
|------|-------------|
| Repository JOIN query | Correct profile data merging, NULL handling for incomplete profiles |
| Search ILIKE | Case-insensitive matching, partial matching, empty string |
| Sorting | Most recent order, alphabetical order, null display_name handling |
| Pagination | Correct offset, has_more flag, cursor encode/decode roundtrip |
| Authorization | Membership check returns 403 for non-members |

---

## 13. Observability

### 13.1 Logging

| Event | Level | Key Fields |
|-------|-------|------------|
| `member_directory_list` | INFO | community_id, requester_id, search, role, sort, result_count |
| `member_directory_unauthorized` | WARN | community_id, requester_id |
| `member_directory_error` | ERROR | community_id, error |

### 13.2 Metrics

| Metric | Type | Purpose |
|--------|------|---------|
| `member_directory_requests_total` | Counter | Usage tracking |
| `member_directory_response_time_ms` | Histogram | Performance monitoring |
| `member_directory_search_usage` | Counter | Track search adoption (success criteria: >15% of visits) |

### 13.3 Tracing

- Span for the handler: `ListMembersHandler.handle`
- Child span for the database query: `member_repository.list_directory`
- Child span for the count query: `member_repository.count_directory`

---

## 14. Deployment Strategy

### 14.1 Migration Plan

No database migrations needed. The directory reads from existing tables (`community_members`, `profiles`). No new tables, columns, or indexes for MVP.

### 14.2 Rollback Plan

- Feature is additive (new endpoint + new frontend route)
- Rollback: Remove the `/members` route from frontend navigation; endpoint remains harmless
- No data migrations to reverse

### 14.3 Feature Flags

Not needed. The feature is a new page/endpoint — it doesn't modify existing behavior. The navigation tab can be added in a single deployment.

---

## 15. Future Considerations

### 15.1 Phase 2 Enhancements

- **Level badges:** Once Gamification context is built, enrich directory entries with level/points. This adds another JOIN to the query (or a denormalized field on the member).
- **"Most active" sorting:** Requires an activity score, likely computed by Gamification and stored as a denormalized field.
- **Online status:** Requires WebSocket presence tracking — a new infrastructure service.
- **Follow/unfollow:** Requires a Relationship domain concept.

### 15.2 Known Limitations

- **No real-time updates:** Directory shows state as of the last fetch. A member joining won't appear until the next page load.
- **Search is basic:** ILIKE search on display_name only. No fuzzy matching, typo tolerance, or full-text search.
- **Single community:** No community_id parameter in the URL — uses the default community (consistent with the rest of the MVP).

### 15.3 Technical Debt

- **Infrastructure JOIN:** The SQL JOIN between `community_members` and `profiles` couples two bounded contexts at the database level. If contexts are later separated into microservices, this repository method must be refactored into an application-level aggregation with an anti-corruption layer.
- **Count query:** Running a separate COUNT query may become expensive for very large communities. Could be replaced with an approximate count or a cached count.

---

## 16. Alignment Verification

See `docs/features/members/ALIGNMENT_VERIFICATION.md` for the complete PRD → BDD → TDD traceability matrix.

---

## 17. Appendices

### 17.1 File Checklist

**Backend (new files):**
- `src/community/application/queries/list_members_query.py` — Query object
- `src/community/application/handlers/list_members_handler.py` — Query handler
- `src/community/application/dtos/member_directory_entry.py` — Result DTO

**Backend (modified files):**
- `src/community/domain/repositories/member_repository.py` — Add `list_directory()` and `count_directory()` methods to interface
- `src/community/infrastructure/persistence/member_repository.py` — Implement the new methods with JOIN
- `src/community/interface/api/member_controller.py` — Add `GET /community/members` endpoint
- `src/community/interface/api/schemas.py` — Add request/response schemas
- `src/community/interface/api/dependencies.py` — Add handler dependency if needed

**Frontend (new files):**
- `frontend/src/features/members/api/memberApi.ts` — API client function
- `frontend/src/features/members/hooks/useMembers.ts` — TanStack Query hook with `useInfiniteQuery`
- `frontend/src/features/members/types/members.ts` — TypeScript interfaces
- `frontend/src/features/members/components/MemberCard.tsx` — Individual member card
- `frontend/src/features/members/components/MemberList.tsx` — Vertical list container with infinite scroll
- `frontend/src/features/members/components/MemberFilters.tsx` — Search, role pill tabs, sort controls
- `frontend/src/features/members/components/index.ts` — Barrel export
- `frontend/src/pages/MembersPage.tsx` — Page component

**Frontend (modified files):**
- `frontend/src/App.tsx` — Add `/members` route and navigation tab

**Tests:**
- `tests/features/members/step_defs/test_directory.py` — BDD step definitions
- `tests/features/members/conftest.py` — Test fixtures

### 17.2 Dependencies

No new packages to add. All functionality is covered by existing dependencies.

### 17.3 References

- [TanStack Query useInfiniteQuery](https://tanstack.com/query/latest/docs/framework/react/guides/infinite-queries) — Infinite scroll pagination
- [SQLAlchemy Joined Eager Loading](https://docs.sqlalchemy.org/en/20/orm/queryguide/relationships.html) — Cross-table queries
- [FastAPI Query Parameters](https://fastapi.tiangolo.com/tutorial/query-params/) — Endpoint design
- Existing patterns: `src/community/application/handlers/get_feed_handler.py`, `frontend/src/features/community/hooks/usePosts.ts`
