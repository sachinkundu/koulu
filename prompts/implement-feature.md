# Implement Feature Prompt

Use this prompt after you have a completed PRD and BDD spec to implement the feature.

---

## When to Use

- After `write-feature-spec.md` has produced PRD + BDD files
- When you're ready to write actual code
- When BDD scenarios are your acceptance criteria

---

## Instructions

1. Ensure PRD and BDD spec exist for the feature
2. Start a new Claude Code conversation (fresh context)
3. Paste this prompt
4. Claude will implement to pass the BDD tests

---

## The Prompt

```
I want to implement [FEATURE_NAME]. The spec is complete.

Follow the instructions below carefully.

---

## Phase 1: Load Context

Read these files in order:

1. `CLAUDE.md` — Core rules (especially scope management)
2. `docs/features/[context]/[feature]-prd.md` — The detailed PRD
3. `tests/features/[context]/[feature].feature` — The BDD acceptance criteria
4. `docs/domain/GLOSSARY.md` — Ubiquitous language
5. `docs/architecture/CONTEXT_MAP.md` — Bounded context relationships

Then read the relevant skills:
- `.claude/skills/architecture.md` — DDD patterns
- `.claude/skills/python.md` — If backend work
- `.claude/skills/frontend.md` — If frontend work

---

## Phase 2: Research Existing Code

Before writing any code, find:

1. **Similar patterns** — Existing features that do something similar (this is your template)
2. **Shared code** — Utilities, components, or services you can reuse
3. **Integration points** — Code that this feature needs to connect with

Summarize what you found and how you'll match existing patterns.

---

## Phase 3: Propose Your Approach (MANDATORY STOP)

Before writing ANY code, present:

1. **Task Summary** — What you're building and why

2. **Spec Reference** — Quote the relevant section from the PRD/BDD that defines correct behavior

3. **Pattern Reference** — The specific file(s) in the codebase where similar work is done (this is your template)

4. **Implementation Plan by Layer:**
   - **Domain Layer** — Entities, value objects, repository interfaces
   - **Application Layer** — Commands, handlers, application services
   - **Infrastructure Layer** — Repository implementations, API controllers
   - **Frontend** — Components, state management, API calls

5. **Files to Create/Modify** — Explicit list

6. **Files NOT to Modify** — What you will NOT touch (important for scope)

7. **Reusable Code** — Existing types, components, utilities you'll use

8. **Recent Context** — Run `git log --oneline -10` and note any relevant recent changes

**⛔ STOP and wait for my approval before implementing.**

If I say "proceed" or "go ahead", then implement.
If I have questions or changes, address them first.

---

## Phase 4: Implement

Follow this order:

### 4.1 Domain Layer First
- Create entities and value objects
- Define repository interfaces
- Define domain events
- NO external dependencies

### 4.2 Application Layer Second
- Create command/query handlers
- Implement business logic orchestration
- Wire up domain event publishing

### 4.3 Infrastructure Layer Third
- Implement repository adapters
- Create API endpoints
- Connect to external services

### 4.4 Frontend Last
- Create/update components
- Implement state management
- Connect to API
- Handle loading/error states

---

## Phase 5: Verify

After implementation:

1. **Run BDD tests:**
   ```bash
   # Python
   pytest tests/features/[context]/[feature].feature

   # Frontend
   npm run test:bdd -- --grep "[feature]"
   ```

2. **Run verification scripts:**
   ```bash
   ./scripts/verify.sh        # Python
   ./scripts/verify-frontend.sh  # Frontend
   ```

3. **Fix any failures** — Do NOT modify tests unless they were incorrect

4. **Verify side effects manually** — For features with integrations:
   - **Email sending** → Check MailHog at http://localhost:8025
   - **Events published** → Check logs for event publication
   - **External APIs** → Verify calls were made (check logs or mocks)
   - **Database changes** → Query DB directly if needed

   ⚠️ **WARNING**: If BDD test steps are stubs (just `pass`), the test passes without verifying anything. Check that step implementations have actual assertions!

---

## Rules

1. **Match existing patterns** — Find similar code and copy its structure
2. **No scope creep** — Only implement what's in the PRD/BDD spec
3. **Domain stays pure** — No framework imports in domain layer
4. **BDD is the contract** — If it's not in a scenario, don't build it
5. **Commit atomically** — One logical change per commit
6. **Don't fix other issues** — If you notice bugs or improvements outside scope, document them in `docs/bugs/` but do NOT fix them now
7. **Only touch listed files** — If you need to modify a file not in your proposal, STOP and update the proposal first

---

## Completion Checklist

Before marking done:

- [ ] All BDD scenarios pass
- [ ] Verification scripts pass (lint, types, tests)
- [ ] No `any` types introduced
- [ ] Domain layer has no external dependencies
- [ ] Existing patterns were followed
- [ ] Code is committed to feature branch
- [ ] **Side effects verified** — Emails, events, webhooks actually work (not just mocked)
- [ ] **No stub test steps** — All `@then` steps have actual assertions (not just `pass`)
```

---

## Example Usage

**You:** I want to implement Post Creation. The spec is complete.

**Claude:** *[Reads CLAUDE.md, PRD, BDD spec, researches existing code]*

**Research Summary:**
- Found similar pattern in `src/community/comments/` 
- Will reuse `BaseEntity` from `src/shared/domain/`
- API follows existing pattern in `src/infrastructure/api/`

**Implementation Plan:**

**Domain Layer:**
- `src/community/domain/entities/post.py` — Post aggregate
- `src/community/domain/value_objects/post_content.py` — Content VO
- `src/community/domain/events/post_created.py` — Domain event
- `src/community/domain/repositories/post_repository.py` — Interface

**Application Layer:**
- `src/community/application/commands/create_post.py` — Command + Handler

**Infrastructure Layer:**
- `src/community/infrastructure/persistence/post_repository_impl.py`
- `src/community/infrastructure/api/post_controller.py`

**Frontend:**
- `frontend/src/features/community/components/CreatePostForm.tsx`
- `frontend/src/features/community/api/posts.ts`

**Shall I proceed with this plan?**

**You:** Yes, proceed.

**Claude:** *[Implements domain layer, then application, then infrastructure, then frontend, runs tests]*