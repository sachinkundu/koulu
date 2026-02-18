# Leaderboards — Product Requirements Document

**Feature:** Leaderboards
**Module:** Leaderboards (Gamification)
**Status:** Draft
**Version:** 1.0
**Last Updated:** February 18, 2026
**Implementation Status:** Phase 1 Complete (13/17 BDD scenarios — Phase 2 pending)
**Bounded Context:** Gamification
**PRD Type:** Feature Specification

---

## 1. Overview

### 1.1 What

Ranked member views that surface the most active contributors in a community over three time horizons: the last 7 days, the last 30 days, and all-time. Each leaderboard ranks members by points earned in the period, displays the top 10 members with medals for the top 3, and shows the current member's own rank if they fall outside the top 10.

A compact leaderboard widget on the Community feed sidebar gives members a quick preview of the 30-day standings without leaving the feed.

### 1.2 Why

Points and levels (already implemented) create a personal progression loop. Leaderboards add a social dimension — members can see how they stack up against each other, which drives competitive engagement and gives top contributors visibility. The sidebar widget puts leaderboard awareness directly in the feed, the most-visited page, so members encounter the rankings in every session without navigating away.

### 1.3 Success Criteria

| Metric | Target |
|--------|--------|
| Members who view leaderboards at least once per week | > 40% of active members |
| Click-through from sidebar widget to full leaderboard page | > 15% of community feed page views |
| Engagement lift (likes + posts + comments per day) after launch | > 10% increase vs. pre-launch baseline |
| Members checking their own rank weekly | > 25% of active members |

---

## 2. User Stories

### 2.1 Leaderboard Rankings

| ID | Story | Priority |
|----|-------|----------|
| US-LB1 | As a member, I want to see who earned the most points in the last 7 days so that I can follow the most active recent contributors | Must Have |
| US-LB2 | As a member, I want to see who earned the most points in the last 30 days so that I can track monthly momentum | Must Have |
| US-LB3 | As a member, I want to see who has accumulated the most points of all time so that I can identify the community's most established contributors | Must Have |
| US-LB4 | As a member, I want to see my own rank if I'm not in the top 10 so that I know where I stand regardless of my position | Must Have |
| US-LB5 | As a member, I want to see gold, silver, and bronze medals for the top 3 so that top positions feel special | Must Have |
| US-LB6 | As a member, I want to see each ranked member's level badge so that I can see their overall standing alongside their ranking | Must Have |
| US-LB7 | As a member, I want to see how many points each ranked member earned in the period (or their total for all-time) so that I can understand the performance gap | Must Have |
| US-LB8 | As a member, I want to see when the leaderboard was last updated so that I know how fresh the data is | Must Have |

### 2.2 Sidebar Widget

| ID | Story | Priority |
|----|-------|----------|
| US-SW1 | As a member, I want to see a compact 30-day leaderboard in the Community feed sidebar so that I can check rankings without leaving the feed | Must Have |
| US-SW2 | As a member, I want to click "See all leaderboards" in the sidebar widget so that I can navigate to the full leaderboard page | Must Have |

---

## 3. Business Rules

### 3.1 Leaderboard Periods

Three leaderboard views are available on the Leaderboards page, displayed simultaneously:

| Period | Definition |
|--------|------------|
| **7-day** | Net points earned in the rolling last 168 hours (7 × 24h) from the time of query |
| **30-day** | Net points earned in the rolling last 720 hours (30 × 24h) from the time of query |
| **All-time** | Member's total accumulated points (lifetime) |

**Rolling window:** The 7-day and 30-day periods are not fixed calendar weeks/months. They slide continuously relative to the current time. A point transaction from 6 days and 23 hours ago is counted in the 7-day board; one from 7 days and 1 hour ago is not.

**Net points:** For 7-day and 30-day, net points = sum of all positive transactions minus sum of all negative transactions (deductions from unlikes) within the window. If net points for a member in a period is negative, display 0.

### 3.2 Ranking Rules

- Members are ranked by net points earned in the period (descending)
- For the all-time board, members are ranked by total accumulated points (descending)
- **Tie-breaking:** When two or more members have identical points for a period, they are ranked alphabetically by display name (A→Z)
- All community members are eligible to appear on the leaderboard, including those with 0 points
- Members with 0 points for a period rank below all members with > 0 points, with ties among them broken alphabetically

### 3.3 Top 10 Display

Each leaderboard shows the top 10 members by default. If fewer than 10 members have been awarded any points (including 0-point members if there are fewer than 10 total members), show all available members.

**Medal icons for top 3:**

| Rank | Medal |
|------|-------|
| 1 | Gold trophy/medal icon |
| 2 | Silver trophy/medal icon |
| 3 | Bronze trophy/medal icon |
| 4–10 | Rank number only |

### 3.4 "Your Rank" Row

A "Your rank" row is shown below the top 10 list under the following conditions:

- **Show "Your rank":** when the current member is NOT in the top 10 for that period
- **Hide "Your rank":** when the current member IS in the top 10 (they can already see themselves in the list)
- **Always show** even if the member earned 0 points in the period (motivates participation)

The "Your rank" row displays the member's exact rank position, their avatar with level badge, their name, and their points for the period (or total for all-time). It is visually separated from the top 10 list (e.g., by a divider).

### 3.5 Point Value Display

| Leaderboard | Points Column Label | Value Shown |
|-------------|--------------------|-|
| 7-day | +X | Net points earned in last 7 days |
| 30-day | +X | Net points earned in last 30 days |
| All-time | (no prefix) | Total accumulated points |

For period leaderboards, points are displayed with a `+` prefix (e.g., `+7`). For all-time, points are shown as plain integers (e.g., `942`).

### 3.6 Last Updated Timestamp

A "Last updated: [date and time]" timestamp is displayed on the leaderboard page. This reflects when the leaderboard data was last computed. The timestamp uses a human-readable format (e.g., "Feb 15th 2026 2:11pm").

### 3.7 Sidebar Widget

The leaderboard sidebar widget appears on the Community feed page in the right sidebar:

- Shows the **30-day leaderboard only** (fixed period — not user-configurable)
- Displays **top 5 members** (not top 10) to fit the compact widget format
- Each entry shows: rank number, member avatar (with level badge), member name, points in period
- A "See all leaderboards" link at the bottom navigates to the full Leaderboards page
- No "Your rank" row in the sidebar widget (space-constrained)

### 3.8 Level Definitions Section (Existing)

The Leaderboards page also displays the level definitions grid (all 9 levels with names, thresholds, and percentage of members at each level) at the top of the page, above the ranking panels. This was defined in the Points & Levels PRD (Section 4.3) and is already partially implemented. The leaderboard PRD requires this to be rendered as the top section of the same page.

---

## 4. UI Behavior

### 4.1 Leaderboards Page Layout

**URL:** `/leaderboards`

**Overall structure (single page):**
1. **Top section:** Current member's profile card (left) + level definitions grid (right) — already implemented from Points & Levels
2. **Last updated timestamp** — shown below the level definitions section
3. **Three side-by-side leaderboard panels** — 7-day, 30-day, all-time

**Top section profile card (left column):**
- Member avatar with level badge
- Member display name
- "Level X - [Level Name]"
- "X points to level up" (or nothing if Level 9)

**Level definitions grid (right column):**
- All 9 levels in a two-column layout
- Lock icon on levels above current member's level
- Current level highlighted
- "X% of members" at each level
- Already implemented — reference Points & Levels Phase 2

### 4.2 Leaderboard Panel (Each of 3 Columns)

**Panel header:** "Leaderboard (7-day)" / "Leaderboard (30-day)" / "Leaderboard (All-time)"

**Each rank entry (rows 1–10):**
- Rank number on the left
- Medal icon overlay on rank number for positions 1, 2, 3 (gold/silver/bronze)
- Member avatar with level badge
- Member display name
- Points for the period (right-aligned), with `+` prefix for timed boards

**"Your rank" divider and row (shown only if current member is outside top 10):**
- Visual separator (e.g., horizontal rule or ellipsis row)
- "Your rank" label
- Same format as rank entries above (rank position, avatar with level badge, name, points)

**States:**
- **Loading:** Skeleton placeholders for each row (shimmer animation)
- **Empty (no members with points):** Short message "No rankings yet — be the first to earn points!"
- **Error:** "Failed to load leaderboard. Please try again."

**Three-panel layout:** Side-by-side columns with equal width on desktop. On mobile, stacks vertically with tabs or accordion to switch between periods.

### 4.3 Sidebar Widget (Community Feed)

**Location:** Right sidebar on Community feed page (`/community`), below the community info card

**Widget structure:**
- Section header: "Leaderboard (30-day)"
- Up to 5 rank entries, each showing: rank number, avatar (with level badge), name, points
- "See all leaderboards" link at the bottom (navigates to `/leaderboards`)

**States:**
- **Loading:** Skeleton placeholders for 5 rows
- **Empty:** Widget hidden or shows "No rankings yet" message
- **Error:** Widget hidden silently (non-critical — feed should not be disrupted by leaderboard failure)

---

## 5. Edge Cases

### 5.1 Fewer Than 10 Members

**Scenario:** A new community has only 3 members.

**Behavior:**
- Leaderboard shows only the 3 members who exist (no empty placeholder rows)
- "Your rank" row is suppressed because all members are visible in the top list

### 5.2 Current Member in Top 10

**Scenario:** The current member is ranked 4th in the 7-day leaderboard.

**Behavior:**
- Their row appears at rank 4 in the main list (no additional "Your rank" section)
- This applies to all three leaderboard panels independently — a member could be in top 10 for 30-day but not for 7-day

### 5.3 Current Member Has 0 Points in Period

**Scenario:** A member has never created content but is viewing the 7-day leaderboard.

**Behavior:**
- "Your rank" row appears below the top 10
- Shows their rank position (e.g., rank 45 if 44 other members earned >0 points)
- Points shown as `+0`

### 5.4 Tied Ranks

**Scenario:** Members A (Alice) and B (Bob) both earned 10 points in the 7-day period.

**Behavior:**
- Alice ranks above Bob (alphabetical: "Alice" < "Bob")
- Both show the same point value (+10)
- Ranks are sequential (not shared): Alice is rank 5, Bob is rank 6 (no rank 5.5 or double rank 5)

### 5.5 Points Deducted Below 0 for Period

**Scenario:** A member earned 2 points in the 7-day period from likes but those likes were subsequently removed, resulting in -1 net points for the period.

**Behavior:**
- Display 0 (not negative) for the period points
- The member is ranked at the bottom of those with 0 points, among whom tie-breaking is alphabetical

### 5.6 All-Time vs. Period Rank Discrepancy

**Scenario:** A very active long-time member has the highest all-time points but hasn't engaged in the last 7 days.

**Behavior:**
- They appear at the top of the all-time leaderboard
- They appear in "Your rank" (or low in the list) for the 7-day leaderboard
- The three panels are independent — ranking is recalculated per period

### 5.7 Very Long Rank Number (Rank 1000+)

**Scenario:** A community has 2000 members and the current member is rank 1247.

**Behavior:**
- "Your rank" row shows "1247" without truncation
- Layout accommodates 4-digit rank numbers without overflow

---

## 6. Security Requirements

### 6.1 Authentication

- All leaderboard API endpoints require a valid authenticated session
- Unauthenticated requests receive a 401 Unauthorized response
- The sidebar widget respects the same authentication requirement as the rest of the feed

### 6.2 Authorization

| Action | Member | Moderator | Admin |
|--------|--------|-----------|-------|
| View 7-day leaderboard | ✓ | ✓ | ✓ |
| View 30-day leaderboard | ✓ | ✓ | ✓ |
| View all-time leaderboard | ✓ | ✓ | ✓ |
| View own rank position | ✓ | ✓ | ✓ |
| View sidebar widget | ✓ | ✓ | ✓ |

No admin-only leaderboard features in MVP.

### 6.3 Data Exposure

- Leaderboard data (member name, level, points) is considered public within the community — visible to all authenticated members
- Point totals and ranks are not sensitive — they reflect community engagement
- No personally identifiable information beyond display name and avatar is exposed

### 6.4 Query Safety

- Leaderboard queries must use parameterized queries with community scoping — a member cannot view leaderboards for a community they don't belong to
- All time-range calculations use server-side timestamps to prevent client-side manipulation

---

## 7. Out of Scope

### 7.1 Not in MVP

- Leaderboard period switching via UI tabs (all three periods shown simultaneously as in Skool)
- Pagination beyond top 10 (no "Load more" or full ranked list beyond top 10 + Your rank)
- Admin ability to reset or freeze leaderboards
- Opt-out from leaderboards (members cannot hide themselves from rankings)
- Separate leaderboards per category or topic
- Weekly/monthly reset announcements or celebration posts
- Real-time leaderboard updates (WebSocket streaming)
- Mobile-specific tab navigation between the three periods (responsive stacking is MVP)
- Highlighting when current member moves up in rank (rank change delta)
- Point history view from the leaderboard
- Custom leaderboard periods (e.g., annual)

### 7.2 Phase 2 Features

- Leaderboard caching with configurable refresh interval (admin setting)
- Leaderboard period tabs on mobile (rather than vertical stacking)
- Rank change delta indicator (e.g., "↑3 from last week")
- Admin ability to feature top members (e.g., "Member of the Month" spotlight)
- Filtering leaderboards by level or role

### 7.3 Phase 3 Features

- Leaderboard analytics dashboard for admins (engagement trends, points distribution)
- Community-to-community leaderboard comparison
- Achievement-based leaderboards (separate from points)
- API webhooks for leaderboard rank changes

---

## 8. Success Metrics

### 8.1 Engagement Metrics

| Metric | Measurement | Target |
|--------|-------------|--------|
| Leaderboard page views per DAU | Views per active user per session | > 0.3 views/session |
| Sidebar widget CTR | Clicks on "See all leaderboards" / widget impressions | > 15% |
| Engagement lift (7-day post-launch) | % change in daily likes + posts + comments | > 10% |

### 8.2 Quality Metrics

| Metric | Measurement | Target |
|--------|-------------|--------|
| Members checking their rank weekly | % of active members who view leaderboards ≥1/week | > 25% |
| Leaderboard stickiness | % of members who view leaderboards in 2+ consecutive weeks | > 40% of leaderboard viewers |

### 8.3 Technical Metrics

| Metric | Measurement | Target |
|--------|-------------|--------|
| Leaderboard API response time (p95) | Time to return all three leaderboards | < 400ms |
| Sidebar widget load time (p95) | Time to render widget data | < 200ms |

---

## 9. Dependencies

### 9.1 Upstream Dependencies

**Gamification Context (Points & Levels — Complete):**
- `MemberPoints` entity with `total_points`, `current_level`, and `transactions` (with timestamps and points per transaction) — required to compute period rankings
- `LevelConfiguration` entity — required to display level badge on leaderboard entries
- `list_by_community()` method on `IMemberPointsRepository` — basis for ranking queries
- Level definitions display section (already implemented in `LevelDefinitionsGrid` component) — rendered at top of leaderboard page

**Identity/Community Context:**
- Member display name and avatar — required for each leaderboard row
- `UserId` value object for scoping queries to the current user

### 9.2 Downstream Consumers

None in MVP. Leaderboard data is read-only, produced from the points system.

---

## 10. Open Questions

None — all questions resolved during discovery.

---

## 11. Appendix

### 11.1 Related Documents

- `docs/prd_summary/PRD/OVERVIEW_PRD.md` — Master PRD (Section 3.7.3: Leaderboard Views)
- `docs/domain/GLOSSARY.md` — Ubiquitous language (Gamification Context)
- `docs/architecture/CONTEXT_MAP.md` — Bounded context relationships
- `docs/features/gamification/points-prd.md` — Points & Levels PRD (upstream dependency, complete)
- `tests/features/gamification/leaderboards.feature` — BDD specifications for this feature
- `docs/features/gamification/UI_SPEC.md` — Visual design specification

### 11.2 Screenshot References

- `docs/features/gamification/screenshots/leaderboard-page-top.png` — Full leaderboards page layout
- `docs/features/gamification/screenshots/leaderboard-page-bottom-your-rank.png` — "Your rank" row below top 10
- `docs/features/gamification/screenshots/sidebar-leaderboard-widget.png` — Community feed sidebar widget

### 11.3 Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-18 | Product Team | Initial draft |

---

## 12. Approval

**Product Owner:** _________________
**Engineering Lead:** _________________
**Design Lead:** _________________

**Status:** Draft — Pending Review
