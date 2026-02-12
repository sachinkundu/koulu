"""Delete category command handler."""

import structlog

from src.community.application.commands import DeleteCategoryCommand
from src.community.domain.exceptions import (
    CannotManageCategoriesError,
    CategoryHasPostsError,
    CategoryNotFoundError,
    NotCommunityMemberError,
)
from src.community.domain.repositories import (
    ICategoryRepository,
    IMemberRepository,
    IPostRepository,
)
from src.community.domain.value_objects import CategoryId, CommunityId
from src.identity.domain.value_objects import UserId

logger = structlog.get_logger()


class DeleteCategoryHandler:
    """Handler for deleting categories."""

    def __init__(
        self,
        category_repository: ICategoryRepository,
        post_repository: IPostRepository,
        member_repository: IMemberRepository,
    ) -> None:
        self._category_repository = category_repository
        self._post_repository = post_repository
        self._member_repository = member_repository

    async def handle(self, command: DeleteCategoryCommand) -> None:
        """Handle delete category command."""
        logger.info("delete_category_attempt", category_id=str(command.category_id))

        community_id = CommunityId(command.community_id)
        deleter_id = UserId(command.deleter_id)

        member = await self._member_repository.get_by_user_and_community(deleter_id, community_id)
        if member is None:
            raise NotCommunityMemberError()

        if not member.role.can_manage_categories():
            raise CannotManageCategoriesError()

        category_id = CategoryId(command.category_id)
        category = await self._category_repository.get_by_id(category_id)
        if category is None:
            raise CategoryNotFoundError()

        # Check if category has posts
        post_count = await self._post_repository.count_by_category(category_id)
        if post_count > 0:
            raise CategoryHasPostsError()

        await self._category_repository.delete(category_id)
        logger.info("delete_category_success", category_id=str(category_id))
