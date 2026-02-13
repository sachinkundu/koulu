---
name: merge-to-main
description: Use when feature work is complete and the user wants to merge the current branch into main, push, and clean up
user_invocable: true
model: haiku
---

# Merge to Main

Merge current feature branch into main, push to origin, and delete the merged branch.

## Usage

```
/merge-to-main
```

## Steps

### 1. Pre-flight Checks

Run these in parallel:

```bash
git branch --show-current
git status
git log --oneline -5
```

**Abort if:**
- Already on `main` or `master` — nothing to merge.
- Working tree is dirty — tell user to commit or stash first.

Save the current branch name as `<feature-branch>`.

### 2. Update Main

```bash
git checkout main
git pull origin main
```

If pull fails (e.g. diverged), stop and ask the user.

### 3. Merge Feature Branch

```bash
git merge <feature-branch>
```

- If conflicts occur, stop and help the user resolve them.
- Do NOT use `--no-ff` unless the user requests it.

### 4. Push Main

```bash
git push origin main
```

### 5. Clean Up

```bash
git branch -d <feature-branch>
git push origin --delete <feature-branch>
```

If remote branch doesn't exist (never pushed), skip the remote delete silently.

### 6. Confirm

Run `git log --oneline -5` and `git branch` to show the merge landed and the branch is gone.

## Rules

- NEVER run on main/master — there must be a feature branch to merge
- NEVER force-push (`--force`)
- NEVER delete main or master
- Use `git branch -d` (safe delete), NOT `-D`
- If any step fails, stop and report — do not continue blindly
- Always pull latest main before merging to avoid push rejection
