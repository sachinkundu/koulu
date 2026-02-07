# Community Feed - Technical Design Document

**Version:** 1.0
**Status:** Draft
**Last Updated:** February 7, 2026
**Bounded Context:** Community
**Related Documents:**
- PRD: `docs/features/community/feed-prd.md`
- BDD Spec: `tests/features/community/feed.feature`
- Context Map: `docs/architecture/CONTEXT_MAP.md`

---

## 1. Overview

### 1.1 Summary

The Community Feed system enables members to create posts, engage through comments and reactions, organize content by categories, and consume a dynamic feed sorted by engagement, recency, or popularity. This is the core social interaction layer of Koulu, driving daily engagement and community building.

### 1.2 Goals

**Primary:**
- Implement a complete discussion system with posts, comments, and reactions
- Provide multiple feed sorting algorithms (Hot, New, Top) with pinned posts
- Enable category-based content organization
- Support role-based permissions (Member, Moderator, Admin)
- Ensure rate limiting prevents spam and abuse
- Maintain data integrity through proper cascading deletion

**Secondary:**
- Lay foundation for future gamification integration (point awards)
- Prepare for future notification system
- Design for eventual multi-community support

### 1.3 Non-Goals

**Not in this implementation:**
- Native image/video upload (URLs only)
- Rich text editor (plain text only)
- Search functionality
- Real-time updates via WebSocket
- Email/push notifications
- Multi-community UI switching
- Content moderation workflows beyond delete/lock

---

## 2. Architecture

### 2.1 System Context Diagram

```
┌─────────────────────────────────────────────────────────┐
│                   External Systems                      │
├─────────────────────────────────────────────────────────┤
│  MailHog (Dev)  │  Redis  │  PostgreSQL  │  Frontend   │
└────────┬────────┴────┬────┴──────┬───────┴──────┬───────┘
         │             │           │              │
         │             │           │              │
┌────────▼─────────────▼───────────▼──────────────▼───────┐
│                   Community Context                      │
├──────────────────────────────────────────────────────────┤
│  ┌─────────────────┐   ┌─────────────────┐             │
│  │     Domain      │   │   Application   │             │
│  │                 │   │                 │             │
│  │ • Post          │   │ • CreatePost    │             │
│  │ • Comment       │   │ • DeletePost    │             │
│  │ • Reaction      │   │ • AddComment    │             │
│  │ • Category      │   │ • LikePost      │             │
│  │ • Member        │   │ • GetFeed       │             │
│  └─────────────────┘   └─────────────────┘             │
│                                                          │
│  ┌─────────────────┐   ┌─────────────────┐             │
│  │ Infrastructure  │   │   Interface     │             │
│  │                 │   │                 │             │
│  │ • Repositories  │   │ • REST API      │             │
│  │ • RateLimiter   │   │ • Controllers   │             │
│  │ • EventBus      │   │ • Schemas       │             │
│  └─────────────────┘   └─────────────────┘             │
└──────────────────────────────────────────────────────────┘
         │             │           │
         ▼             ▼           ▼
┌────────────────────────────────────────────┐
│           Future Bounded Contexts          │
├────────────────────────────────────────────┤
│  Gamification  │  Notification  │  Search  │
│  (Phase 2)     │  (Phase 2)     │  (Ph 3)  │
└────────────────────────────────────────────┘
```

### 2.2 Component Architecture

**Hexagonal Architecture Layers:**

```
┌─────────────────────────────────────────────────────────┐
│                      Interface Layer                    │
│  (Adapters: HTTP Controllers, Schemas, Dependencies)   │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                  Application Layer                      │
│   (Commands, Queries, Handlers - Use Case Orchestration)│
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                    Domain Layer                         │
│    (Entities, Value Objects, Events, Repositories)     │
│              [NO EXTERNAL DEPENDENCIES]                 │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                Infrastructure Layer                     │
│  (Repository Implementations, External Service Adapters)│
└─────────────────────────────────────────────────────────┘
```

### 2.3 DDD Design

**Aggregates:**

1. **Post Aggregate** (Root: Post)
   - Contains: Post entity, Comments (collection), Reactions (collection)
   - Consistency Boundary: All comments and reactions belong to a post
   - Invariants:
     - Cannot add comment if post is locked
     - Cannot modify post if author doesn't own it (unless admin/mod)
     - Cascading deletion: deleting post removes all comments/reactions

2. **Category Aggregate** (Root: Category)
   - Contains: Category entity only
   - Consistency Boundary: Category metadata
   - Invariants:
     - Name and slug must be unique within community
     - Cannot delete category with existing posts

3. **CommunityMember Aggregate** (Root: CommunityMember)
   - Contains: CommunityMember entity
   - Consistency Boundary: Member role and status
   - Invariants:
     - Cannot have multiple roles simultaneously
     - UserId must exist in Identity context

**Key Entities:**
- **Post**: Title, content, author, category, image URL, pinned status, locked status
- **Comment**: Content, author, parent (for threading), depth limit
- **Reaction**: Type (like only for MVP), author, target (post or comment)
- **Category**: Name, slug, emoji, description, display order
- **CommunityMember**: UserId, CommunityId, role, join date

**Value Objects:**
- **PostId, CommentId, ReactionId, CategoryId, CommunityId**: Strongly-typed UUIDs
- **PostTitle**: 1-200 characters, no HTML
- **PostContent**: 1-5000 characters, sanitized
- **CommentContent**: 1-2000 characters, sanitized
- **CategorySlug**: Lowercase alphanumeric + hyphens
- **MemberRole**: Enum (MEMBER, MODERATOR, ADMIN)

**Domain Events:**
- PostCreated, PostEdited, PostDeleted, PostPinned, PostUnpinned, PostLocked, PostUnlocked
- CommentAdded, CommentEdited, CommentDeleted
- PostLiked, PostUnliked, CommentLiked, CommentUnliked
- CategoryCreated, CategoryUpdated, CategoryDeleted

### 2.4 Integration Points

**Upstream (Dependencies):**
- **Identity Context**: UserId value object (shared kernel), JWT authentication, user profile data (display_name, avatar_url)
- **Redis**: Rate limiting counters
- **PostgreSQL**: Persistent storage

**Downstream (Consumers - Future):**
- **Gamification Context**: Listens to PostCreated, CommentAdded, PostLiked events to award points
- **Notification Context**: Listens to CommentAdded, PostLiked to send notifications

**Communication Pattern:**
- Identity → Community: Shared kernel (UserId value object)
- Community → Gamification/Notification: Asynchronous domain events via in-memory event bus
- No direct API calls between contexts

---

## 3. Technology Stack

### 3.1 Backend

**Core Framework:**
- **FastAPI** (existing) - High-performance async web framework
- **Pydantic v2** (existing) - Request/response validation

**New Dependencies:**

**bleach (^6.1.0)** - HTML sanitization
- **Purpose:** Prevent XSS attacks by sanitizing user-generated content (post/comment text)
- **Why:** Mozilla-maintained, battle-tested (10+ years), OWASP recommended
- **Alternatives considered:**
  - `html.escape()` - Too basic, doesn't handle nested tags or attributes
  - Custom regex - Security risk, reinventing the wheel
- **Research:** https://bleach.readthedocs.io/en/latest/

**Existing Dependencies (Reuse):**
- **SQLAlchemy 2.x** - ORM for database access
- **Alembic** - Database migrations
- **structlog** - Structured logging
- **python-jose** - JWT handling (from Identity context)

### 3.2 Frontend

**Core:**
- **React 18** (existing) - UI framework
- **TypeScript strict mode** (existing)
- **TanStack Query v5** (existing) - Server state management
- **React Router v6** (existing) - Client-side routing

**New Dependencies:**

**react-markdown (^9.0.0)** - Render user content safely
- **Purpose:** Display user content with safe, limited formatting
- **Why:** Widely used (20M+ downloads/month), supports custom renderers
- **Configuration:** Disable HTML, links only, no script execution
- **Alternatives:**
  - `DOMPurify` - Lower level, more manual work
  - Custom sanitizer - Security risk
- **Research:** https://github.com/remarkjs/react-markdown

**date-fns (^3.0.0)** - Date formatting
- **Purpose:** Format timestamps ("3h ago", "Jan 5, 2026")
- **Why:** Lightweight (13KB gzipped vs Moment's 67KB), immutable, tree-shakable
- **Alternatives:**
  - `dayjs` - Similar size, less type-safe
  - `luxon` - Larger bundle
- **Research:** https://date-fns.org/

**UI Components:**
- **TailwindCSS** (existing) - Utility-first CSS
- **Radix UI** (existing for modals/dropdowns) - Accessible primitives

### 3.3 Infrastructure

**Database:**
- **PostgreSQL 15+** (existing) - Primary data store
- **Indexes:** On foreign keys, search fields (category_id, created_at, like_count)
- **Constraints:** Unique indexes, foreign key cascades

**Cache:**
- **Redis 7+** (existing) - Rate limiting only (no feed caching in MVP)

**External Services:**
- **Image Hosting:** User-provided HTTPS URLs (no upload service in MVP)

### 3.4 Technology Justification Summary

**Why no caching layer for feed?**
- Premature optimization - start simple, measure first
- Feed is read-heavy but sorting changes with every interaction
- Complexity of cache invalidation not worth initial effort
- Can add later with Redis sorted sets if p95 latency > 1s

**Why plain text only?**
- Reduces XSS attack surface significantly
- Simpler validation and sanitization
- Markdown/rich text deferred to Phase 2

**Why cursor pagination?**
- More stable than offset pagination (no duplicate/missing items)
- Required for "Hot" algorithm (scoring changes over time)
- Better UX for infinite scroll

---

## 4. Data Model

### 4.1 Conceptual Schema

**Core Tables:**

**communities**
- `id` (UUID, PK) - Community identifier
- `name` (String) - Community name
- `created_at`, `updated_at` (Timestamp)
- **Note:** Simplified for MVP, full community management in Phase 2

**categories**
- `id` (UUID, PK)
- `community_id` (UUID, FK → communities)
- `name` (String, 1-50 chars) - Display name
- `slug` (String) - URL-safe identifier (unique per community)
- `emoji` (String) - Single emoji for visual identifier
- `description` (Text, nullable)
- `display_order` (Integer) - Sort order in sidebar
- `created_at`, `updated_at`
- **Unique constraint:** (community_id, name), (community_id, slug)

**community_members**
- `id` (UUID, PK)
- `community_id` (UUID, FK → communities)
- `user_id` (UUID, FK → users in Identity context)
- `role` (Enum: MEMBER, MODERATOR, ADMIN)
- `joined_at` (Timestamp)
- `is_active` (Boolean) - For soft-delete when user leaves
- **Unique constraint:** (community_id, user_id)
- **Index:** user_id, community_id

**posts**
- `id` (UUID, PK)
- `community_id` (UUID, FK → communities)
- `category_id` (UUID, FK → categories)
- `author_id` (UUID, FK → community_members)
- `title` (String, 1-200 chars)
- `content` (Text, 1-5000 chars)
- `image_url` (String, nullable, HTTPS only)
- `is_pinned` (Boolean, default false)
- `pinned_at` (Timestamp, nullable)
- `is_locked` (Boolean, default false)
- `is_deleted` (Boolean, default false) - Soft delete
- `deleted_at`, `deleted_by_id` (for audit)
- `created_at`, `updated_at`, `edited_at`
- **Indexes:**
  - (community_id, is_deleted, created_at DESC) - For "New" feed
  - (community_id, is_deleted, is_pinned, pinned_at DESC) - For pinned posts
  - (category_id, is_deleted) - For category filtering
  - (author_id) - For user activity

**comments**
- `id` (UUID, PK)
- `post_id` (UUID, FK → posts)
- `author_id` (UUID, FK → community_members)
- `parent_comment_id` (UUID, FK → comments, nullable)
- `content` (Text, 1-2000 chars)
- `depth` (Integer, 0 or 1) - Threading depth
- `is_deleted` (Boolean)
- `deleted_at`
- `created_at`, `updated_at`, `edited_at`
- **Indexes:**
  - (post_id, is_deleted, created_at) - For loading comments
  - (parent_comment_id) - For nested replies

**reactions**
- `id` (UUID, PK)
- `community_id` (UUID, FK → communities)
- `target_type` (Enum: POST, COMMENT)
- `target_id` (UUID) - post_id or comment_id
- `author_id` (UUID, FK → community_members)
- `reaction_type` (Enum: LIKE) - Only "like" for MVP
- `created_at`
- **Unique constraint:** (target_type, target_id, author_id) - One like per user per target
- **Indexes:**
  - (target_type, target_id) - For counting likes
  - (author_id) - For user activity

### 4.2 Denormalized Fields (Performance)

**posts table - Denormalized counters:**
- `comment_count` (Integer, default 0)
- `like_count` (Integer, default 0)
- `hot_score` (Float, nullable) - Precomputed for Hot sorting

**Why denormalize?**
- Eliminates COUNT(*) queries on large tables
- Hot sorting formula needs to run on every feed request
- Trade-off: Update complexity vs read performance
- Read-heavy workload (100:1 reads to writes)

**Update strategy:**
- Increment/decrement in same transaction as comment/reaction creation
- Recalculate hot_score periodically (background job, Phase 2)
- Accept eventual consistency for hot_score (recalc every 15 min)

### 4.3 Relationships

```
communities
    ├── categories (1:N)
    ├── community_members (1:N)
    └── posts (1:N)
            ├── comments (1:N)
            │     └── comments (1:N, max depth=1)
            └── reactions (1:N)

community_members
    ├── posts (1:N as author)
    ├── comments (1:N as author)
    └── reactions (1:N as author)
```

### 4.4 Indexes Strategy

**Primary Performance Indexes:**
1. `(community_id, is_deleted, created_at DESC)` - NEW feed sorting
2. `(community_id, is_deleted, like_count DESC, created_at DESC)` - TOP feed
3. `(community_id, is_deleted, hot_score DESC NULLS LAST)` - HOT feed
4. `(category_id, is_deleted)` - Category filtering

**Secondary Indexes:**
- Foreign keys (automatic in PostgreSQL with explicit FK)
- Unique constraints (category slug, reaction uniqueness)

**Index Size Considerations:**
- Each index adds ~30% to table size
- Monitor with `pg_relation_size()` after 10K posts
- Drop unused indexes after metrics collection

### 4.5 Migrations Plan

**Migration Sequence:**
1. Create `communities` table (minimal columns for MVP)
2. Create `categories` table with constraints
3. Create `community_members` table
4. Create `posts` table with all indexes
5. Create `comments` table with FK constraints
6. Create `reactions` table with unique constraint
7. Seed default categories (General, Q&A, Wins, Introductions)

**Rollback Strategy:**
- Each migration includes `downgrade()` function
- Data migrations separated from schema migrations
- Test rollback on staging before production

---

## 5. API Design

### 5.1 Endpoint Overview

**RESTful Resource Design:**

```
/api/communities/{community_id}/
  ├── posts/                    [POST, GET]
  │   ├── {post_id}             [GET, PATCH, DELETE]
  │   │   ├── comments/         [POST, GET]
  │   │   ├── like/             [POST, DELETE]
  │   │   ├── pin/              [POST, DELETE]
  │   │   └── lock/             [POST, DELETE]
  │   └── feed/                 [GET with query params]
  │
  ├── comments/
  │   └── {comment_id}          [GET, PATCH, DELETE]
  │       └── like/             [POST, DELETE]
  │
  └── categories/               [POST, GET]
      └── {category_id}         [GET, PATCH, DELETE]
```

**Design Principles:**
- Resource-oriented URLs (nouns, not verbs)
- Nested resources show ownership (post → comments)
- Consistent HTTP verbs (POST=create, PATCH=update, DELETE=delete)
- Idempotency: PUT/DELETE are idempotent, POST is not

### 5.2 Request/Response Contracts

**Create Post:**
```
POST /api/communities/{community_id}/posts

Request:
{
  "title": string (1-200 chars),
  "content": string (1-5000 chars),
  "category_id": uuid,
  "image_url": string | null (HTTPS only)
}

Response 201 Created:
{
  "id": uuid,
  "title": string,
  "content": string,
  "category": {
    "id": uuid,
    "name": string,
    "slug": string,
    "emoji": string
  },
  "author": {
    "id": uuid,
    "display_name": string,
    "avatar_url": string
  },
  "image_url": string | null,
  "like_count": 0,
  "comment_count": 0,
  "is_pinned": false,
  "is_locked": false,
  "created_at": timestamp,
  "updated_at": timestamp,
  "edited_at": timestamp | null
}
```

**Get Feed:**
```
GET /api/communities/{community_id}/posts/feed
  ?sort=hot|new|top
  &category_id={uuid}
  &limit=20
  &cursor={opaque_string}

Response 200:
{
  "posts": [
    {
      "id": uuid,
      "title": string,
      "content": string,  // Truncated to ~500 chars in list view
      "category": { ... },
      "author": { ... },
      "like_count": number,
      "comment_count": number,
      "is_pinned": boolean,
      "is_liked_by_me": boolean,
      "created_at": timestamp
    }
  ],
  "next_cursor": string | null,
  "has_more": boolean
}
```

**Add Comment:**
```
POST /api/communities/{community_id}/posts/{post_id}/comments

Request:
{
  "content": string (1-2000 chars),
  "parent_comment_id": uuid | null
}

Response 201 Created:
{
  "id": uuid,
  "content": string,
  "author": { ... },
  "parent_comment_id": uuid | null,
  "depth": 0 | 1,
  "like_count": 0,
  "is_liked_by_me": false,
  "created_at": timestamp,
  "edited_at": null
}
```

**Like Post:**
```
POST /api/communities/{community_id}/posts/{post_id}/like

Response 200 (idempotent):
{
  "liked": true,
  "like_count": number
}
```

### 5.3 Authentication & Authorization

**Authentication:**
- All endpoints require `Authorization: Bearer {jwt_token}` header
- JWT contains: `user_id`, `email`, `exp`
- Token validated by existing Identity context middleware
- 401 Unauthorized if token missing/expired

**Authorization:**
- Check `community_members` table for membership
- 403 Forbidden if not a member of the community
- Permission checks based on `MemberRole` enum

**Permission Matrix (enforced in domain layer):**
- Create post: MEMBER, MODERATOR, ADMIN
- Edit own post: MEMBER, MODERATOR, ADMIN
- Delete own post: MEMBER, MODERATOR, ADMIN
- Delete any post: MODERATOR, ADMIN
- Pin/unpin post: MODERATOR, ADMIN
- Lock/unlock post: MODERATOR, ADMIN
- Create category: ADMIN only
- Delete category: ADMIN only

### 5.4 Error Handling

**HTTP Status Codes:**
- `200 OK` - Success (GET, idempotent POST)
- `201 Created` - Resource created (POST)
- `204 No Content` - Success with no body (DELETE)
- `400 Bad Request` - Validation error
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Permission denied
- `404 Not Found` - Resource not found
- `409 Conflict` - Business rule violation (e.g., duplicate category name)
- `422 Unprocessable Entity` - Domain logic error
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Unexpected server error

**Error Response Format:**
```json
{
  "code": "DOMAIN_ERROR_CODE",
  "message": "Human-readable error message",
  "details": {  // Optional
    "field": "validation error"
  }
}
```

**Domain Error Codes:**
- `POST_NOT_FOUND` - Post doesn't exist or is deleted
- `CATEGORY_NOT_FOUND` - Category doesn't exist
- `POST_LOCKED` - Cannot comment on locked post
- `PERMISSION_DENIED` - User lacks required role
- `RATE_LIMIT_EXCEEDED` - Too many requests
- `MAX_DEPTH_EXCEEDED` - Cannot reply to a reply
- `CATEGORY_HAS_POSTS` - Cannot delete non-empty category
- `INVALID_IMAGE_URL` - Image URL must use HTTPS

### 5.5 Versioning Strategy

**Current:** No API versioning (MVP)

**Future (Phase 2+):**
- URL versioning: `/api/v2/communities/...`
- Maintain v1 for 6 months after v2 release
- Deprecation warnings in response headers: `X-API-Deprecated: true`

---

## 6. Domain Model

### 6.1 Aggregates (Deep Dive)

**Post Aggregate Root:**

The Post aggregate is the primary consistency boundary. It owns Comments and Reactions.

**Responsibilities:**
- Enforce post validation (title/content length, image HTTPS)
- Manage pinned/locked status (admin/mod only)
- Track edit history (edited_at timestamp)
- Control commenting permissions (locked posts reject comments)
- Calculate hot score for feed sorting

**Invariants:**
- Title: 1-200 characters, no HTML tags
- Content: 1-5000 characters, sanitized HTML
- Image URL: Must be HTTPS if provided
- Cannot modify if `is_deleted = true`
- Cannot add comments if `is_locked = true`
- Pinned posts limited to 5 per community (enforced at application layer)

**State Transitions:**
```
[Created] → [Edited] → [Deleted]
            ↓
         [Pinned] → [Unpinned]
            ↓
         [Locked] → [Unlocked]
```

**Comment Entity (within Post aggregate):**

**Responsibilities:**
- Enforce comment length (1-2000 chars)
- Manage threading depth (max 1 level)
- Handle soft deletion with "[deleted]" placeholder

**Invariants:**
- Content required (not empty)
- If `parent_comment_id` is set, parent must exist and have `depth = 0`
- If `depth = 1`, cannot have child comments
- Cannot modify if `is_deleted = true`

**Soft Delete Logic:**
- If comment has replies: content → "[deleted]", keep in database
- If no replies: full deletion from database
- Cascade: Delete all reactions when comment deleted

**Reaction Entity (within Post aggregate):**

**Responsibilities:**
- Track who liked what
- Enforce one like per user per target (idempotency)

**Invariants:**
- Unique (author_id, target_type, target_id)
- Cannot like deleted posts/comments

### 6.2 Value Objects

**PostTitle:**
- **Validation:** 1-200 characters, no HTML tags
- **Sanitization:** Strip leading/trailing whitespace, collapse multiple spaces
- **Immutable:** Once created, cannot be modified in place
- **Design Decision:** Separate value object vs plain string → enforces validation at construction

**PostContent / CommentContent:**
- **Validation:** Length limits (5000 for posts, 2000 for comments)
- **Sanitization:** Use bleach to strip dangerous HTML
- **Allowed tags:** None for MVP (plain text only)
- **Design Decision:** Sanitize at value object creation, not at API layer, so domain is always safe

**CategorySlug:**
- **Validation:** Lowercase letters, numbers, hyphens only
- **Generation:** Auto-generate from name (`"Q&A" → "qa"`)
- **Uniqueness:** Must be unique within community (enforced by unique constraint)

**MemberRole (Enum):**
- **Values:** MEMBER, MODERATOR, ADMIN
- **Design Decision:** Single role per member (not role collection) for simplicity
- **Hierarchy:** ADMIN > MODERATOR > MEMBER (for permission checks)

### 6.3 Domain Events

**Naming Convention:** PastTense verb + Entity name

**PostCreated:**
```python
@dataclass(frozen=True)
class PostCreated(DomainEvent):
    post_id: PostId
    community_id: CommunityId
    author_id: UserId
    category_id: CategoryId
    occurred_at: datetime
```

**CommentAdded:**
```python
@dataclass(frozen=True)
class CommentAdded(DomainEvent):
    comment_id: CommentId
    post_id: PostId
    author_id: UserId
    parent_comment_id: CommentId | None
    occurred_at: datetime
```

**PostLiked / CommentLiked:**
```python
@dataclass(frozen=True)
class PostLiked(DomainEvent):
    post_id: PostId
    author_id: UserId  # Who liked it
    occurred_at: datetime
```

**Event Purpose:**
- **Audit trail:** Track what happened and when
- **Analytics:** Feed to data warehouse for metrics
- **Gamification:** Award points when events fire
- **Notifications:** Trigger email/push when user's content is liked
- **Cache invalidation:** Bust feed cache when new post created (future)

### 6.4 Design Patterns

**Repository Pattern:**
- Domain defines interfaces (`IPostRepository`, `ICategoryRepository`)
- Infrastructure implements with SQLAlchemy
- Hides persistence details from domain layer
- Allows in-memory repositories for unit testing

**Factory Pattern:**
- `Post.create()` factory method validates and constructs Post
- Centralizes business rules (default values, initial state)
- Alternative: Constructor - rejected because too many parameters

**Strategy Pattern (Feed Sorting):**
- `IFeedSortStrategy` interface with implementations: `HotSort`, `NewSort`, `TopSort`
- Selected based on user preference (query param)
- **Design Decision:** Strategy vs if/else → enables easier testing and future sort algorithms

**Specification Pattern (Authorization):**
- `CanDeletePostSpec(member, post)` → returns bool
- Encapsulates complex permission logic
- Reusable across commands (delete, edit)
- **Alternative:** Inline if statements - rejected due to duplication

---

## 7. Application Layer

### 7.1 Commands

**Command:** A user intent to change system state.

**CreatePostCommand:**
```python
@dataclass(frozen=True)
class CreatePostCommand:
    community_id: UUID
    author_user_id: UUID  # From JWT
    title: str
    content: str
    category_id: UUID
    image_url: str | None
```

**DeletePostCommand:**
```python
@dataclass(frozen=True)
class DeletePostCommand:
    post_id: UUID
    requesting_user_id: UUID
    community_id: UUID
```

**LikePostCommand:**
```python
@dataclass(frozen=True)
class LikePostCommand:
    post_id: UUID
    author_user_id: UUID
    community_id: UUID
```

**Design Decision - Commands are immutable:**
- Ensures command cannot be modified during handling
- Easier to log and replay for debugging
- Prevents accidental mutation bugs

### 7.2 Queries

**Query:** A request for information (read-only, no side effects).

**GetFeedQuery:**
```python
@dataclass(frozen=True)
class GetFeedQuery:
    community_id: UUID
    requesting_user_id: UUID
    sort: FeedSort  # Enum: HOT, NEW, TOP
    category_id: UUID | None
    limit: int = 20
    cursor: str | None = None
```

**GetPostDetailsQuery:**
```python
@dataclass(frozen=True)
class GetPostDetailsQuery:
    post_id: UUID
    requesting_user_id: UUID
    community_id: UUID
```

**Design Decision - CQRS Lite:**
- Separate read and write models (commands vs queries)
- Queries can bypass domain layer and read directly from database (future optimization)
- Commands always go through domain layer
- No event sourcing (full CQRS) - too complex for MVP

### 7.3 Use Case Flow (Example: Create Post)

**High-level orchestration:**

1. **Validate Input:** API layer validates request schema (Pydantic)
2. **Check Rate Limit:** Infrastructure checks Redis (10 posts/hour)
3. **Check Authorization:** Verify user is community member
4. **Validate Category Exists:** Query repository
5. **Create Domain Entity:** `Post.create(title, content, ...)`
6. **Persist to Database:** `post_repository.save(post)`
7. **Publish Domain Events:** `event_bus.publish_all(post.clear_events())`
8. **Return Response:** Map Post entity to PostResponse DTO

**Error Handling:**
- Validation errors: Return 400 Bad Request
- Rate limit exceeded: Return 429 Too Many Requests
- Authorization failures: Return 403 Forbidden
- Database errors: Log and return 500 Internal Server Error

### 7.4 Event Handling

**Event Flow:**

```
Domain Layer                Application Layer           External Contexts
    │                            │                              │
    ├─ post.create()             │                              │
    ├─ post._add_event(PostCreated)                             │
    │                            │                              │
    ├─ repository.save(post)     │                              │
    │                            │                              │
    │  ┌─────────────────────────▼───────────────┐              │
    │  │ Handler: await event_bus.publish_all()  │              │
    │  └─────────────────────────┬───────────────┘              │
    │                            │                              │
    │                            ├─ Event: PostCreated          │
    │                            │                              │
    │                            ├──────────────────────────────▶ Gamification
    │                            │      (awards points)          │
    │                            │                              │
    │                            ├──────────────────────────────▶ Analytics
    │                            │      (tracks metric)          │
    │                            │                              │
```

**In-Process Event Bus (MVP):**
- Simple, synchronous event dispatch
- Handlers registered at startup
- All handlers must complete before response returned
- **Trade-off:** Simplicity vs eventual consistency

**Future (Phase 2):**
- Async message queue (Redis Pub/Sub, RabbitMQ)
- Retry logic for failed handlers
- Outbox pattern for reliable event publishing

---

## 8. Integration Strategy

### 8.1 Cross-Context Communication

**Identity Context Integration:**

**Type:** Shared Kernel (UserId value object)

```python
# Shared in both contexts
from src.identity.domain.value_objects import UserId

# Community uses it
@dataclass
class Post:
    author_id: UserId  # Strongly typed ID from Identity context
```

**User Profile Data (Read-Only):**
- Community needs: display_name, avatar_url, level badge (future)
- **Pattern:** Anti-Corruption Layer
- **Implementation:** `IUserProfileService` interface in Community domain
- **Infrastructure:** HTTP client or shared database read (decision deferred)

```python
# Domain interface
class IUserProfileService(Protocol):
    async def get_profile(self, user_id: UserId) -> UserProfileDTO:
        ...

# Application layer
class GetPostDetailsHandler:
    async def handle(self, query: GetPostDetailsQuery) -> PostDetailsDTO:
        post = await self._post_repository.get(query.post_id)
        author_profile = await self._user_profile_service.get_profile(post.author_id)
        return PostDetailsDTO(
            post=post,
            author=author_profile,
            ...
        )
```

### 8.2 External Services

**Email Service (Future - Notifications):**
- Interface: `IEmailService` (defined in domain layer)
- Implementation: `MailHogEmailService` (dev), `SendGridEmailService` (prod)
- **Anti-Corruption Layer:** Translate domain events → email templates

**Image Validation (MVP):**
- No external service, just URL validation (HTTPS schema check)
- Future: Integrate with image proxy to validate URL accessibility

### 8.3 Failure Modes

**Database Unavailable:**
- **Detection:** SQLAlchemy raises `OperationalError`
- **Handling:** Return 503 Service Unavailable, log error
- **Retry:** No automatic retry (avoid thundering herd)
- **User Impact:** Cannot create/view posts, show error message

**Redis Unavailable (Rate Limiting):**
- **Detection:** Redis connection timeout
- **Handling:** Fail open (allow request) or fail closed (reject)?
- **Decision:** Fail open for MVP (UX > abuse risk in small community)
- **Logging:** Alert on Redis failures

**Event Bus Handler Failure:**
- **Detection:** Handler raises exception
- **Handling:** Log error, do NOT fail the main request
- **Trade-off:** Risk of lost events vs user experience
- **Mitigation:** Implement outbox pattern in Phase 2

---

## 9. Security Design

### 9.1 Authentication

**JWT Token Validation:**
- Reuse existing Identity context middleware
- Token contains: `user_id`, `email`, `exp`, `is_verified`
- Validates signature with secret key
- Checks expiration timestamp
- Returns 401 if invalid/expired

**Token Refresh:**
- Handled by Identity context
- Community endpoints do NOT refresh tokens
- Frontend responsibility to refresh before expiration

### 9.2 Authorization

**Two-Level Checks:**

1. **Community Membership:**
   - Before ANY operation: verify user is member of community
   - Query: `SELECT * FROM community_members WHERE community_id = ? AND user_id = ?`
   - Cache membership check for 5 minutes (future optimization)

2. **Role-Based Permissions:**
   - Check `member.role` against required permission
   - Implemented as domain specifications: `CanDeletePostSpec`, `CanPinPostSpec`

**Example - Delete Post Authorization:**

```python
class CanDeletePostSpec:
    def is_satisfied_by(self, member: CommunityMember, post: Post) -> bool:
        # Own post: any role can delete
        if post.author_id == member.user_id:
            return True
        # Others' posts: only MODERATOR or ADMIN
        return member.role in [MemberRole.MODERATOR, MemberRole.ADMIN]
```

### 9.3 Input Validation

**Validation Layers:**

1. **API Layer (Pydantic schemas):**
   - Type checking (string, int, UUID)
   - Length limits (title max 200, content max 5000)
   - Format validation (email, URL)
   - Required vs optional fields

2. **Domain Layer (Value objects):**
   - Business rule validation
   - HTML sanitization (bleach library)
   - Cross-field validation (e.g., reply depth check)

**Sanitization Strategy:**

```python
import bleach

# In PostContent value object
@dataclass(frozen=True)
class PostContent:
    value: str

    def __post_init__(self):
        # Strip all HTML tags for MVP
        sanitized = bleach.clean(
            self.value,
            tags=[],  # No tags allowed
            strip=True
        )
        # Validation after sanitization
        if not (1 <= len(sanitized) <= 5000):
            raise ValueError("Content must be 1-5000 characters")
        # Use object.__setattr__ because frozen=True
        object.__setattr__(self, 'value', sanitized)
```

**Why sanitize in value object?**
- Domain entities always contain safe data
- Cannot accidentally render unsanitized content
- Single point of sanitization (DRY)

### 9.4 Data Protection

**Soft Delete:**
- Posts: `is_deleted = true`, preserve for audit
- Comments with replies: content → "[deleted]", preserve structure
- Reactions: hard delete (no audit requirement)

**Hard Delete (GDPR Compliance):**
- Admin endpoint: `DELETE /api/admin/users/{user_id}/data`
- Removes all content by user
- Future requirement, not in MVP

**SQL Injection Prevention:**
- SQLAlchemy ORM with parameterized queries
- Never use string concatenation for SQL
- Input validation at API layer

**CSRF Protection:**
- Not required for stateless JWT API
- Frontend uses JWT stored in memory or httpOnly cookie (user choice)

### 9.5 Threat Model

**Threats Addressed:**

1. **XSS (Cross-Site Scripting):**
   - **Attack:** User posts `<script>alert('XSS')</script>` in content
   - **Defense:** bleach sanitization, CSP headers
   - **Severity:** High

2. **IDOR (Insecure Direct Object Reference):**
   - **Attack:** User modifies post_id in DELETE request to delete others' posts
   - **Defense:** Authorization checks before every operation
   - **Severity:** High

3. **Rate Limit Bypass:**
   - **Attack:** Attacker spams post creation with different IPs
   - **Defense:** User-based rate limiting (keyed by user_id, not IP)
   - **Severity:** Medium

4. **Enumeration Attack:**
   - **Attack:** Attacker checks which user IDs exist by trying to view profiles
   - **Defense:** All users in a community can view each other (no leak)
   - **Severity:** Low

**Threats NOT Addressed (Future):**
- DDoS attacks: Requires infrastructure-level solution (Cloudflare, WAF)
- Content-based spam detection: Requires ML model
- Phishing links in content: Requires URL reputation check

---

## 10. Performance & Scalability

### 10.1 Performance Targets

| Operation | Target Latency (p95) | Rationale |
|-----------|---------------------|-----------|
| Get Feed (20 posts) | < 500ms | Critical path, users expect instant |
| Create Post | < 300ms | Write tolerance higher |
| Add Comment | < 200ms | Faster feedback expected |
| Like/Unlike | < 100ms | Perceived as instant action |

### 10.2 Caching Strategy

**MVP (No Caching):**
- Direct database queries for all reads
- Reason: Premature optimization, measure first
- Feed is dynamic (scoring changes with every interaction)

**Phase 2 (Selective Caching):**

**What to Cache:**
- User profile data (display_name, avatar_url) - 5 minute TTL
- Category list (rarely changes) - 1 hour TTL
- Feed results (first page only, hot sort) - 1 minute TTL

**Cache Invalidation:**
- PostCreated event: Invalidate feed cache
- CategoryUpdated event: Invalidate category cache
- Profile updated: Invalidate user profile cache

**Technology:**
- Redis with key pattern: `feed:{community_id}:{sort}:{category?}`
- LRU eviction policy

### 10.3 Query Optimization

**Feed Query (Most Critical):**

**Hot Sort Algorithm:**
```sql
SELECT p.*
FROM posts p
WHERE p.community_id = ?
  AND p.is_deleted = false
ORDER BY
  p.is_pinned DESC,
  p.hot_score DESC NULLS LAST,
  p.created_at DESC
LIMIT 20
OFFSET ?;
```

**Index Used:** `(community_id, is_deleted, is_pinned, hot_score DESC, created_at DESC)`

**Hot Score Calculation:**
```python
hot_score = (like_count + comment_count * 2) / (hours_since_created + 2) ^ 1.5
```

- Computed at post creation
- Recomputed periodically (background job, every 15 minutes)
- Stored in `posts.hot_score` column

**Cursor Pagination (Not Offset):**
- Cursor encodes: `last_post_id` + `last_score` + `last_created_at`
- Next page query: `WHERE (hot_score, created_at, id) < (?, ?, ?)`
- **Benefit:** Stable pagination (no duplicates/skips when new posts added)

**Comment Loading (N+1 Problem):**

**Anti-pattern:**
```python
# BAD: N+1 queries
post = await post_repository.get(post_id)
for comment in post.comments:
    comment.author = await user_service.get_profile(comment.author_id)  # N queries
```

**Solution:**
```python
# GOOD: Batch fetch
comments = await comment_repository.get_by_post(post_id)
author_ids = [c.author_id for c in comments]
authors = await user_service.get_profiles_batch(author_ids)  # 1 query
author_map = {a.id: a for a in authors}
for comment in comments:
    comment.author = author_map[comment.author_id]
```

### 10.4 Scalability Considerations

**Current Bottleneck Analysis:**

**Database:**
- Single PostgreSQL instance (MVP)
- Horizontal scaling: Read replicas for feed queries
- Vertical scaling: Increase instance size up to 32 CPU / 128GB RAM
- **Limit:** ~10,000 concurrent users before read replicas needed

**Application:**
- Stateless FastAPI servers (easy horizontal scaling)
- No in-memory state (event bus is in-process but async handlers tolerate failures)
- **Limit:** ~100 req/sec per instance, scale to 10+ instances

**Rate Limiter (Redis):**
- Single Redis instance
- Redis can handle 100K ops/sec
- **Limit:** Not a bottleneck until 1M+ users

**Future Scaling (Phase 3 - 100K+ users):**
- **Database:** Partition by community_id (sharding)
- **Caching:** Redis Cluster for distributed cache
- **CDN:** Serve static assets, image proxying
- **Search:** Elasticsearch for full-text post search

---

## 11. Error Handling

### 11.1 Error Taxonomy

**Domain Exceptions (422 Unprocessable Entity):**
- `PostNotFoundException` - Post doesn't exist or is deleted
- `PostLockedException` - Cannot comment on locked post
- `CategoryNotFoundException` - Invalid category_id
- `MaxDepthExceededError` - Cannot reply to a reply
- `CategoryHasPostsError` - Cannot delete non-empty category

**Authorization Exceptions (403 Forbidden):**
- `PermissionDeniedError` - User lacks required role
- `NotCommunityMemberError` - User not a member of community

**Validation Exceptions (400 Bad Request):**
- `InvalidInputError` - Pydantic validation failed
- `InvalidImageUrlError` - Image URL not HTTPS

**Infrastructure Exceptions (500 Internal Server Error):**
- `DatabaseError` - SQLAlchemy OperationalError
- `ExternalServiceError` - Redis, email service failure

### 11.2 HTTP Mapping

```python
# In API controller
try:
    result = await handler.handle(command)
    return result
except PostNotFoundException as e:
    raise HTTPException(status_code=404, detail=e.message)
except PermissionDeniedError as e:
    raise HTTPException(status_code=403, detail=e.message)
except PostLockedException as e:
    raise HTTPException(status_code=422, detail=e.message)
except InvalidInputError as e:
    raise HTTPException(status_code=400, detail=e.message)
except Exception as e:
    logger.error("Unexpected error", exc_info=True)
    raise HTTPException(status_code=500, detail="Internal server error")
```

### 11.3 User Feedback

**Error Message Guidelines:**
- Be specific but not leaky (no SQL errors to user)
- Actionable when possible ("Post is locked. Comments are disabled.")
- Consistent tone (not "Oops!", professional)

**Examples:**

| Error | User Message |
|-------|-------------|
| PostNotFoundException | "This post has been deleted or doesn't exist." |
| PermissionDeniedError | "You don't have permission to delete this post." |
| PostLockedException | "Comments are disabled on this post." |
| RateLimitExceeded | "You've reached the post limit. Try again in 15 minutes." |
| InvalidImageUrlError | "Image URL must use HTTPS." |

---

## 12. Testing Strategy

### 12.1 BDD Tests (Behavior-Driven Development)

**Coverage:** All user-facing scenarios from `feed.feature`

**Test Environment:**
- Real PostgreSQL database (`koulu_test`)
- Real Redis instance (or mock for BDD)
- Mocked email service
- Mocked time (for rate limiting tests)

**Key Scenarios:**
- Post creation with validation errors
- Comment threading (max depth enforcement)
- Role-based authorization (member vs admin)
- Feed sorting algorithms (Hot, New, Top)
- Cascading deletion (post → comments → reactions)
- Rate limiting (10 posts/hour)

**Test Data Fixtures:**
- Use domain layer to create test data (NOT direct DB inserts)
- Ensures domain logic is exercised in tests

### 12.2 Unit Tests (Domain Logic)

**What to Unit Test:**
- Value objects: PostTitle, PostContent validation
- Entities: Post.create(), Comment.reply()
- Specifications: CanDeletePostSpec, CanPinPostSpec
- Domain services: FeedSortStrategy implementations

**Example - Post Entity Unit Test:**
```python
def test_post_lock_prevents_comments():
    post = Post.create(title="Test", content="Test", ...)
    post.lock()

    with pytest.raises(PostLockedException):
        post.add_comment(author_id=user_id, content="Comment")
```

**Example - Value Object Unit Test:**
```python
def test_post_title_rejects_html():
    with pytest.raises(ValueError):
        PostTitle("<script>alert('xss')</script>")
```

**Mock Strategy:**
- Mock repositories (in-memory implementation)
- Mock external services (IUserProfileService)
- Do NOT mock domain entities (test the real thing)

### 12.3 Integration Tests

**API Integration Tests:**
- Full request → response cycle
- Real database (test DB)
- Real authentication (JWT tokens)
- Test error handling (401, 403, 404)

**Repository Integration Tests:**
- Test SQLAlchemy repository implementations
- Verify cascading deletes work
- Test unique constraints (category slug)

---

## 13. Observability

### 13.1 Logging

**Structured Logging (structlog):**

```python
logger.info(
    "post_created",
    post_id=str(post.id),
    community_id=str(community_id),
    author_id=str(author_id),
    category_id=str(category_id),
)
```

**Log Levels:**
- `DEBUG`: SQL queries, cache hits/misses
- `INFO`: Business events (post created, user liked)
- `WARNING`: Validation failures, rate limit hits
- `ERROR`: Exceptions, failed database queries

**Sensitive Data:**
- Never log: passwords, tokens, full email addresses
- Hash user IDs in logs for privacy (future)

### 13.2 Metrics

**Key Metrics (Future - Prometheus):**

**Business Metrics:**
- `posts_created_total` (counter, label: community_id)
- `comments_added_total` (counter)
- `likes_total` (counter, label: target_type)

**Technical Metrics:**
- `http_request_duration_seconds` (histogram, label: endpoint)
- `database_query_duration_seconds` (histogram)
- `rate_limit_rejections_total` (counter)

**Alerting Thresholds:**
- Error rate > 1% for 5 minutes
- p95 latency > 1 second for feed endpoint
- Database connection pool exhaustion

### 13.3 Tracing

**OpenTelemetry Integration (Future):**

**Trace Spans:**
- HTTP request span (root)
  - Command handler span
    - Repository query span
    - Event publishing span

**Trace Context Propagation:**
- Inject trace_id into logs
- Correlate logs with traces in observability tool (Jaeger, DataDog)

---

## 14. Deployment Strategy

### 14.1 Migration Plan

**Database Migrations (Alembic):**

1. Run migrations on staging environment
2. Verify with test data (100K posts, 1M comments)
3. Backup production database
4. Run migrations on production during low-traffic window
5. Monitor for errors (slow queries, lock timeouts)

**Rollback Plan:**
- Alembic downgrade scripts for all migrations
- Keep old application version deployed for 24 hours (blue-green)
- If critical bug: Revert database migration, deploy old code

### 14.2 Feature Flags

**Not Implemented in MVP** (Future: LaunchDarkly, Unleash)

**Candidates for Feature Flags:**
- Hot sorting algorithm (easy to disable if performance issues)
- New feed sorting options (A/B test)
- Rate limit thresholds (adjust without code deploy)

### 14.3 Deployment Sequence

**Backend Deployment:**
1. Run database migrations (if any)
2. Deploy new backend instances (rolling update)
3. Health check: GET /health endpoint returns 200
4. Gradually shift traffic (10% → 50% → 100%)
5. Monitor error logs and latency metrics

**Frontend Deployment:**
1. Build production bundle (Vite)
2. Upload to CDN (or serve from backend)
3. Update version in HTML (cache bust)
4. No downtime (static files, instant switchover)

---

## 15. Future Considerations

### 15.1 Phase 2 Enhancements

**Rich Text Editor:**
- Markdown support (bold, italic, lists, links)
- Library: Tiptap or Lexical
- Security: Whitelist allowed tags, sanitize with DOMPurify
- **Why deferred:** Increases XSS risk, needs thorough security review

**Search Functionality:**
- Full-text search on post titles and content
- Technology: PostgreSQL `tsvector` (simple) or Elasticsearch (advanced)
- Ranking: Relevance score, recency boost
- **Why deferred:** Adds index complexity, low MVP priority

**Notification System:**
- In-app notifications (bell icon)
- Email notifications (configurable per event type)
- Push notifications (web push API)
- **Why deferred:** Requires new bounded context, significant scope

**Advanced Moderation:**
- Report post/comment (flag for review)
- Ban user from community
- Auto-moderation rules (keyword filters)
- Audit log UI for admins
- **Why deferred:** Low abuse risk in small communities

### 15.2 Known Limitations

**No Real-Time Updates:**
- Feed requires manual refresh to see new posts
- **Workaround:** Polling every 30 seconds (future: WebSocket)

**No Post Drafts:**
- Users cannot save partial posts
- **Workaround:** Frontend localStorage (not synced)

**Simplistic Hot Algorithm:**
- Doesn't account for post age decay
- **Workaround:** Periodic recalculation (every 15 min)

**No Content Moderation:**
- Admins must manually find/delete bad content
- **Workaround:** Rely on small community size, future reporting

### 15.3 Technical Debt

**In-Process Event Bus:**
- **Debt:** Not fault-tolerant, blocks request until handlers complete
- **Future:** Message queue (RabbitMQ, Redis Streams)
- **Timeline:** When event volume > 1000/minute

**No Database Read Replicas:**
- **Debt:** All reads hit primary database
- **Future:** Add read replicas for feed queries
- **Timeline:** When p95 latency > 500ms

**Offset Pagination (if used):**
- **Debt:** Unstable (duplicates/skips on concurrent writes)
- **Future:** Cursor pagination for all endpoints
- **Timeline:** Immediate (use cursor from start)

---

## 16. Alignment Verification

See `docs/features/community/ALIGNMENT_VERIFICATION.md` for detailed traceability matrix mapping:
- PRD User Stories → BDD Scenarios
- BDD Scenarios → API Endpoints
- API Endpoints → Domain Logic
- Domain Logic → Test Coverage

**Summary:**
- All 34 user stories from PRD covered by 56 BDD scenarios
- All business rules mapped to domain invariants
- All edge cases addressed with explicit handling
- Authorization matrix fully implemented in domain specifications

---

## 17. Appendices

### 17.1 File Checklist

**New Directories:**
```
src/community/
├── domain/
│   ├── entities/
│   ├── value_objects/
│   ├── events/
│   ├── repositories/
│   ├── services/
│   └── exceptions.py
├── application/
│   ├── commands/
│   ├── queries/
│   └── handlers/
├── infrastructure/
│   ├── persistence/
│   │   ├── models.py
│   │   ├── post_repository.py
│   │   ├── category_repository.py
│   │   └── member_repository.py
│   └── services/
│       └── feed_sort_strategy.py
└── interface/
    └── api/
        ├── controllers/
        │   ├── post_controller.py
        │   ├── comment_controller.py
        │   └── category_controller.py
        ├── schemas.py
        └── dependencies.py
```

**Database Migrations:**
```
migrations/versions/
├── XXXX_create_communities_table.py
├── XXXX_create_categories_table.py
├── XXXX_create_community_members_table.py
├── XXXX_create_posts_table.py
├── XXXX_create_comments_table.py
├── XXXX_create_reactions_table.py
└── XXXX_seed_default_categories.py
```

**Frontend Files:**
```
frontend/src/features/community/
├── api/
│   ├── postApi.ts
│   ├── commentApi.ts
│   └── categoryApi.ts
├── components/
│   ├── FeedView.tsx
│   ├── PostCard.tsx
│   ├── PostDetail.tsx
│   ├── CommentList.tsx
│   ├── CommentForm.tsx
│   ├── CreatePostModal.tsx
│   └── CategorySidebar.tsx
├── hooks/
│   ├── useFeed.ts
│   ├── useCreatePost.ts
│   ├── useLikePost.ts
│   └── useComments.ts
└── types/
    └── community.ts
```

### 17.2 Dependencies

**Python (pyproject.toml):**
```toml
[tool.poetry.dependencies]
bleach = "^6.1.0"  # NEW - HTML sanitization
# Existing dependencies reused:
# fastapi, sqlalchemy, alembic, structlog, redis, etc.
```

**Frontend (package.json):**
```json
{
  "dependencies": {
    "react-markdown": "^9.0.0",
    "date-fns": "^3.0.0"
  }
}
```

### 17.3 References

**Domain-Driven Design:**
- Evans, Eric. "Domain-Driven Design: Tackling Complexity in the Heart of Software" (2003)
- Vernon, Vaughn. "Implementing Domain-Driven Design" (2013)

**Security:**
- OWASP Top 10: https://owasp.org/www-project-top-ten/
- Bleach Documentation: https://bleach.readthedocs.io/en/latest/
- Content Security Policy: https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP

**API Design:**
- RESTful API Design: https://restfulapi.net/
- Cursor Pagination: https://jsonapi.org/profiles/ethanresnick/cursor-pagination/

**Feed Algorithms:**
- Reddit Hot Ranking: https://medium.com/hacking-and-gonzo/how-reddit-ranking-algorithms-work-ef111e33d0d9
- Hacker News Ranking: http://www.righto.com/2013/11/how-hacker-news-ranking-really-works.html

**Libraries:**
- FastAPI: https://fastapi.tiangolo.com/
- SQLAlchemy: https://docs.sqlalchemy.org/
- React Query: https://tanstack.com/query/latest
- React Markdown: https://github.com/remarkjs/react-markdown
- date-fns: https://date-fns.org/

---

## Approval

**Product Owner:** _________________
**Engineering Lead:** _________________
**Architecture Review:** _________________

**Status:** Draft - Ready for Review
**Next Steps:** Implementation via `/implement-feature community/feed`
