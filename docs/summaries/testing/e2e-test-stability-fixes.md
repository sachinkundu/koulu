# E2E Test Stability Fixes - Implementation Summary

**Date:** 2026-02-13
**Status:** Complete
**Branch:** `feature/community-feed-phase4`

---

## What Was Fixed

Fixed 4 E2E test failures caused by UI implementation details and hot sorting behavior:

1. **Comment edit indicator**: Test expected `(edited)` but UI renders `· edited`
2. **Comment like button**: Test expected `<span>` with "Like" text when no likes, but button only shows SVG icon
3. **Category filter visibility**: Hot sort ranks zero-engagement posts last, causing them to fall below the fold
4. **Modal post view visibility**: Same hot sort issue affecting post card discovery

All 23 E2E tests now passing consistently across multiple runs (23/23 on 2 consecutive runs).

---

## Root Cause Analysis

### Issue 1: Edit Indicator Text Mismatch
- **Frontend**: `CommentCard.tsx` line 124 renders `· edited`
- **Test**: Expected `(edited)` with parentheses
- **Fix**: Updated test selector to match actual UI text

### Issue 2: Missing Like Button Text
- **Frontend**: `CommentCard.tsx` lines 168-172 only renders `<span>{like_count}</span>` when `like_count > 0`
- **Test**: `getCommentLikeText()` always waited for `<span>` to be visible, timing out when count is 0
- **Fix**: Check span count first, return `'0'` if no span exists (no likes yet)

### Issue 3 & 4: Hot Sort Engagement Bias
- **Problem**: Default "hot" sort (`(likes + comments*2) / (hours_since_creation + 2)^1.5`) ranks zero-engagement posts at the bottom
- **Race condition**: Parallel test workers create posts with comments/likes, pushing test's zero-engagement posts off page 1
- **React Query caching**: After filtering by category, clicking "All" serves stale cached results without the test's posts
- **Fix**: Added `selectSort('new')` before assertions that search for specific posts (chronological sort ensures recent posts appear first)

---

## Files Changed

### E2E Test Specs
- `tests/e2e/specs/community/comment-interactions.spec.ts`
  - Line 110: Changed `text=(edited)` to `text=· edited`
  - Line 183-184: Changed expectation from `'Like'` to `'0'` for zero-like state

- `tests/e2e/specs/community/feed.spec.ts`
  - Lines 56, 79, 167: Added `await feedPage.selectSort('new')` before searching for specific posts

### Page Object Models
- `tests/e2e/fixtures/pages/community/feed-page.ts`
  - Lines 88-93: Added `selectSort(sort)` method to switch sorting

- `tests/e2e/fixtures/pages/community/post-detail-page.ts`
  - Lines 168-174: Updated `getCommentLikeText()` to handle missing span (returns `'0'` when `span.count() === 0`)

---

## Test Results

### Before Fixes
- **20 passed, 3 failed** (36.5s)
- Failures:
  - `comment-interactions.spec.ts:69` — Edit indicator not found
  - `comment-interactions.spec.ts:158` — Like button span timeout
  - `feed.spec.ts:136` — Category filter post not found

### After Fixes (Run 1)
- **23 passed, 0 failed** (37.9s)

### After Fixes (Run 2 - Stability Check)
- **23 passed, 0 failed** (39.7s)

**Verdict:** 100% pass rate, stable across multiple runs

---

## Test Coverage by Area

| Area | Tests | Status |
|------|-------|--------|
| Community Feed | 5 | ✅ All passing |
| Comment Interactions | 4 | ✅ All passing |
| Community Interactions | 3 | ✅ All passing |
| Identity (Login/Logout/Profile) | 7 | ✅ All passing |
| Classroom (Courses) | 3 | ✅ All passing |
| Onboarding | 1 | ✅ All passing |

---

## How to Verify

Run E2E tests with correct ports:

```bash
cd tests/e2e

# Set environment variables for project-specific ports
BASE_URL=http://localhost:5240 \
API_URL=http://localhost:8067/api/v1 \
MAILHOG_URL=http://localhost:8092 \
npx playwright test

# Expected output: 23 passed
```

**Prerequisites:**
- Backend running on port 8067
- Frontend running on port 5240
- Docker containers running (postgres, redis, mailhog)
- Redis flushed before each run: `docker exec koulu_redis redis-cli FLUSHALL`

---

## Lessons Learned

1. **UI text must match exactly**: E2E selectors using `text=` must match the actual rendered text character-for-character

2. **Conditional rendering breaks naive selectors**: When elements only appear conditionally (like the like count span), Page Object Models must handle both presence and absence

3. **Hot sort creates non-deterministic feeds**: When testing specific posts in feeds with default "hot" sort, posts with zero engagement will rank below posts with any engagement
   - **Solution**: Switch to "new" sort (chronological) before assertions that search for specific test posts
   - **Alternative**: Add engagement (likes/comments) to test posts via API before searching for them

4. **React Query caching amplifies sort issues**: Switching between category filters serves cached results, so zero-engagement posts may never appear even after clicking "All"

---

## Deferred / Out of Scope

- No changes to hot sort algorithm (working as designed)
- No changes to frontend UI text (existing design is intentional)
- No changes to conditional rendering logic (correct implementation)

---

## Next Steps

E2E test suite is now stable. Future considerations:

- [ ] Document the hot sort pattern in E2E testing guide
- [ ] Consider adding a test helper to create posts with engagement for tests that need visibility
- [ ] Monitor for similar issues in future features (calendar events, classroom lessons)
