# Leaderboards E2E Tests

## Critical Paths (P0) - MUST IMPLEMENT

- [ ] Member views leaderboard page with three ranking panels (7-day, 30-day, all-time)
- [ ] Member with points appears in leaderboard rankings
- [ ] Member sees own profile card with level info at top of page
- [ ] Member sees "Your rank" section when outside top 10
- [ ] Sidebar widget shows top-5 on community feed page
- [ ] "See all leaderboards" link navigates from sidebar to full page

## Secondary Paths (P1) - SHOULD IMPLEMENT

- [ ] Rank medals (gold/silver/bronze) display for top 3 positions
- [ ] Points display with + prefix for 7-day and 30-day panels
- [ ] Level definitions grid displays alongside profile card

## Optional Paths (P2) - NICE TO HAVE

- [ ] Loading skeleton renders while data loads
- [ ] Empty state shows when no rankings exist
- [ ] Page updates after member earns new points

## Out of Scope (Covered by BDD)

- Permission checks (non-member 403, unauthenticated 401)
- Negative net points displayed as 0
- Alphabetical tie-breaking
- Rolling window exclusion logic
- Last-updated timestamp format
