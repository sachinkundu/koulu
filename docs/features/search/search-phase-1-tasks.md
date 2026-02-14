# Search Phase 1 — Task Plan

> **For Claude:** Use `/implement-feature search/search --phase=1` to execute this plan.

**Phase goal:** Deliver working member and post search with tabbed results — user can type a query in the header, press Enter, and see matching members or posts on a search results page.

**Files to create:** 17 (7 backend + 8 frontend + 1 migration + 1 test)
**Files to modify:** 7 (4 backend + 3 frontend)
**BDD scenarios to enable:** 11
**Estimated time:** 4-5 hours
**Task count:** 10

---

### Dependency Graph

```
Task 1 (Migration)
    │
    ├──────────────────────────────────┐
    │                                  │
Task 2 (App DTOs + Query + Interface)  │
    │                                  │
    ├──────────────┐                   │
    │              │                   │
Task 3 (Handler)  Task 4 (Repository)─┘
    │              │
    └──────┬───────┘
           │
Task 5 (API Layer)
           │                    Task 6 (FE Types + API + Hook) ─┐
           │                    Task 7 (FE SearchBar)           │
           │                    Task 8 (FE Result Cards)────────┤
           │                                                    │
           │                                        Task 9 (FE Page + Routing)
           │                                                    │
           └────────────────────────────────────────────────────┤
                                                                │
                                                    Task 10 (BDD Tests + Verify)
```

### Parallel Execution Summary

| Batch | Tasks | Mode | Rationale |
|-------|-------|------|-----------|
| 1 | Task 1, Task 2 | Parallel | Migration and app-layer types are independent |
| 2 | Task 3, Task 4 | Parallel | Handler and repository both depend on Task 2 but not each other |
| 3 | Task 5 | Sequential | API layer wires handler + repository |
| 4 | Task 6, Task 7, Task 8 | Parallel | Frontend types/API, SearchBar, and cards are independent |
| 5 | Task 9 | Sequential | Page assembles all frontend components |
| 6 | Task 10 | Sequential | BDD tests verify full stack |

**Sequential execution:** 6 batches
**With parallelism:** ~40% time savings on batches 1, 2, 4

---

### Task 1: Database Migration

**Depends on:** none

**What:** Add `search_vector` (TSVECTOR) columns to `profiles` and `posts` tables, add `username` column to `profiles`, create GIN indexes, create trigger functions for auto-updating search vectors, backfill existing rows.

**Why this matters:** PostgreSQL Full-Text Search requires pre-computed `tsvector` columns with GIN indexes for fast lookups. Triggers ensure the vector stays in sync with source data on every INSERT/UPDATE. The `username` column is needed because the BDD scenarios test searching by username (e.g., "bob-martinez") but no username field currently exists on profiles.

**Files:**
- Create: `alembic/versions/xxxx_add_search_vectors_and_username.py`

**Step 1: Generate migration**

```bash
cd /home/sachin/code/KOULU/cc_koulu
alembic revision --autogenerate -m "add search vectors and username to profiles and posts"
```

**Step 2: Write migration content**

The migration must:

1. Add `username` column (VARCHAR 100, nullable, unique) to `profiles`
2. Add `search_vector` column (TSVECTOR, nullable) to `profiles`
3. Add `search_vector` column (TSVECTOR, nullable) to `posts`
4. Create GIN index on `profiles.search_vector`
5. Create GIN index on `posts.search_vector`
6. Create index on `profiles.username` for ILIKE queries
7. Create trigger function `profiles_search_vector_update()` that computes:
   `to_tsvector('english', coalesce(display_name, '') || ' ' || coalesce(bio, ''))`
8. Create trigger function `posts_search_vector_update()` that computes:
   `to_tsvector('english', coalesce(title, '') || ' ' || coalesce(content, ''))`
9. Create triggers on `profiles` and `posts` for INSERT/UPDATE
10. Backfill existing rows: UPDATE profiles/posts SET search_vector = ...
11. Generate usernames for existing profiles: `lower(replace(display_name, ' ', '-')) || '-' || substr(user_id::text, 1, 4)`

Key SQL for triggers:
```sql
-- Profiles trigger function
CREATE OR REPLACE FUNCTION profiles_search_vector_update() RETURNS trigger AS $$
BEGIN
  NEW.search_vector := to_tsvector('english', coalesce(NEW.display_name, '') || ' ' || coalesce(NEW.bio, ''));
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER profiles_search_vector_trigger
  BEFORE INSERT OR UPDATE OF display_name, bio ON profiles
  FOR EACH ROW EXECUTE FUNCTION profiles_search_vector_update();

-- Posts trigger function
CREATE OR REPLACE FUNCTION posts_search_vector_update() RETURNS trigger AS $$
BEGIN
  NEW.search_vector := to_tsvector('english', coalesce(NEW.title, '') || ' ' || coalesce(NEW.content, ''));
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER posts_search_vector_trigger
  BEFORE INSERT OR UPDATE OF title, content ON posts
  FOR EACH ROW EXECUTE FUNCTION posts_search_vector_update();
```

**Downgrade** must:
- Drop triggers, then trigger functions, then indexes, then columns

**Step 3: Run migration**

```bash
alembic upgrade head
```

**Step 4: Verify migration applied**

```bash
# Check columns exist
psql -d koulu_dev -c "\d profiles" | grep -E "search_vector|username"
psql -d koulu_dev -c "\d posts" | grep search_vector
# Check indexes
psql -d koulu_dev -c "\di" | grep -E "gin|username"
```

---

### Task 2: Application Layer — DTOs, Query, and Repository Interface

**Depends on:** none

**What:** Create the search DTOs (result containers), the SearchQuery dataclass, and the ISearchRepository abstract interface. These are the contracts that the handler and repository implement against.

**Files:**
- Create: `src/community/application/dtos/search_results.py`
- Create: `src/community/application/queries/search_query.py`
- Create: `src/community/domain/repositories/search_repository.py`
- Modify: `src/community/application/dtos/__init__.py` (add exports)
- Modify: `src/community/application/queries/__init__.py` (add exports)
- Modify: `src/community/domain/repositories/__init__.py` (add exports)

**Step 1: Create search DTOs**

File: `src/community/application/dtos/search_results.py`

Pattern reference: `src/community/application/dtos/member_directory_entry.py`

```python
"""Search result DTOs."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class MemberSearchEntry:
    """Member search result entry."""

    user_id: UUID
    display_name: str | None
    username: str | None
    avatar_url: str | None
    role: str
    bio: str | None
    joined_at: datetime


@dataclass
class PostSearchEntry:
    """Post search result entry."""

    id: UUID
    title: str
    body_snippet: str
    author_name: str | None
    author_avatar_url: str | None
    category_name: str | None
    category_emoji: str | None
    created_at: datetime
    like_count: int
    comment_count: int


@dataclass
class SearchResult:
    """Combined search result with both-tab counts."""

    items: list[MemberSearchEntry] | list[PostSearchEntry]
    total_count: int
    member_count: int
    post_count: int
    has_more: bool
```

**Step 2: Create SearchQuery dataclass**

File: `src/community/application/queries/search_query.py`

```python
"""Search query definition."""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class SearchQuery:
    """Query to search members and posts."""

    community_id: UUID
    requester_id: UUID
    query: str
    search_type: str = "members"  # "members" or "posts"
    limit: int = 10
    offset: int = 0
```

**Step 3: Create ISearchRepository interface**

File: `src/community/domain/repositories/search_repository.py`

Pattern reference: `src/community/domain/repositories/member_repository.py`

```python
"""Search repository interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from src.community.domain.value_objects import CommunityId

if TYPE_CHECKING:
    from src.community.application.dtos.search_results import (
        MemberSearchEntry,
        PostSearchEntry,
    )


class ISearchRepository(ABC):
    """Interface for search operations using full-text search."""

    @abstractmethod
    async def search_members(
        self,
        community_id: CommunityId,
        query: str,
        limit: int = 10,
        offset: int = 0,
    ) -> list[MemberSearchEntry]:
        """Search community members by display name, username, or bio."""
        ...

    @abstractmethod
    async def count_members(
        self,
        community_id: CommunityId,
        query: str,
    ) -> int:
        """Count matching members."""
        ...

    @abstractmethod
    async def search_posts(
        self,
        community_id: CommunityId,
        query: str,
        limit: int = 10,
        offset: int = 0,
    ) -> list[PostSearchEntry]:
        """Search community posts by title or content."""
        ...

    @abstractmethod
    async def count_posts(
        self,
        community_id: CommunityId,
        query: str,
    ) -> int:
        """Count matching posts."""
        ...
```

**Step 4: Update `__init__.py` exports**

Add to `src/community/application/dtos/__init__.py`:
```python
from src.community.application.dtos.search_results import (
    MemberSearchEntry,
    PostSearchEntry,
    SearchResult,
)
```
And add to `__all__`.

Add to `src/community/application/queries/__init__.py`:
```python
from src.community.application.queries.search_query import SearchQuery
```
And add `"SearchQuery"` to `__all__`.

Add to `src/community/domain/repositories/__init__.py`:
```python
from src.community.domain.repositories.search_repository import ISearchRepository
```
And add `"ISearchRepository"` to `__all__`.

**Step 5: Verify imports**

```bash
python -c "from src.community.application.dtos import MemberSearchEntry, PostSearchEntry, SearchResult; print('DTOs OK')"
python -c "from src.community.application.queries import SearchQuery; print('Query OK')"
python -c "from src.community.domain.repositories import ISearchRepository; print('Interface OK')"
```

---

### Task 3: SearchHandler

**Depends on:** Task 2

**What:** Create the SearchHandler that orchestrates search: validates membership, sanitizes input, delegates to search repository, returns structured results.

**Files:**
- Create: `src/community/application/handlers/search_handler.py`
- Modify: `src/community/application/handlers/__init__.py` (add export)

**Step 1: Create SearchHandler**

File: `src/community/application/handlers/search_handler.py`

Pattern reference: `src/community/application/handlers/list_members_handler.py`

```python
"""Search query handler."""

import re

import structlog

from src.community.application.dtos.search_results import SearchResult
from src.community.application.queries.search_query import SearchQuery
from src.community.domain.exceptions import NotCommunityMemberError
from src.community.domain.repositories import IMemberRepository, ISearchRepository
from src.community.domain.value_objects import CommunityId
from src.identity.domain.value_objects import UserId

logger = structlog.get_logger()


class SearchHandler:
    """Handler for searching community members and posts."""

    def __init__(
        self,
        search_repository: ISearchRepository,
        member_repository: IMemberRepository,
    ) -> None:
        self._search_repository = search_repository
        self._member_repository = member_repository

    async def handle(self, query: SearchQuery) -> SearchResult:
        """Execute a search query."""
        logger.info(
            "search_attempt",
            community_id=str(query.community_id),
            requester_id=str(query.requester_id),
            query_preview=query.query[:3] + "..." if len(query.query) > 3 else query.query,
            search_type=query.search_type,
        )

        community_id = CommunityId(query.community_id)
        requester_id = UserId(query.requester_id)

        # Verify membership
        member = await self._member_repository.get_by_user_and_community(
            requester_id, community_id
        )
        if member is None:
            raise NotCommunityMemberError()

        # Sanitize query
        sanitized = self._sanitize_query(query.query)

        # Get both counts (always needed for tab labels)
        member_count = await self._search_repository.count_members(community_id, sanitized)
        post_count = await self._search_repository.count_posts(community_id, sanitized)

        # Fetch items for the active type
        if query.search_type == "posts":
            items = await self._search_repository.search_posts(
                community_id, sanitized, query.limit, query.offset
            )
            total_count = post_count
        else:
            items = await self._search_repository.search_members(
                community_id, sanitized, query.limit, query.offset
            )
            total_count = member_count

        has_more = query.offset + query.limit < total_count

        logger.info(
            "search_success",
            community_id=str(community_id),
            result_count=len(items),
            member_count=member_count,
            post_count=post_count,
        )

        return SearchResult(
            items=items,
            total_count=total_count,
            member_count=member_count,
            post_count=post_count,
            has_more=has_more,
        )

    def _sanitize_query(self, query: str) -> str:
        """Strip HTML tags and normalize whitespace."""
        # Remove HTML tags
        cleaned = re.sub(r"<[^>]+>", "", query)
        # Normalize whitespace
        cleaned = " ".join(cleaned.split())
        return cleaned.strip()
```

**Step 2: Update handlers `__init__.py`**

Add to `src/community/application/handlers/__init__.py`:
```python
from src.community.application.handlers.search_handler import SearchHandler
```
And add `"SearchHandler"` to `__all__`.

---

### Task 4: SqlAlchemySearchRepository

**Depends on:** Task 1 (migration), Task 2 (DTOs + interface)

**What:** Implement the search repository using PostgreSQL FTS (`plainto_tsquery`, `@@` operator) with GIN indexes. Members use FTS on `search_vector` + ILIKE on `username`. Posts use FTS on `search_vector`. Members sorted alphabetically, posts sorted by newest first.

**Files:**
- Create: `src/community/infrastructure/persistence/search_repository.py`
- Modify: `src/community/infrastructure/persistence/__init__.py` (add export)

**Step 1: Create SqlAlchemySearchRepository**

File: `src/community/infrastructure/persistence/search_repository.py`

Pattern reference: `src/community/infrastructure/persistence/member_repository.py` (JOIN pattern)

```python
"""SQLAlchemy implementation of search repository using PostgreSQL FTS."""

from sqlalchemy import func as sa_func
from sqlalchemy import or_, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from src.community.application.dtos.search_results import (
    MemberSearchEntry,
    PostSearchEntry,
)
from src.community.domain.repositories.search_repository import ISearchRepository
from src.community.domain.value_objects import CommunityId
from src.community.infrastructure.persistence.models import (
    CategoryModel,
    CommunityMemberModel,
    PostModel,
    ReactionModel,
    CommentModel,
)
from src.identity.infrastructure.persistence.models import ProfileModel


class SqlAlchemySearchRepository(ISearchRepository):
    """PostgreSQL Full-Text Search implementation."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def search_members(
        self,
        community_id: CommunityId,
        query: str,
        limit: int = 10,
        offset: int = 0,
    ) -> list[MemberSearchEntry]:
        tsquery = sa_func.plainto_tsquery("english", query)

        stmt = (
            select(
                CommunityMemberModel.user_id,
                CommunityMemberModel.role,
                CommunityMemberModel.joined_at,
                ProfileModel.display_name,
                ProfileModel.username,
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
                or_(
                    ProfileModel.search_vector.op("@@")(tsquery),
                    ProfileModel.username.ilike(f"%{query}%"),
                ),
            )
            .order_by(ProfileModel.display_name.asc().nulls_last())
            .limit(limit)
            .offset(offset)
        )

        result = await self._session.execute(stmt)
        rows = result.all()

        return [
            MemberSearchEntry(
                user_id=row.user_id,
                display_name=row.display_name,
                username=row.username,
                avatar_url=row.avatar_url,
                role=row.role.lower() if row.role else "member",
                bio=row.bio,
                joined_at=row.joined_at,
            )
            for row in rows
        ]

    async def count_members(
        self,
        community_id: CommunityId,
        query: str,
    ) -> int:
        tsquery = sa_func.plainto_tsquery("english", query)

        stmt = (
            select(sa_func.count())
            .select_from(CommunityMemberModel)
            .outerjoin(
                ProfileModel,
                CommunityMemberModel.user_id == ProfileModel.user_id,
            )
            .where(
                CommunityMemberModel.community_id == community_id.value,
                CommunityMemberModel.is_active.is_(True),
                or_(
                    ProfileModel.search_vector.op("@@")(tsquery),
                    ProfileModel.username.ilike(f"%{query}%"),
                ),
            )
        )

        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def search_posts(
        self,
        community_id: CommunityId,
        query: str,
        limit: int = 10,
        offset: int = 0,
    ) -> list[PostSearchEntry]:
        tsquery = sa_func.plainto_tsquery("english", query)

        # Subquery for like counts
        like_count_sq = (
            select(sa_func.count())
            .where(
                ReactionModel.target_type == "post",
                ReactionModel.target_id == PostModel.id,
            )
            .correlate(PostModel)
            .scalar_subquery()
        )

        # Subquery for comment counts
        comment_count_sq = (
            select(sa_func.count())
            .where(
                CommentModel.post_id == PostModel.id,
                CommentModel.is_deleted.is_(False),
            )
            .correlate(PostModel)
            .scalar_subquery()
        )

        stmt = (
            select(
                PostModel.id,
                PostModel.title,
                sa_func.left(PostModel.content, 200).label("body_snippet"),
                PostModel.created_at,
                ProfileModel.display_name.label("author_name"),
                ProfileModel.avatar_url.label("author_avatar_url"),
                CategoryModel.name.label("category_name"),
                CategoryModel.emoji.label("category_emoji"),
                like_count_sq.label("like_count"),
                comment_count_sq.label("comment_count"),
            )
            .outerjoin(ProfileModel, PostModel.author_id == ProfileModel.user_id)
            .outerjoin(CategoryModel, PostModel.category_id == CategoryModel.id)
            .where(
                PostModel.community_id == community_id.value,
                PostModel.is_deleted.is_(False),
                PostModel.search_vector.op("@@")(tsquery),
            )
            .order_by(PostModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        result = await self._session.execute(stmt)
        rows = result.all()

        return [
            PostSearchEntry(
                id=row.id,
                title=row.title,
                body_snippet=row.body_snippet or "",
                author_name=row.author_name,
                author_avatar_url=row.author_avatar_url,
                category_name=row.category_name,
                category_emoji=row.category_emoji,
                created_at=row.created_at,
                like_count=row.like_count or 0,
                comment_count=row.comment_count or 0,
            )
            for row in rows
        ]

    async def count_posts(
        self,
        community_id: CommunityId,
        query: str,
    ) -> int:
        tsquery = sa_func.plainto_tsquery("english", query)

        stmt = (
            select(sa_func.count())
            .select_from(PostModel)
            .where(
                PostModel.community_id == community_id.value,
                PostModel.is_deleted.is_(False),
                PostModel.search_vector.op("@@")(tsquery),
            )
        )

        result = await self._session.execute(stmt)
        return result.scalar_one()
```

**Step 2: Add `search_vector` column to ORM models**

Add to `src/community/infrastructure/persistence/models.py` — `PostModel`:
```python
from sqlalchemy.dialects.postgresql import TSVECTOR
# ...
search_vector: Mapped[str | None] = mapped_column(TSVECTOR, nullable=True)
```

Add to `src/identity/infrastructure/persistence/models.py` — `ProfileModel`:
```python
from sqlalchemy.dialects.postgresql import TSVECTOR
# ...
username: Mapped[str | None] = mapped_column(String(100), nullable=True, unique=True)
search_vector: Mapped[str | None] = mapped_column(TSVECTOR, nullable=True)
```

**Step 3: Update persistence `__init__.py`**

Add to `src/community/infrastructure/persistence/__init__.py`:
```python
from src.community.infrastructure.persistence.search_repository import (
    SqlAlchemySearchRepository,
)
```
And add `"SqlAlchemySearchRepository"` to `__all__`.

---

### Task 5: API Layer — Schemas, Controller, Dependencies, Router

**Depends on:** Task 3 (handler), Task 4 (repository)

**What:** Create Pydantic response/request schemas, the search controller endpoint, the dependency injection factory, and register the router in main.py.

**Files:**
- Create: `src/community/interface/api/search_controller.py`
- Modify: `src/community/interface/api/schemas.py` (add search schemas)
- Modify: `src/community/interface/api/dependencies.py` (add search handler dep)
- Modify: `src/community/interface/api/__init__.py` (export search router)
- Modify: `src/main.py` (register search router)

**Step 1: Add search schemas to `schemas.py`**

Append to `src/community/interface/api/schemas.py`:

```python
# ============================================================================
# Search Schemas
# ============================================================================


class MemberSearchItemResponse(BaseModel):
    """Member search result item."""

    user_id: UUID
    display_name: str | None
    username: str | None
    avatar_url: str | None
    role: str
    bio: str | None
    joined_at: datetime


class PostSearchItemResponse(BaseModel):
    """Post search result item."""

    id: UUID
    title: str
    body_snippet: str
    author_name: str | None
    author_avatar_url: str | None
    category_name: str | None
    category_emoji: str | None
    created_at: datetime
    like_count: int
    comment_count: int


class SearchResponse(BaseModel):
    """Search results response with tab counts."""

    items: list[MemberSearchItemResponse] | list[PostSearchItemResponse]
    total_count: int
    member_count: int
    post_count: int
    has_more: bool
```

**Step 2: Add search dependencies to `dependencies.py`**

Add imports and factory:

```python
from src.community.application.handlers import SearchHandler
from src.community.infrastructure.persistence import SqlAlchemySearchRepository

def get_search_repository(session: SessionDep) -> SqlAlchemySearchRepository:
    """Get search repository."""
    return SqlAlchemySearchRepository(session)

SearchRepositoryDep = Annotated[SqlAlchemySearchRepository, Depends(get_search_repository)]

def get_search_handler(
    search_repo: SearchRepositoryDep,
    member_repo: MemberRepositoryDep,
) -> SearchHandler:
    """Get search handler."""
    return SearchHandler(
        search_repository=search_repo,
        member_repository=member_repo,
    )

SearchHandlerDep = Annotated[SearchHandler, Depends(get_search_handler)]
```

**Step 3: Create search controller**

File: `src/community/interface/api/search_controller.py`

Pattern reference: `src/community/interface/api/member_controller.py`

```python
"""Search API endpoint."""

from typing import Annotated

from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select

from src.community.application.queries.search_query import SearchQuery
from src.community.domain.exceptions import NotCommunityMemberError
from src.community.infrastructure.persistence.models import CommunityModel
from src.community.interface.api.dependencies import (
    CurrentUserIdDep,
    SearchHandlerDep,
    SessionDep,
)
from src.community.interface.api.schemas import (
    ErrorResponse,
    MemberSearchItemResponse,
    PostSearchItemResponse,
    SearchResponse,
)

logger = structlog.get_logger()

router = APIRouter(
    prefix="/community",
    tags=["Community - Search"],
)


async def get_default_community_id(session: SessionDep) -> UUID:
    """Get the default community ID."""
    result = await session.execute(
        select(CommunityModel.id).order_by(CommunityModel.created_at).limit(1)
    )
    community_id = result.scalar_one_or_none()
    if community_id is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No community found",
        )
    return community_id


DefaultCommunityIdDep = Annotated[UUID, Depends(get_default_community_id)]


@router.get(
    "/search",
    response_model=SearchResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid query"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not a community member"},
    },
)
async def search(
    current_user_id: CurrentUserIdDep,
    community_id: DefaultCommunityIdDep,
    handler: SearchHandlerDep,
    q: str = Query("", description="Search query"),
    type: str = Query("members", description="Search type: members or posts"),
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0),
) -> SearchResponse:
    """Search community members and posts."""
    # Validate query
    trimmed = q.strip()
    if not trimmed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "QUERY_REQUIRED", "message": "A search query is required"},
        )
    if len(trimmed) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "QUERY_TOO_SHORT", "message": "Please enter at least 3 characters to search"},
        )

    # Validate type
    if type not in ("members", "posts"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_SEARCH_TYPE", "message": "Search type must be 'members' or 'posts'"},
        )

    # Truncate long queries
    if len(trimmed) > 200:
        trimmed = trimmed[:200]

    try:
        query = SearchQuery(
            community_id=community_id,
            requester_id=current_user_id,
            query=trimmed,
            search_type=type,
            limit=limit,
            offset=offset,
        )
        result = await handler.handle(query)

        # Map items to response schemas
        if type == "posts":
            response_items = [
                PostSearchItemResponse(
                    id=entry.id,
                    title=entry.title,
                    body_snippet=entry.body_snippet,
                    author_name=entry.author_name,
                    author_avatar_url=entry.author_avatar_url,
                    category_name=entry.category_name,
                    category_emoji=entry.category_emoji,
                    created_at=entry.created_at,
                    like_count=entry.like_count,
                    comment_count=entry.comment_count,
                )
                for entry in result.items
            ]
        else:
            response_items = [
                MemberSearchItemResponse(
                    user_id=entry.user_id,
                    display_name=entry.display_name,
                    username=entry.username,
                    avatar_url=entry.avatar_url,
                    role=entry.role,
                    bio=entry.bio,
                    joined_at=entry.joined_at,
                )
                for entry in result.items
            ]

        return SearchResponse(
            items=response_items,
            total_count=result.total_count,
            member_count=result.member_count,
            post_count=result.post_count,
            has_more=result.has_more,
        )
    except NotCommunityMemberError as err:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this community",
        ) from err
```

**Step 4: Export search router in `__init__.py`**

Add to `src/community/interface/api/__init__.py`:
```python
from src.community.interface.api.search_controller import router as search_router
```
And add `"search_router"` to `__all__`.

**Step 5: Register router in `main.py`**

Add to imports:
```python
from src.community.interface.api import (
    ...
    search_router,
)
```

Add after other router registrations:
```python
app.include_router(search_router, prefix="/api/v1")
```

**Step 6: Verify endpoint is accessible**

```bash
# Start dev server and test
curl -s http://localhost:8000/docs | grep -o "search"
```

---

### Task 6: Frontend Types, API Client, and Hook

**Depends on:** none (mirrors API contract)

**What:** Create TypeScript interfaces matching the backend response, an API client function, and a React Query hook for fetching search results.

**Files:**
- Create: `frontend/src/features/search/types/search.ts`
- Create: `frontend/src/features/search/types/index.ts`
- Create: `frontend/src/features/search/api/searchApi.ts`
- Create: `frontend/src/features/search/api/index.ts`
- Create: `frontend/src/features/search/hooks/useSearch.ts`
- Create: `frontend/src/features/search/hooks/index.ts`

**Step 1: Create TypeScript types**

File: `frontend/src/features/search/types/search.ts`

Pattern reference: `frontend/src/features/members/types/members.ts`

```typescript
export interface MemberSearchItem {
  user_id: string;
  display_name: string | null;
  username: string | null;
  avatar_url: string | null;
  role: 'admin' | 'moderator' | 'member';
  bio: string | null;
  joined_at: string;
}

export interface PostSearchItem {
  id: string;
  title: string;
  body_snippet: string;
  author_name: string | null;
  author_avatar_url: string | null;
  category_name: string | null;
  category_emoji: string | null;
  created_at: string;
  like_count: number;
  comment_count: number;
}

export type SearchType = 'members' | 'posts';

export interface SearchQueryParams {
  q: string;
  type?: SearchType;
  limit?: number;
  offset?: number;
}

export interface SearchResponse {
  items: MemberSearchItem[] | PostSearchItem[];
  total_count: number;
  member_count: number;
  post_count: number;
  has_more: boolean;
}
```

File: `frontend/src/features/search/types/index.ts`
```typescript
export * from './search';
```

**Step 2: Create API client**

File: `frontend/src/features/search/api/searchApi.ts`

```typescript
import { apiClient } from '@/lib/api-client';
import type { SearchQueryParams, SearchResponse } from '../types';

export async function searchCommunity(params: SearchQueryParams): Promise<SearchResponse> {
  const response = await apiClient.get<SearchResponse>('/community/search', { params });
  return response.data;
}
```

File: `frontend/src/features/search/api/index.ts`
```typescript
export { searchCommunity } from './searchApi';
```

**Step 3: Create useSearch hook**

File: `frontend/src/features/search/hooks/useSearch.ts`

Pattern reference: `frontend/src/features/members/hooks/useMembers.ts` (but uses `useQuery` not `useInfiniteQuery` — search uses offset pagination)

```typescript
import { useQuery } from '@tanstack/react-query';
import { searchCommunity } from '../api';
import type { SearchQueryParams, SearchResponse, SearchType } from '../types';

const SEARCH_KEY = ['search'] as const;

export interface UseSearchResult {
  data: SearchResponse | undefined;
  isLoading: boolean;
  error: Error | null;
}

export function useSearch(
  query: string,
  type: SearchType = 'members',
  limit: number = 10,
  offset: number = 0,
): UseSearchResult {
  const params: SearchQueryParams = { q: query, type, limit, offset };

  const { data, isLoading, error } = useQuery({
    queryKey: [...SEARCH_KEY, query, type, limit, offset],
    queryFn: () => searchCommunity(params),
    enabled: query.trim().length >= 3,
    staleTime: 30 * 1000,
    retry: 1,
  });

  return {
    data,
    isLoading,
    error: error ?? null,
  };
}
```

File: `frontend/src/features/search/hooks/index.ts`
```typescript
export { useSearch } from './useSearch';
export type { UseSearchResult } from './useSearch';
```

---

### Task 7: Frontend SearchBar Component

**Depends on:** none (independent UI)

**What:** Create the header search bar with magnifying glass icon, clear button, and Enter-to-navigate behavior. Integrate into the existing AppHeader.

**Files:**
- Create: `frontend/src/features/search/components/SearchBar.tsx`
- Modify: `frontend/src/App.tsx` (embed SearchBar in AppHeader)

**Step 1: Create SearchBar component**

File: `frontend/src/features/search/components/SearchBar.tsx`

```tsx
import { useState, useCallback } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { MagnifyingGlassIcon, XMarkIcon } from '@heroicons/react/24/outline';

export function SearchBar(): JSX.Element {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [value, setValue] = useState(searchParams.get('q') ?? '');

  const handleSubmit = useCallback(
    (e: React.FormEvent) => {
      e.preventDefault();
      const trimmed = value.trim();
      if (trimmed.length >= 3) {
        navigate(`/search?q=${encodeURIComponent(trimmed)}&t=members`);
      }
    },
    [value, navigate],
  );

  const handleClear = useCallback(() => {
    setValue('');
  }, []);

  return (
    <form onSubmit={handleSubmit} className="relative flex-1 max-w-xl mx-8">
      <div className="relative">
        <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
        <input
          type="text"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder="Search members"
          aria-label="Search community members and posts"
          className="w-full rounded-full bg-gray-100 py-2 pl-10 pr-10 text-sm text-gray-900 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-300"
        />
        {value.length > 0 && (
          <button
            type="button"
            onClick={handleClear}
            className="absolute right-3 top-1/2 -translate-y-1/2"
            aria-label="Clear search"
          >
            <XMarkIcon className="h-4 w-4 text-gray-400 hover:text-gray-600" />
          </button>
        )}
      </div>
    </form>
  );
}
```

**Step 2: Integrate SearchBar into AppHeader in `App.tsx`**

In the `AppHeader` function, add SearchBar between the logo and user menu:

```tsx
import { SearchBar } from '@/features/search/components/SearchBar';
```

Modify the header's inner div to include the search bar:
```tsx
<div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6 lg:px-8">
  <div className="flex items-center gap-3">
    <h1 className="text-xl font-bold text-gray-900">Koulu</h1>
    <span className="rounded-full bg-primary-100 px-3 py-1 text-sm font-medium text-primary-700">
      {projectName}
    </span>
  </div>
  {user !== null && <SearchBar />}
  {user !== null && (
    <div className="flex items-center space-x-4">
      <UserDropdown user={user} onLogout={onLogout} />
    </div>
  )}
</div>
```

---

### Task 8: Frontend Result Cards

**Depends on:** Task 6 (uses types)

**What:** Create MemberSearchCard and PostSearchCard components that display search result entries.

**Files:**
- Create: `frontend/src/features/search/components/MemberSearchCard.tsx`
- Create: `frontend/src/features/search/components/PostSearchCard.tsx`

**Step 1: Create MemberSearchCard**

File: `frontend/src/features/search/components/MemberSearchCard.tsx`

Pattern reference: `frontend/src/features/members/components/MemberCard.tsx`

```tsx
import { useNavigate } from 'react-router-dom';
import { CalendarIcon } from '@heroicons/react/24/outline';
import { Avatar } from '@/components/Avatar';
import type { MemberSearchItem } from '../types';

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}

const ROLE_BADGE: Record<string, { label: string; className: string } | null> = {
  admin: { label: 'Admin', className: 'bg-yellow-100 text-yellow-800' },
  moderator: { label: 'Moderator', className: 'bg-blue-100 text-blue-800' },
  member: null,
};

interface MemberSearchCardProps {
  member: MemberSearchItem;
}

export function MemberSearchCard({ member }: MemberSearchCardProps): JSX.Element {
  const navigate = useNavigate();
  const displayName = member.display_name ?? 'Unknown';
  const badge = ROLE_BADGE[member.role];

  return (
    <button
      type="button"
      data-testid="member-search-card"
      onClick={() => navigate(`/profile/${member.user_id}`)}
      className="flex w-full items-start gap-4 rounded-lg border border-gray-200 bg-white p-4 text-left transition-shadow hover:shadow-md"
    >
      <Avatar src={member.avatar_url} alt={displayName} size="lg" fallback={displayName} />
      <div className="min-w-0 flex-1 space-y-1">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-base font-semibold text-gray-900">{displayName}</h3>
            {badge != null && (
              <span className={`inline-flex shrink-0 rounded-full px-2 py-0.5 text-xs font-medium ${badge.className}`}>
                {badge.label}
              </span>
            )}
          </div>
          {member.username != null && (
            <p className="text-sm text-gray-500">@{member.username}</p>
          )}
        </div>
        {member.bio != null && (
          <p className="line-clamp-2 text-sm text-gray-700">{member.bio}</p>
        )}
        <div className="flex items-center gap-1 text-xs text-gray-400">
          <CalendarIcon className="h-3.5 w-3.5" />
          <span>Joined {formatDate(member.joined_at)}</span>
        </div>
      </div>
    </button>
  );
}
```

**Step 2: Create PostSearchCard**

File: `frontend/src/features/search/components/PostSearchCard.tsx`

```tsx
import { useNavigate } from 'react-router-dom';
import { HeartIcon, ChatBubbleLeftIcon } from '@heroicons/react/24/outline';
import { Avatar } from '@/components/Avatar';
import type { PostSearchItem } from '../types';

function relativeTime(dateStr: string): string {
  const now = Date.now();
  const diff = now - new Date(dateStr).getTime();
  const minutes = Math.floor(diff / 60000);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  if (days < 30) return `${days}d ago`;
  return new Date(dateStr).toLocaleDateString();
}

interface PostSearchCardProps {
  post: PostSearchItem;
}

export function PostSearchCard({ post }: PostSearchCardProps): JSX.Element {
  const navigate = useNavigate();

  return (
    <button
      type="button"
      data-testid="post-search-card"
      onClick={() => navigate(`/community/posts/${post.id}`)}
      className="flex w-full flex-col gap-3 rounded-lg border border-gray-200 bg-white p-4 text-left transition-shadow hover:shadow-md"
    >
      <div>
        <h3 className="text-lg font-semibold text-gray-900">{post.title}</h3>
        <p className="mt-1 line-clamp-3 text-sm text-gray-700">{post.body_snippet}</p>
      </div>
      <div className="flex items-center gap-3">
        <Avatar
          src={post.author_avatar_url}
          alt={post.author_name ?? 'Author'}
          size="sm"
          fallback={post.author_name ?? '?'}
        />
        <div className="flex flex-1 flex-wrap items-center gap-x-3 gap-y-1 text-xs text-gray-500">
          <span className="font-medium text-gray-900">{post.author_name}</span>
          {post.category_name != null && (
            <span className="inline-flex items-center rounded-full bg-gray-100 px-2 py-0.5 text-xs">
              {post.category_emoji} {post.category_name}
            </span>
          )}
          <span>{relativeTime(post.created_at)}</span>
          <span className="flex items-center gap-1">
            <HeartIcon className="h-3.5 w-3.5" />
            {post.like_count}
          </span>
          <span className="flex items-center gap-1">
            <ChatBubbleLeftIcon className="h-3.5 w-3.5" />
            {post.comment_count}
          </span>
        </div>
      </div>
    </button>
  );
}
```

---

### Task 9: Frontend SearchResults Page, Tabs, Skeleton, and Routing

**Depends on:** Task 6 (hook), Task 7 (SearchBar), Task 8 (cards)

**What:** Assemble the search results page with tab switching, skeleton loading states, and wire up the `/search` route in App.tsx.

**Files:**
- Create: `frontend/src/features/search/components/SearchResultTabs.tsx`
- Create: `frontend/src/features/search/components/SearchSkeleton.tsx`
- Create: `frontend/src/features/search/components/SearchResults.tsx`
- Create: `frontend/src/features/search/components/index.ts`
- Create: `frontend/src/pages/SearchPage.tsx`
- Modify: `frontend/src/pages/index.ts` (export SearchPage)
- Modify: `frontend/src/App.tsx` (add /search route)

**Step 1: Create SearchResultTabs**

File: `frontend/src/features/search/components/SearchResultTabs.tsx`

```tsx
import type { SearchType } from '../types';

interface SearchResultTabsProps {
  activeTab: SearchType;
  memberCount: number;
  postCount: number;
  onTabChange: (tab: SearchType) => void;
}

export function SearchResultTabs({
  activeTab,
  memberCount,
  postCount,
  onTabChange,
}: SearchResultTabsProps): JSX.Element {
  const tabs: Array<{ key: SearchType; label: string; count: number }> = [
    { key: 'members', label: 'Members', count: memberCount },
    { key: 'posts', label: 'Posts', count: postCount },
  ];

  return (
    <div className="border-b border-gray-200 bg-white">
      <nav className="mx-auto flex max-w-7xl space-x-8 px-4">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            type="button"
            onClick={() => onTabChange(tab.key)}
            className={`whitespace-nowrap border-b-2 py-4 px-1 text-sm font-medium transition-colors ${
              activeTab === tab.key
                ? 'border-gray-900 text-gray-900'
                : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
            }`}
          >
            {tab.label} {tab.count}
          </button>
        ))}
      </nav>
    </div>
  );
}
```

**Step 2: Create SearchSkeleton**

File: `frontend/src/features/search/components/SearchSkeleton.tsx`

```tsx
export function SearchSkeleton(): JSX.Element {
  return (
    <div className="space-y-4">
      {[1, 2, 3].map((i) => (
        <div
          key={i}
          className="flex w-full animate-pulse items-start gap-4 rounded-lg border border-gray-200 bg-white p-4"
        >
          <div className="h-14 w-14 shrink-0 rounded-full bg-gray-200" />
          <div className="flex-1 space-y-2">
            <div className="h-4 w-32 rounded bg-gray-200" />
            <div className="h-3 w-24 rounded bg-gray-200" />
            <div className="h-3 w-full rounded bg-gray-200" />
            <div className="h-3 w-3/4 rounded bg-gray-200" />
          </div>
        </div>
      ))}
    </div>
  );
}
```

**Step 3: Create SearchResults container**

File: `frontend/src/features/search/components/SearchResults.tsx`

```tsx
import { useSearchParams } from 'react-router-dom';
import { useSearch } from '../hooks';
import { SearchResultTabs } from './SearchResultTabs';
import { SearchSkeleton } from './SearchSkeleton';
import { MemberSearchCard } from './MemberSearchCard';
import { PostSearchCard } from './PostSearchCard';
import type { SearchType, MemberSearchItem, PostSearchItem } from '../types';

export function SearchResults(): JSX.Element {
  const [searchParams, setSearchParams] = useSearchParams();
  const query = searchParams.get('q') ?? '';
  const activeTab = (searchParams.get('t') ?? 'members') as SearchType;

  const { data, isLoading, error } = useSearch(query, activeTab);

  const handleTabChange = (tab: SearchType): void => {
    setSearchParams((prev) => {
      prev.set('t', tab);
      return prev;
    });
  };

  if (query.trim().length < 3) {
    return (
      <div className="py-12 text-center">
        <p className="text-sm text-gray-500">
          {query.trim().length === 0
            ? 'Enter a search term above to find members and posts'
            : 'Please enter at least 3 characters to search'}
        </p>
      </div>
    );
  }

  return (
    <div>
      <SearchResultTabs
        activeTab={activeTab}
        memberCount={data?.member_count ?? 0}
        postCount={data?.post_count ?? 0}
        onTabChange={handleTabChange}
      />

      <div className="mx-auto max-w-[1100px] px-4 py-6">
        <div className="grid grid-cols-1 gap-6 md:grid-cols-[2fr_360px]">
          <div className="space-y-4">
            {isLoading ? (
              <SearchSkeleton />
            ) : error != null ? (
              <div className="py-12 text-center">
                <p className="text-sm text-red-600">
                  Search is temporarily unavailable. Please try again.
                </p>
              </div>
            ) : data != null && data.items.length === 0 ? (
              <div className="py-12 text-center">
                <p className="text-base font-semibold text-gray-900">
                  No {activeTab} found for &ldquo;{query}&rdquo;
                </p>
                <p className="mt-2 text-sm text-gray-500">
                  Try a different search term
                </p>
              </div>
            ) : data != null && activeTab === 'members' ? (
              (data.items as MemberSearchItem[]).map((member) => (
                <MemberSearchCard key={member.user_id} member={member} />
              ))
            ) : data != null && activeTab === 'posts' ? (
              (data.items as PostSearchItem[]).map((post) => (
                <PostSearchCard key={post.id} post={post} />
              ))
            ) : null}
          </div>

          {/* Sidebar placeholder — reuse CommunitySidebar in future */}
          <div className="hidden md:block" />
        </div>
      </div>
    </div>
  );
}
```

**Step 4: Create component barrel export**

File: `frontend/src/features/search/components/index.ts`

```typescript
export { SearchBar } from './SearchBar';
export { SearchResults } from './SearchResults';
export { SearchResultTabs } from './SearchResultTabs';
export { MemberSearchCard } from './MemberSearchCard';
export { PostSearchCard } from './PostSearchCard';
export { SearchSkeleton } from './SearchSkeleton';
```

**Step 5: Create SearchPage**

File: `frontend/src/pages/SearchPage.tsx`

```tsx
import { useAuth } from '@/features/identity/hooks';
import { SearchResults } from '@/features/search/components';
import { TabBar, UserDropdown } from '@/components';
import { SearchBar } from '@/features/search/components/SearchBar';

const APP_TABS = [
  { label: 'Community', path: '/' },
  { label: 'Classroom', path: '/classroom' },
  { label: 'Members', path: '/members' },
];

export function SearchPage(): JSX.Element {
  const { user, logout, isLoading } = useAuth();
  const projectName = import.meta.env.VITE_PROJECT_NAME ?? 'koulu';

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary-200 border-t-primary-600" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6 lg:px-8">
          <div className="flex items-center gap-3">
            <h1 className="text-xl font-bold text-gray-900">Koulu</h1>
            <span className="rounded-full bg-primary-100 px-3 py-1 text-sm font-medium text-primary-700">
              {projectName}
            </span>
          </div>
          {user !== null && <SearchBar />}
          {user !== null && (
            <div className="flex items-center space-x-4">
              <UserDropdown user={user} onLogout={() => void logout()} />
            </div>
          )}
        </div>
      </header>
      <TabBar tabs={APP_TABS} />
      <SearchResults />
    </div>
  );
}
```

**Step 6: Export SearchPage from pages index**

Add to `frontend/src/pages/index.ts`:
```typescript
export { SearchPage } from './SearchPage';
```

**Step 7: Add /search route in App.tsx**

Import `SearchPage` at the top of `App.tsx`:
```tsx
import { SearchPage } from '@/pages';
```

Add route inside `<Routes>`, before the catch-all:
```tsx
{/* Search route */}
<Route
  path="/search"
  element={
    <ProtectedRoute>
      <SearchPage />
    </ProtectedRoute>
  }
/>
```

**Step 8: Verify frontend builds**

```bash
cd frontend && npm run build && npm run typecheck
```

---

### Task 10: BDD Test Implementation + Final Verification

**Depends on:** all previous tasks

**What:** Implement BDD step definitions for Phase 1's 11 scenarios, skip Phase 2+3 scenarios with markers, fix the BDD spec issue (line 44 query "a" -> 3+ char query), and run full verification.

**Files:**
- Create: `tests/features/search/test_search.py`
- Modify: `tests/features/search/search.feature` (fix line 44 query length)

**Step 1: Fix BDD spec — line 44 query too short**

In `tests/features/search/search.feature`, line 45-46, change:
```gherkin
    When the member searches for "a" with type "members"
```
to:
```gherkin
    When the member searches for "startup" with type "members"
```
This fixes the conflict where the spec requires 3-char minimum but this scenario uses 1 character. The query "startup" will match Alice Chen's bio ("startup enthusiast").

**Step 2: Create BDD step definitions**

File: `tests/features/search/test_search.py`

Follow the async pattern from `tests/features/community/test_feed.py`:
- ALL step functions must be `async` with `client: AsyncClient` parameter
- Use `# ruff: noqa: ARG001` at top
- Context dict passes state between steps
- Use domain factories then persist for test data setup

Key patterns:
```python
"""BDD tests for Search feature."""
# ruff: noqa: ARG001

import pytest
from httpx import AsyncClient
from pytest_bdd import given, parsers, scenario, then, when

# ... (implement all step definitions following existing test patterns)
```

The step definitions must:
1. Set up community, members, and posts in the Background steps
2. Authenticate users via login
3. Make GET requests to `/api/v1/community/search?q=...&type=...`
4. Assert response status, item counts, and field presence

**Step 3: Add skip markers for Phase 2 and Phase 3 scenarios**

For each Phase 2/3 scenario, add skip markers in the scenario decorators:
```python
@pytest.mark.skip(reason="Phase 2: Pagination support")
@scenario("search.feature", "Search results are paginated")
async def test_search_results_paginated() -> None:
    pass
```

Phase 2 skips (8 scenarios):
- Search results are paginated
- Navigate to next page of results
- Search uses stemming for member bio
- Search uses stemming for post content
- Search with query shorter than 3 characters
- Search with empty query
- Search with invalid type parameter
- Search with query exceeding maximum length

Phase 3 skips (11 scenarios):
- Search returns no results
- Search with special characters
- Deleted posts do not appear in search results
- Inactive members do not appear in search results
- Search with only whitespace
- Member with no bio is still found by name
- Search query matches across multiple members
- Unauthenticated user cannot search
- Non-member cannot search a community
- Search input is sanitized against SQL injection
- Search respects rate limiting

**Step 4: Run BDD tests**

```bash
pytest tests/features/search/test_search.py -v
# Expected: 11 passed, 19 skipped, 0 failed
```

**Step 5: Run full verification**

```bash
./scripts/verify.sh
# Expected: All checks pass (ruff, mypy, pytest)
```

**Step 6: Verify frontend**

```bash
cd frontend && npm run build && npm run typecheck
```

**Step 7: Commit**

```bash
git add -A
git commit -m "feat(search): complete Phase 1 — core search end-to-end

- Add PostgreSQL FTS with tsvector columns, GIN indexes, and triggers
- Add username column to profiles
- Implement SearchHandler, SqlAlchemySearchRepository
- Add GET /api/v1/community/search endpoint
- Add SearchBar to header, SearchResults page with tabs
- 11 BDD scenarios passing, 19 skipped for Phase 2/3"
```
