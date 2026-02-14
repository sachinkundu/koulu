# Search — Alignment Verification

**PRD:** `docs/features/search/search-prd.md`
**BDD:** `tests/features/search/search.feature`
**TDD:** `docs/features/search/search-tdd.md`
**UI_SPEC:** `docs/features/search/UI_SPEC.md`

---

## PRD → BDD Coverage

Every user story must have at least one BDD scenario.

| PRD User Story | BDD Scenario(s) | Covered? |
|----------------|------------------|----------|
| **US-S1** Type query in search bar | "Search for a member by display name" (and all search scenarios) | Yes |
| **US-S2** Press Enter to execute | Implied by all "When the member searches for..." steps | Yes |
| **US-S3** Clear search input | Frontend-only behavior (not BDD-tested) | N/A (UI) |
| **US-S4** Query persists in URL | Frontend-only behavior (not BDD-tested) | N/A (UI) |
| **US-SM1** See matching members | "Search for a member by display name" | Yes |
| **US-SM2** Member card shows fields | "Member result card shows expected fields" | Yes |
| **US-SM3** Members sorted alphabetically | "Member results are sorted alphabetically" | Yes |
| **US-SM4** Click member to view profile | Frontend-only behavior | N/A (UI) |
| **US-SP1** See matching posts | "Search for a post by title" | Yes |
| **US-SP2** Post card shows fields | "Post result card shows expected fields" | Yes |
| **US-SP3** Posts sorted newest first | "Post results are sorted by newest first" | Yes |
| **US-SP4** Click post to view detail | Frontend-only behavior | N/A (UI) |
| **US-ST1** Tabs separate types | "Switch between member and post tabs" | Yes |
| **US-ST2** Tab counts shown | "Search returns counts for both tabs" | Yes |
| **US-ST3** Switch tabs without re-search | Frontend-only (both counts always returned) | N/A (UI) |
| **US-ST4** Paginated results | "Search results are paginated", "Navigate to next page" | Yes |

**Coverage: 12/12 API-testable stories covered. 4 frontend-only stories excluded from BDD.**

---

## PRD Business Rules → BDD Coverage

| Business Rule | BDD Scenario(s) | Covered? |
|---------------|------------------|----------|
| **3.1** Min 3 chars | "Search with query shorter than 3 characters" | Yes |
| **3.1** Max 200 chars | "Search with query exceeding maximum length" | Yes |
| **3.1** Whitespace trimming | "Search with only whitespace" | Yes |
| **3.1** Empty query | "Search with empty query" | Yes |
| **3.2** Members: name search | "Search for a member by display name" | Yes |
| **3.2** Members: username search | "Search for a member by username" | Yes |
| **3.2** Members: bio search | "Search for a member by bio content" | Yes |
| **3.2** Stemming support | "Search uses stemming for member bio" | Yes |
| **3.3** Posts: title search | "Search for a post by title" | Yes |
| **3.3** Posts: body search | "Search for a post by body content" | Yes |
| **3.3** Posts: stemming | "Search uses stemming for post content" | Yes |
| **3.3** Deleted posts excluded | "Deleted posts do not appear in search results" | Yes |
| **3.4** Members alphabetical | "Member results are sorted alphabetically" | Yes |
| **3.4** Posts newest first | "Post results are sorted by newest first" | Yes |
| **3.5** Auth required | "Unauthenticated user cannot search" | Yes |
| **3.5** Membership required | "Non-member cannot search a community" | Yes |
| **3.5** Inactive excluded | "Inactive members do not appear in search results" | Yes |
| **3.6** Rate limiting | "Search respects rate limiting" | Yes |

**Coverage: 18/18 business rules covered.**

---

## PRD Edge Cases → BDD Coverage

| Edge Case | BDD Scenario(s) | Covered? |
|-----------|------------------|----------|
| **5.1** Special characters / XSS | "Search with special characters" | Yes |
| **5.1** SQL injection | "Search input is sanitized against SQL injection" | Yes |
| **5.2** Long query | "Search with query exceeding maximum length" | Yes |
| **5.3** Non-member access | "Non-member cannot search a community" | Yes |
| **5.5** No profile data | "Member with no bio is still found by name" | Yes |
| **5.7** Rapid re-searching | Frontend concern (request cancellation) | N/A (UI) |

**Coverage: 5/5 API-testable edge cases covered. 1 frontend-only excluded.**

---

## PRD Security → BDD Coverage

| Security Requirement | BDD Scenario(s) | Covered? |
|----------------------|------------------|----------|
| **6.1** JWT required | "Unauthenticated user cannot search" | Yes |
| **6.2** Membership required | "Non-member cannot search a community" | Yes |
| **6.3** Input validation (XSS) | "Search with special characters" | Yes |
| **6.3** Input validation (SQLi) | "Search input is sanitized against SQL injection" | Yes |
| **6.3** Min/max query length | "Search with query shorter than 3 characters", "Search with query exceeding maximum length" | Yes |
| **6.4** Rate limiting | "Search respects rate limiting" | Yes |

**Coverage: 6/6 security requirements covered.**

---

## TDD → PRD Alignment

| TDD Section | PRD Requirement | Aligned? |
|-------------|----------------|----------|
| **2. Architecture** | Community context placement | Yes (PRD Section 9.1) |
| **3. Technology** | PostgreSQL FTS | Yes (OVERVIEW_PRD line 716) |
| **4. Data Model** | Member + Post fields | Yes (PRD Sections 3.2, 3.3) |
| **5. API Design** | Single endpoint, tab counts | Yes (PRD Section 4.2) |
| **6. Domain Model** | No new entities (read-only) | Yes (PRD has no domain events) |
| **9. Security** | Auth, membership, sanitization | Yes (PRD Section 6) |
| **10. Performance** | < 200ms p95, < 500ms e2e | Yes (PRD Section 8.3) |
| **11. Error Handling** | All error codes mapped | Yes (PRD Section 4.6) |

**No gaps detected.**

---

## TDD → UI_SPEC Alignment

| TDD File Checklist | UI_SPEC Component | Match? |
|--------------------|-------------------|--------|
| `SearchBar.tsx` | Section: Header Search Bar | Yes |
| `SearchResults.tsx` | Section: Search Results Page (layout) | Yes |
| `SearchResultTabs.tsx` | Section: Search Results Tab Navigation | Yes |
| `MemberSearchCard.tsx` | Section: Member Result Card | Yes |
| `PostSearchCard.tsx` | Section: Post Result Card | Yes |
| `SearchPagination.tsx` | Section: Pagination Controls | Yes |
| `SearchEmptyState.tsx` | Section: Empty States | Yes |
| `SearchSkeleton.tsx` | Section: Loading States | Yes |

**All 8 frontend components match between TDD and UI_SPEC.**

---

## Gap Analysis

| Area | Gap | Severity | Resolution |
|------|-----|----------|------------|
| Username search | PRD says search by username, but FTS doesn't stem usernames well | Low | TDD addresses this: supplementary ILIKE for username matching alongside FTS |
| Frontend-only behaviors | 5 user stories are purely frontend (clear input, click card, URL persistence) | None | These are tested via E2E tests, not BDD |
| Cross-context coupling | Search JOINs profiles (Identity) from Community context | Low | Documented in TDD Section 15 as technical debt, acceptable for monolith |

---

## Approval Checklist

- [x] Every PRD user story has BDD coverage (or is explicitly frontend-only)
- [x] Every business rule has BDD coverage
- [x] Every edge case has BDD coverage (or is explicitly frontend-only)
- [x] Every security requirement has BDD coverage
- [x] TDD architecture matches PRD requirements
- [x] TDD component names match UI_SPEC
- [x] No contradictions between PRD, BDD, TDD, and UI_SPEC
- [x] Gaps identified and documented with resolutions
- [ ] Product Owner approval
- [ ] Engineering Lead approval

---

**Status:** Ready for Review
