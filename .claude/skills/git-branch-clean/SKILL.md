---
name: git-branch-clean
description: Use when the user wants to delete local branches already merged into main
user_invocable: true
model: haiku
---

# Git Branch Clean

Delete all local branches that have already been merged into main.

## Steps

1. **Fetch latest and list merged branches:**
   ```bash
   git fetch --prune && git branch --merged main
   ```

2. **Delete merged branches (excluding main, master, and current branch):**
   ```bash
   git branch --merged main | grep -vE '^\*|^\s*(main|master)$' | xargs -r git branch -d
   ```

3. Report what was deleted. If no branches were deleted, say no cleanup was needed.

## Rules

- NEVER delete `main` or `master`
- NEVER delete the currently checked-out branch
- Use `git branch -d` (safe delete), NOT `-D` (force delete)
- Run `git fetch --prune` first to ensure accurate merge status
