# Community Feed - Product Requirements Document

**Version:** 1.0
**Last Updated:** February 11, 2026
**Status:** In Progress - Phase 3 Complete
**Implementation Status:** Phase 3 Complete (Pinning, Sorting, Category CRUD, Rate Limiting)
**Bounded Context:** Community
**PRD Type:** Feature Specification

**Implementation Summaries:**
- Phase 1: `docs/summaries/community/community-feed-phase1-summary.md`
- Phase 2: `docs/summaries/community/community-feed-phase2-summary.md`
- Phase 3: `docs/summaries/community/community-feed-phase3-summary.md`

---

## 1. Overview

### 1.1 What

A complete community discussion system including posts, comments, reactions (likes), categories, and a dynamic feed. Members can create posts with titles and content, engage through comments and likes, and organize discussions by category. The feed displays posts sorted by engagement (Hot), recency (New), or popularity (Top).

### 1.2 Why

The Community Feed is the heart of Koulu - where members interact, share knowledge, ask questions, and build relationships. Without this, Koulu is just a user database. This feature drives daily engagement and creates the social fabric that makes communities valuable.

### 1.3 Success Criteria

| Metric | Target |
|--------|--------|
| Daily active users (DAU) | > 40% of community members |
| Posts per day per 100 members | > 5 |
| Comments per post | > 3 average |
| Like rate | > 60% of posts receive at least 1 like |
| User retention (7-day) | > 70% |

---

## 2. User Stories

### 2.1 Posts

| ID | Story | Priority |
|----|-------|----------|
| US-P1 | As a member, I want to create a post with a title and content so that I can start a discussion | Must Have |
| US-P2 | As a member, I want to attach an image to my post so that I can share visual content | Must Have |
| US-P3 | As a member, I want to assign a category to my post so that it's organized | Must Have |
| US-P4 | As a member, I want to edit my post after publishing so that I can correct mistakes | Must Have |
| US-P5 | As a member, I want to delete my own post so that I can remove content I regret | Must Have |
| US-P6 | As an admin, I want to delete any post so that I can moderate inappropriate content | Must Have |
| US-P7 | As an admin, I want to pin important posts so they stay at the top of the feed | Must Have |
| US-P8 | As an admin, I want to lock comments on a post so that I can stop toxic discussions | Must Have |

### 2.2 Comments

| ID | Story | Priority |
|----|-------|----------|
| US-C1 | As a member, I want to comment on a post so that I can participate in discussions | Must Have |
| US-C2 | As a member, I want to reply to a comment so that I can have threaded conversations | Must Have |
| US-C3 | As a member, I want to edit my comment so that I can fix typos | Must Have |
| US-C4 | As a member, I want to delete my comment so that I can remove it | Must Have |
| US-C5 | As an admin, I want to delete any comment so that I can moderate discussions | Must Have |

### 2.3 Reactions

| ID | Story | Priority |
|----|-------|----------|
| US-R1 | As a member, I want to like a post so that I can show appreciation | Must Have |
| US-R2 | As a member, I want to like a comment so that I can agree or appreciate it | Must Have |
| US-R3 | As a member, I want to see who liked a post so that I can discover active members | Should Have |
| US-R4 | As a member, I want to unlike a post/comment so that I can change my mind | Must Have |

### 2.4 Categories

| ID | Story | Priority |
|----|-------|----------|
| US-CAT1 | As an admin, I want to create categories so that I can organize discussions | Must Have |
| US-CAT2 | As an admin, I want to edit category names so that I can refine organization | Must Have |
| US-CAT3 | As a member, I want to filter posts by category so that I can find relevant content | Must Have |
| US-CAT4 | As an admin, I want to move posts to different categories so that I can maintain organization | Must Have |

### 2.5 Feed

| ID | Story | Priority |
|----|-------|----------|
| US-F1 | As a member, I want to see a feed of posts sorted by "Hot" so that I see engaging discussions | Must Have |
| US-F2 | As a member, I want to switch to "New" sorting so that I see the latest posts | Must Have |
| US-F3 | As a member, I want to switch to "Top" sorting so that I see the most popular posts | Must Have |
| US-F4 | As a member, I want to see pinned posts at the top so that I don't miss announcements | Must Have |
| US-F5 | As a member, I want the feed to load more posts as I scroll so that I can browse continuously | Must Have |

### 2.6 Permissions

| ID | Story | Priority |
|----|-------|----------|
| US-PERM1 | As an admin, I want to assign moderator roles so that I can delegate moderation | Should Have |
| US-PERM2 | As a moderator, I want to delete posts and lock comments so that I can moderate the community | Should Have |
| US-PERM3 | As a member, I want to only modify my own content so that others can't tamper with my posts | Must Have |

---


## 3. Business Rules

### 3.1 Content Rules

**Post Requirements:**
- Title: Required, 1-200 characters
- Content: Required, 1-5,000 characters
- Image: Optional, must be HTTPS URL if provided
- Category: Required, must exist in community

**Comment Requirements:**
- Content: Required, 1-2,000 characters
- Threading: Maximum 1 level deep (comment → reply, but reply cannot have sub-replies)
- Cannot comment on locked posts

**Category Requirements:**
- Name: Required, 1-50 characters, must be unique within community
- Slug: Required, lowercase alphanumeric + hyphens only, must be unique
- Cannot delete categories with existing posts

---

### 3.2 Permission Rules

| Action | Member | Moderator | Admin |
|--------|--------|-----------|-------|
| Create post | ✓ | ✓ | ✓ |
| Edit own post | ✓ | ✓ | ✓ |
| Delete own post | ✓ | ✓ | ✓ |
| Delete any post | ✗ | ✓ | ✓ |
| Pin/unpin post | ✗ | ✓ | ✓ |
| Lock/unlock post | ✗ | ✓ | ✓ |
| Add comment | ✓ | ✓ | ✓ |
| Edit own comment | ✓ | ✓ | ✓ |
| Delete own comment | ✓ | ✓ | ✓ |
| Delete any comment | ✗ | ✓ | ✓ |
| Like posts/comments | ✓ | ✓ | ✓ |
| Create category | ✗ | ✗ | ✓ |
| Update category | ✗ | ✗ | ✓ |
| Delete category | ✗ | ✗ | ✓ |
| Move post to category | ✗ | ✓ | ✓ |
| Change member roles | ✗ | ✗ | ✓ |

---

### 3.3 Feed Sorting Algorithms

**Hot (Default):**
- Prioritizes recent activity (comments, likes)
- Posts with activity in last 24 hours
- Sorted by: (comment_count + like_count) / hours_since_created
- Pinned posts always appear first

**New:**
- Pure chronological order
- Sorted by: created_at descending
- Pinned posts always appear first

**Top:**
- Most popular posts by like count
- Sorted by: like_count descending, then created_at descending
- Pinned posts always appear first

**Pinned Posts:**
- Always appear at top of feed regardless of sort order
- Displayed in order they were pinned (most recent pin first)
- Maximum 5 pinned posts visible at once

---

### 3.4 Rate Limiting

To prevent spam and abuse:
- Post creation: 10 posts per hour per user
- Comment creation: 50 comments per hour per user
- Reactions: 200 likes per hour per user
- Post editing: Unlimited (but shows edited indicator)

---

### 3.5 Cascading Deletion

**When a post is deleted:**
- All comments on the post are deleted
- All reactions on the post are deleted
- Reactions on deleted comments are deleted
- Domain events are published for audit trail

**When a comment with replies is deleted:**
- If comment has replies: Show "[deleted]" placeholder, keep replies visible
- If comment has no replies: Remove completely
- All reactions on the comment are deleted

**When a user leaves a community:**
- Their posts remain but author shows "[deleted user]"
- Their comments remain but author shows "[deleted user]"
- Their reactions are removed

---

## 4. UI Behavior

### 4.1 Feed View

**Layout:**
- Left sidebar: Category filter list
- Main content: Post feed
- Right sidebar: Community info, online members

**Post Card Display:**
- Author avatar + display name + level badge
- Category badge (colored, with emoji)
- Post title (bold, clickable)
- Post content (truncated to ~500 chars with "Read more...")
- Image (if present, thumbnail)
- Engagement row: Like button + count, Comment count, Share button (future)
- Timestamp (relative: "3h ago")
- "Pinned" indicator if applicable
- "Edited" indicator if applicable

**States:**
- Loading: Skeleton cards
- Empty state: "No posts yet. Be the first to post!"
- Error state: "Failed to load feed. Retry?"

**Interactions:**
- Click post title/content → Navigate to post detail
- Click category badge → Filter feed by that category
- Click like button → Toggle like (optimistic update)
- Scroll to bottom → Load more posts (cursor pagination)
- Sort dropdown → Switch between Hot/New/Top

---

### 4.2 Post Detail View

**Layout:**
- Full post content (title, body, image)
- Author info
- Engagement stats (like count, comment count)
- Like button (shows if current user liked)
- List of likers (avatars, show first 5 + "and X others")
- Comments section below

**Comments Section:**
- Comments listed chronologically (oldest first)
- Each comment shows: avatar, author, content, like button + count, timestamp, "Reply" button
- Replies indented under parent comment
- Reply depth limited to 1 level
- "Add comment" form at bottom
- If post is locked: "Comments are disabled" message, no form

**Edit Mode:**
- If viewing own post: Show "Edit" and "Delete" buttons
- If admin/moderator: Show "Delete", "Pin/Unpin", "Lock/Unlock" buttons
- Edit opens inline form with save/cancel buttons
- On save: Show "edited" indicator with timestamp

---

### 4.3 Create Post Modal

**Trigger:** Click "New Post" button in header

**Form Fields:**
1. Category dropdown (required) - Defaults to "General"
2. Title input (required, 200 char limit with counter)
3. Content textarea (required, 5000 char limit with counter, rich text editor)
4. Image URL input (optional, validates HTTPS)
5. Image preview (if URL provided)

**Validation:**
- Real-time: Character count, URL format
- On submit: All required fields filled

**Actions:**
- "Cancel" - Close modal, discard draft
- "Post" - Create post, close modal, redirect to post detail

**States:**
- Submitting: Disable form, show spinner
- Success: Show toast "Post created!", redirect
- Error: Show error message inline, keep form open

---

### 4.4 Category Filter

**Location:** Left sidebar

**Display:**
- "All" (shows all categories, default)
- List of categories with emoji + name
- Post count badge next to each category

**Interaction:**
- Click category → Filter feed to show only posts in that category
- Active category highlighted
- URL updates with category slug (e.g., `/feed?category=qa`)

---

### 4.5 Notifications (Visual Feedback)

**In-app toasts:**
- "Post created successfully"
- "Post deleted"
- "Comment added"
- "You liked this post"
- "Post pinned"

**Error messages:**
- "Failed to create post. Please try again."
- "You don't have permission to delete this post."
- "Post is locked. Cannot add comments."

**Loading indicators:**
- Skeleton cards while feed loads
- Spinner on buttons during actions
- Progress bar for image uploads (future)

---

## 5. Edge Cases

### 5.1 Deleted Content

**When author deletes post:**
- Post removed from feed immediately
- Users viewing post detail see 404
- Comments and reactions cascade delete
- Domain events published for audit

**When author deletes comment with replies:**
- Comment content replaced with "[deleted]"
- Replies remain visible
- Author name shows "[deleted]"

**When admin deletes content:**
- Same behavior as author delete
- Audit log records who deleted (admin user_id)

---

### 5.2 Concurrent Edits

**Scenario:** Two users edit the same post simultaneously

**Behavior:**
- Last write wins (no conflict resolution in MVP)
- Both edits increment updated_at timestamp
- edited_at shows most recent edit time

**Future:** Add optimistic locking with version field

---

### 5.3 Orphaned References

**Scenario:** Category deleted while posts reference it

**Prevention:**
- Validation: Cannot delete category with posts
- Admin must reassign posts to different category first
- API returns 400 Bad Request with message

**Scenario:** User account deleted (Identity context)

**Behavior:**
- Posts/comments remain but show "[deleted user]"
- Reactions removed
- CommunityMember marked as inactive

---

### 5.4 Rate Limit Exceeded

**Scenario:** User tries to create 11th post in an hour

**Behavior:**
- API returns 429 Too Many Requests
- Response includes: "You've reached the post limit. Try again in X minutes."
- Client disables "New Post" button temporarily
- Shows toast with retry time

---

### 5.5 Invalid Image URLs

**Scenario:** User provides invalid or broken image URL

**Behavior:**
- During post creation: Validate URL format (must be HTTPS)
- After post created: If image fails to load, show broken image placeholder
- No post rejection for broken images after creation
- Users can edit post to fix URL

---

### 5.6 Empty Feed States

**Scenario:** Community has no posts yet

**Display:**
- Empty state illustration
- Message: "No posts yet. Be the first to start a conversation!"
- Prominent "New Post" button

**Scenario:** Category has no posts

**Display:**
- "No posts in this category yet."
- Link back to "All" categories

---

### 5.7 Locked Post Interactions

**Scenario:** User tries to comment on locked post

**Behavior:**
- Comment form hidden
- Message: "Comments are disabled on this post"
- Existing comments remain visible
- Likes still allowed

---

### 5.8 Permission Denials

**Scenario:** Member tries to delete another member's post

**API Response:**
- 403 Forbidden
- Message: "You don't have permission to delete this post"

**UI Behavior:**
- Delete button not shown if user lacks permission
- If attempted via API: Show error toast

---

## 6. Security Requirements

### 6.1 Authentication

- All API endpoints require valid JWT token
- Token must contain user_id and community membership claim
- Expired tokens rejected with 401 Unauthorized

---

### 6.2 Authorization

**Permission Checks:**
- Before any write operation, verify user's CommunityMember role
- Before editing/deleting content, verify ownership OR admin/moderator role
- Before viewing content, verify user is member of community

**Role Assignment:**
- Only admins can change member roles
- Cannot remove last admin from community
- Cannot promote users who are not members

---

### 6.3 Input Validation

**All user input must be validated:**
- Title: 1-200 chars, no HTML tags
- Content: 1-5000 chars (posts) or 1-2000 chars (comments)
- URLs: Valid HTTPS format
- Category slugs: Alphanumeric + hyphens only
- No script injection (sanitize HTML)

---

### 6.4 Data Protection

**Soft Delete:**
- Posts and comments soft-deleted (marked as deleted, not removed from DB)
- Allows audit trail and abuse investigation
- Hard delete option for admins (compliance with data deletion requests)

**Rate Limiting:**
- Prevents spam and abuse
- Limits documented in Business Rules section

**CSRF Protection:**
- All state-changing operations require CSRF token
- Token validated on server side

---

### 6.5 Content Moderation

**Admin Tools:**
- Delete posts/comments
- Lock comment threads
- View audit log of deleted content

**Abuse Prevention:**
- Rate limits on post/comment creation
- Report functionality (Phase 2)
- IP-based rate limiting (future)

---

## 7. Out of Scope

The following features are **NOT** included in this PRD and will be addressed in future phases:

### 7.1 Not in MVP
- Native image upload (using external URLs only)
- Video upload/hosting (embeds only, Phase 2)
- Polls
- Post drafts
- Rich text formatting (bold, italic, links) - plain text only
- @mentions triggering notifications (parsing only)
- Search functionality
- Post bookmarking/saving
- Post sharing
- Email notifications
- Push notifications
- Multi-community switching UI

### 7.2 Phase 2 Features
- Community creation and management UI
- Member invitation system
- Role management UI (assign moderators)
- Notification system
- Advanced moderation tools (ban users, view reports)
- Analytics (post views, engagement metrics)
- Trending posts algorithm

### 7.3 Phase 3 Features
- Native video hosting
- Advanced rich text editor (markdown, embeds)
- Post templates
- Scheduled posts
- Community discovery
- Public vs private communities
- Payment/subscription integration

---

## 8. Success Metrics

### 8.1 Engagement Metrics

| Metric | Measurement | Target |
|--------|-------------|--------|
| Daily Active Users (DAU) | Unique users viewing feed per day | > 40% of members |
| Posts per day | Total posts created per day | > 5 per 100 members |
| Comments per post | Average comments per post | > 3 |
| Like rate | % of posts receiving at least 1 like | > 60% |
| Reply rate | % of comments receiving a reply | > 30% |

### 8.2 Quality Metrics

| Metric | Measurement | Target |
|--------|-------------|--------|
| Post retention | % of posts not deleted by author within 24h | > 95% |
| Average post length | Character count | 200-1000 chars |
| Moderation rate | % of posts requiring admin deletion | < 5% |
| Time to first comment | Median time from post to first comment | < 2 hours |

### 8.3 Technical Metrics

| Metric | Measurement | Target |
|--------|-------------|--------|
| Feed load time | Time to render 20 posts | < 1 second (p95) |
| API response time | Post creation latency | < 300ms (p95) |
| Error rate | % of API requests failing | < 1% |

---

## 9. Dependencies

### 9.1 Upstream Dependencies

**Identity Context:**
- UserId value object
- User authentication (JWT tokens)
- User profile information (display_name, avatar_url)

**Infrastructure:**
- PostgreSQL database
- Redis cache (for rate limiting)
- Image hosting service (external URLs)
- Domain event bus

### 9.2 Downstream Consumers

**Gamification Context (Phase 2):**
- Consumes PostCreated, CommentAdded, PostLiked, CommentLiked events
- Awards points to content creators

**Notification Context (Phase 2):**
- Consumes CommentAdded, PostLiked, UserMentioned events
- Sends in-app and email notifications

---

## 10. Open Questions

1. **Image hosting strategy:** Should we integrate with Cloudinary/S3 for direct uploads, or continue with URL-only approach?
   - Decision deferred to TDD phase

2. **Rich text editor:** Plain text only for MVP, or basic markdown support?
   - Decision: Plain text only (simplifies validation and prevents XSS)

3. **Search functionality:** Should basic post search be in MVP or Phase 2?
   - Decision: Phase 2 (requires full-text search indexing)

4. **Comment sorting:** Always chronological, or allow sorting by likes?
   - Decision: Chronological only for MVP (simpler conversation flow)

---

## 11. Appendix

### 11.1 Related Documents

- `docs/OVERVIEW_PRD.md` - Master PRD with full feature set
- `docs/domain/GLOSSARY.md` - Ubiquitous language definitions
- `docs/architecture/CONTEXT_MAP.md` - Bounded context relationships
- `tests/features/community/feed.feature` - BDD specifications for this feature

### 11.2 Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-06 | Product Team | Initial draft for MVP |

---

## 12. Approval

**Product Owner:** _________________
**Engineering Lead:** _________________
**Design Lead:** _________________

**Status:** Draft - Pending Review
