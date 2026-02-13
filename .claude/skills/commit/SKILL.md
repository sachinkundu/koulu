---
name: commit
description: Stage and commit changes, ensuring work never lands directly on main
user_invocable: true
model: haiku
---

# Commit

Create a git commit. **NEVER commits to main/master** — always ensures a feature branch.

## Usage

```
/commit                          # auto-detect branch or ask
/commit feature/my-branch        # use this branch (create if needed)
```

## Steps

### 1. Branch Guard

Run `git branch --show-current`.

**If argument provided:** switch to that branch (`git checkout -b <branch>` or `git checkout <branch>` if it exists).

**If on `main` or `master` (no argument):**
- Run `git status` and `git diff --stat` to see changed files.
- Infer a branch name from file paths:
  - `src/community/` or `tests/features/community/` → `feature/community-...`
  - `src/classroom/` or `tests/features/classroom/` → `feature/classroom-...`
  - `src/identity/` or `tests/features/identity/` → `feature/identity-...`
  - `tests/e2e/` → `feature/e2e-tests`
  - `docs/` only → `docs/...`
  - `scripts/` or config files → `chore/...`
  - Mixed or unclear → ask user
- **Ask the user** to confirm or provide a branch name. Never offer "commit to main" as an option.
- Create the branch with `git checkout -b <branch>` before proceeding.

**If already on a feature/fix/docs/chore branch:** proceed directly.

### 2. Review and Commit

1. Run `git status` (never `-uall`), `git diff` (staged + unstaged), and `git log --oneline -5` in parallel.
2. Do NOT commit files that look like secrets (`.env`, credentials, tokens).
3. Draft commit message: `type(scope): summary` (max 72 chars). Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `style`.
4. Stage specific files by name (`git add <files>`), not `git add .`.
5. Commit using HEREDOC:
```bash
git commit -m "$(cat <<'EOF'
type(scope): summary

Optional body explaining why, not what.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
EOF
)"
```
6. Run `git status` to confirm clean state.

## Rules

- NEVER commit to main or master — always create a feature branch first
- NEVER amend unless the user explicitly says "amend"
- NEVER push unless the user explicitly asks
- NEVER use `--no-verify`
- If a pre-commit hook fails, fix the issue and create a NEW commit
- If there are no changes, say so and do nothing
