# Search — Implementation Phases

## Complexity Analysis

| Metric | Count | Complexity |
|--------|-------|------------|
| BDD Scenarios | 30 | High |
| New Files | 21 (7 backend, 12 frontend, 2 test) | High |
| Modified Files | 7 | Medium |
| API Endpoints | 1 | Low |
| Dependencies | 2 contexts (Community + Identity) | Medium |

**Overall Complexity:** High

**Decision:** 3-phase implementation

**Strategy:** Vertical Slicing — each phase delivers end-to-end functionality across all layers (database, backend, frontend). Every phase is independently deployable with passing CI.

---

## Phase 1: Core Search End-to-End

### Goal
Deliver working member and post search with tabbed results — a user can type a query in the header, press Enter, and see matching members or posts on a dedicated search results page with tab switching.

### Scope

**Backend (Database -> API):**
- [ ] Database migration: `tsvector` columns on `profiles` and `posts`, GIN indexes, trigger functions, backfill
- [ ] Application query: `SearchQuery` dataclass
- [ ] Application handler: `SearchHandler` (orchestrates search, validates membership)
- [ ] Application DTOs: `SearchResult`, `MemberSearchEntry`, `PostSearchEntry`
- [ ] Domain interface: `ISearchRepository` (abstract base)
- [ ] Infrastructure: `SqlAlchemySearchRepository` with PostgreSQL FTS queries (`plainto_tsquery`, `@@`, `ILIKE` for username)
- [ ] API controller: `GET /api/v1/community/search?q=&type=&limit=&offset=`
- [ ] API schemas: `SearchRequestParams`, `SearchResponse`, `MemberSearchItemResponse`, `PostSearchItemResponse`
- [ ] Dependencies: `get_search_handler` factory
- [ ] Router registration in `main.py`

**Frontend (User-Facing UI):**
- [ ] `SearchBar.tsx` — Header search input with magnifying glass, clear button, Enter-to-search
- [ ] `SearchResults.tsx` — Results page container (layout with sidebar)
- [ ] `SearchResultTabs.tsx` — "Members N" / "Posts N" tab switcher
- [ ] `MemberSearchCard.tsx` — Member profile preview card (avatar, name, username, bio, join date)
- [ ] `PostSearchCard.tsx` — Post preview card (title, snippet, author, category, timestamp)
- [ ] `SearchSkeleton.tsx` — Loading skeleton cards
- [ ] `searchApi.ts` — API client function
- [ ] `useSearch.ts` — React Query hook
- [ ] `search.ts` (types) — TypeScript interfaces
- [ ] `SearchPage.tsx` — Page component wired to route
- [ ] Route `/search` added to `App.tsx`
- [ ] Header component modified to embed `<SearchBar />`

**Testing:**
- [ ] BDD scenarios (API-level): 11 scenarios
- [ ] Unit tests: SearchQuery validation, DTO construction

### BDD Scenarios

**Enabled for this phase (11):**
- [ ] Line 22: Search for a member by display name
- [ ] Line 29: Search for a member by username
- [ ] Line 36: Search for a member by bio content
- [ ] Line 43: Member results are sorted alphabetically (**NOTE:** BDD query `"a"` violates 3-char min — fix to `"startup"` or similar during implementation)
- [ ] Line 49: Member result card shows expected fields
- [ ] Line 62: Search for a post by title
- [ ] Line 69: Search for a post by body content
- [ ] Line 77: Post results are sorted by newest first
- [ ] Line 83: Post result card shows expected fields
- [ ] Line 97: Search returns counts for both tabs
- [ ] Line 104: Switch between member and post tabs

**Skipped (future phases):**
- Lines 113-128: Pagination scenarios -> Phase 2: Requires pagination UI
- Lines 132-143: Stemming scenarios -> Phase 2: Tested alongside pagination completeness
- Lines 148-169: Validation scenarios -> Phase 2: Input validation refinements
- Lines 175-221: Edge cases -> Phase 3: Data filtering edge cases
- Lines 225-249: Security scenarios -> Phase 3: Auth/authz/rate limiting hardening

### Deliverable
**User can:** Type a query in the header search bar, press Enter, land on `/search?q=term&t=members`, see matching members as profile cards, switch to "Posts" tab to see matching posts as content cards, and click any result to navigate to the full profile or post.

### Dependencies
- None (first phase)

### Estimated Time
4-5 hours

### Definition of Done
- [ ] All 12+ backend files created/modified
- [ ] All 12+ frontend files created/modified
- [ ] 11 BDD scenarios passing
- [ ] 19 scenarios skipped with phase markers
- [ ] Unit tests passing
- [ ] `./scripts/verify.sh` passes (ruff, mypy, pytest)
- [ ] Frontend builds without errors (`npm run build`)
- [ ] Search bar visible in header on all pages
- [ ] Tab counts display correctly

### Verification Commands
```bash
# Run phase-specific tests
pytest tests/features/search/test_search.py -v
# Expected: 11 passed, 19 skipped

# Verify all skips have phase markers
grep -r "@pytest.mark.skip" tests/features/search/ | grep "Phase [0-9]"

# Full verification
./scripts/verify.sh

# Frontend
cd frontend && npm run build && npm run typecheck
```

---

## Phase 2: Pagination, Stemming & Validation

### Goal
Complete the search experience with pagination controls, verify stemming works correctly, and add input validation with proper error messages for invalid queries.

### Scope

**Backend (Refinements):**
- [ ] Pagination: Ensure `limit`/`offset` in repository query, `has_more` flag, `total_count` accurate
- [ ] Validation: Enforce 3-char minimum, 200-char max (truncate), empty query rejection, invalid type rejection
- [ ] Error codes: `QUERY_TOO_SHORT`, `QUERY_REQUIRED`, `INVALID_SEARCH_TYPE` in controller
- [ ] Query truncation: Silently cap at 200 characters

**Frontend (Pagination + Validation UI):**
- [ ] `SearchPagination.tsx` — Previous/Next buttons, current page indicator, "1-10 of N" text
- [ ] Validation error display in SearchResults (query too short message)
- [ ] URL state: `?page=N` parameter sync

**Testing:**
- [ ] BDD scenarios (API-level): 8 scenarios enabled
- [ ] Pagination behavior verified with 25+ test members

### BDD Scenarios

**Enabled for this phase (8):**
- [ ] Line 113: Search results are paginated (10 per page, has_more)
- [ ] Line 122: Navigate to next page of results (offset=10)
- [ ] Line 132: Search uses stemming for member bio ("engineering" -> "engineer")
- [ ] Line 139: Search uses stemming for post content ("growing" -> "growth")
- [ ] Line 148: Search with query shorter than 3 characters (400 error)
- [ ] Line 153: Search with empty query (400 error)
- [ ] Line 159: Search with invalid type parameter (400 error)
- [ ] Line 164: Search with query exceeding maximum length (truncated, succeeds)

**Skipped (future phase):**
- Lines 175-221: Edge cases -> Phase 3
- Lines 225-249: Security scenarios -> Phase 3

### Deliverable
**User can:** Browse through paginated results using Previous/Next controls, see page indicators ("1-10 of 47"), search for word variants ("engineering" finds "engineer"), and receive helpful error messages for invalid queries (too short, empty).

### Dependencies
- Phase 1 complete (core search functionality)

### Estimated Time
2-3 hours

### Definition of Done
- [ ] 8 new BDD scenarios passing (19 total)
- [ ] 11 scenarios skipped with Phase 3 markers
- [ ] Pagination renders correctly for 25+ results
- [ ] Validation errors display user-friendly messages
- [ ] Stemming confirmed working (automatic via PostgreSQL FTS)
- [ ] `./scripts/verify.sh` passes

### Verification Commands
```bash
pytest tests/features/search/test_search.py -v
# Expected: 19 passed, 11 skipped

./scripts/verify.sh
```

---

## Phase 3: Edge Cases & Security

### Goal
Harden the search feature for production: handle all edge cases (no results, special characters, deleted content, inactive members), enforce security (authentication, authorization, rate limiting), and add polished empty/error UI states.

### Scope

**Backend (Hardening):**
- [ ] Deleted posts excluded from results (`is_deleted = False` filter)
- [ ] Inactive members excluded (`is_active = True` filter)
- [ ] Special character sanitization (HTML stripping, XSS prevention)
- [ ] Rate limiting: 30 searches/minute per user (reuse `InMemoryRateLimiter`)
- [ ] Auth: 401 for unauthenticated, 403 for non-members
- [ ] SQL injection safety verified (inherent with `plainto_tsquery`)

**Frontend (Empty & Error States):**
- [ ] `SearchEmptyState.tsx` — "No members/posts found" with fallback links
- [ ] Error state UI — "Search temporarily unavailable" with retry button
- [ ] No-query state — "Enter a search term above to find members and posts"

**Testing:**
- [ ] BDD scenarios (API-level): 11 scenarios enabled (all 30 total)
- [ ] Rate limiting test with 31 rapid requests

### BDD Scenarios

**Enabled for this phase (11):**
- [ ] Line 175: Search returns no results (0 members, "no results" indicator)
- [ ] Line 182: Search with special characters (XSS attempt, executes safely)
- [ ] Line 189: Deleted posts do not appear in search results
- [ ] Line 196: Inactive members do not appear in search results
- [ ] Line 203: Search with only whitespace (treated as empty query)
- [ ] Line 209: Member with no bio is still found by name
- [ ] Line 217: Search query matches across multiple members
- [ ] Line 225: Unauthenticated user cannot search (401)
- [ ] Line 231: Non-member cannot search a community (403)
- [ ] Line 239: Search input is sanitized against SQL injection
- [ ] Line 245: Search respects rate limiting (429 on 31st request)

### Deliverable
**User can:** See helpful empty states when no results match, experience zero security vulnerabilities (XSS, SQL injection blocked), receive proper auth errors when not logged in or not a member, and be rate-limited to prevent abuse. Feature is production-ready.

### Dependencies
- Phase 2 complete (pagination and validation)

### Estimated Time
3-4 hours

### Definition of Done
- [ ] All 30 BDD scenarios passing (0 skipped)
- [ ] Rate limiting tested and working
- [ ] Special character handling verified
- [ ] Auth/authz errors return correct status codes
- [ ] Empty state UI renders correctly
- [ ] `./scripts/verify.sh` passes
- [ ] No security vulnerabilities (XSS, SQL injection)
- [ ] Feature fully production-ready

### Verification Commands
```bash
pytest tests/features/search/test_search.py -v
# Expected: 30 passed, 0 skipped, 0 failed

./scripts/verify.sh

# Verify no skip markers remain
grep -r "@pytest.mark.skip" tests/features/search/ | grep -c "Phase"
# Expected: 0
```

---

## Dependency Graph

```
Phase 1 (Core Search End-to-End)
    │
    │  11 BDD scenarios passing
    │  User can search members & posts with tabs
    │
Phase 2 (Pagination, Stemming & Validation)
    │
    │  19 BDD scenarios passing
    │  User can paginate, receives validation errors
    │
Phase 3 (Edge Cases & Security)
    │
    │  30 BDD scenarios passing
    │  Feature production-ready
    ▼
```

---

## Implementation Notes

**Patterns to Follow:**
- Handler pattern: Match `ListMembersHandler` (inject repository, validate membership, return DTO)
- Repository pattern: Match `SqlAlchemyMemberRepository.list_directory()` for JOINs across `CommunityMemberModel` + `ProfileModel`
- Controller pattern: Match `post_controller.py` (catch domain exceptions, map to HTTP status)
- Schema pattern: Match `MemberDirectoryResponse` (items list + total_count + has_more)
- Frontend API pattern: Match `memberApi.ts` (apiClient.get with params)
- Frontend hook pattern: Match `useMembers.ts` (React Query with useQuery)
- BDD test pattern: ALL steps async with `client: AsyncClient` parameter + `# ruff: noqa: ARG001`

**Known Spec Issues:**
- BDD line 44 ("sorted alphabetically") uses query `"a"` which violates 3-char minimum — fix during Phase 1 implementation
- TDD notes username search needs supplementary `ILIKE` (not in search_vector) — implement in Phase 1

**Cross-Context Dependencies:**
- `profiles` table (Identity context) gets `search_vector` column added via migration
- Search repository JOINs `community_members` + `profiles` (follows existing `list_directory` precedent)

**Common Pitfalls:**
- Don't forget to register the search router in `main.py` and `__init__.py` exports
- Don't forget database triggers for auto-updating `search_vector` on INSERT/UPDATE
- Don't forget to backfill existing rows in migration
- Username search needs ILIKE fallback since hyphens/numbers don't stem well
- All BDD step functions must be async with `client: AsyncClient` param
