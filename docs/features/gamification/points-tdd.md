# Points & Levels — Technical Design Document

**Feature:** Points & Levels
**Module:** Leaderboards (Gamification)
**Status:** Draft
**Version:** 1.0
**Last Updated:** February 15, 2026
**Bounded Context:** Gamification

---

## 1. Overview

### 1.1 Summary

The Points & Levels system rewards community members for engagement — liking, posting, commenting, and completing lessons — by awarding points that accumulate into a 9-level progression. Levels are displayed as badges on avatars throughout the platform and can gate access to courses.

This is a greenfield bounded context (`src/gamification/`) that consumes domain events from the Community and Classroom contexts and exposes read APIs consumed by Identity (profile display), Community (avatar badges), and Classroom (course access gating).

### 1.2 Goals

- Award points in response to engagement events from Community and Classroom contexts
- Calculate and maintain member levels with ratchet behavior (levels never decrease)
- Expose level data for avatar badge display across the platform
- Allow admins to configure level names and point thresholds per community
- Enable level-based course access gating

### 1.3 Non-Goals

- Leaderboard views (separate feature: `gamification/leaderboards`)
- Real-time point notifications or level-up animations
- Manual point adjustment by admins
- Point decay, expiration, or multipliers
- Achievement badges system
- Gamification on/off toggle

---

## 2. Architecture

### 2.1 System Context

```
┌──────────────┐       ┌──────────────┐
│  Community   │       │  Classroom   │
│              │       │              │
│ PostCreated  │       │ LessonCompl. │
│ CommentAdded │       │              │
│ PostLiked    │       └──────┬───────┘
│ PostUnliked  │              │
│ CommentLiked │              │ Events
│ CommentUnlkd │              │
└──────┬───────┘              │
       │ Events               │
       │                      │
       ▼                      ▼
┌─────────────────────────────────────┐
│          GAMIFICATION               │
│                                     │
│  ┌─────────────┐  ┌──────────────┐  │
│  │ Point       │  │ Level        │  │
│  │ Ledger      │  │ Configuration│  │
│  │ (Aggregate) │  │ (Aggregate)  │  │
│  └─────────────┘  └──────────────┘  │
│                                     │
└───────────┬─────────────────────────┘
            │ Read APIs (query)
            ▼
   ┌────────────────────┐
   │  Consumers         │
   │  - Avatar badges   │
   │  - Profile level   │
   │  - Course gating   │
   │  - Level defs grid │
   └────────────────────┘
```

### 2.2 Component Architecture

The Gamification context follows the established hexagonal architecture:

```
src/gamification/
├── domain/
│   ├── entities/         # MemberPoints (aggregate root)
│   ├── value_objects/    # PointTransaction, LevelNumber, LevelName, etc.
│   ├── events/           # PointsAwarded, PointsDeducted, MemberLeveledUp
│   └── repositories/     # Interfaces: MemberPointsRepository, LevelConfigRepository
├── application/
│   ├── commands/         # AwardPoints, DeductPoints, UpdateLevelConfig
│   ├── queries/          # GetMemberLevel, GetLevelDefinitions, CheckCourseAccess
│   └── event_handlers/   # Handlers for Community/Classroom events
├── infrastructure/
│   ├── persistence/      # SQLAlchemy models, repository implementations
│   └── api/              # FastAPI routes
└── interface/            # (empty for now — CLI not needed)
```

### 2.3 DDD Design

**Aggregates:**

1. **MemberPoints** — The primary aggregate root. Represents a member's point balance and level within a community. Owns point transactions and enforces business rules (non-negative balance, ratchet behavior, deduplication of lesson completions).

2. **LevelConfiguration** — Per-community configuration of the 9 levels (names and thresholds). Enforces validation rules (strictly increasing thresholds, unique names, character limits). Seeded with defaults on first access.

**Design decision:** Two aggregates rather than one because:
- They have different consistency boundaries — point awards are high-frequency per-member operations while level configuration changes are rare admin operations affecting all members
- Different access patterns — MemberPoints is queried per-member, LevelConfiguration per-community
- Separating them avoids lock contention between point awards and config changes

### 2.4 Integration Points

**Inbound (event subscribers):**
- Community → Gamification: `PostCreated`, `PostLiked`, `PostUnliked`, `CommentAdded`, `CommentLiked`, `CommentUnliked`
- Classroom → Gamification: `LessonCompleted`

**Outbound (published events):**
- `PointsAwarded` — consumed by future Notification context
- `PointsDeducted` — consumed by future Notification context
- `MemberLeveledUp` — consumed by future Notification context, potential future feed auto-post

**Read APIs (query endpoints):**
- Member level and points — consumed by profile display, avatar badges
- Level definitions — consumed by leaderboards page
- Course access check — consumed by Classroom context

**Important:** The existing events from Community (`PostLiked`, `PostUnliked`, etc.) carry the `user_id` of the actor (the liker), but point awards go to the *content author*. The event handlers need the author's user ID, which is available via `PostCreated.author_id` for posts and `CommentAdded.author_id` for comments. For like/unlike events, the handler must look up the content author. Two approaches:

- **Option A (chosen):** Add `author_id` field to `PostLiked`/`CommentLiked`/`PostUnliked`/`CommentUnliked` events in Community context — the Community context already knows the author when publishing the event.
- **Option B (rejected):** Have Gamification query Community for the author — violates context boundaries, creates coupling.

Enriching the Community events with `author_id` is the cleaner approach since the Community context already has this information at publish time, and it keeps the Gamification context from depending on Community's read APIs.

---

## 3. Technology Stack

### 3.1 Backend

No new dependencies required. The feature uses the existing stack:
- **SQLAlchemy (async)** — persistence layer, matching existing patterns
- **Alembic** — schema migrations
- **FastAPI** — API endpoints
- **Pydantic** — request/response schemas
- **Bleach** — HTML sanitization for admin-configured level names

### 3.2 Frontend

No new dependencies required. Uses existing:
- **React + TypeScript** — component framework
- **TailwindCSS** — styling (following UI_SPEC)
- **Heroicons/Lucide** — lock and clock icons (whichever the project already uses)

### 3.3 Infrastructure

- **PostgreSQL** — two new tables in the existing database (gamification context owns its tables)
- **In-memory EventBus** — existing `src/shared/infrastructure/event_bus.py` for event subscription

**Design decision: No Redis caching in MVP.** Member level data is small (one row per member per community) and will be fetched alongside existing profile/avatar queries. If performance targets (< 200ms profile load) are missed, we can add caching in a follow-up.

---

## 4. Data Model

### 4.1 Conceptual Schema

Two tables, owned by the Gamification context:

**`member_points`** — One row per member per community. Stores the running total and the highest level ever achieved.

| Column | Type | Purpose |
|--------|------|---------|
| id | UUID PK | Aggregate identity |
| community_id | UUID | Which community |
| user_id | UUID | Which member |
| total_points | INTEGER | Current accumulated points (≥ 0) |
| current_level | SMALLINT | Highest level ever achieved (1-9, ratchet) |
| created_at | TIMESTAMPTZ | When the record was created |
| updated_at | TIMESTAMPTZ | Last modification time |

- **Unique constraint:** `(community_id, user_id)` — one record per member per community
- **Index:** `(community_id, current_level)` — for level distribution queries (% of members at each level)
- **Index:** `(community_id, total_points DESC)` — for future leaderboard queries

**`point_transactions`** — Append-only audit log of every point change.

| Column | Type | Purpose |
|--------|------|---------|
| id | UUID PK | Transaction identity |
| member_points_id | UUID FK | References member_points |
| points | INTEGER | Amount (+N for award, -N for deduction) |
| source | VARCHAR(30) | Enum: post_created, comment_created, post_liked, comment_liked, lesson_completed |
| source_id | UUID | ID of the triggering entity (post_id, comment_id, lesson_id) |
| created_at | TIMESTAMPTZ | When the transaction occurred |

- **Index:** `(member_points_id, created_at DESC)` — for future point history queries
- **Unique constraint:** `(member_points_id, source, source_id)` WHERE `source = 'lesson_completed'` — prevents duplicate lesson completion points (partial unique index)

**`level_configurations`** — Per-community level names and thresholds.

| Column | Type | Purpose |
|--------|------|---------|
| id | UUID PK | Configuration identity |
| community_id | UUID | Which community (unique) |
| levels | JSONB | Array of 9 objects: `[{level, name, threshold}]` |
| created_at | TIMESTAMPTZ | When created |
| updated_at | TIMESTAMPTZ | Last modification |

- **Unique constraint:** `(community_id)` — one configuration per community

**Design decision: JSONB for levels vs. 9 rows.** Chose JSONB because:
- Levels are always read/written together as a complete set
- Validation (strictly increasing thresholds, unique names) is easier on the full array
- Avoids 9 JOINs or sub-queries; single fetch returns the full configuration
- The 9-level structure is fixed (PRD requirement) so the schema won't evolve
- Alternative considered: A `level_definitions` table with one row per level per community — rejected as over-normalized for a fixed-size, always-together dataset

### 4.2 Relationships

- `member_points` → `point_transactions`: One-to-many (a member has many transactions)
- `level_configurations` → `member_points`: Logical only — level config is referenced during level calculation but no FK needed (different aggregates)
- No FK references to other contexts' tables (Community, Classroom, Identity) — only UUIDs stored as values

### 4.3 Migrations

- Single Alembic migration creating all three tables
- Seed default level configuration on first community access (application-level, not migration-level) — avoids needing to know community IDs at migration time

---

## 5. API Design

### 5.1 Endpoint Overview

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| GET | `/api/communities/{id}/members/{user_id}/level` | Member | Get member's level and points |
| GET | `/api/communities/{id}/levels` | Member | Get level definitions with member distribution |
| PUT | `/api/communities/{id}/levels` | Admin | Update level names and thresholds |
| GET | `/api/communities/{id}/courses/{course_id}/access` | Member | Check if member can access course |
| PUT | `/api/communities/{id}/courses/{course_id}/level-requirement` | Admin | Set minimum level for course |

### 5.2 Request/Response Contracts

**GET `/api/communities/{id}/members/{user_id}/level`**

Response:
```json
{
  "user_id": "uuid",
  "level": 3,
  "level_name": "Builder",
  "total_points": 45,
  "points_to_next_level": 15,
  "is_max_level": false
}

```

- `points_to_next_level` only included when requester is viewing own profile AND not max level
- For other members' profiles: `points_to_next_level` is `null`

**GET `/api/communities/{id}/levels`**

Response:
```json
{
  "levels": [
    {
      "level": 1,
      "name": "Student",
      "threshold": 0,
      "member_percentage": 50.0
    },
    ...
  ],
  "current_user_level": 3
}
```

**PUT `/api/communities/{id}/levels`**

Request:
```json
{
  "levels": [
    { "level": 1, "name": "Beginner", "threshold": 0 },
    { "level": 2, "name": "Explorer", "threshold": 20 },
    ...
  ]
}
```

- Level 1 threshold must be 0
- Thresholds must be strictly increasing
- Names must be 1-30 chars, unique, sanitized

**GET `/api/communities/{id}/courses/{course_id}/access`**

Response:
```json
{
  "has_access": false,
  "required_level": 3,
  "required_level_name": "Builder",
  "current_level": 2
}
```

**PUT `/api/communities/{id}/courses/{course_id}/level-requirement`**

Request:
```json
{
  "minimum_level": 3
}
```

- `minimum_level` is 1-9 (or `null` to remove requirement)

### 5.3 Authentication/Authorization

All endpoints require JWT authentication (existing middleware). Admin endpoints require `ADMIN` role on the community. Member endpoints require community membership.

### 5.4 Error Handling

| Error | HTTP Status | Code |
|-------|------------|------|
| Not authenticated | 401 | `UNAUTHENTICATED` |
| Not a community member | 403 | `FORBIDDEN` |
| Not an admin (for admin endpoints) | 403 | `FORBIDDEN` |
| Invalid level name (empty, too long, duplicate) | 422 | `VALIDATION_ERROR` |
| Non-increasing thresholds | 422 | `VALIDATION_ERROR` |
| Level 1 threshold not zero | 422 | `VALIDATION_ERROR` |
| Invalid minimum_level (not 1-9) | 422 | `VALIDATION_ERROR` |
| Community not found | 404 | `NOT_FOUND` |
| Course not found | 404 | `NOT_FOUND` |

### 5.5 API Design Decisions

**Course level requirement as separate endpoint vs. extending Course API:**

Chose a dedicated endpoint under the gamification API (`/communities/{id}/courses/{course_id}/level-requirement`) rather than adding a field to the existing Course CRUD endpoints in the Classroom context. Rationale:
- Keeps Classroom context unaware of gamification concepts
- Admin sets level requirement through gamification settings, not course editing
- The access check endpoint is in gamification because it owns the level data

**Alternative considered:** Adding `minimum_level` to the Course entity in Classroom — rejected because it would create a dependency from Classroom to Gamification concepts, violating context boundaries.

**Where to store course level requirements:** In the Gamification context's database, not in the Classroom's courses table. A new `course_level_requirements` row or column on a gamification-owned table.

**Revised data model addition:**

**`course_level_requirements`** — Maps courses to their minimum level.

| Column | Type | Purpose |
|--------|------|---------|
| id | UUID PK | Row identity |
| community_id | UUID | Which community |
| course_id | UUID | Which course (references Classroom, no FK) |
| minimum_level | SMALLINT | Required level (1-9) |
| created_at | TIMESTAMPTZ | When set |
| updated_at | TIMESTAMPTZ | Last modification |

- **Unique constraint:** `(community_id, course_id)`

---

## 6. Domain Model

### 6.1 Aggregates

**MemberPoints (Aggregate Root)**

- Represents a member's point balance and level within a community
- Identified by its own UUID; uniquely constrained by (community_id, user_id)
- Contains the list of point transactions as child entities
- Enforces invariants:
  - Total points ≥ 0
  - Level = highest level ever achieved (ratchet)
  - Lesson completion points awarded only once per lesson

Key behaviors:
- `award_points(amount, source, source_id, level_config)` — adds points, recalculates level, publishes events
- `deduct_points(amount, source, source_id, level_config)` — removes points (floor at 0), level unchanged (ratchet)
- `recalculate_level(level_config)` — called when admin changes thresholds; updates level respecting ratchet

**LevelConfiguration (Aggregate Root)**

- Represents the 9-level configuration for a community
- Identified by its own UUID; uniquely constrained by community_id
- Enforces invariants:
  - Exactly 9 levels
  - Level 1 threshold = 0
  - Thresholds strictly increasing
  - Names 1-30 chars, unique, no HTML

Key behaviors:
- `update_levels(level_updates)` — validates and applies name/threshold changes
- `get_level_for_points(points)` — returns which level a given point total maps to
- `threshold_for_level(level)` — returns the points needed for a specific level

### 6.2 Value Objects

**PointTransaction**
- Represents a single point change (positive or negative)
- Properties: points (int), source (enum), source_id (UUID), created_at
- Immutable once created

**LevelNumber**
- Integer 1-9
- Validated at construction

**LevelName**
- String 1-30 characters
- Sanitized (no HTML tags)
- Validated at construction

**PointSource (Enum)**
- `POST_CREATED` = 2 points
- `COMMENT_CREATED` = 1 point
- `POST_LIKED` = 1 point
- `COMMENT_LIKED` = 1 point
- `LESSON_COMPLETED` = 5 points

The point values are hardcoded in the enum (not admin-configurable in MVP).

### 6.3 Domain Events

**PointsAwarded**
- member_id, community_id, points, new_total, source

**PointsDeducted**
- member_id, community_id, points, new_total, source

**MemberLeveledUp**
- member_id, community_id, old_level, new_level, new_level_name

### 6.4 Invariants

1. A member's total points can never be negative
2. A member's level can never decrease (ratchet rule)
3. A member can only receive lesson completion points once per lesson
4. Level thresholds must be strictly increasing (0 < L2 < L3 < ... < L9)
5. Level names must be unique within a community
6. There are always exactly 9 levels

### 6.5 Design Patterns

- **Event Sourcing (light):** Point transactions form an append-only log, but the current total is stored as a materialized value on the aggregate for fast reads. This is not full event sourcing — the transactions are for audit, not for state reconstruction.
- **Ratchet pattern:** Level calculation uses `max(current_level, calculated_level)` to enforce monotonic progression.
- **Lazy initialization:** LevelConfiguration for a community is created with defaults on first access if it doesn't exist (factory method), avoiding a migration that needs to enumerate all communities.

---

## 7. Application Layer

### 7.1 Commands

**AwardPointsCommand**
- Triggered by event handlers when engagement events arrive
- Loads MemberPoints aggregate (or creates with defaults if first interaction)
- Calls `award_points()` on the aggregate
- Persists the aggregate
- Publishes domain events (PointsAwarded, possibly MemberLeveledUp)

**DeductPointsCommand**
- Triggered by unlike event handlers
- Same flow as award but calls `deduct_points()`
- Publishes PointsDeducted event

**UpdateLevelConfigCommand**
- Triggered by admin API endpoint
- Loads LevelConfiguration aggregate
- Validates and applies changes
- If thresholds changed: loads all MemberPoints for the community and recalculates levels
- Persists all changes
- Publishes MemberLeveledUp events for any members who leveled up

**SetCourseLevelRequirementCommand**
- Triggered by admin API endpoint
- Validates minimum_level (1-9 or null)
- Stores/updates the requirement

### 7.2 Queries

**GetMemberLevelQuery**
- Input: community_id, user_id, requesting_user_id
- Returns: level, level_name, total_points, points_to_next_level (if viewing own)
- Joins MemberPoints with LevelConfiguration for names

**GetLevelDefinitionsQuery**
- Input: community_id, requesting_user_id
- Returns: all 9 levels with names, thresholds, and member distribution percentages
- Distribution calculated as: `COUNT(member_points WHERE current_level = X) / COUNT(member_points)` per community

**CheckCourseAccessQuery**
- Input: community_id, course_id, user_id
- Returns: has_access (bool), required_level, current_level

### 7.3 Event Handlers

Event handlers subscribe to events from Community and Classroom contexts via the EventBus and dispatch to the appropriate command:

| Source Event | Command | Points |
|--------------|---------|--------|
| PostCreated | AwardPointsCommand | +2 to author_id |
| CommentAdded | AwardPointsCommand | +1 to author_id |
| PostLiked | AwardPointsCommand | +1 to post author |
| CommentLiked | AwardPointsCommand | +1 to comment author |
| PostUnliked | DeductPointsCommand | -1 from post author |
| CommentUnliked | DeductPointsCommand | -1 from comment author |
| LessonCompleted | AwardPointsCommand | +5 to user_id |

**Author resolution for like events:** As noted in Section 2.4, `PostLiked` and `CommentLiked` events carry the liker's `user_id` but not the content author's ID. The Community events need to be enriched with an `author_id` field. This is a minor modification to the existing Community domain events.

### 7.4 Event Flow

```
Bob likes Alice's post
    │
    ▼
Community publishes PostLiked(user_id=Bob, author_id=Alice, post_id=...)
    │
    ▼
Gamification event handler receives PostLiked
    │
    ▼
AwardPointsCommand(user_id=Alice, points=1, source=POST_LIKED, source_id=post_id)
    │
    ▼
MemberPoints.award_points() → total=11, level 1→2
    │
    ├─► PointsAwarded event published
    └─► MemberLeveledUp event published (level 1→2)
```

---

## 8. Integration Strategy

### 8.1 Cross-Context Communication

**Inbound:** All integration is via the in-memory EventBus (`src/shared/infrastructure/event_bus.py`). Gamification registers handlers for Community and Classroom events at application startup. This is the established pattern in the codebase.

**Outbound:** Gamification publishes its own events (PointsAwarded, MemberLeveledUp) to the same EventBus. No consumers exist yet in MVP, but the events are published for future use (Notification context, leaderboard updates).

**Read access:** Other contexts (Community for avatar badges, Classroom for course gating) call Gamification's query endpoints via HTTP API. There is no direct import of Gamification domain objects from other contexts.

### 8.2 Community Event Enrichment

The existing `PostLiked`, `PostUnliked`, `CommentLiked`, and `CommentUnliked` events need an `author_id: UserId` field added. This is a non-breaking change (adding a field to a frozen dataclass). The Community context already has the author information available when publishing these events.

### 8.3 Failure Modes

| Failure | Impact | Handling |
|---------|--------|----------|
| EventBus handler throws | Point not awarded | Log error, do not retry (in-memory bus). The triggering action (like, post, etc.) still succeeds. Points may be slightly inaccurate but this is acceptable in MVP. |
| Database write fails | Point not persisted | Raise exception, let the originating request's transaction handle rollback. |
| Level config not found | Cannot calculate level | Create default config on first access (lazy init). |
| Concurrent point awards | Race condition | Optimistic locking (version column on member_points) or database-level `SELECT ... FOR UPDATE`. |

**Concurrency design decision:** Use `SELECT ... FOR UPDATE` when updating member_points to prevent lost updates when a member receives multiple likes simultaneously. This is simpler than optimistic locking and acceptable since the lock scope is narrow (single member row, brief hold time).

---

## 9. Security Design

### 9.1 Authentication

All endpoints require valid JWT token (existing middleware). Point-awarding operations are triggered by server-side event handlers, not by user-facing API calls, so there is no user-facing "award myself points" endpoint.

### 9.2 Authorization

| Operation | Requirement |
|-----------|-------------|
| View own level/points | Authenticated + community member |
| View other member's level | Authenticated + community member |
| View level definitions | Authenticated + community member |
| Update level config | Authenticated + community admin |
| Set course level requirement | Authenticated + community admin |

### 9.3 Input Validation

- **Level names:** Sanitized with bleach (strip HTML tags), length validated (1-30 chars), uniqueness checked within community
- **Point thresholds:** Positive integers, strictly increasing sequence, Level 1 locked at 0
- **Course minimum level:** Integer 1-9 validated server-side

### 9.4 Threat Model

| Threat | Mitigation |
|--------|-----------|
| XSS via level names | Bleach sanitization on input |
| Point manipulation (self-liking) | Enforced by Community context (self-likes prevented) |
| Point farming (rapid actions) | Rate limiting on source actions (200 likes/hr, 10 posts/hr) — existing Community limits |
| Privilege escalation (member modifying config) | Role-based access control on admin endpoints |
| IDOR (viewing other community's data) | All queries scoped by community_id with membership verification |

---

## 10. Performance & Scalability

### 10.1 Performance Targets

| Operation | Target (p95) |
|-----------|-------------|
| Point award (event handler) | < 500ms |
| Level calculation | < 100ms |
| Profile load with level | < 200ms |
| Level definitions with distribution | < 300ms |

### 10.2 Query Optimization

- **Member level lookup:** Single row fetch by `(community_id, user_id)` unique index — effectively O(1)
- **Level distribution:** `GROUP BY current_level` on `community_id` index — scans member_points rows for that community. Acceptable for communities up to ~100K members.
- **Future leaderboard:** Index on `(community_id, total_points DESC)` supports ORDER BY queries

### 10.3 Caching Strategy

**MVP: No caching.** Rationale:
- Member level is a single-row lookup (fast)
- Level configuration is rarely changed and small (9 entries)
- Level distribution query is only called on the leaderboards page (low frequency)

**Future consideration:** If avatar badge rendering causes N+1 queries on feeds with many posts, consider:
- Batch loading member levels for all authors on a feed page
- Redis cache for `community:{id}:member:{user_id}:level` with short TTL (60s)

### 10.4 Scalability Considerations

The main bottleneck is the `SELECT ... FOR UPDATE` lock on member_points during concurrent point awards. For a member receiving hundreds of likes in rapid succession, awards will be serialized. This is acceptable because:
- Lock hold time is minimal (read, increment, write)
- Only one member's row is locked at a time
- The originating action (liking) has its own rate limit (200/hr)

---

## 11. Error Handling

### 11.1 Error Taxonomy

**Domain Exceptions:**
- `InvalidLevelNameError` — name empty, too long, contains HTML, or duplicate
- `InvalidThresholdError` — thresholds not strictly increasing, Level 1 not zero, or non-positive
- `InvalidLevelNumberError` — level not 1-9
- `InsufficientLevelError` — member doesn't meet course level requirement
- `DuplicateLessonCompletionError` — lesson already completed (suppressed, not exposed to user)

### 11.2 HTTP Mapping

| Domain Exception | HTTP Status | User Message |
|-----------------|------------|--------------|
| InvalidLevelNameError | 422 | Specific message (e.g., "Level name must be 30 characters or less") |
| InvalidThresholdError | 422 | Specific message (e.g., "Thresholds must be strictly increasing") |
| InsufficientLevelError | 403 | "Unlock at Level {X} - {Name}" |
| DuplicateLessonCompletionError | N/A | Silently ignored (no user-facing impact) |

### 11.3 User Feedback

- Point awards happen silently (no toast in MVP) — members see updated totals on profile
- Level-ups are reflected immediately in the avatar badge
- Admin config errors return clear validation messages
- Course access denial shows the specific level required

---

## 12. Testing Strategy

### 12.1 BDD Tests

The BDD spec (`tests/features/gamification/points.feature`) covers 32 scenarios across:
- Point earning (likes, posts, comments, lessons) — 7 scenarios
- Level progression (level-up, skipping, ratchet) — 5 scenarios
- Level display (badge, profile, definitions) — 5 scenarios
- Course access gating — 5 scenarios
- Admin configuration — 4 scenarios
- Validation errors — 4 scenarios
- Security — 4 scenarios
- Edge cases — 3 scenarios

### 12.2 Unit Tests

Domain logic requiring focused unit tests:
- MemberPoints.award_points — various point amounts, level transitions
- MemberPoints.deduct_points — floor at 0, ratchet preservation
- LevelConfiguration validation — threshold ordering, name uniqueness, character limits
- Level calculation — boundary conditions (exactly at threshold, one below)
- Lesson deduplication logic

### 12.3 Integration Tests

- Event handler wiring — verify each Community/Classroom event triggers the correct command
- Repository persistence — CRUD operations, unique constraints, concurrent updates
- API endpoints — auth, authorization, request/response shapes, error responses
- Level recalculation after threshold change — verify all members updated correctly

---

## 13. Observability

### 13.1 Logging (structlog)

| Event | Level | Fields |
|-------|-------|--------|
| Points awarded | INFO | user_id, community_id, points, new_total, source |
| Points deducted | INFO | user_id, community_id, points, new_total, source |
| Member leveled up | INFO | user_id, community_id, old_level, new_level |
| Level config updated | INFO | community_id, admin_id, changes |
| Duplicate lesson completion ignored | DEBUG | user_id, lesson_id |
| Event handler error | ERROR | event_type, error, traceback |

### 13.2 Metrics

| Metric | Type | Purpose |
|--------|------|---------|
| `gamification.points.awarded` | Counter | Track point volume by source |
| `gamification.points.deducted` | Counter | Track deductions |
| `gamification.levelups.total` | Counter | Level-up frequency |
| `gamification.level.distribution` | Gauge | Members per level (periodic) |

### 13.3 Tracing (OpenTelemetry)

- Span: `gamification.award_points` — traces from event receipt through persistence
- Span: `gamification.check_course_access` — traces access check flow
- Span: `gamification.recalculate_levels` — traces bulk recalculation (admin threshold change)

---

## 14. Deployment Strategy

### 14.1 Migration Plan

1. Run Alembic migration to create `member_points`, `point_transactions`, `course_level_requirements`, and `level_configurations` tables
2. Deploy backend with event handlers registered
3. Deploy frontend with level badge components
4. All existing members will be at Level 1 with 0 points (no backfill needed — the system starts fresh)

### 14.2 Rollback Plan

- Drop the three Gamification tables (no other contexts depend on them via FK)
- Remove event handler registrations
- Frontend gracefully handles missing level data (badge hidden when `level` is undefined, per UI_SPEC)

### 14.3 Feature Flags

Not needed for MVP — the feature is self-contained and additive. Avatar badges without level data render normally (backward-compatible `level?: number` prop).

---

## 15. Future Considerations

### 15.1 Phase 2 Enhancements

- **Leaderboards** (`gamification/leaderboards`) — will query `member_points` table with `ORDER BY total_points DESC`, leveraging the index already defined
- **Point history** — `point_transactions` table already supports this; just needs a UI and API endpoint
- **Manual point adjustment** — new command on MemberPoints aggregate

### 15.2 Known Limitations

- **No real-time updates:** Level badges update on page load, not via WebSocket push
- **No backfill:** Existing engagement before feature launch doesn't earn retroactive points
- **Event handler failures are not retried:** If the EventBus handler fails, the points are lost. For MVP this is acceptable. Production would benefit from a persistent event store with retry.

### 15.3 Technical Debt

- **In-memory EventBus:** Single-process, no persistence, no retry. Should move to a persistent broker (Redis Streams, PostgreSQL LISTEN/NOTIFY) before scaling
- **Community event enrichment:** Adding `author_id` to like/unlike events is a pragmatic shortcut. A more formal approach would be an Anti-Corruption Layer in Gamification that resolves authors, but that adds complexity and a cross-context dependency

---

## 16. Alignment Verification

See `docs/features/gamification/ALIGNMENT_VERIFICATION.md` for the complete PRD → BDD → TDD coverage mapping and gap analysis.

---

## 17. Appendices

### 17.1 File Checklist

**New files (Gamification context):**

```
src/gamification/
├── __init__.py
├── domain/
│   ├── __init__.py
│   ├── entities/
│   │   ├── __init__.py
│   │   └── member_points.py
│   ├── value_objects/
│   │   ├── __init__.py
│   │   ├── point_transaction.py
│   │   ├── point_source.py
│   │   ├── level_number.py
│   │   └── level_name.py
│   ├── events/
│   │   ├── __init__.py
│   │   └── gamification_events.py
│   ├── exceptions.py
│   └── repositories/
│       ├── __init__.py
│       ├── member_points_repository.py
│       └── level_config_repository.py
├── application/
│   ├── __init__.py
│   ├── commands/
│   │   ├── __init__.py
│   │   ├── award_points.py
│   │   ├── deduct_points.py
│   │   ├── update_level_config.py
│   │   └── set_course_level_requirement.py
│   ├── queries/
│   │   ├── __init__.py
│   │   ├── get_member_level.py
│   │   ├── get_level_definitions.py
│   │   └── check_course_access.py
│   └── event_handlers/
│       ├── __init__.py
│       ├── community_event_handlers.py
│       └── classroom_event_handlers.py
├── infrastructure/
│   ├── __init__.py
│   ├── persistence/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── member_points_repository.py
│   │   └── level_config_repository.py
│   └── api/
│       ├── __init__.py
│       ├── routes.py
│       └── schemas.py
```

**Modified files:**

```
src/community/domain/events.py          — Add author_id to PostLiked, PostUnliked, CommentLiked, CommentUnliked
src/community/domain/entities/post.py   — Include author_id when publishing like events (if not already available)
alembic/versions/xxx_add_gamification.py — New migration

frontend/src/components/Avatar.tsx              — Add optional level prop and LevelBadge overlay
frontend/src/features/gamification/             — New feature directory
  ├── components/
  │   ├── LevelBadge.tsx
  │   ├── LevelDefinitionsGrid.tsx
  │   ├── ProfileLevelSection.tsx
  │   └── CourseCardLock.tsx
  ├── api/
  │   └── gamificationApi.ts
  └── types/
      └── index.ts
frontend/src/features/identity/components/ProfileSidebar.tsx  — Integrate ProfileLevelSection
frontend/src/features/classroom/components/CourseCard.tsx      — Integrate CourseCardLock
```

### 17.2 Dependencies

No new Python or JavaScript packages required. All functionality is achievable with the existing stack.

### 17.3 References

- PRD: `docs/features/gamification/points-prd.md`
- BDD: `tests/features/gamification/points.feature`
- UI_SPEC: `docs/features/gamification/UI_SPEC.md`
- Context Map: `docs/architecture/CONTEXT_MAP.md`
- Domain Glossary: `docs/domain/GLOSSARY.md`
- EventBus: `src/shared/infrastructure/event_bus.py`
- Community Events: `src/community/domain/events.py`
- Classroom Events: `src/classroom/domain/events/progress_events.py`

---

## Approval

**Product Owner:** _________________
**Engineering Lead:** _________________
**Design Lead:** _________________

**Status:** Draft — Pending Review
