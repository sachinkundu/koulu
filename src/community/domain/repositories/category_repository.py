"""Category repository interface."""

from abc import ABC, abstractmethod

from src.community.domain.entities import Category
from src.community.domain.value_objects import CategoryId, CommunityId


class ICategoryRepository(ABC):
    """
    Interface for Category persistence operations.

    Implementations handle database operations for Category entity.
    """

    @abstractmethod
    async def save(self, category: Category) -> None:
        """
        Save a category (create or update).

        Args:
            category: The category entity to save
        """
        ...

    @abstractmethod
    async def get_by_id(self, category_id: CategoryId) -> Category | None:
        """
        Get a category by ID.

        Args:
            category_id: The category's ID

        Returns:
            Category if found, None otherwise
        """
        ...

    @abstractmethod
    async def get_by_name(self, community_id: CommunityId, name: str) -> Category | None:
        """
        Get a category by name within a community.

        Args:
            community_id: The community ID
            name: The category name

        Returns:
            Category if found, None otherwise
        """
        ...

    @abstractmethod
    async def get_by_slug(self, community_id: CommunityId, slug: str) -> Category | None:
        """
        Get a category by slug within a community.

        Args:
            community_id: The community ID
            slug: The category slug

        Returns:
            Category if found, None otherwise
        """
        ...

    @abstractmethod
    async def list_by_community(self, community_id: CommunityId) -> list[Category]:
        """
        List all categories in a community.

        Args:
            community_id: The community ID

        Returns:
            List of categories
        """
        ...

    @abstractmethod
    async def exists_by_name(self, community_id: CommunityId, name: str) -> bool:
        """
        Check if a category with the given name exists.

        Args:
            community_id: The community ID
            name: The category name

        Returns:
            True if exists, False otherwise
        """
        ...

    @abstractmethod
    async def delete(self, category_id: CategoryId) -> None:
        """
        Delete a category by ID.

        Args:
            category_id: The ID of the category to delete
        """
        ...
