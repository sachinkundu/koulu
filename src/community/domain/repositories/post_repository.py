"""Post repository interface."""

from abc import ABC, abstractmethod

from src.community.domain.entities import Post
from src.community.domain.value_objects import CategoryId, CommunityId, PostId


class IPostRepository(ABC):
    """
    Interface for Post persistence operations.

    Implementations handle database operations for Post aggregate.
    """

    @abstractmethod
    async def save(self, post: Post) -> None:
        """
        Save a post (create or update).

        Args:
            post: The post entity to save
        """
        ...

    @abstractmethod
    async def get_by_id(self, post_id: PostId) -> Post | None:
        """
        Get a post by ID.

        Args:
            post_id: The post's ID

        Returns:
            Post if found and not deleted, None otherwise
        """
        ...

    @abstractmethod
    async def get_by_id_include_deleted(self, post_id: PostId) -> Post | None:
        """
        Get a post by ID including deleted posts.

        Args:
            post_id: The post's ID

        Returns:
            Post if found, None otherwise
        """
        ...

    @abstractmethod
    async def list_by_community(
        self,
        community_id: CommunityId,
        category_id: CategoryId | None = None,
        limit: int = 20,
        offset: int = 0,
        sort: str = "new",
        cursor: str | None = None,
    ) -> list[Post]:
        """
        List posts in a community.

        Args:
            community_id: The community ID
            category_id: Optional category filter
            limit: Maximum number of posts to return
            offset: Number of posts to skip
            sort: Sort order - "new", "top", or "hot"
            cursor: Base64-encoded cursor for pagination

        Returns:
            List of posts (excluding deleted)
        """
        ...

    @abstractmethod
    async def count_by_category(self, category_id: CategoryId) -> int:
        """
        Count posts in a category.

        Args:
            category_id: The category ID

        Returns:
            Number of non-deleted posts in the category
        """
        ...

    @abstractmethod
    async def delete(self, post_id: PostId) -> None:
        """
        Delete a post by ID (hard delete).

        Args:
            post_id: The ID of the post to delete
        """
        ...
