# Member Directory — Product Requirements Document

**Feature:** Member Directory
**Module:** Members
**Status:** Draft
**Version:** 1.0
**Last Updated:** February 13, 2026
**Implementation Status:** Not Started
**Bounded Context:** Community
**PRD Type:** Feature Specification

---

## 1. Overview

### 1.1 What

The Member Directory provides a browsable, searchable list of all members within a community. It is the primary way members discover and connect with each other. The directory displays member cards in a vertical list with profile information, supports search by name, filtering by role via pill tabs with counts, and sorting by join date or alphabetically. It is accessible via a dedicated "Members" tab in the main navigation.

### 1.2 Why

Communities thrive on connections between members. Without a directory, members have no way to discover who else is in the community, find people with shared interests, or identify community leaders. The directory makes the community feel alive and encourages interaction — it's the social backbone that turns a content platform into a real community.

### 1.3 Success Criteria

| Metric | Measurement | Target |
|--------|-------------|--------|
| Profile views from directory | % of directory visitors who click into a profile | > 20% |
| Directory page visits | Rank among most visited pages | Top 3 within 30 days of launch |
| Search usage | % of directory visits that use search | > 15% |

---

## 2. User Stories

### 2.1 Browsing

| ID | Story | Priority |
|----|-------|----------|
| US-D1 | As a member, I want to see a list of all members in my community so that I can discover who else is part of the community | Must Have |
| US-D2 | As a member, I want to access the member directory from the main navigation so that I can quickly find community members from any page | Must Have |

### 2.2 Search & Filter

| ID | Story | Priority |
|----|-------|----------|
| US-D3 | As a member, I want to search for members by name so that I can quickly find a specific person | Must Have |
| US-D4 | As a member, I want to filter the directory by role (Admin, Moderator, Member) so that I can find community leaders or staff | Must Have |
| US-D5 | As a member, I want to sort members by join date or alphabetically so that I can find the newest members or browse alphabetically | Must Have |

### 2.3 Profile Navigation

| ID | Story | Priority |
|----|-------|----------|
| US-D6 | As a member, I want to click on a member card to see their full profile so that I can learn more about them and see their activity | Must Have |

---

## 3. Business Rules

### 3.1 Access Control

- Only authenticated members of the community can view the member directory.
- Non-members and unauthenticated users cannot access the directory.

### 3.2 Member Visibility

- Only active members are shown in the directory.
- Deactivated or banned members are excluded.

### 3.3 Member Card Information

Each member card displays:

| Field | Source | Behavior |
|-------|--------|----------|
| Avatar | Profile | Default placeholder if none set |
| Display name | Profile | Truncated with ellipsis if too long |
| Role badge | Community Member | Shown for Admin and Moderator only; no badge for regular members |
| Short bio | Profile | Truncated to ~80 characters; "No bio" placeholder if empty |
| Join date | Community Member | Relative format (e.g., "Joined 3 months ago") |

### 3.4 Sorting

Two sort options are available:

| Sort | Behavior | Default |
|------|----------|---------|
| Most Recent | Newest members first, ordered by join date descending | Yes |
| Alphabetical | Ordered by display name A→Z | No |

### 3.5 Filtering

| Filter | Type | Behavior |
|--------|------|----------|
| Search by name | Text input | Case-insensitive partial match on display name |
| Filter by role | Pill tabs with counts | Tabs: All (default), Admin, Moderator — each shows matching member count |

- Filters and search can be combined (e.g., search "John" + filter "Admin").
- Clearing search/filters returns to the full unfiltered directory.

### 3.6 Pagination

- Members load in batches of 20.
- Additional members load automatically as the user scrolls down (infinite scroll).
- A loading indicator appears while fetching the next batch.
- When all members are loaded, no further requests are made.

### 3.7 Empty States

| Condition | Message |
|-----------|---------|
| No members match search/filter | "No members found. Try adjusting your search or filters." |
| Community has no members | "No members yet." |

---

## 4. UI Behavior

### 4.1 Members Tab

- A "Members" tab appears in the main navigation bar alongside "Community" and "Classroom".
- The tab shows the total member count as a badge (e.g., "Members (42)").

### 4.2 Directory Page Layout

**Layout:**
- Top section: Filter controls and search
  - Role filter pill tabs with counts: All (N) / Admin (N) / Moderator (N)
  - Sort dropdown: Most Recent / Alphabetical
  - Search input with placeholder text "Search members..."
- List section: Member cards in a vertical list (full-width cards)
  - Desktop: Two-column layout — member list (main) + community sidebar (320px)
  - Mobile: Single column, sidebar hidden

**States:**
- Loading: Skeleton cards (gray placeholders) while members are fetched
- Empty: "No members found" with suggestion to adjust filters
- Error: "Failed to load members. Retry?" with retry button

**Interactions:**
- Typing in search → Directory filters in real-time (debounced ~300ms)
- Clicking a role filter tab → Directory re-filters immediately; active tab fills dark
- Changing sort → Directory re-sorts immediately
- Scrolling to bottom → Next batch of members loads automatically
- Clicking a member card → Navigates to `/profile/:userId` (existing profile page)

### 4.3 Member Card

**Display:**
- Circular avatar (or default placeholder)
- Display name (bold)
- Role badge (colored tag for Admin/Moderator, none for Member)
- Truncated bio
- Join date (relative format)

**Interactions:**
- Entire card is clickable — navigates to the member's profile page
- Hover state provides visual feedback (subtle elevation or border highlight)

### 4.4 Loading States

| State | Behavior |
|-------|----------|
| Initial load | Skeleton cards (gray placeholders) |
| Loading more | Small spinner at the bottom of the list |
| Search/filter change | Existing results stay visible briefly, then update |

### 4.5 Notifications (Visual Feedback)

**Error messages:**
- "Failed to load members. Please try again."
- "You don't have permission to view this directory."

---

## 5. Edge Cases

### 5.1 Member with No Profile

**Scenario:** Member hasn't completed their profile

**Behavior:**
- Default avatar placeholder shown
- "No bio" placeholder text
- Display name still shown (set during registration)

### 5.2 Very Long Display Names

**Scenario:** Display name exceeds card width

**Behavior:**
- Name truncated with ellipsis
- Full name visible on profile page

### 5.3 Large Communities

**Scenario:** Community has hundreds or thousands of members

**Behavior:**
- Infinite scroll handles pagination transparently
- First batch loads quickly; subsequent batches load on demand
- Total member count shown in tab badge

### 5.4 Concurrent Member Changes

**Scenario:** A member joins or leaves while another member is browsing the directory

**Behavior:**
- Directory reflects changes on the next batch load or page refresh
- Real-time updates are not required for MVP

### 5.5 Network Errors

**Scenario:** A batch fails to load

**Behavior:**
- Show inline error message with a "Retry" button
- Previously loaded members remain visible

---

## 6. Security Requirements

### 6.1 Authentication

- All member directory endpoints require a valid authentication token.
- Expired tokens rejected with 401 Unauthorized.

### 6.2 Authorization

- Users must be an active member of the community to view its member directory.
- Requests from non-members return an authorization error (403 Forbidden).

### 6.3 Data Protection

- Only public profile information is shown (display name, avatar, bio, join date, role).
- Private information (email, settings, etc.) is never exposed through the directory.

---

## 7. Out of Scope

### 7.1 Not in MVP

- Online status indicator (requires real-time WebSocket presence)
- Gamification data (points, levels, level badges) — depends on unbuilt Gamification context
- "Most active" sorting — requires activity aggregation not yet implemented
- "By level" sorting — requires Gamification
- Follow/unfollow from directory
- Direct message from directory — depends on unbuilt DM feature
- Admin tools (invite, ban, assign roles) — separate admin feature

### 7.2 Phase 2

- Level badges on member cards (after Gamification is built)
- "Most active" and "By level" sorting
- Online status indicator
- Follow/unfollow functionality
- Admin member management tools

### 7.3 Phase 3

- Member map (geographic view)
- Mutual connections
- Advanced analytics (member engagement scores)

---

## 8. Success Metrics

### 8.1 Engagement Metrics

| Metric | Measurement | Target |
|--------|-------------|--------|
| Directory visits | Unique visitors per day | > 20% of DAU |
| Profile clicks | % of directory visitors clicking a member card | > 20% |
| Search usage | % of directory visits using search | > 15% |

### 8.2 Quality Metrics

| Metric | Measurement | Target |
|--------|-------------|--------|
| Time to first interaction | Time from page load to first search/click | < 10 seconds |
| Filter usage | % of visits using role filter | > 10% |

### 8.3 Technical Metrics

| Metric | Measurement | Target |
|--------|-------------|--------|
| Directory load time | Time to render first 20 member cards | < 1 second (p95) |
| API response time | Member listing latency | < 200ms (p95) |
| Error rate | % of API requests failing | < 1% |

---

## 9. Dependencies

### 9.1 Upstream Dependencies

**Identity Context:**
- UserId value object
- User authentication (JWT tokens)
- User profile information (display_name, avatar_url, bio)

**Community Context (existing):**
- CommunityMember entity (user_id, community_id, role, joined_at, is_active)
- IMemberRepository with `list_by_community()` method

**Infrastructure:**
- PostgreSQL database
- Existing profile API endpoints

### 9.2 Downstream Consumers

**Gamification Context (Phase 2):**
- Will enrich member cards with points and level badges once built

**Notification Context (Future):**
- May consume directory browsing events for analytics

---

## 10. Open Questions

None — all decisions resolved during discovery:
1. Member card content → Name, avatar, bio, role, join date (no gamification for MVP)
2. View mode → Vertical list (full-width cards, matching Skool.com)
3. Access → Authenticated community members only
4. Sorting → Most recent + alphabetical
5. Filtering → Name search + role pill tabs with counts
6. Pagination → Infinite scroll, 20 per batch
7. Profile navigation → Reuse existing ProfileView page

---

## 11. Appendix

### 11.1 Related Documents

- `docs/prd_summary/PRD/OVERVIEW_PRD.md` — Master PRD (Section 3.5: Members Module)
- `docs/domain/GLOSSARY.md` — Ubiquitous language definitions
- `docs/architecture/CONTEXT_MAP.md` — Bounded context relationships
- `tests/features/members/directory.feature` — BDD specifications for this feature

### 11.2 Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-13 | Product Team | Initial draft for MVP |
| 1.1 | 2026-02-13 | Product Team | Harmonized with Skool.com: grid → vertical list, role dropdown → pill tabs with counts |

---

## 12. Approval

**Product Owner:** _________________
**Engineering Lead:** _________________
**Design Lead:** _________________

**Status:** Draft — Pending Review
