# Leaderboards - Implementation Phases

## Complexity Analysis

| Metric | Count | Complexity |
|--------|-------|------------|
| BDD Scenarios | 17 | Medium |
| New Files | ~22 (4 backend, 15 frontend, 3 test) | Medium |
| Modified Files | ~8 (3 backend, 4 frontend, 1 test) | Medium |
| API Endpoints | 2 | Low |
| Dependencies | 1 context (Identity — read-only JOIN) | Low |

**Overall Complexity:** Medium

**Decision:** 2-phase implementation

**Strategy:** Vertical Slicing — each phase delivers a deployable increment with all layers (backend queries + API + frontend UI + BDD tests).

**Rationale:** Leaderboards is a read-only feature with no new aggregates, tables, or events. The backend is thin (2 query handlers, repository methods, 2 endpoints). The bulk of work is frontend components. Phase 1 delivers the complete `/leaderboards` page; Phase 2 adds the sidebar widget to the community feed. This split is natural because the two features are independent UI surfaces served by separate API endpoints.

---

## Phase 1: Full Leaderboard Page

### Goal

Deliver the complete `/leaderboards` page with three side-by-side ranking panels (7-day, 30-day, all-time), profile card, level definitions, medals, "Your rank" section, and loading/empty/error states. All ranking business logic (rolling windows, tie-breaking, net-zero floor) is implemented and tested.

### Scope

**Backend (Domain → API):**
- [ ] Value object: `src/gamification/domain/value_objects/leaderboard_period.py`
- [ ] Repository interface: extend `IMemberPointsRepository` with `get_leaderboard()` method
- [ ] Repository implementation: SQL queries for period aggregation and ranking in `SqlAlchemyMemberPointsRepository`
- [ ] Query handler: `src/gamification/application/queries/get_leaderboards.py`
- [ ] API schemas: leaderboard response schemas in `src/gamification/infrastructure/api/schemas.py`
- [ ] API endpoint: `GET /community/leaderboards` in `gamification_controller.py`
- [ ] DI wiring: handler factory in `dependencies.py`

**Frontend (User-Facing UI):**
- [ ] TypeScript types: leaderboard interfaces in `frontend/src/features/gamification/types/index.ts`
- [ ] API function: `getLeaderboards()` in `gamificationApi.ts`
- [ ] Hook: `useLeaderboards()` in `frontend/src/features/gamification/hooks/useLeaderboards.ts`
- [ ] Components:
  - [ ] `RankMedal.tsx` — gold/silver/bronze emoji
  - [ ] `LeaderboardRowSkeleton.tsx` — shimmer placeholder
  - [ ] `LeaderboardRow.tsx` — single ranked member row
  - [ ] `YourRankSection.tsx` — separator + highlighted row
  - [ ] `LeaderboardPanel.tsx` — full ranking card for one period
  - [ ] `LeaderboardProfileCard.tsx` — current user profile card
- [ ] Page: Enhanced `LeaderboardsPage.tsx` — complete layout with profile card + level definitions + timestamp + 3 panels
- [ ] Re-exports: update `hooks/index.ts` and `api/index.ts`

**Testing:**
- [ ] BDD scenarios: 13 scenarios (happy path + edge cases + security for main endpoint)
- [ ] Frontend component tests: Vitest tests for each new component

### BDD Scenarios

**Enabled for Phase 1 (13 scenarios):**
- [ ] Line 26: Member views the 7-day leaderboard with ranked members
- [ ] Line 49: Member views the 30-day leaderboard with rolled-up period points
- [ ] Line 58: Member views the all-time leaderboard using total accumulated points
- [ ] Line 68: Points earned in period shown with plus prefix for timed boards
- [ ] Line 77: Member outside top 10 sees their own rank below the list
- [ ] Line 96: Member inside top 10 does not receive a separate your-rank entry
- [ ] Line 102: Member with zero points in period still receives a your-rank entry
- [ ] Line 133: Fewer than 10 members in community shows all available members
- [ ] Line 144: Ties in points are broken alphabetically by display name
- [ ] Line 152: Negative net period points are displayed as zero
- [ ] Line 159: Points earned outside the rolling window are excluded
- [ ] Line 166: All-time leaderboard includes total accumulated points regardless of when earned
- [ ] Line 172: Member with 0 points in all periods has a rank in each leaderboard

**Skipped (Phase 2):**
- Line 114: Community feed sidebar widget shows the 30-day top-5 leaderboard → Phase 2: Sidebar widget
- Line 182: Last updated timestamp is included in the leaderboard response → Phase 2: Tested with widget endpoint
- Line 189: Unauthenticated user cannot view leaderboards → Phase 2: Security batch
- Line 194: Unauthenticated user cannot view the sidebar widget → Phase 2: Widget security
- Line 199: Member cannot view leaderboard for a community they do not belong to → Phase 2: Security batch

### Deliverable

**User can:** Navigate to `/leaderboards` and see their profile card, level definitions grid, and three side-by-side leaderboard panels showing the top 10 members for 7-day, 30-day, and all-time periods. Members outside the top 10 see their own rank below the list with a visual separator. Top 3 ranks display gold/silver/bronze medals.

**Verify by:** Navigate to `http://localhost:5173/leaderboards` — page shows profile card, levels grid, and three populated ranking panels.

### Dependencies

- None (first phase). Depends on existing Points & Levels implementation (complete).

### Estimated Time

4-5 hours

### Definition of Done

- [ ] All backend files created/modified
- [ ] All frontend components created with Vitest tests
- [ ] 13 BDD scenarios passing
- [ ] 4 scenarios skipped with Phase 2 markers
- [ ] `./scripts/verify.sh` passes (backend + frontend)
- [ ] No breaking changes to existing features
- [ ] Leaderboard page renders correctly at `/leaderboards`

### Verification Commands

```bash
# Run phase-specific BDD tests
eval "$(pyenv init -)" && eval "$(pyenv virtualenv-init -)" && pyenv activate koulu
pytest tests/features/gamification/test_leaderboards.py -v

# Full verification
./scripts/verify.sh
```

---

## Phase 2: Sidebar Widget + Security + Polish

### Goal

Add the compact 30-day leaderboard widget to the Community feed sidebar, implement the remaining BDD scenarios (widget, security, timestamp), and complete the feature.

### Scope

**Backend (Query + API):**
- [ ] Repository method: `get_leaderboard_widget()` on `SqlAlchemyMemberPointsRepository`
- [ ] Query handler: `src/gamification/application/queries/get_leaderboard_widget.py`
- [ ] API schemas: widget response schema
- [ ] API endpoint: `GET /community/leaderboards/widget`
- [ ] DI wiring: handler factory
- [ ] Security: explicit membership check for `/communities/{id}/leaderboards` variant

**Frontend (User-Facing UI):**
- [ ] API function: `getLeaderboardWidget()` in `gamificationApi.ts`
- [ ] Hook: `useLeaderboardWidget()` in `frontend/src/features/gamification/hooks/useLeaderboardWidget.ts`
- [ ] Component: `LeaderboardSidebarWidget.tsx` — compact 5-row widget
- [ ] Integration: `CommunitySidebar.tsx` — render widget below stats card
- [ ] Re-exports: update `hooks/index.ts` and `api/index.ts`

**Testing:**
- [ ] BDD scenarios: 4 remaining scenarios (widget + security)
- [ ] Frontend component tests: Vitest tests for widget

### BDD Scenarios

**Enabled for Phase 2 (4 scenarios):**
- [ ] Line 114: Community feed sidebar widget shows the 30-day top-5 leaderboard
- [ ] Line 182: Last updated timestamp is included in the leaderboard response
- [ ] Line 189: Unauthenticated user cannot view leaderboards
- [ ] Line 194: Unauthenticated user cannot view the sidebar widget
- [ ] Line 199: Member cannot view leaderboard for a community they do not belong to

**All Phase 1 scenarios remain passing.**

### Deliverable

**User can:** See a compact 30-day leaderboard in the Community feed sidebar (right column) showing the top 5 members with a "See all leaderboards" link that navigates to `/leaderboards`. Unauthenticated users are blocked. Cross-community access is denied.

**Verify by:** Navigate to `http://localhost:5173/` (community feed) — right sidebar shows the "Leaderboard (30-day)" widget below community stats. Click "See all leaderboards" navigates to `/leaderboards`.

### Dependencies

- Phase 1 complete

### Estimated Time

2-3 hours

### Definition of Done

- [ ] Widget renders in community feed sidebar
- [ ] 17 BDD scenarios passing (all)
- [ ] 0 scenarios skipped
- [ ] `./scripts/verify.sh` passes
- [ ] Widget fails silently on API error (feed not disrupted)

### Verification Commands

```bash
# Run all leaderboard BDD tests
eval "$(pyenv init -)" && eval "$(pyenv virtualenv-init -)" && pyenv activate koulu
pytest tests/features/gamification/test_leaderboards.py -v
# Expected: 17 passed, 0 skipped, 0 failed

# Full verification
./scripts/verify.sh
```

---

## Dependency Graph

```
Phase 1 (Full Leaderboard Page)
    │
    │ All ranking logic, 3 panels, profile card, level defs
    │ 13 BDD scenarios passing
    │
    ▼
Phase 2 (Sidebar Widget + Security + Polish)
    │
    │ Community feed widget, auth/authz enforcement
    │ All 17 BDD scenarios passing
    │
    ▼
  DONE
```

---

## Implementation Notes

**Patterns to Follow:**
- Follow existing gamification query patterns (`get_member_level.py`, `get_level_definitions.py`)
- Follow existing API endpoint patterns in `gamification_controller.py` (dual router: `router` + `default_router`)
- Follow existing frontend hook patterns (`useGamification.ts` → `react-query` with `queryKey`)
- Follow existing fixture patterns in `tests/features/gamification/conftest.py`

**Critical Query Patterns:**
- Period aggregation: JOIN `member_points` ↔ `point_transactions` with time filter, SUM + GREATEST(0, ...), ORDER BY points DESC + display_name ASC
- All-time: Direct ORDER BY on `member_points.total_points DESC`
- Your rank: `ROW_NUMBER()` window function, filter for current user
- Cross-context JOIN to `profiles` table for `display_name` and `avatar_url`

**Common Pitfalls:**
- Don't use `RANK()` — use `ROW_NUMBER()` for sequential unique ranks (no ties share a number)
- Don't forget `GREATEST(0, sum)` for period net points (negative net displays as 0)
- Don't forget tie-breaking by `display_name ASC` as secondary sort
- Don't forget to handle members with zero transactions in a period (they still get a rank for "your rank")
- Widget must fail silently — catch errors in the hook, return null/empty state
