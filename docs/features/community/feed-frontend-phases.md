# Community Feed - Frontend Implementation Phases

**Version:** 1.0
**Last Updated:** 2026-02-08
**Status:** Planned
**Bounded Context:** Community
**Document Type:** Frontend Implementation Plan

---

## Current Status

**Backend:** ✅ Phases 1-2 Complete
- Posts CRUD with categories and images
- Comments with threading (1 level deep)
- Reactions (likes on posts and comments)
- Post locking
- 39 BDD scenarios passing, 89% coverage

**Frontend:** ❌ Completely Missing
- Zero `.tsx` files in `frontend/src/features/community/`
- No pages, no routes, no forms
- Users **cannot interact** with the feature at all

**Problem:** Backend-only implementation violates vertical slicing principle. Users have no way to access this feature.

---

## Implementation Strategy

**Approach:** 4-phase frontend implementation aligned with existing backend capabilities

**Total Estimated Time:** 13-17 hours

**Success Criteria:**
- Users can create posts, comment, and like content
- All components mobile-responsive
- Deployability check passes
- E2E test coverage for critical user journeys

---

## Phase 1: Basic Post Viewing & Creation

**Duration:** 4-5 hours

### Goal
Users can view posts in a feed and create new posts with title, content, category, and optional image.

### Components to Build

**Core Components:**
- `frontend/src/features/community/components/CreatePostInput.tsx` - Quick access button ("Write something...")
- `frontend/src/features/community/components/CreatePostModal.tsx` - Full post creation form
- `frontend/src/features/community/components/FeedPostCard.tsx` - Post display in feed
- `frontend/src/features/community/components/PostDetail.tsx` - Single post full view
- `frontend/src/features/community/components/CategoryTabs.tsx` - Category filter pills

**Pages:**
- `frontend/src/pages/CommunityPage.tsx` - Main feed container
- `frontend/src/pages/PostDetailPage.tsx` - Individual post page

### API Integration

**API Client:**
- `frontend/src/features/community/api/postApi.ts`
  - `createPost(data)` → POST /posts
  - `getPost(id)` → GET /posts/:id
  - `updatePost(id, data)` → PATCH /posts/:id
  - `deletePost(id)` → DELETE /posts/:id
  - `getPosts(params)` → GET /posts

**Custom Hooks:**
- `frontend/src/features/community/hooks/useCreatePost.ts`
- `frontend/src/features/community/hooks/usePost.ts`
- `frontend/src/features/community/hooks/usePosts.ts`

**Types:**
- `frontend/src/features/community/types/community.ts`
  - Post, Category, CommunityMember interfaces
  - CreatePostRequest, UpdatePostRequest types

### Routes

```tsx
// Add to frontend/src/App.tsx
<Route path="/community" element={<CommunityPage />} />
<Route path="/community/posts/:id" element={<PostDetailPage />} />
```

### Component Details

#### CreatePostModal.tsx
- Modal overlay with form
- Fields: title (200 chars), content (5000 chars), category dropdown, image URL
- Character counters
- Real-time validation
- Category selector with emojis
- Submit button (disabled when invalid)
- Cancel button

#### FeedPostCard.tsx
- Author avatar, name, timestamp
- Category badge with emoji
- Post title (clickable)
- Post content (truncated to ~500 chars)
- Image thumbnail (if present)
- Engagement row: like count, comment count
- "Pinned" indicator (if pinned)
- "Edited" indicator (if edited)
- Click → navigate to PostDetailPage

#### CategoryTabs.tsx
- Horizontal scrollable pills
- "All" option
- Category pills with emoji + name + post count
- Active state: black background, white text
- Inactive state: gray background
- Click → filter feed

### User Value

✅ Users can:
- Browse posts in a feed
- Create new posts with rich content
- Filter posts by category
- View individual posts
- Edit/delete their own posts

### Verification Commands

```bash
# Check files created
ls -la frontend/src/features/community/components/
ls -la frontend/src/pages/Community*

# Type checking
cd frontend && npm run typecheck

# Unit tests
npm run test

# Deployability check (should show frontend components)
./scripts/check-deployability.sh community
# Expected: ✅ Frontend: 5+ components
```

### Definition of Done

- [ ] All 7 components/pages created
- [ ] TypeScript types defined
- [ ] API client implemented with error handling
- [ ] Custom hooks implemented
- [ ] Routes added to App.tsx
- [ ] Mobile responsive (375px, 768px, 1024px)
- [ ] Loading states (skeleton cards)
- [ ] Empty state ("No posts yet. Be the first to post!")
- [ ] Error handling (network failures, validation errors)
- [ ] `npm run typecheck` passes
- [ ] Basic smoke tests pass
- [ ] Can create a post end-to-end
- [ ] Can view post in feed and detail page

---

## Phase 2: Comments & Reactions

**Duration:** 4-5 hours

### Goal
Users can comment on posts (with 1-level threading), like posts and comments, and engage in discussions.

### Components to Build

**Core Components:**
- `frontend/src/features/community/components/CommentsSection.tsx` - Full comments display with threading
- `frontend/src/features/community/components/CommentList.tsx` - Threaded comment rendering
- `frontend/src/features/community/components/CommentForm.tsx` - Add/reply to comments
- `frontend/src/features/community/components/LikeButton.tsx` - Reusable like component

### API Integration

**API Clients:**
- `frontend/src/features/community/api/commentApi.ts`
  - `createComment(postId, data)` → POST /posts/:id/comments
  - `replyToComment(commentId, data)` → POST /comments/:id/replies
  - `updateComment(id, data)` → PATCH /comments/:id
  - `deleteComment(id)` → DELETE /comments/:id
  - `getComments(postId)` → GET /posts/:id/comments

- `frontend/src/features/community/api/reactionApi.ts`
  - `likePost(postId)` → POST /posts/:id/like
  - `unlikePost(postId)` → DELETE /posts/:id/like
  - `likeComment(commentId)` → POST /comments/:id/like
  - `unlikeComment(commentId)` → DELETE /comments/:id/like

**Custom Hooks:**
- `frontend/src/features/community/hooks/useComments.ts`
- `frontend/src/features/community/hooks/useCreateComment.ts`
- `frontend/src/features/community/hooks/useLikePost.ts`
- `frontend/src/features/community/hooks/useLikeComment.ts`

**Types:**
- Update `frontend/src/features/community/types/community.ts`
  - Comment, Reaction interfaces
  - CreateCommentRequest, UpdateCommentRequest types

### Component Details

#### CommentsSection.tsx
- Comment count header
- List of comments with replies (indented)
- Add comment form at bottom
- "Comments are disabled" message (if locked)
- Loading state (skeleton comments)
- Empty state ("No comments yet. Be the first!")

#### CommentList.tsx
- Top-level comments
- Replies indented under parent (ml-6)
- Comment bubble: gray background, rounded
- Author avatar (10px main, 8px replies)
- Author name, timestamp, edited indicator
- Comment content
- Like button + count
- Reply button (only on top-level)
- Maximum 1 level deep (no reply to reply)

#### LikeButton.tsx
- Thumbs up emoji
- Like count (if > 0)
- Active state: blue background
- Inactive state: gray background
- Optimistic update on click
- Revert on error

### Updates to Existing Components

**PostDetail.tsx:**
- Add `<CommentsSection postId={post.id} />`
- Add `<LikeButton postId={post.id} />`
- Display likers (avatars + names)

**FeedPostCard.tsx:**
- Add `<LikeButton postId={post.id} />` (compact version)
- Show like count, comment count

### User Value

✅ Users can:
- Comment on posts
- Reply to comments (1 level)
- Like posts and comments
- See who liked content
- Edit/delete their own comments
- View threaded discussions

### Verification Commands

```bash
# Backend BDD tests (should pass comments & reactions scenarios)
pytest tests/features/community/test_feed.py -v -k "comment or reaction"

# Frontend tests
cd frontend && npm run test

# Type checking
npm run typecheck

# Manual testing
npm run dev
# 1. Create a post
# 2. Add a comment
# 3. Reply to comment
# 4. Like post and comment
# 5. Unlike
```

### Definition of Done

- [ ] All 4 components created
- [ ] API clients implemented
- [ ] Custom hooks implemented
- [ ] Comments display with threading
- [ ] Like functionality with optimistic updates
- [ ] Mobile responsive
- [ ] Loading states (skeleton comments)
- [ ] Empty states (no comments)
- [ ] Error handling
- [ ] Locked post state (no comment form)
- [ ] `npm run typecheck` passes
- [ ] Can add comment end-to-end
- [ ] Can like/unlike end-to-end
- [ ] Replies properly indented
- [ ] Edit/delete own comments works

---

## Phase 3: Feed Sorting, Pinning & Sidebar

**Duration:** 3-4 hours

### Goal
Users can sort feed (Hot/New/Top/Pinned), see pinned posts, view community stats, and experience smooth infinite scroll.

### Components to Build

**Core Components:**
- `frontend/src/features/community/components/SortDropdown.tsx` - Hot/New/Top/Pinned selector
- `frontend/src/features/community/components/CommunitySidebar.tsx` - Community stats and promo card
- `frontend/src/features/community/components/FeedView.tsx` - Enhanced feed with sorting & infinite scroll

### API Integration

**API Client:**
- `frontend/src/features/community/api/feedApi.ts`
  - `getFeed(params)` → GET /feed?sort=hot&category=general&cursor=abc123&limit=20
  - `getCategories(communityId)` → GET /communities/:id/categories

**Custom Hooks:**
- `frontend/src/features/community/hooks/useFeed.ts` - Infinite scroll with cursor pagination
- `frontend/src/features/community/hooks/useCategories.ts`
- `frontend/src/features/community/hooks/useInfiniteScroll.ts`

### Component Details

#### SortDropdown.tsx
- Button showing current sort (⚡ Default, 🆕 New, 🔝 Top, 📌 Pinned)
- Dropdown menu on click
- Active item: yellow highlight
- Updates feed on selection

#### CommunitySidebar.tsx
- Promo card (dark background, gradient header, CTA button)
- Community stats card:
  - Member count
  - Online count
  - Admin count
- Member avatars (overlapping circles)
- "INVITE PEOPLE" button
- Sticky positioning (top-20)

#### FeedView.tsx
- CategoryTabs at top
- SortDropdown in header
- List of FeedPostCard
- Infinite scroll (Intersection Observer)
- Loading indicator (skeleton cards) while fetching
- "No more posts" message at end

### Updates to Existing Components

**CommunityPage.tsx:**
- 3-column layout (categories, feed, sidebar)
- Responsive: single column on mobile

**PostDetail.tsx / FeedPostCard.tsx:**
- Add pin/unpin button (admin/moderator only)
- Show "Pinned" indicator

### Infinite Scroll Implementation

- Use Intersection Observer on sentinel div
- Trigger load when sentinel 80% visible
- Cursor-based pagination (not offset)
- Append new posts smoothly (no jump)
- Maintain scroll position

### User Value

✅ Users can:
- Sort feed by engagement (Hot), recency (New), or popularity (Top)
- See pinned posts at top
- View community stats
- Scroll infinitely through feed
- Filter by category + sort combination

### Verification Commands

```bash
# Backend BDD tests (should pass feed scenarios)
pytest tests/features/community/test_feed.py -v -k "feed or sort or pin"

# Frontend tests
cd frontend && npm run test

# E2E test (if written)
npm run test:e2e -- community-feed

# Deployability check
./scripts/check-deployability.sh community
# Expected: ✅ Feature is DEPLOYABLE
```

### Definition of Done

- [ ] All 3 components created
- [ ] Feed API with cursor pagination
- [ ] Infinite scroll working smoothly
- [ ] Sort dropdown changes feed order
- [ ] Pinned posts appear at top
- [ ] Category filter + sort combinations work
- [ ] Sidebar displays community stats
- [ ] Mobile responsive (sidebar moves below feed)
- [ ] Loading states during scroll
- [ ] "No more posts" indicator
- [ ] `npm run typecheck` passes
- [ ] Can sort feed end-to-end
- [ ] Can scroll and load more posts
- [ ] Admins can pin/unpin posts

---

## Phase 4: Polish, Edge Cases & E2E Tests

**Duration:** 2-3 hours

### Goal
Handle all edge cases, implement production-ready polish, and achieve comprehensive E2E test coverage.

### Tasks

#### Empty States
- [ ] No posts in feed: "No posts yet. Be the first to post!"
- [ ] No posts in category: "No posts in this category yet."
- [ ] No comments on post: "No comments yet. Start the conversation!"
- [ ] Post deleted: "This post has been deleted"

#### Loading States
- [ ] Feed loading: Skeleton cards (3-5 cards)
- [ ] Post detail loading: Skeleton post + comments
- [ ] Comments loading: Skeleton comment bubbles
- [ ] Button submitting: Spinner icon, disabled state
- [ ] Infinite scroll: Skeleton cards at bottom

#### Error States
- [ ] Feed load failed: "Failed to load feed. Retry?"
- [ ] Post creation failed: Inline error message
- [ ] Comment submission failed: Toast notification
- [ ] Network offline: "You're offline. Changes will sync when reconnected."
- [ ] 403 Forbidden: "You don't have permission for this action"
- [ ] 404 Not Found: "Post not found" page

#### Optimistic Updates
- [ ] Like button: Toggle immediately, revert on error
- [ ] Comment submission: Show immediately, remove on error
- [ ] Post creation: Navigate to post, rollback on error

#### Mobile Responsive
- [ ] Test at 375px (iPhone SE)
- [ ] Test at 768px (iPad)
- [ ] Test at 1024px (Desktop)
- [ ] Horizontal scroll for category pills on mobile
- [ ] Sidebar moves below feed on tablet
- [ ] Modal full screen on mobile

#### Accessibility
- [ ] Focus states on all interactive elements
- [ ] ARIA labels for icon-only buttons
- [ ] Keyboard navigation (Tab, Enter, ESC)
- [ ] Screen reader announcements for live updates
- [ ] Color contrast WCAG AA minimum
- [ ] Alt text for all images

#### Performance
- [ ] Lazy load CreatePostModal
- [ ] Memoize expensive components (PostCard with many likers)
- [ ] Debounce category filter (if search added)
- [ ] Image lazy loading with blur placeholder

### E2E Tests

**File:** `tests/e2e/specs/community-feed.spec.ts`

**Test Scenarios:**
```typescript
describe('Community Feed', () => {
  it('should display feed with posts', () => {
    // Visit /community
    // See list of posts
    // See category tabs
    // See sort dropdown
  });

  it('should create a post', () => {
    // Click "Write something..."
    // Fill title, content, select category
    // Submit
    // See post in feed
    // Navigate to post detail
  });

  it('should comment on a post', () => {
    // Navigate to post detail
    // Type comment
    // Submit
    // See comment appear
  });

  it('should like a post', () => {
    // Click like button
    // See count increment
    // See button active state
    // Click again to unlike
  });

  it('should filter by category', () => {
    // Click category pill
    // See only posts in that category
    // URL updates with ?category=slug
  });

  it('should sort feed', () => {
    // Click sort dropdown
    // Select "New"
    // See posts sorted by recency
  });

  it('should load more posts on scroll', () => {
    // Scroll to bottom
    // See loading indicator
    // See more posts appear
  });

  it('should handle locked post', () => {
    // Navigate to locked post
    // See "Comments are disabled"
    // No comment form visible
  });
});
```

### User Value

✅ Users experience:
- Production-ready UI with all edge cases handled
- Fast, responsive interactions
- Clear feedback for all actions
- Accessible interface for keyboard/screen reader users
- Smooth mobile experience

### Verification Commands

```bash
# Full E2E test suite
npm run test:e2e

# Frontend unit tests
npm run test

# Coverage check
npm run test:coverage

# Type checking
npm run typecheck

# Linting
npm run lint

# Build check
npm run build

# Backend verification
./scripts/verify.sh

# Frontend verification
./scripts/verify-frontend.sh

# Deployability final check
./scripts/check-deployability.sh community
# Expected:
# ✅ Feature is DEPLOYABLE:
#    ✅ Backend: X controllers
#    ✅ Frontend: Y components
#    ✅ Users can interact with this feature
```

### Definition of Done

- [ ] All empty states implemented
- [ ] All loading states implemented
- [ ] All error states implemented
- [ ] Optimistic updates working
- [ ] Mobile responsive (all breakpoints)
- [ ] Accessibility audit passed
- [ ] E2E tests passing (100% critical paths)
- [ ] No console errors or warnings
- [ ] `npm run build` succeeds
- [ ] All verification scripts pass
- [ ] Deployability check passes
- [ ] Feature ready for production deployment

---

## Dependency Graph

```
Phase 1 (Post Viewing & Creation)
    ↓
Phase 2 (Comments & Reactions)
    ↓
Phase 3 (Feed Sorting & Sidebar)
    ↓
Phase 4 (Polish & E2E Tests)
```

**Linear dependency:** Each phase builds on the previous one.

---

## Success Criteria

**A good phase is:**
- ✅ Independently testable
- ✅ Provides incremental user value
- ✅ Reasonable size (3-5 hours)
- ✅ Clear dependencies

**Phase completion checklist:**
- [ ] All components for phase created
- [ ] API integration complete
- [ ] Mobile responsive
- [ ] Loading/empty states
- [ ] Error handling
- [ ] Type checking passes
- [ ] Manual testing complete
- [ ] User can perform new actions

**Feature completion (after Phase 4):**
- [ ] ALL components created
- [ ] ALL user journeys tested (E2E)
- [ ] Deployability check passes
- [ ] No console errors
- [ ] Production-ready quality

---

## Implementation Notes

### Patterns to Follow

**From Identity Feature:**
- Form patterns: `RegisterForm.tsx`, `LoginForm.tsx`
- API client structure: `frontend/src/features/identity/api/auth.ts`
- Custom hooks: `useAuth.ts`, `useCurrentUser.ts`
- Page structure: `frontend/src/pages/Register.tsx`

**From UI Spec:**
- Color palette: `bg-gray-50` page, `bg-white` cards, `bg-gray-900` primary buttons
- Typography: `text-base` body, `text-lg` card titles, `text-2xl` detail titles
- Spacing: `p-4` cards, `gap-3` elements, `gap-6` sections
- Interactive: `hover:shadow-sm`, `transition-colors`

### Common Pitfalls

- ❌ Don't bypass API client (call fetch directly)
- ❌ Don't skip loading states
- ❌ Don't ignore error handling
- ❌ Don't hardcode community ID (get from context)
- ❌ Don't use offset pagination (use cursor)
- ❌ Don't allow HTML in content (backend sanitizes, but don't render unsafely)

### Testing Strategy

- **Unit tests:** Custom hooks, utility functions
- **Integration tests:** Component interactions
- **E2E tests:** Critical user journeys (create post, comment, like)
- **Manual testing:** Mobile responsive, accessibility

---

## Related Documents

- `docs/features/community/feed-prd.md` - Product requirements
- `docs/features/community/UI_SPEC.md` - Component specifications from Skool screenshots
- `docs/features/community/feed-implementation-phases.md` - Backend implementation phases
- `docs/features/community/feed-tdd.md` - Technical design document
- `.claude/skills/frontend/SKILL.md` - Frontend coding standards
- `.claude/skills/ui-design/SKILL.md` - UI design system standards

---

## Approval

**Engineering Lead:** _________________
**Product Owner:** _________________

**Status:** Planned - Awaiting Approval

**Next Step:** Begin Phase 1 implementation upon approval
