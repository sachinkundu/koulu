# Vertical Slicing Enforcement Strategy

**Date Created:** 2026-02-08
**Status:** Active Policy
**Related:** `CLAUDE.md`, Phase Implementation Templates

---

## Problem Statement

### What Happened

Two major features (Community Feed and Classroom) were implemented using a strategy called "vertical slicing" but resulted in **backend-only implementations** with no user-facing UI, violating the core principle of vertical slicing: **end-to-end deliverability**.

**Community Feed:**
- **Claimed:** "Vertical slicing (all layers per phase)"
- **Phase 1 Scope Promised:** CreatePostModal.tsx, PostDetail.tsx, CommunityPage.tsx
- **Reality:** "Frontend implementation (deferred pending UI design)"
- **Phases 1-2 Complete:** 39 BDD scenarios passing, 89% coverage, ZERO UI components
- **Result:** Fully functional backend API with no way for users to interact with it

**Classroom:**
- **Claimed:** "Vertical slicing" strategy
- **Phase Scope Reality:** NO frontend section in any of 4 phases
- **Phases 1-2 Complete:** Backend fully implemented, tests passing
- **Result:** Honest about being backend-only, but misleadingly called it "vertical slicing"

### Impact

- Features appear "complete" in summaries but are not deployable
- No user value delivered despite passing tests
- E2E tests cannot be written (no UI to test)
- Creates technical debt and false sense of progress
- Violates Definition of Done (features must be deployable)

---

## Root Cause Analysis

### Community Feed

1. **Scope Creep During Planning:** Frontend was in original Phase 1 scope but got deferred
2. **"Pending UI Design" Excuse:** UI_SPEC.md created but implementation never triggered
3. **No Enforcement:** Definition of Done not checked before marking phase complete
4. **Backend Bias:** Focus on "all architectural layers" (domain, application, infrastructure, interface) ignoring that "interface" only meant REST API, not UI

### Classroom

1. **Horizontal Slicing Disguised:** Never planned frontend but called strategy "vertical"
2. **No Challenge:** Phase plans accepted without questioning lack of UI section
3. **Terminology Confusion:** "Vertical slicing" interpreted as "all backend layers" instead of "full user journey"

### Systemic Issues

- **No automated checks** for frontend existence before marking phase complete
- **Ambiguous "vertical slicing" definition** in CLAUDE.md
- **Phase templates don't enforce** frontend section
- **Summaries don't require** explanation when UI is missing
- **Cultural acceptance** of backend-only as "done"

---

## Mitigation Strategy

### 1. Explicit Vertical Slicing Definition in CLAUDE.md

**Add to CLAUDE.md:**

```markdown
## Vertical Slicing: True Definition

A **vertical slice** delivers a complete user journey through ALL layers:

```
User → UI Component → API Endpoint → Handler → Domain Logic → Database → Response → UI Update
```

**Vertical slice includes:**
- ✅ Domain entities and business logic
- ✅ Application handlers (commands/queries)
- ✅ Infrastructure (repositories, database migrations)
- ✅ API endpoints (REST controllers)
- ✅ **Frontend UI components** (pages, forms, displays)
- ✅ **E2E tests** (browser automation through full journey)
- ✅ BDD integration tests (API-level)
- ✅ Unit tests (domain logic)

**NOT vertical slicing:**
- ❌ "All backend layers" without frontend
- ❌ "API-first" with deferred UI
- ❌ "Pending UI design" as reason to skip frontend
- ❌ Backend complete, UI "to be done later"

**Rare exceptions requiring explicit approval:**
- Background jobs (no direct user interaction)
- Internal admin APIs (UI in separate sprint)
- Migration/sync services

**For ALL other features: No UI = Not Done**
```

### 2. Updated Phase Planning Template

**Mandatory Phase Plan Structure:**

```markdown
# {Feature} Phase {N} - Implementation Plan

## Scope

### Backend (Domain → API)
- [ ] Domain entities
- [ ] Value objects
- [ ] Application handlers
- [ ] Repository implementations
- [ ] API endpoints
- [ ] Database migrations

### Frontend (User-Facing UI) **← MANDATORY SECTION**
- [ ] React components (list specific files)
- [ ] Pages/routes
- [ ] Forms and validation
- [ ] State management
- [ ] API integration

**IF NO FRONTEND IN THIS PHASE:**
Explicitly state reason:
- [ ] Background job (no user interaction)
- [ ] Internal API (admin UI in Phase X)
- [ ] Migration service (no UI needed)

### Testing
- [ ] BDD scenarios (API-level)
- [ ] Unit tests (domain logic)
- [ ] **E2E tests (UI automation)** ← Required if UI exists

### Deliverable
**User can:** {describe what user can DO via UI}
**Example:** "User can create a post via CreatePostModal, see it in feed, and click to view details"

**NOT acceptable:** "API endpoints allow post creation" (no user-visible value)
```

### 3. Automated Deployability Check

**Create `scripts/check-deployability.sh`:**

```bash
#!/usr/bin/env bash
set -e

# Deployability Check: Verifies features have UI components

FEATURE=$1
if [ -z "$FEATURE" ]; then
    echo "Usage: ./scripts/check-deployability.sh <feature-name>"
    exit 1
fi

echo "🔍 Checking deployability for: $FEATURE"

# Check backend exists
if [ ! -d "src/$FEATURE" ]; then
    echo "❌ Backend not found: src/$FEATURE"
    exit 1
fi
echo "✅ Backend found: src/$FEATURE"

# Check API endpoints exist
API_FILES=$(find "src/$FEATURE/interface/api" -name "*_controller.py" 2>/dev/null | wc -l)
if [ "$API_FILES" -eq 0 ]; then
    echo "❌ No API controllers found in src/$FEATURE/interface/api"
    exit 1
fi
echo "✅ API endpoints found: $API_FILES controllers"

# Check frontend exists
FRONTEND_DIR="frontend/src/features/$FEATURE"
if [ ! -d "$FRONTEND_DIR" ]; then
    echo "⚠️  WARNING: No frontend found at $FRONTEND_DIR"
    echo ""
    echo "📋 Analysis:"
    echo "   ✅ Backend implemented"
    echo "   ❌ Frontend missing"
    echo ""
    echo "🛠️  This feature is NOT deployable (no user-facing UI)"
    echo ""
    echo "Next steps:"
    echo "1. If backend-only is intentional (background job, internal API):"
    echo "   - Document in docs/features/$FEATURE/*-phases.md why no UI needed"
    echo "   - Add 'Why No UI?' section to phase summary"
    echo ""
    echo "2. If UI should exist:"
    echo "   - Implement components in $FRONTEND_DIR"
    echo "   - Add routes to frontend/src/pages/"
    echo "   - Write E2E tests in tests/e2e/specs/$FEATURE/"
    echo "   - Re-run this script to verify"
    exit 1
fi

COMPONENT_FILES=$(find "$FRONTEND_DIR" -name "*.tsx" 2>/dev/null | wc -l)
if [ "$COMPONENT_FILES" -eq 0 ]; then
    echo "❌ Frontend directory exists but no .tsx components found"
    exit 1
fi
echo "✅ Frontend found: $COMPONENT_FILES components"

# Check E2E tests exist
E2E_DIR="tests/e2e/specs/$FEATURE"
if [ ! -d "$E2E_DIR" ]; then
    echo "⚠️  WARNING: No E2E tests found at $E2E_DIR"
    echo "   Frontend exists but no browser automation tests"
    echo "   Create tests with: /write-e2e-tests $FEATURE"
    # Don't fail - E2E tests can be added after feature works
fi

echo ""
echo "✅ Feature is DEPLOYABLE:"
echo "   ✅ Backend: $API_FILES controllers"
echo "   ✅ Frontend: $COMPONENT_FILES components"
echo "   ✅ Users can interact with this feature"
echo ""
echo "🚀 Ready for deployment"
```

**Usage:**
```bash
# Before marking phase complete
./scripts/check-deployability.sh community
./scripts/check-deployability.sh classroom

# Will exit 1 and show warnings if no UI found
```

### 4. Updated Definition of Done

**Add to CLAUDE.md Verification section:**

```markdown
### Deployability Check (Required for User-Facing Features)

**Before marking phase complete, run:**
```bash
./scripts/check-deployability.sh {feature-name}
```

**Required output:**
```
✅ Feature is DEPLOYABLE:
   ✅ Backend: X controllers
   ✅ Frontend: Y components
   ✅ Users can interact with this feature
```

**If check fails:**
- Feature is NOT complete
- Either implement frontend OR document why backend-only is acceptable
- Get explicit user approval for backend-only exception

**Valid exceptions (require documentation):**
- Background jobs (no direct user interaction)
- Internal admin APIs (UI tracked in separate story)
- Migration/sync services (no UI needed)

**For ALL other features: No UI = Not Done**
```

### 5. Skill Updates

#### `/implement-feature` Skill

**Add to workflow checklist:**

```markdown
### Pre-Implementation Phase Analysis

**Before starting ANY phase, verify:**

1. **Is this a user-facing feature?**
   - User-facing = Community posts, classroom lessons, member profiles, calendar events
   - NOT user-facing = Background sync jobs, admin migrations, internal APIs

2. **If user-facing, does phase scope include frontend?**
   - Read phase plan → check for "Frontend" section
   - If missing: STOP and ask user:
     ```
     ⚠️  Phase plan has no frontend section.

     This appears to be a user-facing feature but phase scope
     only includes backend (domain → API).

     Options:
     1. Add frontend to this phase (recommended for vertical slice)
     2. Explicitly defer frontend with documented reason
     3. Confirm this is backend-only (background job, internal API)

     Which approach should I take?
     ```

3. **If frontend included, verify UI_SPEC.md exists:**
   - Check `docs/features/{feature}/UI_SPEC.md`
   - If missing: STOP and prompt:
     ```
     ❌ Frontend in scope but no UI_SPEC.md found.

     Cannot implement UI without design specification.

     Next steps:
     1. Generate UI_SPEC: /generate-ui-spec {feature}
     2. OR: Remove frontend from this phase scope
     ```

**NEVER start implementation if:**
- User-facing feature with no frontend section in plan
- Frontend in scope but no UI_SPEC.md available
- "Deferred pending UI design" used as excuse
```

#### `/write-e2e-tests` Skill

Already handles this correctly:
- Checks if frontend exists BEFORE generating tests
- Warns and exits if no UI found
- Shows exactly what's missing (components, routes)

**No changes needed** - this skill already enforces UI requirement.

### 6. "Why No UI?" Section in Summaries

**Mandatory section for backend-only phases:**

```markdown
## Why No UI?

**This phase implemented backend-only. Reason:**

[ ] Background job - No direct user interaction
    - Details: {explain what job does}

[ ] Internal admin API - UI tracked separately
    - UI Story: {link to frontend story/phase}

[ ] Migration service - No UI needed
    - Details: {explain migration purpose}

[ ] Foundation phase - UI in next phase
    - Frontend Phase: Phase {N}
    - Reason for split: {explain why backend first}

**User Impact:**
- Users CANNOT use this feature yet (no UI)
- Value delivered: {explain what value, if any}
- Full value delivered: Phase {N} when UI implemented

**Mitigation:**
- Frontend tracked in: {document/issue link}
- Target completion: {date/sprint}
```

**If this section is missing from a summary claiming backend-only:**
- Summary is NOT complete
- Phase cannot be marked done
- Document must explain UI absence

### 7. Retrospective Questions

**After each phase, ask:**

1. **Can a user interact with this feature?**
   - If NO: Why not? Is backend-only justified?
   - If YES: Show me the UI file paths

2. **If I run `/write-e2e-tests {feature}`, will it:**
   - ✅ Find UI and generate tests?
   - ❌ Warn "Frontend not found" and exit?

3. **Would a non-technical stakeholder see value?**
   - If NO: This is likely horizontal slicing disguised as vertical

4. **What can users DO now that they couldn't before?**
   - "Create posts via UI" ✅ (user value)
   - "API accepts post creation" ❌ (no user value)

### 8. Feature Status Dashboard

**Create `docs/FEATURE_STATUS.md`:**

```markdown
# Feature Implementation Status

| Feature | Backend | Frontend | E2E Tests | Deployable? | User Value |
|---------|---------|----------|-----------|-------------|------------|
| Community Feed | ✅ Phases 1-2 | ❌ Missing | ❌ Cannot write | ❌ NO | None (API-only) |
| Classroom | ✅ Phases 1-2 | ❌ Missing | ❌ Cannot write | ❌ NO | None (API-only) |
| Identity | ✅ Complete | ⚠️ Partial | ⚠️ Partial | ⚠️ PARTIAL | Login/register only |

**Legend:**
- ✅ Complete - Working and tested
- ⚠️ Partial - Some parts working
- ❌ Missing - Not implemented
- 🚧 In Progress - Currently being built

**Deployable = Backend + Frontend + Tests**

**Action Items:**
- [ ] Community Feed: Implement frontend (Phases 1-2 scope)
- [ ] Classroom: Implement frontend (Phases 1-2 scope)
```

**Update this file:**
- After each phase completion
- During retrospectives
- Before marking work "done"

### 9. Enforcement in CLAUDE.md

**Add to "New Feature" workflow:**

```markdown
### New Feature Workflow

```
1. git checkout -b feature/description

2. Write phase plan → docs/features/{feature}/*-phases.md
   ⚠️  REQUIRED: Include "Frontend" section for user-facing features
   ⚠️  If backend-only: Document explicit reason

3. Write BDD spec → tests/features/*.feature
   - Scenarios test API behavior
   - NOT a substitute for E2E tests (which test UI)

4. Implement backend (domain → API)
   - Domain entities, handlers, repositories
   - API endpoints
   - Database migrations

5. Implement frontend (UI → User value)
   - React components in frontend/src/features/{feature}/
   - Routes in frontend/src/pages/
   - Forms, displays, interactions
   - ⚠️  REQUIRED for user-facing features

6. Write E2E tests (browser automation)
   - Use: /write-e2e-tests {feature}
   - Tests complete user journeys through UI
   - ⚠️  Will fail if no UI exists

7. Run deployability check
   ./scripts/check-deployability.sh {feature}
   ⚠️  BLOCKING: Must pass before marking phase complete

8. Run verification scripts
   - All tests pass (0 failed)
   - Coverage ≥80%
   - No warnings

9. Notify user—NEVER merge yourself
```

**Valid reasons to skip frontend (rare):**
- Background job (no user interaction)
- Internal admin API (UI separate story)
- Migration service (no UI needed)

**ALL other features: No UI = Not Done**
```

### 10. Cultural Change: "Backend-Complete" ≠ "Done"

**Mindset shift required:**

| OLD (Wrong) | NEW (Correct) |
|-------------|---------------|
| "Phase 1 complete: backend working" | "Phase 1 complete: users can create posts" |
| "API endpoints tested and documented" | "Feature tested through UI and API" |
| "Domain logic implemented" | "User journey end-to-end functional" |
| "39 scenarios passing" | "39 scenarios + 5 E2E tests passing" |
| "Deferring frontend pending UI design" | "Frontend in scope, UI_SPEC required upfront" |
| "Vertical slicing = all backend layers" | "Vertical slicing = user can DO something" |

**Guiding principle:**
> If a non-technical stakeholder can't see or use the feature, it's not done.

**Exceptions are RARE and require:**
1. Explicit documentation in phase plan
2. "Why No UI?" section in summary
3. User approval before proceeding
4. Tracking story for when UI will be built

---

## Implementation Checklist

### Immediate Actions

- [ ] Update CLAUDE.md with explicit vertical slicing definition
- [ ] Create `scripts/check-deployability.sh` automation
- [ ] Update `/implement-feature` skill with pre-phase checks
- [ ] Create phase plan template with mandatory frontend section
- [ ] Create `docs/FEATURE_STATUS.md` dashboard
- [ ] Add "Why No UI?" requirement for backend-only summaries

### Verification

- [ ] Run deployability check on community feed (expect failure)
- [ ] Run deployability check on classroom (expect failure)
- [ ] Update feature status dashboard with current state
- [ ] Document community + classroom as "backend-only, needs UI"

### Cultural

- [ ] Review this document with team
- [ ] Establish "No UI = Not Done" as default policy
- [ ] Define rare exceptions requiring explicit approval
- [ ] Add retrospective questions to phase completion checklist

---

## Success Metrics

**We'll know this is working when:**

1. **No more backend-only "vertical slices"**
   - Feature summaries show both backend + frontend complete
   - E2E tests exist for all user-facing features

2. **Deployability checks pass**
   - `./scripts/check-deployability.sh` shows ✅ for all features
   - No warnings about missing UI components

3. **Feature status dashboard accurate**
   - "Deployable?" column shows ✅ for completed features
   - "User Value" column describes what users can DO

4. **Phase plans include frontend upfront**
   - No "deferred pending UI design" escape clauses
   - UI_SPEC.md created before implementation starts

5. **Summaries explain UI absence**
   - If backend-only, "Why No UI?" section documents reason
   - Explicit tracking of when UI will be built

---

## Related Documents

- `CLAUDE.md` - Project-wide implementation rules
- `docs/testing/e2e-testing-design.md` - E2E test strategy
- `.claude/skills/write-e2e-tests/SKILL.md` - E2E test generation
- `.claude/skills/implement-feature/SKILL.md` - Feature implementation workflow
- `docs/FEATURE_STATUS.md` - Current implementation status dashboard

---

## Revision History

| Date | Change | Reason |
|------|--------|--------|
| 2026-02-08 | Initial creation | Community Feed + Classroom backend-only implementations violated vertical slicing |
