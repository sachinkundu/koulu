# Koulu - Claude Code Instructions

Skool.com clone: community platform with feed, classroom, calendar, members, leaderboards.

## Project Context

Python backend with FastAPI, Alembic migrations, DDD/hexagonal architecture, vertical slicing, pytest with multi-agent isolation. Frontend is React + TypeScript (strict) + TailwindCSS. Vitest for frontend tests, pytest-bdd for backend. OpenTelemetry tracing, structlog logging.

Always run `./scripts/verify.sh` after changes, not ad-hoc pytest commands. Verify runs: ruff check, ruff format, mypy, then `test.sh --all`.

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
- Frontend REQUIRED for user-facing features. No UI = Not Done. Exceptions (require explicit approval): background jobs, internal admin APIs, migration services.

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

Feature workflow:
1. `/write-feature-spec {context}/{feature}` -> PRD + BDD feature file
2. `/generate-ui-spec` -> UI_SPEC.md
3. `/write-technical-design {context}/{feature}` -> TDD
4. `/implement-feature {context}/{feature}` -> Implementation
5. `/write-e2e-tests {feature}` -> Playwright tests
6. `/document-work {context}/{feature}` -> Summary + PRD update

## Key Files

- `docs/OVERVIEW_PRD.md` — master feature list
- `docs/domain/GLOSSARY.md` — ubiquitous language
- `docs/architecture/CONTEXT_MAP.md` — bounded contexts
