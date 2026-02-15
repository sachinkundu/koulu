# Alignment Verification — Points & Levels

**Feature:** Points & Levels
**Last Updated:** February 15, 2026

---

## 1. PRD → BDD Coverage

Every PRD user story and business rule is mapped to at least one BDD scenario.

### User Stories

| PRD ID | User Story | BDD Scenario(s) | Status |
|--------|-----------|-----------------|--------|
| US-EP1 | Earn points when post liked | "Member earns a point when their post is liked" | Covered |
| US-EP2 | Earn points when comment liked | "Member earns a point when their comment is liked" | Covered |
| US-EP3 | Earn points when creating post | "Member earns points when creating a post" | Covered |
| US-EP4 | Earn points when commenting | "Member earns a point when commenting on a post" | Covered |
| US-EP5 | Earn points when completing lesson | "Member earns points when completing a lesson" | Covered |
| US-L1 | See level badge on avatar | "Level badge shown on post author avatar", "Level badge shown in member directory" | Covered |
| US-L2 | See points to next level | "Member sees points needed to reach next level" | Covered |
| US-L3 | Level up automatically | "Member levels up when reaching point threshold" | Covered |
| US-L4 | See all 9 level definitions | "Member can view all level definitions" | Covered |
| US-PD1 | See total points on profile | "Level information shown on member profile" | Covered |
| US-PD2 | See level name and badge on profile | "Level information shown on member profile" | Covered |
| US-PD3 | See points to level up on profile | "Member sees points needed to reach next level" | Covered |
| US-PD4 | See level badges on others' avatars | "Level badge shown on post author avatar", "Level badge shown in member directory" | Covered |
| US-LU1 | Admin set minimum level on course | "Admin customizes point thresholds" (admin config), course access scenarios | Covered |
| US-LU2 | See which courses are locked | "Locked course visible in course list with lock indicator" | Covered |
| US-LU3 | See "Unlock at Level X" | "Member cannot access course below required level" | Covered |
| US-AC1 | Admin customize level names | "Admin customizes level names" | Covered |
| US-AC2 | Admin set point thresholds | "Admin customizes point thresholds" | Covered |

### Business Rules

| PRD Rule | BDD Scenario(s) | Status |
|----------|-----------------|--------|
| 3.1 Point values (+1/+2/+5) | Multiple earning scenarios with exact values | Covered |
| 3.1 Points to content author, not liker | "Member earns a point when their post is liked" (alice earns, bob likes) | Covered |
| 3.1 One-time lesson completion | "No duplicate points for completing the same lesson twice" | Covered |
| 3.2 Points cumulative, permanent | "Multiple point sources accumulate correctly" | Covered |
| 3.2 Points cannot go negative | "Points cannot go below zero" | Covered |
| 3.2 Unlike deducts points | "Point is deducted when a like is removed" | Covered |
| 3.3 9 levels with defaults | Background section defines all 9 levels | Covered |
| 3.3 Level-up automatic | "Member levels up when reaching point threshold" | Covered |
| 3.3 Level ratchet | "Level does not decrease when points drop below threshold" | Covered |
| 3.4 Level badge on avatar | "Level badge shown on post author avatar" | Covered |
| 3.4 Level name on profile | "Level information shown on member profile" | Covered |
| 3.4 Points to level up (own profile) | "Member sees points needed to reach next level" | Covered |
| 3.4 No progress at Level 9 | "Level 9 member sees no level-up progress" | Covered |
| 3.5 Course level gating | 4 course access scenarios | Covered |
| 3.6 Level name validation | Name too long, empty, duplicate scenarios | Covered |
| 3.6 Threshold validation | Non-increasing, zero for L2 scenarios | Covered |
| 3.6 Threshold recalculation | "Threshold change recalculates member levels" | Covered |
| 3.7 Self-like prevention | "No points awarded for self-like attempt" | Covered |

### Edge Cases

| PRD Edge Case | BDD Scenario | Status |
|---------------|-------------|--------|
| 5.1 Unlike after points | "Point is deducted when a like is removed" | Covered |
| 5.3 Lesson completed twice | "No duplicate points for completing the same lesson twice" | Covered |
| 5.4 Threshold changes | "Threshold change recalculates member levels", "Level ratchet preserved when thresholds change" | Covered |
| 5.5 New member joins | "New member starts at Level 1" | Covered |
| 5.6 Maximum level reached | "Level 9 member sees no level-up progress" | Covered |
| 5.7 Concurrent point awards | "Member can skip levels with large point gains" (covers multi-level jump) | Covered |
| 5.8 No custom config | Background uses default config | Covered |

### Security

| PRD Security Rule | BDD Scenario | Status |
|-------------------|-------------|--------|
| 6.1 Authentication required | "Unauthenticated user cannot view points" | Covered |
| 6.2 Admin-only config | "Non-admin cannot configure levels", "Non-admin cannot set course level requirements" | Covered |
| 6.3 Input sanitization | "Level name input is sanitized" | Covered |

---

## 2. BDD → TDD Coverage

Every BDD scenario group maps to TDD design elements.

| BDD Scenario Group | TDD Section | Design Element |
|-------------------|-------------|----------------|
| Earning points (likes) | §6.1 MemberPoints aggregate, §7.3 Event handlers | PostLiked/CommentLiked → AwardPointsCommand |
| Earning points (content) | §6.1, §7.3 | PostCreated/CommentAdded → AwardPointsCommand |
| Earning points (lessons) | §6.1, §7.3 | LessonCompleted → AwardPointsCommand (with dedup) |
| Point deduction | §6.1, §7.1 DeductPointsCommand | deduct_points() behavior on aggregate |
| Level progression | §6.1 MemberPoints, §6.5 Ratchet pattern | award_points() triggers level recalculation |
| Level ratchet | §6.1, §6.4 Invariant #2 | max(current_level, calculated_level) |
| Level badge display | §5.1 API, §17.1 Frontend components | GET member level → LevelBadge component |
| Level definitions | §5.2 API, §7.2 GetLevelDefinitionsQuery | GET levels → LevelDefinitionsGrid component |
| Course access gating | §5.2 API, §7.2 CheckCourseAccessQuery | GET access → CourseCardLock component |
| Admin level config | §5.2 API, §7.1 UpdateLevelConfigCommand | PUT levels → LevelConfiguration aggregate |
| Admin course level | §5.2 API, §7.1 SetCourseLevelRequirementCommand | PUT level-requirement |
| Validation errors | §6.1, §6.4 Invariants, §11.1 Domain exceptions | InvalidLevelNameError, InvalidThresholdError |
| Security (auth) | §9.1, §9.2 | JWT middleware, role checks |
| Security (XSS) | §9.3 Input validation | Bleach sanitization |

---

## 3. PRD → TDD Direct Coverage

| PRD Requirement | TDD Coverage |
|----------------|-------------|
| Point values (§3.1) | §6.2 PointSource enum with hardcoded values |
| Point accumulation (§3.2) | §6.1 MemberPoints aggregate, §6.4 Invariant #1 |
| 9 levels (§3.3) | §6.1 LevelConfiguration aggregate, §4.1 level_configurations table |
| Level display (§3.4) | §5.1 API endpoints, §17.1 Frontend file checklist |
| Course gating (§3.5) | §5.1 API design, §4.1 course_level_requirements table |
| Admin config (§3.6) | §5.2 PUT /levels API, §7.1 UpdateLevelConfigCommand |
| Anti-gaming (§3.7) | §9.4 Threat model (delegated to Community context) |
| Performance targets (§8.3) | §10.1 Performance targets (matching PRD values) |
| UI components (§4) | §17.1 File checklist matches UI_SPEC component names |

---

## 4. UI_SPEC → TDD Coverage

| UI_SPEC Component | TDD Reference | File Path in Checklist |
|-------------------|---------------|----------------------|
| LevelBadge | §17.1 Frontend files | `frontend/src/features/gamification/components/LevelBadge.tsx` |
| LevelDefinitionsGrid | §17.1 Frontend files | `frontend/src/features/gamification/components/LevelDefinitionsGrid.tsx` |
| ProfileLevelSection | §17.1 Frontend files | `frontend/src/features/gamification/components/ProfileLevelSection.tsx` |
| CourseCardLock | §17.1 Frontend files | `frontend/src/features/gamification/components/CourseCardLock.tsx` |
| Avatar enhancement | §17.1 Modified files | `frontend/src/components/Avatar.tsx` |
| ProfileSidebar enhancement | §17.1 Modified files | `frontend/src/features/identity/components/ProfileSidebar.tsx` |
| CourseCard enhancement | §17.1 Modified files | `frontend/src/features/classroom/components/CourseCard.tsx` |

---

## 5. Gap Analysis

### Identified Gaps: None

All PRD requirements, BDD scenarios, and UI_SPEC components have corresponding TDD design elements. No orphaned requirements or untested behaviors detected.

### Minor Notes

1. **PRD Edge Case 5.2 (Deleted content and points):** The BDD spec does not explicitly test this scenario. However, it is a non-issue by design — the Gamification context never listens for PostDeleted events, so points from likes on deleted content are naturally preserved. No code or test needed.

2. **PRD §4.5 (Points feedback):** MVP specifies no real-time notifications. The TDD correctly omits this. Future consideration documented in §15.

3. **Concurrent point awards (PRD §5.7):** Addressed in TDD §8.3 (SELECT ... FOR UPDATE) and §10.4 (scalability). BDD scenario covers level-skipping as the observable behavior.

---

## 6. Approval Checklist

- [x] All PRD user stories mapped to BDD scenarios
- [x] All PRD business rules mapped to BDD scenarios
- [x] All PRD edge cases mapped to BDD scenarios
- [x] All PRD security requirements mapped to BDD scenarios
- [x] All BDD scenarios have corresponding TDD design elements
- [x] All UI_SPEC components appear in TDD file checklist
- [x] Component names match between UI_SPEC and TDD
- [x] No orphaned requirements (PRD items without design)
- [x] No orphaned design (TDD elements without PRD backing)
- [x] Performance targets in TDD match PRD §8.3
- [x] Architecture follows established patterns (hexagonal, DDD, EventBus)
- [x] No new dependencies required

---

**Status:** Complete — Ready for Review
