"""List categories query handler."""

import structlog

from src.community.application.queries import ListCategoriesQuery
from src.community.domain.entities import Category
from src.community.domain.repositories import ICategoryRepository
from src.community.domain.value_objects import CommunityId

logger = structlog.get_logger()


class ListCategoriesHandler:
    """Handler for listing categories in a community."""

    def __init__(
        self,
        category_repository: ICategoryRepository,
    ) -> None:
        """Initialize with dependencies."""
        self._category_repository = category_repository

    async def handle(self, query: ListCategoriesQuery) -> list[Category]:
        """
        Handle listing categories.

        Args:
            query: The list categories query

        Returns:
            List of category entities
        """
        logger.info("list_categories_attempt", community_id=str(query.community_id))

        community_id = CommunityId(query.community_id)
        categories = await self._category_repository.list_by_community(community_id)

        logger.info(
            "list_categories_success", community_id=str(community_id), count=len(categories)
        )
        return categories
