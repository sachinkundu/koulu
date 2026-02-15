---
name: implement-phase-team
description: Implement a feature phase using parallel agent teams (backend + frontend + testing)
user_invocable: true
model: opus
---

# Implement Phase with Team

## Purpose

Execute a feature phase using an agent team for parallel implementation. Spawns backend, frontend, and testing agents that work simultaneously on their respective tasks, coordinated through a shared task list.

**Key Principle:** This skill orchestrates TEAMS. Use `/implement-feature` for single-agent sequential implementation. Use this when the phase task plan has tasks across multiple owners (backend, frontend, testing).

**Prerequisites:**
- Phase task plan must exist with `Owner:` tags and an Agent Execution Plan
- Use `/create-phase-plan` first to generate the plan with agent ownership

---

## Usage

`/implement-phase-team <context>/<feature-name> --phase=<number>`

Example: `/implement-phase-team gamification/leaderboards --phase=1`

---

## Input Requirements

**Must exist before starting:**
- PRD: `docs/features/{context}/{feature}-prd.md` (approved)
- TDD: `docs/features/{context}/{feature}-tdd.md` (approved)
- BDD: `tests/features/{context}/{feature}.feature` (approved)
- Phase plan: `docs/features/{context}/{feature}-implementation-phases.md`
- Granular tasks: `docs/features/{context}/{feature}-phase-{N}-tasks.md` (with `Owner:` tags)

**If Owner tags are missing:** Fall back to `/implement-feature` (single-agent mode). Do NOT guess ownership.

---

## Workflow

### Step 1: Validate Prerequisites

1. Parse arguments to extract `{context}`, `{feature}`, and `{phase}`
2. Read the phase task plan: `docs/features/{context}/{feature}-phase-{N}-tasks.md`
3. Verify it contains:
   - `Owner:` field on every task
   - `Agent Execution Plan` section at the top
   - `Depends on:` field on every task
4. If any are missing, **STOP** and tell the user:
   ```
   Phase task plan missing Owner tags or Agent Execution Plan.

   Regenerate with: /create-phase-plan {context}/{feature}

   The updated skill now generates Owner tags automatically.
   ```

### Step 2: Create Feature Branch

1. Check current branch: `git branch --show-current`
2. If on `main`: create `feature/{context}-{feature}`
3. If already on a feature branch for this feature: stay on it

### Step 3: Parse Agent Execution Plan

Read the Agent Execution Plan table from the task plan and build:

```
agents_needed = {
  "backend": [task_ids],       # single-backend mode
  "frontend": [task_ids],
  "testing": [task_ids],
}
start_conditions = {
  "backend": "immediately",
  "frontend": "immediately",
  "testing": "after backend + frontend",
}
```

**Multi-backend detection:** If the Agent Execution Plan contains `backend-domain`, `backend-infra`, or `backend-app` agents, use multi-backend mode instead:

```
agents_needed = {
  "backend-domain": [task_ids],   # domain layer
  "backend-infra": [task_ids],    # infrastructure layer
  "backend-app": [task_ids],      # application + API layer
  "frontend": [task_ids],
  "testing": [task_ids],
}
start_conditions = {
  "backend-domain": "immediately",
  "backend-infra": "immediately",
  "backend-app": "after backend-domain + backend-infra",
  "frontend": "immediately",
  "testing": "immediately (setup + domain tests), full integration after all implementation agents",
}
```

**Auto-splitting (when plan uses single `backend` owner with 8+ tasks):**
If the plan has a single `backend` agent with 8+ tasks, auto-split by analyzing file paths:
- Tasks creating files in `src/{context}/domain/` → `backend-domain`
- Tasks creating files in `src/{context}/infrastructure/` or `alembic/` → `backend-infra`
- Tasks creating files in `src/{context}/application/` or `src/{context}/interface/` → `backend-app`
- Cross-context modifications (e.g., enriching Community events) → `backend-infra`

Skip agents with no tasks. If only backend tasks exist and <8 tasks, fall back to `/implement-feature`.

### Step 4: Create Team and Task List

1. Create team:
   ```
   TeamCreate(team_name="{context}-{feature}-phase-{N}")
   ```

2. Create tasks in the team task list from the phase task plan:
   - One `TaskCreate` per task from the plan
   - Include full task text (steps, file paths, code snippets) in the description
   - Set `activeForm` to describe what the task does (e.g., "Implementing EventEntity")

3. Set up task dependencies using `TaskUpdate`:
   - Map `Depends on:` fields to `addBlockedBy` relationships
   - Testing tasks blocked by all backend + frontend tasks

### Step 5: Spawn Agents

Spawn agents in parallel using the Task tool. Each agent receives:
- Its agent definition from `.claude/agents/{agent-type}.md`
- The team name for task list coordination
- The feature branch name
- Key file paths (TDD, PRD, BDD, UI_SPEC)

**Backend Agent (single-backend mode):**
```
Task(
  name="backend-dev",
  team_name="{context}-{feature}-phase-{N}",
  subagent_type="general-purpose",
  mode="bypassPermissions",
  prompt="""
  You are the backend developer for this team.

  Read your agent instructions: .claude/agents/backend-dev.md

  Feature: {context}/{feature}, Phase {N}
  Branch: feature/{context}-{feature}

  Key files:
  - TDD: docs/features/{context}/{feature}-tdd.md
  - PRD: docs/features/{context}/{feature}-prd.md
  - BDD: tests/features/{context}/{feature}.feature

  Check TaskList for your assigned tasks (owner: backend-dev).
  Work through them in ID order, following TDD for each.
  Mark tasks completed as you finish them.
  Send a message to the team lead when all your tasks are done.
  """
)
```

**Multi-Backend Agents (when 8+ backend tasks — spawn all three in parallel):**

```
Task(
  name="backend-domain",
  team_name="{context}-{feature}-phase-{N}",
  subagent_type="general-purpose",
  mode="bypassPermissions",
  prompt="""
  You are the DOMAIN layer backend developer for this team.

  Read your agent instructions: .claude/agents/backend-dev.md

  Feature: {context}/{feature}, Phase {N}
  Branch: feature/{context}-{feature}

  Key files:
  - TDD: docs/features/{context}/{feature}-tdd.md
  - PRD: docs/features/{context}/{feature}-prd.md
  - Task plan: docs/features/{context}/{feature}-phase-{N}-tasks.md

  YOUR SCOPE: Domain layer ONLY
  - You own: src/{context}/domain/, tests/unit/{context}/domain/
  - Do NOT touch: src/{context}/infrastructure/, src/{context}/application/, src/{context}/interface/, frontend/, alembic/

  Check TaskList for your assigned tasks (owner: backend-domain).
  Work through them in ID order, following TDD for each.
  Mark tasks completed as you finish them.
  Send a message to the team lead when all your tasks are done.
  """
)
```

```
Task(
  name="backend-infra",
  team_name="{context}-{feature}-phase-{N}",
  subagent_type="general-purpose",
  mode="bypassPermissions",
  prompt="""
  You are the INFRASTRUCTURE layer backend developer for this team.

  Read your agent instructions: .claude/agents/backend-dev.md

  Feature: {context}/{feature}, Phase {N}
  Branch: feature/{context}-{feature}

  Key files:
  - TDD: docs/features/{context}/{feature}-tdd.md
  - Task plan: docs/features/{context}/{feature}-phase-{N}-tasks.md

  YOUR SCOPE: Infrastructure layer + cross-context event enrichment ONLY
  - You own: src/{context}/infrastructure/, alembic/versions/, cross-context event files (e.g., src/community/domain/events.py enrichment)
  - Do NOT touch: src/{context}/domain/, src/{context}/application/, src/{context}/interface/, frontend/

  Check TaskList for your assigned tasks (owner: backend-infra).
  Work through them in ID order, following TDD for each.
  Mark tasks completed as you finish them.
  Send a message to the team lead when all your tasks are done.
  """
)
```

```
Task(
  name="backend-app",
  team_name="{context}-{feature}-phase-{N}",
  subagent_type="general-purpose",
  mode="bypassPermissions",
  prompt="""
  You are the APPLICATION layer backend developer for this team.

  Read your agent instructions: .claude/agents/backend-dev.md

  Feature: {context}/{feature}, Phase {N}
  Branch: feature/{context}-{feature}

  Key files:
  - TDD: docs/features/{context}/{feature}-tdd.md
  - PRD: docs/features/{context}/{feature}-prd.md
  - Task plan: docs/features/{context}/{feature}-phase-{N}-tasks.md

  YOUR SCOPE: Application layer, API endpoints, and app wiring ONLY
  - You own: src/{context}/application/, src/{context}/interface/, tests/unit/{context}/application/
  - Do NOT touch: src/{context}/domain/, src/{context}/infrastructure/, frontend/, alembic/

  IMPORTANT: Your tasks depend on backend-domain and backend-infra completing first.
  Check TaskList — your tasks will be blocked until dependencies are resolved.

  Check TaskList for your assigned tasks (owner: backend-app).
  Work through them in ID order, following TDD for each.
  Mark tasks completed as you finish them.
  Send a message to the team lead when all your tasks are done.
  """
)
```

**Frontend Agent:**
```
Task(
  name="frontend-dev",
  team_name="{context}-{feature}-phase-{N}",
  subagent_type="general-purpose",
  mode="bypassPermissions",
  prompt="""
  You are the frontend developer for this team.

  Read your agent instructions: .claude/agents/frontend-dev.md

  Feature: {context}/{feature}, Phase {N}
  Branch: feature/{context}-{feature}

  Key files:
  - UI_SPEC: docs/features/{context}/UI_SPEC.md
  - TDD: docs/features/{context}/{feature}-tdd.md (API contract)
  - PRD: docs/features/{context}/{feature}-prd.md

  Check TaskList for your assigned tasks (owner: frontend-dev).
  Work through them in ID order.
  Code against the TDD API contract — do NOT wait for backend.
  Mark tasks completed as you finish them.
  Send a message to the team lead when all your tasks are done.
  """
)
```

**Testing Agent (spawned IMMEDIATELY — works in phases):**
```
Task(
  name="test-engineer",
  team_name="{context}-{feature}-phase-{N}",
  subagent_type="general-purpose",
  mode="bypassPermissions",
  prompt="""
  You are the test engineer for this team.

  Read your agent instructions: .claude/agents/test-engineer.md

  Feature: {context}/{feature}, Phase {N}
  Branch: feature/{context}-{feature}

  Key files:
  - BDD: tests/features/{context}/{feature}.feature
  - TDD: docs/features/{context}/{feature}-tdd.md
  - PRD: docs/features/{context}/{feature}-prd.md
  - Task plan: docs/features/{context}/{feature}-phase-{N}-tasks.md

  Check TaskList for your assigned tasks (owner: test-engineer).

  IMPORTANT: You start IMMEDIATELY, not after backend finishes. Work in 3 phases:

  PHASE A — Start now (no dependencies):
  1. Read existing BDD test patterns in tests/features/ (e.g., community/)
  2. Create tests/features/{context}/__init__.py
  3. Create tests/features/{context}/conftest.py with fixtures:
     - Community creation helpers
     - User/auth helpers
     - Any domain factory helpers needed
  4. Add skip markers for all future-phase scenarios
  5. Create step definition shells (function signatures) for all scenarios

  PHASE B — After domain tasks complete (check TaskList for domain task status):
  6. Implement step definitions for domain-level BDD scenarios
     (scenarios testing pure domain logic like level calculation,
     point accumulation, ratchet behavior — these don't need API)
  7. Run these tests to verify domain logic

  PHASE C — After ALL backend + frontend tasks complete:
  8. Implement step definitions for API-level BDD scenarios
     (scenarios testing HTTP endpoints, event-driven point awards)
  9. Run full verification: ./scripts/verify.sh
  10. Send verification results to team lead

  Mark tasks completed as you finish them.
  If blocked waiting for backend, send a message to the team lead.
  """
)
```

### Step 6: Assign Tasks and Monitor

1. **Assign backend tasks** to `backend-dev` (or `backend-domain`/`backend-infra`/`backend-app`) using TaskUpdate
2. **Assign frontend tasks** to `frontend-dev` using TaskUpdate
3. **Assign testing tasks** to `test-engineer` using TaskUpdate — testing starts immediately

   **Testing task dependency strategy:**
   - If the plan has split testing tasks (`testing-setup`, `testing-domain`, `testing-integration`):
     - `testing-setup` tasks: no blockers (assign immediately)
     - `testing-domain` tasks: blocked by domain backend tasks only
     - `testing-integration` tasks: blocked by all backend + frontend tasks
   - If the plan has a single testing task: split it into sub-tasks at team creation time:
     - Create a "Test scaffolding" task (no blockers) — conftest, fixtures, skip markers
     - Create a "Domain BDD tests" task (blocked by domain tasks) — domain-level step definitions
     - Create a "Integration BDD tests + verification" task (blocked by all) — API-level steps, final run

4. **Monitor progress:**
   - Agents send messages when they complete tasks or encounter issues
   - Messages are delivered automatically — no polling needed
   - Check TaskList periodically to see overall progress

5. **When backend + frontend agents report completion:**
   - Verify all their tasks are marked completed in TaskList
   - Run a quick integration check: `ruff check src/{context}/ && mypy src/{context}/`
   - If issues found, send fixes back to the relevant agent
   - Test engineer should already be working on integration tests by this point

### Step 7: Handle Issues

**If an agent reports a blocker:**
- Read the issue
- If it's a cross-agent dependency (e.g., frontend needs an API detail), clarify from the TDD
- If it's a bug, create a fix task and assign to the right agent
- If it requires a decision, ask the user

**If agents have file conflicts:**
- This should not happen if Owner tags are correct
- If it does: stop the conflicting agent, resolve the conflict, restart

**If an agent fails a task:**
- Do NOT continue to the next phase
- Fix the issue or reassign the task
- Re-run verification

### Step 8: Final Verification

After the testing agent reports verification results:

1. **Review test results:**
   - All enabled BDD scenarios pass
   - Future scenarios properly skipped with phase markers
   - Coverage >= 80%

2. **Run full verification yourself:**
   ```bash
   ./scripts/verify-phase-complete.sh "Phase {N}"
   ```

3. **Run deployability check (if user-facing):**
   ```bash
   ./scripts/check-deployability.sh {feature}
   ```

4. **If ALL pass:**
   - Commit any remaining changes
   - Report completion to user with test counts, coverage, CI status
   - Provide manual testing guide (same format as `/implement-feature`)

5. **If ANY fail:**
   - Do NOT mark complete
   - Create fix tasks, assign to agents, iterate

### Step 9: Teardown

After phase is verified complete:

1. Send shutdown requests to all agents:
   ```
   SendMessage(type="shutdown_request", recipient="backend-dev")
   SendMessage(type="shutdown_request", recipient="frontend-dev")
   SendMessage(type="shutdown_request", recipient="test-engineer")
   ```

2. Wait for shutdown confirmations

3. Delete the team:
   ```
   TeamDelete()
   ```

4. Report to user:
   ```
   Phase {N} Complete (Team Mode)

   Agents: 3 (backend-dev, frontend-dev, test-engineer)
   Tasks: X completed, 0 failed

   pytest output:
   ===================== X passed, Y skipped, 0 warnings =======================

   Coverage: XX%
   CI: Green
   Deployable: Yes

   ## Manual Testing Guide
   ...

   Proceed to Phase {N+1}?
   ```

---

## When to Use Team Mode vs Single-Agent Mode

**Use `/implement-phase-team` when:**
- Phase has 6+ tasks across backend + frontend
- Phase task plan has tasks tagged for multiple owners
- Feature has significant UI (not just API endpoints)
- You want maximum speed for a large phase

**Use multi-backend mode (within team mode) when:**
- Phase has 8+ backend tasks
- Backend tasks have independent sub-chains across architectural layers (domain, infra, app)
- Domain foundations and infrastructure can be built in parallel
- Single backend agent would be the bottleneck while frontend finishes quickly

**Use single-backend mode when:**
- Phase has <8 backend tasks
- Backend tasks are highly sequential
- Most tasks touch the same directories

**Use `/implement-feature` when:**
- Phase has < 6 tasks total
- All tasks are backend-only or frontend-only
- Tasks have heavy sequential dependencies (little parallelism possible)
- Feature is backend-only (no UI)

---

## Fallback to Single-Agent Mode

If team mode encounters persistent issues:
1. Send shutdown requests to all agents
2. Delete the team
3. Fall back to `/implement-feature {context}/{feature} --phase={N}`
4. Note the issue for the user

---

## Anti-Patterns to Avoid

- **Don't spawn agents before validating the task plan** — missing Owner tags cause chaos
- **Don't wait to spawn the testing agent until backend finishes** — test scaffolding (conftest, fixtures, skip markers) and domain-level BDD steps can be written in parallel. Only API-level integration tests need the full backend
- **Don't let agents modify files outside their ownership** — causes merge conflicts
- **Don't skip final verification** — agents may report success but have cross-cutting issues
- **Don't keep the team alive after phase completion** — clean up resources
- **Don't use team mode for single-owner phases** — overhead exceeds benefit
- **Don't use a single backend agent for 8+ backend tasks** — it becomes the bottleneck while frontend finishes quickly. Split into backend-domain, backend-infra, and backend-app agents
- **Don't let backend-app start before backend-domain finishes** — app layer imports from domain interfaces
- **Don't let two backend agents touch the same directory** — strict layer ownership prevents conflicts
