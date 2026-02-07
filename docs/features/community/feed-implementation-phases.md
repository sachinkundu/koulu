# Community Feed - Implementation Phases

## Complexity Analysis

| Metric | Count | Complexity |
|--------|-------|------------|
| BDD Scenarios | 70 | High |
| New Files | ~25 files | High |
| Modified Files | ~5 files | Medium |
| API Endpoints | 15+ endpoints | High |
| Dependencies | 2 contexts (Identity, Community) | High |
| Domain Entities | 5 aggregates | High |

**Overall Complexity:** **High**

**Decision:** 4-phase vertical slice implementation

**Strategy:** Vertical slicing (all layers per phase) to ensure:
- ✅ CI tests pass after each phase
- ✅ Each phase is deployable
- ✅ Incremental user-facing value
- ✅ Low risk of integration issues

---

## Phase 1: Foundation - Posts Create & View (Happy Path)

**Duration:** 6-8 hours

### Goal
Create the foundation with Posts aggregate and basic CRUD. Users can create posts with categories and view individual posts. No comments, no reactions, no feed yet - just the core post entity working end-to-end.

### Scope

**Backend - Domain Layer:**
- `src/community/domain/value_objects/post_id.py` - PostId
- `src/community/domain/value_objects/category_id.py` - CategoryId
- `src/community/domain/value_objects/community_id.py` - CommunityId
- `src/community/domain/value_objects/post_title.py` - PostTitle (validation, sanitization)
- `src/community/domain/value_objects/post_content.py` - PostContent (validation, sanitization)
- `src/community/domain/value_objects/member_role.py` - MemberRole enum
- `src/community/domain/entities/post.py` - Post aggregate root
- `src/community/domain/entities/category.py` - Category entity
- `src/community/domain/entities/community_member.py` - CommunityMember entity
- `src/community/domain/events.py` - PostCreated, PostEdited, PostDeleted events
- `src/community/domain/exceptions.py` - Domain exceptions
- `src/community/domain/repositories/post_repository.py` - IPostRepository interface
- `src/community/domain/repositories/category_repository.py` - ICategoryRepository interface
- `src/community/domain/repositories/member_repository.py` - IMemberRepository interface

**Backend - Application Layer:**
- `src/community/application/commands.py` - CreatePostCommand, UpdatePostCommand, DeletePostCommand
- `src/community/application/queries.py` - GetPostQuery
- `src/community/application/handlers/create_post_handler.py`
- `src/community/application/handlers/update_post_handler.py`
- `src/community/application/handlers/delete_post_handler.py`
- `src/community/application/handlers/get_post_handler.py`

**Backend - Infrastructure Layer:**
- `src/community/infrastructure/persistence/models.py` - SQLAlchemy models (communities, categories, community_members, posts)
- `src/community/infrastructure/persistence/post_repository.py` - SQLAlchemyPostRepository
- `src/community/infrastructure/persistence/category_repository.py` - SQLAlchemyCategoryRepository
- `src/community/infrastructure/persistence/member_repository.py` - SQLAlchemyMemberRepository
- `migrations/versions/XXXX_create_communities_table.py`
- `migrations/versions/XXXX_create_categories_table.py`
- `migrations/versions/XXXX_create_community_members_table.py`
- `migrations/versions/XXXX_create_posts_table.py`
- `migrations/versions/XXXX_seed_default_categories.py`

**Backend - Interface Layer:**
- `src/community/interface/api/schemas.py` - Pydantic schemas
- `src/community/interface/api/dependencies.py` - FastAPI dependencies
- `src/community/interface/api/controllers/post_controller.py` - POST /posts, GET /posts/:id, PATCH /posts/:id, DELETE /posts/:id
- `src/community/__init__.py` - Module initialization
- Update `src/main.py` to include community router

**Frontend:**
- `frontend/src/features/community/api/postApi.ts` - API client
- `frontend/src/features/community/types/community.ts` - TypeScript types
- `frontend/src/features/community/hooks/useCreatePost.ts`
- `frontend/src/features/community/hooks/usePost.ts`
- `frontend/src/features/community/components/CreatePostModal.tsx` - Basic form
- `frontend/src/features/community/components/PostDetail.tsx` - View single post
- `frontend/src/pages/CommunityPage.tsx` - Container page

**Dependencies:**
- Add `bleach = "^6.1.0"` to `pyproject.toml`

**Tests:**
- `tests/features/community/conftest.py` - BDD fixtures
- `tests/features/community/test_feed.py` - BDD step definitions
- `tests/unit/community/domain/test_post.py` - Unit tests for Post entity
- `tests/unit/community/domain/test_value_objects.py` - Unit tests for PostTitle, PostContent

### BDD Scenarios Enabled (12 scenarios)

**Post Creation (6 scenarios):**
- ✅ Line 20: Member creates a post with title and content
- ✅ Line 34: Member creates a post with an image
- ✅ Line 46: Post creation fails without title
- ✅ Line 54: Post creation fails with title too long
- ✅ Line 62: Post creation fails with content too long
- ✅ Line 69: Post creation fails with invalid category
- ✅ Line 79: Post creation fails with invalid image URL
- ✅ Line 90: Unauthenticated user cannot create post

**Post Editing (2 scenarios):**
- ✅ Line 107: Author edits their own post
- ✅ Line 120: User cannot edit another user's post

**Post Deletion (2 scenarios):**
- ✅ Line 133: Author deletes their own post
- ✅ Line 162: Regular member cannot delete another member's post

### BDD Scenarios Skipped (58 scenarios)

**Phase 2 (Comments, Reactions & Locking - 25 scenarios):**
- Line 171: Deleting post cascades to comments → Phase 2 (comments exist)
- Line 226: Admin locks comments on a post → Phase 2 (locking)
- Line 237: Admin unlocks a locked post → Phase 2 (locking)
- Line 246: Cannot comment on locked post → Phase 2 (comments + locking)
- Line 254: Regular member cannot lock posts → Phase 2 (locking)
- Line 266: Member adds a comment to a post → Phase 2 (comments)
- Line 276: Member replies to a comment → Phase 2 (comments)
- Line 288: Cannot reply to a reply → Phase 2 (comments)
- Line 296: Comment content too long → Phase 2 (comments)
- Line 304: Comment content required → Phase 2 (comments)
- Line 311: Rate limit prevents comment spam → Phase 2 (comments + rate limiting)
- Line 325: Author edits their own comment → Phase 2 (comments)
- Line 335: Author deletes comment with no replies → Phase 2 (comments)
- Line 345: Author deletes comment that has replies → Phase 2 (comments)
- Line 356: Admin deletes any comment → Phase 2 (comments)
- Line 364: Member cannot edit another member's comment → Phase 2 (comments)
- Line 374: Member cannot delete another member's comment → Phase 2 (comments)
- Line 387: Member likes a post → Phase 2 (reactions)
- Line 398: Member unlikes a post → Phase 2 (reactions)
- Line 410: Member likes a comment → Phase 2 (reactions)
- Line 420: Member unlikes a comment → Phase 2 (reactions)
- Line 431: Liking a post twice is idempotent → Phase 2 (reactions)
- Line 441: Member can like their own post → Phase 2 (reactions)
- Line 450: Rate limit prevents excessive liking → Phase 2 (reactions + rate limiting)
- Line 458: Unauthenticated user cannot like posts → Phase 2 (reactions)

**Phase 3 (Pinning, Feed & Categories - 20 scenarios):**
- Line 95: Rate limit prevents excessive posting → Phase 3 (rate limiting)
- Line 143: Admin deletes another user's post → Phase 3 (admin permissions)
- Line 153: Moderator deletes a post → Phase 3 (moderator permissions)
- Line 187: Admin pins an important post → Phase 3 (pinning)
- Line 198: Moderator pins a post → Phase 3 (pinning)
- Line 206: Admin unpins a post → Phase 3 (pinning)
- Line 214: Regular member cannot pin posts → Phase 3 (pinning)
- Line 468: Admin creates a new category → Phase 3 (category CRUD)
- Line 481: Admin updates a category → Phase 3 (category CRUD)
- Line 493: Admin deletes empty category → Phase 3 (category CRUD)
- Line 503: Cannot delete category with posts → Phase 3 (category CRUD)
- Line 512: Category name must be unique → Phase 3 (category CRUD)
- Line 520: Member cannot create categories → Phase 3 (category CRUD)
- Line 527: Moderator cannot create categories → Phase 3 (category CRUD)
- Line 534: Admin moves post to different category → Phase 3 (category CRUD)
- Line 546: View feed with Hot sorting → Phase 3 (feed)
- Line 558: View feed with New sorting → Phase 3 (feed)
- Line 570: View feed with Top sorting → Phase 3 (feed)
- Line 582: Pinned posts always appear first → Phase 3 (feed + pinning)
- Line 596: Filter feed by category → Phase 3 (feed)
- Line 608: Paginate feed with cursor → Phase 3 (feed)
- Line 619: Empty feed shows appropriate message → Phase 3 (feed)

**Phase 4 (Edge Cases & Auth - 5 scenarios):**
- Line 628: Unauthenticated user cannot view feed → Phase 4 (feed)
- Line 633: Non-member cannot view community feed → Phase 4 (feed)
- Line 644: View post with comments → Phase 4 (comments)
- Line 657: View post with threaded comments → Phase 4 (comments)
- Line 670: Admin role has full permissions → Phase 4 (permissions summary)
- Line 681: Moderator has moderation permissions → Phase 4 (permissions summary)
- Line 692: Member has basic permissions → Phase 4 (permissions summary)
- Line 708: Concurrent edits - last write wins → Phase 4 (edge case)
- Line 717: Viewing deleted post returns 404 → Phase 4 (edge case)
- Line 726: Deleted user's content shows placeholder → Phase 4 (edge case)
- Line 734: Maximum 5 pinned posts displayed → Phase 4 (feed + pinning)

### Dependencies
- None (first phase)

### Estimated Time
6-8 hours

### Definition of Done
- [ ] All Phase 1 files created
- [ ] 12 BDD scenarios passing (post CRUD)
- [ ] 58 scenarios skipped with phase markers
- [ ] Unit tests passing (Post entity, value objects)
- [ ] Linting passes (ruff)
- [ ] Type checking passes (mypy)
- [ ] Coverage ≥ 80%
- [ ] CI green (all enabled tests pass)
- [ ] Database migrations run successfully
- [ ] Verification commands pass

### Verification Commands
```bash
# Database setup
docker-compose up -d
alembic upgrade head

# Backend - BDD tests
pytest tests/features/community/test_feed.py -v
# Expected: 12 passed, 58 skipped

# Verify all skips have phase markers
grep -r "@pytest.mark.skip" tests/features/community/ | grep "Phase [0-9]"

# Unit tests
pytest tests/unit/community/ -v

# Backend verification
./scripts/verify.sh

# Frontend (if implemented)
cd frontend && npm run typecheck && npm run test
```

---

## Phase 2: Comments, Reactions & Post Locking

**Duration:** 6-8 hours

### Goal
Add Comments and Reactions (likes) to posts, plus post locking. Enable threaded discussions with proper depth limits, soft deletion, and rate limiting.

### Scope

**Backend - Domain Layer:**
- `src/community/domain/value_objects/comment_id.py` - CommentId
- `src/community/domain/value_objects/reaction_id.py` - ReactionId
- `src/community/domain/value_objects/comment_content.py` - CommentContent (validation, sanitization)
- `src/community/domain/entities/comment.py` - Comment aggregate root
- `src/community/domain/entities/reaction.py` - Reaction entity
- Update `src/community/domain/entities/post.py` - Add lock(), unlock() methods
- Update `src/community/domain/events.py` - CommentAdded, CommentEdited, CommentDeleted, PostLiked, PostUnliked, CommentLiked, CommentUnliked
- Update `src/community/domain/exceptions.py` - Add CommentNotFoundError
- `src/community/domain/repositories/comment_repository.py` - ICommentRepository
- `src/community/domain/repositories/reaction_repository.py` - IReactionRepository

**Backend - Application Layer:**
- `src/community/application/commands.py` - LockPostCommand, UnlockPostCommand, AddCommentCommand, EditCommentCommand, DeleteCommentCommand, LikePostCommand, UnlikePostCommand, LikeCommentCommand, UnlikeCommentCommand
- `src/community/application/queries.py` - GetPostCommentsQuery
- `src/community/application/handlers/lock_post_handler.py`
- `src/community/application/handlers/unlock_post_handler.py`
- `src/community/application/handlers/add_comment_handler.py`
- `src/community/application/handlers/edit_comment_handler.py`
- `src/community/application/handlers/delete_comment_handler.py`
- `src/community/application/handlers/like_post_handler.py`
- `src/community/application/handlers/unlike_post_handler.py`
- `src/community/application/handlers/like_comment_handler.py`
- `src/community/application/handlers/unlike_comment_handler.py`
- `src/community/application/handlers/get_post_comments_handler.py`
- Update `src/community/application/handlers/delete_post_handler.py` - Add cascade delete

**Backend - Infrastructure Layer:**
- Update `src/community/infrastructure/persistence/models.py` - Add CommentModel, ReactionModel
- `src/community/infrastructure/persistence/comment_repository.py` - SqlAlchemyCommentRepository
- `src/community/infrastructure/persistence/reaction_repository.py` - SqlAlchemyReactionRepository
- `migrations/versions/20260208_1000_create_comments.py`
- `migrations/versions/20260208_1010_create_reactions.py`

**Backend - Interface Layer:**
- `src/community/interface/api/schemas.py` - Add AddCommentRequest, EditCommentRequest, CommentResponse, CreateCommentResponse, LikeResponse; update PostResponse
- `src/community/interface/api/dependencies.py` - Add repository and handler factories
- Update `src/community/interface/api/post_controller.py` - Add POST /posts/:id/lock, DELETE /posts/:id/lock, POST /posts/:id/like, DELETE /posts/:id/like
- `src/community/interface/api/comment_controller.py` - Full CRUD for comments and comment likes

**Frontend:**
- `frontend/src/features/community/api/commentApi.ts`
- `frontend/src/features/community/api/reactionApi.ts`
- `frontend/src/features/community/hooks/useComments.ts`
- `frontend/src/features/community/hooks/useLikePost.ts`
- `frontend/src/features/community/components/CommentList.tsx`
- `frontend/src/features/community/components/CommentForm.tsx`
- `frontend/src/features/community/components/LikeButton.tsx`
- Update `frontend/src/features/community/components/PostDetail.tsx` - Add comments, like button

**Tests:**
- `tests/unit/community/domain/test_comment.py` - ~15 tests
- `tests/unit/community/domain/test_reaction.py` - ~4 tests
- `tests/unit/community/domain/test_comment_content.py` - ~10 tests
- Update `tests/unit/community/domain/test_post.py` - Add lock/unlock tests (~7 tests)

### BDD Scenarios Enabled (25 new = 45 total)

**Post Locking (4 scenarios):**
- ✅ Line 226: Admin locks comments on a post
- ✅ Line 237: Admin unlocks a locked post
- ✅ Line 246: Cannot comment on locked post
- ✅ Line 254: Regular member cannot lock posts

**Comments (12 scenarios):**
- ✅ Line 266: Member adds a comment to a post
- ✅ Line 276: Member replies to a comment
- ✅ Line 288: Cannot reply to a reply (max depth)
- ✅ Line 296: Comment content too long
- ✅ Line 304: Comment content required
- ✅ Line 311: Rate limit prevents comment spam
- ✅ Line 325: Author edits their own comment
- ✅ Line 335: Author deletes comment with no replies
- ✅ Line 345: Author deletes comment that has replies
- ✅ Line 356: Admin deletes any comment
- ✅ Line 364: Member cannot edit another member's comment
- ✅ Line 374: Member cannot delete another member's comment

**Reactions (8 scenarios):**
- ✅ Line 387: Member likes a post
- ✅ Line 398: Member unlikes a post
- ✅ Line 410: Member likes a comment
- ✅ Line 420: Member unlikes a comment
- ✅ Line 431: Liking a post twice is idempotent
- ✅ Line 441: Member can like their own post
- ✅ Line 450: Rate limit prevents excessive liking
- ✅ Line 458: Unauthenticated user cannot like posts

**Cascading (1 scenario):**
- ✅ Line 171: Deleting post cascades to comments and reactions

### BDD Scenarios Skipped (25 remaining)

**Phase 3 (Pinning, Feed & Categories - 25 scenarios):**
- All pinning, feed sorting, pagination, and category management scenarios

### Dependencies
- Phase 1 complete

### Estimated Time
6-8 hours

### Definition of Done
- [ ] All Phase 2 files created
- [ ] 45 BDD scenarios passing (20 from Phase 1 + 25 new)
- [ ] 25 scenarios skipped with Phase 3+ markers
- [ ] Unit tests passing (~36 new tests)
- [ ] Comment threading working (max depth 1)
- [ ] Soft deletion working (comments with replies)
- [ ] Post locking working
- [ ] Reactions working (like/unlike idempotent)
- [ ] Rate limiting working (comments, likes)
- [ ] Cascade delete working (post → comments → reactions)
- [ ] Linting passes
- [ ] Type checking passes
- [ ] Coverage ≥ 80%
- [ ] CI green (0 failed, 0 warnings)

### Verification Commands
```bash
# Run migrations
alembic upgrade head

# Backend - BDD tests
pytest tests/features/community/test_feed.py -v
# Expected: 45 passed, 25 skipped

# Unit tests
pytest tests/unit/community/ -v

# Backend verification
./scripts/verify.sh

# Verify skip markers reference correct phases
grep -r "@pytest.mark.skip" tests/features/community/ | grep "Phase [0-9]"
```

---

## Phase 3: Pinning, Feed & Categories

**Duration:** 6-8 hours

### Goal
Add post pinning, implement the feed with Hot/New/Top sorting, cursor pagination, category filtering, and full category CRUD.

### Scope

**Backend - Domain Layer:**
- `src/community/domain/specifications/can_pin_post_spec.py` - Authorization spec
- Update `src/community/domain/entities/post.py` - Add pin(), unpin() methods
- Update `src/community/domain/events.py` - Add PostPinned, PostUnpinned
- `src/community/domain/services/feed_sort_strategy.py` - IFeedSortStrategy interface
- `src/community/domain/services/hot_sort_strategy.py`
- `src/community/domain/services/new_sort_strategy.py`
- `src/community/domain/services/top_sort_strategy.py`
- `src/community/domain/value_objects/category_slug.py`
- Update `src/community/domain/entities/category.py` - Add validation, slug generation

**Backend - Application Layer:**
- `src/community/application/commands.py` - PinPostCommand, UnpinPostCommand, CreateCategoryCommand, UpdateCategoryCommand, DeleteCategoryCommand
- `src/community/application/queries.py` - GetFeedQuery
- `src/community/application/handlers/pin_post_handler.py`
- `src/community/application/handlers/unpin_post_handler.py`
- `src/community/application/handlers/get_feed_handler.py`
- `src/community/application/handlers/create_category_handler.py`
- `src/community/application/handlers/update_category_handler.py`
- `src/community/application/handlers/delete_category_handler.py`

**Backend - Infrastructure Layer:**
- Update `src/community/infrastructure/persistence/models.py` - Add is_pinned, pinned_at columns
- Update `src/community/infrastructure/persistence/post_repository.py` - Add feed queries with sorting
- `src/community/infrastructure/services/cursor_pagination.py` - Cursor encoding/decoding
- `src/community/infrastructure/services/rate_limiter.py` - Redis-based rate limiter (for post rate limit)

**Backend - Interface Layer:**
- Update `src/community/interface/api/controllers/post_controller.py` - Add POST /posts/:id/pin, DELETE /posts/:id/pin, GET /posts/feed
- `src/community/interface/api/controllers/category_controller.py` - Full CRUD
- `src/community/interface/api/middleware/rate_limit_middleware.py` - Rate limit decorator

**Frontend:**
- `frontend/src/features/community/api/categoryApi.ts`
- `frontend/src/features/community/hooks/useFeed.ts`
- `frontend/src/features/community/hooks/useCategories.ts`
- `frontend/src/features/community/components/FeedView.tsx` - Main feed component
- `frontend/src/features/community/components/PostCard.tsx` - Feed item
- `frontend/src/features/community/components/CategorySidebar.tsx` - Category filter
- `frontend/src/features/community/components/SortDropdown.tsx` - Hot/New/Top
- Update `frontend/src/pages/CommunityPage.tsx` - Full layout with sidebar

**Tests:**
- Update `tests/unit/community/domain/test_post.py` - Test pin/unpin methods
- `tests/unit/community/domain/test_specifications.py` - Test authorization specs
- `tests/unit/community/domain/test_feed_sort_strategy.py`
- `tests/unit/community/infrastructure/test_cursor_pagination.py`
- `tests/unit/community/infrastructure/test_rate_limiter.py`

### BDD Scenarios Enabled (20 new = 65 total)

**Pinning (4 scenarios):**
- ✅ Line 187: Admin pins an important post
- ✅ Line 198: Moderator pins a post
- ✅ Line 206: Admin unpins a post
- ✅ Line 214: Regular member cannot pin posts

**Categories (8 scenarios):**
- ✅ Line 468: Admin creates a new category
- ✅ Line 481: Admin updates a category
- ✅ Line 493: Admin deletes empty category
- ✅ Line 503: Cannot delete category with posts
- ✅ Line 512: Category name must be unique
- ✅ Line 520: Member cannot create categories
- ✅ Line 527: Moderator cannot create categories
- ✅ Line 534: Admin moves post to different category

**Feed (7 scenarios):**
- ✅ Line 546: View feed with Hot sorting
- ✅ Line 558: View feed with New sorting
- ✅ Line 570: View feed with Top sorting
- ✅ Line 582: Pinned posts always appear first
- ✅ Line 596: Filter feed by category
- ✅ Line 608: Paginate feed with cursor
- ✅ Line 619: Empty feed shows appropriate message

**Rate Limiting (1 scenario):**
- ✅ Line 95: Rate limit prevents excessive posting

### BDD Scenarios Skipped (5 remaining)

**Phase 4 (Edge Cases & Permissions Summary - 5 scenarios):**
- Line 628: Unauthenticated user cannot view feed
- Line 633: Non-member cannot view community feed
- Line 644: View post with comments (already passing in Phase 2, may need feed integration)
- Line 657: View post with threaded comments (already passing in Phase 2, may need feed integration)
- Line 670: Admin role has full permissions
- Line 681: Moderator has moderation permissions
- Line 692: Member has basic permissions
- Line 708: Concurrent edits - last write wins
- Line 717: Viewing deleted post returns 404
- Line 726: Deleted user's content shows placeholder
- Line 734: Maximum 5 pinned posts displayed

### Dependencies
- Phase 2 complete

### Estimated Time
6-8 hours

### Definition of Done
- [ ] All Phase 3 files created
- [ ] 65 BDD scenarios passing (45 from Phase 2 + 20 new)
- [ ] 5 scenarios skipped with Phase 4 markers
- [ ] Unit tests passing
- [ ] Post pinning working
- [ ] Hot/New/Top sorting working correctly
- [ ] Cursor pagination working
- [ ] Category CRUD working
- [ ] Rate limiting working (post creation)
- [ ] Linting passes
- [ ] Type checking passes
- [ ] Coverage ≥ 80%
- [ ] CI green

### Verification Commands
```bash
# Backend - BDD tests
pytest tests/features/community/test_feed.py -v
# Expected: 65 passed, 5 skipped

# Unit tests
pytest tests/unit/community/ -v

# Backend verification
./scripts/verify.sh

# Verify skip markers
grep -r "@pytest.mark.skip" tests/features/community/ | grep "Phase [0-9]"
```

---

## Phase 4: Edge Cases & Permissions Summary

**Duration:** 2-3 hours

### Goal
Complete remaining edge cases, permission summary scenarios, and authentication checks. Finalize the feature.

### Scope

**Backend - Application Layer:**
- Minor adjustments to existing handlers for edge cases
- Ensure all authorization checks complete

**Frontend:**
- `frontend/src/features/community/api/postApi.ts`
- `frontend/src/features/community/api/commentApi.ts`
- `frontend/src/features/community/api/reactionApi.ts`
- `frontend/src/features/community/hooks/useFeed.ts`
- `frontend/src/features/community/hooks/useCategories.ts`
- `frontend/src/features/community/components/FeedView.tsx` - Main feed component
- `frontend/src/features/community/components/PostCard.tsx` - Feed item
- `frontend/src/features/community/components/CategorySidebar.tsx` - Category filter
- `frontend/src/features/community/components/SortDropdown.tsx` - Hot/New/Top
- `frontend/src/features/community/components/CommentList.tsx`
- `frontend/src/features/community/components/CommentForm.tsx`
- `frontend/src/features/community/components/LikeButton.tsx`
- Update `frontend/src/pages/CommunityPage.tsx` - Full layout with sidebar

**Tests:**
- Integration tests for edge cases

### BDD Scenarios Enabled (5 new = 70 total - ALL SCENARIOS)

**Authentication & Authorization (2 scenarios):**
- ✅ Line 628: Unauthenticated user cannot view feed
- ✅ Line 633: Non-member cannot view community feed

**View Scenarios (2 scenarios):**
- ✅ Line 644: View post with comments
- ✅ Line 657: View post with threaded comments

**Permissions Summary (3 scenarios):**
- ✅ Line 670: Admin role has full permissions
- ✅ Line 681: Moderator has moderation permissions
- ✅ Line 692: Member has basic permissions

**Edge Cases (3 scenarios):**
- ✅ Line 708: Concurrent edits - last write wins
- ✅ Line 717: Viewing deleted post returns 404
- ✅ Line 726: Deleted user's content shows placeholder

**Pinning Limit (1 scenario):**
- ✅ Line 734: Maximum 5 pinned posts displayed

### BDD Scenarios Skipped
- None - all 70 scenarios enabled ✅

### Dependencies
- Phase 3 complete

### Estimated Time
2-3 hours

### Definition of Done
- [ ] All Phase 4 adjustments complete
- [ ] **ALL 70 BDD scenarios passing** ✅
- [ ] 0 scenarios skipped ✅
- [ ] All edge cases handled
- [ ] Frontend complete
- [ ] Feed displays correctly
- [ ] Linting passes
- [ ] Type checking passes
- [ ] Coverage ≥ 80%
- [ ] CI green
- [ ] **FEATURE COMPLETE** ✅

### Verification Commands
```bash
# Backend - BDD tests
pytest tests/features/community/test_feed.py -v
# Expected: 70 passed, 0 skipped ✅

# Unit tests
pytest tests/unit/community/ -v

# Backend verification
./scripts/verify.sh

# Frontend
cd frontend && npm run typecheck && npm run test

# E2E tests (optional but recommended)
# See /e2e-test command for adding E2E tests
```

---

## Dependency Graph

```
Phase 1 (Foundation - Posts CRUD)
    ↓
Phase 2 (Comments, Reactions & Post Locking)
    ↓
Phase 3 (Pinning, Feed & Categories)
    ↓
Phase 4 (Edge Cases & Permissions Summary)
```

**Linear dependency:** Each phase builds on the previous one.

---

## Implementation Notes

### Patterns to Follow
- **Value Objects:** Reuse Identity context patterns (EmailAddress, DisplayName) for validation
- **Repositories:** Match SQLAlchemyUserRepository structure
- **Authorization:** Use specification pattern like CanRegisterSpec
- **Events:** Follow UserRegistered event structure
- **API Controllers:** Match auth controller patterns (FastAPI, Pydantic schemas)

### Common Pitfalls
- Don't skip value object validation (PostTitle, PostContent must sanitize)
- Don't bypass aggregate boundaries (add comments through Post.add_comment(), not directly)
- Don't forget to publish domain events after persistence
- Don't use offset pagination (use cursor pagination for stable results)
- Don't allow HTML in MVP (use bleach to strip all tags)

### Testing Strategy
- **Unit tests first:** Test Post.create(), PostTitle validation before integration
- **BDD tests after:** Implement step definitions after handlers work
- **Use domain factories:** Create test data via User.register(), Post.create() (not ORM models)
- **Skip future scenarios:** Always include phase number and condition in skip reason

### Security Checklist
- [ ] All user input sanitized (bleach for HTML)
- [ ] Authorization checks before every write operation
- [ ] Rate limiting on posts, comments, reactions
- [ ] JWT token validation on all endpoints
- [ ] No SQL injection (use SQLAlchemy ORM, parameterized queries)
- [ ] Image URLs validated (HTTPS only)

---

## Success Criteria

**A good phase is:**
- ✅ Independently testable (N passed, M skipped with phase markers)
- ✅ Deployable (CI green after phase)
- ✅ Provides incremental value (users can do X after Phase N)
- ✅ Reasonable size (4-8 hours)
- ✅ Clear dependencies (Phase N depends only on Phase N-1)

**Phase completion checklist:**
- [ ] All files for phase created
- [ ] BDD scenarios for phase passing
- [ ] Future scenarios skipped with phase markers
- [ ] Unit tests passing
- [ ] Verification scripts pass
- [ ] CI green
- [ ] Coverage ≥ 80%
- [ ] User can perform new actions (create post, comment, view feed)
