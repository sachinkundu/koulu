# Community Feed Phase 2: Comments, Reactions & Post Locking - Implementation Summary

**Date:** 2026-02-07
**Status:** Complete
**PRD:** `docs/features/community/feed-prd.md`
**BDD Spec:** `tests/features/community/feed.feature`
**Implementation Phases:** `docs/features/community/feed-implementation-phases.md`

---

## What Was Built

Phase 2 adds social interactions to the community feed. Members can comment on posts (with single-level threading), like/unlike posts and comments, and admins/moderators can lock posts to prevent further comments. Comments support soft deletion (preserving thread structure when replies exist) and hard deletion (when no replies). Rate limiting prevents spam on comments and likes.

---

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| **Max reply depth of 1** | Keeps threading simple — comments can have replies, but replies cannot be nested further. Matches Skool.com's flat threading model |
| **Soft delete for comments with replies** | When a comment has child replies, content is replaced with "[deleted]" to preserve thread context. Comments without replies are hard-deleted |
| **Idempotent likes** | Liking a post/comment twice returns success without creating duplicates. Uses unique constraint on (user_id, target_type, target_id) |
| **Generic reaction entity** | Single `reactions` table handles both post and comment likes via `target_type` discriminator. Extensible for future reaction types |
| **Rate limiting via Redis** | Comment spam prevention (configurable per-minute limits) and like spam prevention. Uses Redis TTL keys for sliding window |
| **Lock prevents new comments only** | Locking a post blocks new comment creation but does not hide existing comments. Existing comments can still be edited/deleted |

---

## Files Created

### Domain Layer (5 new files)
- `src/community/domain/entities/comment.py` — Comment aggregate with `create()`, `edit()`, `delete()` methods. Threading validation (max depth 1), soft delete logic
- `src/community/domain/entities/reaction.py` — Immutable Reaction entity with `create()` factory. Supports post and comment target types
- `src/community/domain/value_objects/comment_content.py` — Required, max 2000 chars, HTML sanitized via bleach
- `src/community/domain/value_objects/comment_id.py` — UUID wrapper
- `src/community/domain/value_objects/reaction_id.py` — UUID wrapper

### Domain Layer (modified)
- `src/community/domain/entities/post.py` — Added `lock()` and `unlock()` methods with `is_locked` state management
- `src/community/domain/events.py` — Added 8 events: CommentAdded, CommentEdited, CommentDeleted, PostLiked, PostUnliked, CommentLiked, CommentUnliked, PostLocked, PostUnlocked
- `src/community/domain/exceptions.py` — Added 7 exceptions: CommentContentRequiredError, CommentContentTooLongError, PostLockedError, MaxReplyDepthExceededError, CannotEditCommentError, CannotDeleteCommentError, CommentNotFoundError
- `src/community/domain/repositories/comment_repository.py` — ICommentRepository interface
- `src/community/domain/repositories/reaction_repository.py` — IReactionRepository interface

### Application Layer (10 new handlers)
- `src/community/application/handlers/add_comment_handler.py` — Add comment/reply with threading validation, lock check
- `src/community/application/handlers/edit_comment_handler.py` — Edit with author/admin permission check
- `src/community/application/handlers/delete_comment_handler.py` — Smart delete: hard if no replies, soft if has replies
- `src/community/application/handlers/get_post_comments_handler.py` — Retrieve comments with hierarchy
- `src/community/application/handlers/like_post_handler.py` — Idempotent like creation
- `src/community/application/handlers/unlike_post_handler.py` — Remove like
- `src/community/application/handlers/like_comment_handler.py` — Like comment
- `src/community/application/handlers/unlike_comment_handler.py` — Unlike comment
- `src/community/application/handlers/lock_post_handler.py` — Lock post (admin/moderator only)
- `src/community/application/handlers/unlock_post_handler.py` — Unlock post

### Infrastructure Layer (2 new files)
- `src/community/infrastructure/persistence/comment_repository.py` — SqlAlchemyCommentRepository with hierarchy loading
- `src/community/infrastructure/persistence/reaction_repository.py` — SqlAlchemyReactionRepository with unique constraint handling

### Interface Layer (1 new file, 2 modified)
- `src/community/interface/api/comment_controller.py` — (new) Full CRUD for comments + comment likes
- `src/community/interface/api/post_controller.py` — (modified) Added lock/unlock and like/unlike endpoints
- `src/community/interface/api/schemas.py` — (modified) Added AddCommentRequest, EditCommentRequest, CommentResponse, LikeResponse

### Tests (5 new files)
- `tests/unit/community/domain/test_comment.py` — Comment entity unit tests (threading, deletion, permissions)
- `tests/unit/community/domain/test_comment_content.py` — CommentContent value object validation
- `tests/unit/community/domain/test_reaction.py` — Reaction entity tests
- `tests/unit/community/application/handlers/test_comment_handlers.py` — Comment handler unit tests with mocked repos
- `tests/unit/community/application/handlers/test_reaction_handlers.py` — Reaction handler unit tests

---

## BDD Scenarios Passing

### Phase 1 (15 scenarios — carried forward)
All Phase 1 scenarios continue to pass.

### Phase 2 (24 new scenarios — all passing)

**Comments (12 scenarios):**
- [x] Member adds a comment to a post
- [x] Member replies to a comment
- [x] Cannot reply to a reply (max depth exceeded)
- [x] Comment content too long (2001 chars)
- [x] Comment content required
- [x] Rate limit prevents comment spam
- [x] Author edits their own comment
- [x] Author deletes comment with no replies (hard delete)
- [x] Author deletes comment that has replies (soft delete — "[deleted]")
- [x] Admin deletes any comment
- [x] Member cannot edit another member's comment
- [x] Member cannot delete another member's comment

**Reactions (8 scenarios):**
- [x] Member likes a post
- [x] Member unlikes a post
- [x] Member likes a comment
- [x] Member unlikes a comment
- [x] Liking a post twice is idempotent
- [x] Member can like their own post
- [x] Rate limit prevents excessive liking
- [x] Unauthenticated user cannot like posts

**Post Locking (4 scenarios):**
- [x] Admin locks comments on a post
- [x] Admin unlocks a locked post
- [x] Cannot comment on locked post
- [x] Regular member cannot lock posts

**Total: 39 passing, 31 skipped (Phase 3-4)**

---

## API Endpoints (New in Phase 2)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/community/posts/{id}/comments` | Member | Add comment/reply |
| PATCH | `/api/v1/community/comments/{id}` | Author/Admin | Edit comment |
| DELETE | `/api/v1/community/comments/{id}` | Author/Admin | Delete comment |
| POST | `/api/v1/community/posts/{id}/like` | Member | Like post |
| DELETE | `/api/v1/community/posts/{id}/like` | Member | Unlike post |
| POST | `/api/v1/community/comments/{id}/like` | Member | Like comment |
| DELETE | `/api/v1/community/comments/{id}/like` | Member | Unlike comment |
| POST | `/api/v1/community/posts/{id}/lock` | Mod/Admin | Lock post |
| DELETE | `/api/v1/community/posts/{id}/lock` | Mod/Admin | Unlock post |

---

## Comment Threading Model

```
Post
├── Comment A (depth 0)
│   ├── Reply A1 (depth 1) — allowed
│   └── Reply A2 (depth 1) — allowed
│       └── Reply A2a (depth 2) — REJECTED (MaxReplyDepthExceededError)
└── Comment B (depth 0)
```

**Deletion behavior:**
- Comment with no replies → hard delete (removed from DB)
- Comment with replies → soft delete (content = "[deleted]", is_deleted = true, thread preserved)
- Admin can delete any comment (same hard/soft logic applies)

---

## Domain Events (New in Phase 2)

- `CommentAdded` — Published when a comment is created
- `CommentEdited` — Published when a comment is edited
- `CommentDeleted` — Published when a comment is deleted
- `PostLiked` / `PostUnliked` — Published on post like/unlike
- `CommentLiked` / `CommentUnliked` — Published on comment like/unlike
- `PostLocked` / `PostUnlocked` — Published on post lock/unlock

---

## Permission Model (Updated)

```
MEMBER:     Create/edit/delete own comments, like/unlike posts and comments
MODERATOR:  All member + delete any comment, lock/unlock posts
ADMIN:      All moderator permissions
```

---

## Deferred / Out of Scope

**Phase 3:** Post pinning, feed sorting (Hot/New/Top), cursor pagination, category CRUD, rate limiting on post creation
**Phase 4:** Edge cases (concurrent edits, deleted user content), auth checks, comprehensive permissions summary

---

## Architecture Notes

- Comment is its own aggregate (separate from Post) — loaded independently via CommentRepository
- Reactions use a generic target model (`target_type` + `target_id`) rather than separate post_likes/comment_likes tables
- Rate limiting checks happen in application handlers before domain operations
- Like/unlike counters are denormalized on posts and comments (`like_count` column) for efficient feed queries
- Comment count is denormalized on posts (`comment_count` column)
