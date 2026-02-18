# Koulu - Claude Code Instructions

Skool.com clone: community platform with feed, classroom, calendar, members, leaderboards.

## Project Context

Python backend with FastAPI, Alembic migrations, DDD/hexagonal architecture, vertical slicing, pytest with multi-agent isolation. Frontend is React + TypeScript (strict) + TailwindCSS. Vitest for frontend tests, pytest-bdd for backend. OpenTelemetry tracing, structlog logging.

## Python Environment (Non-Negotiable)

**ALWAYS use pyenv with the `koulu` virtualenv.** NEVER use `source .venv/bin/activate` or create new virtual environments.

```bash
eval "$(pyenv init -)" && eval "$(pyenv virtualenv-init -)" && pyenv activate koulu
```

All Python commands (pytest, ruff, mypy, pip, etc.) MUST run inside this environment. Subagents must also use this activation sequence.

## Verification (Non-Negotiable)

**ALWAYS use `./scripts/verify.sh` for verification — NEVER run ad-hoc pytest/ruff/mypy/eslint commands.**

verify.sh runs **everything except E2E tests**:
- **Backend:** ruff check, ruff format --check, mypy, then `test.sh --all` with coverage and test scope
- **Frontend:** ESLint, TypeScript typecheck, Vitest tests, production build (via `verify-frontend.sh`)
- It handles test database setup, proper ignores (e.g., `tests/features/identity/`), and `--cov-fail-under=80`
- If verify.sh fails on DB connectivity: run `docker compose up -d postgres`, create test DB if needed, then re-run verify.sh
- **ALL checks must pass — backend AND frontend.** If verify.sh reveals failures from ANY layer, fix them FIRST before starting new work. Zero failures is non-negotiable.
- The ONLY exception for running individual test commands is targeted debugging after verify.sh identifies a failure
- E2E tests are run separately via `./scripts/run-e2e-tests.sh` (not part of verify.sh)

## Scope Rules (Non-Negotiable)

Build ONLY what is explicitly requested. Nothing more.

Before writing ANY code:
1. Did the user explicitly request this exact feature?
2. Am I adding anything beyond the stated requirement?
3. Is this the minimum implementation that satisfies the request?

If NO to any, STOP and ask for clarification. NEVER add "helpful" features, badges, or enhancements without permission. NEVER assume features are needed. NEVER pick an interpretation and proceed—ask first.

## General Rules

- Before building new infrastructure or systems, check if the project already has an existing solution. Read `start.sh`, `project-env.sh`, `docker-compose` files, and existing scripts first. Ask before replacing existing patterns.
- Before ANY implementation: read relevant specs in `docs/`, find existing patterns in codebase and match them exactly, read every file you plan to modify.
- Before using ANY external library: research exact API signatures. Never assume from memory.
- NEVER mark work complete with failing tests. `0 failed` required, coverage >=80%, no warnings. Fix failures or skip with `@pytest.mark.skip(reason="Phase X: condition")`.
- Test fixtures MUST use domain factory methods then persist—never create ORM models directly.
- Bug fix iterations continue on the SAME feature branch. New branch only for new features.

## Architecture: Hexagonal + DDD

Read `.claude/skills/architecture/SKILL.md` FIRST for DDD design decisions.

Reference: `docs/domain/GLOSSARY.md` | `docs/architecture/CONTEXT_MAP.md`

```
src/{context}/
├── domain/           # Pure business logic, NO external deps
│   ├── entities/
│   ├── value_objects/
│   ├── events/
│   └── repositories/ # Interfaces only
├── application/      # Use cases, orchestration
│   ├── commands/
│   └── queries/
├── infrastructure/   # Implementations
│   ├── persistence/
│   ├── api/
│   └── external/
└── interface/        # Controllers, CLI
```

- Domain layer has ZERO external imports
- No anemic models—entities contain behavior
- Aggregates protect their own consistency
- Cross-context communication via events only
- Each context owns its data—no shared database tables
- Use ubiquitous language from GLOSSARY.md

## Implementation Rules

- When implementing phased plans, only implement tasks for phases that are already complete on the backend. Do not start work on phases that haven't been built yet unless explicitly asked.
- Frontend REQUIRED for user-facing features. No UI = Not Done. **"UI" means components rendered in actual pages/routes that users can navigate to in a browser.** Isolated components not imported into any page/route are NOT "frontend done." If you can't give the user a URL to see the feature, it's not done. Exceptions (require explicit approval): background jobs, internal admin APIs, migration services.
- **Multi-backend agents:** When a phase has 8+ backend tasks, split into multiple parallel backend agents by layer (domain, infra, app) — never use a single backend agent as bottleneck. See MEMORY.md for file ownership boundaries and start conditions.
- **Read summaries first:** Before implementing Phase N+1, read `docs/summaries/{context}/{feature}-phase-N-summary.md` for a quick overview of what exists. Do NOT re-read every implementation file individually.
- **Subagents inherit environment rules:** Every subagent MUST use `pyenv activate koulu` and `./scripts/verify.sh`. Pass these instructions explicitly when dispatching agents.

## Debugging

When fixing bugs, always check for related/downstream issues before declaring done. If you fix a backend field name, check all frontend consumers. If you fix one async bug, scan for similar patterns nearby.

## DevOps / Infrastructure

After modifying any system service files (systemd, Docker, etc.), verify symlinks and restart policies are correct. Use `always` restart policy for daemons that should persist. Never delete service files without first disabling the service.

## Skills

Reference (read BEFORE implementation):
- DDD/Architecture: `.claude/skills/architecture/SKILL.md` (read first for any new context)
- BDD: `.claude/skills/bdd/SKILL.md`
- Python: `.claude/skills/python/SKILL.md`
- Frontend: `.claude/skills/frontend/SKILL.md`
- Security: `.claude/skills/security/SKILL.md`
- UI: `.claude/skills/ui-design/SKILL.md`

Feature workflow (screenshots-first — one-direction flow):
1. Gather Skool.com screenshots into `docs/features/{context}/screenshots/` (manual — before any specs)
2. `/write-feature-spec {context}/{feature}` -> PRD + BDD (analyzes screenshots to inform UI Behavior section)
3. `/generate-ui-spec` -> UI_SPEC.md (details the visual approach from PRD + screenshots — confirms, not discovers)
4. `/write-technical-design {context}/{feature}` -> TDD (references UI_SPEC for component names)
5. `/create-phase-plan {context}/{feature}` -> Phase plan + Phase 1 granular tasks
6. `/implement-feature {context}/{feature} --phase=N` -> Implementation per phase
7. `/write-e2e-tests {feature}` -> Playwright tests
8. `/document-work {context}/{feature}` -> Summary + PRD update

## Git Worktrees (Parallel Epic Development)

Multiple epics can be developed simultaneously using git worktrees. Each worktree gets fully independent infrastructure (Docker containers, databases, ports).

**Hierarchy:** Epic (worktree) → Feature branches (within worktree) → main (deploy)

### Quick Reference
```bash
# Create a worktree for an epic (creates epic/<name> branch)
./scripts/worktree-create.sh leaderboards

# Check all worktrees and their status
./scripts/worktree-status.sh

# Work in the worktree — create feature branches within it
cd ../koulu-leaderboards
git checkout -b feature/leaderboard-api    # feature branch
# ... implement, verify, commit ...
git checkout epic/leaderboards && git merge feature/leaderboard-api  # merge to epic

# When epic is complete, merge to main
git checkout main && git merge epic/leaderboards
git push origin main

# Tear down
cd ../koulu && ./scripts/worktree-teardown.sh leaderboards
```

### How It Works
- `scripts/project-env.sh` derives unique ports and container names from the directory path
- Each worktree directory (e.g., `~/code/koulu-leaderboards`) gets its own:
  - Docker containers (postgres, redis, mailhog) — named via `KOULU_VOLUME_PREFIX`
  - Docker volumes — unique per worktree
  - Host ports — deterministic offset from directory path hash
  - `.env` and `frontend/.env` — generated by `setup.sh`
  - `node_modules/` — per-worktree `npm install`
  - Test databases — named per project
- Python deps are shared via the pyenv `koulu` virtualenv (same packages, no per-worktree install needed)
- Every script header shows project name, branch, and ports so you always know which worktree you're in
- Opening a Claude Code session in a worktree directory (`cd ~/code/koulu-leaderboards && claude`) scopes that session to the epic's infrastructure

### Alembic Migration Conflicts
- Each worktree runs migrations against its own database — no runtime conflicts
- At merge time, if two epics added migrations, run `alembic merge heads -m "merge"` to resolve multiple Alembic heads
- Merge one epic at a time into main, then rebase the others

### Rules for Worktree Development
- NEVER share Docker containers or databases between worktrees
- Always run `./setup.sh` after creating a new worktree (worktree-create.sh does this automatically)
- Run `./scripts/verify.sh` within each worktree — it operates on that worktree's infra only
- Feature branches are created and merged **within** the epic worktree, then the epic branch merges to main when complete
- When done with an epic, use `worktree-teardown.sh` to clean up Docker resources

## Key Files

- `docs/OVERVIEW_PRD.md` — master feature list
- `docs/domain/GLOSSARY.md` — ubiquitous language
- `docs/architecture/CONTEXT_MAP.md` — bounded contexts
