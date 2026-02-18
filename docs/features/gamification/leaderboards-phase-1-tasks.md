# Leaderboards Phase 1 — Task Plan

> **For Claude:** Use `/implement-feature gamification/leaderboards --phase=1` to execute this plan.

**Phase goal:** Deliver the complete `/leaderboards` page with three side-by-side ranking panels (7-day, 30-day, all-time), profile card, level definitions, medals, "Your rank" section, and loading/empty/error states.
**Files to create/modify:** ~25
**BDD scenarios to enable:** 13
**Estimated time:** 4-5 hours
**Task count:** 16

---

### Dependency Graph

```
Backend:                              Frontend:                         Testing:

T1 (LeaderboardPeriod)──┐            T7 (TS types)                     T15 (conftest fixtures)
                        │              │                                   │
T5 (API schemas)        │            T8 (API function)                    │
    │                   ▼              │                                   │
    │               T2 (repo iface)  T9 (hook)      T10 (Medal)  T11(Skel) T15(ProfileCard)
    │                   │              │               │    │         │
    │               T3 (repo impl)     │           T12 (LeaderboardRow)
    │                   │              │               │
    │               T4 (query handler) │           T13 (YourRankSection)
    │                   │              │               │
    └──────────────►T6 (endpoint+DI)   │           T14 (LeaderboardPanel)
                        │              │               │
                        │              └───────┬───────┘
                        │                      │
                        │              T16 (LeaderboardsPage)
                        │                      │
                        └──────────────────────┤
                                               │
                                       T17 (BDD steps + verify)
```

### Parallel Execution Summary

| Batch | Tasks | Mode | Rationale |
|-------|-------|------|-----------|
| 1 | T1, T5, T7, T10, T11, T15 (conftest), T15b (ProfileCard) | Parallel | All independent foundations |
| 2 | T2, T8, T12 | Parallel | Depend on Batch 1 items within their agent |
| 3 | T3, T4, T9, T13 | Parallel | Each depends on own agent's prior work |
| 4 | T6, T14 | Parallel | Endpoint wiring + panel assembly |
| 5 | T16 | Sequential | Page composition — needs hook + all components |
| 6 | T17 | Sequential | BDD tests — needs full backend + frontend |

**Sequential execution:** 16 tasks × ~20 min = ~5.3 hours
**Parallel execution:** 6 batches (estimated ~40% time savings)

### Agent Execution Plan

| Agent | Tasks | Starts | Blocked Until |
|-------|-------|--------|---------------|
| backend | T1, T2, T3, T4, T5, T6 | Immediately | — |
| frontend | T7, T8, T9, T10, T11, T12, T13, T14, T15b, T16 | Immediately | — |
| testing | T15, T17 | T15 immediately; T17 after backend + frontend | All implementation tasks complete |

**File ownership boundaries:**
- `backend` owns: `src/gamification/` (all subdirectories), no Alembic migration needed
- `frontend` owns: `frontend/src/features/gamification/`, `frontend/src/pages/LeaderboardsPage.tsx`
- `testing` owns: `tests/features/gamification/conftest.py` (additions), `tests/features/gamification/test_leaderboards.py`

---

### Task 1: LeaderboardPeriod Value Object

**Owner:** backend
**Depends on:** none

**Files:**
- Create: `src/gamification/domain/value_objects/leaderboard_period.py`

**What to build:**
An enum with three variants: `SEVEN_DAY`, `THIRTY_DAY`, `ALL_TIME`. Each variant exposes:
- `interval_hours: int | None` — 168 for 7-day, 720 for 30-day, `None` for all-time
- `display_label: str` — "7-day", "30-day", "All-time"

**Implementation notes:**
- Follow existing `PointSource` enum pattern in `src/gamification/domain/value_objects/point_source.py`
- Use Python `enum.Enum` with property methods
- No unit test file needed — enum is trivial and fully exercised by integration tests

---

### Task 2: Repository Interface Extension

**Owner:** backend
**Depends on:** T1

**Files:**
- Modify: `src/gamification/domain/repositories/member_points_repository.py`

**What to build:**
Add a new abstract method to `IMemberPointsRepository`:

```python
async def get_leaderboard(
    self,
    community_id: UUID,
    period: LeaderboardPeriod,
    limit: int,
    current_user_id: UUID,
) -> LeaderboardResult:
    ...
```

Also define the result dataclass(es) in the same file or in a new `leaderboard_result.py`:

```python
@dataclass(frozen=True)
class LeaderboardEntry:
    rank: int
    user_id: UUID
    display_name: str
    avatar_url: str | None
    level: int
    points: int

@dataclass(frozen=True)
class LeaderboardResult:
    entries: list[LeaderboardEntry]   # top N
    your_rank: LeaderboardEntry | None  # None if user is in entries
```

**Implementation notes:**
- Follow the existing pattern: `IMemberPointsRepository` is an ABC with abstract methods
- Import `LeaderboardPeriod` from Task 1
- Result dataclasses are frozen (immutable) — consistent with existing value objects

---

### Task 3: Repository Implementation (SQL Queries)

**Owner:** backend
**Depends on:** T2

**Files:**
- Modify: `src/gamification/infrastructure/persistence/member_points_repository.py`

**What to build:**
Implement `get_leaderboard()` on `SqlAlchemyMemberPointsRepository`. This is the core query logic:

**For period boards (7-day, 30-day):**
1. Join `member_points` → `point_transactions` WHERE `point_transactions.created_at >= NOW() - interval`
2. SUM `point_transactions.points` per member, apply `GREATEST(0, sum)` to floor negative net
3. LEFT JOIN `profiles` for `display_name` and `avatar_url` (cross-context read)
4. ORDER BY `net_points DESC, display_name ASC`
5. Use `ROW_NUMBER()` window function to assign sequential ranks
6. Return top N entries + current user's rank row if not in top N

**For all-time:**
1. Select from `member_points` directly (use `total_points` column)
2. LEFT JOIN `profiles` for display data
3. ORDER BY `total_points DESC, display_name ASC`
4. Same `ROW_NUMBER()` + "your rank" logic

**Critical SQL details:**
- Use `ROW_NUMBER()` not `RANK()` — no tied positions
- Use `COALESCE(p.display_name, 'Member')` for members without profile rows
- For period queries, members with zero transactions in the window still need to be ranked (they have 0 points in the period). Use a LEFT JOIN from `member_points` to a subquery of period transactions, so members without transactions appear with `SUM = 0`.
- The `your_rank` entry is `None` when the current user's rank falls within the top N

**Implementation notes:**
- Use SQLAlchemy `text()` for the complex window function query, or build with SQLAlchemy Core expressions
- Import `ProfileModel` from `src.identity.infrastructure.persistence.models` for the JOIN
- Follow existing repository patterns (async session, `await self._session.execute(stmt)`)
- This is the most complex task — allocate extra time

---

### Task 4: GetLeaderboards Query Handler

**Owner:** backend
**Depends on:** T2

**Files:**
- Create: `src/gamification/application/queries/get_leaderboards.py`

**What to build:**
A query dataclass and handler following existing patterns (`get_member_level.py`, `get_level_definitions.py`):

**Query:**
```python
@dataclass(frozen=True)
class GetLeaderboardsQuery:
    community_id: UUID
    current_user_id: UUID
```

**Result:**
```python
@dataclass(frozen=True)
class LeaderboardPeriodResult:
    entries: list[LeaderboardEntry]
    your_rank: LeaderboardEntry | None

@dataclass(frozen=True)
class LeaderboardsResult:
    seven_day: LeaderboardPeriodResult
    thirty_day: LeaderboardPeriodResult
    all_time: LeaderboardPeriodResult
    last_updated: datetime  # UTC now
```

**Handler:**
```python
class GetLeaderboardsHandler:
    def __init__(self, member_points_repo: IMemberPointsRepository):
        self._repo = member_points_repo

    async def handle(self, query: GetLeaderboardsQuery) -> LeaderboardsResult:
        # Call repo.get_leaderboard() three times (one per period)
        # Assemble LeaderboardsResult
        # last_updated = datetime.now(UTC)
```

**Implementation notes:**
- Follow existing handler pattern: constructor takes repo, `handle()` is async
- The handler depends only on the repository interface (T2), not the implementation (T3)
- Use `structlog` for logging query duration (optional but follows pattern)

---

### Task 5: API Response Schemas

**Owner:** backend
**Depends on:** none

**Files:**
- Modify: `src/gamification/infrastructure/api/schemas.py`

**What to build:**
Add Pydantic models for the leaderboard API response:

```python
class LeaderboardEntrySchema(BaseModel):
    rank: int
    user_id: UUID
    display_name: str
    avatar_url: str | None
    level: int
    points: int

class LeaderboardPeriodSchema(BaseModel):
    entries: list[LeaderboardEntrySchema]
    your_rank: LeaderboardEntrySchema | None

class LeaderboardsResponse(BaseModel):
    seven_day: LeaderboardPeriodSchema
    thirty_day: LeaderboardPeriodSchema
    all_time: LeaderboardPeriodSchema
    last_updated: datetime
```

**Implementation notes:**
- Follow existing schema patterns in the same file (e.g., `MemberLevelResponse`)
- Use `from pydantic import BaseModel` (already imported)

---

### Task 6: API Endpoint + DI Wiring

**Owner:** backend
**Depends on:** T4, T5

**Files:**
- Modify: `src/gamification/interface/api/gamification_controller.py`
- Modify: `src/gamification/interface/api/dependencies.py`

**What to build:**

**In `dependencies.py`:**
- Add `get_get_leaderboards_handler()` factory function returning `GetLeaderboardsHandler(member_points_repo=mp_repo)`
- Follow existing pattern (e.g., `get_get_member_level_handler`)

**In `gamification_controller.py`:**
- Add `GET /{community_id}/leaderboards` on the `router` (explicit community)
- Add `GET /leaderboards` on the `default_router` (auto-resolving)
- Both wire through `GetLeaderboardsHandler` → `LeaderboardsResponse`

**Implementation notes:**
- Follow existing dual-router pattern exactly
- Map handler result to response schema (same pattern as `get_member_level` endpoint)
- Add auth dependency (`CurrentUserIdDep`) — same as existing endpoints

---

### Task 7: TypeScript Types

**Owner:** frontend
**Depends on:** none

**Files:**
- Modify: `frontend/src/features/gamification/types/index.ts`

**What to build:**
Add TypeScript interfaces matching the API response contract:

```typescript
export interface LeaderboardEntry {
  rank: number;
  user_id: string;
  display_name: string;
  avatar_url: string | null;
  level: number;
  points: number;
}

export interface LeaderboardPeriod {
  entries: LeaderboardEntry[];
  your_rank: LeaderboardEntry | null;
}

export interface LeaderboardsResponse {
  seven_day: LeaderboardPeriod;
  thirty_day: LeaderboardPeriod;
  all_time: LeaderboardPeriod;
  last_updated: string;
}
```

**Implementation notes:**
- Append to existing file (don't overwrite existing types)
- Use `string` for UUID and datetime fields (JSON serialization)

---

### Task 8: API Function

**Owner:** frontend
**Depends on:** T7

**Files:**
- Modify: `frontend/src/features/gamification/api/gamificationApi.ts`
- Modify: `frontend/src/features/gamification/api/index.ts`

**What to build:**

```typescript
export async function getLeaderboards(): Promise<LeaderboardsResponse> {
  const response = await apiClient.get<LeaderboardsResponse>('/community/leaderboards');
  return response.data;
}
```

**Implementation notes:**
- Follow existing pattern (`getMemberLevel`, `getLevelDefinitions`)
- Uses auto-resolving `/community/` prefix (no community ID needed)
- Add re-export in `index.ts`

---

### Task 9: useLeaderboards Hook

**Owner:** frontend
**Depends on:** T8

**Files:**
- Create: `frontend/src/features/gamification/hooks/useLeaderboards.ts`
- Modify: `frontend/src/features/gamification/hooks/index.ts`

**What to build:**

```typescript
export function useLeaderboards(): UseLeaderboardsResult {
  const { data, isLoading, error } = useQuery<LeaderboardsResponse>({
    queryKey: ['leaderboards'],
    queryFn: getLeaderboards,
  });
  return { data, isLoading, error };
}
```

**Interface:**
```typescript
interface UseLeaderboardsResult {
  data: LeaderboardsResponse | undefined;
  isLoading: boolean;
  error: Error | null;
}
```

**Implementation notes:**
- Follow existing pattern from `useGamification.ts` (`useMemberLevel`, `useLevelDefinitions`)
- Add re-export in `hooks/index.ts`

---

### Task 10: RankMedal Component

**Owner:** frontend
**Depends on:** none

**Files:**
- Create: `frontend/src/features/gamification/components/RankMedal.tsx`
- Create: `frontend/src/features/gamification/components/RankMedal.test.tsx`

**What to build:**
A simple component that renders emoji medals for ranks 1-3.

**Props:** `{ rank: 1 | 2 | 3 }`

**Implementation:**
```tsx
const medalEmoji: Record<1 | 2 | 3, string> = { 1: '🥇', 2: '🥈', 3: '🥉' };

export function RankMedal({ rank }: { rank: 1 | 2 | 3 }): JSX.Element {
  return (
    <span className="text-base leading-none" role="img" aria-label={...}>
      {medalEmoji[rank]}
    </span>
  );
}
```

**Test:** Renders correct emoji for each rank. Has appropriate aria-label.

---

### Task 11: LeaderboardRowSkeleton Component

**Owner:** frontend
**Depends on:** none

**Files:**
- Create: `frontend/src/features/gamification/components/LeaderboardRowSkeleton.tsx`

**What to build:**
Shimmer placeholder row with animate-pulse divs matching row layout (rank circle + avatar circle + name bar + points bar).

**Structure per UI_SPEC:**
```tsx
<div className="flex items-center gap-3 px-4 py-2.5">
  <div className="h-4 w-4 animate-pulse rounded-full bg-gray-200" />
  <div className="h-8 w-8 animate-pulse rounded-full bg-gray-200" />
  <div className="h-4 flex-1 animate-pulse rounded bg-gray-200" />
  <div className="h-4 w-8 animate-pulse rounded bg-gray-200" />
</div>
```

**No test needed** — purely presentational with no logic.

---

### Task 12: LeaderboardRow Component

**Owner:** frontend
**Depends on:** T10

**Files:**
- Create: `frontend/src/features/gamification/components/LeaderboardRow.tsx`
- Create: `frontend/src/features/gamification/components/LeaderboardRow.test.tsx`

**What to build:**
A single ranked member row showing rank/medal, avatar with level badge, name, and points.

**Props:**
```typescript
interface LeaderboardRowProps {
  entry: LeaderboardEntry;
  period: '7day' | '30day' | 'alltime';
  highlight?: boolean;
}
```

**Key logic:**
- Rank 1-3: render `<RankMedal rank={entry.rank} />` instead of rank number
- Rank 4+: render `<span>{entry.rank}</span>` in gray
- Points: `+${points}` for period boards, `${points}` (no prefix) for all-time
- `highlight={true}` → `bg-blue-50` (for "Your rank" row)
- Uses existing `<Avatar>` component with `level` prop

**Implementation per UI_SPEC:**
```tsx
<div className={`flex items-center gap-3 px-4 py-2.5 ${highlight ? 'bg-blue-50' : 'hover:bg-gray-50'}`}>
  <div className="flex w-6 shrink-0 items-center justify-center">
    {entry.rank <= 3 ? <RankMedal rank={entry.rank as 1|2|3} /> : <span className="text-sm font-medium text-gray-400">{entry.rank}</span>}
  </div>
  <Avatar src={entry.avatar_url} alt={entry.display_name} size="sm" fallback={entry.display_name} level={entry.level} />
  <span className="min-w-0 flex-1 truncate text-sm font-medium text-gray-900">{entry.display_name}</span>
  <span className="shrink-0 text-sm font-semibold text-gray-700">
    {period !== 'alltime' ? `+${entry.points}` : entry.points}
  </span>
</div>
```

**Tests:**
- Renders medal for top 3
- Renders rank number for rank 4+
- Shows + prefix for period boards, no prefix for all-time
- Applies highlight class when `highlight={true}`
- Truncates long names

---

### Task 13: YourRankSection Component

**Owner:** frontend
**Depends on:** T12

**Files:**
- Create: `frontend/src/features/gamification/components/YourRankSection.tsx`
- Create: `frontend/src/features/gamification/components/YourRankSection.test.tsx`

**What to build:**
A separator with "Your rank" label centered between two horizontal lines, followed by a highlighted `LeaderboardRow`.

**Props:**
```typescript
interface YourRankSectionProps {
  entry: LeaderboardEntry;
  period: '7day' | '30day' | 'alltime';
}
```

**Structure per UI_SPEC:**
```tsx
<div>
  <div className="flex items-center gap-2 px-4 py-2">
    <div className="h-px flex-1 bg-gray-200" />
    <span className="text-xs font-medium uppercase tracking-wide text-gray-400">Your rank</span>
    <div className="h-px flex-1 bg-gray-200" />
  </div>
  <LeaderboardRow entry={entry} period={period} highlight />
</div>
```

**Tests:**
- Renders "Your rank" label
- Renders a highlighted LeaderboardRow
- Passes correct period through

---

### Task 14: LeaderboardPanel Component

**Owner:** frontend
**Depends on:** T11, T12, T13

**Files:**
- Create: `frontend/src/features/gamification/components/LeaderboardPanel.tsx`
- Create: `frontend/src/features/gamification/components/LeaderboardPanel.test.tsx`

**What to build:**
White card containing panel header, list of `LeaderboardRow` entries, optional `YourRankSection`, and loading/empty/error states.

**Props:**
```typescript
interface LeaderboardPanelProps {
  title: string;
  entries: LeaderboardEntry[];
  yourRank: LeaderboardEntry | null;
  period: '7day' | '30day' | 'alltime';
  isLoading?: boolean;
  error?: Error | null;
}
```

**Structure per UI_SPEC:**
```tsx
<div className="rounded-lg border border-gray-200 bg-white">
  <div className="border-b border-gray-100 px-4 py-3">
    <h3 className="text-sm font-semibold text-gray-700">{title}</h3>
  </div>
  {isLoading ? (skeleton rows) : error ? (error message) : entries.length === 0 ? (empty message) : (
    <>
      <div className="divide-y divide-gray-50">
        {entries.map(e => <LeaderboardRow key={e.user_id} entry={e} period={period} />)}
      </div>
      {yourRank && <YourRankSection entry={yourRank} period={period} />}
    </>
  )}
</div>
```

**Tests:**
- Renders header title
- Renders correct number of rows
- Shows YourRankSection when `yourRank` is not null
- Hides YourRankSection when `yourRank` is null
- Shows skeleton during loading
- Shows empty message when no entries
- Shows error message on error

---

### Task 15a: LeaderboardProfileCard Component

**Owner:** frontend
**Depends on:** none

**Files:**
- Create: `frontend/src/features/gamification/components/LeaderboardProfileCard.tsx`
- Create: `frontend/src/features/gamification/components/LeaderboardProfileCard.test.tsx`

**What to build:**
Profile card showing the current member's avatar (with level badge), name, level label, and points to level up. Displayed in the top-left of the leaderboards page.

**Props:**
```typescript
interface LeaderboardProfileCardProps {
  avatarUrl: string | null;
  displayName: string;
  level: number;
  levelName: string;
  pointsToNextLevel: number | null;
  isMaxLevel: boolean;
}
```

**Structure per UI_SPEC:**
```tsx
<div className="flex flex-col items-center rounded-lg border border-gray-200 bg-white p-6">
  <Avatar src={avatarUrl} alt={displayName} size="lg" fallback={displayName} level={level} />
  <h2 className="mt-3 text-lg font-bold text-gray-900">{displayName}</h2>
  <p className="mt-1 text-sm font-medium text-gray-600">Level {level} - {levelName}</p>
  {!isMaxLevel && pointsToNextLevel != null && (
    <p className="mt-1 text-xs text-gray-400">{pointsToNextLevel} points to level up</p>
  )}
</div>
```

**Tests:**
- Renders avatar, name, level label
- Shows "points to level up" when not max level
- Hides "points to level up" when max level

---

### Task 15b: BDD Test Fixtures (conftest additions)

**Owner:** testing
**Depends on:** none

**Files:**
- Modify: `tests/features/gamification/conftest.py`

**What to build:**
Add leaderboard-specific fixtures to the existing conftest:

1. **`leaderboard_handler` fixture** — creates `GetLeaderboardsHandler` from `mp_repo`
2. **`award_points_for_member` helper fixture** — factory that awards N points to a given member via `AwardPointsHandler` (creating the member_points record and point_transactions with controlled timestamps)
3. **`create_point_transaction_at` helper fixture** — directly inserts a `PointTransactionModel` with a specific `created_at` timestamp (needed for testing rolling windows — awards via handler always use `NOW()`)

**Critical detail for rolling window tests:**
The BDD scenarios like "earned 50 points 8 days ago" require inserting transactions with past timestamps. The `AwardPointsHandler` always sets `created_at=now()`. The test fixture must bypass the handler and insert `PointTransactionModel` rows directly with controlled timestamps, then update `MemberPointsModel.total_points` accordingly.

**Implementation notes:**
- Follow existing fixture patterns in the conftest (factory fixtures as async callables)
- Import `PointTransactionModel` and `MemberPointsModel` for direct DB insertion
- Import `datetime`, `timedelta` for timestamp manipulation

---

### Task 16: Enhanced LeaderboardsPage

**Owner:** frontend
**Depends on:** T9, T14, T15a

**Files:**
- Modify: `frontend/src/pages/LeaderboardsPage.tsx`

**What to build:**
Replace the current stub page (which only shows `LevelDefinitionsGrid`) with the full layout:

1. Top section: `LeaderboardProfileCard` (left) + `LevelDefinitionsGrid` (right) in a grid
2. "Last updated" timestamp below the grid
3. Three `LeaderboardPanel` components side-by-side

**Structure per UI_SPEC:**
```tsx
<div className="mx-auto max-w-[1100px] px-4 py-8">
  {/* Top section */}
  <div className="grid grid-cols-1 gap-6 md:grid-cols-[280px_1fr]">
    <LeaderboardProfileCard ... />
    <LevelDefinitionsGrid ... />
  </div>

  {/* Timestamp */}
  {data?.last_updated && (
    <p className="mt-4 text-sm text-gray-500">Last updated: {formatTimestamp(data.last_updated)}</p>
  )}

  {/* Three panels */}
  <div className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-3">
    <LeaderboardPanel title="Leaderboard (7-day)" entries={...} yourRank={...} period="7day" ... />
    <LeaderboardPanel title="Leaderboard (30-day)" entries={...} yourRank={...} period="30day" ... />
    <LeaderboardPanel title="Leaderboard (All-time)" entries={...} yourRank={...} period="alltime" ... />
  </div>
</div>
```

**Data sources:**
- `useLeaderboards()` — for ranking data (three periods + last_updated)
- `useLevelDefinitions()` — for level definitions grid (already used in current stub)
- `useMemberLevel(currentUserId)` — for profile card (level name, points to next level)
- `useAuth()` — for current user info (avatar, display name, user ID)

**Timestamp formatting:**
Use `Intl.DateTimeFormat` or a simple helper to format ISO string to "Feb 18th 2026 2:11pm" style. Check if `date-fns` is available; if not, use `Intl.DateTimeFormat`.

**Implementation notes:**
- Import from existing hooks (`useLevelDefinitions`, `useMemberLevel`) and the new `useLeaderboards`
- Preserve the existing `MembersLayout` wrapper (header + tabs) — the page is rendered inside it per `App.tsx`
- Handle combined loading state: show full skeleton layout if either hook is loading
- The existing page import in `App.tsx` and route definition already work — no route changes needed

---

### Task 17: BDD Step Definitions + Final Verification

**Owner:** testing
**Depends on:** T3, T4, T6 (all backend), T16 (frontend page)

**Files:**
- Create: `tests/features/gamification/test_leaderboards.py`

**What to build:**
Implement pytest-bdd step definitions for all 13 Phase 1 BDD scenarios, plus skip markers for the 4 Phase 2 scenarios.

**Step definitions needed:**

1. **Background steps:** "Given a community exists", "And the community has default level configuration", "And the following members exist in the community" — reuse/extend existing conftest fixtures

2. **Given steps for point transactions:**
   - "Given the following point transactions occurred in the last 7 days" — use `award_points_for_member` fixture
   - "Given {member} earned {N} points between {X} and {Y} days ago" — use `create_point_transaction_at` with past timestamps
   - "Given {member} has a total of {N} accumulated points" — directly set `MemberPointsModel.total_points`
   - "Given {member} earned {N} points {X} days ago" — use `create_point_transaction_at`
   - "Given 10 members each earned between 1 and 10 points" — bulk creation loop
   - "Given {member} earned {N} points from likes/had {N} points deducted" — insert positive and negative transactions

3. **When steps:**
   - "When {member} requests the {period} leaderboard" — call `GetLeaderboardsHandler.handle()` with the appropriate query
   - "When {member} requests the sidebar leaderboard widget" — skip (Phase 2)

4. **Then steps:**
   - "Then the response contains {N} ranked members" — assert `len(result.entries) == N`
   - "Then rank {N} is {member} with {points} points" — assert entry at index N-1
   - "Then ranks 1, 2, 3 have medal indicators" — assert entries[0..2].rank <= 3 (medals are a frontend concern, but verify rank values)
   - "Then each entry includes the member's level badge" — assert `entry.level` is present
   - "Then {member} appears at rank {N} with {points} points in the {period} leaderboard" — assert correct entry
   - "Then the response includes a 'your_rank' entry for {member}" — assert `result.your_rank is not None`
   - "Then the response does not include a separate 'your_rank' entry" — assert `result.your_rank is None`
   - "Then {member}'s rank is {N}" — assert `result.your_rank.rank == N`
   - "Then {member}'s points for the period are {N}" — assert `result.your_rank.points == N`
   - "Then rank {N} displays '+{points}' as the point value" — frontend formatting concern, verify `entry.points == N`
   - "Then {member}'s {period} points are {N}" — assert points for specific member

5. **Skipped scenarios (Phase 2):**
   - Mark widget, timestamp, and security scenarios with `@pytest.mark.skip(reason="Phase 2: ...")`

**Testing approach:**
- Tests exercise the handler directly (application-level testing), not via HTTP API
- This matches the existing pattern in `test_points.py`
- Use the conftest fixtures from Task 15b for data setup

**Verification:**
```bash
eval "$(pyenv init -)" && eval "$(pyenv virtualenv-init -)" && pyenv activate koulu
pytest tests/features/gamification/test_leaderboards.py -v
# Expected: 13 passed, 4 skipped, 0 failed

./scripts/verify.sh
# Expected: All checks pass
```

---

## Summary

| # | Task | Owner | Depends On |
|---|------|-------|------------|
| T1 | LeaderboardPeriod value object | backend | none |
| T2 | Repository interface extension | backend | T1 |
| T3 | Repository implementation (SQL queries) | backend | T2 |
| T4 | GetLeaderboards query handler | backend | T2 |
| T5 | API response schemas | backend | none |
| T6 | API endpoint + DI wiring | backend | T4, T5 |
| T7 | TypeScript types | frontend | none |
| T8 | API function (getLeaderboards) | frontend | T7 |
| T9 | useLeaderboards hook | frontend | T8 |
| T10 | RankMedal component | frontend | none |
| T11 | LeaderboardRowSkeleton component | frontend | none |
| T12 | LeaderboardRow component | frontend | T10 |
| T13 | YourRankSection component | frontend | T12 |
| T14 | LeaderboardPanel component | frontend | T11, T12, T13 |
| T15a | LeaderboardProfileCard component | frontend | none |
| T15b | BDD test fixtures (conftest) | testing | none |
| T16 | Enhanced LeaderboardsPage | frontend | T9, T14, T15a |
| T17 | BDD step definitions + verification | testing | T3, T4, T6, T15b |
