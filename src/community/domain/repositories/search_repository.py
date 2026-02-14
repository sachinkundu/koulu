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
