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

## ⛔ ZERO TOLERANCE POLICY: TEST FAILURES

**NEVER mark ANY work complete while tests are failing.**

This means:
- ✅ `pytest` output MUST show `0 failed` (not `1 failed`, not `10 failed`, not `100 failed`)
- ✅ All tests MUST either `PASS` or be explicitly `SKIPPED` with phase markers
- ✅ FAILING tests are NOT the same as SKIPPED tests — do not conflate them
- ✅ "Phase 2-4 scenarios" is NOT an excuse to commit failing tests

**If you see ANY number other than 0 in the "failed" count:**
1. ❌ **STOP** — do not mark work complete
2. ❌ **DO NOT COMMIT** — do not create git commits
3. ❌ **DO NOT RATIONALIZE** — "these failures are for future phases" is WRONG
4. ✅ **FIX OR SKIP** — either implement the missing code or add `@pytest.mark.skip(reason="Phase X: condition")`

**Examples:**

```bash
# ❌ WRONG - Work is NOT complete, do not mark done
===================== 60 passed, 10 failed, 2 skipped ======================

# ✅ CORRECT - All tests passing or properly skipped
===================== 60 passed, 30 skipped ===============================
```

**What "CI must be green" means:**
- pytest exit code 0 (no failures)
- All tests either pass or are skipped with phase markers
- Coverage meets threshold (≥80%)
- No warnings (fix root cause, don't suppress)

**Consequences of violation:**
- Code must be reverted to last green state
- Bug documented with root cause analysis
- Trust lost — will be remembered in MEMORY.md

**This is non-negotiable. Zero tolerance means zero.**

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

**⚠️ MANDATORY: A feature is NOT complete until ALL checks pass with ZERO failures, ZERO warnings, AND coverage threshold met.**

### Before Marking ANY Feature Complete — BLOCKING CHECKLIST:

**Run these commands and verify EXACT outputs:**

1. **Infrastructure Running:**
   ```bash
   docker-compose up -d
   ```
   - ✅ Must show: All services healthy

2. **Test Database Exists:**
   ```bash
   docker exec koulu-postgres psql -U koulu -c "\l" | grep koulu_test
   ```
   - ✅ Must show: `koulu_test` database present

3. **BDD Tests — MUST SHOW `0 failed`:**
   ```bash
   pytest tests/features/ --tb=short
   ```
   - ✅ **REQUIRED:** `===================== X passed, Y skipped ======================`
   - ✅ **REQUIRED:** `0 failed` in output (if you see `10 failed`, work is NOT complete)
   - ✅ **REQUIRED:** `0 warnings` in output
   - ❌ **BLOCKING:** ANY number other than `0` in "failed" count = work is NOT done

4. **Python Verification — MUST SHOW coverage ≥80%:**
   ```bash
   ./scripts/verify.sh
   ```
   - ✅ **REQUIRED:** `TOTAL ... 80%` or higher in coverage report
   - ✅ **REQUIRED:** All linting, type checking, unit tests pass
   - ❌ **BLOCKING:** Coverage <80% = work is NOT done

5. **Frontend Verification (if applicable):**
   ```bash
   ./scripts/verify-frontend.sh
   ```
   - ✅ Must show: All checks pass

**If ANY check fails, work is NOT complete. No exceptions. No rationalizations.**

### Red Flags (Feature is NOT Complete):
- ❌ Tests contain `pass` stubs instead of real assertions
- ❌ `@then` steps without assertions (must verify outcome)
- ❌ Comments say "mocked" but no actual mock/verification
- ❌ Coverage below 80% threshold
- ❌ "Tests require infrastructure" used as excuse to skip
- ❌ Verification scripts not run
- ❌ Any test failure, even 1 out of 100
- ❌ Any warnings in test output (fix the root cause, don't ignore)

### Warning Policy:
- **Fix warnings at the source** — don't suppress them
- If suppression is truly unavoidable (e.g., library integration issues):
  1. Use the most targeted filter possible (specific warning type + source module)
  2. Add a comment explaining WHY suppression is necessary
  3. **Inform the user** before suppressing — get explicit approval
- Never silently suppress warnings

### Evidence Required:

**When documenting completion, you MUST include EXACT output showing:**

1. **Test results with `0 failed`:**
   ```
   ======================= 36 passed, 30 skipped, 0 warnings =======================
   ```
   - ✅ Shows pass count
   - ✅ Shows skip count (if phased implementation)
   - ✅ **CRITICAL:** Shows `0 failed` (not `10 failed`, not `1 failed`)
   - ✅ Shows `0 warnings`

2. **Coverage ≥80%:**
   ```
   TOTAL                          1586    317    132     12    80%
   ```
   - ✅ Shows coverage percentage meets threshold

**Invalid evidence examples:**
```
# ❌ WRONG - 10 failed means work is NOT done
===================== 60 passed, 10 failed, 2 skipped ======================

# ❌ WRONG - 53% coverage is below 80% threshold
TOTAL                          1586    848    132     12    53%

# ❌ WRONG - Warnings present
===================== 36 passed, 5 warnings ================================
```

**If you cannot provide evidence showing `0 failed` and coverage ≥80%, the feature is NOT complete. Fix the failures or add the missing tests.**

### Self-Correction Protocol:

**If you realize you made a mistake (marked work complete when tests were failing):**

1. **Acknowledge immediately:**
   - "I made a mistake marking this complete while tests were failing."
   - No excuses, no rationalizations

2. **Assess damage:**
   - Was code committed? `git log -1`
   - What tests are failing? `pytest tests/features/ -v`
   - Is CI broken? Check exit code

3. **Fix or revert:**
   - **Option A (Fix):** If failures are quick to fix (< 30 min), fix them now
   - **Option B (Revert):** If complex, revert to last green state: `git reset --hard HEAD~1`

4. **Document lesson:**
   - Update MEMORY.md with new BUG-XXX entry
   - Include root cause analysis
   - Include prevention measures
   - Share with user

5. **Verify green:**
   - Run full verification checklist
   - Confirm `0 failed` before proceeding

**Better to catch your own mistakes early than have user discover them.**

---

## Testing Requirements

### Test Layers (ALL required for features)

| Layer | What to Test | Location |
|-------|--------------|----------|
| **Unit Tests** | Domain entities, value objects, handlers | `tests/unit/` |
| **BDD Tests** | User-facing behavior via API | `tests/features/` |

### Unit Tests for Domain Logic

**Every domain entity and handler with business logic MUST have unit tests.**

```python
# tests/unit/identity/domain/test_user.py
def test_user_verify_email_when_already_verified_raises_error():
    user = User.register(email, hashed_password)
    user.verify_email()  # First time succeeds

    with pytest.raises(UserAlreadyVerifiedError):
        user.verify_email()  # Second time fails
```

**Test these critical paths:**
- State transitions with guards (verify, login, disable)
- Value object validation (email format, password length, display name)
- Handler decision branches (all if/else paths)
- Error conditions and edge cases

### Test Fixture Standards

**⚠️ NEVER bypass the domain layer in test fixtures.**

```python
# ❌ WRONG - Creates ORM model directly, bypasses domain logic
async def create_user(db_session):
    user = UserModel(id=uuid4(), email=email, hashed_password=hash)
    db_session.add(user)
    return user

# ✅ CORRECT - Uses domain factory, then persists
async def create_user(user_repository, password_hasher):
    user = User.register(
        email=EmailAddress(email),
        hashed_password=password_hasher.hash(password)
    )
    await user_repository.save(user)
    return user
```

**Why this matters:**
- Domain logic (validation, events, invariants) gets tested
- Fixtures match real application flow
- Catches bugs in domain layer that direct DB inserts miss

### BDD Step Implementation Rules

```python
# ❌ NEVER write steps like this
@then('a verification email should be sent')
def email_sent(context):
    pass  # ALWAYS FAILS REVIEW

# ✅ ALWAYS verify the outcome
@then('a verification email should be sent to "{email}"')
async def email_sent(email: str):
    response = httpx.get(f"http://localhost:8025/api/v2/search?query=to:{email}")
    assert len(response.json()["items"]) > 0
```

---

Read the appropriate skill BEFORE implementation:

| Task | Skill |
|------|-------|
| Frontend code | `.claude/skills/frontend.md` |
| Python code | `.claude/skills/python.md` |
| DDD/Architecture | `.claude/skills/architecture.md` |
| BDD specs | `.claude/skills/bdd.md` |
| Security review | `.claude/skills/security.md` |
| UI components | `.claude/skills/ui-design.md` |
| Generate UI spec from screenshots | `/generate-ui-spec` |

---

## Prompts (Workflows)

| Workflow | Prompt File | When to Use |
|----------|-------------|-------------|
| Write Feature Spec | `prompts/write-feature-spec.md` | Creating PRD + BDD from OVERVIEW_PRD |
| Generate UI Spec | `/generate-ui-spec` skill | Analyzing Skool.com screenshots to create UI_SPEC.md |
| Implement Feature | `prompts/implement-feature.md` | Building code from completed spec |

---

## Key Files

- `docs/OVERVIEW_PRD.md` - Master feature list
- `docs/domain/GLOSSARY.md` - Ubiquitous language
- `docs/architecture/CONTEXT_MAP.md` - Bounded contexts
