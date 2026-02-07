---
name: implement-feature
description: Implement a feature from completed PRD and BDD specs
model: opus
---

# Implement Feature (Vertical Slicing)

## Purpose

Implement features from approved PRD, TDD, and BDD specifications using vertical slicing for complex features.

**Key Principle:** Each phase delivers a working end-to-end slice through all layers, ensuring tests pass and features are deployable at every phase.

**Default Strategy:** Vertical slicing (all layers per phase) to enable continuous integration with passing CI tests.

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

### Step 1: Check Branch and Create Feature Branch

**Before starting implementation:**

1. **Check current branch:**
   ```bash
   git branch --show-current
   ```

2. **If on `main` or `master`:**
   - Create a new feature branch following the naming convention: `feature/<context>-<feature-name>`
   - Example: `feature/identity-profile`
   ```bash
   git checkout -b feature/<context>-<feature-name>
   ```

3. **If already on a feature branch:**
   - For bug fixes or iterations on the same feature, stay on the current branch
   - For a completely new feature, create a new branch

**Critical:** NEVER implement features directly on `main` or `master`. Always work on a feature branch.

### Step 2: Analyze Complexity

Read PRD, TDD, and BDD specs to assess feature complexity.

**Complexity Indicators:**
- Number of BDD scenarios (> 20 = complex)
- Number of new files (> 10 = complex)
- Number of dependencies (> 2 contexts = complex)
- Number of API endpoints (> 3 = complex)
- Estimated implementation time (> 4 hours = complex)

**Decision:**
- **Simple feature** (< 20 scenarios, < 10 files): Single-phase implementation
- **Complex feature** (≥ 20 scenarios, ≥ 10 files): Multi-phase vertical slicing

**Phasing Strategy:** Use vertical slicing (all layers per phase) as the default to ensure:
- ✅ CI tests pass after each phase
- ✅ Each phase is deployable
- ✅ User-facing functionality available incrementally
- ✅ Low risk of integration issues

### Step 3: Create Phase Plan (if complex)

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

### Step 4: Get Approval

**Present phase plan to user:**
1. Show phase breakdown
2. Explain rationale for phasing
3. Highlight dependencies
4. Request approval to proceed

**Wait for approval before implementing.**

### Step 5: Implement Phase

Once approved, implement the current phase:

1. **Create files** listed in phase plan
2. **Write code** following TDD architecture
3. **Write tests** for phase's BDD scenarios:
   - **Implement** step definitions for scenarios enabled in this phase
   - **Skip** scenarios for future phases with `@pytest.mark.skip(reason="Phase X: condition")`
   - **Document** which scenarios are skipped and why
4. **Run verification:**
   - BDD tests for this phase (should show "X passed, Y skipped")
   - Unit tests
   - Linting, type checking
   - Verify all skip markers include phase numbers
5. **Verify all pass** before marking complete
   - All enabled tests pass ✅
   - All skipped tests have phase markers ✅
   - CI green ✅

### Step 6: Phase Completion

**Mark phase complete when:**
- All files created
- All phase-specific tests passing (BDD + unit)
- Future tests skipped with phase markers
- Verification scripts pass
- CI green (no failing tests)
- Code reviewed (if applicable)

**Report completion with:**
- Test pass/skip counts (e.g., "8 passed, 30 skipped")
- Which scenarios are skipped and for which phase
- CI status (must be green ✅)
- Coverage percentage (must meet threshold)

**Then ask:** "Phase X complete. Proceed to Phase X+1?"

**Example completion message:**
```
Phase 1 Complete ✅

Tests: 8 passed, 30 skipped (Phase 2: 12, Phase 3: 18)
Coverage: 81%
CI: Green ✅
Deployable: Yes

Proceed to Phase 2 (Validation & Error Handling)?
```

### Step 7: Consider E2E Tests (Optional)

After phase completion, consider if E2E tests would add value:

**When to consider E2E tests:**
- ✅ Feature involves multi-page user journey
- ✅ Feature has complex frontend-backend integration
- ✅ Feature is critical to business (auth, payment, core workflow)
- ✅ Frontend UI is implemented (Phase 4+)

**When to skip E2E tests:**
- ❌ Backend-only implementation (BDD tests sufficient)
- ❌ Simple CRUD (unit + BDD coverage adequate)
- ❌ Internal/admin features (lower priority)
- ❌ No frontend UI yet

**Important:** E2E tests are NOT part of Definition of Done. They are recommended for critical flows but optional. Use `/e2e-test` command to add E2E tests after phase completion if needed.

**See:** `docs/testing/e2e-testing-design.md` for E2E testing strategy and best practices.

---

## Phasing Strategies

### Strategy 1: Vertical Slicing (Default - Recommended)

**Use for:** Features requiring continuous integration, deployable increments, passing CI tests at each phase.

**Phase 1:** Core Happy Path (All Layers)
- Domain: Minimal entities + core value objects
- Application: Single command handler (success path only)
- Infrastructure: Basic repository + 1-2 API endpoints
- Frontend: Minimal UI (happy path only)
- Tests: 5-8 BDD scenarios (core flow works end-to-end)
- **Result:** Feature works end-to-end for basic case ✅

**Phase 2:** Validation & Error Handling (All Layers)
- Domain: Add validation to value objects
- Application: Error cases in handlers
- Infrastructure: Error responses in API (400, 409, etc.)
- Frontend: Error states + validation messages
- Tests: 8-12 BDD scenarios (validation + errors)
- **Result:** Feature handles invalid inputs gracefully ✅

**Phase 3:** Extended Features (All Layers)
- Domain: Additional value objects + business rules
- Application: Extended command/query handlers
- Infrastructure: Additional endpoints
- Frontend: Extended UI components
- Tests: 10-15 BDD scenarios (full feature set)
- **Result:** Feature complete with all functionality ✅

**Phase 4:** Security & Edge Cases (Optional)
- Application: Authorization checks
- Infrastructure: Rate limiting, logging, monitoring
- Tests: 5-8 BDD scenarios (security + edge cases)
- **Result:** Feature hardened for production ✅

**Rationale:** Each phase is deployable, CI green, user-facing functionality available incrementally

**Advantages:**
- ✅ All tests pass at each phase
- ✅ Can integrate/deploy after any phase
- ✅ Users see incremental value
- ✅ Low risk of breaking changes
- ✅ Fast feedback on integration issues

### Strategy 2: Layer-Based (Alternative)

**Use for:** Features with complex domain logic requiring foundation before integration, or when frontend is not ready.

**Phase 1:** Domain Layer + Database
- Value objects, entities, domain events
- Database schema (migration)
- Repository interfaces and implementations
- Domain unit tests

**Phase 2:** Application Layer
- Commands, queries, handlers
- Application logic tests
- BDD scenarios for domain logic

**Phase 3:** API Layer
- Controller endpoints, schemas
- API integration tests
- BDD scenarios for API contracts

**Phase 4:** Frontend
- Pages, components, API integration
- E2E tests

**Rationale:** Build solid foundation, clear separation of concerns

**Disadvantages:**
- ⚠️ Some BDD scenarios can't pass until later phases
- ⚠️ Can't deploy user-facing functionality until Phase 4
- ⚠️ Integration issues discovered late

**When to use:** Complex domain logic, backend-only features, or when UI design is not finalized.

### Strategy 3: Hybrid (Vertical Read/Write Split)

**Use for:** Features where read operations are simpler than write operations.

**Phase 1:** Foundation (Vertical - Read Only)
- Domain: Basic entities (read model)
- Application: Query handlers
- Infrastructure: Repository + GET endpoints
- Frontend: View/list pages
- Tests: BDD scenarios for viewing
- **Result:** Users can view data ✅

**Phase 2:** Write Operations (Vertical - Create/Update)
- Domain: Add write methods + validation
- Application: Command handlers
- Infrastructure: POST/PATCH endpoints
- Frontend: Forms, edit pages
- Tests: BDD scenarios for mutations
- **Result:** Users can modify data ✅

**Phase 3:** Advanced Features (Vertical)
- Domain: Complex business rules
- Application: Advanced handlers
- Infrastructure: Additional endpoints
- Frontend: Advanced UI
- Tests: BDD scenarios for advanced features
- **Result:** Full functionality available ✅

**Rationale:** Read before write, each phase adds capability

**Advantages:**
- ✅ Get data visible to users quickly (Phase 1)
- ✅ Each phase is deployable
- ✅ Simpler phases (read is easier than write)

---

## Test Management Across Phases

### Handling Tests That Can't Pass Yet

**Principle:** All committed code must have CI passing. Tests for future phases should be disabled with clear phase markers.

**When to skip tests:**
- BDD scenario requires functionality planned for a future phase
- Test depends on endpoints/components not yet implemented
- Feature is partially implemented (e.g., Phase 1 does create, Phase 2 does update)

**How to skip tests:**

#### Python (pytest-bdd)

```python
import pytest

# Mark individual scenario
@pytest.mark.skip(reason="Phase 2: Will be enabled when validation is implemented")
@scenario('features/posts.feature', 'Invalid post title rejected')
def test_invalid_post_rejected():
    pass

# Mark entire test function
@pytest.mark.skip(reason="Phase 3: Will be enabled when GET /posts endpoint is implemented")
def test_user_views_posts():
    """Scenario: User views list of posts"""
    pass

# Conditional skip based on phase
@pytest.mark.skipif(
    not hasattr(sys.modules['app.api.posts'], 'update_post'),
    reason="Phase 3: Waiting for update_post endpoint"
)
def test_user_updates_post():
    pass
```

#### Frontend (Vitest)

```typescript
import { describe, it, expect } from 'vitest';

// Skip individual test
it.skip('should show validation error for empty title', () => {
  // Phase 2: Will be enabled when validation UI is implemented
  expect(true).toBe(true);
});

// Skip entire test suite
describe.skip('Post editing', () => {
  // Phase 3: Will be enabled when PostEditForm is implemented
  it('should update post title', () => {
    // ...
  });
});
```

### Test Skip Documentation

**Always include in skip reason:**
1. **Phase number:** When test will be enabled
2. **Condition:** What needs to be implemented
3. **Optional context:** Why it's deferred

**Good skip reasons:**
```python
# ✅ Clear phase and condition
@pytest.mark.skip(reason="Phase 2: Will be enabled when DisplayName value object is implemented")

# ✅ Specific feature dependency
@pytest.mark.skip(reason="Phase 3: Requires POST /posts/:id/comments endpoint (Phase 3)")

# ✅ Technical blocker with phase
@pytest.mark.skip(reason="Phase 4: Needs frontend PostEditForm component")
```

**Bad skip reasons:**
```python
# ❌ No phase information
@pytest.mark.skip(reason="Not implemented yet")

# ❌ Too vague
@pytest.mark.skip(reason="TODO")

# ❌ No clear enablement condition
@pytest.mark.skip(reason="Later")
```

### Phase Completion Checklist with Skipped Tests

**Before marking phase complete:**

1. **All phase-specific tests pass:**
   ```bash
   pytest tests/features/posts.py -v
   # Should show: X passed, Y skipped (with Phase markers)
   ```

2. **Verify skip markers are correct:**
   ```bash
   # List all skipped tests with reasons
   pytest tests/features/ -v | grep "SKIPPED"

   # Verify all skips reference future phases
   grep -r "@pytest.mark.skip" tests/features/ | grep -v "Phase [2-9]"
   # Should return nothing (all skips have phase markers)
   ```

3. **Document skipped tests in phase summary:**
   ```markdown
   ## Phase 1 Complete

   **Tests Passing:** 8/8 phase-specific scenarios ✅
   **Tests Skipped:** 12 scenarios (Phase 2: 7, Phase 3: 5)
   **CI Status:** Green ✅

   **Skipped Scenarios (will be enabled in Phase 2):**
   - Invalid post title rejected (validation)
   - Empty post content rejected (validation)
   - Duplicate post prevented (validation)
   ...
   ```

4. **Update phase plan with actual skip count:**
   ```markdown
   ## Phase 1: Core Happy Path ✅ COMPLETE
   - Tests Passing: 8/8 ✅
   - Tests Skipped: 12 (documented for Phase 2+)
   - CI: Green ✅
   ```

### Moving from Skipped to Active

**When starting Phase 2:**

1. **List tests to enable:**
   ```bash
   # Find all tests marked for Phase 2
   grep -r "Phase 2:" tests/features/ | grep "@pytest.mark.skip"
   ```

2. **Remove skip markers:**
   ```python
   # Before (Phase 1)
   @pytest.mark.skip(reason="Phase 2: Will be enabled when validation is implemented")
   @scenario('features/posts.feature', 'Invalid post title rejected')
   def test_invalid_post_rejected():
       pass

   # After (Phase 2)
   @scenario('features/posts.feature', 'Invalid post title rejected')
   def test_invalid_post_rejected():
       pass
   ```

3. **Verify newly enabled tests pass:**
   ```bash
   # Run only Phase 2 tests (remove skip markers first)
   pytest tests/features/posts.py::test_invalid_post_rejected -v
   # Must pass before marking Phase 2 complete
   ```

### Alternative: Feature Flags (Advanced)

For features that need gradual rollout:

```python
# Environment-based skipping
@pytest.mark.skipif(
    os.getenv('FEATURE_POST_EDITING') != 'true',
    reason="Feature flag: POST_EDITING not enabled"
)
def test_user_edits_post():
    pass
```

**When to use:**
- Feature needs A/B testing
- Gradual rollout to production
- Feature toggle in codebase

**When NOT to use:**
- Simple phased implementation (use phase markers instead)
- Tests will definitely be enabled in next phase

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

**Enabled for this phase:**
- [ ] Line X: Scenario title (test_scenario_x)
- [ ] Line Y: Scenario title (test_scenario_y)
...

**Skipped (future phases):**
- Line A: Scenario title → Phase 2: Requires validation logic
- Line B: Scenario title → Phase 3: Requires update endpoint
...

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

### Verification Commands
```bash
# Backend - Run phase-specific tests
pytest tests/features/{context}/test_{feature}.py -v
# Expected: X passed, Y skipped (Phase markers visible)

# Verify all skips have phase markers
grep -r "@pytest.mark.skip" tests/features/{context}/ | grep "Phase [0-9]"

# List skipped tests for verification
pytest tests/features/{context}/ -v | grep "SKIPPED"

# Unit tests
pytest tests/unit/{context}/...
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

**Required (Definition of Done):**
- [ ] All phase files created
- [ ] Code follows existing patterns
- [ ] All phase-specific BDD scenarios passing (X passed)
- [ ] Future BDD scenarios skipped with phase markers (Y skipped, documented)
- [ ] Unit tests written and passing
- [ ] No regressions (existing tests still pass)
- [ ] Linting passes (ruff)
- [ ] Type checking passes (mypy)
- [ ] No security issues introduced
- [ ] Documentation updated (if needed)
- [ ] Git commit created with clear message
- [ ] **CI green** (all enabled tests pass, skipped tests have phase markers)

**Test Skip Verification:**
- [ ] Run `pytest tests/features/{context}/ -v` shows "X passed, Y skipped"
- [ ] Run `grep -r "@pytest.mark.skip" tests/features/{context}/` shows phase markers
- [ ] All skip reasons include phase number and condition
- [ ] Skipped tests documented in phase completion summary

**Optional (Recommended for critical flows):**
- [ ] E2E tests added for critical user journeys (use `/e2e-test` if needed)

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

## Example: Complex Feature (Vertical Slicing)

**Feature:** Community Feed (Post creation, viewing, reactions)

**Complexity:** High (38 scenarios, 18 files)

**Approach:** 3-phase vertical slicing

---

### Phase 1: Create & View Posts (Happy Path) - 4 hours

**All Layers:**
- Domain: `Post` entity (id, title, content, author_id, created_at)
- Application: `CreatePostHandler`, `GetPostHandler`
- Infrastructure: `SQLAlchemyPostRepository`, `POST /posts`, `GET /posts/:id`
- Frontend: `CreatePostForm`, `PostDetailPage`

**BDD Scenarios Enabled (8):**
- ✅ User creates a post with title and content
- ✅ User views their own post
- ✅ User views another user's post
- ✅ Post displays author name
- ✅ Post displays creation timestamp
- ✅ User creates multiple posts
- ✅ Post persists across sessions
- ✅ GET /posts/:id returns 404 for non-existent post

**BDD Scenarios Skipped (30) - Examples:**
```python
@pytest.mark.skip(reason="Phase 2: Will be enabled when validation is implemented")
@scenario('features/community/feed.feature', 'Empty title rejected')
def test_empty_title_rejected():
    pass

@pytest.mark.skip(reason="Phase 3: Will be enabled when GET /posts endpoint is implemented")
@scenario('features/community/feed.feature', 'User views feed of all posts')
def test_user_views_feed():
    pass
```

**Result:** Users can create and view posts ✅ | CI Green ✅

---

### Phase 2: Validation & Error Handling - 3 hours

**All Layers:**
- Domain: Add `PostTitle`, `PostContent` value objects with validation
- Application: Update handlers to use value objects, throw validation errors
- Infrastructure: Return 400 errors with validation messages
- Frontend: Show validation errors in `CreatePostForm`

**BDD Scenarios Enabled (12 new + 8 from Phase 1 = 20 total):**
- ✅ Empty title rejected (400 error)
- ✅ Title too long rejected (max 200 chars)
- ✅ Empty content rejected
- ✅ Content too long rejected (max 10,000 chars)
- ✅ Whitespace-only title rejected
- ✅ Invalid characters in title rejected
- ✅ Validation errors shown in UI
- ✅ User corrects validation error and submits successfully
- ✅ Multiple validation errors shown at once
- ✅ Authenticated user required for post creation
- ✅ Unauthenticated user sees 401 error
- ✅ User cannot create post for another user

**BDD Scenarios Skipped (18) - Examples:**
```python
@pytest.mark.skip(reason="Phase 3: Will be enabled when GET /posts and feed pagination are implemented")
@scenario('features/community/feed.feature', 'User views feed of all posts')
def test_user_views_feed():
    pass
```

**Result:** Robust validation prevents invalid posts ✅ | CI Green ✅

---

### Phase 3: Feed Listing & Pagination - 4 hours

**All Layers:**
- Domain: Add pagination logic
- Application: `ListPostsHandler` with pagination
- Infrastructure: `GET /posts` (paginated), feed repository queries
- Frontend: `FeedPage`, `PostList`, infinite scroll

**BDD Scenarios Enabled (18 new + 20 from Phase 1-2 = 38 total):**
- ✅ User views feed of all posts (newest first)
- ✅ Feed shows 20 posts per page
- ✅ User loads next page of posts
- ✅ Feed shows posts from all users
- ✅ User's own posts appear in feed
- ✅ Empty feed shows helpful message
- ✅ Feed updates when new post created
- ✅ Feed pagination handles edge cases
- ✅ Feed shows author avatars
- ✅ Feed shows relative timestamps ("2 hours ago")
- ✅ User clicks post to view detail
- ✅ Infinite scroll loads more posts
- ✅ Feed caches posts for performance
- ✅ Feed handles deleted posts gracefully
- ✅ User refreshes feed to see latest posts
- ✅ Feed sorting is stable
- ✅ Feed handles concurrent updates
- ✅ Feed shows loading state

**BDD Scenarios Skipped:** None (all 38 enabled)

**Result:** Full feed functionality ✅ | CI Green ✅ | **Feature Complete**

---

**Total Time:** 11 hours (spread over 3 phases)
**CI Status:** Green after every phase ✅
**Deployable:** After Phase 1, 2, or 3

---

## Phase Completion Report Example

**Example completion message for Phase 1:**

```markdown
## Phase 1 Complete: Create & View Posts (Happy Path) ✅

**Implementation Summary:**
- Domain: `Post` entity, basic value objects
- Application: `CreatePostHandler`, `GetPostHandler`
- Infrastructure: `SQLAlchemyPostRepository`, POST/GET endpoints
- Frontend: `CreatePostForm`, `PostDetailPage`

**Test Results:**
```
pytest tests/features/community/test_feed.py -v

tests/features/community/test_feed.py::test_create_post PASSED
tests/features/community/test_feed.py::test_view_own_post PASSED
tests/features/community/test_feed.py::test_view_other_post PASSED
tests/features/community/test_feed.py::test_post_author_name PASSED
tests/features/community/test_feed.py::test_post_timestamp PASSED
tests/features/community/test_feed.py::test_create_multiple_posts PASSED
tests/features/community/test_feed.py::test_post_persistence PASSED
tests/features/community/test_feed.py::test_get_nonexistent_post_404 PASSED
tests/features/community/test_feed.py::test_empty_title_rejected SKIPPED (Phase 2: Will be enabled when validation is implemented)
tests/features/community/test_feed.py::test_title_too_long SKIPPED (Phase 2: Will be enabled when PostTitle value object is implemented)
... (22 more skipped)

===================== 8 passed, 30 skipped in 2.34s =====================
```

**Coverage:**
```
TOTAL                          423     41      12      2    81%
```

**BDD Scenarios:**
- ✅ Enabled: 8/38 (21%) - All passing
- ⏭️ Skipped: 30/38 (79%) - Documented for Phase 2-3

**Skipped Scenarios Distribution:**
- Phase 2 (Validation): 12 scenarios
- Phase 3 (Feed Listing): 18 scenarios

**CI Status:** ✅ Green

**Verification:**
```bash
./scripts/verify.sh
✅ All checks passed

grep -r "@pytest.mark.skip" tests/features/community/ | grep "Phase [0-9]" | wc -l
30  # All skips have phase markers
```

**Deployment Status:** Ready to deploy - users can create and view posts

**Next Steps:** Proceed to Phase 2 (Validation & Error Handling)?
```

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
- Problem: Frontend waits for all backend work, can't deploy until Phase 4
- Better: Use vertical slicing (all layers per phase)

❌ **Don't create phases that can't be tested independently**
- Problem: Can't verify until all phases done, CI fails mid-implementation
- Better: Each phase has passing BDD scenarios (skip future scenarios with phase markers)

❌ **Don't skip tests without phase markers**
- Problem: No one knows when to re-enable tests
- Better: Always use `@pytest.mark.skip(reason="Phase X: Specific condition")`

❌ **Don't leave tests skipped after implementing the functionality**
- Problem: False sense of completion, tests not actually verifying behavior
- Better: Remove skip markers as soon as functionality is implemented in that phase

❌ **Don't make phases too small**
- Problem: Too much coordination overhead, too many skip/unskip cycles
- Better: Each phase should be 2-4 hours of work

❌ **Don't make phases too large**
- Problem: Hard to review, high risk, many skipped tests
- Better: Keep phases focused and manageable

❌ **Don't skip phase plan approval**
- Problem: Wasted effort if user disagrees with approach
- Better: Always get approval before implementing

❌ **Don't commit failing tests**
- Problem: CI fails, blocks other work
- Better: Skip tests for future phases with clear markers, ensure CI green

---

## Success Criteria

**A good phase plan:**
- ✅ Uses vertical slicing (all layers per phase) for deployability
- ✅ Each phase independently testable with passing CI
- ✅ Each phase provides incremental user-facing value
- ✅ Clear dependencies between phases
- ✅ Reasonable time estimates (2-4 hours per phase)
- ✅ BDD scenarios distributed across phases (some enabled, some skipped with markers)
- ✅ Low risk of breaking existing features
- ✅ Can be deployed after any phase
- ✅ Test skip strategy documented (which scenarios, which phase enables them)
- ✅ Can be reviewed and approved separately

**A bad phase plan:**
- ❌ Uses layer-based phasing when vertical slicing would work
- ❌ Phases depend on each other in complex ways
- ❌ No way to test until all phases done (no skip markers)
- ❌ Tests skipped without phase markers or conditions
- ❌ Uneven distribution (Phase 1: 1 hour, Phase 2: 10 hours)
- ❌ Arbitrary splits (Phase 1: Files A-M, Phase 2: Files N-Z)
- ❌ All BDD scenarios in last phase
- ❌ Can't deploy until all phases complete
