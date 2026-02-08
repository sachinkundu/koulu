# Feature Implementation Status

**Last Updated:** 2026-02-08

This dashboard tracks implementation status of all features in the Koulu platform.

## Status Legend

- ✅ **Complete** - Working and tested
- ⚠️ **Partial** - Some parts working
- ❌ **Missing** - Not implemented
- 🚧 **In Progress** - Currently being built

**Deployable = Backend + Frontend + Tests**

---

## Feature Status

| Feature | Backend | Frontend | E2E Tests | Deployable? | User Value |
|---------|---------|----------|-----------|-------------|------------|
| **Identity** | ✅ Complete | ⚠️ Partial | ⚠️ Partial | ⚠️ PARTIAL | Login/register only |
| **Community Feed** | ✅ Phases 1-2 | ❌ Missing | ❌ Cannot write | ❌ NO | None (API-only) |
| **Classroom** | ✅ Phases 1-2 | ❌ Missing | ❌ Cannot write | ❌ NO | None (API-only) |

---

## Feature Details

### Identity

**Status:** ⚠️ Partially Deployable

**Backend:**
- ✅ User registration
- ✅ Email verification
- ✅ Login/authentication
- ✅ Password hashing
- ✅ JWT tokens
- ✅ BDD tests passing

**Frontend:**
- ✅ Login page
- ✅ Registration page
- ⚠️ Limited UI components
- ❌ Full profile management missing

**E2E Tests:**
- ⚠️ Some tests exist
- ❌ Coverage incomplete

**User Value:** Users can register and log in

**Next Steps:**
- Complete profile management UI
- Add comprehensive E2E tests

---

### Community Feed

**Status:** ❌ NOT Deployable (Backend-Only)

**Backend:**
- ✅ Post creation, viewing, reactions
- ✅ Comment system
- ✅ Category management
- ✅ 39 BDD scenarios passing
- ✅ 89% code coverage
- ✅ Phases 1-2 complete

**Frontend:**
- ❌ No UI components
- ❌ No pages/routes
- ❌ No forms
- ❌ Zero .tsx files in `frontend/src/features/community/`

**E2E Tests:**
- ❌ Cannot write (no UI to test)

**User Value:** NONE - Users cannot interact with posts (API-only)

**Problem:**
Feature was implemented using claimed "vertical slicing" but only delivered backend layers. Frontend was "deferred pending UI design" despite UI_SPEC.md existing.

**Action Items:**
- [ ] Implement frontend components (Phases 1-2 scope):
  - [ ] CreatePostModal.tsx
  - [ ] PostDetail.tsx
  - [ ] CommunityPage.tsx
  - [ ] PostList.tsx
  - [ ] CommentSection.tsx
- [ ] Add routes to frontend/src/pages/
- [ ] Write E2E tests for post creation and viewing
- [ ] Run deployability check: `./scripts/check-deployability.sh community`

**Priority:** HIGH - Major feature claiming to be "complete" but not usable

---

### Classroom

**Status:** ❌ NOT Deployable (Backend-Only)

**Backend:**
- ✅ Course management
- ✅ Lesson system
- ✅ Phases 1-2 complete
- ✅ BDD tests passing

**Frontend:**
- ❌ No UI components
- ❌ No pages/routes
- ❌ No forms
- ❌ Zero .tsx files in `frontend/src/features/classroom/`

**E2E Tests:**
- ❌ Cannot write (no UI to test)

**User Value:** NONE - Users cannot access classroom (API-only)

**Problem:**
Feature was labeled "vertical slicing" in documentation but was honest about being backend-only. However, calling it "vertical slicing" was misleading since it only implemented backend layers.

**Action Items:**
- [ ] Implement frontend components:
  - [ ] CourseList.tsx
  - [ ] CoursePage.tsx
  - [ ] LessonViewer.tsx
  - [ ] LessonList.tsx
- [ ] Add routes to frontend/src/pages/
- [ ] Write E2E tests for course viewing and lessons
- [ ] Run deployability check: `./scripts/check-deployability.sh classroom`

**Priority:** HIGH - Core feature not accessible to users

---

## Summary Statistics

**Total Features:** 3
- ✅ Fully Deployable: 0
- ⚠️ Partially Deployable: 1 (Identity)
- ❌ Not Deployable: 2 (Community, Classroom)

**Technical Debt:**
- 2 features claiming to be "complete" but lacking frontend UI
- Both features have passing backend tests but no user-facing value
- E2E test coverage blocked by missing UI

---

## Verification Commands

Run these commands to verify current status:

```bash
# Check deployability of each feature
./scripts/check-deployability.sh identity
./scripts/check-deployability.sh community    # Expected to fail
./scripts/check-deployability.sh classroom    # Expected to fail

# Check backend implementation
ls -la src/identity src/community src/classroom

# Check frontend implementation
ls -la frontend/src/features/

# Check E2E tests
ls -la tests/e2e/specs/
```

---

## Policy

**Going forward, a feature is NOT complete until:**

1. ✅ Backend implemented (domain → API)
2. ✅ Frontend implemented (UI components → user interaction)
3. ✅ BDD tests passing (API-level)
4. ✅ Unit tests passing (domain logic)
5. ✅ Deployability check passes: `./scripts/check-deployability.sh {feature}`
6. ✅ Coverage ≥80%

**Valid exceptions (rare, require explicit approval):**
- Background jobs (no direct user interaction)
- Internal admin APIs (UI tracked in separate story)
- Migration/sync services (no UI needed)

**For ALL other features: No UI = Not Done**

See `docs/process/vertical-slicing-enforcement.md` for full policy details.

---

## Revision History

| Date | Change | Reason |
|------|--------|--------|
| 2026-02-08 | Initial creation | Document current state after discovering backend-only implementations |
