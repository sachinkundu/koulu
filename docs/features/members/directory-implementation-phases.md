# Member Directory - Implementation Phases

## Complexity Analysis

| Metric | Count | Complexity |
|--------|-------|------------|
| BDD Scenarios | 23 | High (>20) |
| New Files | ~17 | High (>10) |
| Modified Files | ~6 | Medium |
| API Endpoints | 1 | Low |
| Dependencies | 2 contexts (Community + Identity) | Medium |

**Overall Complexity:** High

**Decision:** 3-phase implementation

**Strategy:** Vertical Slicing — all layers per phase. Each phase is independently deployable with passing CI. Phase 1 gets the directory visible to users; Phase 2 adds discoverability via search/filter/sort; Phase 3 hardens edge cases and security.

---

## Phase 1: Core Directory — Browse & Paginate

### Goal

Deliver a working member directory page where users can browse community members in a vertical list with infinite scroll. Members display with avatar, name, role badge, bio, and join date. Default sort is most recent first.

### Scope

**Backend (Domain -> API):**
- [ ] Application query: `src/community/application/queries/list_members_query.py` (new)
- [ ] Application handler: `src/community/application/handlers/list_members_handler.py` (new)
- [ ] Application DTO: `src/community/application/dtos/member_directory_entry.py` (new)
- [ ] Domain repository interface: `src/community/domain/repositories/member_repository.py` (extend with `list_directory()`, `count_directory()`)
- [ ] Infrastructure persistence: `src/community/infrastructure/persistence/member_repository.py` (implement new methods with JOIN to profiles)
- [ ] Interface controller: `src/community/interface/api/member_controller.py` (add GET /community/members endpoint)
- [ ] Interface schemas: `src/community/interface/api/schemas.py` (add MemberDirectoryResponse, MemberResponse)
- [ ] Interface dependencies: `src/community/interface/api/dependencies.py` (add ListMembersHandler dependency)

**Frontend (User-Facing UI):**
- [ ] Types: `frontend/src/features/members/types/members.ts` (new)
- [ ] API client: `frontend/src/features/members/api/memberApi.ts` (new)
- [ ] Hook: `frontend/src/features/members/hooks/useMembers.ts` (new — useInfiniteQuery)
- [ ] Component: `frontend/src/features/members/components/MemberCard.tsx` (new)
- [ ] Component: `frontend/src/features/members/components/MemberList.tsx` (new — infinite scroll)
- [ ] Component: `frontend/src/features/members/components/MemberCardSkeleton.tsx` (new)
- [ ] Barrel: `frontend/src/features/members/components/index.ts` (new)
- [ ] Page: `frontend/src/pages/MembersPage.tsx` (new)
- [ ] Route + nav: `frontend/src/App.tsx` (add /members route + Members tab)

**Testing:**
- [ ] BDD step definitions: `tests/features/members/step_defs/test_directory.py` (new)
- [ ] Test fixtures: `tests/features/members/conftest.py` (new)
- [ ] Unit tests for handler: `tests/unit/community/test_list_members_handler.py` (new)

### BDD Scenarios

**Enabled for this phase (6):**
- [ ] Line 20: View member directory as a community member
- [ ] Line 28: Member directory shows correct member count
- [ ] Line 83: Sort members by most recent
- [ ] Line 97: Paginated member loading (first page, limit 20)
- [ ] Line 104: Load second page of members
- [ ] Line 113: Load final page of members

**Skipped (future phases):**
- Lines 34-38: Search members by name -> Phase 2: Requires search query param
- Lines 41-44: Search is case-insensitive -> Phase 2: Requires search
- Lines 47-52: Search with partial name match -> Phase 2: Requires search
- Lines 55-59: Filter members by admin role -> Phase 2: Requires role filter
- Lines 62-65: Filter members by moderator role -> Phase 2: Requires role filter
- Lines 68-73: Filter members by member role -> Phase 2: Requires role filter
- Lines 75-79: Sort members alphabetically -> Phase 2: Requires sort option
- Lines 89-94: Combine search with role filter -> Phase 2: Requires search + filter
- Lines 123-127: Search returns no results -> Phase 2: Requires search
- Lines 130-134: Filter returns no results -> Phase 2: Requires filter
- Lines 155-158: Empty search query returns all members -> Phase 2: Requires search
- Lines 139-144: Deactivated members excluded -> Phase 3: Edge case
- Lines 147-152: Members without completed profiles -> Phase 3: Edge case
- Lines 161-164: Single member community -> Phase 3: Edge case
- Lines 169-172: Unauthenticated user cannot access -> Phase 3: Security
- Lines 175-178: Non-member cannot access -> Phase 3: Security
- Lines 181-185: No private info exposed -> Phase 3: Security

### Deliverable

**User can:** Open the Members tab from the navigation bar, see a list of community members with avatars, names, role badges, bios, and join dates (newest first), scroll down to load more members via infinite scroll, and click any member card to navigate to their profile page.

### Dependencies

None (first phase).

### Estimated Time

3-4 hours

### Definition of Done

- [ ] All new backend files created (query, handler, DTO, schemas, endpoint)
- [ ] Repository interface extended + implementation with JOIN
- [ ] 6 BDD scenarios passing
- [ ] 17 BDD scenarios skipped with phase markers
- [ ] Unit tests for handler passing
- [ ] Frontend MembersPage renders with member cards
- [ ] Infinite scroll loads subsequent pages
- [ ] Members tab visible in navigation
- [ ] Linting passes (ruff)
- [ ] Type checking passes (mypy + TypeScript)
- [ ] `./scripts/verify.sh` green
- [ ] Frontend builds and renders correctly

### Verification Commands

```bash
# Run BDD tests
pytest tests/features/members/step_defs/test_directory.py -v
# Expected: 6 passed, 17 skipped

# Verify skip markers
grep -r "@pytest.mark.skip" tests/features/members/ | grep "Phase [0-9]"

# Full verification
./scripts/verify.sh

# Frontend
cd frontend && npm run typecheck && npm run build
```

---

## Phase 2: Search, Filter & Sort

### Goal

Add member discoverability — name search (debounced, case-insensitive), role filter pill tabs with counts (All / Admin / Moderator), and alphabetical sort option. These controls update the member list in real time.

### Scope

**Backend (Domain -> API):**
- [ ] Extend repository query: search ILIKE on display_name, role filter, alphabetical sort
- [ ] Extend ListMembersQuery with `search`, `role`, `sort` fields
- [ ] Extend handler to pass new filter params through
- [ ] Extend API schemas for query parameter validation (search max 100 chars, role enum, sort enum)

**Frontend (User-Facing UI):**
- [ ] Component: `frontend/src/features/members/components/MemberFilters.tsx` (new — search, role tabs, sort dropdown)
- [ ] Hook: Update `useMembers` to accept search/role/sort params
- [ ] Debounce: Add search debounce (300ms) to MemberFilters
- [ ] Update MembersPage to wire MemberFilters to useMembers

**Testing:**
- [ ] BDD step definitions for search, filter, sort scenarios
- [ ] Unit tests for search/filter/sort query building

### BDD Scenarios

**Enabled for this phase (11):**
- [ ] Line 34: Search members by name
- [ ] Line 41: Search is case-insensitive
- [ ] Line 47: Search with partial name match
- [ ] Line 55: Filter members by admin role
- [ ] Line 62: Filter members by moderator role
- [ ] Line 68: Filter members by member role
- [ ] Line 75: Sort members alphabetically
- [ ] Line 89: Combine search with role filter
- [ ] Line 123: Search returns no results
- [ ] Line 130: Filter returns no results
- [ ] Line 155: Empty search query returns all members

**Skipped (Phase 3):**
- Lines 139-144: Deactivated members excluded -> Phase 3: Edge case
- Lines 147-152: Members without completed profiles -> Phase 3: Edge case
- Lines 161-164: Single member community -> Phase 3: Edge case
- Lines 169-172: Unauthenticated user cannot access -> Phase 3: Security
- Lines 175-178: Non-member cannot access -> Phase 3: Security
- Lines 181-185: No private info exposed -> Phase 3: Security

### Deliverable

**User can:** Type a name in the search bar and see matching members after a brief debounce; click role filter tabs (All/Admin/Moderator) with live counts to narrow results; switch between "Most Recent" and "Alphabetical" sorting; combine search with filters for precise discovery.

### Dependencies

Phase 1 must be complete (base directory endpoint, MembersPage, useMembers hook).

### Estimated Time

2-3 hours

### Definition of Done

- [ ] Search, filter, and sort working end-to-end (backend + frontend)
- [ ] 17 BDD scenarios passing (6 from Phase 1 + 11 new)
- [ ] 6 BDD scenarios skipped with Phase 3 markers
- [ ] Search debounce working (300ms)
- [ ] Role tabs show accurate counts
- [ ] `./scripts/verify.sh` green

### Verification Commands

```bash
# Run BDD tests
pytest tests/features/members/step_defs/test_directory.py -v
# Expected: 17 passed, 6 skipped

# Full verification
./scripts/verify.sh
```

---

## Phase 3: Edge Cases, Empty States & Security

### Goal

Harden the directory for production — handle deactivated members, incomplete profiles, empty results, error states, and security (authentication + authorization + no private data leakage).

### Scope

**Backend (Domain -> API):**
- [ ] Verify deactivated member exclusion (is_active=false filtered out)
- [ ] Verify LEFT JOIN handles missing/incomplete profiles (null display_name, avatar, bio)
- [ ] Add explicit authorization error for non-members (403)
- [ ] Ensure no private fields (email, settings) in response schema

**Frontend (User-Facing UI):**
- [ ] Component: `frontend/src/features/members/components/MemberEmptyState.tsx` (new)
- [ ] Error state: Add error UI with retry button to MembersPage
- [ ] Handle null/missing profile fields in MemberCard (default avatar, "No bio" placeholder)

**Testing:**
- [ ] BDD step definitions for edge cases and security scenarios
- [ ] Security assertions: no email in response, no private settings

### BDD Scenarios

**Enabled for this phase (6):**
- [ ] Line 139: Deactivated members are excluded from directory
- [ ] Line 147: Members without completed profiles appear with defaults
- [ ] Line 161: Member directory for community with single member
- [ ] Line 169: Unauthenticated user cannot access member directory
- [ ] Line 175: Non-member cannot access community directory
- [ ] Line 181: Member directory does not expose private information

### Deliverable

**User can:** See only active members (deactivated excluded); see placeholder content for members without profiles; see "No members found" empty state when search/filter yields nothing; see an error message with retry if the API fails. Non-members and unauthenticated users are rejected with appropriate errors.

### Dependencies

Phase 2 must be complete (search + filter + sort).

### Estimated Time

2 hours

### Definition of Done

- [ ] All 23 BDD scenarios passing (0 skipped)
- [ ] Deactivated members excluded
- [ ] Incomplete profiles render with placeholders
- [ ] Empty state displayed when no results
- [ ] Error state with retry displayed on API failure
- [ ] 401 for unauthenticated, 403 for non-members
- [ ] No private data in API responses
- [ ] `./scripts/verify.sh` green
- [ ] Coverage >= 80%

### Verification Commands

```bash
# Run ALL BDD tests
pytest tests/features/members/step_defs/test_directory.py -v
# Expected: 23 passed, 0 skipped, 0 failed

# Verify no remaining skip markers
grep -r "@pytest.mark.skip" tests/features/members/step_defs/
# Expected: no output

# Full verification
./scripts/verify.sh
```

---

## Dependency Graph

```
Phase 1 (Core Directory — Browse & Paginate)
    |
Phase 2 (Search, Filter & Sort)
    |
Phase 3 (Edge Cases, Empty States & Security)
```

---

## Implementation Notes

**Patterns to Follow:**
- Follow existing feed patterns: `GetFeedHandler` for handler structure, `usePosts` for frontend hook, `FeedPostCard` for card component
- Repository uses SQL JOIN at infrastructure layer (community_members + profiles) — returns flat DTO, not domain entities
- Cursor-based pagination matching feed pattern (base64-encoded JSON offset)
- `useInfiniteQuery` with IntersectionObserver for infinite scroll
- Two-column layout matching HomePage (main content + CommunitySidebar)

**Parallel Execution:** Tasks within each phase are analyzed for dependencies. Independent tasks (e.g., frontend types vs. backend infrastructure) can be dispatched to parallel subagents by `/implement-feature` for faster execution. See the phase granular task plan for the dependency graph and parallel execution summary.

**Common Pitfalls:**
- Don't import Identity context types in Community domain layer — the JOIN is confined to infrastructure
- Don't use SELECT * — only select the specific columns needed (no email, no settings)
- Don't forget LEFT JOIN for profiles — members without profiles must still appear
- Don't skip the membership authorization check before returning data
- Don't use offset-based pagination — use cursor-based for consistency with feed

**Existing Components to Reuse:**
- `Avatar` (shared component) — `size="lg"` for 48px
- `CommunitySidebar` — right column on desktop
- `TabBar` — add "Members" tab entry
- Pattern from `SortDropdown` — create variant for directory sort options
