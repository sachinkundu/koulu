# BUG-001: Test Infrastructure Failures

**Date Discovered:** 2026-02-05
**Feature:** Registration & Authentication
**Severity:** Critical (all 36 tests failing)
**Status:** Resolved

---

## Summary

All 36 BDD tests for the registration-authentication feature were failing when running `pytest`. The feature was marked as "Complete" in `docs/summaries/registration-authentication-summary.md` despite tests never having been successfully executed.

---

## Root Causes

### 1. Database URL String Replacement Bug
**File:** `tests/features/identity/conftest.py:32`

```python
# BROKEN: Replaces username AND database name
TEST_DATABASE_URL = settings.database_url.replace("/koulu", "/koulu_test")

# URL: postgresql+asyncpg://koulu:password@localhost:5432/koulu
# Becomes: postgresql+asyncpg://koulu_test:password@localhost:5432/koulu_test
#                         ^^^^^^^^^^^ Username corrupted!
```

**Fix:** Use `rsplit` to only replace the database name at the end.

### 2. Missing Test Database
The `koulu_test` database was never created in PostgreSQL.

### 3. Fixture Name Typo
**File:** `tests/features/identity/conftest.py:70`

```python
# BROKEN: References non-existent fixture
async def client(_db_session: AsyncSession)  # Should be db_session
```

### 4. App Database Session Not Overridden
The FastAPI app used its production database connection, not the test database. The `client` fixture didn't override `get_session` dependency.

### 5. Async/Sync Context Sharing Failure
Sync step functions (`def`) couldn't share the `context` dict with async step functions (`async def`) in pytest-bdd. All sync steps that used `context` needed to be converted to async with an async fixture dependency.

### 6. Underscore-Prefixed Parameters
Parameters like `_email`, `_code`, `_ordinal` were interpreted as fixture names by pytest, causing fixture lookup failures.

### 7. Missing Step Definitions
Step text variations like `"a user has..."` vs `"the user has..."` weren't covered.

---

## Why This Happened

### Process Failures

1. **Tests were never actually run successfully.** The implementation summary claims the feature is "Complete" but tests were failing. The verification steps in the summary mention running tests but don't enforce they must pass.

2. **Test infrastructure setup was incomplete.** The test database wasn't created, and the conftest had multiple bugs that prevented tests from even starting.

3. **No CI/CD pipeline.** Without automated test runs, failures went undetected.

4. **Stub tests masked problems.** Many BDD `@then` steps contained only `pass`, hiding that the actual assertions were never implemented. The summary even documents this: *"BDD tests were stubs (`pass`), hiding that EmailService was never called."*

5. **Definition of Done not enforced.** CLAUDE.md states to run verification scripts, but this wasn't done before marking complete.

### Technical Debt Indicators

- The conftest.py had obvious typos (`_db_session` instead of `db_session`)
- String manipulation for database URLs is fragile
- Mixing sync/async in pytest-bdd requires careful fixture design
- Underscore-prefix convention conflicts with pytest fixture injection

---

## Files Changed to Fix

| File | Changes |
|------|---------|
| `tests/features/identity/conftest.py` | Fixed DB URL, fixture names, added dependency override |
| `tests/features/identity/test_registration_authentication.py` | Converted ~40 sync functions to async, fixed underscore params, added missing step defs |

---

## Prevention Measures

### Immediate Actions

1. **Always run tests before marking complete.** Add explicit checklist item:
   ```
   - [ ] `pytest tests/` passes with 0 failures
   ```

2. ✅ **IMPLEMENTED: Auto-create test database.** Added `scripts/setup-test-db.sh`:
   - Checks if PostgreSQL container is running
   - Waits for health check
   - Creates `koulu_test` database if missing
   - Called automatically by `scripts/verify.sh`

3. ✅ **IMPLEMENTED: verify.sh calls setup-test-db.sh** before running pytest.

### Process Improvements

4. ✅ **IMPLEMENTED: Updated CLAUDE.md Definition of Done** with mandatory checklist, red flags, and evidence requirements.

5. **Add to document-work skill:**
   - Require screenshot or output of passing tests
   - Verify test count matches expected scenarios

6. **Implement CI/CD pipeline** (already in Next Steps):
   - Block PRs with failing tests
   - Require test coverage thresholds

### Technical Safeguards

7. **Use environment variable for test database:**
   ```python
   TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", f"{base_url}/koulu_test")
   ```

8. **Add pytest-bdd async compatibility note to BDD skill:**
   - All steps using shared `context` must be async
   - Add `client: AsyncClient` dependency to trigger async execution

9. **Lint for underscore-prefixed function parameters:**
   - These conflict with pytest's fixture injection

---

## Lessons Learned

1. **"Complete" means tests pass, not just code exists.** A feature with failing tests is not complete.

2. **Test infrastructure is part of the feature.** Database setup, fixtures, and CI are not optional.

3. **Stub tests are technical debt.** `pass` in a test step hides bugs.

4. **Verify before documenting.** Don't write implementation summaries until verification passes.

5. **Framework quirks matter.** pytest-bdd's async handling differs from standard pytest-asyncio.

---

## Related

- `docs/summaries/registration-authentication-summary.md` - Implementation summary (update needed)
- `.claude/skills/bdd.md` - BDD skill (add async guidance)
- `.claude/skills/implement-feature.md` - Feature implementation (strengthen verification)
- `CLAUDE.md` - Project instructions (add explicit test requirement)
