# Create Phase Plan Skill — Design Document

## Problem

`/implement-feature` currently handles both planning (complexity analysis, phase splitting, BDD distribution) and implementation (code, verification, testing). For large features, this coupling makes it hard to review the plan separately, iterate on phasing decisions, and produce granular task breakdowns.

## Solution

Split into two skills:

1. **`/create-phase-plan`** (NEW) — Takes specs, produces phased implementation plan + granular Phase 1 tasks
2. **`/implement-feature`** (REFACTORED) — Focuses on executing a single phase with verification guardrails

Internally, `/create-phase-plan` uses `superpowers:writing-plans` format for granular TDD-style task breakdowns within each phase.

## Architecture

```
Specs (PRD + BDD + TDD + UI_SPEC)
        |
/create-phase-plan
  |-- {feature}-implementation-phases.md    (high-level, all phases)
  |-- {feature}-phase-1-tasks.md            (granular TDD tasks, Phase 1 only)
        |
/implement-feature --phase=1
  |-- auto-detects phase-1-tasks.md
  |-- follows granular plan task-by-task
  |-- runs verification protocol
  |-- generates manual testing guide
        |
/implement-feature --phase=2
  |-- generates phase-2-tasks.md on-the-fly if not present
  |-- (or uses pre-generated one from end-of-Phase-1 prompt)
```

## Decisions

### Two separate output documents
- **Phase plan** (`{feature}-implementation-phases.md`): High-level phases with scope, goals, BDD scenario distribution
- **Task plan** (`{feature}-phase-N-tasks.md`): Granular TDD-style steps within a single phase

**Rationale:** Separates strategic decisions (what goes in each phase) from tactical execution (exact test-first steps). Reviewable independently.

### Phase 1 granular plan only, on-demand for later phases
- `/create-phase-plan` generates granular tasks for Phase 1 only
- Phase 2+ granular plans generated when starting that phase (by `/implement-feature` or explicitly)

**Rationale:** Later phases benefit from lessons learned during earlier implementation. Avoids stale plans.

### Co-located file output
- All files in `docs/features/{context}/` alongside existing specs

**Rationale:** Keeps everything for a feature together. Easy to cross-reference PRD, TDD, phase plan, and task plan.

### Auto-detect in /implement-feature
- `/implement-feature --phase=N` checks for `{feature}-phase-N-tasks.md` automatically
- If found: follows it. If not found: generates one on-the-fly.

**Rationale:** Works with or without prior planning. Backwards-compatible with existing workflow.

## /create-phase-plan Skill

### Frontmatter
```yaml
name: create-phase-plan
description: Create phased implementation plan from approved specs (PRD, BDD, TDD, UI_SPEC)
user_invocable: true
model: opus
```

### Usage
`/create-phase-plan <context>/<feature-name>`

### Input Requirements
- PRD: `docs/features/{context}/{feature}-prd.md` (required)
- BDD: `tests/features/{context}/{feature}.feature` (required)
- TDD: `docs/features/{context}/{feature}-tdd.md` (required)
- UI_SPEC: `docs/features/{context}/UI_SPEC.md` (required for user-facing features)

### Output
- `docs/features/{context}/{feature}-implementation-phases.md`
- `docs/features/{context}/{feature}-phase-1-tasks.md`

### Workflow
1. Parse arguments — extract context + feature name
2. Locate and read all specs (fail if missing required ones)
3. Read existing codebase patterns — find similar implementations to reference
4. Complexity analysis — scenarios, files, endpoints, dependencies
5. Choose phasing strategy — vertical slicing (default), hybrid, or single-phase
6. Frontend gate — verify UI_SPEC for user-facing features
7. Distribute BDD scenarios across phases
8. Generate phase plan document
9. Present plan for user approval (WAIT)
10. Generate Phase 1 granular tasks (writing-plans format)
11. Present granular plan for confirmation

### Content moved FROM /implement-feature
- Complexity analysis criteria (Step 2)
- Pre-implementation frontend check (Step 2.5)
- Phase plan creation + phasing strategies (Step 3)
- Strategy definitions: vertical slicing, layer-based, hybrid
- Phase document template
- BDD scenario distribution logic
- Approval gate (Step 4)

## /implement-feature Refactored

### Content REMOVED
- Steps 2-4 (complexity analysis, frontend gate, phase plan creation, approval)
- Phasing strategy definitions
- Phase document template

### Content KEPT (unchanged)
- Step 1: Branch management
- Step 5: Implementation execution
- Step 6: Phase completion verification (red-flags protocol)
- Step 7: E2E test consideration
- Step 8: Manual testing guide
- Test skip marker management
- Quality checklist
- Anti-patterns section

### New behavior
- **Step 1.5 (new):** Auto-detect `{feature}-phase-{N}-tasks.md`. If found, follow it task-by-task. If not found, generate on-the-fly.
- **End of phase:** After verification passes, offer to generate granular tasks for Phase N+1

## Granular Task Plan Format

```markdown
# {Feature} Phase {N} -- Task Plan

> **For Claude:** Use /implement-feature {context}/{feature} --phase={N} to execute.

**Phase goal:** {one sentence}
**Files to create/modify:** {count}
**BDD scenarios to enable:** {count}

---

### Task 1: {Component Name}

**Files:**
- Create: `exact/path/to/file.py`
- Test: `tests/exact/path/to/test.py`

**Step 1: Write failing test**
(exact test code)

**Step 2: Run test, verify failure**
Run: `pytest tests/path/test.py::test_name -v`
Expected: FAIL

**Step 3: Implement**
(exact implementation code)

**Step 4: Run test, verify pass**
Run: `pytest tests/path/test.py::test_name -v`
Expected: PASS

**Step 5: Commit**
(exact git commands)
```

## Workflow Update

Current docs/WORKFLOW.md Phase 6 becomes:

```
Phase 6a: Planning        -> /create-phase-plan   -> Phase plan + Phase 1 tasks
Phase 6b: Implementation  -> /implement-feature    -> Code per phase
```

Quick reference adds:

| I want to...              | Skill               | Creates...                  |
|---------------------------|---------------------|-----------------------------|
| Plan implementation phases | `/create-phase-plan` | Phase plan + Phase 1 tasks |

## Files to Create/Modify

1. **Create:** `.claude/skills/create-phase-plan/SKILL.md` — new skill
2. **Modify:** `.claude/skills/implement-feature/SKILL.md` — remove planning, add auto-detect
3. **Modify:** `docs/WORKFLOW.md` — add Phase 6a, update quick reference
4. **Modify:** `CLAUDE.md` — add `/create-phase-plan` to workflow list
