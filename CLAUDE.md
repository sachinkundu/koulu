# Koulu - Claude Code Instructions

A Skool.com clone: community platform with feed, classroom, calendar, members, leaderboards.

---

## ⛔ SCOPE RULES (NON-NEGOTIABLE)

**Build ONLY what is explicitly requested. Nothing more.**

Before writing ANY code, ask yourself:
1. Did the user EXPLICITLY request this exact feature?
2. Am I adding ANYTHING beyond the stated requirement?
3. Is this the MINIMUM implementation that satisfies the request?

**If NO to any question → STOP and ask for clarification.**

❌ **NEVER** add "helpful" features, badges, indicators, or enhancements without permission  
❌ **NEVER** assume features are needed  
❌ **NEVER** pick an interpretation and proceed—ask first  

**Violation = code deletion + bug documentation + loss of trust**

---

## Research Protocol

**Before ANY implementation:**
1. Read relevant specs in `docs/` 
2. Find existing patterns in codebase—match them exactly
3. Read every file you plan to modify

**Before using ANY external library:** Research exact API signatures. Never assume from memory.

---

## Tech Stack

| Layer | Stack |
|-------|-------|
| Frontend | React (Vite) + TypeScript (strict) + TailwindCSS |
| Backend | Python + FastAPI |
| Testing | Vitest + pytest-bdd |
| Tracing | OpenTelemetry |
| Logging | structlog (Python), console wrapper (Frontend) |

---

## Architecture: Hexagonal + DDD

```
src/
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

**Rules:**
- Domain layer has ZERO external imports
- No anemic models—entities contain behavior
- Aggregates protect their own consistency
- Cross-context communication via events only

---

## Workflow

### New Feature
```
1. git checkout -b feature/description
2. Write BDD spec → tests/features/*.feature
3. Implement (match existing patterns)
4. Run verification scripts
5. Notify user—NEVER merge yourself
```

### Bug Fix / Iteration
Continue on the SAME feature branch. New branch only for new features.

---

## Verification (Definition of Done)

**Frontend:** `./scripts/verify-frontend.sh`
- Lint, typecheck, test, build must all pass

**Python:** `./scripts/verify.sh`  
- ruff, mypy, pytest with >80% coverage

**BDD:** `pytest tests/features/` or `npm run test:bdd`

---

## Skills Reference

Read the appropriate skill BEFORE implementation:

| Task | Skill |
|------|-------|
| Frontend code | `.claude/skills/frontend.md` |
| Python code | `.claude/skills/python.md` |
| DDD/Architecture | `.claude/skills/architecture.md` |
| BDD specs | `.claude/skills/bdd.md` |
| Security review | `.claude/skills/security.md` |
| UI components | `.claude/skills/ui-design.md` |

---

## Prompts (Workflows)

| Workflow | Prompt File | When to Use |
|----------|-------------|-------------|
| Write Feature Spec | `prompts/write-feature-spec.md` | Creating PRD + BDD from OVERVIEW_PRD |
| Implement Feature | `prompts/implement-feature.md` | Building code from completed spec |

---

## Key Files

- `docs/OVERVIEW_PRD.md` - Master feature list
- `docs/domain/GLOSSARY.md` - Ubiquitous language
- `docs/architecture/CONTEXT_MAP.md` - Bounded contexts
