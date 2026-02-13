# Member Directory — Phase 1 Implementation Summary

**Date:** 2026-02-13
**Status:** Phase 1 of 3 Complete
**PRD:** `docs/features/members/directory-prd.md`
**TDD:** `docs/features/members/directory-tdd.md`
**BDD Spec:** `tests/features/members/directory.feature`
**Phase Plan:** `docs/features/members/directory-implementation-phases.md`

---

## What Was Built

Phase 1 delivers a working member directory page where users can browse community members in a vertical list with infinite scroll pagination. Each member card displays avatar, display name, role badge (admin/moderator/member), bio (truncated to 2 lines), and join date. Members are sorted by join date descending (most recent first). The directory is accessible via a "Members" tab in the main navigation and shows a total member count badge.

---

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| Cross-context JOIN at infrastructure layer | Member data (community.community_members) and profile data (identity.profiles) live in separate bounded contexts. We perform LEFT JOIN in SqlAlchemyMemberRepository to project a flat DTO, avoiding N+1 queries while respecting context boundaries at the domain layer. |
| Cursor-based pagination with offset | Matches existing feed pattern. Cursor encodes `{"offset": N}` in base64. Simple, works for small communities (Phase 1 target), can upgrade to keyset pagination in Phase 3 if needed. |
| Role badges with Tailwind colors | Admin = yellow (`bg-yellow-500`), Moderator = blue (`bg-blue-500`), Member = hidden. Visual hierarchy makes community leadership immediately recognizable. |
| Infinite scroll with IntersectionObserver | Users expect social feed UX. Sentinel div triggers `fetchNextPage()` when scrolling near bottom. Shows loading skeletons during fetch. Matches existing feed behavior. |
| Frontend types mirror backend schemas | `DirectoryMember` interface matches `MemberDirectoryItemResponse` exactly. Type-safe API integration with no transformation layer needed. |

---

## Files Changed

### Application Layer
- `src/community/application/queries/__init__.py` — Added `ListMembersQuery` import (replaced old `queries.py` file)
- `src/community/application/queries/list_members_query.py` — NEW: Query object for directory listing
- `src/community/application/dtos/member_directory_entry.py` — NEW: Flat DTOs for cross-context projection (`MemberDirectoryEntry`, `MemberDirectoryResult`)
- `src/community/application/handlers/list_members_handler.py` — NEW: Query handler with membership check, cursor decode, and structlog logging
- `src/community/application/handlers/__init__.py` — Added `ListMembersHandler` export

### Domain Layer
- `src/community/domain/repositories/member_repository.py` — Extended `IMemberRepository` interface with `list_directory()` and `count_directory()` methods

### Infrastructure Layer
- `src/community/infrastructure/persistence/member_repository.py` — Implemented `list_directory()` with LEFT JOIN to `identity.profiles`, sort by join date or alphabetical, offset/limit pagination. Implemented `count_directory()` with `func.count()`.

### API Layer
- `src/community/interface/api/schemas.py` — Added `MemberDirectoryItemResponse` and `MemberDirectoryResponse` schemas
- `src/community/interface/api/dependencies.py` — Added `ListMembersHandlerDep` factory
- `src/community/interface/api/member_controller.py` — Added `GET /api/v1/community/members` endpoint with sort, limit, cursor params

### Frontend
- `frontend/src/features/members/types/members.ts` — NEW: `DirectoryMember`, `MembersQueryParams`, `MembersResponse` interfaces
- `frontend/src/features/members/api/memberApi.ts` — NEW: `getMembers()` API client function
- `frontend/src/features/members/hooks/useMembers.ts` — NEW: React Query `useInfiniteQuery` hook for infinite scroll
- `frontend/src/features/members/components/MemberCard.tsx` — NEW: Member card component with avatar, name, role badge, bio, join date, click to profile navigation
- `frontend/src/features/members/components/MemberCardSkeleton.tsx` — NEW: Loading skeleton matching card layout
- `frontend/src/features/members/components/MemberList.tsx` — NEW: Infinite scroll list with IntersectionObserver, loading/error/empty states
- `frontend/src/pages/MembersPage.tsx` — NEW: Two-column layout (MemberList + CommunitySidebar)
- `frontend/src/App.tsx` — Added Members tab to `APP_TABS`, added `/members` route with `MembersLayout`, route is protected with `ProtectedRoute`

### Tests
- `tests/features/members/directory.feature` — 23 scenarios (6 Phase 1, 11 Phase 2, 6 Phase 3)
- `tests/features/members/conftest.py` — NEW: `create_community` and `create_member_with_profile` factory fixtures
- `tests/features/members/test_directory.py` — NEW: BDD step definitions for all 23 scenarios (6 active, 17 skipped with phase markers)

---

## BDD Scenarios Passing

**Phase 1 (6 active):**
- [x] View member directory as a community member
- [x] Member directory shows correct member count
- [x] Sort members by most recent
- [x] Paginated member loading
- [x] Load second page of members
- [x] Load final page of members

**Phase 2 (11 skipped):**
- [ ] Search members by name → Phase 2: Requires search query param
- [ ] Search is case-insensitive → Phase 2: Requires search query param
- [ ] Search with partial name match → Phase 2: Requires search query param
- [ ] Filter members by admin role → Phase 2: Requires role filter param
- [ ] Filter members by moderator role → Phase 2: Requires role filter param
- [ ] Filter members by member role → Phase 2: Requires role filter param
- [ ] Sort members alphabetically → Phase 2: Requires alphabetical sort option
- [ ] Combine search with role filter → Phase 2: Requires search + filter combination
- [ ] Search returns no results → Phase 2: Requires search query param
- [ ] Filter returns no results → Phase 2: Requires role filter param
- [ ] Empty search query returns all members → Phase 2: Requires search query param

**Phase 3 (6 skipped):**
- [ ] Deactivated members are excluded from directory → Phase 3: Edge case — deactivated members
- [ ] Members without completed profiles appear with defaults → Phase 3: Edge case — incomplete profiles
- [ ] Member directory for community with single member → Phase 3: Edge case — single member community
- [ ] Unauthenticated user cannot access member directory → Phase 3: Security — authentication required
- [ ] Non-member cannot access community directory → Phase 3: Security — membership required
- [ ] Member directory does not expose private information → Phase 3: Security — no private data exposure

---

## How to Verify

**Automated:**
```bash
pytest tests/features/members/test_directory.py -v
# Expected: 6 passed, 17 skipped
```

**Manual:**
1. Start app: `./start.sh`
2. Open http://localhost:5173/community
3. Log in as any community member
4. Click **Members** tab in top navigation
5. Verify: member list appears with avatars, names, role badges, bios, join dates
6. Verify: members ordered by most recent join date first
7. Verify: total count badge shows correct number
8. Scroll down → more members load automatically (infinite scroll)
9. Click any member card → navigates to their profile page

---

## Issues & Resolutions

| Issue | Resolution |
|-------|------------|
| `queries.py` vs `queries/` package conflict | Python package system prioritizes `__init__.py` over module file. Merged `queries.py` content into `queries/__init__.py` and deleted the old file. |
| pytest-bdd async step functions not executing | All step functions (given, when, then) must be `async` and include `client: AsyncClient` param to maintain async fixture chain. Without `client` on sync steps, pytest-asyncio doesn't await coroutines → context dict stays empty → KeyError. |
| Ruff B904 lint error on exception handling | Added `as err` and `from err` to `raise HTTPException` in member controller to properly chain exceptions. |

---

## Deferred / Out of Scope

**Phase 2 (Search, Filter, Sort Options):**
- Search by name (case-insensitive, partial match)
- Filter by role with pill tabs
- Sort alphabetical option
- Combine search + filter

**Phase 3 (Edge Cases & Security):**
- Deactivated member handling
- Incomplete profile defaults
- Single-member community
- Unauthenticated/non-member access prevention
- Private data exposure checks

---

## Next Steps

- [ ] Phase 2: Implement search query param, role filter param, alphabetical sort option
- [ ] Phase 2: Add UI components — search input, role filter pills with counts
- [ ] Phase 3: Edge case handling, security hardening
- [ ] E2E tests (optional, after Phase 3 UI complete)
