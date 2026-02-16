# Points & Levels — Product Requirements Document

**Feature:** Points & Levels
**Module:** Leaderboards (Gamification)
**Status:** Complete
**Version:** 1.0
**Last Updated:** February 16, 2026
**Implementation Status:** Complete — All 3 Phases (Core Engine, Display & Admin Config, Course Gating & Security)
**Implementation Summary:**
  - Phase 1: `docs/summaries/gamification/points-phase-1-summary.md`
  - Phase 2: `docs/summaries/gamification/points-phase-2-summary.md`
  - Phase 3: `docs/summaries/gamification/points-phase-3-summary.md`
**Bounded Context:** Gamification
**PRD Type:** Feature Specification

---

## 1. Overview

### 1.1 What

A points and leveling system that rewards members for participating in the community. Members earn points through engagement activities — receiving likes on their posts and comments, creating posts, commenting on discussions, and completing course lessons. As points accumulate, members progress through 9 levels, each with a custom name and visual badge displayed on their avatar throughout the platform.

Admins can configure level names and the point thresholds required to reach each level. Levels can also gate access to specific courses, encouraging members to engage more to unlock premium content.

### 1.2 Why

Gamification is a proven driver of community engagement. Without incentive mechanics, communities tend toward passive consumption — a few active posters and many lurkers. The points and levels system gives every member a visible, progressive goal to work toward, transforming routine interactions (liking, commenting, posting) into meaningful progress. It also gives admins a tool to reward their most engaged members with exclusive content access.

### 1.3 Success Criteria

| Metric | Target |
|--------|--------|
| Daily likes per 100 members | > 20 (baseline to measure lift) |
| Posts per day per 100 members | > 8 (up from ~5 without gamification) |
| Comments per post | > 4 average (up from ~3) |
| Members reaching Level 2+ within 30 days | > 30% |
| Members checking their level/points weekly | > 50% of active members |

---

## 2. User Stories

### 2.1 Earning Points

| ID | Story | Priority |
|----|-------|----------|
| US-EP1 | As a member, I want to earn points when someone likes my post so that I'm rewarded for quality content | Must Have |
| US-EP2 | As a member, I want to earn points when someone likes my comment so that my contributions are valued | Must Have |
| US-EP3 | As a member, I want to earn points when I create a post so that I'm rewarded for starting discussions | Must Have |
| US-EP4 | As a member, I want to earn points when I comment on a post so that participation is encouraged | Must Have |
| US-EP5 | As a member, I want to earn points when I complete a lesson so that learning is rewarded | Must Have |

### 2.2 Levels

| ID | Story | Priority |
|----|-------|----------|
| US-L1 | As a member, I want to see my current level badge on my avatar so that others know my standing | Must Have |
| US-L2 | As a member, I want to see how many points I need to reach the next level so that I have a goal to work toward | Must Have |
| US-L3 | As a member, I want to level up automatically when I reach the point threshold so that progression feels seamless | Must Have |
| US-L4 | As a member, I want to see all 9 level definitions so that I understand the progression path | Must Have |

### 2.3 Points Display

| ID | Story | Priority |
|----|-------|----------|
| US-PD1 | As a member, I want to see my total points on my profile so that I can track my overall contribution | Must Have |
| US-PD2 | As a member, I want to see my level name and badge on my profile so that my rank is visible | Must Have |
| US-PD3 | As a member, I want to see "X points to level up" on my profile so that I know my progress | Must Have |
| US-PD4 | As a member, I want to see level badges on other members' avatars so that I can identify experienced members | Must Have |

### 2.4 Level-Based Unlocks

| ID | Story | Priority |
|----|-------|----------|
| US-LU1 | As an admin, I want to set a minimum level on a course so that it's only accessible to engaged members | Must Have |
| US-LU2 | As a member, I want to see which courses are locked by level so that I know what I'm working toward | Must Have |
| US-LU3 | As a member, I want to see "Unlock at Level X" on gated courses so that the requirement is clear | Must Have |

### 2.5 Admin Configuration

| ID | Story | Priority |
|----|-------|----------|
| US-AC1 | As an admin, I want to customize level names so that they match my community's brand | Must Have |
| US-AC2 | As an admin, I want to set point thresholds for each level so that I can control progression speed | Must Have |

---

## 3. Business Rules

### 3.1 Point Awarding Rules

| Action | Points Awarded | Recipient |
|--------|---------------|-----------|
| Like received on post | +1 | Post author |
| Like received on comment | +1 | Comment author |
| Post created | +2 | Post author |
| Comment created | +1 | Comment author |
| Lesson completed | +5 | Member who completed lesson |

**Key constraints:**
- Points are awarded at the time the action occurs
- Points from likes are awarded to the **content author**, not the person who liked
- Points from posting, commenting, and lesson completion are awarded to the **acting member**
- Members cannot earn points from liking their own content (self-likes are already prevented by the Community module)
- A member can only earn lesson completion points once per lesson (completing again does not re-award)

### 3.2 Point Accumulation

- Points are **cumulative and permanent** — they never decay or expire
- Total points determine the member's current level
- Points cannot go negative
- If a post or comment is deleted, points previously earned from likes on that content are **not** revoked (points represent historical engagement)
- If a like is removed (unliked), the point earned from that like **is** revoked (the point is deducted from the author's total)

### 3.3 Level Definitions

Members are assigned a level based on their total accumulated points. There are 9 levels:

| Level | Default Name | Point Threshold | Unlock Condition |
|-------|-------------|-----------------|------------------|
| 1 | Student | 0 | All new members start here |
| 2 | Practitioner | 10 | |
| 3 | Builder | 30 | |
| 4 | Leader | 60 | |
| 5 | Mentor | 100 | |
| 6 | Empire Builder | 150 | |
| 7 | Ruler | 210 | |
| 8 | Legend | 280 | |
| 9 | Icon | 360 | |

**Level rules:**
- All new members start at Level 1 with 0 points
- Level-ups happen automatically and immediately when the point threshold is crossed
- Levels never decrease — if a member loses points (e.g., from an unlike), their level stays the same even if their total drops below the threshold (ratchet behavior)
- A member's level is always determined by the **highest threshold they have ever reached**
- The 9-level structure is fixed (cannot add or remove levels)

### 3.4 Level Display

- Level is displayed as a **numbered badge** on the member's avatar (e.g., blue circle with "2")
- The badge appears everywhere the avatar is shown: feed posts, comments, member directory, profile, leaderboard
- Level name is shown on the member's profile (e.g., "Level 2 - Practitioner")
- "X points to level up" is shown on the member's own profile (not visible on other members' profiles)
- For Level 9 members, no "points to level up" message is shown (they've reached the top)

### 3.5 Level-Based Course Access

- Admins can set a **minimum level** (1-9) on any course
- Members below the minimum level see the course in the list but cannot access its content
- Locked courses display "Unlock at Level X" where X is the required level
- The lock indicator includes the level name (e.g., "Unlock at Level 2 - Practitioner")
- If an admin lowers the required level for a course, members who now qualify gain immediate access
- If an admin raises the required level, members currently below the new threshold lose access
- Default: courses have no level requirement (accessible to all members)

### 3.6 Admin Configuration

**Level Names:**
- Admins can customize the display name for each of the 9 levels
- Names must be 1-30 characters
- Names must be unique within the community
- Changing a level name takes effect immediately across the platform

**Point Thresholds:**
- Admins can set custom point thresholds for levels 2-9
- Level 1 always starts at 0 points (not configurable)
- Thresholds must be strictly increasing (Level 3 threshold > Level 2 threshold)
- Minimum threshold for Level 2 is 1 point
- Changing thresholds recalculates all member levels immediately (respecting the ratchet rule)

### 3.7 Anti-Gaming Protections

- Members cannot like their own posts or comments (enforced by Community module)
- Community rate limits apply: 200 likes per hour, 10 posts per hour, 50 comments per hour
- No additional point-specific rate limiting in MVP

---

## 4. UI Behavior

### 4.1 Level Badge on Avatar

**Location:** Everywhere the member avatar is displayed (feed, comments, member directory, profile sidebar, leaderboard)

**Display:**
- Small circular badge overlapping the bottom-right of the avatar
- Badge shows the level number (1-9)
- Badge uses the community's accent color (blue in Skool's design)
- Badge is always visible — no hover or interaction required

**States:**
- Level 1-9: Numbered badge displayed
- All members have a badge (Level 1 is the minimum)

### 4.2 Member Profile — Points & Level Section

**Location:** Right sidebar on the member's profile page

**Display (viewing own profile):**
- Avatar with level badge
- "Level X - [Level Name]" text below avatar (e.g., "Level 2 - Practitioner")
- "X points to level up" with a clock/progress icon
- For Level 9: Show "Level 9 - [Level Name]" with no "points to level up" message

**Display (viewing another member's profile):**
- Avatar with level badge
- "Level X - [Level Name]" text below avatar
- No "points to level up" message (that's private to the member)

**States:**
- Loading: Skeleton placeholder for level info
- Level 9 reached: No progress indicator shown

### 4.3 Level Definitions View

**Location:** Accessible from the Leaderboards page (top section in Skool's design)

**Display:**
- Grid of all 9 levels showing:
  - Level number and name
  - Lock icon for levels above the current member's level
  - "X% of members" showing the percentage of community members at each level
- Current member's level highlighted

**Interactions:**
- This section is informational only (no clickable actions)

### 4.4 Course Card — Level Lock Indicator

**Location:** Classroom course grid/list view

**Display (locked course):**
- Lock icon overlaying the course card
- Text: "Unlock at Level X" or "Unlock at Level X - [Level Name]"
- Course title and description still visible (but dimmed/muted)
- Clicking a locked course shows the requirement instead of navigating to course content

**Display (unlocked course):**
- No lock indicator
- Normal course card behavior

**States:**
- Unlocked: Standard course card
- Locked: Dimmed card with lock overlay and level requirement text
- Just unlocked (member just leveled up): No special animation in MVP

### 4.5 Points Feedback

**On point-earning actions:**
- No real-time point notification in MVP (member sees updated total when they visit their profile or leaderboard)
- Level-up is reflected immediately in the avatar badge across the platform

**Future (not in MVP):**
- Toast notification: "+1 point" when receiving a like
- Level-up celebration animation
- Level-up post in community feed

---

## 5. Edge Cases

### 5.1 Unlike After Points Awarded

**Scenario:** A member likes a post (awarding the author 1 point), then unlikes it.

**Behavior:**
- The point is deducted from the author's total
- If the author's total drops below their current level threshold, the **level does not decrease** (ratchet rule)
- Points cannot go below 0

### 5.2 Deleted Content and Points

**Scenario:** A post with 10 likes is deleted by the author.

**Behavior:**
- Points previously awarded from those 10 likes are **not revoked**
- Rationale: The engagement already happened; retroactive point removal creates confusion

**Scenario:** A post with 10 likes is deleted by an admin (moderation action).

**Behavior:**
- Same as author deletion — points are not revoked
- Admins who need to penalize a member can use future manual point adjustment tools (out of scope for MVP)

### 5.3 Lesson Completed Multiple Times

**Scenario:** A member marks a lesson as complete, then uncompletes and recompletes it.

**Behavior:**
- Points are awarded only on the **first** completion
- Subsequent completions of the same lesson do not award additional points

### 5.4 Threshold Changes by Admin

**Scenario:** Admin lowers Level 3 threshold from 30 to 20 points. Several members with 20-29 points are now eligible for Level 3.

**Behavior:**
- All member levels are recalculated immediately
- Members who now qualify for a higher level are promoted
- The ratchet rule still applies: members who were previously at a higher level stay there even if the new thresholds would place them lower

### 5.5 New Member Joins

**Scenario:** A new member joins the community.

**Behavior:**
- Starts at Level 1 with 0 points
- Level badge shows "1" on their avatar immediately
- Profile shows "Level 1 - [Level 1 Name]" and "X points to level up"

### 5.6 Maximum Level Reached

**Scenario:** A member reaches Level 9.

**Behavior:**
- Level badge shows "9"
- Profile shows "Level 9 - [Level Name]"
- No "points to level up" message
- Points continue to accumulate (still tracked for leaderboard purposes)
- No additional levels are unlocked

### 5.7 Concurrent Point Awards

**Scenario:** A member receives multiple likes simultaneously (e.g., a popular post gets 50 likes in a minute).

**Behavior:**
- Each like awards 1 point independently
- If the accumulated points cross one or more level thresholds, the member immediately reaches the appropriate level (could skip from Level 2 to Level 4 if enough points are awarded)
- No "one level at a time" restriction

### 5.8 Community with No Gamification Configuration

**Scenario:** A community is created and admin has not customized level names or thresholds.

**Behavior:**
- Default level names and thresholds apply (as defined in Section 3.3)
- Points system is active from the start — no opt-in required
- Admins can customize at any time

---

## 6. Security Requirements

### 6.1 Authentication

- All point-awarding events require the originating action to come from an authenticated user
- Point queries (viewing own or others' points/levels) require valid authentication
- Admin configuration endpoints require valid JWT with admin role

### 6.2 Authorization

| Action | Member | Moderator | Admin |
|--------|--------|-----------|-------|
| View own points/level | ✓ | ✓ | ✓ |
| View other member's level | ✓ | ✓ | ✓ |
| View level definitions | ✓ | ✓ | ✓ |
| Customize level names | ✗ | ✗ | ✓ |
| Set level thresholds | ✗ | ✗ | ✓ |
| Set course level requirement | ✗ | ✗ | ✓ |

### 6.3 Input Validation

- Level names: 1-30 characters, no HTML tags
- Point thresholds: Positive integers, strictly increasing sequence
- Course level requirement: Integer 1-9
- All admin inputs sanitized against XSS

### 6.4 Data Protection

- Point totals and level are not sensitive data (visible to all community members)
- "Points to level up" is only visible to the member themselves
- Point transaction history is stored for audit purposes but not exposed in MVP UI
- Rate limiting on source actions (likes, posts, comments) prevents point manipulation

---

## 7. Out of Scope

### 7.1 Not in MVP

- Real-time point notifications ("+1 point" toast)
- Level-up celebration animation or confetti
- Level-up auto-post in community feed
- Manual point adjustment by admins
- Point decay or expiration
- Point multipliers (e.g., 2x points events)
- Achievement badges (separate from levels)
- Points for non-content actions (e.g., daily login, profile completion)
- Leaderboard views (separate PRD: `gamification/leaderboards`)
- Gamification on/off toggle for community

### 7.2 Phase 2 Features

- Leaderboard views (7-day, 30-day, all-time)
- Leaderboard sidebar widget on community feed
- Level-gating for chat/DM access
- Level-gating for posting privileges
- Custom point awards by admin
- Point history/activity log

### 7.3 Phase 3 Features

- Achievement badges system
- Point multiplier events (2x weekends, etc.)
- Custom rewards per level (badges, titles, flair)
- Analytics dashboard (points distribution, level-up rates)
- Gamification A/B testing tools

---

## 8. Success Metrics

### 8.1 Engagement Metrics

| Metric | Measurement | Target |
|--------|-------------|--------|
| Like rate increase | % change in likes/day after launch | > 25% increase |
| Post creation increase | % change in posts/day | > 30% increase |
| Comment increase | % change in comments/day | > 20% increase |
| Course completion increase | % change in lessons completed/day | > 15% increase |

### 8.2 Quality Metrics

| Metric | Measurement | Target |
|--------|-------------|--------|
| Level 2+ rate (30-day) | % of members reaching Level 2 within 30 days | > 30% |
| Level 5+ rate (90-day) | % of members reaching Level 5 within 90 days | > 10% |
| Active member retention | % of members with >0 points who return weekly | > 60% |

### 8.3 Technical Metrics

| Metric | Measurement | Target |
|--------|-------------|--------|
| Point award latency | Time from triggering action to point recorded | < 500ms (p95) |
| Level calculation time | Time to recalculate member level | < 100ms (p95) |
| Profile load time with level data | API response for profile with level info | < 200ms (p95) |

---

## 9. Dependencies

### 9.1 Upstream Dependencies

**Community Context:**
- PostLiked / PostUnliked events — triggers point award/deduction for post author
- CommentLiked / CommentUnliked events — triggers point award/deduction for comment author
- PostCreated event — triggers point award for post author
- CommentAdded event — triggers point award for comment author

**Classroom Context:**
- LessonCompleted event — triggers point award for the member

**Identity Context:**
- UserId value object
- User authentication (JWT tokens)
- Member profile information (for displaying level badge)

### 9.2 Downstream Consumers

**Leaderboards (Gamification Phase 2):**
- Queries member points for ranking and display
- Uses level data for leaderboard badges

**Classroom Context:**
- Checks member level to enforce course access restrictions

**Community Context (display only):**
- Reads member level for avatar badge display in feed, comments, member directory

**Notification Context (Future):**
- Consumes level-up events for notifications

---

## 10. Open Questions

None — all questions resolved during discovery.

---

## 11. Appendix

### 11.1 Related Documents

- `docs/prd_summary/PRD/OVERVIEW_PRD.md` — Master PRD (Section 3.7: Leaderboards Module)
- `docs/domain/GLOSSARY.md` — Ubiquitous language (Gamification Context)
- `docs/architecture/CONTEXT_MAP.md` — Bounded context relationships
- `tests/features/gamification/points.feature` — BDD specifications for this feature
- `docs/features/community/feed-prd.md` — Community Feed PRD (upstream dependency)

### 11.2 Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-15 | Product Team | Initial draft |

---

## 12. Approval

**Product Owner:** _________________
**Engineering Lead:** _________________
**Design Lead:** _________________

**Status:** Draft — Pending Review
