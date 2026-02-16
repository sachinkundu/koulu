# Points & Levels Phase 2 - Implementation Summary

**Date:** 2026-02-16
**Status:** Phase 2 of 3 Complete
**PRD:** `docs/features/gamification/points-prd.md`
**BDD Spec:** `tests/features/gamification/points.feature`
**Implementation Plan:** `docs/features/gamification/points-implementation-phases.md`

---

## What Was Built

Phase 2 delivers full level visibility and admin configuration. Members now see their level badge, name, and progress on profiles. The level definitions grid shows all 9 levels with member distribution percentages. Admins can customize level names and point thresholds, with automatic member recalculation that respects the level ratchet rule (levels never decrease).

---

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| **HTML sanitization in domain** | Level names are stripped of HTML tags at the domain layer (`LevelConfiguration.update_levels()`) to prevent XSS without relying on external libraries — pure regex approach keeps domain dependency-free |
| **Member distribution calculation in query handler** | `GetLevelDefinitionsHandler` calculates percentage distribution on-the-fly from all members — simple, correct, and avoids denormalization complexity for MVP |
| **Ratchet-preserving recalculation** | When admin changes thresholds, `UpdateLevelConfigHandler` recalculates all member levels but preserves the ratchet invariant (levels never decrease) — ensures consistency without breaking the user trust |
| **AsyncMock for event_bus in tests** | Unit tests use `@patch(..., new_callable=AsyncMock)` to make `event_bus.publish_all` awaitable, matching the async handler pattern |
| **BDD tests at application layer** | Phase 2 BDD scenarios test via command/query handlers directly (not HTTP API) — faster execution, clearer intent, matches Phase 1 approach |

---

## Files Changed

### Domain Layer
- `src/gamification/domain/entities/level_configuration.py`
  - Added `MAX_LEVEL_NAME_LENGTH = 30` and `_HTML_TAG_RE` regex
  - Added `update_levels()` method with full validation: exactly 9 levels, HTML stripping, unique names (1-30 chars), level 1 threshold=0, strictly increasing thresholds
  - Raises `InvalidLevelNameError` or `InvalidThresholdError` on validation failure

### Application Layer
- `src/gamification/application/queries/get_level_definitions.py` — **NEW**
  - `GetLevelDefinitionsQuery` (community_id, requesting_user_id)
  - `LevelDefinitionResult`, `LevelDefinitionsResult` result dataclasses
  - `GetLevelDefinitionsHandler` — fetches all members, calculates % distribution per level, returns requesting user's current level
- `src/gamification/application/commands/update_level_config.py` — **NEW**
  - `LevelUpdate` frozen dataclass (level, name, threshold)
  - `UpdateLevelConfigCommand` (community_id, admin_user_id, levels)
  - `UpdateLevelConfigHandler` — calls domain `update_levels()`, saves, recalculates all member levels if thresholds changed, publishes `MemberLeveledUp` events

### Infrastructure Layer
- `src/gamification/infrastructure/api/schemas.py`
  - Added 4 Pydantic models: `LevelDefinitionSchema`, `LevelDefinitionsResponse`, `LevelUpdateSchema`, `UpdateLevelConfigRequest`
- `src/gamification/interface/api/gamification_controller.py`
  - **Fixed router prefix:** Changed from `prefix="/api/communities"` to `prefix="/communities"` (was causing double /api prefix)
  - Added `GET /{community_id}/levels` → `LevelDefinitionsResponse`
  - Added `PUT /{community_id}/levels` → `{"status": "ok"}`
- `src/gamification/interface/api/dependencies.py`
  - Added `get_get_level_definitions_handler()` and `get_update_level_config_handler()` dependency functions

### Frontend
- `frontend/src/features/gamification/types/index.ts`
  - Added `LevelDefinition`, `LevelDefinitionsResponse`, `LevelUpdateRequest` interfaces
- `frontend/src/features/gamification/api/gamificationApi.ts`
  - Added `getLevelDefinitions()` and `updateLevelConfig()` functions
- `frontend/src/features/gamification/components/ProfileLevelSection.tsx` — **NEW**
  - Shows level badge, level name ("Level 3 - Builder"), total points, and "X points to level Y" progress
  - Handles max level (Level 9) with "Max level reached" message
- `frontend/src/features/gamification/components/LevelDefinitionsGrid.tsx` — **NEW**
  - 3x3 grid of all 9 levels with names, thresholds ("100 points"), and member distribution ("25% of members")
  - Highlights current user's level with `bg-blue-50 border-blue-300`
- `frontend/src/features/identity/components/ProfileSidebar.tsx`
  - Added optional `levelInfo?: MemberLevel` prop
  - Renders `ProfileLevelSection` when `levelInfo` is provided

### Tests
- `tests/features/gamification/points.feature` — 40 scenarios total
- `tests/features/gamification/conftest.py`
  - Added `level_definitions_handler` and `update_level_config_handler` fixtures
- `tests/features/gamification/test_points.py`
  - **Removed skip markers** from 9 Phase 2 scenarios
  - **Implemented real step definitions** for all Phase 2 when/then steps:
    - `view_community_feed`, `view_member_directory`, `view_level_definitions` — query level data via handlers
    - `admin_updates_level_name`, `admin_updates_thresholds`, `admin_updates_single_threshold` — call `UpdateLevelConfigHandler`
    - `post_shows_level_badge`, `member_shows_level_badge`, `profile_shows_text`, `profile_shows_badge` — verify level data in context
    - `see_levels_displayed`, `level_named_with_threshold`, `level_named`, `level_shows_text`, `level_has_threshold` — verify level definitions
    - `user_still_at_level` — verify ratchet preservation after threshold change
    - `community_has_members`, `members_at_level` — bulk member creation for distribution tests
- `tests/unit/gamification/domain/test_level_configuration.py`
  - Added `TestUpdateLevels` class with 12 tests: valid update, name too long, empty name, whitespace-only, duplicate names, non-increasing thresholds, level 1 threshold not 0, wrong number of levels, HTML stripping, HTML-only name rejected, timestamp updated
- `tests/unit/gamification/application/test_get_level_definitions.py` — **NEW** (6 tests)
  - Returns all 9 levels, distribution calculation (50%/25%/25%), zero members, correct current user level, new user defaults to level 1, creates default config when none exists
- `tests/unit/gamification/application/test_update_level_config.py` — **NEW** (7 tests)
  - Successful config update, recalculates member levels when thresholds change, ratchet preserved when thresholds increase, publishes MemberLeveledUp events, no recalculation when only names change, creates default config when none exists, invalid config raises domain exception
- `frontend/src/features/gamification/components/ProfileLevelSection.test.tsx` — **NEW** (5 tests)
  - Renders level info, progress bar, points to next level, max level message, no undefined errors
- `frontend/src/features/gamification/components/LevelDefinitionsGrid.test.tsx` — **NEW** (5 tests)
  - Renders 9 levels, highlights current level, shows distribution percentages, displays thresholds, no undefined errors

---

## BDD Scenarios Passing

**Phase 1 (15 scenarios):**
- [x] Member earns a point when their post is liked
- [x] Member earns a point when their comment is liked
- [x] Point is deducted when a like is removed
- [x] Member earns points when creating a post
- [x] Member earns a point when commenting on a post
- [x] Member earns points when completing a lesson
- [x] No duplicate points for completing the same lesson twice
- [x] New member starts at Level 1
- [x] Member levels up when reaching point threshold
- [x] Member can skip levels with large point gains
- [x] Member sees points needed to reach next level
- [x] Level 9 member sees no level-up progress
- [x] Level does not decrease when points drop below threshold
- [x] Points cannot go below zero
- [x] Multiple point sources accumulate correctly

**Phase 2 (9 scenarios):**
- [x] Level badge shown on post author avatar
- [x] Level badge shown in member directory
- [x] Level information shown on member profile
- [x] Member can view all level definitions
- [x] Level definitions show percentage of members at each level
- [x] Admin customizes level names
- [x] Admin customizes point thresholds
- [x] Threshold change recalculates member levels
- [x] Level ratchet preserved when thresholds change

**Phase 3 (16 scenarios) — skipped with phase markers:**
- [ ] Member can access course when at required level
- [ ] Member cannot access course below required level
- [ ] Locked course visible in course list with lock indicator
- [ ] Course with no level requirement is accessible to all
- [ ] No points awarded for self-like attempt
- [ ] Level name too long is rejected
- [ ] Empty level name is rejected
- [ ] Duplicate level names are rejected
- [ ] Non-increasing thresholds are rejected
- [ ] Zero threshold for level 2 is rejected
- [ ] Unauthenticated user cannot view points
- [ ] Non-admin cannot configure levels
- [ ] Non-admin cannot set course level requirements
- [ ] Level name input is sanitized
- [ ] Admin lowers course level requirement grants immediate access
- [ ] Admin raises course level requirement revokes access

---

## How to Verify

**Backend API:**
```bash
# Get level definitions for a community (shows all 9 levels + distribution)
curl -H "Authorization: Bearer <token>" \
  http://localhost:8095/api/v1/communities/<community_id>/levels

# Update level config (admin)
curl -X PUT -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  http://localhost:8095/api/v1/communities/<community_id>/levels \
  -d '{"levels": [{"level":1,"name":"Newbie","threshold":0}, ...]}'
```

**Automated verification:**
```bash
# Run full verification (linting, mypy, tests, coverage)
./scripts/verify.sh

# Expected: 823 passed, 16 skipped, 7 warnings, coverage 83.95%

# Frontend tests + typecheck
cd frontend && npm run test -- --run && npm run typecheck

# Expected: 19 passed (4 test files)
```

**Manual testing:**
1. Open profile page — should see level badge, "Level X - Name", total points, "Y points to level Z"
2. Navigate to `/communities/{slug}/levels` — should see 3x3 grid with all 9 levels, member distribution, current level highlighted
3. As admin, use API to update level names or thresholds — verify members recalculate, ratchet is preserved

---

## Issues & Resolutions

| Issue | Resolution |
|-------|------------|
| **Double API prefix** | Router had `prefix="/api/communities"` but app mounts with `/api/v1`, creating `/api/v1/api/communities/...`. Fixed by changing to `prefix="/communities"` |
| **Mypy errors on None config** | After `config = lc_repo.get_by_community()` fallback to `context.get()`, mypy still saw `config` as potentially `None`. Added `assert config is not None` to satisfy type checker |
| **event_bus.publish_all not awaitable** | Unit tests used `@patch()` creating `MagicMock`, but handler calls `await event_bus.publish_all()`. Fixed by using `@patch(..., new_callable=AsyncMock)` |
| **HTML-only name test failure** | Test used `<script>alert('xss')</script>` which leaves `alert('xss')` after HTML stripping (not HTML-only). Fixed to use `<b><i></i></b>` (truly HTML-only) |
| **Test DB name mismatch** | BDD tests expected `koulu_test` but setup script created `koulu_test_koulu`. Created missing `koulu_test` database with `docker exec koulu_postgres psql -U koulu -c "CREATE DATABASE koulu_test;"` |

---

## Deferred / Out of Scope

- **Course level gating** — Phase 3 (requires Classroom context integration)
- **Validation error scenarios** — Phase 3 (comprehensive validation coverage)
- **Security/authz scenarios** — Phase 3 (non-admin cannot configure levels, unauthenticated access)
- **Admin UI for level configuration** — Out of scope (API-first, admin uses API directly or future admin panel)
- **Feed/directory badge integration** — Frontend components exist but not wired into feed/directory pages (Phase 3 or future work)

---

## Test Results

```
./scripts/verify.sh

✅ All Checks Passed!
823 passed, 16 skipped, 7 warnings in 107.07s
Coverage: 83.95%

Frontend:
19 passed (4 test files)
Typecheck: ✅
```

**Breakdown:**
- **Unit tests:** 89 passed (gamification context)
- **BDD tests:** 24 passed, 16 skipped (Phase 3)
- **Frontend tests:** 19 passed

---

## Next Steps

- [ ] **Phase 3:** Validation, Error Handling & Authorization (16 scenarios)
  - Course level gating (4 scenarios)
  - Validation errors (7 scenarios)
  - Security/authz (3 scenarios)
  - Edge cases (2 scenarios)
- [ ] Wire feed/directory badge display into UI (currently components exist but not integrated into feed/directory pages)
- [ ] Optional: Build admin UI for level configuration (currently API-only)
