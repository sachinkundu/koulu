# Create Phase Plan Skill — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Split `/implement-feature` into a planning skill (`/create-phase-plan`) and a slimmed-down implementation skill, with granular writing-plans-style task output.

**Architecture:** Extract Steps 2-4 and all phasing strategy content from `implement-feature/SKILL.md` into a new `create-phase-plan/SKILL.md`. Add auto-detect logic to the remaining `implement-feature`. Update workflow docs.

**Tech Stack:** Markdown skill files, no code changes.

---

### Task 1: Create the `/create-phase-plan` skill directory

**Files:**
- Create: `.claude/skills/create-phase-plan/` (directory)

**Step 1: Create directory**

Run: `mkdir -p .claude/skills/create-phase-plan`

**Step 2: Verify directory exists**

Run: `ls .claude/skills/ | grep create-phase-plan`
Expected: `create-phase-plan`

**Step 3: Commit**

```bash
# No commit yet — empty directory won't be tracked by git. Commit with Task 2.
```

---

### Task 2: Write the `/create-phase-plan` SKILL.md

**Files:**
- Create: `.claude/skills/create-phase-plan/SKILL.md`

**Step 1: Write the skill file**

Create `.claude/skills/create-phase-plan/SKILL.md` with this exact content:

````markdown
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
- **Complex feature** (≥ 20 scenarios, ≥ 10 files): Multi-phase vertical slicing

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

Phase 1: Domain Layer + Database → Phase 2: Application Layer → Phase 3: API Layer → Phase 4: Frontend

Disadvantages: Some BDD scenarios can't pass until later phases. Can't deploy user-facing functionality until Phase 4. Integration issues discovered late.

**Strategy 3: Hybrid (Vertical Read/Write Split)**

Use for: Features where read operations are simpler than write operations.

Phase 1: Read Only (All Layers) → Phase 2: Write Operations (All Layers) → Phase 3: Advanced Features (All Layers)

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
- Each task follows TDD: write failing test → run it → implement → run it → commit
- Exact file paths, exact code, exact commands
- Reference relevant skills: `@architecture`, `@python`, `@frontend`
- Follow hexagonal architecture patterns from existing contexts
- Match existing codebase conventions (find a similar file, follow its patterns)

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
**Example:** "User can create a post via CreatePostModal, see it in feed, and click to view details"

**NOT acceptable:** "API endpoints allow post creation" (no user-visible value)

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

---

### Task 1: {Component Name}

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
````

**Step 2: Verify file was created**

Run: `ls -la .claude/skills/create-phase-plan/SKILL.md`
Expected: File exists with content

**Step 3: Commit**

```bash
git add .claude/skills/create-phase-plan/SKILL.md
git commit -m "feat: add /create-phase-plan skill for phased implementation planning"
```

---

### Task 3: Refactor `/implement-feature` — Remove planning sections

**Files:**
- Modify: `.claude/skills/implement-feature/SKILL.md`

This is the largest task. Remove Steps 2-4, phasing strategies, phase document template, examples, when-to-use sections, anti-patterns, and success criteria. Add auto-detect logic for granular task plans.

**Step 1: Replace the entire implement-feature SKILL.md**

The new file keeps:
- Frontmatter (updated description)
- Purpose (updated to reference /create-phase-plan)
- Usage (kept, emphasize --phase=N)
- Input Requirements (updated to include task plan)
- Step 1: Branch management (unchanged)
- NEW Step 1.5: Auto-detect granular task plan
- Step 2: Implement Phase (was Step 5, updated to follow task plan)
- Step 3: Phase Completion (was Step 6, unchanged — the full verification protocol)
- Step 4: Consider E2E Tests (was Step 7, unchanged)
- Step 5: Manual Testing Guide (was Step 8, unchanged)
- Test Management Across Phases (kept — implementation-level guidance)
- Quality Checklist (kept)

The new file removes:
- Step 2: Analyze Complexity (moved to create-phase-plan)
- Step 2.5: Pre-Implementation Phase Analysis (moved to create-phase-plan)
- Step 3: Create Phase Plan (moved to create-phase-plan)
- Step 4: Get Approval (moved to create-phase-plan)
- Phasing Strategies section (moved to create-phase-plan)
- Phase Document Template (moved to create-phase-plan)
- Examples: Simple/Complex Feature (moved to create-phase-plan)
- When to Use Single/Multi Phase (moved to create-phase-plan)
- Anti-Patterns to Avoid (moved to create-phase-plan)
- Success Criteria (moved to create-phase-plan)

Write the refactored `.claude/skills/implement-feature/SKILL.md` with this exact content:

(See Task 3 content in actual implementation — the full refactored SKILL.md. It retains Steps 1, 5-8, Test Management, Quality Checklist from the original, renumbered as Steps 1-5, with a new Step 1.5 for auto-detect.)

**Step 2: Verify the file has no planning sections**

Run: `grep -c "Analyze Complexity\|Phasing Strategies\|Phase Document Template\|Anti-Patterns\|Success Criteria" .claude/skills/implement-feature/SKILL.md`
Expected: `0` (none of these headers remain)

Run: `grep -c "auto-detect\|task plan\|phase-.*-tasks.md" .claude/skills/implement-feature/SKILL.md`
Expected: > 0 (new auto-detect logic is present)

**Step 3: Commit**

```bash
git add .claude/skills/implement-feature/SKILL.md
git commit -m "refactor: slim down /implement-feature — extract planning to /create-phase-plan"
```

---

### Task 4: Update `docs/WORKFLOW.md`

**Files:**
- Modify: `docs/WORKFLOW.md`

**Step 1: Update Phase 6 section**

Replace the current Phase 6 section (lines 127-150) with two sub-phases:

```markdown
## Phase 6a: Implementation Planning

**Skill:** `/create-phase-plan`

**Purpose:** Analyze specs and create phased implementation plan with granular tasks

**Owner:** Engineering Lead/Architect

**Workflow:**
1. Read PRD + BDD + TDD + UI_SPEC
2. Analyze complexity and choose phasing strategy
3. Distribute BDD scenarios across phases
4. Generate phase plan document
5. Generate Phase 1 granular task plan

**Output Files:**
- `docs/features/[context]/[feature]-implementation-phases.md`
- `docs/features/[context]/[feature]-phase-1-tasks.md`

**Review:** Engineers review phase plan for approach, scope, and feasibility

---

## Phase 6b: Implementation

**Skill:** `/implement-feature`

**Purpose:** Execute a single phase from the implementation plan

**Owner:** Engineers (or Claude as engineer)

**Workflow:**
1. Auto-detect granular task plan for the phase
2. Follow tasks in TDD order (failing test -> implement -> verify)
3. Run verification scripts
4. Generate manual testing guide

**Output:**
- Source code in `src/`
- Unit/integration tests

**Definition of Done:**
- All BDD scenarios for this phase pass
- Unit tests pass
- Verification scripts pass
- Code follows CLAUDE.md rules
```

**Step 2: Update the Quick Reference table**

Add row for `/create-phase-plan` before the `/implement-feature` row:

```markdown
| Plan implementation phases | `/create-phase-plan` | Phase plan + Phase 1 tasks |
```

**Step 3: Verify changes**

Run: `grep "create-phase-plan" docs/WORKFLOW.md`
Expected: Multiple matches (Phase 6a section + quick reference)

**Step 4: Commit**

```bash
git add docs/WORKFLOW.md
git commit -m "docs: update workflow with /create-phase-plan step (Phase 6a)"
```

---

### Task 5: Update `CLAUDE.md`

**Files:**
- Modify: `CLAUDE.md`

**Step 1: Update the feature workflow list**

Replace the current step 5 (line 89) with two steps:

```markdown
5. `/create-phase-plan {context}/{feature}` -> Phase plan + Phase 1 granular tasks
6. `/implement-feature {context}/{feature} --phase=N` -> Implementation per phase
```

And renumber steps 6-7 to 7-8:

```markdown
7. `/write-e2e-tests {feature}` -> Playwright tests
8. `/document-work {context}/{feature}` -> Summary + PRD update
```

**Step 2: Verify changes**

Run: `grep "create-phase-plan" CLAUDE.md`
Expected: 1 match in workflow list

**Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: add /create-phase-plan to CLAUDE.md feature workflow"
```

---

### Task 6: Final verification

**Step 1: Verify all skill files exist**

Run: `ls .claude/skills/create-phase-plan/SKILL.md .claude/skills/implement-feature/SKILL.md`
Expected: Both files listed

**Step 2: Verify no planning content in implement-feature**

Run: `grep -c "Analyze Complexity" .claude/skills/implement-feature/SKILL.md`
Expected: `0`

**Step 3: Verify create-phase-plan has planning content**

Run: `grep -c "Analyze Complexity\|Phasing Strategies\|Frontend Gate" .claude/skills/create-phase-plan/SKILL.md`
Expected: > 0

**Step 4: Verify workflow references both skills**

Run: `grep "create-phase-plan\|implement-feature" docs/WORKFLOW.md | wc -l`
Expected: >= 4

**Step 5: Verify CLAUDE.md references both skills**

Run: `grep "create-phase-plan\|implement-feature" CLAUDE.md | wc -l`
Expected: >= 2

**Step 6: Final commit (if any unstaged changes)**

```bash
git status
# If clean: no commit needed
# If changes: stage and commit
```
