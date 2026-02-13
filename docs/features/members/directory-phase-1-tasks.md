# Member Directory Phase 1 -- Task Plan

> **For Claude:** Use /implement-feature members/directory --phase=1 to execute this plan.

**Phase goal:** Deliver a working member directory page where users browse community members in a vertical list with infinite scroll (default sort: most recent first).
**Files to create/modify:** ~20
**BDD scenarios to enable:** 6
**Estimated time:** 3-4 hours
**Task count:** 9

### Dependency Graph

```
Task 1 (App Layer) ──→ Task 2 (Domain) ──→ Task 3 (Infra) ──┐
       │                                                      ├──→ Task 5 (BDD Tests) ──→ Task 9 (Verify)
       └──→ Task 4 (API) ───────────────────────────────────┘                                 ↑
                                                                                               │
Task 6 (FE Types) ──→ Task 7 (FE Card) ──→ Task 8 (FE Page) ────────────────────────────────┘
```

### Parallel Execution Summary

| Batch | Tasks | Mode | Rationale |
|-------|-------|------|-----------|
| 1 | Task 1, Task 6 | **Parallel** | Both independent; app layer and frontend types don't share files |
| 2 | Task 2, Task 4, Task 7 | **Parallel** | Deps met (2←1, 4←1, 7←6); no file overlap across layers |
| 3 | Task 3, Task 8 | **Parallel** | Deps met (3←2, 8←7); backend infra and frontend page don't share files |
| 4 | Task 5 | Sequential | BDD tests need full backend stack (deps: 3, 4) |
| 5 | Task 9 | Sequential | Final verification needs everything (deps: 5, 8) |

**Sequential execution:** 9 tasks
**Parallel execution:** 5 batches (estimated ~40% time savings)

---

## Task 1: Application Layer — Query + DTO + Handler

**Purpose:** Define the query object, result DTOs, and handler that orchestrates the directory listing.

**Depends on:** none

**Files:**
- Create: `src/community/application/queries/list_members_query.py`
- Create: `src/community/application/dtos/__init__.py`
- Create: `src/community/application/dtos/member_directory_entry.py`
- Create: `src/community/application/handlers/list_members_handler.py`
- Modify: `src/community/application/queries.py` (add ListMembersQuery import)
- Modify: `src/community/application/handlers/__init__.py` (add exports)

**Step 1: Create the query object**

Create `src/community/application/queries/list_members_query.py`:

```python
"""List members query."""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class ListMembersQuery:
    """Query to list members of a community directory."""

    community_id: UUID
    requester_id: UUID
    sort: str = "most_recent"
    limit: int = 20
    cursor: str | None = None
```

Also add to `src/community/application/queries.py`:
```python
from src.community.application.queries.list_members_query import ListMembersQuery
```

**Step 2: Create the DTO**

Create `src/community/application/dtos/__init__.py`:
```python
"""Community application DTOs."""

from src.community.application.dtos.member_directory_entry import (
    MemberDirectoryEntry,
    MemberDirectoryResult,
)

__all__ = ["MemberDirectoryEntry", "MemberDirectoryResult"]
```

Create `src/community/application/dtos/member_directory_entry.py`:

```python
"""Member directory DTOs."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class MemberDirectoryEntry:
    """Flat DTO combining membership + profile data for the directory."""

    user_id: UUID
    display_name: str | None
    avatar_url: str | None
    role: str
    bio: str | None
    joined_at: datetime


@dataclass
class MemberDirectoryResult:
    """Result of a directory listing query with pagination."""

    items: list[MemberDirectoryEntry]
    total_count: int
    cursor: str | None
    has_more: bool
```

**Step 3: Create the handler**

Create `src/community/application/handlers/list_members_handler.py`:

Follow the `GetFeedHandler` pattern exactly:
- Constructor takes `IMemberRepository`
- `handle(query: ListMembersQuery) -> MemberDirectoryResult`
- Check membership first (raise `NotCommunityMemberError` if not a member)
- Call `self._member_repository.list_directory(...)` with `limit + 1` for has_more detection
- Call `self._member_repository.count_directory(...)` for total_count
- Build next cursor using base64-encoded JSON offset (same pattern as GetFeedHandler)
- Log with structlog at entry/exit

**Step 4: Export from handlers `__init__.py`**

Add to `src/community/application/handlers/__init__.py`:
```python
from src.community.application.handlers.list_members_handler import (
    ListMembersHandler,
)
```
And add `"ListMembersHandler"` to `__all__`.

**Step 5: Commit**

```bash
git add src/community/application/queries/ src/community/application/dtos/ \
  src/community/application/handlers/list_members_handler.py \
  src/community/application/queries.py \
  src/community/application/handlers/__init__.py
git commit -m "feat(members): add ListMembersQuery, DTOs, and ListMembersHandler"
```

---

## Task 2: Domain Layer — Extend IMemberRepository Interface

**Purpose:** Add `list_directory()` and `count_directory()` abstract methods to the repository interface.

**Depends on:** Task 1

**Files:**
- Modify: `src/community/domain/repositories/member_repository.py`

**Step 1: Add the new abstract methods**

Add to `IMemberRepository` class (after `list_by_community`):

```python
from src.community.application.dtos.member_directory_entry import MemberDirectoryEntry
```

Wait — the domain layer should NOT import from the application layer. Instead, the repository interface should return a generic type or the handler should call a separate method.

**Corrected approach:** The repository interface returns `MemberDirectoryEntry` DTOs. Since this is a read-only query that returns a projection (not a domain entity), the DTO can live at the application level but be referenced from the repository interface. However, to keep the domain layer clean, we'll have the repository return `MemberDirectoryEntry` objects that are defined in the application layer — this is acceptable for CQRS query-side repositories.

**Alternative (cleaner):** Define the new methods to accept and return simple types. The handler will construct DTOs. But the TDD says the repository returns flat DTOs directly from the JOIN.

**Chosen approach:** Add the methods to the infrastructure implementation directly and have the handler call them through the concrete type. But this breaks hexagonal architecture.

**Final decision:** Add `list_directory` and `count_directory` to `IMemberRepository` with the DTO import. This is a pragmatic trade-off documented in the TDD — the directory is a read-only query concern that crosses context boundaries at the infrastructure level. The DTO is a simple data holder, not business logic.

Add to `src/community/domain/repositories/member_repository.py`:

```python
@abstractmethod
async def list_directory(
    self,
    community_id: CommunityId,
    sort: str = "most_recent",
    limit: int = 20,
    offset: int = 0,
) -> list["MemberDirectoryEntry"]:
    """
    List community members with profile data for the directory view.

    Returns flat DTOs joining membership + profile data.
    """
    ...

@abstractmethod
async def count_directory(
    self,
    community_id: CommunityId,
) -> int:
    """Count active members in a community directory."""
    ...
```

Use `from __future__ import annotations` at top of file for forward reference, and add the import inside a `TYPE_CHECKING` block:

```python
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.community.application.dtos.member_directory_entry import MemberDirectoryEntry
```

**Step 2: Commit**

```bash
git add src/community/domain/repositories/member_repository.py
git commit -m "feat(members): extend IMemberRepository with list_directory and count_directory"
```

---

## Task 3: Infrastructure Layer — Implement Repository Methods with JOIN

**Purpose:** Implement `list_directory()` and `count_directory()` in `SqlAlchemyMemberRepository` with a SQL JOIN to the profiles table.

**Depends on:** Task 2

**Files:**
- Modify: `src/community/infrastructure/persistence/member_repository.py`

**Step 1: Implement the methods**

Add imports:
```python
from sqlalchemy import func as sa_func
from src.community.application.dtos.member_directory_entry import MemberDirectoryEntry
from src.identity.infrastructure.persistence.models import ProfileModel
```

Implement `list_directory`:
```python
async def list_directory(
    self,
    community_id: CommunityId,
    sort: str = "most_recent",
    limit: int = 20,
    offset: int = 0,
) -> list[MemberDirectoryEntry]:
    """List community members with profile data via JOIN."""
    # Build base query: community_members LEFT JOIN profiles
    query = (
        select(
            CommunityMemberModel.user_id,
            CommunityMemberModel.role,
            CommunityMemberModel.joined_at,
            ProfileModel.display_name,
            ProfileModel.avatar_url,
            ProfileModel.bio,
        )
        .outerjoin(
            ProfileModel,
            CommunityMemberModel.user_id == ProfileModel.user_id,
        )
        .where(
            CommunityMemberModel.community_id == community_id.value,
            CommunityMemberModel.is_active.is_(True),
        )
    )

    # Sorting
    if sort == "alphabetical":
        query = query.order_by(ProfileModel.display_name.asc().nulls_last())
    else:  # most_recent (default)
        query = query.order_by(CommunityMemberModel.joined_at.desc())

    # Pagination
    query = query.offset(offset).limit(limit)

    result = await self._session.execute(query)
    rows = result.all()

    return [
        MemberDirectoryEntry(
            user_id=row.user_id,
            display_name=row.display_name,
            avatar_url=row.avatar_url,
            role=row.role.lower(),
            bio=row.bio,
            joined_at=row.joined_at,
        )
        for row in rows
    ]
```

Implement `count_directory`:
```python
async def count_directory(
    self,
    community_id: CommunityId,
) -> int:
    """Count active members in a community."""
    result = await self._session.execute(
        select(sa_func.count())
        .select_from(CommunityMemberModel)
        .where(
            CommunityMemberModel.community_id == community_id.value,
            CommunityMemberModel.is_active.is_(True),
        )
    )
    return result.scalar_one()
```

**Step 2: Commit**

```bash
git add src/community/infrastructure/persistence/member_repository.py
git commit -m "feat(members): implement list_directory with SQL JOIN to profiles"
```

---

## Task 4: API Layer — Schemas + Endpoint + Dependencies

**Purpose:** Add the API endpoint `GET /community/members` with request validation and response serialization.

**Depends on:** Task 1

**Files:**
- Modify: `src/community/interface/api/schemas.py` (add response schemas)
- Modify: `src/community/interface/api/dependencies.py` (add handler dependency)
- Modify: `src/community/interface/api/member_controller.py` (add endpoint)

**Step 1: Add schemas**

Add to `src/community/interface/api/schemas.py`:

```python
# ============================================================================
# Member Directory Schemas
# ============================================================================


class MemberDirectoryItemResponse(BaseModel):
    """Single member entry in the directory."""

    user_id: UUID
    display_name: str | None
    avatar_url: str | None
    role: str
    bio: str | None
    joined_at: datetime


class MemberDirectoryResponse(BaseModel):
    """Paginated member directory response."""

    items: list[MemberDirectoryItemResponse]
    total_count: int
    cursor: str | None
    has_more: bool
```

**Step 2: Add handler dependency**

Add to `src/community/interface/api/dependencies.py`:

Import the handler:
```python
from src.community.application.handlers import ListMembersHandler
```

Add factory function:
```python
def get_list_members_handler(
    member_repo: MemberRepositoryDep,
) -> ListMembersHandler:
    """Get list members handler."""
    return ListMembersHandler(
        member_repository=member_repo,
    )
```

Add typed dependency:
```python
ListMembersHandlerDep = Annotated[ListMembersHandler, Depends(get_list_members_handler)]
```

**Step 3: Add endpoint to member_controller.py**

Add to `src/community/interface/api/member_controller.py`:

```python
from src.community.application.queries.list_members_query import ListMembersQuery
from src.community.domain.exceptions import NotCommunityMemberError
from src.community.interface.api.dependencies import ListMembersHandlerDep
from src.community.interface.api.schemas import MemberDirectoryItemResponse, MemberDirectoryResponse


@router.get(
    "/members",
    response_model=MemberDirectoryResponse,
    responses={
        401: {"description": "Not authenticated"},
        403: {"description": "Not a community member"},
    },
)
async def list_members(
    current_user_id: CurrentUserIdDep,
    community_id: DefaultCommunityIdDep,
    handler: ListMembersHandlerDep,
    sort: str = "most_recent",
    limit: int = 20,
    cursor: str | None = None,
) -> MemberDirectoryResponse:
    """List community members in the directory."""
    try:
        query = ListMembersQuery(
            community_id=community_id,
            requester_id=current_user_id,
            sort=sort,
            limit=limit,
            cursor=cursor,
        )
        result = await handler.handle(query)
        return MemberDirectoryResponse(
            items=[
                MemberDirectoryItemResponse(
                    user_id=entry.user_id,
                    display_name=entry.display_name,
                    avatar_url=entry.avatar_url,
                    role=entry.role,
                    bio=entry.bio,
                    joined_at=entry.joined_at,
                )
                for entry in result.items
            ],
            total_count=result.total_count,
            cursor=result.cursor,
            has_more=result.has_more,
        )
    except NotCommunityMemberError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this community",
        )
```

**Step 4: Verify import exists for `ListMembersHandlerDep`**

In the dependency import block at the top of `member_controller.py`, add:
```python
from src.community.interface.api.dependencies import (
    CurrentUserIdDep,
    ListMembersHandlerDep,
    MemberRepositoryDep,
    SessionDep,
)
```

**Step 5: Commit**

```bash
git add src/community/interface/api/schemas.py \
  src/community/interface/api/dependencies.py \
  src/community/interface/api/member_controller.py
git commit -m "feat(members): add GET /community/members endpoint"
```

---

## Task 5: BDD Test Infrastructure — Conftest + Step Definitions

**Purpose:** Create test fixtures and step definitions for the 6 Phase 1 BDD scenarios.

**Depends on:** Task 3, Task 4

**Files:**
- Create: `tests/features/members/__init__.py`
- Create: `tests/features/members/step_defs/__init__.py`
- Create: `tests/features/members/conftest.py`
- Create: `tests/features/members/step_defs/test_directory.py`

**Step 1: Create package init files**

Create empty `__init__.py` files for `tests/features/members/` and `tests/features/members/step_defs/`.

**Step 2: Create conftest.py**

Create `tests/features/members/conftest.py` following the pattern from `tests/features/community/conftest.py`. Provide factory fixtures for:
- `create_community` — reuse or create
- `create_member_with_profile` — creates a user + profile + community membership in one call
  - Parameters: `community_id`, `display_name`, `role`, `bio`, `avatar_url`, `joined_days_ago`
  - Creates: UserModel, ProfileModel, CommunityMemberModel with correct joined_at offset

This fixture is key because the BDD Background requires creating 5 members with specific display names, roles, bios, and join date offsets.

**Step 3: Create step definitions**

Create `tests/features/members/step_defs/test_directory.py`:

Structure with `@scenario` decorators for the 6 enabled scenarios:
```python
@scenario("../../members/directory.feature", "View member directory as a community member")
def test_view_member_directory() -> None:
    pass

@scenario("../../members/directory.feature", "Member directory shows correct member count")
def test_member_directory_shows_count() -> None:
    pass

@scenario("../../members/directory.feature", "Sort members by most recent")
def test_sort_by_most_recent() -> None:
    pass

@scenario("../../members/directory.feature", "Paginated member loading")
def test_paginated_member_loading() -> None:
    pass

@scenario("../../members/directory.feature", "Load second page of members")
def test_load_second_page() -> None:
    pass

@scenario("../../members/directory.feature", "Load final page of members")
def test_load_final_page() -> None:
    pass
```

Add skip markers for the remaining 17 scenarios:
```python
@pytest.mark.skip(reason="Phase 2: Requires search query param")
@scenario("../../members/directory.feature", "Search members by name")
def test_search_members_by_name() -> None:
    pass
# ... etc for all 17
```

Implement `@given`, `@when`, `@then` step functions:
- Background steps: create community, create 5 members with profiles
- `@given("the user is an authenticated member")` — login as one of the members, get JWT token
- `@when("the user requests the member directory")` — `GET /api/v1/community/members`
- `@then("the directory should return a list of active members")` — assert items in response
- `@then("each member entry should include display name, avatar URL, role, bio, and join date")` — assert all fields present
- `@then("the members should be ordered by join date descending by default")` — verify order
- `@then("the total member count should be 5")` — assert total_count
- Pagination steps: create 45 members, request with limit=20, verify has_more + cursor

**Step 4: Run tests**

```bash
pytest tests/features/members/step_defs/test_directory.py -v
```

Expected: 6 passed, 17 skipped, 0 failed

**Step 5: Commit**

```bash
git add tests/features/members/
git commit -m "test(members): add BDD step definitions for Phase 1 directory scenarios"
```

---

## Task 6: Frontend — Types + API Client + Hook

**Purpose:** Create the TypeScript types, API client function, and React Query hook for fetching members.

**Depends on:** none

**Files:**
- Create: `frontend/src/features/members/types/members.ts`
- Create: `frontend/src/features/members/api/memberApi.ts`
- Create: `frontend/src/features/members/api/index.ts`
- Create: `frontend/src/features/members/hooks/useMembers.ts`
- Create: `frontend/src/features/members/hooks/index.ts`

**Step 1: Create types**

Create `frontend/src/features/members/types/members.ts`:

```typescript
export interface DirectoryMember {
  user_id: string;
  display_name: string | null;
  avatar_url: string | null;
  role: 'admin' | 'moderator' | 'member';
  bio: string | null;
  joined_at: string;
}

export interface MembersQueryParams {
  sort?: 'most_recent' | 'alphabetical';
  limit?: number;
  cursor?: string;
}

export interface MembersResponse {
  items: DirectoryMember[];
  total_count: number;
  cursor: string | null;
  has_more: boolean;
}
```

**Step 2: Create API client**

Create `frontend/src/features/members/api/memberApi.ts`:

```typescript
import { apiClient } from '@/lib/api-client';
import type { MembersQueryParams, MembersResponse } from '../types/members';

export async function getMembers(params?: MembersQueryParams): Promise<MembersResponse> {
  const response = await apiClient.get<MembersResponse>('/community/members', { params });
  return response.data;
}
```

Create `frontend/src/features/members/api/index.ts`:
```typescript
export { getMembers } from './memberApi';
```

**Step 3: Create hook**

Create `frontend/src/features/members/hooks/useMembers.ts` following `usePosts` pattern exactly:

```typescript
import { useInfiniteQuery } from '@tanstack/react-query';
import { getMembers } from '../api';
import type { DirectoryMember, MembersQueryParams } from '../types/members';

const MEMBERS_KEY = ['members'] as const;

export interface UseMembersResult {
  members: DirectoryMember[] | undefined;
  totalCount: number;
  isLoading: boolean;
  error: Error | null;
  hasMore: boolean;
  isFetchingNextPage: boolean;
  fetchNextPage: () => void;
}

export function useMembers(params?: MembersQueryParams): UseMembersResult {
  const {
    data,
    isLoading,
    error,
    hasNextPage,
    isFetchingNextPage,
    fetchNextPage,
  } = useInfiniteQuery({
    queryKey: [...MEMBERS_KEY, params],
    queryFn: ({ pageParam }) => {
      const queryParams: MembersQueryParams = { ...params };
      if (pageParam != null) {
        queryParams.cursor = pageParam;
      }
      return getMembers(queryParams);
    },
    initialPageParam: null as string | null,
    getNextPageParam: (lastPage) =>
      lastPage.has_more ? lastPage.cursor : undefined,
    staleTime: 5 * 60 * 1000,
    retry: 1,
  });

  const members = data?.pages.flatMap((page) => page.items);
  const totalCount = data?.pages[0]?.total_count ?? 0;

  return {
    members,
    totalCount,
    hasMore: hasNextPage ?? false,
    isLoading,
    isFetchingNextPage,
    fetchNextPage: () => void fetchNextPage(),
    error: error ?? null,
  };
}
```

Create `frontend/src/features/members/hooks/index.ts`:
```typescript
export { useMembers } from './useMembers';
export type { UseMembersResult } from './useMembers';
```

**Step 4: Commit**

```bash
git add frontend/src/features/members/
git commit -m "feat(members): add frontend types, API client, and useMembers hook"
```

---

## Task 7: Frontend — MemberCard + MemberCardSkeleton Components

**Purpose:** Create the member card component matching the UI_SPEC design.

**Depends on:** Task 6

**Files:**
- Create: `frontend/src/features/members/components/MemberCard.tsx`
- Create: `frontend/src/features/members/components/MemberCardSkeleton.tsx`

**Step 1: Create MemberCard**

Follow the UI_SPEC exactly. Key details:
- Reuse `Avatar` component with `size="lg"` (48x48)
- Role badge: yellow for admin, blue for moderator, hidden for member
- Bio truncated with `line-clamp-2`, "No bio" placeholder if null
- Join date in relative format ("Joined 3 months ago")
- Entire card clickable → navigates to `/profile/:userId`
- Hover: `hover:shadow-sm`
- `data-testid="member-card"` for E2E testing

Use `useNavigate` from react-router-dom for card click navigation.

Create a simple `relativeDate` helper inside the component file (or as a utility):
```typescript
function relativeDate(dateStr: string): string {
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffDays === 0) return 'today';
  if (diffDays === 1) return '1 day ago';
  if (diffDays < 30) return `${diffDays} days ago`;
  const diffMonths = Math.floor(diffDays / 30);
  if (diffMonths === 1) return '1 month ago';
  if (diffMonths < 12) return `${diffMonths} months ago`;
  const diffYears = Math.floor(diffDays / 365);
  if (diffYears === 1) return '1 year ago';
  return `${diffYears} years ago`;
}
```

**Step 2: Create MemberCardSkeleton**

Follow UI_SPEC skeleton pattern: `animate-pulse`, gray placeholders for avatar, name, bio, date.

**Step 3: Commit**

```bash
git add frontend/src/features/members/components/MemberCard.tsx \
  frontend/src/features/members/components/MemberCardSkeleton.tsx
git commit -m "feat(members): add MemberCard and MemberCardSkeleton components"
```

---

## Task 8: Frontend — MemberList + MembersPage + Route

**Purpose:** Create the list container with infinite scroll, the page layout, and wire into routing.

**Depends on:** Task 7

**Files:**
- Create: `frontend/src/features/members/components/MemberList.tsx`
- Create: `frontend/src/features/members/components/index.ts`
- Create: `frontend/src/pages/MembersPage.tsx`
- Modify: `frontend/src/pages/index.ts` (add export)
- Modify: `frontend/src/App.tsx` (add route + Members tab)

**Step 1: Create MemberList**

Implements infinite scroll with `IntersectionObserver` on a sentinel div:
- Maps over members array, renders `MemberCard` for each
- Shows `MemberCardSkeleton` (3x) during initial loading
- Shows loading spinner during `isFetchingNextPage`
- Shows sentinel `<div ref={sentinelRef} />` at bottom
- Uses `useEffect` + `useRef` + `IntersectionObserver` to trigger `fetchNextPage`
- Card gap: `space-y-3`
- `data-testid="member-list"` for E2E testing

**Step 2: Create barrel export**

Create `frontend/src/features/members/components/index.ts`:
```typescript
export { MemberCard } from './MemberCard';
export { MemberCardSkeleton } from './MemberCardSkeleton';
export { MemberList } from './MemberList';
```

**Step 3: Create MembersPage**

Create `frontend/src/pages/MembersPage.tsx` following `HomePage` layout:

```tsx
import { useAuth } from '@/features/identity/hooks';
import { CommunitySidebar } from '@/features/community/components';
import { MemberList } from '@/features/members/components';
import { useMembers } from '@/features/members/hooks';
import { TabBar, UserDropdown } from '@/components';
import { AppHeader } from './components'; // or inline like HomePage

// Same APP_TABS but with Members added
const APP_TABS = [
  { label: 'Community', path: '/' },
  { label: 'Classroom', path: '/classroom' },
  { label: 'Members', path: '/members' },
];
```

Layout structure (matches UI_SPEC):
```tsx
<div className="min-h-screen bg-gray-50">
  <AppHeader />
  <TabBar tabs={APP_TABS} />
  <div className="mx-auto max-w-[1100px] px-4 py-6">
    <div className="grid grid-cols-1 gap-6 lg:grid-cols-[1fr_320px]">
      <main>
        <MemberList
          members={members}
          totalCount={totalCount}
          isLoading={isLoading}
          hasMore={hasMore}
          isFetchingNextPage={isFetchingNextPage}
          fetchNextPage={fetchNextPage}
          error={error}
        />
      </main>
      <aside className="hidden lg:block">
        <CommunitySidebar />
      </aside>
    </div>
  </div>
</div>
```

Note: `AppHeader` is defined inline in `App.tsx` currently. For the MembersPage, replicate the same pattern or extract `AppHeader` into a shared component. Match whichever approach causes the least disruption.

**Step 4: Add page export**

Add to `frontend/src/pages/index.ts`:
```typescript
export { MembersPage } from './MembersPage';
```

**Step 5: Add route + update tabs in App.tsx**

In `frontend/src/App.tsx`:

1. Import `MembersPage`:
```typescript
import { MembersPage } from '@/pages';
```

2. Update `APP_TABS` array:
```typescript
const APP_TABS = [
  { label: 'Community', path: '/' },
  { label: 'Classroom', path: '/classroom' },
  { label: 'Members', path: '/members' },
];
```

3. Add route (after classroom routes, before catch-all):
```tsx
<Route
  path="/members"
  element={
    <ProtectedRoute>
      <MembersPage />
    </ProtectedRoute>
  }
/>
```

**Step 6: Commit**

```bash
git add frontend/src/features/members/components/ \
  frontend/src/pages/MembersPage.tsx \
  frontend/src/pages/index.ts \
  frontend/src/App.tsx
git commit -m "feat(members): add MembersPage with infinite scroll and Members tab"
```

---

## Task 9: Final — Enable BDD Scenarios + Full Verification

**Depends on:** Task 5, Task 8

**Step 1: Verify all Phase 1 skip markers are removed**

Ensure the 6 enabled scenarios have NO skip markers. Verify the 17 skipped scenarios have correct Phase markers.

**Step 2: Run BDD tests**

```bash
pytest tests/features/members/step_defs/test_directory.py -v
```

Expected: 6 passed, 17 skipped, 0 failed

**Step 3: Run full verification**

```bash
./scripts/verify.sh
```

Expected: All checks pass (ruff, mypy, pytest, frontend build)

**Step 4: Run frontend build**

```bash
cd frontend && npm run typecheck && npm run build
```

**Step 5: Final commit**

```bash
git add -A
git commit -m "feat(members): complete Phase 1 — member directory with browse and pagination"
```

---

## Implementation Notes

**Patterns to match:**
- Handler: Follow `GetFeedHandler` (structlog, membership check, cursor building)
- Repository: Follow `SqlAlchemyMemberRepository.list_by_community()` but with JOIN
- API: Follow `post_controller.py` endpoint pattern (dependencies, error handling)
- Frontend hook: Follow `usePosts` exactly (useInfiniteQuery, flatMap, staleTime)
- Frontend page: Follow `HomePage` layout (AppHeader + TabBar + 2-column grid + CommunitySidebar)
- BDD tests: Follow `tests/features/community/conftest.py` fixtures and `test_feed.py` step patterns

**Key decisions:**
- LEFT JOIN (not INNER) to profiles — members without profiles must still appear
- Role stored as uppercase in DB (`MEMBER`, `ADMIN`) but returned lowercase in API (`member`, `admin`)
- Cursor uses base64-encoded JSON `{"offset": N}` — same as feed
- Frontend requests `limit + 1` is NOT done on frontend — backend handles it
- `total_count` comes from a separate COUNT query, not from `len(items)`
