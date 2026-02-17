# Gamification Points & Levels E2E Tests

## Critical Paths (P0) - MUST IMPLEMENT

- [x] Member views level definitions grid on leaderboards page
- [x] Member views own level and points on profile page
- [x] Member earns points from actions and sees level progress update
- [x] Locked course shows lock overlay on classroom page

## Secondary Paths (P1) - SHOULD IMPLEMENT

- [x] Member's current level is highlighted in leaderboard grid
- [x] Member unlocks course after reaching required level

## Out of Scope (Covered by BDD)

- Point award validation (exact amounts per action type)
- Level ratchet behavior (levels never decrease)
- Admin level config CRUD (name/threshold updates)
- Admin course level requirement management
- Authentication/authorization checks (401/403)
- Input validation (level name length, threshold ordering)
- XSS sanitization
- Points cannot go negative
- No duplicate lesson completion points
