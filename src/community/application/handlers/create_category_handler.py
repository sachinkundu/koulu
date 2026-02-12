"""Create category command handler."""

import structlog

from src.community.application.commands import CreateCategoryCommand
from src.community.domain.entities import Category
from src.community.domain.exceptions import (
    CannotManageCategoriesError,
    CategoryNameExistsError,
    NotCommunityMemberError,
)
from src.community.domain.repositories import ICategoryRepository, IMemberRepository
from src.community.domain.value_objects import CommunityId
from src.identity.domain.value_objects import UserId

logger = structlog.get_logger()


class CreateCategoryHandler:
    """Handler for creating categories."""

    def __init__(
        self,
        category_repository: ICategoryRepository,
        member_repository: IMemberRepository,
    ) -> None:
        self._category_repository = category_repository
        self._member_repository = member_repository

    async def handle(self, command: CreateCategoryCommand) -> Category:
        """Handle create category command."""
        logger.info("create_category_attempt", creator_id=str(command.creator_id))

        community_id = CommunityId(command.community_id)
        creator_id = UserId(command.creator_id)

        member = await self._member_repository.get_by_user_and_community(creator_id, community_id)
        if member is None:
            raise NotCommunityMemberError()

        if not member.role.can_manage_categories():
            raise CannotManageCategoriesError()

        if await self._category_repository.exists_by_name(community_id, command.name):
            raise CategoryNameExistsError()

        category = Category.create(
            community_id=community_id,
            name=command.name,
            slug=command.slug,
            emoji=command.emoji,
            description=command.description,
        )

        await self._category_repository.save(category)
        logger.info("create_category_success", category_id=str(category.id))
        return category
