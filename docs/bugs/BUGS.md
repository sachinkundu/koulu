# Bug & Missing Feature Tracker

Discovered during manual testing. Use `/bug-report <description>` to add entries.

To fix items: ask Claude to "fix BUG-NNN" or "go through the bug list".

---

## Open

(none)

## Resolved

### BUG-001: Comments not visible in UI until page refresh
- **Reported:** 2026-02-12
- **Resolved:** 2026-02-12
- **Type:** bug
- **Area:** community, identity
- **Root cause:** Backend uses yield-based FastAPI session dependency — `session.commit()` runs AFTER the HTTP response is sent. React Query's `onSuccess` immediately refetched comments, but the transaction hadn't committed yet, so the refetch returned stale data which was then cached for 2 minutes.
- **Fix (v2):** Added explicit `await session.commit()` before response in ALL mutating backend route handlers across post, comment, category, member, auth, and user controllers. This ensures data is persisted before the HTTP response reaches the client. Reverted the frontend optimistic cache workaround back to simple `invalidateQueries` — no longer needed with proper backend commit timing.
- **Files changed:** `post_controller.py`, `comment_controller.py`, `category_controller.py`, `member_controller.py`, `auth_controller.py`, `user_controller.py`, `useAddComment.ts`, `CommentCard.tsx`
