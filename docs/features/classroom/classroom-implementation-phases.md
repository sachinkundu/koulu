# Classroom - Implementation Phases

**Strategy:** Vertical Slicing (all layers per phase)
**Total BDD Scenarios:** 71
**Total New Files:** ~55
**Recommended Phases:** 4
**Estimated Total Time:** 16-22 hours

---

## Complexity Analysis

| Metric | Count | Complexity |
|--------|-------|------------|
| BDD Scenarios | 71 | High |
| New Files (backend) | ~45 | High |
| New DB Tables | 5 (courses, modules, lessons, progress, lesson_completions) | High |
| API Endpoints | 15 | High |
| New Dependencies | 1 backend (bleach) | Low |
| Domain Aggregates | 2 (Course, Progress) | Medium |
| Value Objects | 6+ | Medium |
| Domain Events | 5 | Medium |

**Overall Complexity:** High

**Decision:** 4-phase vertical slicing implementation

---

## Phase 1: Course Foundation

### Goal

Admins can create, list, edit, and soft-delete courses. Members can browse the course list. This establishes the Classroom bounded context, database schema (courses table), and API layer.

### Scope

**Backend - Domain Layer:**
- `src/classroom/__init__.py`
- `src/classroom/domain/__init__.py`
- `src/classroom/domain/entities/__init__.py`
- `src/classroom/domain/entities/course.py` — Course aggregate root (create, update, soft_delete)
- `src/classroom/domain/value_objects/__init__.py`
- `src/classroom/domain/value_objects/course_title.py` — 2-200 chars, strip whitespace
- `src/classroom/domain/value_objects/course_description.py` — max 2000 chars, optional
- `src/classroom/domain/value_objects/cover_image_url.py` — HTTPS URL validation
- `src/classroom/domain/value_objects/estimated_duration.py` — free-form string
- `src/classroom/domain/events/__init__.py`
- `src/classroom/domain/events/course_created.py`
- `src/classroom/domain/events/course_deleted.py`
- `src/classroom/domain/repositories/__init__.py`
- `src/classroom/domain/repositories/course_repository.py` — Interface (ABC)
- `src/classroom/domain/exceptions.py`

**Backend - Application Layer:**
- `src/classroom/application/__init__.py`
- `src/classroom/application/commands/__init__.py`
- `src/classroom/application/commands/create_course.py`
- `src/classroom/application/commands/update_course.py`
- `src/classroom/application/commands/delete_course.py`
- `src/classroom/application/queries/__init__.py`
- `src/classroom/application/queries/get_course_list.py`
- `src/classroom/application/queries/get_course_details.py`
- `src/classroom/application/handlers/__init__.py`
- `src/classroom/application/handlers/create_course_handler.py`
- `src/classroom/application/handlers/update_course_handler.py`
- `src/classroom/application/handlers/delete_course_handler.py`
- `src/classroom/application/handlers/get_course_list_handler.py`
- `src/classroom/application/handlers/get_course_details_handler.py`

**Backend - Infrastructure Layer:**
- `src/classroom/infrastructure/__init__.py`
- `src/classroom/infrastructure/persistence/__init__.py`
- `src/classroom/infrastructure/persistence/models.py` — CourseModel (courses table only)
- `src/classroom/infrastructure/persistence/course_repository.py`
- `alembic/versions/20260207_1500_create_classroom_courses.py`

**Backend - Interface Layer:**
- `src/classroom/interface/__init__.py`
- `src/classroom/interface/api/__init__.py`
- `src/classroom/interface/api/course_controller.py` — Admin + Member course endpoints
- `src/classroom/interface/api/schemas.py` — Request/Response Pydantic models
- `src/classroom/interface/api/dependencies.py` — Handler dependency injection

**Wire-up:**
- `src/main.py` — Register classroom router

**Tests:**
- `tests/features/classroom/conftest.py` — Classroom-specific test fixtures
- `tests/features/classroom/test_classroom.py` — BDD step definitions
- `tests/unit/classroom/__init__.py`
- `tests/unit/classroom/domain/__init__.py`
- `tests/unit/classroom/domain/test_course.py`
- `tests/unit/classroom/domain/test_value_objects.py`

### BDD Scenarios

**Enabled (11):**

| # | Line | Scenario | Tag |
|---|------|----------|-----|
| 1 | L16 | Admin creates a course with required fields only | @happy_path |
| 2 | L27 | Admin creates a course with all optional fields | @happy_path |
| 3 | L40 | Admin lists all courses | @happy_path |
| 4 | L61 | Admin edits course details | @happy_path |
| 5 | L87 | Course creation fails without title | @error |
| 6 | L93 | Course creation fails with title too short | @error |
| 7 | L99 | Course creation fails with title too long | @error |
| 8 | L105 | Course creation fails with description too long | @error |
| 9 | L114 | Course creation fails with invalid cover image URL | @error |
| 10 | L411 | Member views course list | @happy_path |
| 11 | L456 | Soft-deleted courses are hidden from members | @happy_path |

**Skipped (60) — Phase 2: 28, Phase 3: 22, Phase 4: 10**

### API Endpoints (Phase 1)

```
POST   /api/v1/courses                    — Create course (admin)
GET    /api/v1/courses                    — List courses (admin + member)
GET    /api/v1/courses/{course_id}        — Get course details (basic, no modules yet)
PATCH  /api/v1/courses/{course_id}        — Update course (admin)
DELETE /api/v1/courses/{course_id}        — Soft delete course (admin)
```

### Dependencies

- None (first phase)
- Depends on Identity context for auth (already exists)

### Estimated Time

4-5 hours

### Definition of Done

- [ ] All domain files created with proper value object validation
- [ ] All application handlers implemented
- [ ] Database migration creates `courses` table
- [ ] API endpoints functional with proper HTTP status codes
- [ ] Router registered in `src/main.py`
- [ ] 11 BDD scenarios passing
- [ ] 60 BDD scenarios skipped with phase markers
- [ ] Unit tests for Course entity and all value objects
- [ ] `pytest tests/features/classroom/ -v` shows `11 passed, 60 skipped, 0 warnings`
- [ ] `./scripts/verify.sh` passes with coverage ≥80%

### Verification Commands

```bash
# BDD tests
pytest tests/features/classroom/test_classroom.py -v
# Expected: 11 passed, 60 skipped, 0 warnings

# Unit tests
pytest tests/unit/classroom/ -v

# Full verification
./scripts/verify.sh

# Verify all skips have phase markers
grep -r "@pytest.mark.skip" tests/features/classroom/ | grep "Phase [0-9]"
```

---

## Phase 2: Module & Lesson Management

### Goal

Admins can add, edit, delete, and reorder modules within courses and lessons within modules. Members can view full course structure (modules + lessons). This phase builds out the full Course aggregate with Module and Lesson child entities.

### Scope

**Backend - Domain Layer:**
- `src/classroom/domain/entities/module.py` — Module entity (within Course aggregate)
- `src/classroom/domain/entities/lesson.py` — Lesson entity (within Module)
- `src/classroom/domain/value_objects/module_title.py` — 2-200 chars
- `src/classroom/domain/value_objects/module_description.py` — max 1000 chars
- `src/classroom/domain/value_objects/lesson_title.py` — 2-200 chars
- `src/classroom/domain/value_objects/content_type.py` — TEXT | VIDEO enum
- `src/classroom/domain/value_objects/text_content.py` — 1-50,000 chars, HTML sanitization
- `src/classroom/domain/value_objects/video_url.py` — YouTube/Vimeo/Loom URL validation
- Update `src/classroom/domain/entities/course.py` — Add module management methods (add_module, reorder_modules)
- Update `src/classroom/domain/exceptions.py` — Add module/lesson-specific exceptions

**Backend - Application Layer:**
- `src/classroom/application/commands/add_module.py`
- `src/classroom/application/commands/update_module.py`
- `src/classroom/application/commands/delete_module.py`
- `src/classroom/application/commands/reorder_modules.py`
- `src/classroom/application/commands/add_lesson.py`
- `src/classroom/application/commands/update_lesson.py`
- `src/classroom/application/commands/delete_lesson.py`
- `src/classroom/application/commands/reorder_lessons.py`
- `src/classroom/application/handlers/add_module_handler.py`
- `src/classroom/application/handlers/update_module_handler.py`
- `src/classroom/application/handlers/delete_module_handler.py`
- `src/classroom/application/handlers/reorder_modules_handler.py`
- `src/classroom/application/handlers/add_lesson_handler.py`
- `src/classroom/application/handlers/update_lesson_handler.py`
- `src/classroom/application/handlers/delete_lesson_handler.py`
- `src/classroom/application/handlers/reorder_lessons_handler.py`
- Update `src/classroom/application/handlers/get_course_details_handler.py` — Include modules + lessons

**Backend - Infrastructure Layer:**
- Update `src/classroom/infrastructure/persistence/models.py` — Add ModuleModel, LessonModel
- Update `src/classroom/infrastructure/persistence/course_repository.py` — Module/Lesson persistence
- `alembic/versions/20260207_1600_add_modules_lessons.py` — Migration for modules + lessons tables

**Backend - Interface Layer:**
- Update `src/classroom/interface/api/course_controller.py` — Add module/lesson endpoints
- Update `src/classroom/interface/api/schemas.py` — Module/Lesson request/response models
- Update `src/classroom/interface/api/dependencies.py` — New handler dependencies

**Tests:**
- Update `tests/features/classroom/test_classroom.py` — Enable Phase 2 scenarios, add new step definitions
- `tests/unit/classroom/domain/test_module.py`
- `tests/unit/classroom/domain/test_lesson.py`
- `tests/unit/classroom/domain/test_video_url.py`
- `tests/unit/classroom/domain/test_text_content.py`

### BDD Scenarios

**Newly Enabled (28):**

| # | Line | Scenario | Tag |
|---|------|----------|-----|
| 12 | L51 | Admin views course details | @happy_path |
| 13 | L127 | Admin adds a module to a course | @happy_path |
| 14 | L138 | Admin adds multiple modules in sequence | @happy_path |
| 15 | L148 | Admin reorders modules | @happy_path |
| 16 | L164 | Admin edits module details | @happy_path |
| 17 | L175 | Admin soft deletes a module | @happy_path |
| 18 | L189 | Module creation fails without title | @error |
| 19 | L196 | Module creation fails with title too short | @error |
| 20 | L203 | Module creation fails with title too long | @error |
| 21 | L210 | Reorder fails with duplicate positions | @error |
| 22 | L221 | Admin creates a text lesson | @happy_path |
| 23 | L234 | Admin creates a video lesson with YouTube embed | @happy_path |
| 24 | L247 | Admin creates a video lesson with Vimeo embed | @happy_path |
| 25 | L259 | Admin creates a video lesson with Loom embed | @happy_path |
| 26 | L271 | Admin adds multiple lessons in sequence | @happy_path |
| 27 | L281 | Admin reorders lessons within a module | @happy_path |
| 28 | L297 | Admin edits a text lesson | @happy_path |
| 29 | L308 | Admin edits a video lesson URL | @happy_path |
| 30 | L332 | Lesson creation fails without title | @error |
| 31 | L339 | Lesson creation fails with title too short | @error |
| 32 | L346 | Lesson creation fails with title too long | @error |
| 33 | L353 | Lesson creation fails without content | @error |
| 34 | L363 | Lesson creation fails with invalid content type | @error |
| 35 | L374 | Video lesson creation fails with invalid YouTube URL | @error |
| 36 | L385 | Video lesson creation fails with unsupported platform | @error |
| 37 | L396 | Text lesson creation fails with content too long | @error |
| 38 | L432 | Member views course details | @happy_path |
| 39 | L632 | Course with no modules shows empty state to member | @edge_case |

**Total Enabled:** 11 (Phase 1) + 28 = 39
**Skipped:** 32 (Phase 3: 22, Phase 4: 10)

### API Endpoints (New in Phase 2)

```
POST   /api/v1/courses/{course_id}/modules                — Add module (admin)
PATCH  /api/v1/modules/{module_id}                        — Update module (admin)
DELETE /api/v1/modules/{module_id}                        — Soft delete module (admin)
POST   /api/v1/courses/{course_id}/modules/reorder        — Reorder modules (admin)
POST   /api/v1/modules/{module_id}/lessons                — Add lesson (admin)
PATCH  /api/v1/lessons/{lesson_id}                        — Update lesson (admin)
DELETE /api/v1/lessons/{lesson_id}                        — Soft delete lesson (admin)
POST   /api/v1/modules/{module_id}/lessons/reorder        — Reorder lessons (admin)
```

### Dependencies

- Phase 1 must be complete (Course entity, courses table, base API)
- New backend dependency: `bleach ^6.1.0` (for HTML sanitization in TextContent)

### Estimated Time

5-6 hours

### Definition of Done

- [ ] Module + Lesson entities with full behavior
- [ ] All value objects with validation (VideoUrl regex, TextContent sanitization)
- [ ] Drag-and-drop reorder support (backend position management)
- [ ] Database migration adds `modules` and `lessons` tables
- [ ] All 8 new API endpoints functional
- [ ] 39 BDD scenarios passing (11 Phase 1 + 28 Phase 2)
- [ ] 32 BDD scenarios skipped with phase markers
- [ ] Unit tests for Module, Lesson, VideoUrl, TextContent, ContentType
- [ ] `pytest tests/features/classroom/ -v` shows `39 passed, 32 skipped, 0 warnings`
- [ ] `./scripts/verify.sh` passes with coverage ≥80%

### Verification Commands

```bash
# BDD tests
pytest tests/features/classroom/test_classroom.py -v
# Expected: 39 passed, 32 skipped, 0 warnings

# Unit tests
pytest tests/unit/classroom/ -v

# Full verification
./scripts/verify.sh
```

---

## Phase 3: Progress Tracking & Course Consumption

### Goal

Members can start courses, view lesson content, navigate between lessons (Previous/Next, across modules), mark lessons complete/incomplete, and see progress percentages. This phase builds the Progress aggregate and enables all member-facing learning flows.

### Scope

**Backend - Domain Layer:**
- `src/classroom/domain/entities/progress.py` — Progress aggregate root (mark_complete, unmark, calculate_completion, get_next_incomplete)
- `src/classroom/domain/entities/lesson_completion.py` — LessonCompletion entity
- `src/classroom/domain/events/progress_started.py`
- `src/classroom/domain/events/lesson_completed.py`
- `src/classroom/domain/events/course_completed.py`
- `src/classroom/domain/repositories/progress_repository.py` — Interface (ABC)
- Update `src/classroom/domain/entities/__init__.py`

**Backend - Application Layer:**
- `src/classroom/application/commands/start_course.py`
- `src/classroom/application/commands/mark_lesson_complete.py`
- `src/classroom/application/commands/unmark_lesson.py`
- `src/classroom/application/queries/get_lesson.py`
- `src/classroom/application/queries/get_progress.py`
- `src/classroom/application/queries/get_next_incomplete_lesson.py`
- `src/classroom/application/handlers/start_course_handler.py`
- `src/classroom/application/handlers/mark_lesson_complete_handler.py`
- `src/classroom/application/handlers/unmark_lesson_handler.py`
- `src/classroom/application/handlers/get_lesson_handler.py`
- `src/classroom/application/handlers/get_progress_handler.py`
- `src/classroom/application/handlers/get_next_incomplete_lesson_handler.py`
- Update `src/classroom/application/handlers/get_course_list_handler.py` — Include progress data
- Update `src/classroom/application/handlers/get_course_details_handler.py` — Include per-lesson completion

**Backend - Infrastructure Layer:**
- Update `src/classroom/infrastructure/persistence/models.py` — Add ProgressModel, LessonCompletionModel
- `src/classroom/infrastructure/persistence/progress_repository.py`
- `alembic/versions/20260207_1700_add_progress_tables.py` — Migration for progress + lesson_completions

**Backend - Interface Layer:**
- `src/classroom/interface/api/progress_controller.py` — Progress + consumption endpoints
- Update `src/classroom/interface/api/schemas.py` — Progress response models, lesson content response
- Update `src/classroom/interface/api/dependencies.py` — Progress handler dependencies
- Update `src/main.py` — Register progress router

**Tests:**
- Update `tests/features/classroom/test_classroom.py` — Enable Phase 3 scenarios
- `tests/unit/classroom/domain/test_progress.py`
- `tests/unit/classroom/domain/test_lesson_completion.py`

### BDD Scenarios

**Newly Enabled (22):**

| # | Line | Scenario | Tag |
|---|------|----------|-----|
| 40 | L72 | Admin soft deletes a course (progress retention) | @happy_path |
| 41 | L318 | Admin soft deletes a lesson (completion retention) | @happy_path |
| 42 | L423 | Member views course list with progress indicators | @happy_path |
| 43 | L445 | Member views course details with progress | @happy_path |
| 44 | L468 | Member starts a course | @happy_path |
| 45 | L477 | Member views a text lesson | @happy_path |
| 46 | L486 | Member views a video lesson | @happy_path |
| 47 | L494 | Member navigates to next lesson within module | @happy_path |
| 48 | L502 | Member navigates to previous lesson within module | @happy_path |
| 49 | L510 | Member navigates to next lesson across modules | @happy_path |
| 50 | L521 | Member navigates to previous lesson across modules | @happy_path |
| 51 | L532 | Member continues where they left off | @happy_path |
| 52 | L540 | Member continues on fully completed course | @happy_path |
| 53 | L553 | Member marks a lesson as complete | @happy_path |
| 54 | L563 | Member un-marks a lesson as complete | @happy_path |
| 55 | L572 | Member completes all lessons in a course | @happy_path |
| 56 | L582 | Module completion percentage updates | @happy_path |
| 57 | L590 | Course completion percentage updates | @happy_path |
| 58 | L601 | Progress is retained after course soft delete | @happy_path |
| 59 | L611 | Next incomplete lesson is null when course is complete | @edge_case |
| 60 | L619 | Progress excludes soft-deleted lessons from percentage | @edge_case |
| 61 | L639 | Module with no lessons shows empty state | @edge_case |

**Total Enabled:** 39 (Phase 1+2) + 22 = 61
**Skipped:** 10 (Phase 4: Security)

### API Endpoints (New in Phase 3)

```
GET    /api/v1/lessons/{lesson_id}                        — Get lesson content (member)
POST   /api/v1/courses/{course_id}/start                  — Start course (member)
GET    /api/v1/courses/{course_id}/continue                — Get next incomplete lesson (member)
GET    /api/v1/progress/courses/{course_id}               — Get course progress (member)
POST   /api/v1/progress/lessons/{lesson_id}/complete       — Mark lesson complete (member)
DELETE /api/v1/progress/lessons/{lesson_id}/complete       — Un-mark lesson (member)
```

### Dependencies

- Phase 2 must be complete (Modules + Lessons exist to track progress against)

### Estimated Time

5-6 hours

### Definition of Done

- [ ] Progress aggregate with completion calculation logic
- [ ] All navigation logic (next/previous across modules, continue)
- [ ] Lesson content retrieval (text + video URL)
- [ ] Database migration adds `progress` and `lesson_completions` tables
- [ ] All 6 new API endpoints functional
- [ ] Course list and details endpoints enriched with progress data
- [ ] 61 BDD scenarios passing
- [ ] 10 BDD scenarios skipped with phase markers (Phase 4: Security)
- [ ] Unit tests for Progress entity, completion calculations, navigation logic
- [ ] `pytest tests/features/classroom/ -v` shows `61 passed, 10 skipped, 0 warnings`
- [ ] `./scripts/verify.sh` passes with coverage ≥80%

### Verification Commands

```bash
# BDD tests
pytest tests/features/classroom/test_classroom.py -v
# Expected: 61 passed, 10 skipped, 0 warnings

# Unit tests
pytest tests/unit/classroom/ -v

# Full verification
./scripts/verify.sh
```

---

## Phase 4: Security Hardening

### Goal

Enforce authentication on all endpoints, authorization checks (admin-only for management, member-only for own progress), XSS prevention for rich text content, video URL sanitization, and rate limiting for course creation.

### Scope

**Backend - Application Layer:**
- Update all admin handlers — Add role verification (`require_admin`)
- Update progress handlers — Add user ownership verification

**Backend - Infrastructure Layer:**
- Ensure `bleach` sanitization is applied in TextContent value object (may already exist from Phase 2)
- Rate limiting configuration for course creation endpoint

**Backend - Interface Layer:**
- Update `src/classroom/interface/api/dependencies.py` — Add admin role check dependency
- Update `src/classroom/interface/api/course_controller.py` — Apply rate limiting decorator
- Update `src/classroom/interface/api/progress_controller.py` — Verify user ownership

**Tests:**
- Update `tests/features/classroom/test_classroom.py` — Enable Phase 4 security scenarios
- `tests/unit/classroom/domain/test_security.py` — XSS sanitization tests

### BDD Scenarios

**Newly Enabled (10):**

| # | Line | Scenario | Tag |
|---|------|----------|-----|
| 62 | L650 | Unauthenticated user cannot view courses | @security |
| 63 | L656 | Non-admin cannot create a course | @security |
| 64 | L663 | Non-admin cannot edit a course | @security |
| 65 | L671 | Non-admin cannot delete a course | @security |
| 66 | L679 | Non-admin cannot manage modules | @security |
| 67 | L687 | Non-admin cannot manage lessons | @security |
| 68 | L695 | Rich text content is sanitized to prevent XSS | @security |
| 69 | L704 | Video embed URLs are validated to prevent XSS | @security |
| 70 | L711 | Member can only view their own progress | @security |
| 71 | L718 | Course creation is rate limited | @security |

**Total Enabled:** 61 (Phase 1-3) + 10 = 71
**Skipped:** 0 — **All scenarios enabled. Feature complete.**

### Dependencies

- Phase 3 must be complete (all functionality exists to secure)
- Existing rate limiter infrastructure (`slowapi`)

### Estimated Time

3-4 hours

### Definition of Done

- [ ] All endpoints require authentication (JWT token)
- [ ] Admin-only endpoints reject member requests with 403
- [ ] Members can only access their own progress
- [ ] Rich text HTML sanitized (script tags stripped, safe tags allowed)
- [ ] Video URLs validated against XSS patterns
- [ ] Rate limiting applied to course creation
- [ ] **71 BDD scenarios passing, 0 skipped**
- [ ] Unit tests for sanitization and authorization
- [ ] `pytest tests/features/classroom/ -v` shows `71 passed, 0 skipped, 0 warnings`
- [ ] `./scripts/verify.sh` passes with coverage ≥80%
- [ ] **Feature complete** — all BDD scenarios enabled and passing

### Verification Commands

```bash
# BDD tests
pytest tests/features/classroom/test_classroom.py -v
# Expected: 71 passed, 0 skipped, 0 warnings

# Unit tests
pytest tests/unit/classroom/ -v

# Full verification
./scripts/verify.sh

# Verify NO remaining skips
grep -r "@pytest.mark.skip" tests/features/classroom/
# Expected: No results (all skip markers removed)
```

---

## Dependency Graph

```
Phase 1: Course Foundation
├── Domain: Course entity + 4 VOs + 2 events
├── App: 5 handlers (CRUD + list)
├── Infra: courses table + CourseRepository
├── API: 5 endpoints
└── Tests: 11 BDD + unit tests
         │
         ▼
Phase 2: Module & Lesson Management
├── Domain: Module + Lesson entities + 4 VOs
├── App: 8 handlers (CRUD + reorder)
├── Infra: modules + lessons tables
├── API: 8 endpoints
└── Tests: 39 BDD + unit tests
         │
         ▼
Phase 3: Progress Tracking & Consumption
├── Domain: Progress aggregate + events
├── App: 6 handlers (start, complete, navigate)
├── Infra: progress + completions tables
├── API: 6 endpoints + enriched existing
└── Tests: 61 BDD + unit tests
         │
         ▼
Phase 4: Security Hardening
├── Auth: Role checks on all admin endpoints
├── Sanitization: XSS prevention (bleach)
├── Rate limiting: Course creation throttle
├── Ownership: Progress isolation
└── Tests: 71 BDD (ALL enabled) + security unit tests
```

---

## Implementation Notes

### Patterns to Follow (from existing codebase)

**Domain Entities** (reference: `src/community/domain/entities/post.py`):
- Use `@dataclass` with factory `create()` classmethod
- Private `_events` list with `_add_event()` / `clear_events()`
- Value objects for all validated fields (never raw `str`/`int`)
- `__eq__` and `__hash__` based on entity ID

**Application Handlers** (reference: `src/community/application/handlers/`):
- Constructor injection for repositories
- `async def handle(command) -> ReturnType`
- `structlog` logging with context variables
- Convert raw types to value objects early in handler
- Raise domain exceptions, catch in controller

**API Controllers** (reference: `src/community/interface/api/post_controller.py`):
- `APIRouter(prefix="/...", tags=[...])`
- Dependency injection via `Annotated[Handler, Depends(get_handler)]`
- `CurrentUserIdDep` for authenticated user
- Exception-specific HTTP status codes (201/400/403/404/409)
- PATCH for partial updates

**Persistence Models** (reference: `src/community/infrastructure/persistence/models.py`):
- SQLAlchemy 2.0 `Mapped` type hints
- `PgUUID(as_uuid=True)` for UUIDs
- `server_default=func.now()` for timestamps
- Composite indexes for common queries

**BDD Tests** (reference: `tests/features/community/test_feed.py`):
- `scenarios("classroom.feature")` to load all scenarios
- `@given/@when/@then` with `parsers.parse()` for parameterized steps
- `context: dict[str, Any]` for inter-step state
- `client: AsyncClient` for HTTP calls
- Phase skipping: `@pytest.mark.skip(reason="Phase N: condition")`

### Common Pitfalls

- **Don't skip value object validation** — Every user input must pass through a VO
- **Don't forget domain events** — CourseCreated, LessonCompleted, CourseCompleted must publish
- **Don't bypass aggregate boundaries** — Module/Lesson access goes through Course
- **Don't use raw SQL** — Use SQLAlchemy ORM with repository pattern
- **Don't hardcode user roles** — Use auth dependency for admin checks
- **Position management** — Sequential (1,2,3), recalculate on reorder, unique constraint with is_deleted filter

### Key Technical Decisions (from TDD)

- **Course is Aggregate Root** — Modules + Lessons are child entities within Course
- **Progress is separate Aggregate** — Independent lifecycle, one per member per course
- **Completion calculated on-demand** — No stored percentage (always accurate)
- **Single `content` column** — TEXT type stores both HTML (text lessons) and URLs (video lessons)
- **Sequential positions** — Recalculated on reorder (no gaps)
- **Soft delete everywhere** — `is_deleted` flag + `deleted_at` timestamp

---

## Summary

| Phase | Scenarios | Cumulative | New Files | Key Deliverable |
|-------|-----------|------------|-----------|-----------------|
| 1 | 11 | 11/71 | ~25 | Admins create courses, members browse |
| 2 | 28 | 39/71 | ~15 | Modules + lessons with reordering |
| 3 | 22 | 61/71 | ~12 | Progress tracking + lesson consumption |
| 4 | 10 | 71/71 | ~5 | Security, auth, XSS prevention |

**Total:** 71 BDD scenarios, ~55 new files, 15 API endpoints, 5 DB tables

**CI Status:** Green after every phase (tests pass or are properly skipped)

**Deployable:** After any phase — each phase provides incremental user-facing value
