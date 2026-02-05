# Document Work Prompt

Use this prompt at the end of each implementation session to document what was done and commit changes.

---

## When to Use

After you've:
1. Completed implementation for a feature or phase
2. All BDD tests pass
3. Verification scripts pass (`./scripts/verify.sh` or `./scripts/verify-frontend.sh`)
4. Ready to close out the work

---

## The Prompt

```
Good work.

Now document everything you accomplished:

1. **Write a phase/feature summary document**
   - Save to: `docs/summaries/[feature-name]-summary.md`
   - Include:
     - What was built (reference the PRD)
     - Key implementation decisions and why
     - Files created or modified (grouped by layer: domain, application, infrastructure, frontend)
     - BDD scenarios that now pass
     - How to verify it works (manual steps if needed)
     - Any issues encountered and how they were resolved
     - Known limitations or deferred items

2. **Update the PRD** (if exists)
   - Add "Implementation Status: Complete" at the top
   - Note any deviations from the original spec with rationale

3. **Update OVERVIEW_PRD.md**
   - In Appendix A, mark the feature as implemented: `[x] Feature Name`

4. **Commit all changes** with a clear message:
   ```
   feat(context): implement [feature-name]
   
   - Implements [brief description]
   - Closes #[issue] (if applicable)
   - See docs/summaries/[feature-name]-summary.md for details
   ```

5. **Notify me** that the feature branch is ready for review
   - Do NOT merge to main yourself
```

---

## Extended Version (Multi-Phase Features)

For features split across multiple implementation phases:

```
Good work on Phase [X].

Now document this phase:

1. **Write a phase summary document**
   - Save to: `docs/summaries/[feature-name]/phase-[X]-summary.md`
   - Include:
     - What was built in THIS phase
     - Key decisions made
     - Files created or modified
     - Which BDD scenarios now pass (vs. total)
     - Blockers or dependencies for next phase
     - Time estimate for remaining phases

2. **Update the implementation plan**
   - Mark completed steps with [x]
   - Add any new tasks discovered during implementation
   - Note: `docs/features/[context]/[feature-name]-plan.md`

3. **Commit phase changes**
   ```
   feat(context): [feature-name] phase [X] - [brief description]
   
   Phase X of Y complete.
   - [What this phase accomplished]
   - See docs/summaries/[feature-name]/phase-[X]-summary.md
   ```

4. **Do NOT start next phase** — wait for my go-ahead
```

---

## Summary Document Template

```markdown
# [Feature Name] - Implementation Summary

**Date:** YYYY-MM-DD  
**Status:** Complete | Phase X of Y  
**PRD:** `docs/features/[context]/[feature]-prd.md`  
**BDD Spec:** `tests/features/[context]/[feature].feature`

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
- `src/[context]/domain/entities/[file].py` — [what/why]

### Application Layer
- `src/[context]/application/commands/[file].py` — [what/why]

### Infrastructure Layer
- `src/[context]/infrastructure/[file].py` — [what/why]

### Frontend
- `frontend/src/features/[context]/[file].tsx` — [what/why]

### Tests
- `tests/features/[context]/[feature].feature` — [X scenarios]
- `tests/unit/[context]/test_[file].py` — [X tests]

---

## BDD Scenarios Passing

- [x] Scenario: [name]
- [x] Scenario: [name]
- [ ] Scenario: [name] (deferred to phase Y)

---

## How to Verify

1. [Step to test manually]
2. [Another verification step]

Or run: `pytest tests/features/[context]/[feature].feature`

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

- [ ] [If multi-phase: what's next]
- [ ] [Any follow-up tasks]
```

---

## Folder Structure for Summaries

```
docs/
├── OVERVIEW_PRD.md
├── features/
│   └── community/
│       ├── posts-prd.md
│       └── posts-plan.md (if multi-phase)
└── summaries/
    ├── posts-summary.md (single-phase feature)
    └── comments/        (multi-phase feature)
        ├── phase-1-summary.md
        ├── phase-2-summary.md
        └── phase-3-summary.md
```

---

## After Documentation

1. ✅ Verify summary was created in `docs/summaries/`
2. ✅ Verify OVERVIEW_PRD.md was updated
3. ✅ Verify changes were committed
4. ✅ Verify you're still on the feature branch (not main)
5. 🛑 STOP — notify me the branch is ready for review