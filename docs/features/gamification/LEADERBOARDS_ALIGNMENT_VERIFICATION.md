# Alignment Verification — Leaderboards

**Feature:** Leaderboards
**Last Updated:** February 18, 2026

---

## 1. PRD → BDD Coverage

Every PRD user story and business rule is mapped to at least one BDD scenario.

### User Stories

| PRD ID | User Story | BDD Scenario(s) | Status |
|--------|-----------|-----------------|--------|
| US-LB1 | See top earners in last 7 days | "Member views the 7-day leaderboard with ranked members" | Covered |
| US-LB2 | See top earners in last 30 days | "Member views the 30-day leaderboard with rolled-up period points" | Covered |
| US-LB3 | See top earners all time | "Member views the all-time leaderboard using total accumulated points" | Covered |
| US-LB4 | See own rank if not in top 10 | "Member outside top 10 sees their own rank below the list" | Covered |
| US-LB5 | Gold/silver/bronze medals for top 3 | "ranks 1, 2, 3 have medal indicators" | Covered |
| US-LB6 | See level badge on each entry | "each entry includes the member's level badge" | Covered |
| US-LB7 | See points earned per entry | "rank 1 is Bob Builder with 15 points" + point display scenarios | Covered |
| US-LB8 | See last updated timestamp | "Last updated timestamp is included in the leaderboard response" | Covered |
| US-SW1 | Compact 30-day widget in sidebar | "Community feed sidebar widget shows the 30-day top-5 leaderboard" | Covered |
| US-SW2 | Click "See all leaderboards" link | "widget includes a link to the leaderboards page" | Covered |

### Business Rules

| PRD Rule | BDD Scenario(s) | Status |
|----------|-----------------|--------|
| 3.1 Rolling 7-day window (168h) | "Points earned outside the rolling window are excluded" | Covered |
| 3.1 Rolling 30-day window (720h) | "Member views the 30-day leaderboard with rolled-up period points" | Covered |
| 3.1 All-time = total accumulated | "Member views the all-time leaderboard" + "All-time leaderboard includes total accumulated points regardless of when earned" | Covered |
| 3.2 Net points (positive - negative) | "Negative net period points are displayed as zero" | Covered |
| 3.2 Rank by points descending | "rank 1 is Bob Builder with 15 points" (highest first) | Covered |
| 3.2 Tie-breaking alphabetically | "Ties in points are broken alphabetically by display name" | Covered |
| 3.3 Top 10 display | "response contains 10 ranked members" | Covered |
| 3.3 <10 members shows all | "Fewer than 10 members in community shows all available members" | Covered |
| 3.3 Medal icons for top 3 | "ranks 1, 2, 3 have medal indicators (gold, silver, bronze)" | Covered |
| 3.4 Your rank shown when outside top 10 | "Member outside top 10 sees their own rank below the list" | Covered |
| 3.4 Your rank hidden when inside top 10 | "Member inside top 10 does not receive a separate your-rank entry" | Covered |
| 3.4 Your rank with 0 points | "Member with zero points in period still receives a your-rank entry" | Covered |
| 3.5 Points prefix (+X for periods) | "Points earned in period shown with plus prefix for timed boards" | Covered |
| 3.5 No prefix for all-time | "all-time leaderboard displays total points without a plus prefix" | Covered |
| 3.6 Last updated timestamp | "Last updated timestamp is included in the leaderboard response" | Covered |
| 3.7 Widget shows 30-day top 5 | "widget contains exactly 5 entries" | Covered |
| 3.7 Widget no your-rank | "widget does not include a your_rank row" | Covered |
| 3.7 Widget has link to full page | "widget includes a link to the leaderboards page" | Covered |

### Edge Cases

| PRD Edge Case | BDD Scenario | Status |
|---------------|-------------|--------|
| 5.1 Fewer than 10 members | "Fewer than 10 members in community shows all available members" | Covered |
| 5.2 Current member in top 10 | "Member inside top 10 does not receive a separate your-rank entry" | Covered |
| 5.3 Zero points in period | "Member with zero points in period still receives a your-rank entry" | Covered |
| 5.4 Tied ranks | "Ties in points are broken alphabetically by display name" | Covered |
| 5.5 Negative net in period | "Negative net period points are displayed as zero" | Covered |
| 5.6 All-time vs. period discrepancy | "Member views the all-time leaderboard" (Bob top all-time, low 7-day) | Covered |
| 5.7 Very long rank number | No explicit BDD scenario (layout concern, tested in frontend) | Note [1] |

### Security

| PRD Security Rule | BDD Scenario | Status |
|-------------------|-------------|--------|
| 6.1 Authentication required | "Unauthenticated user cannot view leaderboards", "Unauthenticated user cannot view the sidebar widget" | Covered |
| 6.4 Cross-community isolation | "Member cannot view leaderboard for a community they do not belong to" | Covered |

---

## 2. BDD → TDD Coverage

Every BDD scenario group maps to TDD design elements.

| BDD Scenario Group | TDD Section | Design Element |
|-------------------|-------------|----------------|
| 7-day leaderboard ranking | §4.2 Query Strategy, §6.2 Repository methods | Period aggregation with rolling 168h window |
| 30-day leaderboard ranking | §4.2 Query Strategy, §6.2 Repository methods | Period aggregation with rolling 720h window |
| All-time leaderboard ranking | §4.2 Query Strategy | Direct ORDER BY on total_points |
| Point display format (+prefix) | §5.2 API response contract | Frontend formatting per period type |
| Your rank (outside top 10) | §4.2 Your rank computation, §6.2 | ROW_NUMBER() window function |
| Your rank (inside top 10) | §5.2 API contract | your_rank = null when in entries |
| Your rank (0 points) | §4.2, §6.5 Invariant #1 | GREATEST(0, sum) + rank computation |
| Sidebar widget (30-day top 5) | §5.2 Widget API, §7.1 GetLeaderboardWidgetQuery | Separate endpoint, limit=5 |
| Fewer than 10 members | §5.2 API contract | entries array length < 10, no your_rank |
| Ties broken alphabetically | §6.5 Invariant #2 | ORDER BY points DESC, display_name ASC |
| Negative net floored at zero | §6.5 Invariant #1 | GREATEST(0, SUM(points)) |
| Rolling window exclusion | §4.2 Query Strategy | WHERE created_at >= NOW() - interval |
| All-time totals | §4.2 Query Strategy | Uses total_points column directly |
| Last updated timestamp | §5.2 API contract | last_updated field in response |
| Authentication (401) | §9.1 Authentication | Existing JWT middleware |
| Cross-community (403) | §9.2 Authorization | community_id scoping + membership check |

---

## 3. PRD → TDD Direct Coverage

| PRD Requirement | TDD Coverage |
|----------------|-------------|
| 3 leaderboard periods (§3.1) | §4.2 Query Strategy — three distinct query patterns |
| Rolling windows (§3.1) | §4.2 — NOW() - interval filter on point_transactions |
| Net points >= 0 (§3.2) | §6.5 Invariant #1 — GREATEST(0, SUM) |
| Alphabetical tie-breaking (§3.2) | §6.5 Invariant #2 — ORDER BY display_name ASC |
| Top 10 display (§3.3) | §5.2 API — entries array, LIMIT 10 |
| Medal icons (§3.3) | §17.1 — RankMedal.tsx component |
| Your rank section (§3.4) | §4.2, §5.2 — your_rank computation and response |
| Point display format (§3.5) | §5.2 — period type determines display |
| Last updated (§3.6) | §5.2 — last_updated ISO timestamp |
| Sidebar widget 30-day top 5 (§3.7) | §5.2 Widget API — separate endpoint, limit=5 |
| Performance < 400ms (§8.3) | §10.1 — performance targets match PRD |
| Widget < 200ms (§8.3) | §10.1 — widget target matches PRD |

---

## 4. UI_SPEC → TDD Coverage

| UI_SPEC Component | TDD Reference | File Path in Checklist |
|-------------------|---------------|----------------------|
| LeaderboardPanel | §17.1 Frontend files | `frontend/src/features/gamification/components/LeaderboardPanel.tsx` |
| LeaderboardRow | §17.1 Frontend files | `frontend/src/features/gamification/components/LeaderboardRow.tsx` |
| LeaderboardRowSkeleton | §17.1 Frontend files | `frontend/src/features/gamification/components/LeaderboardRowSkeleton.tsx` |
| RankMedal | §17.1 Frontend files | `frontend/src/features/gamification/components/RankMedal.tsx` |
| YourRankSection | §17.1 Frontend files | `frontend/src/features/gamification/components/YourRankSection.tsx` |
| LeaderboardSidebarWidget | §17.1 Frontend files | `frontend/src/features/gamification/components/LeaderboardSidebarWidget.tsx` |
| LeaderboardProfileCard | §17.1 Frontend files | `frontend/src/features/gamification/components/LeaderboardProfileCard.tsx` |
| LeaderboardsPage (enhanced) | §17.1 Modified files | `frontend/src/pages/LeaderboardsPage.tsx` |
| CommunitySidebar (enhanced) | §17.1 Modified files | `frontend/src/features/community/components/CommunitySidebar.tsx` |
| useLeaderboards hook | §17.1 Frontend files | `frontend/src/features/gamification/hooks/useLeaderboards.ts` |
| useLeaderboardWidget hook | §17.1 Frontend files | `frontend/src/features/gamification/hooks/useLeaderboardWidget.ts` |

---

## 5. Gap Analysis

### Identified Gaps: None

All PRD requirements, BDD scenarios, and UI_SPEC components have corresponding TDD design elements.

### Notes

1. **PRD Edge Case 5.7 (Very long rank number):** No explicit BDD scenario because this is a layout/CSS concern. The UI_SPEC addresses it (`w-6` rank column, `text-xs` for large numbers). Frontend component tests will cover this.

2. **PRD §3.8 (Level definitions at page top):** Already implemented by Points & Levels. The TDD references the existing `LevelDefinitionsGrid` component and `useLevelDefinitions` hook as reused components. No new design needed.

3. **PRD §4.1 (Profile card at page top):** Covered by `LeaderboardProfileCard` component in UI_SPEC and TDD file checklist.

4. **Widget error silence (PRD §4.3):** The TDD addresses this in §8.3 Failure Modes — widget renders null on API failure. Frontend component handles this internally.

---

## 6. Approval Checklist

- [x] All PRD user stories (US-LB1 through US-LB8, US-SW1, US-SW2) mapped to BDD scenarios
- [x] All PRD business rules (§3.1-§3.8) mapped to BDD scenarios
- [x] All PRD edge cases (§5.1-§5.7) mapped to BDD scenarios or noted
- [x] All PRD security requirements (§6.1-§6.4) mapped to BDD scenarios
- [x] All BDD scenarios (17 total) have corresponding TDD design elements
- [x] All UI_SPEC components (11 total) appear in TDD file checklist
- [x] Component names match between UI_SPEC and TDD
- [x] No orphaned requirements (PRD items without design)
- [x] No orphaned design (TDD elements without PRD backing)
- [x] Performance targets in TDD match PRD §8.3
- [x] Architecture follows established Gamification context patterns
- [x] No new dependencies required
- [x] Cross-context read dependency (profiles JOIN) documented and justified

---

**Status:** Complete — Ready for Review
