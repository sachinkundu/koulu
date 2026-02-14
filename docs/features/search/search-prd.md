# Search — Product Requirements Document

**Feature:** Search
**Module:** Search (Cross-cutting)
**Status:** Draft
**Version:** 1.0
**Last Updated:** February 14, 2026
**Implementation Status:** Phase 1 of 3 Complete
**Bounded Context:** Community (MVP — members and posts are both Community-owned)
**PRD Type:** Feature Specification

---

## 1. Overview

### 1.1 What

A global search feature accessible from the header bar that allows community members to find other members and posts by typing a query. Results are displayed on a dedicated search results page with tabs separating content types (Members and Posts). Members are displayed as profile cards sorted alphabetically; posts are displayed as content cards sorted by newest first.

### 1.2 Why

As communities grow, finding specific people or past discussions becomes increasingly difficult. Scrolling through the feed or member directory is impractical at scale. Search gives members instant access to the content and people they're looking for, reducing friction and increasing engagement. This is a core platform utility — Skool.com places the search bar prominently in the header, signaling its importance to the user experience.

### 1.3 Success Criteria

| Metric | Target |
|--------|--------|
| Search adoption | > 30% of active members use search weekly |
| Results relevance | > 80% of searches return at least 1 relevant result |
| Search-to-action rate | > 40% of searches lead to a profile view or post click |
| Search latency (p95) | < 500ms |
| Zero-result rate | < 20% of searches return no results |

---

## 2. User Stories

### 2.1 Search Input

| ID | Story | Priority |
|----|-------|----------|
| US-S1 | As a member, I want to type a query in the header search bar so that I can find people or content | Must Have |
| US-S2 | As a member, I want to press Enter to execute my search so that results load on a dedicated page | Must Have |
| US-S3 | As a member, I want to clear my search input so that I can start a new search | Must Have |
| US-S4 | As a member, I want my search query to persist in the URL so that I can share or bookmark a search | Should Have |

### 2.2 Search Results — Members

| ID | Story | Priority |
|----|-------|----------|
| US-SM1 | As a member, I want to see matching members when I search so that I can find people in the community | Must Have |
| US-SM2 | As a member, I want member results to show avatar, name, username, bio, online status, join date, and location so that I can identify the right person | Must Have |
| US-SM3 | As a member, I want member results sorted alphabetically so that I can scan them predictably | Must Have |
| US-SM4 | As a member, I want to click a member result to view their full profile | Must Have |

### 2.3 Search Results — Posts

| ID | Story | Priority |
|----|-------|----------|
| US-SP1 | As a member, I want to see matching posts when I search so that I can find discussions I'm looking for | Must Have |
| US-SP2 | As a member, I want post results to show title, content snippet, author, category, and timestamp so that I can decide which post to read | Must Have |
| US-SP3 | As a member, I want post results sorted by newest first so that I see the most recent discussions | Must Have |
| US-SP4 | As a member, I want to click a post result to view the full post | Must Have |

### 2.4 Result Tabs & Navigation

| ID | Story | Priority |
|----|-------|----------|
| US-ST1 | As a member, I want to see results separated into "Members" and "Posts" tabs so that I can focus on the type I need | Must Have |
| US-ST2 | As a member, I want each tab to show the count of matching results so that I know how many matches exist | Must Have |
| US-ST3 | As a member, I want to switch between tabs without re-executing the search | Must Have |
| US-ST4 | As a member, I want paginated results (10 per page) with Previous/Next navigation so that I can browse through many results | Must Have |

---

## 3. Business Rules

### 3.1 Query Rules

- **Minimum query length:** 3 characters. Queries shorter than 3 characters are rejected with a helpful message.
- **Maximum query length:** 200 characters.
- **Query trimming:** Leading and trailing whitespace is stripped before searching.
- **Empty query:** If the user navigates to the search page with no query, show a prompt to enter a search term.

### 3.2 Searchable Content — Members

Members are matched against the following fields:
- **Display name** (e.g., "Sachin Kundu")
- **Username** (e.g., "sachin-kundu-3386")
- **Bio** (e.g., "Experienced software engineer and serial failed entrepreneur")

All fields are searched using full-text matching with stemming support (e.g., searching "engineer" also matches "engineering").

### 3.3 Searchable Content — Posts

Posts are matched against the following fields:
- **Title**
- **Body content**

Only published (non-deleted) posts are included in search results.

### 3.4 Result Ordering

| Content Type | Sort Order | Rationale |
|-------------|-----------|-----------|
| Members | Alphabetical by display name | Predictable, easy to scan |
| Posts | Newest first (created_at descending) | Most recent discussions are most relevant |

### 3.5 Access Rules

| Rule | Description |
|------|-------------|
| Authentication required | Only authenticated, logged-in users can search |
| Community membership required | Users can only search within communities they belong to |
| Inactive members excluded | Deactivated or banned members do not appear in results |
| Deleted posts excluded | Soft-deleted posts do not appear in results |

### 3.6 Rate Limiting

- Search queries: 30 per minute per user
- Prevents abuse and excessive load on the database

---

## 4. UI Behavior

### 4.1 Header Search Bar

**Layout (from Skool.com screenshots):**
- Positioned center of header, between community name/logo (left) and user menu icons (right)
- Full-width text input (~50% of header width)
- Magnifying glass icon on the left inside the input
- Placeholder text: "Search members" (changes contextually — future: "Search posts, members...")
- Light gray background with rounded corners
- Clear button (X) appears when text is entered

**Interactions:**
- Click input → Focus with cursor, ready for typing
- Type query + press Enter → Navigate to search results page
- Click X → Clear input, stay on current page
- Search bar persists across all tabs (Community, Classroom, Calendar, Members, etc.)

**States:**
- Default: Placeholder text, unfocused
- Focused: Border highlight, cursor blinking
- With text: Clear (X) button visible
- Searching: Brief loading indicator on results page (not in header)

### 4.2 Search Results Page

**URL pattern:** `/search?q={query}&t={type}`
- `q` = search query string
- `t` = active tab: `members` (default) or `posts`

**Layout:**
- Header search bar pre-filled with the query
- Tab bar below header: "Members {count}" | "Posts {count}" (active tab underlined)
- Results list below tabs (left-aligned, main content area)
- Community sidebar on right (same as feed sidebar)

**Tab counts:**
- Each tab label shows result count (e.g., "Members 1", "Posts 12")
- Tabs with 0 results still visible but show "0"
- Default active tab: Members

### 4.3 Member Result Card

Each member result displays:
- Avatar with level badge overlay (top-left)
- **Display name** (bold, clickable → navigates to profile)
- **Username** (gray, below name, e.g., "@sachin-kundu-3386")
- **Bio** (truncated to 1-2 lines)
- **Online status** (green dot + "Online now" or gray)
- **Join date** (calendar icon + "Joined Jan 20, 2026")
- **Location** (pin icon + city, if available)

Card is clickable — entire card navigates to member profile.

### 4.4 Post Result Card

Each post result displays:
- **Post title** (bold, clickable → navigates to post detail)
- **Content snippet** (first ~200 characters of body, with search terms highlighted)
- **Author** (avatar + display name)
- **Category** badge
- **Timestamp** (relative: "3h ago")
- **Engagement** indicators: like count, comment count

Card is clickable — navigates to full post.

### 4.5 Pagination

- 10 results per page per tab
- "Previous" / "Next" navigation links at bottom
- Current page indicator: "1-10 of 47"
- Page 1 has no "Previous" link
- Last page has no "Next" link

### 4.6 Empty & Error States

**No results:**
- Message: "No {members|posts} found for '{query}'"
- Suggestion: "Try a different search term or browse the [member directory | community feed]"

**Query too short:**
- Message: "Please enter at least 3 characters to search"
- Search not executed

**Error state:**
- Message: "Search is temporarily unavailable. Please try again."
- Retry button

**No query:**
- Message: "Enter a search term above to find members and posts"

---

## 5. Edge Cases

### 5.1 Special Characters in Query

**Scenario:** User enters special characters (e.g., `<script>`, `'; DROP TABLE`, emojis)

**Behavior:** All input is sanitized. Special characters are treated as literal search terms. HTML/SQL is not executed. Emojis are included in the search if the content contains them.

### 5.2 Very Long Query

**Scenario:** User enters more than 200 characters

**Behavior:** Query is truncated to 200 characters. No error shown — silently capped.

### 5.3 No Community Membership

**Scenario:** Authenticated user who is not a member of the community tries to search

**Behavior:** 403 Forbidden. User sees "You must be a member of this community to search."

### 5.4 Concurrent Content Changes

**Scenario:** A post is deleted while search results are displayed

**Behavior:** Clicking the stale result shows a 404 page. Search results are not live-updated — user must re-search to see current state.

### 5.5 Members with No Profile Data

**Scenario:** A member has not completed their profile (no bio, no location)

**Behavior:** Member still appears in results if their display name or username matches. Missing fields show as empty (no placeholder text like "No bio").

### 5.6 Posts with Very Long Content

**Scenario:** Post body is 5,000 characters

**Behavior:** Result snippet shows first ~200 characters of body text. No highlighting of match position within long content (MVP simplification).

### 5.7 Rapid Re-Searching

**Scenario:** User types a query, presses Enter, then immediately changes query and presses Enter again

**Behavior:** Previous search request is abandoned. Only the latest query's results are displayed. No stale results flash on screen.

---

## 6. Security Requirements

### 6.1 Authentication

- All search endpoints require a valid JWT token
- Expired or missing tokens result in 401 Unauthorized
- Search bar is not visible to unauthenticated users

### 6.2 Authorization

- Users can only search within communities they are active members of
- Community membership is verified server-side on every search request
- Deactivated/banned members cannot search and do not appear in results

### 6.3 Input Validation

- Query string is sanitized to prevent SQL injection and XSS
- Maximum query length enforced (200 characters)
- Minimum query length enforced (3 characters)
- HTML tags stripped from query input
- Query parameters validated: `t` must be one of `members`, `posts`

### 6.4 Data Protection

- Search queries are not logged with personally identifiable information
- Rate limiting prevents brute-force enumeration of member data
- Search results respect the same access controls as direct navigation (no data leakage)

---

## 7. Out of Scope

### 7.1 Not in MVP

- Search suggestions / autocomplete as user types
- Recent search history (saved queries)
- Fuzzy matching / "Did you mean...?" suggestions
- Advanced filters on search results (by date, role, category)
- Search within specific category
- Highlighting of matched terms within result snippets
- Real-time search (as-you-type with debounce)
- Search analytics (popular queries, zero-result queries)

### 7.2 Phase 2

- Course and Lesson search (Classroom context)
- Comment search
- Relevance-based ranking (instead of alphabetical/date)
- Search result highlighting (bold matched terms)
- Search within specific module tabs (contextual search)
- Advanced filters (date range, category, role)

### 7.3 Phase 3

- Elasticsearch migration for better relevance and performance at scale
- Search suggestions / autocomplete
- Recent and popular searches
- Federated search across multiple communities
- Search analytics dashboard for admins

---

## 8. Success Metrics

### 8.1 Engagement Metrics

| Metric | Measurement | Target |
|--------|-------------|--------|
| Weekly search users | Unique members performing search per week | > 30% of active members |
| Searches per session | Average search queries per user session | 1.5 |
| Search-to-click rate | % of searches resulting in a profile/post click | > 40% |

### 8.2 Quality Metrics

| Metric | Measurement | Target |
|--------|-------------|--------|
| Zero-result rate | % of searches returning 0 results | < 20% |
| Results relevance | User satisfaction with top results (future survey) | > 80% positive |
| Repeat search rate | % of users who immediately re-search (indicates poor results) | < 15% |

### 8.3 Technical Metrics

| Metric | Measurement | Target |
|--------|-------------|--------|
| Search latency (p95) | Time from Enter to results rendered | < 500ms |
| API response time (p95) | Backend search query execution | < 200ms |
| Error rate | % of search requests that fail | < 1% |
| Index freshness | Delay between content creation and searchability | < 5 seconds |

---

## 9. Dependencies

### 9.1 Upstream Dependencies

**Identity Context:**
- User profiles (display_name, username, bio, avatar_url, location)
- User authentication (JWT tokens)

**Community Context:**
- Community membership verification
- Post data (title, body, author, category, timestamps)
- Member data (role, join date, active status)

**Infrastructure:**
- PostgreSQL with Full-Text Search support
- Existing header component (to embed search bar)

### 9.2 Downstream Consumers

**Search Analytics (Phase 3):**
- Popular queries tracking
- Zero-result query logging for content gap analysis

**Contextual Search (Phase 2):**
- Classroom context will consume the same search infrastructure pattern
- Each module tab may offer in-context search

---

## 10. Open Questions

None — all decisions resolved during discovery.

---

## 11. Appendix

### 11.1 Related Documents

- `docs/prd_summary/PRD/OVERVIEW_PRD.md` — Master PRD, Section 3.11 (Search)
- `docs/domain/GLOSSARY.md` — Ubiquitous language
- `docs/architecture/CONTEXT_MAP.md` — Bounded context relationships
- `tests/features/search/search.feature` — BDD specifications
- `docs/features/search/screenshots/` — Skool.com reference screenshots

### 11.2 Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-13 | Product Team | Initial draft for MVP |

---

## 12. Approval

**Product Owner:** _________________
**Engineering Lead:** _________________
**Design Lead:** _________________

**Status:** Draft — Pending Review
