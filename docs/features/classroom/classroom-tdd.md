# Classroom - Technical Design Document

**Version:** 1.0
**Date:** February 7, 2026
**Status:** Draft
**Related PRD:** `classroom-prd.md`
**Related BDD:** `tests/features/classroom/classroom.feature`
**Bounded Context:** Classroom

---

## 1. Overview

### 1.1 Summary

The Classroom system enables structured learning through courses composed of modules and lessons. Admins create and organize content (text and embedded video), while members consume content, track progress, and navigate flexibly through materials. The architecture supports course discovery, non-linear learning paths, and comprehensive progress tracking across lesson, module, and course levels.

### 1.2 Goals

**Primary:**
- Implement complete course management (CRUD operations for courses, modules, lessons)
- Support two content types: rich text lessons and embedded video lessons (YouTube, Vimeo, Loom)
- Enable flexible navigation (Previous/Next across modules, Continue to next incomplete)
- Track member progress with completion percentages at all levels (lesson, module, course)
- Enforce role-based permissions (members consume, admins manage)
- Provide drag-and-drop reordering for modules and lessons
- Use soft deletion for courses, modules, and lessons (preserve progress)

**Secondary:**
- Lay foundation for gamification integration (publish completion events)
- Design for future notification system
- Prepare for future Map feature (instructor profiles)

### 1.3 Non-Goals

**Not in this implementation:**
- Native video/file upload (URLs only for MVP)
- PDF/document attachments
- Quiz/assessment lessons
- Certificates on completion
- Lesson prerequisites or locking
- Drip content (scheduled release)
- Discussion threads per lesson
- Downloadable resources
- Video transcripts/captions
- Automatic progress tracking (watch time)
- Course search/filtering
- Course ratings/reviews
- Draft mode (unpublished courses)

---

## 2. Architecture

### 2.1 System Context Diagram

```
┌─────────────────────────────────────────────────────────┐
│                   External Systems                      │
├─────────────────────────────────────────────────────────┤
│  PostgreSQL  │  Redis  │  YouTube/Vimeo/Loom  │ Frontend│
└────────┬─────┴────┬────┴──────────┬──────────┴────┬────┘
         │          │               │               │
         │          │               │               │
┌────────▼──────────▼───────────────▼───────────────▼─────┐
│                  Classroom Context                      │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────────┐   ┌─────────────────┐            │
│  │     Domain      │   │   Application   │            │
│  │                 │   │                 │            │
│  │ • Course        │   │ • CreateCourse  │            │
│  │ • Module        │   │ • AddModule     │            │
│  │ • Lesson        │   │ • AddLesson     │            │
│  │ • Progress      │   │ • MarkComplete  │            │
│  │ • ContentTypes  │   │ • GetFeed       │            │
│  └─────────────────┘   └─────────────────┘            │
│                                                         │
│  ┌─────────────────┐   ┌─────────────────┐            │
│  │ Infrastructure  │   │   Interface     │            │
│  │                 │   │                 │            │
│  │ • Repositories  │   │ • REST API      │            │
│  │ • RateLimiter   │   │ • Controllers   │            │
│  │ • EventBus      │   │ • Schemas       │            │
│  └─────────────────┘   └─────────────────┘            │
└─────────────────────────────────────────────────────────┘
         │             │           │
         ▼             ▼           ▼
┌────────────────────────────────────────────┐
│          Future Bounded Contexts           │
├────────────────────────────────────────────┤
│  Gamification │  Notification │   Map      │
│  (Phase 2)    │  (Phase 2)    │  (Phase 2) │
└────────────────────────────────────────────┘
```

**Key Architectural Principles:**
- Course is Aggregate Root containing Modules and Lessons
- Progress is separate Aggregate (member-specific, independent lifecycle)
- Cross-context communication via domain events only
- Video providers accessed via iframe embedding (no API integration)
- No direct database joins across contexts

### 2.2 Component Architecture

**Hexagonal Architecture Layers:**

```
┌─────────────────────────────────────────────────────────┐
│                    Interface Layer                      │
│  (Controllers: CourseController, ProgressController)   │
│  Admin Endpoints: POST/PUT/DELETE courses/modules/lessons│
│  Member Endpoints: GET courses, GET lessons, PATCH progress│
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                  Application Layer                      │
│   Commands: CreateCourse, AddModule, AddLesson,        │
│            MarkLessonComplete, ReorderModules          │
│   Queries: GetCourseList, GetCourseDetails,            │
│           GetLesson, GetProgress, GetNextIncomplete    │
│   Handlers: Orchestrate domain logic + persistence     │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                    Domain Layer                         │
│   Aggregates: Course (root), Progress (root)           │
│   Entities: Module, Lesson                             │
│   Value Objects: CourseTitle, LessonContent,           │
│                  VideoUrl, ContentType                 │
│   Events: CourseCreated, LessonCompleted,              │
│          CourseCompleted, CourseDeleted                │
│              [NO EXTERNAL DEPENDENCIES]                 │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                Infrastructure Layer                     │
│  Repositories: CourseRepository, ProgressRepository    │
│  ORM Models: CourseModel, ModuleModel, LessonModel,    │
│             ProgressModel, CompletionModel             │
│  Services: RateLimiter, EventBus                       │
└─────────────────────────────────────────────────────────┘
```

**Design Decision: Course vs Module as Aggregate Root**

**Chosen:** Course is Aggregate Root, Module and Lesson are entities within

**Rationale:**
- Course lifecycle controls module/lesson lifecycle (cascade delete)
- Module reordering requires transactional consistency (all positions update together)
- Lessons cannot exist without a module, modules cannot exist without a course
- All course editing requires admin permission check (single boundary)

**Alternative Rejected:** Module as separate Aggregate
- Pros: Smaller aggregate size, independent module updates
- Cons: Distributed transactions for reordering, inconsistent deletion, complex referential integrity

**Tradeoff:** Larger aggregate size (1 course + N modules + M lessons loaded together), but transactional consistency and simpler business rules

### 2.3 DDD Design

**Aggregates:**

**1. Course Aggregate (Root: Course)**
- **Contains:** Course entity, Modules (collection), Lessons (nested collection within modules)
- **Consistency Boundary:** All modules and lessons belong to course, managed together
- **Invariants:**
  - Course title must be unique within community (future constraint)
  - Module positions must be sequential (1, 2, 3...) with no gaps
  - Lesson positions must be sequential within each module
  - Cannot delete course if any member has progress (soft delete only)
  - Instructor reference (user_id) must be valid

**2. Progress Aggregate (Root: Progress)**
- **Contains:** Progress entity, LessonCompletion (collection)
- **Consistency Boundary:** Member's progress on a single course
- **Invariants:**
  - One progress record per member per course
  - Lesson completion references must point to existing lessons
  - Completion percentage must match actual completed lessons
  - Next incomplete lesson must be first non-completed lesson by position

**Key Entities:**

**Course (Aggregate Root)**
- Purpose: Container for learning content
- Properties: title, description, cover_image_url, estimated_duration, instructor_id, deleted_at
- Behavior:
  - add_module(title, description) → Module
  - reorder_modules(module_position_map) → void
  - delete() → soft delete (sets deleted_at, publishes CourseDeleted event)

**Module (Entity within Course)**
- Purpose: Section grouping related lessons
- Properties: title, description, position, deleted_at
- Behavior:
  - add_lesson(title, content_type, content) → Lesson
  - reorder_lessons(lesson_position_map) → void
  - delete() → soft delete

**Lesson (Entity within Module)**
- Purpose: Individual unit of learning content
- Properties: title, content_type (TEXT | VIDEO), content, position, deleted_at
- Behavior:
  - update_content(new_content) → void
  - delete() → soft delete

**Progress (Aggregate Root)**
- Purpose: Track member's course journey
- Properties: user_id, course_id, started_at, last_accessed_at, completion_percentage
- Behavior:
  - mark_lesson_complete(lesson_id) → void (publishes LessonCompleted)
  - unmark_lesson(lesson_id) → void
  - update_last_accessed(lesson_id) → void
  - calculate_completion() → float (0-100)
  - get_next_incomplete_lesson() → Lesson | None

**Value Objects:**

**CourseTitle**
- Invariant: 2-200 characters, no leading/trailing whitespace
- Validation: Strip whitespace, reject if empty after strip
- Immutable

**CourseDescription**
- Invariant: Max 2000 characters, plain text only
- Validation: Optional (can be empty string)
- Immutable

**CoverImageUrl**
- Invariant: Must be valid HTTPS URL if provided
- Validation: Pydantic HttpUrl validator
- Immutable

**LessonTitle**
- Invariant: 2-200 characters
- Similar to CourseTitle
- Immutable

**LessonContent (abstract)**
- Two implementations: TextContent, VideoContent
- Enforces content type constraints

**TextContent (Value Object)**
- Invariant: 1-50,000 characters
- Security: HTML sanitization via bleach library
- Supports: `<p>`, `<h1>`-`<h6>`, `<strong>`, `<em>`, `<ul>`, `<ol>`, `<li>`, `<a>`, `<code>`, `<pre>`, `<br>`
- Strips: `<script>`, `<iframe>`, `<object>`, event handlers
- Immutable

**VideoUrl (Value Object)**
- Invariant: Must match YouTube, Vimeo, or Loom URL pattern
- Validation: Regex patterns for each platform
- Supported formats:
  - YouTube: `https://www.youtube.com/watch?v=VIDEO_ID`, `https://youtu.be/VIDEO_ID`
  - Vimeo: `https://vimeo.com/VIDEO_ID`
  - Loom: `https://www.loom.com/share/VIDEO_ID`
- Immutable

**ContentType (Enum)**
- Values: TEXT, VIDEO
- Determines which content value object is required

**Domain Events:**

**CourseCreated**
- When: Admin creates new course
- Data: course_id, instructor_id, title, occurred_at
- Consumers: Future notification system (announce new course)

**CourseDeleted**
- When: Admin soft deletes course
- Data: course_id, deleted_by_id, occurred_at
- Consumers: Analytics (track content churn)

**ProgressStarted**
- When: Member accesses first lesson (creates progress record)
- Data: user_id, course_id, occurred_at
- Consumers: Gamification (award "started course" points - future)

**LessonCompleted**
- When: Member marks lesson as complete
- Data: user_id, course_id, lesson_id, occurred_at
- Consumers: Gamification (award points for lesson completion)

**CourseCompleted**
- When: Member completes last lesson in course
- Data: user_id, course_id, occurred_at, completion_date
- Consumers:
  - Gamification (award bonus points, unlock achievement)
  - Notification (send congratulations, generate certificate - future)

**Design Decision:** Separate vs Combined Events
- **Chosen:** Separate LessonCompleted and CourseCompleted events
- **Rationale:** Different consumers, different actions (small points vs big reward)
- **Tradeoff:** More event types, but clearer intent

---

## 3. Technology Stack

### 3.1 Backend Dependencies

**Existing (Reused):**
- FastAPI ^0.110.0 - Web framework
- SQLAlchemy ^2.0.0 - ORM
- Alembic - Database migrations
- Pydantic v2 - Validation
- slowapi - Rate limiting
- structlog - Logging

**New Dependency:**

**bleach (^6.1.0)** - HTML sanitization for rich text lessons
- **Purpose:** Sanitize user-generated HTML in text lessons to prevent XSS
- **Why This Library:**
  - Mozilla-maintained (Firefox/Thunderbird security team)
  - Battle-tested 10+ years (PyPI, Reddit, GitHub use it)
  - OWASP recommended for Python HTML sanitization
  - Whitelist-based (secure by default)
  - Actively maintained (latest: 6.3.0, October 2025)
- **Alternatives Considered:**
  - `html.escape()` - Too basic, doesn't handle nested tags or attributes
  - `nh3` (Rust-based) - Faster but less mature Python ecosystem
  - Custom regex - Security risk, cannot parse HTML reliably
- **Usage Pattern:**
  ```python
  import bleach

  ALLOWED_TAGS = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'strong', 'em',
                  'ul', 'ol', 'li', 'a', 'code', 'pre', 'br']
  ALLOWED_ATTRIBUTES = {'a': ['href'], '*': ['class']}

  sanitized = bleach.clean(
      user_input,
      tags=ALLOWED_TAGS,
      attributes=ALLOWED_ATTRIBUTES,
      strip=True
  )
  ```
- **Research:** [Bleach Documentation](https://bleach.readthedocs.io/en/latest/clean.html), [PyPI](https://pypi.org/project/bleach/), [GitHub](https://github.com/mozilla/bleach)

### 3.2 Frontend Dependencies

**Existing (Reused):**
- React 18 - UI framework
- TypeScript (strict mode) - Type safety
- TanStack Query v5 - Server state management
- React Router v6 - Client-side routing
- TailwindCSS - Styling
- react-hook-form + zod - Form validation

**New Dependencies:**

**1. Tiptap (^2.1.0)** - Rich text editor for admin lesson creation
- **Purpose:** WYSIWYG editor for creating text lessons
- **Why This Library:**
  - Built on ProseMirror (battle-tested architecture)
  - Excellent documentation with interactive examples
  - Smaller bundle size than Lexical (~40KB gzipped)
  - Real-time collaboration support (future)
  - Active community and regular updates
- **Alternatives Considered:**
  - Lexical - Faster but overwhelming docs, steeper learning curve
  - Quill - Mature but less flexible extension system
- **Configuration:** Basic toolbar (headings, bold, italic, lists, links, code)
- **Research:** [Liveblocks Comparison](https://liveblocks.io/blog/which-rich-text-editor-framework-should-you-choose-in-2025), [DEV Article](https://dev.to/codeideal/best-rich-text-editor-for-react-in-2025-3cdb), [Medium Comparison](https://medium.com/@faisalmujtaba/tiptap-vs-lexical-which-rich-text-editor-should-you-pick-for-your-next-project-17a1817efcd9)

**2. @dnd-kit/core (^6.1.0)** - Drag-and-drop for module/lesson reordering
- **Purpose:** Accessible drag-and-drop for admin reordering UI
- **Why This Library:**
  - Modern React hooks API
  - Fully accessible (keyboard navigation, screen readers)
  - Smaller bundle (~10KB) than react-beautiful-dnd
  - Better TypeScript support
  - Active maintenance (React 18 compatible)
- **Alternatives Considered:**
  - react-beautiful-dnd - No longer maintained, React 18 issues
  - react-dnd - Complex API, larger bundle
- **Usage:** Module list reordering, lesson list reordering

**3. react-player (^2.13.0)** - Embedded video player for lessons
- **Purpose:** Universal video player component supporting YouTube, Vimeo, Loom
- **Why This Library:**
  - Supports all required platforms out-of-box
  - Unified API (no platform-specific code)
  - Lightweight wrapper around iframe embeds
  - Responsive, configurable controls
- **Alternatives Considered:**
  - Custom iframe embeds - Requires platform-specific code, no unified controls
  - Platform SDKs - Larger bundle, complex API
- **Configuration:** Responsive (16:9), light mode (loads on click), controls enabled

### 3.3 Infrastructure

**Database:**
- PostgreSQL 15+ (existing)
- New tables: courses, modules, lessons, progress, lesson_completions
- Indexes: On course_id, module_id, user_id, deleted_at
- Foreign key cascades: ON DELETE SET NULL for soft deletes

**Cache:**
- Redis 7+ (existing) - Rate limiting only
- No course/lesson caching in MVP (add later if needed)

**External Services:**
- YouTube, Vimeo, Loom - Video embedding via iframe (no API calls)
- Cover images - User-provided HTTPS URLs (no upload service)

### 3.4 Technology Decision Summary

**Why no video upload?**
- Requires S3/CDN setup, transcoding, significant cost
- Embed URLs cover 95% of use cases (YouTube/Vimeo are free)
- Can add in Phase 2 if demand exists

**Why soft delete?**
- Preserves member progress data (GDPR compliance concern)
- Allows content restoration if deleted by accident
- Audit trail for admin actions

**Why no course draft mode?**
- Adds complexity (published/unpublished state, preview mode)
- Admin can create course and add content before announcing
- Can add in Phase 2 if needed

**Why cursor pagination?**
- More stable than offset (no duplicate/missing items when content changes)
- Better for infinite scroll UX
- Required if we add search/filtering later

---

## 4. Data Model

### 4.1 Conceptual Schema

**Core Tables:**

**courses**
- `id` (UUID, PK)
- `title` (String, 2-200 chars)
- `description` (Text, max 2000 chars, nullable)
- `cover_image_url` (String, HTTPS URL, nullable)
- `estimated_duration` (String, free-form, nullable) - e.g., "2 hours", "4 weeks"
- `instructor_id` (UUID, FK → users in Identity context)
- `is_deleted` (Boolean, default false)
- `deleted_at` (Timestamp, nullable)
- `deleted_by_id` (UUID, FK → users, nullable)
- `created_at`, `updated_at` (Timestamp)
- **Indexes:**
  - `idx_courses_deleted` on (is_deleted, created_at DESC) - Course list query
  - `idx_courses_instructor` on (instructor_id) - Admin's course list
- **Constraints:**
  - CHECK: title length >= 2 AND <= 200
  - CHECK: description length <= 2000

**modules**
- `id` (UUID, PK)
- `course_id` (UUID, FK → courses, NOT NULL)
- `title` (String, 2-200 chars)
- `description` (Text, max 1000 chars, nullable)
- `position` (Integer, NOT NULL) - Sequential ordering (1, 2, 3...)
- `is_deleted` (Boolean, default false)
- `deleted_at` (Timestamp, nullable)
- `created_at`, `updated_at` (Timestamp)
- **Indexes:**
  - `idx_modules_course` on (course_id, is_deleted, position) - Module list query
- **Constraints:**
  - CHECK: position > 0
  - UNIQUE (course_id, position) WHERE is_deleted = false

**lessons**
- `id` (UUID, PK)
- `module_id` (UUID, FK → modules, NOT NULL)
- `title` (String, 2-200 chars)
- `content_type` (Enum: 'text' | 'video')
- `content` (Text, NOT NULL) - HTML for text, URL for video
- `position` (Integer, NOT NULL)
- `is_deleted` (Boolean, default false)
- `deleted_at` (Timestamp, nullable)
- `created_at`, `updated_at`, `edited_at` (Timestamp)
- **Indexes:**
  - `idx_lessons_module` on (module_id, is_deleted, position) - Lesson list query
- **Constraints:**
  - CHECK: content_type IN ('text', 'video')
  - CHECK: position > 0
  - CHECK: (content_type = 'text' AND length(content) BETWEEN 1 AND 50000) OR (content_type = 'video')
  - UNIQUE (module_id, position) WHERE is_deleted = false

**progress**
- `id` (UUID, PK)
- `user_id` (UUID, FK → users in Identity context, NOT NULL)
- `course_id` (UUID, FK → courses, NOT NULL)
- `started_at` (Timestamp, NOT NULL)
- `last_accessed_lesson_id` (UUID, FK → lessons, nullable)
- `last_accessed_at` (Timestamp, nullable)
- `created_at`, `updated_at` (Timestamp)
- **Indexes:**
  - `idx_progress_user_course` UNIQUE on (user_id, course_id) - One progress per member per course
  - `idx_progress_user` on (user_id) - User's course list
  - `idx_progress_course` on (course_id) - Course analytics (future)
- **Constraints:**
  - UNIQUE (user_id, course_id)

**lesson_completions**
- `id` (UUID, PK)
- `progress_id` (UUID, FK → progress, NOT NULL)
- `lesson_id` (UUID, FK → lessons, NOT NULL)
- `completed_at` (Timestamp, NOT NULL)
- `created_at` (Timestamp)
- **Indexes:**
  - `idx_completions_progress` on (progress_id, lesson_id) - Completion lookup
  - UNIQUE (progress_id, lesson_id) - One completion per lesson per progress
- **Constraints:**
  - UNIQUE (progress_id, lesson_id)

### 4.2 Design Decisions

**Columns vs JSON for Content**

**Chosen:** Single `content` column (Text type) for both text and video

**Rationale:**
- Simpler schema (one field vs text_content + video_url)
- content_type enum disambiguates interpretation
- PostgreSQL Text type handles both (HTML or URL string)
- Validation happens in domain layer (TextContent vs VideoUrl value objects)

**Alternative Rejected:** Separate text_content and video_url columns
- Pros: Type-safe at DB level, clear schema
- Cons: One column always NULL, more complex queries, migration complexity

**Tradeoff:** Domain layer must validate content based on content_type (acceptable)

---

**Position Gaps vs Sequential**

**Chosen:** Sequential positions (1, 2, 3...) recalculated on reorder

**Rationale:**
- Simpler queries (ORDER BY position ASC)
- No "lost" positions if item deleted
- Consistent numbering for display ("Lesson 1", "Lesson 2")

**Alternative Rejected:** Position gaps (10, 20, 30...) for reorder optimization
- Pros: Reorder can be single UPDATE (move item to gap)
- Cons: Gaps eventually run out, complex gap-filling logic, inconsistent display

**Tradeoff:** Reorder updates multiple rows, but happens rarely

---

**Completion Percentage Storage**

**Chosen:** Calculate on-demand (not stored in progress table)

**Rationale:**
- Always accurate (no stale data if lessons added/deleted)
- Simpler writes (no percentage update logic)
- COUNT query is fast (indexed on progress_id)

**Alternative Rejected:** Store completion_percentage in progress table
- Pros: Faster reads (no calculation)
- Cons: Stale data, complex update logic (add/delete lesson = recalc all progress), eventual consistency

**Tradeoff:** Extra query on progress fetch, but simple and correct

---

**Soft Delete Implementation**

**Chosen:** `is_deleted` flag + `deleted_at` timestamp

**Rationale:**
- Preserves data for analytics and potential restore
- Progress calculations can exclude deleted lessons (WHERE is_deleted = false)
- Audit trail (who deleted, when)
- GDPR compliance (data retained until user account deletion)

**Alternative Rejected:** Hard delete (DELETE FROM table)
- Pros: Simpler schema, no deleted records
- Cons: Breaks progress references, no restore, no audit trail

**Tradeoff:** Larger tables (deleted rows remain), more complex queries (filter is_deleted)

### 4.3 Relationships & Cascading

**Foreign Key Cascade Rules:**

```
users (Identity context)
  └── courses (instructor_id) - ON DELETE SET NULL (course remains, instructor shows as "[Deleted User]")
  └── progress (user_id) - ON DELETE CASCADE (delete progress when user account deleted)

courses
  ├── modules (course_id) - ON DELETE CASCADE (delete modules when course deleted)
  └── progress (course_id) - ON DELETE CASCADE (delete progress when course deleted)

modules
  └── lessons (module_id) - ON DELETE CASCADE (delete lessons when module deleted)

progress
  └── lesson_completions (progress_id) - ON DELETE CASCADE (delete completions when progress deleted)
```

**Design Decision:** Soft vs Hard Cascade

**Chosen:** Soft delete for course/module/lesson (flag), hard cascade for progress (when user deleted)

**Rationale:**
- Admin deletions are reversible (accidental delete recovery)
- User account deletion is final (GDPR right to erasure)
- Progress tied to user identity (no orphaned progress)

### 4.4 Indexes Strategy

**Primary Performance Indexes:**

1. **Course List (Member View):**
   - Query: `SELECT * FROM courses WHERE is_deleted = false ORDER BY created_at DESC`
   - Index: `(is_deleted, created_at DESC)`

2. **Module List (Course Detail):**
   - Query: `SELECT * FROM modules WHERE course_id = ? AND is_deleted = false ORDER BY position ASC`
   - Index: `(course_id, is_deleted, position)`

3. **Lesson List (Module Detail):**
   - Query: `SELECT * FROM lessons WHERE module_id = ? AND is_deleted = false ORDER BY position ASC`
   - Index: `(module_id, is_deleted, position)`

4. **Progress Lookup:**
   - Query: `SELECT * FROM progress WHERE user_id = ? AND course_id = ?`
   - Index: UNIQUE `(user_id, course_id)`

5. **Completion Check:**
   - Query: `SELECT lesson_id FROM lesson_completions WHERE progress_id = ?`
   - Index: `(progress_id, lesson_id)` UNIQUE

**Index Size Considerations:**
- Each index adds ~30% to table size
- Courses table: Small (< 1000 rows per community), indexes negligible
- Lessons table: Medium (10K-100K rows), indexes ~3MB-30MB
- Completions table: Large (1M+ rows), indexes ~30MB-300MB
- Monitor with `pg_relation_size()` and `pg_indexes_size()` after 10K courses

### 4.5 Migration Strategy

**Zero-Downtime Migration:**

1. **Phase 1 - Schema Creation:**
   - Create tables: courses, modules, lessons, progress, lesson_completions
   - Create indexes and constraints
   - No data migration (new feature)

2. **Phase 2 - Application Deployment:**
   - Deploy application code
   - No downtime (new routes, no breaking changes)

3. **Phase 3 - Verification:**
   - Smoke test: Create course, add module, add lesson
   - Smoke test: Member view course, mark lesson complete
   - Monitor error rates and query performance

**Rollback Plan:**
- Drop tables in reverse order (FK constraints)
- Remove application routes
- Revert code deployment

---

## 5. API Design

### 5.1 Endpoint Overview

**RESTful Resource Design:**

**Course Management (Admin Only):**
```
POST   /api/v1/courses                    - Create course
GET    /api/v1/courses                    - List all courses (admin view)
GET    /api/v1/courses/{course_id}        - Get course details
PATCH  /api/v1/courses/{course_id}        - Update course metadata
DELETE /api/v1/courses/{course_id}        - Soft delete course
```

**Module Management (Admin Only):**
```
POST   /api/v1/courses/{course_id}/modules                - Add module
PATCH  /api/v1/modules/{module_id}                        - Update module
DELETE /api/v1/modules/{module_id}                        - Soft delete module
POST   /api/v1/courses/{course_id}/modules/reorder        - Reorder all modules
```

**Lesson Management (Admin Only):**
```
POST   /api/v1/modules/{module_id}/lessons                - Add lesson
PATCH  /api/v1/lessons/{lesson_id}                        - Update lesson
DELETE /api/v1/lessons/{lesson_id}                        - Soft delete lesson
POST   /api/v1/modules/{module_id}/lessons/reorder        - Reorder all lessons
```

**Course Discovery (Member):**
```
GET    /api/v1/courses                    - List courses (member view, with progress)
GET    /api/v1/courses/{course_id}        - Get course details (with progress)
```

**Course Consumption (Member):**
```
GET    /api/v1/lessons/{lesson_id}        - Get lesson content
POST   /api/v1/courses/{course_id}/start  - Start course (create progress)
GET    /api/v1/courses/{course_id}/continue - Get next incomplete lesson
```

**Progress Tracking (Member):**
```
GET    /api/v1/progress/courses/{course_id}       - Get progress for course
POST   /api/v1/progress/lessons/{lesson_id}/complete   - Mark lesson complete
DELETE /api/v1/progress/lessons/{lesson_id}/complete   - Un-mark lesson
```

**Design Decision: REST Verb Choices**

**PATCH vs PUT for updates:**
- Chosen: PATCH (partial updates, send only changed fields)
- Rejected: PUT (requires full resource replacement, verbose)

**POST for reordering:**
- Chosen: POST to `/reorder` sub-resource (not idempotent, batch operation)
- Rejected: Multiple PATCH requests (inefficient, no transactional guarantee)

**DELETE for completion:**
- Chosen: DELETE (removing completion state)
- Alternative: POST to `/uncomplete` (acceptable, but less RESTful)

### 5.2 Request/Response Contracts

**Create Course Request:**
```json
{
  "title": "string (2-200 chars)",
  "description": "string (max 2000 chars, optional)",
  "cover_image_url": "string (HTTPS URL, optional)",
  "estimated_duration": "string (free-form, optional)"
}
```

**Course Response:**
```json
{
  "id": "uuid",
  "title": "string",
  "description": "string | null",
  "cover_image_url": "string | null",
  "estimated_duration": "string | null",
  "instructor": {
    "id": "uuid",
    "display_name": "string",
    "avatar_url": "string | null"
  },
  "module_count": "integer",
  "lesson_count": "integer",
  "created_at": "iso8601",
  "updated_at": "iso8601",

  // Member-specific fields (only if authenticated as member)
  "progress": {
    "started": "boolean",
    "completion_percentage": "integer (0-100)",
    "last_accessed_lesson_id": "uuid | null",
    "next_incomplete_lesson_id": "uuid | null"
  } | null
}
```

**Add Module Request:**
```json
{
  "title": "string (2-200 chars)",
  "description": "string (max 1000 chars, optional)"
}
```

**Module Response:**
```json
{
  "id": "uuid",
  "course_id": "uuid",
  "title": "string",
  "description": "string | null",
  "position": "integer",
  "lesson_count": "integer",
  "created_at": "iso8601",

  // Member-specific field (only if authenticated as member)
  "completion_percentage": "integer (0-100) | null"
}
```

**Add Lesson Request:**
```json
{
  "title": "string (2-200 chars)",
  "content_type": "text | video",
  "content": "string (HTML for text, URL for video)"
}
```

**Lesson Response:**
```json
{
  "id": "uuid",
  "module_id": "uuid",
  "title": "string",
  "content_type": "text | video",
  "content": "string (sanitized HTML or embed URL)",
  "position": "integer",
  "created_at": "iso8601",
  "updated_at": "iso8601",
  "edited_at": "iso8601 | null",

  // Member-specific field (only if authenticated as member)
  "is_complete": "boolean"
}
```

**Reorder Request:**
```json
{
  "module_positions": [
    {"id": "uuid", "position": 1},
    {"id": "uuid", "position": 2},
    {"id": "uuid", "position": 3}
  ]
}
```

**Progress Response:**
```json
{
  "user_id": "uuid",
  "course_id": "uuid",
  "started_at": "iso8601",
  "last_accessed_lesson_id": "uuid | null",
  "last_accessed_at": "iso8601 | null",
  "completion_percentage": "integer (0-100)",
  "completed_lessons": ["uuid", "uuid", ...],
  "next_incomplete_lesson_id": "uuid | null"
}
```

**Design Decision: Nested Objects vs Flat**

**Chosen:** Nested instructor object in course response

**Rationale:**
- Semantic grouping (all instructor info together)
- Frontend can pass entire object to InstructorCard component
- Avoids field name collisions (instructor_display_name vs display_name)

**Tradeoff:** More verbose, but clearer and more maintainable

---

**Design Decision: Progress in Course Response**

**Chosen:** Embed progress in course response (optional, member-only)

**Rationale:**
- Avoids separate API call for progress
- Course list shows "X% complete" without extra request
- Progress is always tied to specific course (no independent use)

**Alternative Rejected:** Separate GET /progress/{course_id} endpoint
- Pros: Cleaner resource separation
- Cons: N+1 queries for course list (fetch each course's progress)

**Tradeoff:** Course response schema varies by role (admin vs member), acceptable with OpenAPI schema variants

### 5.3 Authentication & Authorization

**Authorization Model:**

| Endpoint | Auth Required | Authorization Rule |
|----------|---------------|--------------------|
| POST /courses | Yes | Admin role |
| PATCH /courses/{id} | Yes | Admin role |
| DELETE /courses/{id} | Yes | Admin role |
| POST /modules | Yes | Admin role |
| PATCH /modules/{id} | Yes | Admin role |
| DELETE /modules/{id} | Yes | Admin role |
| POST /lessons | Yes | Admin role |
| PATCH /lessons/{id} | Yes | Admin role |
| DELETE /lessons/{id} | Yes | Admin role |
| GET /courses | Yes | Any authenticated user |
| GET /courses/{id} | Yes | Any authenticated user |
| GET /lessons/{id} | Yes | Any authenticated user |
| POST /progress/lessons/{id}/complete | Yes | JWT user_id matches progress owner |
| DELETE /progress/lessons/{id}/complete | Yes | JWT user_id matches progress owner |

**Design Decision: Admin Check Location**

**Chosen:** Admin role check in application layer (handler)

**Rationale:**
- Domain layer has no concept of "roles" (keeps domain pure)
- Application layer orchestrates authorization + domain logic
- Centralized role verification (reusable across handlers)

**Pattern:**
```python
# In handler
async def handle(self, command: CreateCourseCommand) -> Course:
    if not command.user.is_admin():
        raise UnauthorizedError("Admin role required")

    # Domain logic
    course = Course.create(...)
```

**Alternative Rejected:** Middleware-level role check
- Pros: Fails fast (before handler)
- Cons: Route-level configuration complex, harder to test

### 5.4 Error Handling

**HTTP Status Code Mapping:**

| Domain Exception | HTTP Status | Response Body |
|-----------------|-------------|---------------|
| InvalidCourseTitleError | 400 Bad Request | `{"detail": "Title must be 2-200 characters"}` |
| InvalidVideoUrlError | 400 Bad Request | `{"detail": "Invalid video URL. Supported: YouTube, Vimeo, Loom"}` |
| InvalidTextContentError | 400 Bad Request | `{"detail": "Text content must be 1-50,000 characters"}` |
| CourseNotFoundError | 404 Not Found | `{"detail": "Course not found"}` |
| ModuleNotFoundError | 404 Not Found | `{"detail": "Module not found"}` |
| LessonNotFoundError | 404 Not Found | `{"detail": "Lesson not found"}` |
| UnauthorizedError | 403 Forbidden | `{"detail": "Admin role required"}` |
| Unauthenticated | 401 Unauthorized | `{"detail": "Authentication required"}` |
| RateLimitExceeded | 429 Too Many Requests | `{"detail": "Rate limit exceeded, retry in X seconds"}` |
| DuplicatePositionError | 400 Bad Request | `{"detail": "Duplicate positions in reorder request"}` |
| LessonAlreadyCompleteError | 409 Conflict | `{"detail": "Lesson already marked complete"}` |

**Design Principle:** Domain exceptions bubble up, mapped at interface layer

---

## 6. Domain Model Design

### 6.1 Aggregates

**Course Aggregate**

**Responsibilities:**
- Enforce course invariants (valid title, description)
- Manage module lifecycle (add, reorder, delete)
- Cascade delete to modules and lessons
- Publish course lifecycle events

**Methods:**
```
Course.create(title, description, cover_image_url, estimated_duration, instructor_id) -> Course
  - Validates title, description, cover_image_url
  - Publishes CourseCreated event

course.add_module(title, description) -> Module
  - Creates module with next sequential position
  - Adds to course.modules collection

course.reorder_modules(module_position_map: Dict[UUID, int]) -> None
  - Validates no duplicate positions
  - Updates all module positions transactionally
  - Maintains sequential order (1, 2, 3...)

course.update(title?, description?, cover_image_url?, estimated_duration?) -> None
  - Validates new values if provided
  - Updates only changed fields

course.soft_delete(deleted_by_id) -> None
  - Sets is_deleted = true, deleted_at = now
  - Cascades soft delete to modules and lessons
  - Publishes CourseDeleted event
```

**Invariants:**
- Title: 2-200 characters
- Description: max 2000 characters (optional)
- Cover image URL: valid HTTPS URL (optional)
- Module positions: sequential (1, 2, 3...) with no gaps
- Cannot have multiple modules with same position

---

**Progress Aggregate**

**Responsibilities:**
- Track member's course progress
- Manage lesson completions
- Calculate completion percentage
- Determine next incomplete lesson
- Publish completion events

**Methods:**
```
Progress.start_course(user_id, course_id) -> Progress
  - Creates progress record
  - Publishes ProgressStarted event

progress.mark_lesson_complete(lesson_id) -> None
  - Adds lesson_id to completed_lessons
  - Publishes LessonCompleted event
  - Checks if course complete → publishes CourseCompleted event

progress.unmark_lesson(lesson_id) -> None
  - Removes lesson_id from completed_lessons
  - Recalculates completion percentage

progress.update_last_accessed(lesson_id) -> None
  - Sets last_accessed_lesson_id
  - Updates last_accessed_at timestamp

progress.calculate_completion_percentage() -> float
  - Queries all non-deleted lessons in course
  - Returns (completed / total) * 100

progress.get_next_incomplete_lesson() -> Lesson | None
  - Queries lessons ordered by (module.position, lesson.position)
  - Returns first lesson not in completed_lessons
  - Returns None if all complete
```

**Invariants:**
- One progress per user per course
- Completed lessons must exist in course (foreign key constraint)
- Completion percentage: 0-100 (calculated, not stored)
- Last accessed lesson must exist (foreign key constraint)

### 6.2 Value Objects

**CourseTitle**
- **Purpose:** Validated course title
- **Validation:** 2-200 characters, strip leading/trailing whitespace
- **Immutable:** Yes

**LessonTitle**
- **Purpose:** Validated lesson title
- **Validation:** Same as CourseTitle

**TextContent**
- **Purpose:** Sanitized HTML content for text lessons
- **Validation:** 1-50,000 characters, HTML sanitization
- **Sanitization Strategy:**
  ```python
  import bleach

  ALLOWED_TAGS = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                  'strong', 'em', 'ul', 'ol', 'li', 'a',
                  'code', 'pre', 'br']
  ALLOWED_ATTRS = {'a': ['href', 'title'], '*': []}

  sanitized = bleach.clean(
      html_input,
      tags=ALLOWED_TAGS,
      attributes=ALLOWED_ATTRS,
      strip=True,
      protocols=['http', 'https']
  )
  ```
- **Security:** Strips `<script>`, `<iframe>`, `<object>`, event handlers
- **Immutable:** Yes

**VideoUrl**
- **Purpose:** Validated video embed URL
- **Validation:** Must match YouTube, Vimeo, or Loom URL pattern
- **Patterns:**
  ```python
  YOUTUBE_PATTERNS = [
      r'^https?://(www\.)?youtube\.com/watch\?v=[\w-]+',
      r'^https?://youtu\.be/[\w-]+',
      r'^https?://(www\.)?youtube\.com/embed/[\w-]+'
  ]

  VIMEO_PATTERNS = [
      r'^https?://vimeo\.com/\d+',
      r'^https?://player\.vimeo\.com/video/\d+'
  ]

  LOOM_PATTERNS = [
      r'^https?://(www\.)?loom\.com/share/[\w-]+'
  ]
  ```
- **Research:** [Regex Tester](https://www.regextester.com/96461), [GitHub Gist](https://gist.github.com/Mecanik/b339e629c1020fcddbf7df5fadf305b1), [RegExr](https://regexr.com/3begm)
- **Immutable:** Yes

**ContentType (Enum)**
- **Values:** TEXT, VIDEO
- **Purpose:** Disambiguate content field interpretation

### 6.3 Domain Events

**CourseCreated**
```python
@dataclass(frozen=True)
class CourseCreated(BaseEvent):
    course_id: UUID
    instructor_id: UUID
    title: str
    occurred_at: datetime
```

**CourseDeleted**
```python
@dataclass(frozen=True)
class CourseDeleted(BaseEvent):
    course_id: UUID
    deleted_by_id: UUID
    occurred_at: datetime
```

**ProgressStarted**
```python
@dataclass(frozen=True)
class ProgressStarted(BaseEvent):
    user_id: UUID
    course_id: UUID
    occurred_at: datetime
```

**LessonCompleted**
```python
@dataclass(frozen=True)
class LessonCompleted(BaseEvent):
    user_id: UUID
    course_id: UUID
    lesson_id: UUID
    occurred_at: datetime
```

**CourseCompleted**
```python
@dataclass(frozen=True)
class CourseCompleted(BaseEvent):
    user_id: UUID
    course_id: UUID
    completion_date: datetime
    occurred_at: datetime
```

**Design Decision:** Event Granularity

**Chosen:** Separate events for each domain action (5 events)

**Rationale:**
- Clear intent (each event has specific meaning)
- Different consumers (Gamification listens to LessonCompleted, Notification listens to CourseCompleted)
- Easy to add new consumers without changing existing events

**Alternative Rejected:** Generic CourseEvent with type field
- Pros: Single event type
- Cons: Loses type safety, consumers must switch on type, less clear

---

## 7. Application Layer Design

### 7.1 Commands

**CreateCourse**
- **Intent:** Admin creates new course
- **Inputs:** title, description?, cover_image_url?, estimated_duration?, instructor_id
- **Orchestration:**
  1. Verify user is admin
  2. Create Course aggregate (validates inputs)
  3. Save course via repository
  4. Publish CourseCreated event
- **Returns:** Course entity
- **Idempotency:** Not idempotent (creates new UUID each time)

**AddModule**
- **Intent:** Admin adds module to course
- **Inputs:** course_id, title, description?
- **Orchestration:**
  1. Verify user is admin
  2. Load Course aggregate
  3. Course.add_module(title, description) - assigns next position
  4. Save course
- **Returns:** Module entity

**AddLesson**
- **Intent:** Admin adds lesson to module
- **Inputs:** module_id, title, content_type, content
- **Orchestration:**
  1. Verify user is admin
  2. Load Course aggregate (via module.course_id)
  3. Validate content based on content_type (create TextContent or VideoUrl)
  4. Module.add_lesson(title, content_type, content) - assigns next position
  5. Save course
- **Returns:** Lesson entity

**ReorderModules**
- **Intent:** Admin changes module order via drag-and-drop
- **Inputs:** course_id, module_position_map: Dict[UUID, int]
- **Orchestration:**
  1. Verify user is admin
  2. Load Course aggregate
  3. Course.reorder_modules(module_position_map) - validates, updates all positions
  4. Save course (transactional)
- **Returns:** void

**MarkLessonComplete**
- **Intent:** Member marks lesson as complete
- **Inputs:** user_id, lesson_id
- **Orchestration:**
  1. Load or create Progress aggregate (user_id, course_id)
  2. Progress.mark_lesson_complete(lesson_id)
  3. Save progress
  4. Publish LessonCompleted event
  5. If completion_percentage == 100, publish CourseCompleted event
- **Returns:** void
- **Idempotency:** Idempotent (marking complete twice = no-op)

### 7.2 Queries

**GetCourseList**
- **Intent:** Retrieve all courses (filtered by is_deleted)
- **Inputs:** user_id (for progress lookup), is_admin (for filtering)
- **Returns:** List[CourseWithProgress]
- **Optimization:** Single query with LEFT JOIN on progress

**GetCourseDetails**
- **Intent:** Retrieve course with all modules and lessons
- **Inputs:** course_id, user_id (for progress)
- **Returns:** Course with nested modules/lessons, completion status per lesson
- **Optimization:** Single query with eager loading (JOIN modules, lessons)

**GetLesson**
- **Intent:** Retrieve lesson content for viewing
- **Inputs:** lesson_id, user_id (for completion status)
- **Returns:** Lesson with is_complete flag
- **Side Effect:** Updates progress.last_accessed_lesson_id

**GetProgress**
- **Intent:** Retrieve member's progress for a course
- **Inputs:** user_id, course_id
- **Returns:** Progress with completion_percentage, next_incomplete_lesson_id

**GetNextIncompleteLesson**
- **Intent:** Determine where member should continue
- **Inputs:** user_id, course_id
- **Returns:** Lesson entity or None (if course complete)
- **Logic:** First lesson (by module.position, lesson.position) not in completed_lessons

### 7.3 Use Case Flow Example

**"Member Marks Lesson Complete" Flow:**

```
1. Frontend: User clicks "Mark as Complete" on Lesson 3
   → POST /api/v1/progress/lessons/{lesson_id}/complete

2. Controller:
   - Extracts user_id from JWT token
   - Validates lesson_id is UUID
   - Calls MarkLessonCompleteHandler

3. Handler:
   - Load Progress aggregate (user_id, course_id)
   - If progress doesn't exist, create it (auto-start course)
   - progress.mark_lesson_complete(lesson_id)
     → Adds lesson_id to completed_lessons
     → Publishes LessonCompleted event
   - Save progress via repository
   - Calculate completion_percentage
   - If 100%, publish CourseCompleted event

4. Repository:
   - INSERT INTO lesson_completions (progress_id, lesson_id, completed_at)
   - ON CONFLICT (progress_id, lesson_id) DO NOTHING (idempotent)

5. Event Bus:
   - LessonCompleted event → (future) Gamification handler (award 10 points)
   - CourseCompleted event → (future) Notification handler (send congrats)

6. Controller:
   - Returns 204 No Content (success)

7. Frontend:
   - Updates UI (checkmark appears)
   - Progress bar increases
   - "Next Lesson" button highlights
```

---

## 8. Integration Strategy

### 8.1 Cross-Context Communication

**Identity Context → Classroom:**
- **Type:** Customer/Supplier
- **Flow:** Classroom reads user data (display_name, avatar_url) for instructor display
- **Integration:** Direct database read (users table) via user_id foreign key
- **Alternative Considered:** Domain events (UserRegistered → create ClassroomMember)
  - Rejected: Unnecessary duplication, Identity owns user data
  - Classroom only needs read access, not local copy

**Classroom → Gamification (Future):**
- **Type:** Publisher/Subscriber
- **Flow:** Classroom publishes LessonCompleted, CourseCompleted events
- **Integration:** Asynchronous domain events via in-memory event bus
- **Pattern:**
  ```python
  # Classroom publishes
  event_bus.publish(LessonCompleted(user_id, course_id, lesson_id, occurred_at))

  # Gamification subscribes (future)
  @event_handler(LessonCompleted)
  async def award_lesson_points(event: LessonCompleted) -> None:
      await gamification_service.award_points(
          user_id=event.user_id,
          points=10,
          reason="lesson_completed"
      )
  ```

**Classroom → Notification (Future):**
- **Type:** Publisher/Subscriber
- **Flow:** Classroom publishes CourseCompleted event
- **Integration:** Asynchronous domain events
- **Use Case:** Send congratulations email, generate certificate

### 8.2 External Services

**Video Providers (YouTube, Vimeo, Loom):**
- **Integration:** Iframe embedding (no API calls)
- **Pattern:**
  ```html
  <!-- YouTube -->
  <iframe src="https://www.youtube.com/embed/VIDEO_ID" />

  <!-- Vimeo -->
  <iframe src="https://player.vimeo.com/video/VIDEO_ID" />

  <!-- Loom -->
  <iframe src="https://www.loom.com/embed/VIDEO_ID" />
  ```
- **Failure Mode:** Video load error (private, deleted, geo-restricted)
  - Frontend shows fallback: "Unable to load video. Contact instructor."
- **No API Key Required:** Embedding is public, no rate limits

**Cover Image Hosting:**
- **Integration:** User-provided HTTPS URLs
- **No Upload Service:** MVP relies on external hosting (Imgur, Cloudinary, etc.)
- **Validation:** Check URL format (HTTPS), no content validation
- **Failure Mode:** Image fails to load → frontend shows placeholder image

### 8.3 Anti-Corruption Layer

**Not Required for MVP:**
- Video providers use standard iframe API (stable, no translation needed)
- Identity context uses shared kernel (UserId value object)

**Future Consideration:**
- If adding native video upload (Phase 2), create VideoStorageService ACL
- Abstracts S3/Cloudflare R2/Backblaze B2 differences
- Domain layer depends on VideoStorage interface, infrastructure implements

---

## 9. Security Design

### 9.1 Authentication

**All endpoints require valid JWT token:**
- Token extracted from `Authorization: Bearer <token>` header
- Token validated via existing Identity context JWT service
- user_id extracted from token claims

### 9.2 Authorization

**Role-Based Access Control:**

| Action | Member | Admin |
|--------|--------|-------|
| View courses/lessons | ✓ | ✓ |
| Track progress | ✓ | ✓ |
| Create course | ✗ | ✓ |
| Edit course/module/lesson | ✗ | ✓ |
| Delete course/module/lesson | ✗ | ✓ |
| Reorder modules/lessons | ✗ | ✓ |

**Implementation:**
- Role check in application layer handler (before domain logic)
- Role stored in JWT token claims (set by Identity context on login)
- Centralized role verification utility:
  ```python
  def require_admin(user: User) -> None:
      if not user.is_admin:
          raise UnauthorizedError("Admin role required")
  ```

**Progress Isolation:**
- Members can only access their own progress
- Progress lookup filtered by JWT user_id (cannot forge)
- No "view other member progress" endpoint (even for admins)

### 9.3 Input Validation

**All user input validated at multiple layers:**

**1. Interface Layer (Pydantic schemas):**
- Type checking (string, integer, UUID)
- Length constraints (minLength, maxLength)
- Format validation (URL, enum)

**2. Domain Layer (Value objects):**
- Business rule validation (title 2-200 chars, content type specific)
- HTML sanitization (TextContent value object)
- URL pattern matching (VideoUrl value object)

**HTML Sanitization (XSS Prevention):**
```python
# TextContent value object
import bleach

ALLOWED_TAGS = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'strong', 'em',
                'ul', 'ol', 'li', 'a', 'code', 'pre', 'br']
ALLOWED_ATTRIBUTES = {'a': ['href', 'title']}

def sanitize(html: str) -> str:
    return bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True,
        protocols=['http', 'https']
    )
```

**Video URL Validation:**
- Regex patterns for YouTube/Vimeo/Loom
- Only HTTPS URLs accepted
- Reject URLs with suspicious characters (e.g., `javascript:`)

**Cover Image URL Validation:**
- Pydantic HttpUrl validator (HTTPS only)
- No content validation (assumes external hosting is safe)

### 9.4 Rate Limiting

**Classroom-Specific Limits:**

| Endpoint | Limit | Window | Scope |
|----------|-------|--------|-------|
| POST /courses | 10 | 1 hour | Per admin user |
| POST /modules | 50 | 1 hour | Per admin user |
| POST /lessons | 100 | 1 hour | Per admin user |
| POST /progress/*/complete | 1000 | 1 hour | Per member |
| GET /courses | 100 | 1 minute | Per user |
| GET /lessons/* | 500 | 1 minute | Per user |

**Rationale:**
- Course creation: Generous limit (prevents spam, allows bulk creation)
- Lesson creation: Higher limit (courses may have 50+ lessons)
- Progress updates: Very high limit (rapid lesson completion should work)
- Read endpoints: High limit (support rapid navigation)

**Implementation:**
- Redis-based rate limiter (existing slowapi library)
- Key format: `rate_limit:{user_id}:{endpoint}`
- Returns 429 Too Many Requests on exceed

### 9.5 Data Protection

**Soft Delete Strategy:**
- All deletions are soft delete (is_deleted flag)
- Preserves audit trail (who deleted, when)
- Allows accidental deletion recovery (future admin UI)
- Progress data retained even if course deleted

**GDPR Compliance:**
- User account deletion → hard delete progress via CASCADE
- Right to erasure: progress data deleted when user account deleted
- Right to access: progress data exportable via API (future)

**Threat Model:**

**Threat 1: XSS via Text Lesson Content**
- **Attack:** Admin creates lesson with `<script>alert('xss')</script>`
- **Mitigation:** HTML sanitization in TextContent value object (bleach library)
- **Defense Depth:** Content-Security-Policy header (no inline scripts)

**Threat 2: CSRF on Course Deletion**
- **Attack:** Malicious site tricks admin into DELETE /courses/{id}
- **Mitigation:** CSRF token validation (existing FastAPI middleware)
- **Defense Depth:** SameSite=Strict cookie attribute on JWT token

**Threat 3: Unauthorized Progress Modification**
- **Attack:** Member tries to mark another member's lesson complete
- **Mitigation:** Progress filtered by JWT user_id (cannot forge)
- **Defense Depth:** Foreign key constraint (progress.user_id → users.id)

**Threat 4: SQL Injection**
- **Attack:** Admin creates course with title `'; DROP TABLE courses;--`
- **Mitigation:** Parameterized queries (SQLAlchemy ORM)
- **Defense Depth:** Input validation (rejects special characters)

---

## 10. Performance & Scalability

### 10.1 Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Course list load time | < 500ms (p95) | Time to first byte + render |
| Course detail load time | < 800ms (p95) | Includes modules/lessons |
| Lesson content load time | < 300ms (p95) | Text only (video load async) |
| Progress update latency | < 200ms (p95) | Mark complete response time |
| Video embed load time | < 2s (p95) | Dependent on provider |

### 10.2 Caching Strategy

**No Caching in MVP:**
- Premature optimization (unknown access patterns)
- Course content changes infrequently (admin edits)
- Read queries are fast enough (indexed, < 500ms)

**Future Caching (Phase 2):**
- Redis cache for course list (5 min TTL)
- Redis cache for course details (5 min TTL)
- Cache invalidation on course/module/lesson update
- Pattern: Cache-aside (query DB, populate cache)

### 10.3 Query Optimization

**Course List Query:**
```sql
-- Without progress (fast)
SELECT * FROM courses WHERE is_deleted = false ORDER BY created_at DESC LIMIT 20;

-- With progress (still fast)
SELECT c.*, p.completion_percentage, p.last_accessed_at
FROM courses c
LEFT JOIN progress p ON c.id = p.course_id AND p.user_id = ?
WHERE c.is_deleted = false
ORDER BY c.created_at DESC
LIMIT 20;
```
- Uses index: `(is_deleted, created_at DESC)`
- Execution time: ~10ms for 1000 courses, ~50ms for 10K courses

**Course Detail Query:**
```sql
-- Single query with eager loading
SELECT c.*, m.*, l.*
FROM courses c
LEFT JOIN modules m ON c.id = m.course_id AND m.is_deleted = false
LEFT JOIN lessons l ON m.id = l.module_id AND l.is_deleted = false
WHERE c.id = ? AND c.is_deleted = false
ORDER BY m.position, l.position;
```
- Uses indexes: `(course_id, is_deleted, position)` on modules, lessons
- Execution time: ~20ms for course with 10 modules, 100 lessons

**Progress Calculation:**
```sql
-- Count completed lessons
SELECT COUNT(*) FROM lesson_completions WHERE progress_id = ?;

-- Count total lessons in course
SELECT COUNT(*) FROM lessons l
JOIN modules m ON l.module_id = m.id
WHERE m.course_id = ? AND l.is_deleted = false AND m.is_deleted = false;
```
- Uses index: `(progress_id)` on completions, `(course_id)` on modules
- Execution time: ~5ms per query

**Optimization:** Denormalize lesson count
- Add `lesson_count` column to courses table
- Update on lesson add/delete (increment/decrement)
- Reduces progress calculation to single COUNT query

### 10.4 Scalability Considerations

**Database:**
- Single PostgreSQL instance sufficient for MVP (< 10K courses)
- Read replicas needed at scale (> 100K courses, > 1M progress records)
- Partitioning strategy (future): Partition progress table by course_id

**Bottlenecks:**
- Course detail query (JOIN modules + lessons) slowest
- Progress calculation on every course list request
- Video embed iframes (external dependency)

**Scaling Strategy:**
1. **Vertical scaling:** Upgrade PostgreSQL instance (16 CPU, 64GB RAM)
2. **Horizontal scaling:** Read replicas for course queries
3. **Caching:** Redis cache for course list/details
4. **CDN:** Cache course cover images
5. **Database partitioning:** Partition progress table by course_id

**Capacity Planning:**
- 10K courses = ~1GB database
- 1M progress records = ~500MB database
- 10M lesson completions = ~2GB database
- Total: ~3.5GB for mature community

---

## 11. Error Handling Design

### 11.1 Error Taxonomy

**1. Validation Errors (400 Bad Request):**
- InvalidCourseTitleError - Title too short/long/empty
- InvalidTextContentError - Content too long or empty
- InvalidVideoUrlError - URL doesn't match YouTube/Vimeo/Loom pattern
- InvalidDescriptionError - Description too long
- DuplicatePositionError - Reorder request has duplicate positions

**2. Not Found Errors (404 Not Found):**
- CourseNotFoundError - Course ID doesn't exist or is deleted
- ModuleNotFoundError - Module ID doesn't exist or is deleted
- LessonNotFoundError - Lesson ID doesn't exist or is deleted
- ProgressNotFoundError - Progress doesn't exist for user+course

**3. Authorization Errors (403 Forbidden):**
- UnauthorizedError - Non-admin tries admin action
- ProgressAccessDeniedError - Member tries to access another member's progress

**4. Authentication Errors (401 Unauthorized):**
- InvalidTokenError - JWT token expired or invalid
- MissingTokenError - Authorization header missing

**5. Rate Limit Errors (429 Too Many Requests):**
- RateLimitExceeded - User exceeded rate limit

**6. Conflict Errors (409 Conflict):**
- CourseDeletedError - Trying to access deleted course
- LessonAlreadyCompleteError - Already marked complete (informational)

### 11.2 Error Response Format

**Standard Error Response:**
```json
{
  "detail": "Human-readable error message",
  "error_code": "INVALID_VIDEO_URL", // Optional, for client error handling
  "field": "content", // Optional, for field-specific errors
  "timestamp": "2026-02-07T12:34:56Z"
}
```

**Validation Error Response (Multiple Fields):**
```json
{
  "detail": "Validation failed",
  "errors": [
    {
      "field": "title",
      "message": "Title must be 2-200 characters"
    },
    {
      "field": "cover_image_url",
      "message": "Invalid URL format"
    }
  ]
}
```

### 11.3 Error Handling Flow

**1. Domain Layer:** Raises domain-specific exceptions
```python
class InvalidVideoUrlError(Exception):
    def __init__(self, url: str):
        self.url = url
        super().__init__(f"Invalid video URL: {url}")
```

**2. Application Layer:** Catches and re-raises or logs
```python
async def handle(self, command: AddLessonCommand) -> Lesson:
    try:
        content = VideoUrl(command.content)  # Raises InvalidVideoUrlError
    except InvalidVideoUrlError as e:
        logger.warning("Invalid video URL", url=e.url)
        raise  # Re-raise to interface layer
```

**3. Interface Layer:** Maps exceptions to HTTP responses
```python
@app.exception_handler(InvalidVideoUrlError)
async def handle_invalid_video_url(request, exc):
    return JSONResponse(
        status_code=400,
        content={
            "detail": "Invalid video URL. Supported: YouTube, Vimeo, Loom",
            "error_code": "INVALID_VIDEO_URL",
            "field": "content"
        }
    )
```

---

## 12. Testing Strategy

### 12.1 Test Layers

**1. Unit Tests (Domain Layer):**
- Test entities, value objects, events
- No external dependencies (database, network)
- Fast (< 1ms per test)

**Example:**
```python
def test_course_add_module_assigns_sequential_position():
    course = Course.create(title="Test Course", instructor_id=uuid4())
    module1 = course.add_module(title="Module 1")
    module2 = course.add_module(title="Module 2")

    assert module1.position == 1
    assert module2.position == 2
```

**2. BDD Tests (Application Layer):**
- Test use cases via API (pytest-bdd)
- Use test database (reset between scenarios)
- Cover all BDD scenarios from classroom.feature

**3. Integration Tests (Infrastructure Layer):**
- Test repository implementations
- Test database constraints and cascades
- Test rate limiter behavior

### 12.2 BDD Coverage

**All 723 BDD scenarios in classroom.feature must pass:**

- Course Management (Admin): 7 scenarios
- Course Validation Errors: 5 scenarios
- Module Management (Admin): 5 scenarios
- Module Validation Errors: 4 scenarios
- Lesson Management (Admin): 10 scenarios
- Lesson Validation Errors: 8 scenarios
- Course Discovery (Member): 6 scenarios
- Course Consumption (Member): 11 scenarios
- Progress Tracking (Member): 8 scenarios
- Empty States: 2 scenarios
- Security: 10 scenarios

**Total: 76 BDD scenarios**

### 12.3 Test Fixtures

**Use domain layer for test data creation:**

```python
# ✓ CORRECT - Uses domain factory
async def create_course(course_repository, user_repository):
    user = User.register(email, hashed_password)
    await user_repository.save(user)

    course = Course.create(title="Test Course", instructor_id=user.id)
    await course_repository.save(course)
    return course

# ✗ WRONG - Bypasses domain, creates ORM model directly
async def create_course(db_session):
    course = CourseModel(id=uuid4(), title="Test Course", ...)
    db_session.add(course)
    return course
```

**Why:**
- Tests domain logic (validation, events)
- Matches real application flow
- Catches bugs in domain layer

### 12.4 Coverage Requirements

**Minimum 80% code coverage:**
- Domain layer: 95%+ (all business logic)
- Application layer: 90%+ (all handlers)
- Infrastructure layer: 70%+ (repository implementations)
- Interface layer: 60%+ (controller error handling)

**Critical paths must have 100% coverage:**
- Course creation and deletion
- Progress tracking and completion events
- HTML sanitization (XSS prevention)
- Video URL validation

---

## 13. Observability

### 13.1 Logging

**Structured logging with structlog:**

**Log Levels:**
- **DEBUG:** Query execution, cache hits/misses
- **INFO:** Command execution, event publishing
- **WARNING:** Validation errors, rate limit hits
- **ERROR:** Unexpected exceptions, external service failures

**Key Log Events:**

```python
# Course created
logger.info(
    "course_created",
    course_id=course.id,
    instructor_id=course.instructor_id,
    title=course.title
)

# Lesson completed
logger.info(
    "lesson_completed",
    user_id=user_id,
    course_id=course_id,
    lesson_id=lesson_id,
    completion_percentage=progress.completion_percentage
)

# Video embed failed
logger.warning(
    "video_embed_failed",
    lesson_id=lesson_id,
    video_url=lesson.content,
    error="Video is private or deleted"
)

# Course deleted
logger.info(
    "course_deleted",
    course_id=course.id,
    deleted_by_id=deleted_by_id,
    soft_delete=True
)
```

### 13.2 Metrics

**Key Metrics to Track:**

**Engagement Metrics:**
- `classroom.courses_created` (counter) - Total courses created
- `classroom.lessons_completed` (counter) - Total lessons marked complete
- `classroom.courses_completed` (counter) - Total courses finished
- `classroom.course_start_rate` (gauge) - % of members starting at least 1 course
- `classroom.course_completion_rate` (gauge) - % of started courses completed

**Performance Metrics:**
- `classroom.query_duration` (histogram) - Query execution time by endpoint
- `classroom.course_list_load_time` (histogram) - Time to load course list
- `classroom.lesson_load_time` (histogram) - Time to load lesson content

**Error Metrics:**
- `classroom.validation_errors` (counter) - Validation failures by type
- `classroom.video_embed_failures` (counter) - Video load failures by provider
- `classroom.rate_limit_hits` (counter) - Rate limit exceeded count

### 13.3 Tracing

**OpenTelemetry Spans:**

**Key Spans:**
- `CreateCourseHandler.handle` - Course creation flow
- `AddLessonHandler.handle` - Lesson creation flow
- `MarkLessonCompleteHandler.handle` - Progress tracking flow
- `GetCourseListQuery.execute` - Course list query
- `CourseRepository.save` - Database write

**Trace Attributes:**
- `user_id` - Authenticated user ID
- `course_id` - Course being accessed
- `lesson_id` - Lesson being accessed
- `role` - User role (admin or member)
- `content_type` - Lesson content type (text or video)

**Example Trace:**
```
CreateCourseHandler.handle (100ms)
  ├─ Course.create (5ms)
  ├─ CourseRepository.save (20ms)
  │   └─ PostgreSQL INSERT (15ms)
  └─ EventBus.publish (10ms)
      └─ CourseCreated event (5ms)
```

---

## 14. Deployment Strategy

### 14.1 Migration Plan

**Phase 1: Database Migration**
1. Run Alembic migration to create tables (courses, modules, lessons, progress, lesson_completions)
2. Create indexes (5-10 seconds downtime)
3. Verify schema with smoke test queries

**Phase 2: Application Deployment**
1. Deploy backend code (zero downtime, new routes)
2. Deploy frontend code (SPA, no downtime)
3. Smoke test: Create course, view course, mark lesson complete

**Phase 3: Monitoring**
1. Watch error rates (expect 0% for new routes)
2. Monitor query performance (course list < 500ms, lesson load < 300ms)
3. Check event publishing (LessonCompleted events appearing in logs)

**Phase 4: Announcement**
1. Admin creates first course (onboarding content)
2. Announce to community (feed post, email)
3. Monitor engagement (course start rate)

### 14.2 Rollback Plan

**If critical bug found:**
1. Remove Classroom navigation links from frontend (hide feature)
2. Keep backend routes live (preserve data)
3. Fix bug, redeploy
4. Re-enable navigation links

**If database corruption:**
1. Restore from backup (PostgreSQL point-in-time recovery)
2. Replay missing transactions from logs
3. Verify data integrity (progress calculations)

**If performance degradation:**
1. Add database indexes (CREATE INDEX CONCURRENTLY, no downtime)
2. Enable Redis caching (course list, course details)
3. Scale PostgreSQL instance (vertical scaling)

### 14.3 Feature Flags

**Not using feature flags in MVP:**
- Classroom is new feature (no backward compatibility needed)
- All-or-nothing deployment (easier to reason about)

**Future feature flags (Phase 2):**
- `enable_video_upload` - Toggle native video upload
- `enable_course_certificates` - Toggle certificate generation
- `enable_lesson_prerequisites` - Toggle lesson locking

---

## 15. Future Considerations

### 15.1 Phase 2 Enhancements

**Content Features:**
- Native video upload (S3 + CloudFlare Stream)
- PDF/document attachments (per lesson)
- Audio lessons (podcast-style content)
- Quiz/assessment lessons (multiple choice, grading)
- Lesson notes (member annotations)

**Navigation Features:**
- Lesson prerequisites (lock lessons until prior complete)
- Drip content (scheduled release by date)
- Course bookmarks (save for later)
- Lesson search within course

**Social Features:**
- Discussion threads per lesson
- "Ask instructor" button
- Course ratings and reviews
- Share completion badge to feed

**Admin Features:**
- Course analytics (views, completion rates, drop-off points)
- Draft mode (unpublished courses)
- Course duplication
- Bulk lesson import (CSV, Markdown)
- Course templates

### 15.2 Known Limitations

**1. No Real-Time Collaboration:**
- Admin edits not visible to viewing members until refresh
- No conflict resolution if two admins edit simultaneously
- Solution: Optimistic locking (version field on course)

**2. No Video Playback Analytics:**
- Cannot track watch time or completion percentage
- Cannot detect if member actually watched video
- Solution: Integrate YouTube/Vimeo Player API (Phase 3)

**3. No Course Search:**
- Members must browse full list
- No filtering by topic, instructor, duration
- Solution: PostgreSQL full-text search (Phase 2)

**4. No Offline Access:**
- Members must be online to view lessons
- No download for offline viewing
- Solution: Progressive Web App (PWA) with service worker cache

### 15.3 Technical Debt

**1. Reorder Performance:**
- Reordering updates N rows (N modules or lessons)
- Could be optimized with position gaps (10, 20, 30...)
- Trade-off: Consistency vs performance

**2. Progress Calculation:**
- Calculated on every request (COUNT query)
- Could be denormalized (store completion_percentage)
- Trade-off: Stale data vs query cost

**3. No Caching:**
- Every course list request hits database
- Could cache with Redis (5 min TTL)
- Trade-off: Complexity vs performance gain

**4. Single Aggregate Size:**
- Course aggregate loads all modules + lessons
- Could separate Module as aggregate (smaller loads)
- Trade-off: Consistency vs memory usage

---

## 16. Alignment Verification

See `ALIGNMENT_VERIFICATION.md` for full PRD → BDD → TDD coverage analysis.

**Summary:**
- ✓ All 19 user stories from PRD covered
- ✓ All 76 BDD scenarios mapped to technical components
- ✓ All business rules enforced by domain model
- ✓ All security requirements addressed
- ✓ All UI behaviors supported by API design

**Gaps (Intentional):**
- Rich text editor choice: Tiptap selected (PRD open question resolved)
- Video embed sandbox: Using default iframe (no CSP sandbox - revisit in security review)
- Progress auto-save: Manual only (PRD decision confirmed)
- Course image hosting: URLs only (PRD decision confirmed)

---

## 17. Appendices

### 17.1 File Checklist

**Backend (Python):**

**Domain Layer:**
- `src/classroom/domain/entities/course.py` - Course aggregate root
- `src/classroom/domain/entities/module.py` - Module entity
- `src/classroom/domain/entities/lesson.py` - Lesson entity
- `src/classroom/domain/entities/progress.py` - Progress aggregate root
- `src/classroom/domain/value_objects/course_title.py` - CourseTitle VO
- `src/classroom/domain/value_objects/lesson_title.py` - LessonTitle VO
- `src/classroom/domain/value_objects/text_content.py` - TextContent VO (HTML sanitization)
- `src/classroom/domain/value_objects/video_url.py` - VideoUrl VO (validation)
- `src/classroom/domain/value_objects/content_type.py` - ContentType enum
- `src/classroom/domain/events/course_created.py` - CourseCreated event
- `src/classroom/domain/events/course_deleted.py` - CourseDeleted event
- `src/classroom/domain/events/progress_started.py` - ProgressStarted event
- `src/classroom/domain/events/lesson_completed.py` - LessonCompleted event
- `src/classroom/domain/events/course_completed.py` - CourseCompleted event
- `src/classroom/domain/repositories/course_repository.py` - Course repository interface
- `src/classroom/domain/repositories/progress_repository.py` - Progress repository interface
- `src/classroom/domain/exceptions.py` - Domain exceptions

**Application Layer:**
- `src/classroom/application/commands/create_course.py` - CreateCourse command
- `src/classroom/application/commands/add_module.py` - AddModule command
- `src/classroom/application/commands/add_lesson.py` - AddLesson command
- `src/classroom/application/commands/reorder_modules.py` - ReorderModules command
- `src/classroom/application/commands/reorder_lessons.py` - ReorderLessons command
- `src/classroom/application/commands/update_course.py` - UpdateCourse command
- `src/classroom/application/commands/update_module.py` - UpdateModule command
- `src/classroom/application/commands/update_lesson.py` - UpdateLesson command
- `src/classroom/application/commands/delete_course.py` - DeleteCourse command
- `src/classroom/application/commands/delete_module.py` - DeleteModule command
- `src/classroom/application/commands/delete_lesson.py` - DeleteLesson command
- `src/classroom/application/commands/mark_lesson_complete.py` - MarkLessonComplete command
- `src/classroom/application/commands/unmark_lesson.py` - UnmarkLesson command
- `src/classroom/application/queries/get_course_list.py` - GetCourseList query
- `src/classroom/application/queries/get_course_details.py` - GetCourseDetails query
- `src/classroom/application/queries/get_lesson.py` - GetLesson query
- `src/classroom/application/queries/get_progress.py` - GetProgress query
- `src/classroom/application/queries/get_next_incomplete_lesson.py` - GetNextIncompleteLesson query
- `src/classroom/application/handlers/` - Handlers for all commands/queries (15 files)

**Infrastructure Layer:**
- `src/classroom/infrastructure/persistence/models.py` - SQLAlchemy models (CourseModel, ModuleModel, LessonModel, ProgressModel, CompletionModel)
- `src/classroom/infrastructure/persistence/course_repository.py` - Course repository implementation
- `src/classroom/infrastructure/persistence/progress_repository.py` - Progress repository implementation
- `src/classroom/infrastructure/persistence/alembic/versions/XXX_create_classroom_tables.py` - Alembic migration

**Interface Layer:**
- `src/classroom/interface/api/course_controller.py` - Course endpoints (admin + member)
- `src/classroom/interface/api/progress_controller.py` - Progress endpoints (member)
- `src/classroom/interface/api/schemas.py` - Pydantic request/response schemas
- `src/classroom/interface/api/dependencies.py` - FastAPI dependencies (auth, DB session)

**Frontend (TypeScript + React):**

**API Client:**
- `frontend/src/api/classroom.ts` - API client functions (getCourses, createCourse, etc.)

**Types:**
- `frontend/src/types/classroom.ts` - TypeScript interfaces (Course, Module, Lesson, Progress)

**Components:**
- `frontend/src/components/classroom/CourseCard.tsx` - Course card component
- `frontend/src/components/classroom/CourseList.tsx` - Course list grid
- `frontend/src/components/classroom/CourseDetail.tsx` - Course overview page
- `frontend/src/components/classroom/ModuleAccordion.tsx` - Module accordion component
- `frontend/src/components/classroom/LessonView.tsx` - Lesson content page
- `frontend/src/components/classroom/ProgressBar.tsx` - Progress indicator
- `frontend/src/components/classroom/VideoPlayer.tsx` - Video embed (react-player)
- `frontend/src/components/classroom/RichTextEditor.tsx` - Tiptap editor (admin)
- `frontend/src/components/classroom/ModuleList.tsx` - Admin module management
- `frontend/src/components/classroom/LessonList.tsx` - Admin lesson management
- `frontend/src/components/classroom/DragDropList.tsx` - Reorder UI (@dnd-kit)

**Pages:**
- `frontend/src/pages/classroom/CoursesPage.tsx` - Course list page
- `frontend/src/pages/classroom/CourseDetailPage.tsx` - Course overview page
- `frontend/src/pages/classroom/LessonPage.tsx` - Lesson view page
- `frontend/src/pages/classroom/AdminCoursePage.tsx` - Admin course management

**Hooks:**
- `frontend/src/hooks/useClassroom.ts` - TanStack Query hooks (useGetCourses, useCreateCourse, etc.)

### 17.2 Dependencies

**Backend (Python):**
```toml
[tool.poetry.dependencies]
bleach = "^6.1.0"  # NEW - HTML sanitization
fastapi = "^0.110.0"
sqlalchemy = "^2.0.0"
alembic = "^1.13.0"
pydantic = "^2.5.0"
slowapi = "^0.1.9"
structlog = "^24.1.0"
```

**Frontend (TypeScript):**
```json
{
  "dependencies": {
    "@tiptap/react": "^2.1.0",  // NEW - Rich text editor
    "@tiptap/starter-kit": "^2.1.0",  // NEW - Tiptap extensions
    "@dnd-kit/core": "^6.1.0",  // NEW - Drag-and-drop
    "@dnd-kit/sortable": "^8.0.0",  // NEW - Sortable list
    "react-player": "^2.13.0",  // NEW - Video player
    "react": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "@tanstack/react-query": "^5.17.0",
    "react-hook-form": "^7.49.0",
    "zod": "^3.22.4"
  }
}
```

### 17.3 References

**Documentation:**
- [Bleach HTML Sanitization](https://bleach.readthedocs.io/en/latest/clean.html)
- [Tiptap Editor Guide](https://tiptap.dev/guide)
- [React Player Documentation](https://www.npmjs.com/package/react-player)
- [DND Kit Documentation](https://docs.dndkit.com/)
- [PostgreSQL Full Text Search](https://www.postgresql.org/docs/current/textsearch.html)

**Research:**
- [Liveblocks: Which Rich Text Editor Framework in 2025](https://liveblocks.io/blog/which-rich-text-editor-framework-should-you-choose-in-2025)
- [DEV: Best Rich Text Editor for React in 2025](https://dev.to/codeideal/best-rich-text-editor-for-react-in-2025-3cdb)
- [Medium: Tiptap vs Lexical Comparison](https://medium.com/@faisalmujtaba/tiptap-vs-lexical-which-rich-text-editor-should-you-pick-for-your-next-project-17a1817efcd9)
- [Regex Tester: YouTube/Vimeo Validation](https://www.regextester.com/96461)
- [GitHub Gist: Video URL Regex Patterns](https://gist.github.com/Mecanik/b339e629c1020fcddbf7df5fadf305b1)

**Related Koulu Documents:**
- `docs/OVERVIEW_PRD.md` - Master product roadmap
- `docs/domain/GLOSSARY.md` - Ubiquitous language
- `docs/architecture/CONTEXT_MAP.md` - Bounded context relationships
- `docs/features/classroom/classroom-prd.md` - Product Requirements Document
- `tests/features/classroom/classroom.feature` - BDD Specifications
- `docs/features/identity/profile-tdd.md` - Reference TDD (similar patterns)
- `docs/features/community/feed-tdd.md` - Reference TDD (domain event patterns)

---

**End of Technical Design Document**
