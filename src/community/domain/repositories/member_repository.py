"""Community member repository interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from src.community.domain.entities import CommunityMember
from src.community.domain.value_objects import CommunityId
from src.identity.domain.value_objects import UserId

if TYPE_CHECKING:
    from src.community.application.dtos.member_directory_entry import MemberDirectoryEntry


class IMemberRepository(ABC):
    """
    Interface for CommunityMember persistence operations.

    Implementations handle database operations for CommunityMember entity.
    """

    @abstractmethod
    async def save(self, member: CommunityMember) -> None:
        """
        Save a community member (create or update).

        Args:
            member: The member entity to save
        """
        ...

    @abstractmethod
    async def get_by_user_and_community(
        self,
        user_id: UserId,
        community_id: CommunityId,
    ) -> CommunityMember | None:
        """
        Get a member by user ID and community ID.

        Args:
            user_id: The user's ID
            community_id: The community ID

        Returns:
            CommunityMember if found and active, None otherwise
        """
        ...

    @abstractmethod
    async def exists(
        self,
        user_id: UserId,
        community_id: CommunityId,
    ) -> bool:
        """
        Check if a user is a member of a community.

        Args:
            user_id: The user's ID
            community_id: The community ID

        Returns:
            True if member exists and is active, False otherwise
        """
        ...

    @abstractmethod
    async def list_by_community(
        self,
        community_id: CommunityId,
    ) -> list[CommunityMember]:
        """
        List all members in a community.

        Args:
            community_id: The community ID

        Returns:
            List of active members
        """
        ...

    @abstractmethod
    async def delete(
        self,
        user_id: UserId,
        community_id: CommunityId,
    ) -> None:
        """
        Delete a community member.

        Args:
            user_id: The user's ID
            community_id: The community ID
        """
        ...

    @abstractmethod
    async def list_directory(
        self,
        community_id: CommunityId,
        sort: str = "most_recent",
        limit: int = 20,
        offset: int = 0,
    ) -> list[MemberDirectoryEntry]:
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
