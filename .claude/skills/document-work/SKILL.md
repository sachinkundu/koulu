---
name: document-work
description: Document completed work, create summary, update PRDs, and commit changes
model: sonnet
---

# Usage
`/document-work <context>/<feature-name>`

Example: `/document-work identity/registration-authentication`

---

When invoked, execute the documentation workflow from `prompts/document-work.md` with these substitutions:

**Parse the argument:**
- Split on `/` to get `<context>` and `<feature-name>`
- If no `/` found, ask user to provide format: `context/feature-name`

**Substitutions:**
- `[feature-name]` → Feature slug (e.g., "registration-authentication")
- `[context]` → Context directory name (e.g., "identity")
- `[Feature Name]` → Title-cased version (e.g., "Registration Authentication")

**Expected file paths after substitution:**
- Summary: `docs/summaries/{feature-name}-summary.md`
- PRD: `docs/features/{context}/{feature-name}-prd.md`
- BDD: `tests/features/{context}/{feature-name}.feature`

---

## Instructions

1. Parse the provided argument to extract context and feature name
2. Execute the following documentation workflow:

### Step 1: Write a feature summary document

Save to: `docs/summaries/{feature-name}-summary.md`

Include:
- What was built (reference the PRD at `docs/features/{context}/{feature-name}-prd.md`)
- Key implementation decisions and why
- Files created or modified (grouped by layer: domain, application, infrastructure, frontend)
- BDD scenarios that now pass (from `tests/features/{context}/{feature-name}.feature`)
- How to verify it works (manual steps if needed)
- Any issues encountered and how they were resolved
- Known limitations or deferred items

Use this template structure:
```markdown
# {Feature Name} - Implementation Summary

**Date:** YYYY-MM-DD
**Status:** Complete
**PRD:** `docs/features/{context}/{feature-name}-prd.md`
**BDD Spec:** `tests/features/{context}/{feature-name}.feature`

---

## What Was Built

[2-3 sentence overview of what this feature delivered]

---

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| [Choice made] | [Why this approach] |

---

## Files Changed

### Domain Layer
- `src/{context}/domain/...` — [what/why]

### Application Layer
- `src/{context}/application/...` — [what/why]

### Infrastructure Layer
- `src/{context}/infrastructure/...` — [what/why]

### Frontend
- `frontend/src/features/{context}/...` — [what/why]

### Tests
- `tests/features/{context}/{feature-name}.feature` — [X scenarios]
- `tests/unit/{context}/...` — [X tests]

---

## BDD Scenarios Passing

- [x] Scenario: [name]
- [x] Scenario: [name]

---

## How to Verify

1. [Step to test manually]
2. [Another verification step]

Or run: `pytest tests/features/{context}/{feature-name}.feature`

---

## Issues & Resolutions

| Issue | Resolution |
|-------|------------|
| [Problem encountered] | [How it was solved] |

---

## Deferred / Out of Scope

- [Item explicitly not included and why]

---

## Next Steps

- [ ] [Any follow-up tasks]
```

### Step 2: Update the PRD (if exists)

Check if `docs/features/{context}/{feature-name}-prd.md` exists. If so:
- Add `**Implementation Status:** Complete` at the top (after the title)
- Note any deviations from the original spec with rationale

### Step 3: Update OVERVIEW_PRD.md

In `docs/OVERVIEW_PRD.md`, find Appendix A and mark the feature as implemented:
- Change `[ ] Feature Name` to `[x] Feature Name`

### Step 4: Commit all changes

Use a clear commit message:
```
feat({context}): implement {feature-name}

- Implements [brief description from summary]
- See docs/summaries/{feature-name}-summary.md for details

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```

### Step 5: Notify user

Report that the feature branch is ready for review.
- Do NOT merge to main
- Do NOT push to remote unless asked

---

## Critical Notes

- Read all relevant files before writing the summary (PRD, BDD spec, implementation files)
- Be thorough in documenting what was built
- Stay on the feature branch

---

## Pre-Documentation Verification

Before documenting as "Complete", verify:

1. **No stub test steps** — Search test files for `pass` statements in step definitions:
   ```bash
   grep -n "^    pass$" tests/features/{context}/test_*.py
   ```
   If found, these are likely untested functionality!

2. **Side effects work** — For features with:
   - Email sending → Manually trigger and check MailHog
   - Events → Check logs for event publication
   - External integrations → Verify they actually connect

3. **Integration wiring complete** — If domain events exist, verify handlers are registered and called

⚠️ A feature is NOT complete if tests pass but functionality doesn't work. Stub tests (`pass` statements) hide missing implementations.
