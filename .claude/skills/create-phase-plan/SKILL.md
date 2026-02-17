---
name: create-phase-plan
description: Create phased implementation plan from approved specs (PRD, BDD, TDD, UI_SPEC)
user_invocable: true
model: opus
---

# Create Phase Plan

## Purpose

Analyze approved specifications and create a phased implementation plan. Each phase is a deployable vertical slice through all layers, with BDD scenarios distributed across phases.

**Key Principle:** Planning is separate from implementation. This skill produces the PLAN. Use `/implement-feature --phase=N` to EXECUTE each phase.

**Default Strategy:** Vertical slicing (all layers per phase) to enable continuous integration with passing CI tests.

---

## Usage

`/create-phase-plan <context>/<feature-name>`

Example: `/create-phase-plan community/posts`

---

## Input Requirements

**Must exist before starting:**
- PRD: `docs/features/{context}/{feature}-prd.md` (approved)
- TDD: `docs/features/{context}/{feature}-tdd.md` (approved)
- BDD: `tests/features/{context}/{feature}.feature` (approved)

**Required for user-facing features:**
- UI_SPEC: `docs/features/{context}/UI_SPEC.md`

**Output:**
- Phase plan: `docs/features/{context}/{feature}-implementation-phases.md`
- Phase 1 granular tasks: `docs/features/{context}/{feature}-phase-1-tasks.md`

---

## Workflow

### Step 1: Read All Specifications

1. Parse arguments to extract `{context}` and `{feature-name}`
2. Read PRD, TDD, BDD, and UI_SPEC (if exists)
3. If any required spec is missing, **STOP** and tell the user which spec to generate first
4. Read existing codebase patterns — find similar implementations in other contexts to reference

### Step 2: Analyze Complexity

Assess feature complexity from specs:

**Complexity Indicators:**
- Number of BDD scenarios (> 20 = complex)
- Number of new files (> 10 = complex)
- Number of dependencies (> 2 contexts = complex)
- Number of API endpoints (> 3 = complex)
- Estimated implementation time (> 4 hours = complex)

**Decision:**
- **Simple feature** (< 20 scenarios, < 10 files): Single-phase implementation
- **Complex feature** (>= 20 scenarios, >= 10 files): Multi-phase vertical slicing

### Step 3: Frontend Gate (CRITICAL)

**Before creating any phase plan, verify frontend requirements:**

1. **Is this a user-facing feature?**
   - User-facing = Community posts, classroom lessons, member profiles, calendar events
   - NOT user-facing = Background sync jobs, admin migrations, internal APIs

2. **If user-facing, verify UI_SPEC.md exists:**
   - Check `docs/features/{context}/UI_SPEC.md`
   - If missing: **STOP and prompt:**
     ```
     Frontend in scope but no UI_SPEC.md found.

     Cannot plan UI implementation without design specification.

     Next steps:
     1. Generate UI_SPEC: /generate-ui-spec {feature}
     2. OR: Confirm this is backend-only (background job, internal API)
     ```

3. **Each phase with user-facing work MUST include a Frontend section.**
   - If a phase has backend but no frontend: explicitly state why
   - Valid reasons: background job, internal API, migration service
   - Invalid reason: "Deferred pending UI design"

**NEVER create a phase plan if:**
- User-facing feature with no UI_SPEC.md available
- "Deferred pending UI design" used as excuse

### Step 4: Choose Phasing Strategy

Present recommended strategy to user with rationale.

**Strategy 1: Vertical Slicing (Default - Recommended)**

Use for: Features requiring continuous integration, deployable increments, passing CI tests at each phase.

- Phase 1: Core Happy Path (All Layers) — minimal entities, single command handler, basic repository + 1-2 API endpoints, minimal UI. Result: Feature works end-to-end for basic case.
- Phase 2: Validation & Error Handling (All Layers) — add validation to value objects, error cases in handlers, error responses in API, error states in UI. Result: Feature handles invalid inputs gracefully.
- Phase 3: Extended Features (All Layers) — additional value objects + business rules, extended handlers, additional endpoints, extended UI. Result: Feature complete with all functionality.
- Phase 4: Security & Edge Cases (Optional) — authorization checks, rate limiting, logging, monitoring. Result: Feature hardened for production.

Advantages: All tests pass at each phase. Can deploy after any phase. Users see incremental value. Low risk of breaking changes.

**Strategy 2: Layer-Based (Alternative)**

Use for: Features with complex domain logic requiring foundation before integration, or when frontend is not ready.

Phase 1: Domain Layer + Database -> Phase 2: Application Layer -> Phase 3: API Layer -> Phase 4: Frontend

Disadvantages: Some BDD scenarios can't pass until later phases. Can't deploy user-facing functionality until Phase 4. Integration issues discovered late.

**Strategy 3: Hybrid (Vertical Read/Write Split)**

Use for: Features where read operations are simpler than write operations.

Phase 1: Read Only (All Layers) -> Phase 2: Write Operations (All Layers) -> Phase 3: Advanced Features (All Layers)

Advantages: Get data visible to users quickly. Each phase is deployable. Simpler phases.

### Step 5: Distribute BDD Scenarios

For each phase, assign BDD scenarios:

1. Read the `.feature` file and list ALL scenarios
2. For each scenario, determine which phase it belongs to based on:
   - What domain entities/value objects it requires
   - What endpoints it needs
   - What UI interactions it tests
3. Document clearly:
   - **Enabled** scenarios per phase (will have step definitions)
   - **Skipped** scenarios per phase (with phase markers and conditions)

**Phase Criteria:**
- Each phase is independently testable
- Each phase provides incremental value
- Each phase can be deployed separately
- Dependencies flow in one direction (Phase N depends on Phase N-1)
- Each phase takes 2-4 hours to implement

### Step 6: Generate Phase Plan Document

Write `docs/features/{context}/{feature}-implementation-phases.md` using the Phase Document Template (see below).

### Step 7: Present Plan for Approval

Present the phase plan to the user:
1. Show complexity analysis table
2. Show phase breakdown with goals and BDD scenario counts
3. Show dependency graph
4. Explain rationale for chosen strategy
5. **Wait for approval before proceeding to Step 8**

### Step 8: Generate Phase 1 Granular Tasks

After approval, generate granular TDD-style tasks for Phase 1 only.

Write `docs/features/{context}/{feature}-phase-1-tasks.md` following the Granular Task Plan Format (see below).

**Granular task generation rules:**
- Each task = one component or one logical unit
- Each task follows TDD: write failing test -> run it -> implement -> run it -> commit
- Exact file paths, exact code, exact commands
- Reference relevant skills: `@architecture`, `@python`, `@frontend`
- Follow hexagonal architecture patterns from existing contexts
- Match existing codebase conventions (find a similar file, follow its patterns)

**Task dependency analysis (REQUIRED for parallel execution):**

After defining all tasks, analyze inter-task dependencies to enable `/implement-feature` or `/implement-phase-team` to dispatch independent tasks in parallel:

1. **For each task, identify what it creates/modifies** — already captured in the Files section
2. **Check imports/usage:** If Task B's code imports from files Task A creates, B depends on A
3. **Check file overlap:** If two tasks modify the same file, they must be sequential
4. **Declare `Depends on:` field** on each task — list task numbers, or "none" if independent
5. **Declare `Owner:` field** on each task — one of: `backend`, `frontend`, `testing`
6. **Generate a dependency graph, parallel execution summary, AND agent execution plan** at the top of the task plan

**Owner assignment rules:**
- `backend` — Domain entities, value objects, application handlers, repositories, infrastructure, API endpoints, database migrations, unit tests for backend code
- `frontend` — TypeScript types, API hooks, React components, pages, routes, Vitest component tests
- `testing` — BDD step definitions, integration test wiring, E2E Playwright specs, final verification
- If a task spans both backend and frontend (rare — avoid this), split it into two tasks

**Multi-backend agent splitting (for phases with 8+ backend tasks):**

When the backend has many tasks (8+), split the `backend` owner into sub-owners by architectural layer to enable parallel execution by multiple backend agents:

- `backend-domain` — Domain entities, value objects, events, exceptions, repository interfaces, domain unit tests. Owns: `src/{context}/domain/`, `tests/unit/{context}/domain/`
- `backend-infra` — SQLAlchemy models, Alembic migrations, repository implementations, cross-context event enrichment. Owns: `src/{context}/infrastructure/`, `alembic/versions/`, cross-context files (e.g., `src/community/domain/events.py`)
- `backend-app` — Application commands/queries/handlers, event handlers, API routes/schemas/dependencies, app wiring, application unit tests. Owns: `src/{context}/application/`, `src/{context}/interface/`, `tests/unit/{context}/application/`

When to split:
- Phase has 8+ backend tasks with independent sub-chains across layers
- Domain and infrastructure foundations can be built in parallel (e.g., domain entities and DB models don't depend on each other)
- Application layer naturally waits for both domain interfaces and infrastructure to be ready

When NOT to split (keep single `backend` owner):
- Phase has <8 backend tasks
- Tasks are highly sequential with no parallelism opportunity
- Most tasks touch the same files/directories

**Testing task splitting (for parallel test development):**

Instead of a single final testing task that depends on ALL implementation, split testing work into phases that can start earlier:

- `testing-setup` — Conftest fixtures (community/user creation helpers, auth helpers), skip markers for future-phase scenarios, step definition shells. Depends on: **none** (uses existing test infrastructure patterns). Owns: `tests/features/{context}/conftest.py`, `tests/features/{context}/__init__.py`
- `testing-domain` — BDD step definitions for domain-level scenarios (e.g., "new member starts at Level 1", "member levels up", "points cannot go below zero"). These test domain logic directly, not via API. Depends on: **backend-domain** tasks only. Owns: domain-level step definitions in `tests/features/{context}/test_{feature}.py`
- `testing-integration` — BDD step definitions for API-level scenarios (e.g., "member earns a point when their post is liked") + final verification run. Depends on: **all backend + frontend** tasks. Owns: API-level step definitions, runs `./scripts/verify.sh`

When to split testing:
- Phase has 10+ BDD scenarios to enable
- Some scenarios test pure domain logic (can run without API)
- Testing setup (conftest, fixtures) is non-trivial

When NOT to split (keep single `testing` owner):
- Phase has <10 BDD scenarios
- All scenarios require API-level testing
- Simple fixture setup

**Common dependency patterns (architecture-aware):**
- Application layer (handlers, DTOs) → typically independent, can start first
- Domain interface extensions → depend on knowing what the handler needs
- Infrastructure implementations → depend on the domain interface they implement
- API endpoints → depend on the application handler they wire up
- Frontend types/hooks → do NOT depend on backend files (they mirror the API contract)
- Frontend components → depend on frontend types/hooks
- BDD test setup (conftest, fixtures, skip markers) → do NOT depend on backend (uses existing patterns)
- BDD domain-level tests → depend on domain layer only (entities, value objects)
- BDD API-level tests → depend on the full backend stack they exercise
- Final verification → depends on ALL other tasks

**Cross-agent independence:** Backend and frontend agents can run fully in parallel because the frontend codes against the API contract defined in the TDD document, not against live backend code. Testing agent starts after both complete.

### Step 9: Present Granular Plan

Present the Phase 1 task plan to user:
1. Show task count and estimated time
2. List task names
3. Confirm ready to implement

**Then say:**
```
Phase plan and Phase 1 tasks ready.

To implement: /implement-feature {context}/{feature} --phase=1

Phase 1 has {N} tasks covering {M} BDD scenarios.
```

---

## Phase Document Template

```markdown
# {Feature} - Implementation Phases

## Complexity Analysis

| Metric | Count | Complexity |
|--------|-------|------------|
| BDD Scenarios | X | High/Medium/Low |
| New Files | Y | High/Medium/Low |
| Modified Files | Z | High/Medium/Low |
| API Endpoints | N | High/Medium/Low |
| Dependencies | M contexts | High/Medium/Low |

**Overall Complexity:** High/Medium/Low

**Decision:** X-phase implementation

**Strategy:** {Vertical Slicing | Layer-Based | Hybrid} because {rationale}

---

## Phase 1: {Name}

### Goal
What this phase achieves in 1-2 sentences.

### Scope

**Backend (Domain -> API):**
- [ ] Domain entities: `list/of/files.py`
- [ ] Value objects: `list/of/files.py`
- [ ] Application handlers: `list/of/files.py`
- [ ] Repository implementations: `list/of/files.py`
- [ ] API endpoints: `list/of/files.py`
- [ ] Database migrations: `list/of/files.py`

**Frontend (User-Facing UI):**
- [ ] React components: `list/of/files.tsx`
- [ ] Pages/routes: `list/of/files.tsx`
- [ ] Forms and validation: `list/of/files.tsx`
- [ ] State management
- [ ] API integration
- [ ] **Page/route integration: components wired into actual pages users can navigate to** (new route created OR existing page updated to render the components)

**IF NO FRONTEND IN THIS PHASE:**
Explicitly state reason:
- [ ] Background job (no user interaction)
- [ ] Internal API (admin UI in Phase X)
- [ ] Migration service (no UI needed)

**Testing:**
- [ ] BDD scenarios (API-level): X scenarios
- [ ] Unit tests (domain logic): Y test files
- [ ] E2E tests (UI automation): Required if UI exists

### BDD Scenarios

**Enabled for this phase:**
- [ ] Line X: Scenario title (test_scenario_x)
- [ ] Line Y: Scenario title (test_scenario_y)

**Skipped (future phases):**
- Line A: Scenario title -> Phase 2: Requires validation logic
- Line B: Scenario title -> Phase 3: Requires update endpoint

### Deliverable
**User can:** {describe what user can DO via UI}
**Verify by:** {exact URL where user navigates to see the feature}
**Example:** "User can create a post via CreatePostModal, see it in feed, and click to view details — verify at http://localhost:5173/community"

**NOT acceptable:**
- "API endpoints allow post creation" (no user-visible value)
- "Components built and tested" (isolated components not wired into pages = not done)
- "Frontend types and hooks created" (infrastructure without rendered UI = not done)

### Dependencies
- None (first phase)
- Or: Requires Phase X to be complete

### Estimated Time
X-Y hours

### Definition of Done
- [ ] All files created/modified
- [ ] X BDD scenarios passing (phase-specific)
- [ ] Y scenarios skipped with phase markers (future phases)
- [ ] Z unit tests passing
- [ ] Linting passes
- [ ] Type checking passes
- [ ] No breaking changes to existing features
- [ ] CI green (all enabled tests pass, skipped tests documented)
- [ ] Deployability check passes (if user-facing)

### Verification Commands
```bash
# Run phase-specific tests
pytest tests/features/{context}/test_{feature}.py -v
# Expected: X passed, Y skipped (Phase markers visible)

# Verify all skips have phase markers
grep -r "@pytest.mark.skip" tests/features/{context}/ | grep "Phase [0-9]"

# Full verification
./scripts/verify.sh

# Frontend (if applicable)
npm run test
npm run typecheck
```

---

## Phase 2: {Name}
...

---

## Dependency Graph

```
Phase 1 ({name})
    |
Phase 2 ({name})
    |
Phase 3 ({name})
```

---

## Implementation Notes

**Patterns to Follow:**
- Follow existing {context} patterns (find similar context, match structure)
- Use same value object patterns as identity context
- Follow hexagonal architecture

**Common Pitfalls:**
- Don't skip value object validation
- Don't forget domain events
- Don't bypass aggregate boundaries
- Don't write integration tests before unit tests
```

---

## Granular Task Plan Format

Each `{feature}-phase-N-tasks.md` follows this structure:

```markdown
# {Feature} Phase {N} -- Task Plan

> **For Claude:** Use /implement-feature {context}/{feature} --phase={N} to execute this plan.

**Phase goal:** {one sentence from phase plan}
**Files to create/modify:** {count}
**BDD scenarios to enable:** {count}
**Estimated time:** {X hours}
**Task count:** {N}

### Dependency Graph

{ASCII diagram showing task dependency flow — tasks as nodes, arrows for dependencies}

### Parallel Execution Summary

| Batch | Tasks | Mode | Rationale |
|-------|-------|------|-----------|
| 1 | Task X, Task Y | Parallel | {why these are independent} |
| ... | ... | ... | ... |

**Sequential execution:** {N} tasks
**Parallel execution:** {M} batches (estimated ~{P}% time savings)

### Agent Execution Plan

> Used by `/implement-phase-team` to assign tasks to team agents.

| Agent | Tasks | Starts | Blocked Until |
|-------|-------|--------|---------------|
| backend | Task 1, 2, 3, 4 | Immediately | — |
| frontend | Task 5, 6, 7 | Immediately | — |
| testing | Task 8, 9 | After backend + frontend | All implementation tasks complete |

**For phases with 8+ backend tasks, use multi-backend split:**

| Agent | Tasks | Starts | Blocked Until |
|-------|-------|--------|---------------|
| backend-domain | Task 1, 2, 3, 4, 5, 6 | Immediately | — |
| backend-infra | Task 7, 8, 9 | Immediately | — |
| backend-app | Task 10, 11, 12, 13, 14 | After backend-domain + backend-infra | Domain interfaces + persistence ready |
| frontend | Task 15, 16, 17 | Immediately | — |
| testing | Task 18 | After all implementation agents | All implementation tasks complete |

**File ownership boundaries (no overlap allowed):**
- `backend` owns: `src/{context}/`, `tests/unit/{context}/`, `alembic/` (single-agent mode)
- `backend-domain` owns: `src/{context}/domain/`, `tests/unit/{context}/domain/` (multi-agent mode)
- `backend-infra` owns: `src/{context}/infrastructure/`, `alembic/versions/`, cross-context event files (multi-agent mode)
- `backend-app` owns: `src/{context}/application/`, `src/{context}/interface/`, `tests/unit/{context}/application/` (multi-agent mode)
- `frontend` owns: `frontend/src/features/{context}/`, `frontend/src/types/`
- `testing` owns: `tests/features/{context}/`, `tests/e2e/`
- Shared files (e.g., `__init__.py` re-exports): assign to ONE agent only

---

### Task 1: {Component Name}

**Owner:** backend | frontend | testing
**Depends on:** none | Task X, Task Y

**Files:**
- Create: `exact/path/to/file.py`
- Test: `tests/exact/path/to/test.py`

**Step 1: Write the failing test**

```python
def test_specific_behavior():
    result = function(input)
    assert result == expected
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/path/test.py::test_name -v`
Expected: FAIL with "function not defined"

**Step 3: Write minimal implementation**

```python
def function(input):
    return expected
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/path/test.py::test_name -v`
Expected: PASS

**Step 5: Commit**

```bash
git add tests/path/test.py src/path/file.py
git commit -m "feat({context}): add specific feature"
```

### Task 2: ...

---

### Final Task: Enable BDD Scenarios + Verification

**Depends on:** all previous tasks

**Step 1: Remove skip markers for Phase {N} scenarios**

(List exact files and lines to modify)

**Step 2: Run full verification**

Run: `./scripts/verify.sh`
Expected: All checks pass

**Step 3: Run BDD tests**

Run: `pytest tests/features/{context}/test_{feature}.py -v`
Expected: X passed, Y skipped, 0 failed

**Step 4: Commit**

```bash
git add -A
git commit -m "feat({context}): complete Phase {N} - {phase name}"
```
```

---

## When to Use Single Phase

Use single-phase implementation when:
- Feature is small (< 20 BDD scenarios)
- Few files affected (< 10 files)
- No complex dependencies
- Can be implemented in < 4 hours
- Risk is low

For single-phase features, still generate a granular task plan but skip the phase plan document. Output only `{feature}-phase-1-tasks.md`.

---

## When to Use Multi-Phase

Use multi-phase implementation when:
- Feature is large (>= 20 BDD scenarios)
- Many files created (>= 10 files)
- Complex cross-layer changes
- Takes > 4 hours to implement
- High risk of breaking existing features

---

## Anti-Patterns to Avoid

- **Don't phase by "backend then frontend"** — Use vertical slicing (all layers per phase)
- **Don't create phases that can't be tested independently** — Each phase has passing BDD scenarios
- **Don't make phases too small** (< 2 hours) — Too much coordination overhead
- **Don't make phases too large** (> 6 hours) — Hard to review, high risk
- **Don't skip phase plan approval** — Always get user approval before generating granular tasks
- **Don't put all BDD scenarios in the last phase** — Distribute incrementally
- **Don't generate granular tasks for all phases upfront** — Only Phase 1 initially; later phases benefit from implementation lessons
- **Don't create frontend tasks that only build isolated components** — Every frontend task MUST include wiring the component into an actual page/route. A component that isn't rendered in the app is not done. If a new component needs a new page, include route creation in the task. If it enhances an existing page, include the import/render in the existing page.

---

## Success Criteria

**A good phase plan:**
- Uses vertical slicing (all layers per phase) for deployability
- Each phase independently testable with passing CI
- Each phase provides incremental user-facing value
- Clear dependencies between phases
- Reasonable time estimates (2-4 hours per phase)
- BDD scenarios distributed across phases
- Test skip strategy documented
- Can be reviewed and approved separately

**A good granular task plan:**
- Each task is 2-5 minutes of work
- Follows TDD: failing test -> implement -> verify
- Exact file paths and exact code
- Exact commands with expected output
- Frequent commits (every 1-3 tasks)
- References relevant architecture patterns
- Task dependencies declared with `Depends on:` field on every task
- Dependency graph and parallel execution summary at top of plan
- No false dependencies (e.g., frontend types don't depend on backend files)
