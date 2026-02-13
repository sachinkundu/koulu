---
name: update-mvp-status
description: Read implementation summaries and update OVERVIEW_PRD.md with accurate feature statuses
user_invocable: true
---

# Update MVP Status

Sync the OVERVIEW_PRD.md status markers with the actual implementation state by reading the summaries directory.

## Steps

### Step 1: Read implementation summaries

List all files in `docs/summaries/` recursively and read the header of each summary file (first ~15 lines) to extract:
- **Feature area** (identity, community, classroom, etc.)
- **Phase status** (e.g., "Phase 3 of 4 Complete", "Feature Complete")
- **Date** of completion
- **What was built** (first paragraph)

Build a lookup of feature → implementation status from the summaries.

### Step 2: Read current PRD state

Read `docs/prd_summary/PRD/OVERVIEW_PRD.md` and extract:
- **Section 6 (Feature Prioritization)** — the MVP/Phase 2/Phase 3 checklists
- **Appendix A (Feature Breakdown Index)** — the detailed feature table

### Step 3: Cross-reference and determine accurate status

For each feature in the PRD, determine its true status:

**Status rules:**
- ✅ **Complete** — has a summary file showing all phases done AND frontend exists AND tests pass
- ⚠️ **Partial** — has a summary but missing layers (e.g., backend done, no frontend). Note what's missing.
- ❌ **Not started** — no summary file exists for this feature

**Key checks:**
- A feature with backend summaries but no frontend vertical slice is ⚠️ Partial, not ✅ Complete
- A feature with "Phase X of Y Complete" where X < Y is ⚠️ Partial
- The `vertical-slice-completion-summary.md` indicates which features have full UI + E2E coverage

### Step 4: Update Section 6 (Feature Prioritization)

Edit the MVP/Phase 2/Phase 3 checklists in Section 6 to reflect accurate statuses.

Format each line as:
- `- ✅ Feature name` (done)
- `- ⚠️ Feature name (details of what's partial)` (partial)
- `- ❌ Feature name` (not started)

### Step 5: Update Appendix A (Feature Breakdown Index)

Edit the Status column of the feature table in Appendix A.

Use these status formats:
- `✅ Complete` or `✅ Complete (N/N scenarios)` for fully done features
- `✅ Complete (included in Feed Phase X)` for sub-features bundled into a parent
- `⚠️ Partial — backend Phase X/Y complete, frontend missing` for partial work
- `❌ Not started` for features with no implementation

### Step 6: Report changes

Output a brief summary of what was updated:

```
## Status Updates Applied

| Feature | Old Status | New Status | Reason |
|---------|-----------|------------|--------|
```

Only show rows where the status actually changed. If nothing changed, say "PRD is already up to date."

## Rules

- ONLY modify `docs/prd_summary/PRD/OVERVIEW_PRD.md` — no other files
- ONLY modify Section 6 and Appendix A — do not touch other sections
- Preserve all existing PRD content, formatting, and structure
- Use the Edit tool for targeted replacements — do not rewrite the entire file
- If a summary file is ambiguous about completion status, mark as ⚠️ Partial and note the ambiguity
- If no summaries exist at all, warn the user that status data is unavailable
