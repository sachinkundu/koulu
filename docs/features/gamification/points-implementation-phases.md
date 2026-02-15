# Points & Levels - Implementation Phases

## Complexity Analysis

| Metric | Count | Complexity |
|--------|-------|------------|
| BDD Scenarios | 40 | High |
| New Files | ~35 | High |
| Modified Files | ~6 | Medium |
| API Endpoints | 5 | Medium |
| Dependencies | 2 contexts (Community, Classroom) | Medium |

**Overall Complexity:** High

**Decision:** 3-phase implementation

**Strategy:** Vertical Slicing — each phase delivers a working feature slice across all layers (domain, application, infrastructure, API, frontend, tests). Every phase ends with green CI.

---

## Phase 1: Core Points Engine + Level Calculation

### Goal

Members earn points from engagement actions (likes, posts, comments, lesson completions) and automatically level up through a 9-level progression. Level badges appear on avatars across the platform.

### Scope

**Backend (Domain -> API):**
- [ ] Value objects: `PointSource`, `LevelNumber`, `LevelName`, `PointTransaction`
- [ ] Domain exceptions: `InvalidLevelNameError`, `InvalidThresholdError`, `InvalidLevelNumberError`, `DuplicateLessonCompletionError`
- [ ] Domain events: `PointsAwarded`, `PointsDeducted`, `MemberLeveledUp`
- [ ] Entity: `LevelConfiguration` aggregate (with defaults, `get_level_for_points`)
- [ ] Entity: `MemberPoints` aggregate (`award_points`, `deduct_points`, ratchet behavior)
- [ ] Repository interfaces: `IMemberPointsRepository`, `ILevelConfigRepository`
- [ ] SQLAlchemy models: `MemberPointsModel`, `PointTransactionModel`, `LevelConfigurationModel`
- [ ] Alembic migration: Create `member_points`, `point_transactions`, `level_configurations` tables
- [ ] Repository implementations: `SqlAlchemyMemberPointsRepository`, `SqlAlchemyLevelConfigRepository`
- [ ] Commands: `AwardPointsCommand` + handler, `DeductPointsCommand` + handler
- [ ] Query: `GetMemberLevelQuery` + handler
- [ ] Event handlers: `PostCreated`, `PostLiked`, `PostUnliked`, `CommentAdded`, `CommentLiked`, `CommentUnliked`, `LessonCompleted`
- [ ] Community event enrichment: Add `author_id` to `PostLiked`, `PostUnliked`, `CommentLiked`, `CommentUnliked`
- [ ] API endpoint: `GET /api/communities/{id}/members/{user_id}/level`
- [ ] API schemas: `MemberLevelResponse`

**Frontend (User-Facing UI):**
- [ ] TypeScript types: `MemberLevel`, `PointSource`
- [ ] API client: `getMemberLevel()`
- [ ] `LevelBadge` component (reusable badge overlay)
- [ ] `Avatar` enhancement: optional `level` prop with badge overlay

**Testing:**
- [ ] Unit tests: Value objects, MemberPoints aggregate, LevelConfiguration entity
- [ ] BDD scenarios (API-level): 15 scenarios enabled
- [ ] Frontend component tests: LevelBadge, Avatar with level

### BDD Scenarios

**Enabled for this phase (15):**
- [ ] Line 26: Member earns a point when their post is liked
- [ ] Line 35: Member earns a point when their comment is liked
- [ ] Line 46: Point is deducted when a like is removed
- [ ] Line 62: Member earns points when creating a post
- [ ] Line 69: Member earns a point when commenting on a post
- [ ] Line 83: Member earns points when completing a lesson
- [ ] Line 91: No duplicate points for completing the same lesson twice
- [ ] Line 104: New member starts at Level 1
- [ ] Line 112: Member levels up when reaching point threshold
- [ ] Line 122: Member can skip levels with large point gains
- [ ] Line 132: Member sees points needed to reach next level
- [ ] Line 140: Level 9 member sees no level-up progress
- [ ] Line 154: Level does not decrease when points drop below threshold
- [ ] Line 166: Points cannot go below zero
- [ ] Line 394: Multiple point sources accumulate correctly

**Skipped (future phases):**
- Lines 179-199: Display scenarios -> Phase 2: Requires ProfileLevelSection and feed integration
- Lines 207-223: Level definitions -> Phase 2: Requires GetLevelDefinitions query and grid component
- Lines 231-262: Course access -> Phase 3: Requires course gating infrastructure
- Lines 270-302: Admin config -> Phase 2: Requires UpdateLevelConfig command and admin UI
- Lines 310-355: Validation errors -> Phase 3: Requires full validation coverage
- Lines 363-387: Security -> Phase 3: Requires auth/authz enforcement on all endpoints
- Lines 404-431: Edge cases (course gating, ratchet on threshold change) -> Phase 2/3

### Deliverable
**User can:** Earn points from community engagement (liking, posting, commenting, completing lessons), see their level badge on avatars, and view their current level and points via the member level API.

### Dependencies
- None (first phase)
- Requires existing Community and Classroom event infrastructure

### Estimated Time
4-5 hours

### Definition of Done
- [ ] All gamification domain files created
- [ ] 15 BDD scenarios passing
- [ ] 25 remaining scenarios skipped with phase markers
- [ ] Unit tests for all value objects and entities
- [ ] Linting passes (ruff check + ruff format)
- [ ] Type checking passes (mypy)
- [ ] No breaking changes to Community or Classroom contexts
- [ ] `./scripts/verify.sh` green
- [ ] Frontend LevelBadge renders correctly with Vitest tests

### Verification Commands
```bash
# Run phase-specific tests
pytest tests/features/gamification/test_points.py -v
# Expected: 15 passed, 25 skipped (Phase markers visible)

# Run unit tests
pytest tests/unit/gamification/ -v

# Verify all skips have phase markers
grep -r "@pytest.mark.skip" tests/features/gamification/ | grep "Phase [0-9]"

# Full verification
./scripts/verify.sh

# Frontend
cd frontend && npm run test -- --run && npm run typecheck
```

---

## Phase 2: Level Display, Definitions & Admin Configuration

### Goal

Members see full level information on profiles (their own and others'), browse all 9 level definitions with member distribution, and admins can customize level names and thresholds.

### Scope

**Backend (Domain -> API):**
- [ ] Query: `GetLevelDefinitionsQuery` + handler (with member distribution calculation)
- [ ] Command: `UpdateLevelConfigCommand` + handler (with member level recalculation)
- [ ] API endpoint: `GET /api/communities/{id}/levels`
- [ ] API endpoint: `PUT /api/communities/{id}/levels`
- [ ] API schemas: `LevelDefinitionsResponse`, `UpdateLevelConfigRequest`

**Frontend (User-Facing UI):**
- [ ] API client: `getLevelDefinitions()`, `updateLevelConfig()`
- [ ] `ProfileLevelSection` component (level name, points to next level)
- [ ] `LevelDefinitionsGrid` component (9-level grid with distribution)
- [ ] `ProfileSidebar` enhancement: integrate ProfileLevelSection
- [ ] Feed post avatar badge integration (pass level to Avatar)
- [ ] Member directory badge integration

**Testing:**
- [ ] BDD scenarios (API-level): 9 scenarios enabled (cumulative: 24)
- [ ] Frontend component tests: ProfileLevelSection, LevelDefinitionsGrid

### BDD Scenarios

**Enabled for this phase (9):**
- [ ] Line 179: Level badge shown on post author avatar
- [ ] Line 186: Level badge shown in member directory
- [ ] Line 193: Level information shown on member profile
- [ ] Line 207: Member can view all level definitions
- [ ] Line 215: Level definitions show percentage of members at each level
- [ ] Line 270: Admin customizes level names
- [ ] Line 278: Admin customizes point thresholds
- [ ] Line 295: Threshold change recalculates member levels
- [ ] Line 424: Level ratchet preserved when thresholds change

**Skipped (Phase 3):**
- Lines 231-262: Course access -> Phase 3
- Lines 310-355: Validation errors -> Phase 3
- Lines 363-387: Security -> Phase 3
- Lines 404-421: Course gating edge cases -> Phase 3

### Deliverable
**User can:** See level badges on all avatars throughout the platform, view their level name and "X points to level up" on their profile, browse the level definitions grid on the leaderboards page. **Admin can:** Customize level names and point thresholds, with member levels recalculated immediately.

### Dependencies
- Phase 1 must be complete

### Estimated Time
3-4 hours

### Definition of Done
- [ ] 24 BDD scenarios passing (cumulative)
- [ ] 16 remaining scenarios skipped with phase markers
- [ ] Frontend profile integration complete
- [ ] Admin configuration functional
- [ ] `./scripts/verify.sh` green

### Verification Commands
```bash
pytest tests/features/gamification/test_points.py -v
# Expected: 24 passed, 16 skipped

./scripts/verify.sh

cd frontend && npm run test -- --run && npm run typecheck
```

---

## Phase 3: Course Gating, Validation & Security

### Goal

Admins can gate courses behind level requirements, full input validation for admin configuration, security enforcement on all endpoints, and all remaining edge cases covered.

### Scope

**Backend (Domain -> API):**
- [ ] Database: `course_level_requirements` table (migration)
- [ ] Command: `SetCourseLevelRequirementCommand` + handler
- [ ] Query: `CheckCourseAccessQuery` + handler
- [ ] API endpoint: `GET /api/communities/{id}/courses/{course_id}/access`
- [ ] API endpoint: `PUT /api/communities/{id}/courses/{course_id}/level-requirement`
- [ ] Full input validation: level names (length, uniqueness, XSS sanitization), thresholds (increasing, positive)
- [ ] Security: auth checks on all endpoints, admin-only enforcement
- [ ] API schemas: `CourseAccessResponse`, `SetCourseLevelRequirementRequest`

**Frontend (User-Facing UI):**
- [ ] API client: `checkCourseAccess()`, `setCourseLevelRequirement()`
- [ ] `CourseCardLock` component (lock overlay with level requirement)
- [ ] `CourseCard` enhancement: integrate lock overlay
- [ ] Admin course level requirement UI

**Testing:**
- [ ] BDD scenarios (API-level): 16 scenarios enabled (cumulative: 40)
- [ ] Frontend component tests: CourseCardLock

### BDD Scenarios

**Enabled for this phase (16):**
- [ ] Line 231: Member can access course when at required level
- [ ] Line 238: Member cannot access course below required level
- [ ] Line 247: Locked course visible in course list with lock indicator
- [ ] Line 257: Course with no level requirement is accessible to all
- [ ] Line 310: No points awarded for self-like attempt
- [ ] Line 323: Level name too long is rejected
- [ ] Line 329: Empty level name is rejected
- [ ] Line 336: Duplicate level names are rejected
- [ ] Line 344: Non-increasing thresholds are rejected
- [ ] Line 351: Zero threshold for level 2 is rejected
- [ ] Line 363: Unauthenticated user cannot view points
- [ ] Line 367: Non-admin cannot configure levels
- [ ] Line 375: Non-admin cannot set course level requirements
- [ ] Line 383: Level name input is sanitized
- [ ] Line 404: Admin lowers course level requirement grants immediate access
- [ ] Line 414: Admin raises course level requirement revokes access

### Deliverable
**User can:** See locked courses with "Unlock at Level X" overlay, access courses when they reach the required level. **Admin can:** Set minimum level requirements on courses. **System:** Rejects invalid admin configuration, enforces authentication and authorization on all endpoints, sanitizes input against XSS.

### Dependencies
- Phase 2 must be complete

### Estimated Time
3-4 hours

### Definition of Done
- [ ] All 40 BDD scenarios passing
- [ ] 0 scenarios skipped
- [ ] Full validation coverage
- [ ] Security tests passing
- [ ] Course gating functional end-to-end
- [ ] `./scripts/verify.sh` green
- [ ] Frontend course lock overlay renders correctly
- [ ] Coverage >= 80%

### Verification Commands
```bash
pytest tests/features/gamification/test_points.py -v
# Expected: 40 passed, 0 skipped, 0 failed

./scripts/verify.sh

cd frontend && npm run test -- --run && npm run typecheck
```

---

## Dependency Graph

```
Phase 1 (Core Points Engine + Level Calculation)
    |
Phase 2 (Level Display, Definitions & Admin Config)
    |
Phase 3 (Course Gating, Validation & Security)
```

---

## Implementation Notes

**Patterns to Follow:**
- Follow `src/community/` structure exactly (hexagonal architecture)
- Value objects: frozen dataclasses with `__post_init__` validation (like `PostTitle`, `PostId`)
- Entities: dataclasses with factory `create()` methods and `_events` list (like `Post`)
- Repository interfaces: ABC in domain layer (like `IPostRepository`)
- Repository implementations: SQLAlchemy in infrastructure (like `SqlAlchemyPostRepository`)
- Command handlers: single responsibility, orchestrate domain + repos (like `CreatePostHandler`)
- API routes: FastAPI router with dependency injection (like `post_controller.py`)
- Frontend: feature directory under `frontend/src/features/gamification/` with `api/`, `components/`, `hooks/`, `types/` subdirectories
- Events: frozen dataclasses inheriting `DomainEvent` (like Community events)

**Community Event Enrichment (Phase 1):**
- Add `author_id: UserId` to `PostLiked`, `PostUnliked`, `CommentLiked`, `CommentUnliked` in `src/community/domain/events.py`
- Update Community publishers to include author_id (non-breaking — adding a field to frozen dataclass)

**Common Pitfalls:**
- Don't skip value object validation — every VO validates in `__post_init__`
- Don't forget the ratchet rule — `MemberPoints.current_level = max(current_level, calculated_level)`
- Don't bypass aggregate boundaries — all point changes go through `MemberPoints` methods
- Don't create direct DB queries from API layer — always go through application handlers
- Don't forget to publish events after persistence — follow existing pattern of collecting events in entities
- Don't hardcode level names in frontend — always fetch from API
