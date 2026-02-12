---
name: bug-report
description: Log a bug or missing feature found during manual testing
user_invocable: true
model: haiku
---

# Bug Report

Log a bug, missing feature, or UX issue discovered during manual use of the application.

## Usage

```
/bug-report the post editor doesn't clear after submitting
/bug-report clicking the back button on course detail loses scroll position
/bug-report there's no way to delete a comment
```

The argument is the user's plain-language description of what they noticed.

## Steps

### Step 1: Read current tracker

Read `docs/bugs/BUGS.md` to determine the next available ID (BUG-NNN).

### Step 2: Categorize

From the user's description, determine:

- **Type**: one of `bug`, `missing-feature`, or `ux-issue`
  - `bug` — something is broken or behaves incorrectly
  - `missing-feature` — expected functionality that doesn't exist yet
  - `ux-issue` — it works but the experience is poor (confusing, slow, ugly)
- **Area**: the bounded context or module affected (e.g., `community`, `classroom`, `identity`, `infrastructure`)
- **Title**: a short (< 80 char) summary in imperative form

If the description is ambiguous about the type or area, make your best guess — the user can correct it later.

### Step 3: Append entry

Add a new entry to the `## Open` section of `docs/bugs/BUGS.md` using this exact format:

```markdown
### BUG-NNN: Short imperative title
- **Reported:** YYYY-MM-DD
- **Type:** bug | missing-feature | ux-issue
- **Area:** context/module
- **Description:** The user's description, lightly cleaned up for clarity. Keep their intent intact.
```

Add steps to reproduce only if the user provided them or they're obvious from the description.

### Step 4: Confirm

Tell the user:
- The ID assigned (e.g., BUG-003)
- The type and area you picked
- That they can say "fix BUG-003" or "go through the bug list" anytime to address it

## Rules

- NEVER fix the bug during this skill — only log it
- NEVER remove or modify existing entries
- NEVER reuse an ID that already exists
- Keep descriptions concise but preserve the user's original intent
- Use today's date for the Reported field
