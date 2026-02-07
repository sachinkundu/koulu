"""Comment repository interface."""

from abc import ABC, abstractmethod

from src.community.domain.entities import Comment
from src.community.domain.value_objects import CommentId, PostId


class ICommentRepository(ABC):
    """
    Interface for Comment persistence operations.

    Implementations handle database operations for Comment aggregate.
    """

    @abstractmethod
    async def save(self, comment: Comment) -> None:
        """
        Save a comment (create or update).

        Args:
            comment: The comment entity to save
        """
        ...

    @abstractmethod
    async def get_by_id(self, comment_id: CommentId) -> Comment | None:
        """
        Get a comment by ID.

        Args:
            comment_id: The comment's ID

        Returns:
            Comment if found and not deleted, None otherwise
        """
        ...

    @abstractmethod
    async def list_by_post(
        self,
        post_id: PostId,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Comment]:
        """
        List comments for a post.

        Args:
            post_id: The post ID
            limit: Maximum number of comments to return
            offset: Number of comments to skip

        Returns:
            List of comments ordered by created_at ascending
        """
        ...

    @abstractmethod
    async def count_by_post(self, post_id: PostId) -> int:
        """
        Count total comments for a post.

        Args:
            post_id: The post ID

        Returns:
            Total comment count (excluding deleted)
        """
        ...

    @abstractmethod
    async def has_replies(self, comment_id: CommentId) -> bool:
        """
        Check if a comment has any replies.

        Args:
            comment_id: The comment ID

        Returns:
            True if comment has replies, False otherwise
        """
        ...

    @abstractmethod
    async def delete(self, comment_id: CommentId) -> None:
        """
        Delete a comment by ID (hard delete).

        Args:
            comment_id: The ID of the comment to delete
        """
        ...

    @abstractmethod
    async def delete_by_post(self, post_id: PostId) -> None:
        """
        Delete all comments for a post (cascade delete).

        Args:
            post_id: The post ID
        """
        ...
