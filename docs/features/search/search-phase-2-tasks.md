# Search — Phase 2 Granular Tasks

## Phase: Phase 2 — Pagination, Stemming & Validation
## Goal: Complete the search experience with pagination controls, verify stemming works, and add input validation with proper error messages.

---

## Dependency Graph

```
Task 1 (Enable validation BDD tests) ──┐
Task 2 (Enable stemming BDD tests)  ───┤── Task 5 (Run full verification)
Task 3 (Enable pagination BDD tests) ──┤
Task 4 (Frontend pagination UI)     ───┘
```

## Parallel Execution Summary

| Batch | Tasks | Parallel? | Rationale |
|-------|-------|-----------|-----------|
| 1 | 1, 2, 3 | Yes | Independent test-enable tasks, different scenarios |
| 2 | 4 | No | Frontend pagination component, depends on understanding pagination API behavior |
| 3 | 5 | No | Full verification after all tasks |

---

## Task 1: Enable and verify validation BDD tests (4 scenarios)

**Depends on:** None

**Files:**
- `tests/features/search/test_search.py` (MODIFY — remove skip markers for 4 validation scenarios)

**Steps:**
1. Remove `@pytest.mark.skip` from these 4 scenarios:
   - `test_search_with_query_shorter_than_3_characters`
   - `test_search_with_empty_query`
   - `test_search_with_invalid_type_parameter`
   - `test_search_with_query_exceeding_maximum_length`
2. Enhance assertion in `search_fails_with_error` to check proper error codes
3. Run `pytest tests/features/search/test_search.py -k "shorter or empty or invalid_type or exceeding" -v`
4. Verify all 4 pass

**Notes:**
- The controller already implements validation (3-char min, empty check, type check, 200-char truncation)
- The `search_fails_with_error` step currently only checks `status != 200` — needs to verify specific error codes

---

## Task 2: Enable and verify stemming BDD tests (2 scenarios)

**Depends on:** None

**Files:**
- `tests/features/search/test_search.py` (MODIFY — remove skip markers for 2 stemming scenarios)

**Steps:**
1. Remove `@pytest.mark.skip` from:
   - `test_search_uses_stemming_for_member_bio`
   - `test_search_uses_stemming_for_post_content`
2. Run `pytest tests/features/search/test_search.py -k "stemming" -v`
3. Verify both pass (PostgreSQL English FTS handles stemming natively)

**Notes:**
- Stemming is automatic via `plainto_tsquery('english', ...)` and `to_tsvector('english', ...)`
- "engineering" → "engin" stem matches "engineer" → "engin"
- "growing" → "grow" stem matches "growth" → "grow"

---

## Task 3: Enable and verify pagination BDD tests (2 scenarios)

**Depends on:** None

**Files:**
- `tests/features/search/test_search.py` (MODIFY — remove skip markers for 2 pagination scenarios)

**Steps:**
1. Remove `@pytest.mark.skip` from:
   - `test_search_results_are_paginated`
   - `test_navigate_to_next_page_of_results`
2. Enhance `results_from_second_page` step to verify items are different from first page
3. Run `pytest tests/features/search/test_search.py -k "paginated or next_page" -v`
4. Verify both pass

**Notes:**
- Backend already supports `limit` and `offset` parameters
- `has_more` flag is already calculated in handler
- Test fixtures create 25 members with "developer" bio for pagination testing

---

## Task 4: Add frontend pagination component

**Depends on:** None

**Files:**
- `frontend/src/features/search/components/SearchPagination.tsx` (CREATE)
- `frontend/src/features/search/components/SearchResults.tsx` (MODIFY — add pagination)
- `frontend/src/features/search/components/index.ts` (MODIFY — export SearchPagination)
- `frontend/src/features/search/hooks/useSearch.ts` (MODIFY — accept page param)

**Steps:**
1. Create `SearchPagination.tsx` with Previous/Next buttons and "1-10 of N" indicator
2. Modify `SearchResults.tsx` to read `?page=N` from URL and pass offset to useSearch
3. Update `useSearch.ts` to support page-based offset calculation
4. Export new component from index

---

## Task 5: Run full verification

**Depends on:** Tasks 1, 2, 3, 4

**Steps:**
1. Run `pytest tests/features/search/test_search.py -v` — expect 19 passed, 11 skipped
2. Run `./scripts/verify.sh` — expect all green
3. Run `cd frontend && npm run build && npm run typecheck` — expect no errors
4. Verify all Phase 3 scenarios still have skip markers
