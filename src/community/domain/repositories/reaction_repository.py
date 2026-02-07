"""Reaction repository interface."""

from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from src.community.domain.entities import Reaction
from src.community.domain.value_objects import PostId, ReactionId
from src.identity.domain.value_objects import UserId


class IReactionRepository(ABC):
    """
    Interface for Reaction persistence operations.

    Implementations handle database operations for Reaction entity.
    """

    @abstractmethod
    async def save(self, reaction: Reaction) -> None:
        """
        Save a reaction (create).

        Args:
            reaction: The reaction entity to save
        """
        ...

    @abstractmethod
    async def find_by_user_and_target(
        self,
        user_id: UserId,
        target_type: str,
        target_id: UUID,
    ) -> Reaction | None:
        """
        Find a reaction by user and target.

        Args:
            user_id: The user ID
            target_type: "post" or "comment"
            target_id: The target ID (post or comment)

        Returns:
            Reaction if found, None otherwise
        """
        ...

    @abstractmethod
    async def delete(self, reaction_id: ReactionId) -> None:
        """
        Delete a reaction by ID.

        Args:
            reaction_id: The reaction ID to delete
        """
        ...

    @abstractmethod
    async def delete_by_target(self, target_type: str, target_id: UUID) -> None:
        """
        Delete all reactions for a target (cascade delete).

        Args:
            target_type: "post" or "comment"
            target_id: The target ID
        """
        ...

    @abstractmethod
    async def count_by_target(self, target_type: str, target_id: UUID) -> int:
        """
        Count reactions for a target.

        Args:
            target_type: "post" or "comment"
            target_id: The target ID

        Returns:
            Total reaction count
        """
        ...

    @abstractmethod
    async def list_users_by_target(
        self,
        target_type: str,
        target_id: UUID,
        limit: int = 100,
    ) -> list[UserId]:
        """
        List users who reacted to a target.

        Args:
            target_type: "post" or "comment"
            target_id: The target ID
            limit: Maximum number of user IDs to return

        Returns:
            List of user IDs
        """
        ...

    @abstractmethod
    async def count_by_user_since(self, user_id: UserId, since: datetime) -> int:
        """
        Count reactions created by a user since a given time.

        Used for rate limiting.

        Args:
            user_id: The user ID
            since: Timestamp to count from

        Returns:
            Count of reactions created since the timestamp
        """
        ...

    @abstractmethod
    async def delete_by_post_cascade(self, post_id: PostId) -> None:
        """
        Delete all reactions for a post and its comments (cascade delete).

        Args:
            post_id: The post ID
        """
        ...
