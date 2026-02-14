# Search — Technical Design Document

**Feature:** Search
**Version:** 1.0
**Last Updated:** February 13, 2026
**Status:** Draft
**PRD:** `docs/features/search/search-prd.md`
**BDD:** `tests/features/search/search.feature`
**UI_SPEC:** `docs/features/search/UI_SPEC.md`

---

## 1. Overview

### Summary

Add full-text search across community members and posts using PostgreSQL's built-in Full-Text Search (FTS) with `tsvector`/`tsquery` and GIN indexes. Expose via a single API endpoint and a dedicated search results page in the frontend with tabbed navigation.

### Goals

- Enable members to find people and discussions within their community via a header search bar
- Deliver search results in < 200ms (p95) for communities up to 10,000 members and 50,000 posts
- Provide stemming support (e.g., "running" matches "run") with zero additional infrastructure

### Non-Goals

- Elasticsearch or external search engine integration (deferred to Phase 3)
- Real-time as-you-type search / autocomplete (Phase 2)
- Comment search (Phase 2)
- Course/Lesson search (Phase 2)
- Search relevance ranking (MVP uses alphabetical for members, date for posts)
- Cross-community search (Phase 3)

---

## 2. Architecture

### System Context

```
┌──────────────┐     ┌─────────────────────────────────┐
│   Browser    │────▶│         FastAPI Application       │
│  (React SPA) │◀────│                                   │
└──────────────┘     │  ┌─────────────────────────────┐  │
                     │  │    Community Context          │  │
                     │  │                               │  │
                     │  │  ┌──────────┐  ┌──────────┐  │  │
                     │  │  │ Search   │  │ Existing │  │  │
                     │  │  │ Handler  │  │ Handlers │  │  │
                     │  │  └────┬─────┘  └──────────┘  │  │
                     │  │       │                       │  │
                     │  │  ┌────▼──────────────────┐   │  │
                     │  │  │  Search Repository    │   │  │
                     │  │  │  (queries both tables) │   │  │
                     │  │  └────┬──────────────────┘   │  │
                     │  └───────┼───────────────────────┘  │
                     │          │                           │
                     │  ┌───────▼───────────────────────┐  │
                     │  │   PostgreSQL                   │  │
                     │  │   ┌──────────┐ ┌───────────┐  │  │
                     │  │   │ profiles │ │   posts   │  │  │
                     │  │   │ +search_ │ │ +search_  │  │  │
                     │  │   │  vector  │ │  vector   │  │  │
                     │  │   │ +GIN idx │ │ +GIN idx  │  │  │
                     │  │   └──────────┘ └───────────┘  │  │
                     │  └───────────────────────────────┘  │
                     └─────────────────────────────────────┘
```

### Component Architecture

Search is a **read-only, query-side concern** within the Community context. It introduces no new aggregates, no new domain entities, and no write operations. It sits entirely in the application and infrastructure layers.

```
Community Context
├── domain/                    (NO CHANGES)
├── application/
│   ├── queries/
│   │   └── search_query.py        ← NEW: SearchQuery dataclass
│   ├── handlers/
│   │   └── search_handler.py      ← NEW: SearchHandler
│   └── dtos/
│       └── search_results.py      ← NEW: SearchResult DTOs
├── infrastructure/
│   └── persistence/
│       ├── models.py              ← MODIFY: add tsvector columns
│       └── search_repository.py   ← NEW: FTS query implementation
└── interface/
    └── api/
        ├── search_controller.py   ← NEW: GET /community/search
        ├── schemas.py             ← MODIFY: add search schemas
        └── dependencies.py        ← MODIFY: add search deps
```

### Why Community Context (Not a New Search Context)

**Decision:** Keep Search within Community context for MVP.

**Rationale:**
- Both searchable content types (members and posts) are owned by Community context
- Search introduces no new aggregates or domain concepts — it's purely a query concern
- Creating a separate Search context would force cross-context queries for basic operations (violates the "friction" test from architecture skill)
- When Phase 2 adds Classroom search, we can evaluate whether a dedicated Search context makes sense as a read-model aggregator

**Alternative rejected:** Separate `Search` bounded context — would only have 1-2 query-side entities, violates the "too granular" anti-pattern.

### Why No Domain Layer Changes

Search is not a business domain concept — it's an infrastructure concern (how users find things). There are no invariants to enforce, no business rules to protect, no domain events to publish. The entire feature is:
1. Accept a query string (application layer)
2. Execute a full-text search against PostgreSQL (infrastructure layer)
3. Return formatted results (interface layer)

This is consistent with DDD guidance: not everything needs a domain model. Query-side operations often skip the domain layer entirely.

---

## 3. Technology Stack

### Backend

**PostgreSQL Full-Text Search (built-in)**
- **Purpose:** Indexed full-text search with stemming, ranking, and query parsing
- **Why:** Already deployed (no new infrastructure), GIN indexes provide fast lookups, stemming is automatic, well-documented with 20+ years of production use
- **Version:** PostgreSQL 14+ (already in use)
- **Documentation:** https://www.postgresql.org/docs/current/textsearch.html
- **Key functions:** `to_tsvector('english', text)`, `to_tsquery('english', query)`, `@@` operator for matching
- **Alternatives rejected:**
  - **`ILIKE` queries** — Current approach in member directory. No index support for leading wildcards (`%term%`), O(n) scan. Unacceptable for post body search at scale.
  - **Elasticsearch** — Best relevance scoring and features, but requires new infrastructure (deployment, data sync, monitoring). Overkill for MVP. Planned for Phase 3.
  - **pg_trgm extension** — Good for fuzzy/typo matching but less effective for natural language search. May supplement FTS in Phase 2.

**SQLAlchemy 2.0 (existing)**
- **Purpose:** ORM for building FTS queries
- **FTS support:** `func.to_tsvector()`, `func.to_tsquery()`, `type_.match()` via `TSVectorType`
- **Note:** SQLAlchemy does not have a dedicated `tsvector` column type — use `mapped_column(TSVECTOR)` from `sqlalchemy.dialects.postgresql`

**bleach (existing in project) or html.escape (stdlib)**
- **Purpose:** Sanitize search query input to prevent XSS
- **Approach:** Strip HTML tags from query before processing. Use `markupsafe.escape()` for any reflected output.

### Frontend

**React Query (existing: @tanstack/react-query)**
- **Purpose:** Data fetching with caching for search results
- **Pattern:** `useQuery` (not `useInfiniteQuery` — search uses offset pagination, not cursor)
- **Cache key:** `['search', communityId, query, type, page]`

**react-router-dom (existing)**
- **Purpose:** URL-based search state (`/search?q=term&t=members&page=1`)
- **Pattern:** `useSearchParams()` hook for reading/writing query parameters

### Infrastructure

No new infrastructure required. Search uses existing PostgreSQL instance with built-in FTS capabilities.

---

## 4. Data Model

### Conceptual Schema

Search requires two new `tsvector` columns on existing tables and corresponding GIN indexes. No new tables are created.

```
┌──────────────────────────────┐
│         profiles             │
│  (Identity context table)    │
├──────────────────────────────┤
│  user_id           UUID PK   │
│  display_name      VARCHAR   │
│  bio               TEXT      │
│  ...existing columns...      │
│  search_vector     TSVECTOR  │  ← NEW
├──────────────────────────────┤
│  GIN INDEX on search_vector  │  ← NEW
└──────────────────────────────┘

┌──────────────────────────────┐
│           posts              │
│  (Community context table)   │
├──────────────────────────────┤
│  id                UUID PK   │
│  title             VARCHAR   │
│  content           TEXT      │
│  is_deleted        BOOLEAN   │
│  ...existing columns...      │
│  search_vector     TSVECTOR  │  ← NEW
├──────────────────────────────┤
│  GIN INDEX on search_vector  │  ← NEW
└──────────────────────────────┘
```

### Design Decisions

**Decision: Stored `tsvector` columns vs. computed at query time**

- **Chosen:** Stored `tsvector` columns updated by database triggers
- **Rationale:** Pre-computing `tsvector` at write time means reads are index-only scans. Computing `to_tsvector()` at query time requires processing every row — unacceptable for large tables.
- **Trade-off:** Slightly slower writes (trigger overhead) for much faster reads. Writes are infrequent compared to search queries.

**Decision: Database triggers vs. application-level updates**

- **Chosen:** PostgreSQL triggers to auto-update `search_vector` on INSERT/UPDATE
- **Rationale:** Guarantees index freshness regardless of how data is written (migrations, admin tools, direct SQL). Application-level updates risk stale indexes if code paths are missed.
- **Alternative rejected:** Application-side `tsvector` computation — fragile, requires every write path to remember to update the vector.

**Decision: Single vector per row combining multiple fields**

- **Profiles:** `search_vector = to_tsvector('english', coalesce(display_name, '') || ' ' || coalesce(bio, ''))`
- **Posts:** `search_vector = to_tsvector('english', coalesce(title, '') || ' ' || coalesce(content, ''))`
- **Rationale:** Single GIN index per table is simpler and faster than multiple per-field indexes. Field weighting (e.g., title matches rank higher than body) can be added in Phase 2 using `setweight()`.

**Decision: English language configuration**

- **Chosen:** `to_tsvector('english', ...)` for both tables
- **Rationale:** MVP targets English-speaking communities. Multi-language support (using `simple` or auto-detection) is Phase 3.

### Migration Strategy

The migration must:
1. Add `search_vector` column (nullable initially) to `profiles` and `posts`
2. Create GIN indexes on both columns
3. Create trigger functions to auto-update `search_vector` on INSERT/UPDATE
4. Backfill existing rows by running `UPDATE ... SET search_vector = to_tsvector(...)`
5. Make column NOT NULL after backfill (or leave nullable to handle edge cases)

**Cross-context table modification:** The `profiles` table is owned by the Identity context. Adding a `search_vector` column to it is a pragmatic choice — the alternative (duplicating profile data into Community context) introduces data sync complexity disproportionate to the benefit. Document this cross-context dependency and plan to migrate to a dedicated search index if contexts are ever deployed independently.

---

## 5. API Design

### Endpoint Overview

A single search endpoint serves both member and post results:

```
GET /api/v1/community/search?q={query}&type={members|posts}&limit={10}&offset={0}
```

**Design decision:** Single endpoint with `type` parameter vs. two separate endpoints (`/search/members`, `/search/posts`).
- **Chosen:** Single endpoint — simpler client integration, allows future unified response with both types, matches Skool.com URL pattern (`/search?q=sachin&t=members`)
- **Alternative rejected:** Separate endpoints — forces two API calls for tab counts, increases frontend complexity

### Request Contract

| Parameter | Type | Required | Default | Constraints |
|-----------|------|----------|---------|-------------|
| `q` | string | Yes | — | 3-200 characters, trimmed |
| `type` | enum | No | `members` | `members` or `posts` |
| `limit` | int | No | 10 | 1-50 |
| `offset` | int | No | 0 | >= 0 |

### Response Contract

```
{
  "items": [...],          // Array of member or post results
  "total_count": 47,       // Total matches for active type
  "has_more": true,         // Whether more pages exist
  "member_count": 12,       // Total member matches (always returned)
  "post_count": 35          // Total post matches (always returned)
}
```

**Design decision:** Always return both counts, regardless of active `type`.
- **Rationale:** The frontend needs both counts to render tab labels ("Members 12 | Posts 35") without a second API call. Counting is cheap (single SQL `COUNT(*)` with GIN index).

### Authentication & Authorization

- Requires valid JWT token (reuse existing `CurrentUserIdDep`)
- Requires active community membership (reuse existing `MemberRepositoryDep.exists()`)
- Returns 401 for missing/invalid token
- Returns 403 for non-members

### Error Responses

| Status | Condition | Response Body |
|--------|-----------|---------------|
| 400 | Query < 3 chars | `{"code": "QUERY_TOO_SHORT", "message": "..."}` |
| 400 | Query empty | `{"code": "QUERY_REQUIRED", "message": "..."}` |
| 400 | Invalid type | `{"code": "INVALID_SEARCH_TYPE", "message": "..."}` |
| 401 | Not authenticated | `{"detail": "Not authenticated"}` |
| 403 | Not a member | `{"detail": "Not a member of this community"}` |
| 429 | Rate limit exceeded | `{"code": "RATE_LIMIT_EXCEEDED", "message": "..."}` |

---

## 6. Domain Model

### No New Domain Entities

Search is purely a query-side concern. It does not create, modify, or delete any domain objects. There are no invariants, no business rules, and no domain events.

The feature reads from existing aggregates:
- **Post** aggregate (title, content, author, category, timestamps)
- **CommunityMember** / **Profile** (display name, username, bio, location, join date)

### Value Objects

**SearchQuery** — Represents a validated search request (application layer, not domain)
- Query text (3-200 chars, trimmed, sanitized)
- Search type (members or posts)
- Pagination (limit, offset)
- Community scope (community_id)
- Requester identity (user_id for auth check)

This is modeled as an application-layer query object, not a domain value object, because search is not a domain concept.

### Domain Events

None. Search is read-only.

---

## 7. Application Layer

### Queries

**SearchQuery** — Immutable dataclass representing a search request
- Carries: community_id, requester_id, query text, type, limit, offset
- Follows existing pattern: `ListMembersQuery`, `GetFeedQuery`

### Handler

**SearchHandler** — Orchestrates the search operation:
1. Verify requester is an active member of the community (reuse member repository)
2. Sanitize query input (strip HTML, trim whitespace)
3. Execute search via search repository
4. Return structured result DTO

The handler does NOT contain FTS query logic — that belongs in the infrastructure layer's search repository. The handler only orchestrates.

### DTOs

**SearchResult** — Contains:
- `items`: List of `MemberSearchEntry` or `PostSearchEntry`
- `total_count`: Total matches for the active type
- `member_count`: Total member matches
- `post_count`: Total post matches
- `has_more`: Whether more results exist

**MemberSearchEntry** — Enhanced version of existing `MemberDirectoryEntry`:
- user_id, display_name, username, avatar_url, bio, role, joined_at, location

**PostSearchEntry** — Lightweight post preview:
- id, title, body_snippet (first 200 chars), author (name + avatar), category (name + emoji), created_at, like_count, comment_count

---

## 8. Integration Strategy

### Cross-Context Data Access

Search queries data from two contexts:
- **Community context:** Posts table (owned), CommunityMembers table (owned)
- **Identity context:** Profiles table (owned by Identity)

**Decision: Direct SQL JOIN vs. cross-context API call**

- **Chosen:** Direct JOIN between `community_members`, `profiles`, and `posts` tables within search queries
- **Rationale:** For a read-only query concern, the pragmatic approach is a database JOIN. Cross-context API calls would add latency and complexity for zero benefit in a monolithic deployment.
- **Trade-off:** Creates a coupling between Community and Identity at the data layer. Acceptable for MVP — if contexts are deployed independently (microservices), search would migrate to a dedicated read model with event-driven data replication.
- **Precedent:** The existing `list_directory()` method already JOINs `CommunityMemberModel` with `ProfileModel`. Search follows the same pattern.

### Failure Modes

| Failure | Impact | Handling |
|---------|--------|----------|
| PostgreSQL down | Search unavailable | Return 503, frontend shows error state |
| GIN index corrupt | Slow queries | Fallback detected by p95 monitoring, manual reindex |
| Stale `tsvector` | Missing recent content | Trigger ensures < 1 second lag; acceptable |

---

## 9. Security Design

### Input Validation

**Query sanitization pipeline:**
1. Strip leading/trailing whitespace
2. Enforce length (3-200 characters)
3. Strip HTML tags (prevent stored XSS if query is reflected in UI)
4. Pass to PostgreSQL's `plainto_tsquery()` which handles SQL injection by design — it's a parameterized function, not string interpolation

**Design decision:** Use `plainto_tsquery()` instead of `to_tsquery()`
- `plainto_tsquery()` treats the entire input as plain text search terms joined by AND
- `to_tsquery()` requires tsquery syntax (`&`, `|`, `!`) which is confusing for end users and opens injection vectors
- Users searching "SaaS startup" expect both words to match, not tsquery operators

### Authorization Model

Search reuses the existing authorization pattern:
1. JWT validation (existing `CurrentUserIdDep`)
2. Community membership check (existing `MemberRepositoryDep.exists()`)
3. Results filtered by community_id (cannot see other communities' data)
4. Inactive/deleted members excluded from results
5. Soft-deleted posts excluded from results

### Rate Limiting

- 30 searches per minute per user
- Reuse existing `InMemoryRateLimiter` pattern from post creation
- Returns 429 with retry-after information

### Threat Model

| Threat | Mitigation |
|--------|------------|
| SQL injection via query param | Parameterized `plainto_tsquery()` — immune by design |
| XSS via reflected search term | HTML stripped on input, escaped on output |
| Enumeration attack (guessing member names) | Rate limiting, authentication required |
| DoS via expensive queries | Min 3 chars prevents full-table wildcard, GIN index bounds query cost |

---

## 10. Performance & Scalability

### Performance Targets

| Metric | Target | Approach |
|--------|--------|----------|
| API response time (p95) | < 200ms | GIN indexes, pre-computed tsvector |
| End-to-end latency (p95) | < 500ms | API + network + render |
| Index freshness | < 1 second | Database triggers (synchronous) |

### Query Optimization Strategy

**GIN indexes** are the primary optimization:
- GIN (Generalized Inverted Index) maps each lexeme to the rows containing it
- `tsvector @@ tsquery` lookups are O(log n) with GIN vs. O(n) with sequential scan
- Index size is proportional to unique lexemes, not row count

**Expected performance at scale:**
- 10,000 profiles with GIN index: < 5ms query time
- 50,000 posts with GIN index: < 10ms query time
- Combined with COUNT queries: < 50ms total

### Caching Strategy

**MVP: No caching.** PostgreSQL FTS with GIN indexes is fast enough for MVP traffic.

**Phase 2 consideration:** If search latency increases:
- Cache popular queries in Redis (TTL: 30 seconds)
- Cache tab counts separately (they change less frequently)
- Invalidate on post create/delete events

### Scalability Bottlenecks

1. **GIN index size** — Grows with content. At 1M posts, index may reach ~500MB. Manageable on a single PostgreSQL instance.
2. **COUNT(*) queries** — Computing total matches for both tabs on every request. If expensive, cache counts or use approximate counts (`reltuples`).
3. **Concurrent searches** — PostgreSQL handles concurrent reads well. Connection pooling (existing) prevents exhaustion.

---

## 11. Error Handling

### Error Taxonomy

| Error | HTTP Status | Code | User Message |
|-------|-------------|------|--------------|
| Query too short | 400 | `QUERY_TOO_SHORT` | "Please enter at least 3 characters to search" |
| Query empty/missing | 400 | `QUERY_REQUIRED` | "A search query is required" |
| Invalid type | 400 | `INVALID_SEARCH_TYPE` | "Search type must be 'members' or 'posts'" |
| Not authenticated | 401 | — | "Not authenticated" |
| Not a member | 403 | — | "Not a member of this community" |
| Rate limited | 429 | `RATE_LIMIT_EXCEEDED` | "Too many searches. Please wait a moment." |
| Server error | 500 | `SEARCH_ERROR` | "Search is temporarily unavailable" |

### Error Implementation Pattern

Follow existing pattern from Community context:
- Domain-level exceptions raised by handler (e.g., `NotCommunityMemberError`)
- Controller catches and maps to HTTP responses
- Use `ErrorResponse` schema for structured errors

---

## 12. Testing Strategy

### BDD Tests (30 scenarios in `search.feature`)

| Category | Count | Coverage |
|----------|-------|----------|
| Happy path — Members | 5 | Name, username, bio search, sorting, card fields |
| Happy path — Posts | 4 | Title, body search, sorting, card fields |
| Happy path — Tabs | 2 | Tab counts, tab switching |
| Happy path — Pagination | 2 | Page size, next page |
| Happy path — Stemming | 2 | Member bio stemming, post content stemming |
| Validation errors | 4 | Short query, empty query, invalid type, long query |
| Edge cases | 7 | No results, special chars, deleted posts, inactive members, whitespace, no bio, multiple matches |
| Security | 4 | Unauthenticated, non-member, SQL injection, rate limiting |

### Unit Tests

- **SearchQuery validation:** Min/max length, trimming, sanitization
- **DTO construction:** MemberSearchEntry, PostSearchEntry field mapping
- **Query sanitization:** HTML stripping, special character handling

### Integration Tests

- **FTS queries:** Verify `tsvector`/`tsquery` matching with test data
- **GIN index usage:** Verify queries use index (EXPLAIN ANALYZE)
- **Stemming behavior:** Verify "engineering" matches "engineer"
- **Cross-table JOINs:** Member results correctly join profiles with community_members

---

## 13. Observability

### Logging

| Event | Level | Fields |
|-------|-------|--------|
| Search attempt | INFO | user_id, community_id, query (redacted), type |
| Search success | INFO | user_id, result_count, duration_ms |
| Search error | ERROR | user_id, error_type, query (redacted) |
| Rate limit hit | WARN | user_id, requests_in_window |

**Privacy:** Search queries are logged without PII. Use first 3 characters + length only (e.g., `"sac..." (6 chars)`).

### Metrics

| Metric | Type | Purpose |
|--------|------|---------|
| `search.request.count` | Counter | Traffic volume |
| `search.request.duration_ms` | Histogram | Latency distribution |
| `search.results.count` | Histogram | Results per query (detect zero-result patterns) |
| `search.error.count` | Counter | Error rate by type |

### Tracing

- Span: `search.handler` — covers full handler execution
- Child span: `search.query.members` — member FTS query
- Child span: `search.query.posts` — post FTS query
- Child span: `search.count` — count queries

---

## 14. Deployment Strategy

### Migration Plan

1. **Deploy migration** — Adds `search_vector` columns, GIN indexes, and triggers. This is a non-breaking schema change (new nullable columns).
2. **Backfill existing data** — Migration includes `UPDATE` statements to populate `search_vector` for all existing rows. For large tables, consider batched updates.
3. **Deploy application code** — New search endpoint, frontend search bar
4. **Verify** — Run BDD tests, check GIN index usage with `EXPLAIN ANALYZE`

### Rollback Plan

- **Application rollback:** Remove search route from main.py, redeploy. Search bar hidden via feature flag or conditional rendering.
- **Migration rollback:** Drop `search_vector` columns and triggers. GIN indexes drop automatically with columns.
- **Data safety:** No existing data is modified or deleted. Rollback is clean.

### Feature Flag

**Not required for MVP.** The search bar is a new UI element — deploying it is the feature toggle. If gradual rollout is desired, conditionally render `<SearchBar />` based on a config flag.

---

## 15. Future Considerations

### Phase 2 Enhancements

- **Course/Lesson search** — Add `search_vector` to classroom tables, extend API with `type=courses`
- **Comment search** — Add `search_vector` to comments table
- **Relevance ranking** — Use `ts_rank()` or `ts_rank_cd()` for ordering instead of alphabetical/date
- **Field weighting** — Use `setweight()` to prioritize title matches over body matches (e.g., title = A weight, body = B weight)
- **Result highlighting** — Use `ts_headline()` to highlight matched terms in snippets
- **Advanced filters** — Date range, category, role filters on search results
- **Real-time search** — Debounced as-you-type with dropdown suggestions

### Phase 3 Enhancements

- **Elasticsearch migration** — When PostgreSQL FTS hits scaling limits (~1M+ documents) or relevance requirements become complex
- **Search suggestions** — Autocomplete based on popular queries
- **Multi-language** — Dynamic language detection or `simple` dictionary
- **Search analytics** — Popular queries dashboard, zero-result tracking

### Known Limitations

- **No fuzzy matching** — Typos won't match (e.g., "Sachn" won't find "Sachin"). `pg_trgm` extension can address this in Phase 2.
- **English only** — `to_tsvector('english', ...)` hardcoded. Non-English content will have degraded stemming.
- **No username search via FTS** — Usernames (e.g., "sachin-kundu-3386") don't stem well with English dictionary. The `profiles.search_vector` includes display_name and bio but username matching will use a supplementary `ILIKE` condition.

### Technical Debt

- **Cross-context JOIN** — Search queries JOIN `profiles` (Identity) with `community_members` (Community). Acceptable for monolith but creates coupling.
- **Trigger-based indexing** — Triggers are invisible to application code. Must be documented and tested.

---

## 16. Alignment Verification

See `docs/features/search/ALIGNMENT_VERIFICATION.md`

---

## 17. Appendices

### A. File Checklist

**Backend — New Files:**
- `src/community/application/queries/search_query.py` — SearchQuery dataclass
- `src/community/application/handlers/search_handler.py` — SearchHandler
- `src/community/application/dtos/search_results.py` — SearchResult, MemberSearchEntry, PostSearchEntry DTOs
- `src/community/infrastructure/persistence/search_repository.py` — ISearchRepository implementation with FTS queries
- `src/community/domain/repositories/search_repository.py` — ISearchRepository interface
- `src/community/interface/api/search_controller.py` — GET /community/search endpoint
- `alembic/versions/xxx_add_search_vector_columns.py` — Migration for tsvector columns, GIN indexes, triggers

**Backend — Modified Files:**
- `src/community/interface/api/schemas.py` — Add search request/response schemas
- `src/community/interface/api/dependencies.py` — Add search handler dependency
- `src/community/infrastructure/persistence/__init__.py` — Export search repository
- `src/community/application/handlers/__init__.py` — Export SearchHandler
- `src/main.py` — Register search router

**Frontend — New Files:**
- `frontend/src/features/search/components/SearchBar.tsx`
- `frontend/src/features/search/components/SearchResults.tsx`
- `frontend/src/features/search/components/SearchResultTabs.tsx`
- `frontend/src/features/search/components/MemberSearchCard.tsx`
- `frontend/src/features/search/components/PostSearchCard.tsx`
- `frontend/src/features/search/components/SearchPagination.tsx`
- `frontend/src/features/search/components/SearchEmptyState.tsx`
- `frontend/src/features/search/components/SearchSkeleton.tsx`
- `frontend/src/features/search/api/searchApi.ts` — API client functions
- `frontend/src/features/search/hooks/useSearch.ts` — React Query hook
- `frontend/src/features/search/types/search.ts` — TypeScript interfaces
- `frontend/src/pages/SearchPage.tsx` — Search results page

**Frontend — Modified Files:**
- `frontend/src/App.tsx` — Add `/search` route
- Header component — Embed `<SearchBar />`

**Test Files:**
- `tests/features/search/test_search.py` — BDD step implementations
- `tests/unit/community/test_search_handler.py` — Unit tests

### B. Dependencies

**No new Python packages required.**
- PostgreSQL FTS is built-in
- SQLAlchemy 2.0 supports `tsvector` via `sqlalchemy.dialects.postgresql.TSVECTOR`
- All frontend dependencies already available (React Query, react-router-dom, Heroicons)

### C. References

- PostgreSQL Full-Text Search: https://www.postgresql.org/docs/current/textsearch.html
- PostgreSQL GIN Indexes: https://www.postgresql.org/docs/current/gin.html
- SQLAlchemy TSVECTOR: https://docs.sqlalchemy.org/en/20/dialects/postgresql.html
- `plainto_tsquery` vs `to_tsquery`: https://www.postgresql.org/docs/current/textsearch-controls.html
