---
name: mvp-status
description: Show MVP feature implementation status and identify the next candidate to work on
user_invocable: true
model: haiku
---

# MVP Status

Show a summary of MVP feature implementation status by reading the PRD and display what to work on next.

## Steps

### Step 1: Read the PRD

Read `docs/prd_summary/PRD/OVERVIEW_PRD.md`, specifically:
- **Section 6 (Feature Prioritization)** — the MVP checklist with status markers
- **Appendix A (Feature Breakdown Index)** — the detailed feature table with status

### Step 2: Build the summary table

Output a table with these columns:

| Feature | Phase | Status | Notes |
|---------|-------|--------|-------|

Status values:
- ✅ **Done** — backend + frontend + tests complete
- ⚠️ **Partial** — some layers missing (specify which in Notes)
- ❌ **Not started** — no implementation exists

Group features by MVP phase (Phase 1 = MVP, Phase 2, Phase 3).

### Step 3: Show MVP completion percentage

Count features in Phase 1 (MVP) and calculate:
- Total MVP features
- Done count
- Partial count
- Not started count
- Completion percentage (Done / Total, partial counts as 0.5)

### Step 4: Identify next candidate

Determine the next feature to work on using this priority order:

1. **Partial features first** — finishing something 80% done is higher value than starting fresh
2. **MVP (Phase 1) features before Phase 2/3** — MVP must be complete first
3. **Features with fewer dependencies** — prefer features that don't require other features to exist

Output a clear recommendation:

```
## Next Up
**[Feature Name]** — [1-sentence reason why this is next]

What's needed:
- [bullet list of remaining work]
```

### Step 5: Show the full roadmap order

List the recommended order for all remaining unfinished MVP features, numbered.

## Rules

- ONLY read the PRD file — do not explore the codebase
- Do NOT modify any files — this is a read-only status report
- Keep output concise and scannable
- If the PRD status markers are missing or stale, warn the user to run an update
