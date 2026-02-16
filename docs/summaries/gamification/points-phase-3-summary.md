# Points & Levels Phase 3 - Implementation Summary

**Date:** 2026-02-16
**Status:** Phase 3 of 3 Complete — ALL 40 BDD scenarios passing
**PRD:** `docs/features/gamification/points-prd.md`
**BDD Spec:** `tests/features/gamification/points.feature`
**Implementation Plan:** `docs/features/gamification/points-implementation-phases.md`

---

## What Was Built

Phase 3 delivers course-level gating, validation error handling, and comprehensive security. Admins can set minimum level requirements on courses — members below the threshold see lock indicators and "Unlock at Level X" messages. Full validation prevents invalid admin input (long names, empty names, duplicates, non-increasing thresholds, zero thresholds). Security ensures unauthenticated requests return 401, non-admin attempts to configure levels or course requirements return 403, and XSS attacks via level names are sanitized at the domain layer.

Frontend includes `CourseCardLock` component with lock overlay UI. All 40 BDD scenarios (spanning all 3 phases) now pass with 0 skipped, 0 failed, 83.80% coverage.

---

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| **Course gating via separate aggregate** | `CourseLevelRequirement` is its own domain entity (not embedded in `Course`) — follows DDD bounded context rules (gamification owns gating, classroom owns courses) and allows independent evolution |
| **Admin role check in controller** | Admin verification (`_require_admin()`) queries `SqlAlchemyMemberRepository` and checks `MemberRole.ADMIN` directly in the controller — simpler than handler-based checks since gamification doesn't own member concept |
| **Domain validation reused** | Phase 3 validation scenarios use existing `LevelConfiguration.update_levels()` validation logic — no new validation code needed, just test coverage for edge cases |
| **BDD tests mix handler + API** | Security scenarios (401/403) use HTTP API via `client`, validation scenarios use handlers directly — minimizes HTTP overhead while testing auth boundary correctly |
| **Frontend lock overlay component** | `CourseCardLock` is a reusable overlay component that wraps course cards — returns `null` when unlocked, shows lock icon + level requirement when access denied |
| **XSS sanitization documented** | Phase 2 already implemented HTML tag stripping in domain (`LevelConfiguration._HTML_TAG_RE`) — Phase 3 just adds BDD test coverage to verify it works |

---

## Files Changed

### Domain Layer
- `src/gamification/domain/entities/course_level_requirement.py` — **NEW**
  - Domain entity with `community_id`, `course_id`, `minimum_level` fields
  - `create()` factory method and `update_minimum_level()` behavior method
  - Extends `BaseEntity[UUID]`

- `src/gamification/domain/repositories/course_level_requirement_repository.py` — **NEW**
  - `ICourseLevelRequirementRepository` interface
  - Methods: `save()`, `get_by_community_and_course()`, `delete()`

- `src/gamification/domain/repositories/__init__.py`
  - Added `ICourseLevelRequirementRepository` export

- `src/gamification/domain/exceptions.py`
  - Added `NotAdminError` exception (used in handler-level admin checks, but current impl does controller-level checks instead)

### Application Layer
- `src/gamification/application/commands/set_course_level_requirement.py` — **NEW**
  - `SetCourseLevelRequirementCommand` (community_id, course_id, admin_user_id, minimum_level)
  - `SetCourseLevelRequirementHandler` — creates or updates course level requirement via repository
  - Logs `course_level_requirement_set` event

- `src/gamification/application/queries/check_course_access.py` — **NEW**
  - `CheckCourseAccessQuery` (community_id, course_id, user_id)
  - `CourseAccessResult` (course_id, has_access, minimum_level, minimum_level_name, current_level)
  - `CheckCourseAccessHandler` — queries member points, level config, course requirement; calculates access based on current_level >= minimum_level

### Infrastructure Layer
- `src/gamification/infrastructure/persistence/models.py`
  - Added `CourseLevelRequirementModel` with columns: id, community_id, course_id, minimum_level, created_at, updated_at
  - Unique constraint: `uq_course_level_req_community_course` on `(community_id, course_id)`

- `src/gamification/infrastructure/persistence/course_level_requirement_repository.py` — **NEW**
  - SQLAlchemy implementation of `ICourseLevelRequirementRepository`
  - `save()` handles create-or-update via merge
  - `get_by_community_and_course()` filters by composite key
  - `delete()` removes by composite key

- `alembic/versions/8782370332f4_add_course_level_requirements_table.py` — **NEW**
  - Migration creating `course_level_requirements` table
  - Down revision: `a1b2c3d4e5f6`

- `src/gamification/infrastructure/api/schemas.py`
  - Added `CourseAccessResponse` (course_id, has_access, minimum_level, minimum_level_name, current_level)
  - Added `SetCourseLevelRequirementRequest` (minimum_level)

- `src/gamification/interface/api/dependencies.py`
  - Added `get_course_req_repo()`, `CourseReqRepoDep`
  - Added `get_check_course_access_handler()`, `get_set_course_level_requirement_handler()`

- `src/gamification/interface/api/gamification_controller.py`
  - **MAJOR REWRITE**: Added `_require_admin()` helper that queries member repo and checks `MemberRole.ADMIN`, raises `HTTPException(403)` if not admin
  - Added admin check to `PUT /communities/{id}/levels` endpoint
  - Added validation error handling: catches `InvalidLevelNameError`, `InvalidThresholdError`, `GamificationDomainError` → returns 400 with error message
  - Added `GET /communities/{id}/courses/{course_id}/access` endpoint — returns course access result
  - Added `PUT /communities/{id}/courses/{course_id}/level-requirement` endpoint (admin only) — sets minimum level for course

### Frontend
- `frontend/src/features/gamification/components/CourseCardLock.tsx` — **NEW**
  - Lock overlay component with lock icon and "Unlock at Level X - Name" text
  - Props: `hasAccess`, `minimumLevel`, `minimumLevelName`
  - Returns `null` when `hasAccess` is true
  - Styled with TailwindCSS: absolute positioning, semi-transparent backdrop, centered flex layout

- `frontend/src/features/gamification/components/CourseCardLock.test.tsx` — **NEW**
  - 4 tests: locked state rendering, unlocked when meeting requirement, unlocked when exceeding requirement, lock icon presence

- `frontend/src/features/gamification/types/index.ts`
  - Added `CourseAccessResponse` interface
  - Added `SetCourseLevelRequirementRequest` interface

- `frontend/src/features/gamification/api/gamificationApi.ts`
  - Added `checkCourseAccess(communityId, courseId)` — GET endpoint wrapper
  - Added `setCourseLevelRequirement(communityId, courseId, minimumLevel)` — PUT endpoint wrapper

- `frontend/src/features/gamification/api/index.ts`
  - Updated re-exports to include new API functions

### Tests
- `tests/features/gamification/points.feature` — 40 scenarios total (no changes, all scenarios now enabled)

- `tests/features/gamification/conftest.py`
  - Added `course_req_repo` fixture → `SqlAlchemyCourseLevelRequirementRepository`
  - Added `check_course_access_handler` fixture → `CheckCourseAccessHandler`
  - Added `set_course_req_handler` fixture → `SetCourseLevelRequirementHandler`

- `tests/features/gamification/test_points.py`
  - Removed all 16 `@pytest.mark.skip` markers for Phase 3 scenarios
  - Implemented 12 `given` step definitions for course setup (with/without level requirements)
  - Implemented 11 `when` step definitions for course access attempts, self-like attempts, validation edge cases, security scenarios
  - Implemented 13 `then` step definitions for access assertions, validation error checks, security status checks, XSS sanitization checks
  - Total: ~2200 lines of BDD test code covering all 40 scenarios

---

## BDD Scenarios Passing

### Phase 1 - Core Engine (8 scenarios)
- [x] Member earns a point when their post is liked
- [x] Member earns a point when their comment is liked
- [x] Point is deducted when a like is removed
- [x] Member earns points when creating a post
- [x] Member earns a point when commenting on a post
- [x] Member earns points when completing a lesson
- [x] No duplicate points for completing the same lesson twice
- [x] New member starts at level 1
- [x] Member levels up when reaching point threshold
- [x] Member can skip levels with large point gains
- [x] Member sees points needed to reach next level
- [x] Level 9 member sees no level-up progress
- [x] Level does not decrease when points drop below threshold
- [x] Points cannot go below zero
- [x] Multiple point sources accumulate correctly

### Phase 2 - Display & Admin Config (9 scenarios)
- [x] Level badge shown on post author avatar
- [x] Level badge shown in member directory
- [x] Level information shown on member profile
- [x] Member can view all level definitions
- [x] Level definitions show percentage of members at each level
- [x] Admin customizes level names
- [x] Admin customizes point thresholds
- [x] Threshold change recalculates member levels
- [x] Level ratchet preserved when thresholds change

### Phase 3 - Gating, Validation & Security (16 scenarios)

**Course Gating (4 + 2 edge cases):**
- [x] Member can access course when at required level
- [x] Member cannot access course below required level
- [x] Locked course visible in course list with lock indicator
- [x] Course with no level requirement is accessible to all
- [x] Admin lowers course level requirement → grants immediate access
- [x] Admin raises course level requirement → revokes access

**Validation Errors (5 + 1):**
- [x] Level name too long is rejected
- [x] Empty level name is rejected
- [x] Duplicate level names are rejected
- [x] Non-increasing thresholds are rejected
- [x] Zero threshold for level 2+ is rejected
- [x] No points awarded for self-like attempt

**Security (4):**
- [x] Unauthenticated user cannot view points
- [x] Non-admin cannot configure levels
- [x] Non-admin cannot set course level requirements
- [x] Level name input is sanitized (XSS prevented)

---

## How to Verify

### Backend (curl)

1. **Set course level requirement (admin):**
   ```bash
   curl -X PUT http://localhost:8000/api/v1/communities/{community_id}/courses/{course_id}/level-requirement \
     -H "Authorization: Bearer {admin_token}" \
     -H "Content-Type: application/json" \
     -d '{"minimum_level": 3}'
   ```

2. **Check course access:**
   ```bash
   curl http://localhost:8000/api/v1/communities/{community_id}/courses/{course_id}/access \
     -H "Authorization: Bearer {token}"
   # Response: {"course_id": "...", "has_access": false, "minimum_level": 3, "minimum_level_name": "Builder", "current_level": 1}
   ```

3. **Non-admin attempt → 403:**
   ```bash
   curl -X PUT http://localhost:8000/api/v1/communities/{community_id}/levels \
     -H "Authorization: Bearer {member_token}" \
     -H "Content-Type: application/json" \
     -d '{"levels": [...]}'
   # Response: 403 Forbidden
   ```

4. **Validation error → 400:**
   ```bash
   curl -X PUT http://localhost:8000/api/v1/communities/{community_id}/levels \
     -H "Authorization: Bearer {admin_token}" \
     -H "Content-Type: application/json" \
     -d '{"levels": [{"level": 1, "name": "This name is way too long and exceeds the 30 character limit", "threshold": 0}, ...]}'
   # Response: 400 Bad Request - "Level name must be 30 characters or less"
   ```

### Frontend (manual)

1. **Lock overlay on locked course:**
   - Navigate to course list (when integrated)
   - Courses with `has_access: false` should show lock icon overlay
   - Hover text: "Unlock at Level {X} - {Name}"

2. **No lock on accessible course:**
   - Courses with `has_access: true` should NOT show lock overlay
   - Normal course card rendering

### Automated Tests

```bash
pytest tests/features/gamification/test_points.py -v
# Result: 40 passed, 0 skipped, 0 failed
```

---

## Issues & Resolutions

| Issue | Resolution |
|-------|------------|
| **Alembic autogenerate detected spurious removals** | Backend agent initially created migration with `op.drop_table()` calls for existing tables (level_configurations, member_points). Fixed by rewriting migration to only include `op.create_table("course_level_requirements", ...)` |
| **Import ordering in controller** | Ruff flagged unordered imports. Fixed by reorganizing imports: stdlib → third-party → local, with structlog before fastapi imports |
| **Unused `NotAdminError` import** | `set_course_level_requirement.py` imported but didn't use `NotAdminError` (admin checks moved to controller). Removed import. |
| **Unused `SqlAlchemyCourseLevelRequirementRepository` in test** | `test_points.py` imported repository directly but used it via fixtures. Removed direct import. |
| **Unused `user_id` variable in `attempt_self_like`** | Extracted `user_id` but never used it (auth token enough). Removed variable assignment. |
| **Parser parameter name mismatch** | Initial `then` step used `{status:d}` but function param was `status_code`. Fixed to use `{status_code:d}` consistently. |
| **Pytest warnings (7)** | Pre-existing warnings from unknown BDD marks (`@display`, `@admin`, etc.) and test class collection. Not caused by Phase 3 changes, do not block completion. |

---

## Deferred / Out of Scope

- **Classroom integration:** Courses are stubbed in tests (`context["courses"]`). Actual course list UI + integration deferred until classroom context is built.
- **Real-time lock state updates:** If admin changes course requirement, frontend doesn't auto-refresh. User must reload page. Real-time updates deferred to WebSocket implementation.
- **Bulk course requirement management:** Setting levels for multiple courses requires multiple API calls. Bulk endpoint deferred to future optimization phase.
- **Course access audit log:** No logging of denied access attempts. Deferred to observability/analytics phase.

---

## Next Steps

**Feature is COMPLETE — all 3 phases done.**

Optional enhancements (not required for MVP):
- [ ] Add E2E tests for course lock overlay (Playwright)
- [ ] Real-time updates for lock state changes (WebSocket)
- [ ] Bulk course requirement management endpoint
- [ ] Course access analytics dashboard (admin)
