# User Profile - Technical Design Document

**Version:** 1.0
**Date:** February 5, 2026
**Status:** Draft
**Related PRD:** `profile-prd.md`
**Related BDD:** `tests/features/identity/profile.feature`
**Bounded Context:** Identity

---

## 1. Overview

### 1.1 Summary

This design extends the existing user profile system to support rich member identities through social links, geographic location, and activity visibility. The architecture enables public profile discovery while maintaining authorization boundaries and preparing for future community integration.

### 1.2 Goals

- Extend Profile entity with structured location and social links
- Enable public profile viewing for authenticated users
- Separate profile "completion" (one-time) from "updates" (ongoing)
- Design extensible activity/stats endpoints (empty states for MVP)
- Maintain hexagonal architecture and DDD principles
- Zero new frontend dependencies; one new backend dependency (sanitization)

### 1.3 Non-Goals

- Avatar file upload (requires S3 - Phase 2)
- Follow/unfollow relationships (separate social graph feature - Phase 2)
- Profile privacy controls (MVP assumption: all profiles public - Phase 2)
- Real-time activity updates (Phase 3)
- Profile badge system (requires gamification integration - Phase 2)

---

## 2. Architecture

### 2.1 System Context

```
┌──────────────────────────────────────────────────────────┐
│                    Koulu Platform                         │
│                                                           │
│  ┌────────────────────────────────────────────────────┐  │
│  │         Identity Context (Extended)                │  │
│  │                                                     │  │
│  │  ┌──────────┐       ┌──────────────────┐          │  │
│  │  │  User    │───────│  Profile         │          │  │
│  │  │Aggregate │       │  (Entity)        │          │  │
│  │  └──────────┘       │  + location ◄──NEW         │  │
│  │       │             │  + social_links ◄──NEW     │  │
│  │       │             └──────────────────┘          │  │
│  │       │                                            │  │
│  │       │ ProfileCompleted, ProfileUpdated ◄──NEW   │  │
│  └────────────────────────────────────────────────────┘  │
│                       │                                   │
│                       │ Domain Events                     │
│                       ▼                                   │
│  ┌────────────────────────────────────────────────────┐  │
│  │            Future Contexts                          │  │
│  │  Community - Activity feed                          │  │
│  │  Gamification - Contribution stats                  │  │
│  │  Members - Profile directory                        │  │
│  │  Map - Location-based discovery                     │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

**Key Architectural Principles:**
- Profile remains within User aggregate boundary
- Cross-context communication via domain events only
- Activity/stats endpoints designed for future integration (return empty now)
- No direct database joins across contexts

### 2.2 Component Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Interface Layer                        │
│  user_controller.py                                      │
│    + GET /users/{id}/profile ◄──NEW                     │
│    + PATCH /users/me/profile ◄──NEW                     │
│    + GET /users/{id}/activity ◄──NEW (placeholder)      │
│    + GET /users/{id}/stats ◄──NEW (placeholder)         │
├─────────────────────────────────────────────────────────┤
│                  Application Layer                       │
│  Commands:                                               │
│    UpdateProfile ◄──NEW                                  │
│  Queries:                                                │
│    GetProfile ◄──NEW                                     │
│    GetProfileActivity ◄──NEW (returns empty)             │
│    GetProfileStats ◄──NEW (returns zero)                 │
│  Handlers:                                               │
│    UpdateProfileHandler ◄──NEW                           │
│    GetProfileHandler ◄──NEW                              │
├─────────────────────────────────────────────────────────┤
│                    Domain Layer                          │
│  Entities:                                               │
│    Profile (extend with location, social_links)          │
│  Value Objects:                                          │
│    Location ◄──NEW (city + country)                      │
│    SocialLinks ◄──NEW (4 URL fields)                     │
│    Bio ◄──NEW (validated, sanitized text)                │
│  Events:                                                 │
│    ProfileUpdated ◄──NEW                                 │
├─────────────────────────────────────────────────────────┤
│                Infrastructure Layer                      │
│  ProfileModel: Add 6 columns (location×2, social×4)      │
│  ProfileRepository: Extend entity<->model mapping        │
└─────────────────────────────────────────────────────────┘
```

**Design Decision: Extend vs Replace**
- **Chosen:** Extend existing CompleteProfile with new fields
- **Rationale:** Backward compatible, no breaking changes, existing flows intact
- **Alternative:** Separate ProfileSetup from ProfileUpdate commands
  - Rejected: Unnecessary complexity, same validation rules apply

### 2.3 Domain-Driven Design

**Aggregates:**
- **User** (Aggregate Root) - Continues to own Profile lifecycle
  - Profile is entity within User aggregate (not separate aggregate)
  - User enforces profile consistency boundaries
  - All profile mutations go through User aggregate

**Value Objects (New):**

**Location**
- Represents geographic position (city + country)
- **Invariant:** Both fields required together (no partial location)
- **Rationale:** Future Map feature needs structured data, not free text
- **Validation:** 2-100 chars each, no HTML/script tags
- Immutable once created

**SocialLinks**
- Collection of external profile URLs (Twitter, LinkedIn, Instagram, Website)
- **Design Decision:** 4 explicit fields vs generic list
  - Chose explicit fields: Type-safe, queryable, UI can render specific icons
  - Rejected generic list: Loses semantic meaning, hard to query "find all LinkedIn profiles"
- All fields optional, validated when present
- Immutable (replace entire object on update)

**Bio**
- User's self-description text
- **Security Concern:** XSS attack vector
- **Mitigation:** HTML sanitization on construction (bleach library)
- Max 500 characters (prevents abuse, ensures UI readability)

**Domain Events (New):**

**ProfileUpdated**
- Published whenever profile fields change
- Contains: user_id, list of changed field names, timestamp
- **Design Decision:** Single generic event vs specific events (BioUpdated, LocationUpdated...)
  - Chose single event: Simpler event handling, fewer subscribers, bulk updates publish once
  - Tradeoff: Subscribers must check changed_fields list
- Enables:
  - Analytics tracking (which fields users actually fill)
  - Notification system (future: "X updated their profile")
  - Cache invalidation

---

## 3. Technology Stack

### 3.1 Backend Dependencies

**Existing (Reused):**
- FastAPI, SQLAlchemy, Pydantic - Already installed, no changes needed
- slowapi - Rate limiting (already configured)

**New Dependency:**

**bleach (^6.1.0)**
- **Purpose:** HTML/script tag sanitization for XSS prevention
- **Why This Library:**
  - Mozilla-maintained (Firefox, Thunderbird security team)
  - Battle-tested 10+ years in production (PyPI, Reddit, GitHub use it)
  - OWASP recommended for Python HTML sanitization
  - Whitelist-based (secure by default)
  - Actively maintained (last release: 2025-01)
- **Alternatives Considered:**
  - `html.escape()` - Too basic, doesn't handle nested tags or attributes
  - Custom regex - Historically dangerous (regex can't parse HTML reliably)
  - `nh3` (Rust-based) - Faster but less mature Python ecosystem
- **Research:** https://bleach.readthedocs.io/en/latest/
- **Usage Pattern:** Apply in Bio value object constructor (domain layer)

### 3.2 Frontend Dependencies

**No New Dependencies Required**
- react-hook-form - Form handling (already installed)
- zod - Schema validation (already installed)
- @tanstack/react-query - Data fetching (already installed)

**Design Decision: Avatar Upload**
- **Out of Scope:** File upload requires S3 integration (Phase 2)
- **MVP Solution:** URL input only
  - Users can host images elsewhere (Imgur, Gravatar, etc.)
  - Avoids S3 setup, file size validation, image processing
  - Faster MVP delivery

---

## 4. Data Model

### 4.1 Conceptual Schema

**Extend `profiles` table with 6 new columns:**

| Column | Type | Nullable | Purpose |
|--------|------|----------|---------|
| location_city | String(100) | Yes | City name |
| location_country | String(100) | Yes | Country name |
| twitter_url | String(500) | Yes | Twitter/X profile |
| linkedin_url | String(500) | Yes | LinkedIn profile |
| instagram_url | String(500) | Yes | Instagram profile |
| website_url | String(500) | Yes | Personal website |

**Design Decision: Columns vs JSON**

**Chosen:** Separate columns for each social link

**Rationale:**
- **Queryability:** Can index/filter by specific platform (e.g., "find all users with LinkedIn")
- **Type Safety:** Database enforces column existence, no JSON parsing errors
- **Partial Indexes:** PostgreSQL can create conditional indexes (WHERE linkedin_url IS NOT NULL)
- **Migration Safety:** Easy to add/remove specific platforms without JSON schema versioning

**Alternative Rejected:** JSONB column for social_links
- **Pros:** Flexible schema, easy to add new platforms
- **Cons:**
  - Requires JSON extraction functions in queries (complex, slower)
  - No built-in validation at DB level
  - Indexes on JSONB fields are complex (GIN indexes, operator classes)
  - Harder for analytics queries

**Tradeoff:** More columns = wider table, but profile table is small (1 row per user) and rarely queried in bulk.

### 4.2 Indexes

**New Indexes:**

```
CREATE INDEX idx_profiles_location ON profiles(location_city, location_country)
  WHERE location_city IS NOT NULL;

CREATE INDEX idx_profiles_updated_at ON profiles(updated_at);
```

**Rationale:**

**Location Index (Composite, Partial):**
- **Query:** Future Map feature: "find members near Austin, USA"
- **Partial:** Only indexes rows with location set (~50% of users expected)
- **Composite:** City+Country together (common query pattern)
- **Benefit:** Reduces index size by 50%, speeds up Map queries

**Updated_At Index:**
- **Query:** "Recently active profiles" analytics
- **Query:** Cache invalidation (find profiles updated since timestamp)
- **Benefit:** Chronological ordering common in profile lists

### 4.3 Migration Strategy

**Zero-Downtime Migration:**
1. Add nullable columns (no default values needed)
2. Existing rows: new columns = NULL (expected)
3. Deploy application code (handles NULL gracefully)
4. No data backfill needed

**Rollback Plan:**
- Drop columns in reverse order
- Application falls back to existing fields (bio, display_name, avatar)

---

## 5. API Design

### 5.1 Endpoint Overview

**RESTful Resource Design:**

```
GET    /api/v1/users/{user_id}/profile       - View any user's profile
PATCH  /api/v1/users/me/profile              - Update own profile
GET    /api/v1/users/{user_id}/activity      - Get activity feed (placeholder)
GET    /api/v1/users/{user_id}/stats         - Get contribution stats (placeholder)
GET    /api/v1/users/{user_id}/activity-chart - Get 30-day activity data (placeholder)
```

**Design Decision: REST Verb Choice**
- **PATCH vs PUT** for updates:
  - Chose PATCH: Partial updates, clients send only changed fields
  - Rejected PUT: Requires full resource replacement, verbose payloads

**Design Decision: Separate vs Embedded Endpoints**
- **Separate /activity endpoint** vs embedding in /profile:
  - Chose separate: Activity changes frequently (cache separately), large payload
  - Benefit: Profile data cacheable for 5 min, activity for 1 min

### 5.2 Request/Response Contracts

**Profile Response:**
```json
{
  "user_id": "uuid",
  "display_name": "string",
  "avatar_url": "string?",
  "bio": "string?",
  "location": {
    "city": "string",
    "country": "string"
  } | null,
  "social_links": {
    "twitter_url": "string?",
    "linkedin_url": "string?",
    "instagram_url": "string?",
    "website_url": "string?"
  },
  "is_complete": "boolean",
  "created_at": "iso8601",
  "updated_at": "iso8601",
  "is_own_profile": "boolean"
}
```

**Design Decision: Nested Objects**
- **Location as object** (not flat city/country fields):
  - **Rationale:** Semantic grouping, client knows both fields required together
  - **Tradeoff:** More verbose, but clearer intent
- **SocialLinks as object** (not flat):
  - **Rationale:** Namespace (avoids "url1, url2" generic names), extensible

**Update Profile Request:**
```json
{
  "display_name": "string?",
  "avatar_url": "string?",
  "bio": "string?",
  "location": { "city": "string", "country": "string" } | null,
  "social_links": {
    "twitter_url": "string?",
    "linkedin_url": "string?",
    "instagram_url": "string?",
    "website_url": "string?"
  } | null
}
```

**Design Decision: Null Semantics**
- **Field omitted** = no change (PATCH behavior)
- **Field = null** = clear the field
- **location = null** = remove location entirely
- **location = {city: "X", country: "Y"}** = set/update location

### 5.3 Authentication & Authorization

**Authorization Model:**

| Endpoint | Auth Required | Authorization Rule |
|----------|---------------|-------------------|
| GET /users/{id}/profile | Yes | Any authenticated user (public profiles) |
| PATCH /users/me/profile | Yes | JWT user_id must match "me" (implicit) |
| GET /users/{id}/activity | Yes | Any authenticated user |
| GET /users/{id}/stats | Yes | Any authenticated user |

**Design Decision: Public Profiles**
- **Chosen:** All profiles visible to all authenticated users
- **Rationale:** Community platform needs discoverability, trust through visibility
- **Phase 2:** Add privacy settings (who can view my profile?)

**Security: Preventing Unauthorized Updates**
- PATCH endpoint uses `/users/me` (not `/users/{id}`)
- JWT token extraction provides user_id (can't be forged)
- No need for explicit "if user_id != profile.user_id" check (impossible by design)

### 5.4 Error Handling

**HTTP Status Code Mapping:**

| Domain Exception | HTTP Status | Response Body |
|-----------------|-------------|---------------|
| InvalidLocationError | 400 Bad Request | `{"detail": "Both city and country required"}` |
| InvalidSocialLinkError | 400 Bad Request | `{"detail": "Invalid URL format: {field}"}` |
| InvalidBioError | 400 Bad Request | `{"detail": "Bio exceeds 500 characters"}` |
| ProfileNotFoundError | 404 Not Found | `{"detail": "Profile not found"}` |
| Unauthenticated | 401 Unauthorized | `{"detail": "Authentication required"}` |
| RateLimitExceeded | 429 Too Many Requests | `{"detail": "Rate limit exceeded, retry in X seconds"}` |

**Design Principle:** Domain exceptions map to HTTP semantics
- 400: Client error (invalid input)
- 404: Resource not found
- 401: Authentication missing
- 429: Too many requests

---

## 6. Domain Model Design

### 6.1 Value Objects

**Location**
- **Purpose:** Structured geographic data for Map feature
- **Invariant:** City and country must both be present or both absent
- **Validation:** Length (2-100 chars), no HTML tags
- **Immutable:** Create new instance on change
- **Design Decision:** Structured vs Free Text
  - Chose structured: Enables map querying, prevents ambiguity ("NY" = New York or New Yemen?)
  - Tradeoff: User must pick from predefined format

**SocialLinks**
- **Purpose:** External identity verification, cross-platform connections
- **Validation:** URL format check using Pydantic HttpUrl
- **Immutable:** Replace entire object on update
- **Design Decision:** 4 explicit fields vs generic "links: [{platform, url}]"
  - Chose explicit: Type-safe, UI can show platform-specific icons
  - Tradeoff: Adding new platform requires code change (acceptable for MVP)

**Bio**
- **Purpose:** Self-description for profile visitors
- **Security:** XSS prevention via HTML sanitization
- **Validation:** Max 500 chars (UI readability constraint)
- **Sanitization Strategy:** Strip all HTML tags (not whitelist)
  - **Rationale:** Plain text only for MVP, Markdown support in Phase 2
  - **Implementation:** bleach.clean(text, tags=[], strip=True)

### 6.2 Aggregate Boundaries

**User Aggregate (unchanged):**
- User owns Profile (1:1 relationship)
- Profile cannot exist without User
- All profile mutations validated by User aggregate
- **Consistency Boundary:** Profile state always reflects User's latest changes

**Design Decision: Profile as Entity vs Separate Aggregate**
- **Chosen:** Profile as entity within User aggregate
- **Rationale:**
  - Profile lifecycle tied to User (cascade delete)
  - No independent profile operations (always "user updates their profile")
  - Transactional consistency (profile + user update must succeed/fail together)
- **Alternative Rejected:** Profile as separate aggregate
  - Requires eventual consistency (complex)
  - Distributed transactions (slow, error-prone)

### 6.3 Domain Events

**ProfileUpdated**
- **When:** Any field modification
- **Data:** user_id, changed_fields: ["bio", "location"], occurred_at
- **Consumers (Future):**
  - Analytics: Track field completion rates
  - Notifications: "X updated their profile" (Phase 2)
  - Cache: Invalidate profile caches

**Design Decision:** Granular vs Coarse Events
- **Alternative:** Separate events (BioUpdated, LocationUpdated, SocialLinksUpdated)
- **Rejected:** Too many event types, overwhelming subscribers
- **Chosen:** Single ProfileUpdated with changed_fields list
- **Tradeoff:** Subscribers must filter by changed_fields, but simpler overall

---

## 7. Application Layer Design

### 7.1 Commands

**UpdateProfile**
- **Intent:** User modifies one or more profile fields
- **Inputs:** user_id, optional fields (display_name, bio, location, social_links, avatar_url)
- **Orchestration:**
  1. Load User aggregate from repository
  2. Validate inputs (create value objects)
  3. User.update_profile(...) - enforces business rules
  4. Save User aggregate
  5. Publish ProfileUpdated event
- **Idempotency:** Repeated updates with same data = no-op (updated_at doesn't change)

### 7.2 Queries

**GetProfile**
- **Intent:** Retrieve user's profile for display
- **Inputs:** user_id, current_user_id (for is_own_profile flag)
- **Returns:** Profile entity with metadata
- **No Business Logic:** Simple data retrieval

**GetProfileActivity** (Placeholder)
- **Intent:** Future integration point for Community context
- **MVP Behavior:** Returns empty list `{items: [], total_count: 0}`
- **Design:** Pre-define contract so Community can implement later without breaking changes

**GetProfileStats** (Placeholder)
- **Intent:** Future integration point for Gamification context
- **MVP Behavior:** Returns `{contributions: 0, joined_at: user.created_at}`
- **Design:** Real contributions calculated by querying Community context (not stored)

### 7.3 Use Case Flow

**Profile Update Flow:**
```
[User] -> [UpdateProfile Command]
          |
          v
      [UpdateProfileHandler]
          |
          |--> Load User aggregate (repository)
          |--> Validate inputs (create value objects)
          |--> User.update_profile() (domain logic)
          |--> Save aggregate (repository)
          |--> Publish ProfileUpdated event
          |
          v
      [ProfileUpdated Event]
          |
          |--> Analytics Subscriber (track field usage)
          |--> Cache Invalidation Subscriber
          |--> [Future] Notification Subscriber
```

**Design Principle:** Handler orchestrates, Domain validates
- Handler = workflow (load, call domain, save, publish)
- Domain = business rules (validation, invariants)

---

## 8. Integration Strategy

### 8.1 Cross-Context Communication

**Event-Driven Integration:**

```
Identity Context                Community Context (Future)
     │                                │
     │  ProfileUpdated                │
     │─────────────────────────────>│
     │                                │
     │                                │
     │  GetProfileActivity Query      │
     │<───────────────────────────────│
     │  (empty list for now)          │
```

**Design Decision: Query vs Event for Activity**
- **Chosen:** Query pattern (pull model)
- **Rationale:**
  - Activity data lives in Community context (boundary)
  - Identity shouldn't store Community data (coupling)
  - On-demand query keeps contexts decoupled
- **Alternative Rejected:** ProfileActivityChanged event (push model)
  - Would require Identity to maintain activity cache (violates bounded context)

### 8.2 Future Community Integration

**When Community is built, it will:**
1. Implement GetProfileActivity query handler
2. Return user's posts/comments from its own database
3. Identity simply forwards the query (no data storage)

**No Changes Required in Identity:**
- Endpoint contract already defined
- Query handler already wired
- Just swap empty-list implementation with Community query client

---

## 9. Security Design

### 9.1 Threat Model

**Threats:**
1. **XSS via Bio Field**
   - Mitigation: HTML sanitization (bleach library) in Bio value object
   - Defense in depth: Content-Security-Policy headers (infrastructure)

2. **Profile Enumeration**
   - Threat: Attacker scrapes all profiles
   - Mitigation: Authentication required (can't scrape without account)
   - Rate limiting: 100 profile views per minute per user (slowapi)

3. **Unauthorized Profile Updates**
   - Mitigation: JWT-based auth, implicit user_id from token
   - Impossible to update another user's profile by design

4. **URL Injection in Social Links**
   - Mitigation: Pydantic HttpUrl validation (rejects javascript:, data: schemes)
   - Allows only http:// and https://

### 9.2 Input Validation Strategy

**Validation Layers:**
1. **API Layer (Pydantic):** Format validation (URL, length)
2. **Domain Layer (Value Objects):** Business rule validation, sanitization
3. **Database Layer (Constraints):** Final safety net (NOT NULL, length limits)

**Defense in Depth:** Multiple validation layers prevent bypass attacks

### 9.3 Rate Limiting

**Profile Update Endpoint:**
- Limit: 10 requests per hour per user
- Storage: Redis (key: `ratelimit:profile_update:{user_id}`, TTL: 1 hour)
- Reason: Prevent spam, abuse, excessive activity event publishing

**Profile View Endpoint:**
- Limit: 100 requests per minute per IP
- Storage: Redis (key: `ratelimit:profile_view:{ip}`, TTL: 1 min)
- Reason: Prevent profile scraping

---

## 10. Performance & Scalability

### 10.1 Performance Targets

| Operation | Target | Measurement |
|-----------|--------|-------------|
| Profile View (GET) | < 100ms p95 | Single DB query + cache hit |
| Profile Update (PATCH) | < 200ms p95 | DB write + event publish |
| Activity Query (placeholder) | < 50ms p95 | Empty list return |

### 10.2 Caching Strategy

**Profile Data:**
- **Cache:** Client-side (React Query), 5-minute TTL
- **Invalidation:** On ProfileUpdated event
- **Rationale:** Profile changes infrequently, high read/write ratio

**Activity Feed (future):**
- **Cache:** 1-minute TTL (more dynamic)
- **Rationale:** Activity changes frequently (new posts/comments)

**No Server-Side Caching (MVP):**
- PostgreSQL query performance sufficient for MVP scale (< 10K users)
- Redis caching added if query times exceed 100ms p95

### 10.3 Query Optimization

**Existing Optimization:**
- User + Profile loaded via single JOIN (registration-auth feature)
- Eager loading prevents N+1 queries

**New Indexes:**
- location composite index: O(log n) lookup for Map queries
- updated_at index: Chronological sorting

**Future Optimization (Phase 2):**
- Materialized view for "recently active profiles" (analytics)

---

## 11. Error Handling Design

### 11.1 Error Taxonomy

**Domain Exceptions:**
- `InvalidLocationError` - Location validation failure
- `InvalidSocialLinkError` - URL format validation failure
- `InvalidBioError` - Bio length/sanitization failure
- `ProfileNotFoundError` - User ID doesn't exist

**Infrastructure Exceptions:**
- `DatabaseError` - Persistence layer failure
- `RateLimitError` - Too many requests

**HTTP Error Mapping:**
- Domain exceptions → 400 Bad Request (client error)
- Not found → 404 Not Found
- Authentication → 401 Unauthorized
- Rate limit → 429 Too Many Requests

### 11.2 User-Facing Error Messages

**Design Principle:** Specific, actionable errors

**Examples:**
- ❌ "Invalid input" (vague)
- ✅ "City and country must both be provided, or both left empty" (actionable)

- ❌ "Validation failed" (vague)
- ✅ "Website URL must start with http:// or https://" (actionable)

---

## 12. Testing Strategy

### 12.1 BDD Scenarios (42 total)

**Coverage:**
- Profile completion: 10 scenarios (happy + validation)
- Profile viewing: 4 scenarios (own/other, not found)
- Profile updates: 14 scenarios (happy + validation)
- Activity/stats: 5 scenarios (placeholders)
- Security: 4 scenarios (auth, sanitization, rate limit)
- Edge cases: 5 scenarios (avatar handling, location handling)

**Test Data Strategy:**
- Factories for User and Profile entities
- Mocked Community queries (return empty until Community exists)

### 12.2 Unit Tests

**Domain Layer:**
- Value object validation (Location, SocialLinks, Bio)
- Profile entity mutation methods
- Domain event creation

**Application Layer:**
- Command handler orchestration
- Query handler data retrieval
- Event publishing

### 12.3 Integration Tests

**API Layer:**
- End-to-end HTTP requests (FastAPI TestClient)
- Auth middleware integration
- Rate limiting behavior

---

## 13. Observability

### 13.1 Logging

**Events to Log:**
- `profile_updated` - user_id, changed_fields, timestamp
- `profile_viewed` - viewer_id, target_user_id
- `validation_error` - error_type, field, user_id

**Structured Logging (JSON):**
```json
{
  "event": "profile_updated",
  "user_id": "uuid",
  "changed_fields": ["bio", "location"],
  "timestamp": "iso8601"
}
```

### 13.2 Metrics

**Track:**
- `profile_update_count` (counter) - Total updates
- `profile_view_count` (counter) - Total views
- `profile_completeness` (gauge) - % of optional fields filled (avg)
- `validation_error_rate` (counter) - By error type

**Analytics Questions:**
- Which social links do users actually fill? (adoption rate)
- What % of users set location? (Map feature viability)
- Average profile completeness? (engagement indicator)

### 13.3 Tracing (Future - Phase 2)

**OpenTelemetry Spans:**
- `UpdateProfile` command execution
- `GetProfile` query execution
- Database query latency
- Event publishing latency

---

## 14. Deployment Strategy

### 14.1 Migration Plan

**Step 1: Schema Migration**
```
1. Deploy migration (add 6 nullable columns)
2. Zero downtime (existing code unaffected)
3. Deploy application code
4. Existing profiles: new fields = NULL (expected)
```

**Step 2: Feature Flag (Optional)**
- Flag: `FEATURE_SOCIAL_LINKS_ENABLED`
- Allows gradual rollout
- Can disable if issues discovered

### 14.2 Rollback Plan

**If Needed:**
1. Revert application code
2. Run migration rollback (drop 6 columns)
3. No data loss (optional fields)

**Risk: Low** (additive change only)

---

## 15. Future Considerations

### 15.1 Phase 2 Enhancements

**Real Activity Data:**
- Community context implements GetProfileActivity
- Shows actual posts/comments
- Pagination support

**Avatar Upload:**
- S3 integration for file storage
- Image processing (resize, compress)
- URL generation

**Follow System:**
- Separate feature (social graph)
- Adds follower/following counts to profile

### 15.2 Known Limitations

**MVP Limitations:**
- Activity feed always empty (acceptable, design complete)
- Stats always zero contributions (acceptable, design complete)
- No profile privacy controls (Phase 2)
- No profile search (covered by Members feature)

### 15.3 Technical Debt

**None (Clean Architecture Maintained):**
- No shortcuts taken
- All patterns follow established codebase conventions
- Activity/stats endpoints properly designed (not hacks)

---

## 16. Alignment Verification

See `ALIGNMENT_VERIFICATION.md` for complete traceability:
- ✅ All 12 PRD acceptance criteria mapped to design
- ✅ All 42 BDD scenarios covered
- ✅ All 17 business rules enforced
- ✅ All 11 edge cases handled
- ✅ All security requirements addressed

---

## 17. Appendices

### Appendix A: File Changes

**Backend (New Files):**
```
src/identity/domain/value_objects/location.py
src/identity/domain/value_objects/social_links.py
src/identity/domain/value_objects/bio.py
src/identity/domain/events/profile_updated.py
src/identity/application/commands/update_profile.py
src/identity/application/handlers/update_profile_handler.py
src/identity/application/queries/get_profile.py
src/identity/application/queries/get_profile_activity.py
src/identity/application/queries/get_profile_stats.py
src/identity/application/handlers/get_profile_handler.py
src/identity/application/handlers/get_profile_activity_handler.py
alembic/versions/20260205_add_profile_fields.py
```

**Backend (Modified Files):**
```
src/identity/domain/entities/profile.py (add fields, update methods)
src/identity/domain/exceptions.py (add new exceptions)
src/identity/infrastructure/persistence/models.py (add columns)
src/identity/infrastructure/persistence/profile_repository.py (extend mapping)
src/identity/interface/api/user_controller.py (add endpoints)
src/identity/interface/api/schemas.py (add request/response models)
```

**Frontend (New Files):**
```
frontend/src/pages/ProfileView.tsx
frontend/src/pages/ProfileEdit.tsx
frontend/src/features/identity/components/ProfileSidebar.tsx
frontend/src/features/identity/components/ProfileStats.tsx
frontend/src/features/identity/components/ActivityChart.tsx
frontend/src/features/identity/components/ActivityFeed.tsx
frontend/src/features/identity/hooks/useProfile.ts
frontend/src/features/identity/api/profile.ts
```

**Frontend (Modified Files):**
```
frontend/src/features/identity/types/user.ts (extend Profile interface)
frontend/src/App.tsx (add routes)
```

**Tests (New Files):**
```
tests/features/identity/test_profile.py (42 BDD scenarios)
tests/unit/domain/value_objects/test_location.py
tests/unit/domain/value_objects/test_social_links.py
tests/unit/domain/value_objects/test_bio.py
tests/unit/application/handlers/test_update_profile_handler.py
tests/unit/application/handlers/test_get_profile_handler.py
```

### Appendix B: Dependencies

**Backend:**
```toml
[tool.poetry.dependencies]
bleach = "^6.1.0"  # HTML sanitization (NEW)
```

**Frontend:**
```json
No new dependencies required
```

### Appendix C: References

**Libraries:**
- bleach: https://bleach.readthedocs.io/
- Pydantic HttpUrl: https://docs.pydantic.dev/latest/api/networks/
- slowapi (rate limiting): https://github.com/laurentS/slowapi

**Patterns:**
- DDD Aggregates: Evans, "Domain-Driven Design" (2003), Chapter 6
- Event-Driven Architecture: Fowler, "Event-Driven Architecture" (2005)
- RESTful API Design: Fielding, "REST" (2000)

---

**Document Version:** 1.0
**Last Updated:** 2026-02-05
**Status:** Ready for Implementation
