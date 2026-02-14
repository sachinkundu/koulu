# Search E2E Tests

## Critical Paths (P0) - MUST IMPLEMENT

- [ ] User searches for member by name and sees results
- [ ] User searches for post by title and sees results
- [ ] User switches between Members and Posts tabs with correct counts
- [ ] User clicks member card and navigates to profile

## Secondary Paths (P1) - SHOULD IMPLEMENT

- [ ] User clicks post card and navigates to post detail
- [ ] Search with no results shows empty state
- [ ] Short query (< 3 chars) shows guidance message

## Optional Paths (P2) - NICE TO HAVE

- [ ] Search bar clear button resets input
- [ ] Search query persists in search bar on results page

## Out of Scope (Covered by BDD)

- Query validation (too short, empty, invalid type)
- Permission checks (unauthenticated, non-member)
- SQL injection and security edge cases
- Pagination (Phase 2)
- Stemming behavior (Phase 2)
- Deleted posts / inactive members filtering (Phase 3)
- Rate limiting (Phase 3)
