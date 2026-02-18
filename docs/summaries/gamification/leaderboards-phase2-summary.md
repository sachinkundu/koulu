# Leaderboards - Phase 2 Implementation Summary

**Date:** 2026-02-18
**Status:** Complete (Phase 2 of 2 — all phases done)
**PRD:** `docs/features/gamification/leaderboards-prd.md`
**BDD Spec:** `tests/features/gamification/leaderboards.feature`
**Branch:** `feature/leaderboard-page` (on `epic/leaderboards`)

---

## What Was Built

Phase 2 completes the Leaderboards feature by adding the compact 30-day leaderboard widget to the Community feed sidebar, enforcing authentication and membership checks on all leaderboard endpoints, and enabling the last_updated timestamp. All 18 BDD scenarios now pass (0 skipped), and the leaderboard sidebar widget renders directly on the community feed page that members visit every session.

---

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| Widget fails silently (returns `null`) | Feed page must not break if the widget API errors; React component returns null and the sidebar renders without it |
| Membership check on `/communities/{id}/leaderboards` | Phase 2 spec requires 403 for non-members; default_router (`/community/leaderboards`) remains open (auto-resolves to the user's community) |
| Widget endpoint reuses existing `_period_leaderboard` SQL pattern | Same CTE + ROW_NUMBER query, no `your_rank` since widget doesn't need it, with `limit=5` |
| BDD security steps use `AsyncClient` via `_function_scoped_runner` | Follows same sync+Runner pattern established in Phase 1; HTTP client needed for 401/403 status verification |
| JWT token generated in test via `JWTService.generate_auth_tokens()` | Allows testing authenticated cross-community requests without a full login flow |

---

## Files Changed

### Domain Layer
- `src/gamification/domain/repositories/member_points_repository.py` — Added `get_leaderboard_widget()` abstract method returning `list[LeaderboardEntry]`

### Application Layer
- `src/gamification/application/queries/get_leaderboard_widget.py` *(new)* — `GetLeaderboardWidgetQuery`, `LeaderboardWidgetResult`, `GetLeaderboardWidgetHandler` (top-5, 30-day)

### Infrastructure Layer
- `src/gamification/infrastructure/persistence/member_points_repository.py` — Added `get_leaderboard_widget()` SQL implementation (CTE + ROW_NUMBER, 30-day window, limit=5)
- `src/gamification/infrastructure/api/schemas.py` — Added `LeaderboardWidgetResponse` schema
- `src/gamification/interface/api/dependencies.py` — Added `get_get_leaderboard_widget_handler` factory
- `src/gamification/interface/api/gamification_controller.py` — Added `_require_membership()` helper, `GET /{community_id}/leaderboards/widget` and `GET /leaderboards/widget` endpoints; membership check on `GET /{community_id}/leaderboards`

### Frontend
- `frontend/src/features/gamification/types/index.ts` — Added `LeaderboardWidgetResponse` interface
- `frontend/src/features/gamification/api/gamificationApi.ts` — Added `getLeaderboardWidget()` API function
- `frontend/src/features/gamification/api/index.ts` — Re-exported `getLeaderboardWidget`
- `frontend/src/features/gamification/hooks/useLeaderboardWidget.ts` *(new)* — react-query hook for widget data
- `frontend/src/features/gamification/hooks/index.ts` — Re-exported `useLeaderboardWidget`
- `frontend/src/features/gamification/components/LeaderboardSidebarWidget.tsx` *(new)* — Compact 5-row widget with medals, loading skeleton, silent error fallback, "See all leaderboards" link
- `frontend/src/features/community/components/CommunitySidebar.tsx` — Integrated `LeaderboardSidebarWidget` below community stats

### Tests
- `tests/features/gamification/test_leaderboards.py` — Removed 5 skip markers; added widget steps (Given/When/Then), timestamp step, security steps (unauthenticated + cross-community)
- `tests/features/gamification/conftest.py` — Added `widget_handler` fixture (`GetLeaderboardWidgetHandler`)
- `frontend/src/features/gamification/components/LeaderboardSidebarWidget.test.tsx` *(new)* — 6 Vitest tests covering render, entries, medals, link, error silence, loading skeleton

---

## BDD Scenarios Passing (18/18)

- [x] Member views the 7-day leaderboard with ranked members
- [x] Member views the 30-day leaderboard with rolled-up period points
- [x] Member views the all-time leaderboard using total accumulated points
- [x] Points earned in period shown with plus prefix for timed boards
- [x] Member outside top 10 sees their own rank below the list
- [x] Member inside top 10 does not receive a separate your-rank entry
- [x] Member with zero points in period still receives a your-rank entry
- [x] Community feed sidebar widget shows the 30-day top-5 leaderboard *(Phase 2)*
- [x] Fewer than 10 members in community shows all available members
- [x] Ties in points are broken alphabetically by display name
- [x] Negative net period points are displayed as zero
- [x] Points earned outside the rolling window are excluded
- [x] All-time leaderboard includes total accumulated points regardless of when earned
- [x] Member with 0 points in all periods has a rank in each leaderboard
- [x] Last updated timestamp is included in the leaderboard response *(Phase 2)*
- [x] Unauthenticated user cannot view leaderboards *(Phase 2)*
- [x] Unauthenticated user cannot view the sidebar widget *(Phase 2)*
- [x] Member cannot view leaderboard for a community they do not belong to *(Phase 2)*

---

## Verification Results

```
pytest tests/features/gamification/test_leaderboards.py -v
======================== 18 passed in 15.83s ==============================

./scripts/verify.sh
857 passed, 112 warnings in 31.79s
Coverage: 82.96%
✅ All Checks Passed (backend + frontend)
```

---

## How to Verify

1. Start the app: `./start.sh`
2. Open http://localhost:5173/ (community feed)
3. Right sidebar — below community stats — shows "Leaderboard (30-day)" widget with top 5 members
4. Click "See all leaderboards" → navigates to `/leaderboards` (full page with 3 panels)
5. Unauthenticated requests to `/api/v1/communities/{id}/leaderboards` return 401

---

## Issues & Resolutions

| Issue | Resolution |
|-------|------------|
| `generate_access_token` method doesn't exist on `JWTService` | Used `generate_auth_tokens()` returning `AuthTokens`; accessed `.access_token` field |
| `typing.Any` not imported in gamification controller | Added to the `from typing import Annotated, Any` import |
| ruff import sort violation in test file | Applied `ruff check --fix` to auto-sort imports |

---

## Feature Complete

The Leaderboards feature is fully implemented across both phases:
- **Phase 1:** `/leaderboards` page with profile card, level definitions, and 3 ranking panels
- **Phase 2:** Sidebar widget on community feed, auth/authz enforcement, last_updated timestamp
