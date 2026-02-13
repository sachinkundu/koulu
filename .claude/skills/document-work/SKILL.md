---
name: document-work
description: Document completed work, create summary, update PRDs, and commit changes
user_invocable: true
model: sonnet
---

# Document Work

## Purpose

Document completed implementation work: create a summary, update PRDs, update OVERVIEW_PRD.md, and commit changes.

---

## Usage

`/document-work <context>/<feature-name>`

Example: `/document-work identity/registration-authentication`

**Parse the argument:**
- Split on `/` to get `<context>` and `<feature-name>`
- If no `/` found, ask user to provide format: `context/feature-name`

---

## Verification (BLOCKING — Must Pass Before Documenting)

A feature is NOT complete until ALL checks pass with ZERO failures, ZERO warnings, AND coverage >=80%.

### Blocking Checklist

Run these commands and verify exact outputs:

1. Infrastructure: `docker-compose up -d` — all services healthy
2. All tests: `./scripts/test.sh --all --ignore=tests/features/identity/`
   - Required: `X passed, Y skipped` with 0 failed, 0 warnings, coverage >=80%
   - Test database is created automatically and isolated per agent
3. Alternative (run separately, both must pass):
   - `./scripts/test.sh --integration --ignore=tests/features/identity/`
   - `./scripts/test.sh --unit`
4. Frontend (if applicable): `./scripts/verify-frontend.sh`
5. Deployability (user-facing features): `./scripts/check-deployability.sh {feature-name}` — must show backend controllers + frontend components

If ANY check fails, work is NOT complete.

### Red Flags (Feature NOT Complete)
- Tests contain `pass` stubs instead of real assertions
- `@then` steps without assertions
- Comments say "mocked" but no actual mock/verification
- Coverage below 80%
- "Tests require infrastructure" used as excuse to skip
- Verification scripts not run
- Any test failure or warning

### Warning Policy
Fix warnings at the source. If suppression is unavoidable: use targeted filter, add comment explaining why, get explicit user approval. Never silently suppress.

### Evidence Required
Completion documentation MUST include exact output showing `0 failed` in test results and coverage >=80%.

### Self-Correction Protocol
If you marked work complete while tests were failing:
1. Acknowledge immediately, no excuses
2. Assess: was code committed? what's failing? is CI broken?
3. Fix (if quick) or revert to last green state
4. Document in MEMORY.md with root cause analysis
5. Verify green before proceeding

### Pre-Documentation Checks

Also verify before documenting:

1. No stub test steps — `grep -n "^    pass$" tests/features/{context}/test_*.py` should return nothing
2. Side effects work — email sending (check MailHog), events (check logs), external integrations
3. Integration wiring complete — domain event handlers registered and called

---

## Documentation Workflow

### Step 1: Write Feature Summary

Save to: `docs/summaries/{feature-name}-summary.md`
(For multi-phase features: `docs/summaries/{context}/{feature-name}-phase{X}-summary.md`)

Read all relevant files before writing (PRD, BDD spec, implementation files).

**Template:**

```markdown
# {Feature Name} - Implementation Summary

**Date:** YYYY-MM-DD
**Status:** Complete | Phase X of Y
**PRD:** `docs/features/{context}/{feature-name}-prd.md`
**BDD Spec:** `tests/features/{context}/{feature-name}.feature`

---

## What Was Built

[2-3 sentence overview of what this feature/phase delivered]

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
- [ ] Scenario: [name] (deferred to phase Y)

---

## How to Verify

1. [Step to test manually]
2. [Another verification step]

Or run: `pytest tests/features/{context}/`

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

In `docs/prd_summary/PRD/OVERVIEW_PRD.md`, find Appendix A and mark the feature as implemented:
- Change status to `Complete`

### Step 4: Commit all changes

Use a clear commit message:
```
feat({context}): implement {feature-name}

- Implements [brief description from summary]
- See docs/summaries/{feature-name}-summary.md for details

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```

### Step 5: Notify user

Report that the feature branch is ready for review.
- Do NOT merge to main
- Do NOT push to remote unless asked

---

## Multi-Phase Variant

For features split across multiple implementation phases, adapt the workflow:

1. **Summary file:** `docs/summaries/{context}/{feature-name}-phase{X}-summary.md`
2. **Include phase-specific info:** Which BDD scenarios now pass vs total, blockers for next phase
3. **Update implementation plan:** Mark completed steps, add discovered tasks
4. **Commit message:**
   ```
   feat({context}): {feature-name} phase {X} - [brief description]

   Phase X of Y complete.
   - [What this phase accomplished]
   - See docs/summaries/{context}/{feature-name}-phase{X}-summary.md
   ```
5. **Do NOT start next phase** — wait for user go-ahead

---

## After Documentation

Verify:
1. Summary was created in `docs/summaries/`
2. OVERVIEW_PRD.md was updated
3. Changes were committed
4. You're still on the feature branch (not main)
5. STOP — notify user the branch is ready for review
