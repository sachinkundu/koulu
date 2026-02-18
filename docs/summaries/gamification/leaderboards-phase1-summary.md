# Leaderboards - Phase 1 Implementation Summary

**Date:** 2026-02-18
**Status:** Phase 1 of 2 — Complete
**PRD:** `docs/features/gamification/leaderboards-prd.md`
**BDD Spec:** `tests/features/gamification/leaderboards.feature`
**Branch:** `feature/leaderboard-page` (on `epic/leaderboards`)

---

## What Was Built

Phase 1 delivers the complete `/leaderboards` page with three side-by-side ranking panels (7-day, 30-day, all-time), a profile card showing the current user's level and points, a level definitions grid, gold/silver/bronze medals for top 3, and a "Your Rank" section for members outside the top 10. All ranking business logic — rolling windows, tie-breaking by display name, net-zero floor for negative period points — is implemented and tested with 13 passing BDD scenarios.

---

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| `ROW_NUMBER()` not `RANK()` | Sequential unique ranks (ties don't share a number per spec) |
| `GREATEST(0, SUM(points))` | Negative net period points floor at 0 (unlikes can't go negative) |
| Tie-breaking: `display_name ASC` | Alphabetical secondary sort as specified in TDD |
| CTE for ranking query | Clean separation of aggregation and `ROW_NUMBER()` window function |
| Cross-context JOIN to `profiles` table | Read-only — no event or shared aggregate; profiles needed for display_name + avatar_url |
| `_function_scoped_runner` for BDD async steps | pytest-bdd 8.1.0 doesn't support `async def` steps; sync wrapper pattern runs coroutines on the same event loop as pytest-asyncio fixtures |

---

## Files Changed

### Domain Layer
- `src/gamification/domain/value_objects/leaderboard_period.py` — `LeaderboardPeriod` enum (SEVEN_DAY, THIRTY_DAY, ALL_TIME) with hours window
- `src/gamification/domain/repositories/member_points_repository.py` — Added `LeaderboardEntry`, `LeaderboardResult` frozen dataclasses + `get_leaderboard()` abstract method

### Application Layer
- `src/gamification/application/queries/get_leaderboards.py` — `GetLeaderboardsQuery`, `LeaderboardPeriodResult`, `LeaderboardsResult` dataclasses, `GetLeaderboardsHandler` calling repo for all three periods

### Infrastructure Layer
- `src/gamification/infrastructure/persistence/member_points_repository.py` — `get_leaderboard()`, `_get_period_leaderboard()` (CTE + ROW_NUMBER + GREATEST), `_get_alltime_leaderboard()`, `_build_leaderboard_result()`
- `src/gamification/infrastructure/api/schemas.py` — `LeaderboardEntrySchema`, `LeaderboardPeriodSchema`, `LeaderboardsResponse`
- `src/gamification/interface/api/dependencies.py` — `get_get_leaderboards_handler` factory
- `src/gamification/interface/api/gamification_controller.py` — `GET /{community_id}/leaderboards` (router) + `GET /leaderboards` (default_router)

### Frontend
- `frontend/src/features/gamification/types/index.ts` — `LeaderboardEntry`, `LeaderboardPeriod`, `LeaderboardsResponse` interfaces
- `frontend/src/features/gamification/api/gamificationApi.ts` — `getLeaderboards()` API function
- `frontend/src/features/gamification/hooks/useLeaderboards.ts` — react-query hook
- `frontend/src/features/gamification/components/RankMedal.tsx` — Gold/silver/bronze emoji medals
- `frontend/src/features/gamification/components/LeaderboardRowSkeleton.tsx` — Shimmer loading placeholder
- `frontend/src/features/gamification/components/LeaderboardRow.tsx` — Ranked member row
- `frontend/src/features/gamification/components/YourRankSection.tsx` — Separator + highlighted row
- `frontend/src/features/gamification/components/LeaderboardPanel.tsx` — Full ranking card with states
- `frontend/src/features/gamification/components/LeaderboardProfileCard.tsx` — Current user profile card
- `frontend/src/pages/LeaderboardsPage.tsx` — Full page with profile card + level grid + 3 panels

### Tests
- `tests/features/gamification/leaderboards.feature` — 17 BDD scenarios (13 Phase 1, 4 Phase 2)
- `tests/features/gamification/test_leaderboards.py` — Step definitions using `_function_scoped_runner` pattern
- `tests/features/gamification/conftest.py` — Added `leaderboard_handler`, `create_member_points`, `create_point_transaction` fixtures
- `frontend/src/features/gamification/components/*.test.tsx` — 22 Vitest component tests

---

## BDD Scenarios Passing (13/17)

- [x] Member views the 7-day leaderboard with ranked members
- [x] Member views the 30-day leaderboard with rolled-up period points
- [x] Member views the all-time leaderboard using total accumulated points
- [x] Points earned in period shown with plus prefix for timed boards
- [x] Member outside top 10 sees their own rank below the list
- [x] Member inside top 10 does not receive a separate your-rank entry
- [x] Member with zero points in period still receives a your-rank entry
- [x] Fewer than 10 members in community shows all available members
- [x] Ties in points are broken alphabetically by display name
- [x] Negative net period points are displayed as zero
- [x] Points earned outside the rolling window are excluded
- [x] All-time leaderboard includes total accumulated points regardless of when earned
- [x] Member with 0 points in all periods has a rank in each leaderboard
- [ ] Community feed sidebar widget shows the 30-day top-5 leaderboard (Phase 2)
- [ ] Last updated timestamp is included in the leaderboard response (Phase 2)
- [ ] Unauthenticated user cannot view leaderboards (Phase 2)
- [ ] Unauthenticated user cannot view the sidebar widget (Phase 2)
- [ ] Member cannot view leaderboard for a community they do not belong to (Phase 2)

---

## Verification Results

```
pytest tests/features/gamification/test_leaderboards.py -v
======================== 13 passed, 5 skipped in 22.16s ========================

./scripts/verify.sh
852 passed, 5 skipped, 112 warnings in 45.97s
Coverage: 82.91%
✅ All Checks Passed (backend + frontend)
```

---

## How to Verify

1. Start the app: `docker compose up -d && uvicorn src.main:app --reload & cd frontend && npm run dev`
2. Open http://localhost:5173/leaderboards
3. Verify: profile card (top), level definitions grid, three ranking panels side by side
4. Members outside top 10 should see "Your Rank" section below the list

---

## Issues & Resolutions

| Issue | Resolution |
|-------|------------|
| pytest-bdd 8.1.0 doesn't await async steps | Used sync steps with `_function_scoped_runner: Runner` fixture from pytest-asyncio; wrap async logic in `async def _setup()` and call via `runner.run()` |
| `CommunityMemberModel` has no `id` column | Composite PK (`user_id`, `community_id`) — removed `id=uuid4()` from fixture |
| Worktree test database not created | Manually created `koulu_test` DB in the worktree's postgres container |
| pytest-bdd datatables return raw rows not dicts | Added `_table_to_dicts()` helper converting `Sequence[Sequence[str]]` to `list[dict]` |

---

## Deferred to Phase 2

- Sidebar widget endpoint (`GET /community/leaderboards/widget`) — 30-day top-5 compact view
- `last_updated` timestamp in leaderboard response
- Auth enforcement: unauthenticated users blocked
- Cross-community access denial

---

## Next Steps

- [ ] Phase 2: Sidebar widget + security + timestamp (see `leaderboards-implementation-phases.md`)
