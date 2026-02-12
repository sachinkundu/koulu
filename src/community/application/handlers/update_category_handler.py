"""Update category command handler."""

import structlog

from src.community.application.commands import UpdateCategoryCommand
from src.community.domain.exceptions import (
    CannotManageCategoriesError,
    CategoryNameExistsError,
    CategoryNotFoundError,
    NotCommunityMemberError,
)
from src.community.domain.repositories import ICategoryRepository, IMemberRepository
from src.community.domain.value_objects import CategoryId, CommunityId
from src.identity.domain.value_objects import UserId

logger = structlog.get_logger()


class UpdateCategoryHandler:
    """Handler for updating categories."""

    def __init__(
        self,
        category_repository: ICategoryRepository,
        member_repository: IMemberRepository,
    ) -> None:
        self._category_repository = category_repository
        self._member_repository = member_repository

    async def handle(self, command: UpdateCategoryCommand) -> None:
        """Handle update category command."""
        logger.info("update_category_attempt", category_id=str(command.category_id))

        community_id = CommunityId(command.community_id)
        updater_id = UserId(command.updater_id)

        member = await self._member_repository.get_by_user_and_community(updater_id, community_id)
        if member is None:
            raise NotCommunityMemberError()

        if not member.role.can_manage_categories():
            raise CannotManageCategoriesError()

        category_id = CategoryId(command.category_id)
        category = await self._category_repository.get_by_id(category_id)
        if category is None:
            raise CategoryNotFoundError()

        # Check name uniqueness if name is being changed
        if (
            command.name is not None
            and command.name != category.name
            and await self._category_repository.exists_by_name(community_id, command.name)
        ):
            raise CategoryNameExistsError()

        category.update(
            name=command.name,
            emoji=command.emoji,
            description=command.description,
        )

        await self._category_repository.save(category)
        logger.info("update_category_success", category_id=str(category_id))
