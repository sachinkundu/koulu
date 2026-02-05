---
name: implement-feature
description: Implement a feature from completed PRD and BDD specs
---

# Implement Feature (Phased Approach)

## Purpose

Implement features from approved PRD, TDD, and BDD specifications using a phased approach for complex features.

**Key Principle:** Complex features are broken into logical phases, each independently testable and deployable.

---

## Usage

`/implement-feature <context>/<feature-name>`

Example: `/implement-feature identity/profile`

Or for a specific phase:

`/implement-feature <context>/<feature-name> --phase=<number>`

Example: `/implement-feature identity/profile --phase=2`

---

## Input Requirements

**Must exist before starting:**
- PRD: `docs/features/{context}/{feature}-prd.md` (approved)
- TDD: `docs/features/{context}/{feature}-tdd.md` (approved)
- BDD: `tests/features/{context}/{feature}.feature` (approved)

**Output:**
- Phase plan document (if multi-phase)
- Implementation files per phase
- Passing BDD tests per phase

---

## Workflow

### Step 1: Analyze Complexity

Read PRD, TDD, and BDD specs to assess feature complexity.

**Complexity Indicators:**
- Number of BDD scenarios (> 20 = complex)
- Number of new files (> 10 = complex)
- Number of dependencies (> 2 contexts = complex)
- Number of API endpoints (> 3 = complex)
- Estimated implementation time (> 4 hours = complex)

**Decision:**
- **Simple feature** (< 20 scenarios, < 10 files): Single-phase implementation
- **Complex feature** (≥ 20 scenarios, ≥ 10 files): Multi-phase implementation

### Step 2: Create Phase Plan (if complex)

If feature is complex, create implementation phases document:

**Phase Criteria:**
- Each phase is independently testable
- Each phase provides incremental value
- Each phase can be deployed separately
- Dependencies flow in one direction (Phase N depends on Phase N-1)
- Each phase takes 2-4 hours to implement

**Phase Plan Document:** `docs/features/{context}/{feature}-implementation-phases.md`

**Structure:**
```markdown
# {Feature} - Implementation Phases

## Overview
- Total BDD Scenarios: X
- Total Files: Y
- Recommended Phases: Z

## Phase Breakdown

### Phase 1: {Name}
**Goal:** What this phase achieves
**Components:**
- Domain layer: List files
- Infrastructure: List files
- Tests: X scenarios

**BDD Scenarios Covered:** List scenario titles
**Dependencies:** None (or list)
**Estimated Time:** X hours
**Definition of Done:**
- [ ] All Phase 1 files created
- [ ] X BDD scenarios passing
- [ ] Unit tests passing
- [ ] Verification scripts pass

### Phase 2: {Name}
...

## Dependency Graph
```
Phase 1 (Domain & Data)
    ↓
Phase 2 (Application Layer)
    ↓
Phase 3 (API Layer)
    ↓
Phase 4 (Frontend)
```
```

### Step 3: Get Approval

**Present phase plan to user:**
1. Show phase breakdown
2. Explain rationale for phasing
3. Highlight dependencies
4. Request approval to proceed

**Wait for approval before implementing.**

### Step 4: Implement Phase

Once approved, implement the current phase:

1. **Create files** listed in phase plan
2. **Write code** following TDD architecture
3. **Write tests** for phase's BDD scenarios
4. **Run verification:**
   - BDD tests for this phase
   - Unit tests
   - Linting, type checking
5. **Verify all pass** before marking complete

### Step 5: Phase Completion

**Mark phase complete when:**
- All files created
- All tests passing (BDD + unit)
- Verification scripts pass
- Code reviewed (if applicable)

**Then ask:** "Phase X complete. Proceed to Phase X+1?"

---

## Phasing Strategies

### Strategy 1: Layer-Based (Recommended)

**Phase 1:** Domain Layer + Database
- Value objects, entities, domain events
- Database schema (migration)
- Repository interfaces and implementations
- Domain unit tests

**Phase 2:** Application Layer
- Commands, queries
- Handlers (command + query)
- Application logic tests
- BDD scenarios for domain logic

**Phase 3:** API Layer
- Controller endpoints
- Request/response schemas
- API integration tests
- BDD scenarios for API contracts

**Phase 4:** Frontend
- Pages, components
- API integration
- React hooks
- E2E tests

**Rationale:** Each layer builds on previous, clear separation of concerns

### Strategy 2: Feature-Based

**Phase 1:** Core Feature (MVP)
- Minimum viable functionality
- Essential BDD scenarios only
- All layers (vertical slice)

**Phase 2:** Extended Features
- Optional fields, advanced features
- Additional BDD scenarios

**Phase 3:** Polish
- Error handling edge cases
- Security hardening
- Performance optimization

**Rationale:** Get working feature fast, iterate

### Strategy 3: Hybrid (Complex Features)

**Phase 1:** Foundation
- New value objects, database schema
- Repository setup

**Phase 2:** Read Operations
- Query handlers, GET endpoints
- View functionality

**Phase 3:** Write Operations
- Command handlers, POST/PATCH endpoints
- Update functionality

**Phase 4:** Frontend
- UI components, pages

**Rationale:** Read before write, API before UI

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

---

## Phase 1: {Name}

### Goal
What this phase achieves in 1-2 sentences.

### Scope

**Backend:**
- Domain: `list/of/files.py`
- Infrastructure: `list/of/files.py`
- Application: `list/of/files.py`

**Frontend:**
- None (or list)

**Tests:**
- BDD: X scenarios (list titles)
- Unit: Y test files

### BDD Scenarios

**From {feature}.feature:**
- [ ] Line X: Scenario title
- [ ] Line Y: Scenario title
...

### Dependencies
- None (first phase)
- Or: Requires Phase X to be complete

### Estimated Time
X-Y hours

### Definition of Done
- [ ] All files created/modified
- [ ] X BDD scenarios passing
- [ ] Y unit tests passing
- [ ] Linting passes
- [ ] Type checking passes
- [ ] No breaking changes to existing features

### Verification Commands
```bash
# Backend
pytest tests/features/{context}/test_{feature}.py::test_scenario_X
pytest tests/unit/...
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
[Visual representation of phase dependencies]
```

---

## Implementation Notes

**Patterns to Follow:**
- Follow existing {context} patterns
- Match registration-authentication structure
- Use same value object patterns
- Follow hexagonal architecture

**Common Pitfalls:**
- Don't skip value object validation
- Don't forget domain events
- Don't bypass aggregate boundaries
- Don't write integration tests before unit tests

**Testing Strategy:**
- Write BDD scenario outline first
- Implement step definitions
- Write domain unit tests
- Then implement feature
- BDD tests should pass when done
```

---

## Quality Checklist

Before marking any phase complete:

- [ ] All phase files created
- [ ] Code follows existing patterns
- [ ] All phase BDD scenarios passing
- [ ] Unit tests written and passing
- [ ] No regressions (existing tests still pass)
- [ ] Linting passes (ruff)
- [ ] Type checking passes (mypy)
- [ ] No security issues introduced
- [ ] Documentation updated (if needed)
- [ ] Git commit created with clear message

---

## Example: Simple Feature (Single Phase)

**Feature:** Add "bio" field to profile

**Complexity:** Low (3 scenarios, 4 files)

**Approach:** Single-phase implementation
1. Add bio field to Profile entity
2. Update repository mapping
3. Update API schema
4. Add validation tests
5. Run verification

**Time:** 1-2 hours

---

## Example: Complex Feature (Multi-Phase)

**Feature:** User Profile (full implementation)

**Complexity:** High (42 scenarios, 20+ files)

**Approach:** 4-phase implementation

**Phase 1:** Domain & Data (4 hours)
- 3 value objects, database migration, repositories
- 10 scenarios (validation)

**Phase 2:** Profile Viewing (3 hours)
- GET endpoints, query handlers
- 8 scenarios (view own/other profiles)

**Phase 3:** Profile Updates (4 hours)
- PATCH endpoint, update command/handler
- 15 scenarios (update fields)

**Phase 4:** Frontend (5 hours)
- ProfileView, ProfileEdit pages
- 9 scenarios (UI interactions)

**Total:** 16 hours (spread over 4 phases)

---

## When to Use Single Phase

Use single-phase implementation when:
- Feature is small (< 20 BDD scenarios)
- Few files affected (< 10 files)
- No complex dependencies
- Can be implemented in < 4 hours
- Risk is low

**Example single-phase features:**
- Add a single field to existing entity
- Simple validation rule change
- New query endpoint (read-only)
- UI component update

---

## When to Use Multi-Phase

Use multi-phase implementation when:
- Feature is large (≥ 20 BDD scenarios)
- Many files created (≥ 10 files)
- Complex cross-layer changes
- Takes > 4 hours to implement
- High risk of breaking existing features

**Example multi-phase features:**
- New aggregate with multiple entities
- Full CRUD operations across layers
- Complex business logic with many edge cases
- Frontend + Backend integration

---

## Anti-Patterns to Avoid

❌ **Don't phase by "backend then frontend"**
- Problem: Frontend waits for all backend work
- Better: Phase by feature slice (vertical), implement backend+frontend for one slice

❌ **Don't create phases that can't be tested independently**
- Problem: Can't verify until all phases done
- Better: Each phase has passing BDD scenarios

❌ **Don't make phases too small**
- Problem: Too much coordination overhead
- Better: Each phase should be 2-4 hours of work

❌ **Don't make phases too large**
- Problem: Hard to review, high risk
- Better: Keep phases focused and manageable

❌ **Don't skip phase plan approval**
- Problem: Wasted effort if user disagrees with approach
- Better: Always get approval before implementing

---

## Success Criteria

**A good phase plan:**
- ✅ Each phase independently testable
- ✅ Each phase provides incremental value
- ✅ Clear dependencies between phases
- ✅ Reasonable time estimates (2-4 hours per phase)
- ✅ BDD scenarios evenly distributed
- ✅ Low risk of breaking existing features
- ✅ Can be reviewed and approved separately

**A bad phase plan:**
- ❌ Phases depend on each other in complex ways
- ❌ No way to test until all phases done
- ❌ Uneven distribution (Phase 1: 1 hour, Phase 2: 10 hours)
- ❌ Arbitrary splits (Phase 1: Files A-M, Phase 2: Files N-Z)
- ❌ All BDD scenarios in last phase
