# E2E Test Plan

## Existing Coverage (18 tests)

### Identity (7 tests)
- [x] Full registration flow (register → verify email → profile → homepage)
- [x] Login with valid credentials
- [x] Login with invalid credentials shows error
- [x] View own profile with edit button
- [x] View other user's profile without edit button
- [x] Edit profile fields and verify persistence
- [x] Profile edit validation (empty display name)

### Community (9 tests)
- [x] Create post and see it in feed
- [x] View post detail in modal
- [x] View post detail via direct URL
- [x] Filter feed by category
- [x] Delete own post
- [x] Like and unlike a post
- [x] Add a comment to a post
- [x] Edit own post via modal

### Classroom (3 tests)
- [x] Create course and see it in list
- [x] View course with modules and lessons
- [x] Delete own course

---

## New Tests

### Critical Paths (P0) - MUST IMPLEMENT

- [ ] **Member replies to a comment** — Threading is a core community feature; reply form is fully implemented with `data-testid` attributes
- [ ] **Member edits their own comment** — Edit button, form, and save are all wired up in CommentCard
- [ ] **Member deletes their own comment** — Delete with confirmation dialog exists in CommentCard
- [ ] **User logs out and is redirected** — Logout button exists in UserDropdown, untested

### Secondary Paths (P1) - SHOULD IMPLEMENT

- [ ] **Member likes a comment** — Comment like button exists with count display
- [ ] **Two users interact on a post** — One user comments, another user replies (multi-user scenario)

### Out of Scope (Covered by BDD)
- Post validation (title length, content required) — BDD scenarios
- Permission checks (non-author cannot edit/delete) — BDD scenarios
- Rate limiting behavior — BDD scenarios
- Post locking prevents comments — BDD scenarios
- Comment threading max depth — BDD scenarios
- Error messages and edge cases — BDD scenarios
