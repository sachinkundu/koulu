# Community Feed - Phase 3 Implementation Summary

**Date:** February 11, 2026
**Status:** Phase 3 of 4 Complete
**PRD:** `docs/features/community/feed-prd.md`
**BDD Spec:** `tests/features/community/feed.feature`

---

## What Was Built

Phase 3 adds post pinning, feed sorting (Hot/New/Top), cursor-based pagination, admin category CRUD, and rate limiting. All 20 new BDD scenarios pass (613 total, 44 skipped for Phase 4, 87.31% coverage). The feed now supports dynamic sorting with visual pills, admins can manage categories, and rate limiting prevents spam (10 posts/hour).

---

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| In-memory rate limiter (class-level dict) | Simple for MVP, avoids Redis dependency, sufficient for current scale (can migrate to Redis later) |
| Cursor-based pagination with base64 JSON | Simple offset encoding, future-proof for keyset pagination |
| Hot sort formula: `(likes + comments*2) / (hours+2)^1.5` | Wilson-style ranking balances recency and engagement |
| Vertical slicing (4 slices) | Each slice independently testable with 0 failed tests, CI green throughout |
| SortDropdown pills (not dropdown) | Matches Skool.com UX pattern, more discoverable than hidden dropdown |

---

## Files Changed

### Domain Layer
- `src/community/domain/entities/post.py` — Added `pin()` and `unpin()` methods with role guards, publishes `PostPinned`/`PostUnpinned` events
- `src/community/domain/services/rate_limiter.py` — New `IRateLimiter` ABC for pluggable rate limiting
- `src/community/domain/repositories/post_repository.py` — Added `count_by_category()` for delete guard

### Application Layer
- `src/community/application/commands.py` — Added 5 commands: `PinPostCommand`, `UnpinPostCommand`, `CreateCategoryCommand`, `UpdateCategoryCommand`, `DeleteCategoryCommand`
- `src/community/application/handlers/pin_post_handler.py` — New handler for pinning (admin/mod only)
- `src/community/application/handlers/unpin_post_handler.py` — New handler for unpinning
- `src/community/application/handlers/create_category_handler.py` — New handler with name uniqueness check
- `src/community/application/handlers/update_category_handler.py` — New handler with conditional uniqueness check
- `src/community/application/handlers/delete_category_handler.py` — New handler with has-posts guard
- `src/community/application/handlers/create_post_handler.py` — Added rate limiter injection, checks limit before post creation
- `src/community/application/handlers/get_feed_handler.py` — Added `FeedResult` dataclass with cursor/has_more, requests `limit+1` for pagination detection
- `src/community/application/queries.py` — Added `sort` and `cursor` fields to `GetFeedQuery`

### Infrastructure Layer
- `src/community/infrastructure/services/in_memory_rate_limiter.py` — Class-level dict tracking timestamps, 10 posts/hour limit, `reset()` for tests
- `src/community/infrastructure/persistence/post_repository.py` — Implemented 3 sort modes (hot/new/top) with correlated subqueries for like/comment counts, cursor decoding, `is_pinned DESC` prefix
- `src/community/infrastructure/persistence/post_repository.py` — Added `count_by_category()` using SQLAlchemy COUNT with `is_deleted.is_(False)` filter

### Interface Layer
- `src/community/interface/api/post_controller.py` — Added `POST /{post_id}/pin` and `DELETE /{post_id}/pin` endpoints (204), added `sort` and `cursor` query params to `get_feed()` with validation, added `RateLimitExceededError` → 429 handling
- `src/community/interface/api/category_controller.py` — Rewrote with full CRUD: `POST /categories` (201), `PATCH /categories/{id}` (200), `DELETE /categories/{id}` (204), all admin-only
- `src/community/interface/api/dependencies.py` — Added 7 factory functions: `get_rate_limiter()`, `get_pin_post_handler()`, `get_unpin_post_handler()`, `get_create_category_handler()`, `get_update_category_handler()`, `get_delete_category_handler()`
- `src/community/interface/api/schemas.py` — Added `CreateCategoryRequest`, `UpdateCategoryRequest`, `CreateCategoryResponse`

### Frontend
- `frontend/src/features/community/components/SortDropdown.tsx` — New pill-style sort selector (Hot/New/Top) matching CategoryTabs pattern
- `frontend/src/features/community/components/CreatePostModal.tsx` — Added 429 error handling with specific message
- `frontend/src/features/community/api/postApi.ts` — Added `pinPost()`, `unpinPost()`, `createCategory()`, `updateCategory()`, `deleteCategory()`
- `frontend/src/pages/CommunityPage.tsx` — Added `selectedSort` state, renders `SortDropdown`, passes `sort` to `usePosts`
- `frontend/src/App.tsx` — Added `SortDropdown` to `HomePage` component (root route `/`) with same state management
- `frontend/src/features/community/types/community.ts` — Added `sort?: 'hot' | 'new' | 'top'` to `PostsQueryParams`

### Tests
- `tests/features/community/test_feed.py` — Removed skip markers from 20 scenarios, implemented all step definitions including datatable handling for feed sorting tests, relabeled remaining skips to "Phase 4"
- `tests/features/community/conftest.py` — Added autouse `_reset_rate_limiter` fixture to prevent cross-test contamination
- `tests/unit/community/domain/test_post.py` — Added `TestPostPin` (6 tests), `TestPostUnpin` (5 tests)
- `tests/unit/community/application/handlers/test_pin_handlers.py` — New file with 7 tests (PinPostHandler + UnpinPostHandler)
- `tests/unit/community/application/handlers/test_category_handlers.py` — New file with 13 tests covering create/update/delete with all permission/validation cases
- `tests/unit/community/application/handlers/test_create_post_handler.py` — Added `mock_rate_limiter` fixture, added rate limit test (11th post fails)

### Documentation
- `.claude/skills/implement-feature/SKILL.md` — Added Step 8: Manual Testing Guide requirement (mandatory after every phase/slice)

### Fixes
- `alembic/versions/ffcae5cbe8b3_add_modules_and_lessons_tables.py` — Fixed lint: imports, Union → `|` syntax

---

## BDD Scenarios Passing (Phase 3)

### Slice 1: Post Pinning (4 scenarios)
- [x] Admin pins an important post
- [x] Moderator pins a post
- [x] Admin unpins a post
- [x] Regular member cannot pin posts

### Slice 2: Feed Sorting & Pagination (7 scenarios)
- [x] View feed with Hot sorting (default)
- [x] View feed with New sorting
- [x] View feed with Top sorting
- [x] Pinned posts always appear first
- [x] Filter feed by category
- [x] Paginate feed with cursor
- [x] Empty feed shows appropriate message

### Slice 3: Category CRUD (7 scenarios)
- [x] Admin creates a new category
- [x] Admin updates a category
- [x] Admin deletes empty category
- [x] Cannot delete category with posts
- [x] Category name must be unique
- [x] Member cannot create categories
- [x] Moderator cannot create categories

### Slice 4: Rate Limiting (1 scenario)
- [x] Rate limit prevents excessive posting

### Deferred to Phase 4 (12 scenarios skipped)
- [ ] Permissions summary (3 scenarios)
- [ ] Admin moves post to different category (1 scenario)
- [ ] Unauthenticated/non-member feed access (2 scenarios)
- [ ] Post detail view (2 scenarios)
- [ ] Edge cases (4 scenarios: concurrent edits, deleted posts, max pins)

---

## How to Verify

### Start the app (if not running):
```bash
./start.sh
```

### Test manually:

1. **Feed Sorting:**
   - Open http://localhost:5173/
   - Click **Hot / New / Top** pills above the feed → posts should reorder
   - Hot: balances likes, comments, and recency
   - New: most recent first
   - Top: most liked first

2. **Post Pinning (admin only):**
   - Log in as an admin user
   - Pin a post → it jumps to the top with a "Pinned" indicator
   - Unpin it → returns to normal position

3. **Rate Limiting:**
   - Create 10 posts rapidly
   - 11th attempt → "Rate limit exceeded. Try again later."

4. **Category CRUD (admin only):**
   - Admin can create/edit/delete categories
   - Deleting a category with posts → blocked with error
   - Category names must be unique

5. **Pagination:**
   - If >20 posts exist, scroll down → feed loads more
   - Cursor-based, stable across edits

### Run tests:
```bash
./scripts/verify.sh
```
Expected: 613 passed, 44 skipped, 0 failed, 87.31% coverage

---

## Issues & Resolutions

| Issue | Resolution |
|-------|------------|
| SortDropdown not visible on screenshot | Was only added to CommunityPage (/community), not HomePage (/). Fixed by adding to both. |
| Ruff format not run initially | Added to MEMORY.md: always run `./scripts/verify.sh`, not individual commands. |
| pytest-bdd datatable format unclear | Resolved: datatables arrive as `list[list[str]]` from `DataTable.raw()`, first row is headers. |
| Nested if SIM102 lint error | Combined nested conditionals with `and` in `update_category_handler.py`. |

---

## Deferred / Out of Scope

- **Redis-based rate limiting:** In-memory sufficient for MVP, can migrate later if needed
- **Post detail page:** Phase 4
- **Permissions summary scenarios:** Phase 4 comprehensive testing
- **Optimistic locking for concurrent edits:** Phase 4 edge cases
- **Max pinned posts limit (5):** Phase 4 validation

---

## Next Steps

- [ ] User approval before starting Phase 4
- [ ] Phase 4: Permissions summary, edge cases, post detail view (12 scenarios)
- [ ] Migrate rate limiter to Redis if traffic increases
- [ ] E2E tests for feed sorting and pagination (optional)
