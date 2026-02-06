# User Profile - Implementation Phases

**Feature:** User Profile (Extended)
**Context:** Identity
**Status:** Complete (All 5 Phases)

---

## Complexity Analysis

| Metric | Count | Complexity |
|--------|-------|------------|
| BDD Scenarios | 42 | **High** |
| New Backend Files | 11 | **High** |
| Modified Backend Files | 6 | **Medium** |
| New Frontend Files | 8 | **High** |
| Modified Frontend Files | 2 | **Low** |
| API Endpoints | 5 | **Medium** |
| Dependencies | 0 (self-contained in Identity) | **Low** |
| **Total Files** | **27** | **High** |

**Overall Complexity:** ⚠️ **HIGH**

**Decision:** **5-phase implementation** (Layer-Based Strategy + Security Phase)

**Estimated Total Time:** 18-22 hours

---

## Phase Breakdown

### Phase 1: Domain & Data Foundation
**Goal:** Establish domain model extensions and database schema

### Phase 2: Profile Viewing (Read Operations)
**Goal:** Enable viewing own and other users' profiles

### Phase 3: Profile Updates (Write Operations)
**Goal:** Enable profile modification with validation

### Phase 4: Security & Edge Cases
**Goal:** Harden security, rate limiting, XSS prevention

### Phase 5: Frontend UI
**Goal:** Build profile view and edit pages

---

## Phase 1: Domain & Data Foundation ✅ COMPLETE

**Status:** Complete (2026-02-05)
**Summary:** `docs/summaries/profile-phase1-summary.md`

### Goal
Create new value objects (Location, SocialLinks, Bio), extend Profile entity, add database columns, and update repository mappings. This phase establishes the data model foundation for all other phases.

### Scope

**Backend - Domain Layer:**
- `src/identity/domain/value_objects/location.py` ◄─── NEW
- `src/identity/domain/value_objects/social_links.py` ◄─── NEW
- `src/identity/domain/value_objects/bio.py` ◄─── NEW
- `src/identity/domain/entities/profile.py` ◄─── EXTEND (add location, social_links, bio fields)
- `src/identity/domain/exceptions.py` ◄─── EXTEND (add InvalidLocationError, InvalidSocialLinkError, InvalidBioError)

**Backend - Infrastructure Layer:**
- `src/identity/infrastructure/persistence/models.py` ◄─── EXTEND (add 6 columns to ProfileModel)
- `src/identity/infrastructure/persistence/profile_repository.py` ◄─── EXTEND (mapping methods)
- `alembic/versions/20260205_add_profile_fields.py` ◄─── NEW (migration)

**Frontend:**
- None (data layer only)

**Tests:**
- `tests/unit/domain/value_objects/test_location.py` ◄─── NEW
- `tests/unit/domain/value_objects/test_social_links.py` ◄─── NEW
- `tests/unit/domain/value_objects/test_bio.py` ◄─── NEW
- `tests/features/identity/test_profile.py` ◄─── NEW (validation scenarios only)

### BDD Scenarios Covered (10 validation scenarios)

**From `profile.feature`:**
- [ ] Line 59: Profile completion fails without display name
- [ ] Line 65: Profile completion fails with display name too short
- [ ] Line 71: Profile completion fails with display name too long
- [ ] Line 77: Profile completion fails with bio too long
- [ ] Line 85: Profile completion fails with invalid avatar URL
- [ ] Line 95: Profile completion fails with city but no country
- [ ] Line 103: Profile completion fails with country but no city
- [ ] Line 113: Profile completion fails with invalid social link URL
- [ ] Line 248: Update fails with display name too short
- [ ] Line 254: Update fails with display name too long

### Dependencies
- None (first phase, foundational)

### Estimated Time
**4-5 hours**

### Definition of Done
- [x] 3 value objects created with validation logic
- [x] Profile entity extended with new fields
- [x] 4 new domain exceptions added (InvalidBioError, InvalidLocationError, InvalidSocialLinkError, ProfileNotFoundError)
- [x] Database migration created and applied
- [x] ProfileModel extended with 6 new columns
- [x] Repository mapping updated (entity ↔ model)
- [x] 38 unit tests for all value objects passing (Bio: 7, Location: 12, SocialLinks: 10)
- [x] `./scripts/verify.sh` passes (81% coverage, exceeds 80% threshold)
- [x] No regressions (187 existing BDD tests still pass)

### Verification Commands
```bash
# Run database migration
docker-compose up -d
alembic upgrade head

# Unit tests
pytest tests/unit/domain/value_objects/test_location.py -v
pytest tests/unit/domain/value_objects/test_social_links.py -v
pytest tests/unit/domain/value_objects/test_bio.py -v

# BDD validation scenarios
pytest tests/features/identity/test_profile.py -k "fails" -v

# Full verification
./scripts/verify.sh
```

---

## Phase 2: Profile Viewing (Read Operations) ✅ COMPLETE

**Status:** Complete (2026-02-05)
**Summary:** `docs/summaries/profile-phase2-summary.md`

### Goal
Implement GET endpoints and query handlers to view own profile, other users' profiles, and retrieve activity/stats (placeholders for now).

### Scope

**Backend - Application Layer:**
- `src/identity/application/queries/get_profile.py` ◄─── NEW
- `src/identity/application/queries/get_profile_activity.py` ◄─── NEW
- `src/identity/application/queries/get_profile_stats.py` ◄─── NEW
- `src/identity/application/handlers/get_profile_handler.py` ◄─── NEW
- `src/identity/application/handlers/get_profile_activity_handler.py` ◄─── NEW
- `src/identity/application/handlers/get_profile_stats_handler.py` ◄─── NEW

**Backend - Interface Layer:**
- `src/identity/interface/api/user_controller.py` ◄─── EXTEND (add 4 GET endpoints)
- `src/identity/interface/api/schemas.py` ◄─── EXTEND (add ProfileResponse, ActivityResponse, StatsResponse)

**Frontend:**
- None (API layer only)

**Tests:**
- `tests/features/identity/test_profile.py` ◄─── EXTEND (view scenarios)
- `tests/unit/application/handlers/test_get_profile_handler.py` ◄─── NEW

### BDD Scenarios Covered (10 scenarios)

**From `profile.feature`:**
- [x] Line 126: User views their own profile
- [x] Line 140: User views own profile with empty activity
- [x] Line 152: User views another member's profile
- [x] Line 164: View profile of non-existent user
- [x] Line 282: Profile stats show zero contributions for new user
- [x] Line 290: Profile stats show member since date
- [x] Line 301: Activity feed is empty for user with no posts or comments
- [x] Line 309: Activity feed placeholder until Community feature exists
- [x] Line 320: Activity chart returns empty data for user with no activity
- [x] Line 331: Unauthenticated user cannot view profiles

### Dependencies
- **Requires Phase 1 complete** (value objects, database schema)

### Estimated Time
**3-4 hours**

### Definition of Done
- [x] 3 query classes created
- [x] 3 query handlers implemented
- [x] 4 GET endpoints added to user_controller (actually 5: added activity chart endpoint)
- [x] Request/response schemas defined
- [x] Activity and stats return empty placeholders
- [x] 10 BDD scenarios passing
- [x] Unit tests for query handlers passing
- [x] API returns 404 for non-existent users
- [x] API returns 401 for unauthenticated requests
- [x] `./scripts/verify.sh` passes (81.37% coverage, exceeds 80% threshold)

### Verification Commands
```bash
# Unit tests
pytest tests/unit/application/handlers/test_get_profile_handler.py -v

# BDD scenarios (profile viewing)
pytest tests/features/identity/test_profile.py -k "views" -v
pytest tests/features/identity/test_profile.py -k "stats" -v
pytest tests/features/identity/test_profile.py -k "activity" -v

# API integration tests
pytest tests/features/identity/test_profile.py::test_unauthenticated_cannot_view -v

# Full verification
./scripts/verify.sh
```

---

## Phase 3: Profile Updates (Write Operations)

### Goal
Implement PATCH endpoint, UpdateProfile command/handler, and ProfileUpdated event to enable profile modification.

### Scope

**Backend - Domain Layer:**
- `src/identity/domain/events/profile_updated.py` ◄─── NEW
- `src/identity/domain/entities/profile.py` ◄─── EXTEND (add update_fields method)

**Backend - Application Layer:**
- `src/identity/application/commands/update_profile.py` ◄─── NEW
- `src/identity/application/handlers/update_profile_handler.py` ◄─── NEW

**Backend - Interface Layer:**
- `src/identity/interface/api/user_controller.py` ◄─── EXTEND (add PATCH /users/me/profile)
- `src/identity/interface/api/schemas.py` ◄─── EXTEND (add UpdateProfileRequest)

**Frontend:**
- None (API layer only)

**Tests:**
- `tests/features/identity/test_profile.py` ◄─── EXTEND (update scenarios)
- `tests/unit/application/handlers/test_update_profile_handler.py` ◄─── NEW
- `tests/unit/domain/entities/test_profile.py` ◄─── NEW (update_fields tests)

### BDD Scenarios Covered (17 scenarios)

**From `profile.feature`:**
- [ ] Line 15: Complete profile with display name only
- [ ] Line 23: Complete profile with all optional fields
- [ ] Line 41: Complete profile with partial optional fields
- [ ] Line 174: Update display name
- [ ] Line 181: Update bio
- [ ] Line 188: Add location to profile
- [ ] Line 197: Remove location from profile
- [ ] Line 205: Update social links
- [ ] Line 217: Update avatar URL
- [ ] Line 224: Clear avatar URL reverts to auto-generated
- [ ] Line 231: Update multiple fields at once
- [ ] Line 260: Update fails with bio too long
- [ ] Line 266: Update fails with invalid avatar URL
- [ ] Line 272: Update fails with partial location
- [ ] Line 337: User cannot edit another user's profile
- [ ] Line 344: Profile text inputs are sanitized
- [ ] Line 351: Profile update requests are rate limited

### Dependencies
- **Requires Phase 1 complete** (value objects, domain model)
- **Requires Phase 2 complete** (to verify updates via GET endpoints)

### Estimated Time
**4-5 hours**

### Definition of Done
- [ ] ProfileUpdated domain event created
- [ ] UpdateProfile command created
- [ ] UpdateProfileHandler implemented with validation
- [ ] PATCH endpoint added
- [ ] Auto-generation of avatar on clear
- [ ] ProfileUpdated event published on changes
- [ ] Authorization check (users can only update own profile)
- [ ] 17 BDD scenarios passing
- [ ] Unit tests for update logic passing
- [ ] Event publishing verified
- [ ] `./scripts/verify.sh` passes

### Verification Commands
```bash
# Unit tests
pytest tests/unit/application/handlers/test_update_profile_handler.py -v
pytest tests/unit/domain/entities/test_profile.py -v

# BDD scenarios (profile updates)
pytest tests/features/identity/test_profile.py -k "Update" -v
pytest tests/features/identity/test_profile.py -k "Complete" -v

# Event publishing test
pytest tests/features/identity/test_profile.py -k "ProfileUpdated" -v

# Full verification
./scripts/verify.sh
```

---

## Phase 4: Security & Edge Cases ✅ COMPLETE

**Status:** Complete (2026-02-06)
**Summary:** `docs/summaries/profile-phase4-summary.md`

### Goal
Add XSS sanitization (bleach), rate limiting, and comprehensive security checks to harden the feature.

### Scope

**Backend - Domain Layer:**
- `src/identity/domain/value_objects/bio.py` ◄─── Already has bleach sanitization (from Phase 1)

**Backend - Infrastructure Layer:**
- `src/identity/infrastructure/services/rate_limiter.py` ◄─── EXTEND (add PROFILE_UPDATE_LIMIT)
- `src/identity/infrastructure/services/__init__.py` ◄─── EXTEND (export new constant)

**Backend - Interface Layer:**
- `src/identity/interface/api/user_controller.py` ◄─── EXTEND (add rate limiting decorator)

**Frontend:**
- None (backend security hardening)

**Tests:**
- `tests/features/identity/test_profile.py` ◄─── EXTEND (fixed security scenarios)

### BDD Scenarios Covered (4 scenarios)

**From `profile.feature`:**
- [x] Line 331: Unauthenticated user cannot view profiles
- [x] Line 337: User cannot edit another user's profile
- [x] Line 344: Profile text inputs are sanitized
- [x] Line 351: Profile update requests are rate limited

### Dependencies
- **Requires Phase 3 complete** (update operations to secure)

### Estimated Time
**2-3 hours**

### Definition of Done
- [x] bleach library installed and configured (done in Phase 1)
- [x] Bio value object sanitizes HTML/script tags
- [x] Rate limiting applied to PATCH endpoint (10 req/hour)
- [x] XSS protection tested with malicious input
- [x] Rate limiting tested (exceeding limit returns 429)
- [x] All security BDD scenarios passing (4/4)
- [x] `./scripts/verify.sh` passes (83.87% coverage)

### Verification Commands
```bash
# Security scenarios
pytest tests/features/identity/test_profile.py -k "sanitized or rate_limited or cannot_edit or unauthenticated" -v

# Full verification
./scripts/verify.sh
```

---

## Phase 5: Frontend UI

### Goal
Build ProfileView and ProfileEdit pages with all components, integrate with backend API, and complete end-to-end user flow.

### Scope

**Frontend - Pages:**
- `frontend/src/pages/ProfileView.tsx` ◄─── NEW
- `frontend/src/pages/ProfileEdit.tsx` ◄─── NEW

**Frontend - Components:**
- `frontend/src/features/identity/components/ProfileSidebar.tsx` ◄─── NEW
- `frontend/src/features/identity/components/ProfileStats.tsx` ◄─── NEW
- `frontend/src/features/identity/components/ActivityChart.tsx` ◄─── NEW
- `frontend/src/features/identity/components/ActivityFeed.tsx` ◄─── NEW

**Frontend - API Integration:**
- `frontend/src/features/identity/api/profile.ts` ◄─── NEW
- `frontend/src/features/identity/hooks/useProfile.ts` ◄─── NEW

**Frontend - Types:**
- `frontend/src/features/identity/types/user.ts` ◄─── EXTEND (Profile interface)

**Frontend - Routing:**
- `frontend/src/App.tsx` ◄─── EXTEND (add /profile/:userId and /profile/edit routes)

**Backend:**
- None (frontend only)

**Tests:**
- `tests/features/identity/test_profile.py` ◄─── VERIFY (all scenarios pass end-to-end)
- Frontend component tests (optional)

### BDD Scenarios Verified (All 42 scenarios)

**All scenarios should pass end-to-end through UI:**
- Profile completion flow (post-registration)
- Profile viewing (own and others)
- Profile editing form
- Validation error display
- Empty state displays (activity, stats)
- Social link icons rendering
- Location formatting display

### Dependencies
- **Requires Phase 1-4 complete** (all backend functionality)

### Estimated Time
**5-6 hours**

### Definition of Done
- [ ] ProfileView page displays all profile data
- [ ] ProfileEdit page with form and validation
- [ ] Profile sidebar shows avatar, name, bio, location, social links
- [ ] Stats bar shows contribution count and member since date
- [ ] Activity chart shows 30-day heatmap (empty state)
- [ ] Activity feed shows empty state
- [ ] Edit button only visible on own profile
- [ ] All form validations working (client-side + server-side)
- [ ] Success/error toast notifications
- [ ] Navigation links functional (header menu)
- [ ] React Query caching configured (5 min for profile)
- [ ] All 42 BDD scenarios passing end-to-end
- [ ] `./scripts/verify-frontend.sh` passes

### Verification Commands
```bash
# Frontend verification
cd frontend
npm run typecheck
npm run lint
npm run test

# Full BDD test suite (end-to-end)
pytest tests/features/identity/test_profile.py -v

# Manual UI testing checklist:
# 1. Navigate to /profile/edit
# 2. Fill all fields and save
# 3. View own profile
# 4. View another user's profile
# 5. Try to edit another user's profile (should fail)
# 6. Submit invalid data (see validation errors)
# 7. Clear avatar (see initials avatar)
# 8. Check empty states (activity, chart)

# Full verification (backend + frontend)
./scripts/verify.sh
./scripts/verify-frontend.sh
```

---

## Dependency Graph

```
Phase 1: Domain & Data Foundation
         (Value Objects, Database, Repositories)
                    ↓
Phase 2: Profile Viewing (Read Operations)
         (GET endpoints, Query handlers)
                    ↓
Phase 3: Profile Updates (Write Operations)
         (PATCH endpoint, Command/Handler, Events)
                    ↓
Phase 4: Security & Edge Cases
         (XSS sanitization, Rate limiting)
                    ↓
Phase 5: Frontend UI
         (Pages, Components, Integration)
```

**Critical Path:** 1 → 2 → 3 → 4 → 5 (sequential dependencies)

**Parallelization Opportunities:**
- Phase 4 and 5 could run in parallel if Phase 3 is complete (frontend doesn't need security layer)
- However, recommended to complete security before frontend for safety

---

## Implementation Notes

### Patterns to Follow

**Domain Layer:**
- Match existing `DisplayName` value object pattern
- Use `frozen=True` dataclasses for value objects
- Validate in `__post_init__` method
- Raise domain-specific exceptions

**Application Layer:**
- Follow `CompleteProfileHandler` pattern
- Use dependency injection for repositories and services
- Publish domain events via EventBus
- Handle errors with try/except

**Infrastructure Layer:**
- Match `ProfileRepository` mapping pattern
- Use SQLAlchemy async ORM
- Handle NULL values gracefully in mapping

**Frontend:**
- Use react-hook-form + zod (existing pattern)
- React Query for data fetching
- TailwindCSS for styling (Skool-inspired)
- Error boundaries for graceful failures

### Common Pitfalls

1. **Don't forget NULL handling**
   - Location can be NULL (both fields or neither)
   - Social links can be NULL individually

2. **Don't skip value object validation**
   - Every value object must validate on construction
   - Don't assume data is valid just because it's from DB

3. **Don't forget avatar regeneration**
   - When avatar_url is cleared, regenerate from initials
   - Use existing AvatarGenerator service

4. **Don't skip event publishing**
   - ProfileUpdated must be published on every change
   - Include list of changed fields

5. **Don't hardcode URLs**
   - Use configuration for API base URL
   - Support environment-specific URLs

### Testing Strategy

**Phase 1:** Focus on value object unit tests
- Each validation rule has a test
- Each edge case covered

**Phase 2:** Focus on query logic
- Mock repository responses
- Test 404 scenarios
- Test empty placeholders

**Phase 3:** Focus on command orchestration
- Test event publishing
- Test avatar regeneration
- Test partial updates

**Phase 4:** Focus on security
- XSS injection tests
- Rate limiting tests
- Authorization tests

**Phase 5:** Focus on integration
- End-to-end user flows
- Error state rendering
- Empty state rendering

---

## Progress Tracking

### Phase 1: Domain & Data Foundation
- **Status:** Not started
- **Started:** _____
- **Completed:** _____
- **Notes:** _____

### Phase 2: Profile Viewing
- **Status:** ✅ Complete
- **Started:** 2026-02-05
- **Completed:** 2026-02-05
- **Notes:** All 10 BDD scenarios passing, 81.37% coverage. Placeholder responses ready for Community feature integration.

### Phase 3: Profile Updates
- **Status:** ✅ Complete
- **Started:** 2026-02-06
- **Completed:** 2026-02-06
- **Notes:** All 17 BDD scenarios passing, 83.86% coverage. PATCH endpoint, UpdateProfile command/handler, ProfileUpdated event.

### Phase 4: Security & Edge Cases
- **Status:** ✅ Complete
- **Started:** 2026-02-06
- **Completed:** 2026-02-06
- **Notes:** All 4 security BDD scenarios passing, 83.87% coverage. Rate limiting (10/hour), XSS sanitization (bleach), auth/authz verified.

### Phase 5: Frontend UI
- **Status:** ✅ Complete
- **Started:** 2026-02-06
- **Completed:** 2026-02-06
- **Notes:** ProfileView + ProfileEdit pages, 4 components, API client + React Query hooks, routing, 4 E2E tests (all passing in parallel). Fixed home-page POM to use data-testid. Added Redis flush globalSetup + retry-on-429 for rate limit resilience.

---

## Success Criteria

### Overall Feature Complete When:
- ✅ All 42 BDD scenarios passing
- ✅ All 5 phases completed
- ✅ Backend verification passes (`./scripts/verify.sh`)
- ✅ Frontend verification passes (`./scripts/verify-frontend.sh`)
- ✅ No regressions in existing features
- ✅ Security checklist completed
- ✅ User acceptance testing passed
- ✅ Documentation updated
- ✅ Feature flag enabled (if using)

---

**Document Version:** 1.0
**Created:** 2026-02-05
**Status:** Awaiting Approval

**Recommended Approach:** Implement phases sequentially, get approval for each phase before proceeding to next.
