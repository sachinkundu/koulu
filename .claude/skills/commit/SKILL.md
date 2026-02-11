---
name: commit
description: Stage and commit changes with a well-crafted commit message
user_invocable: true
model: haiku
---

# Commit

Create a git commit for the current changes.

## Usage

```
/commit                          # auto-detect or ask for branch
/commit feature/my-branch        # use this branch (create if needed)
/commit chore/cleanup            # use this branch (create if needed)
```

If an argument is provided, treat it as the target branch name. Skip the branch inference/question logic entirely.

## Steps

### Step 0: Branch Check

1. Run `git branch --show-current` to get the current branch name.
2. **If the user provided a branch name as an argument:**
   - If already on that branch, proceed directly.
   - If on a different branch, run `git checkout -b <branch>` (or `git checkout <branch>` if it already exists) to switch.
3. **If no argument provided and on `main` or `master`:**
   - Run `git status` and `git diff --stat` to see what changed.
   - Look at the changed files to infer a reasonable branch name:
     - Files in `src/community/` or `tests/features/community/` → suggest `feature/community-...`
     - Files in `src/classroom/` or `tests/features/classroom/` → suggest `feature/classroom-...`
     - Files in `tests/e2e/` → suggest `feature/e2e-tests`
     - Files in `docs/` only → suggest `docs/...`
     - Files in `scripts/` or config files → suggest `chore/...`
     - Mixed or unclear → cannot infer
   - **Ask the user** what branch to commit into. Suggest the inferred name if possible. Offer options like:
     - The inferred branch name (if one could be determined)
     - "Commit directly to main" (if the user really wants to)
   - If the user picks a new branch, create it with `git checkout -b <branch>` before proceeding.
4. **If no argument provided and already on a feature/fix/docs/chore branch:** proceed directly — no need to ask.

### Step 1: Review Changes

Run `git status` (never use `-uall`), `git diff` (staged + unstaged), and `git log --oneline -5` in parallel.

Review all changes. Do NOT commit files that look like secrets (`.env`, credentials, tokens).

### Step 2: Draft Commit Message

- First line: `type(scope): short summary` (max 72 chars)
- Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `style`
- Scope: module or area affected (e.g., `community`, `classroom`, `e2e`, `scripts`)
- Body (if needed): blank line then explanation of *why*, not *what*

### Step 3: Stage and Commit

Stage the relevant files by name (`git add <files>`). Prefer specific files over `git add .`.

Commit using a HEREDOC:
```bash
git commit -m "$(cat <<'EOF'
type(scope): summary

Optional body.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
EOF
)"
```

### Step 4: Verify

Run `git status` after to confirm clean state.

## Rules

- NEVER amend a previous commit unless the user explicitly says "amend"
- NEVER push unless the user explicitly asks
- NEVER use `--no-verify`
- If a pre-commit hook fails, fix the issue and create a NEW commit
- If there are no changes, say so and do nothing
