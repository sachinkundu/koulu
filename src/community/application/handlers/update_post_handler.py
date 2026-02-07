"""Update post command handler."""

import structlog

from src.community.application.commands import UpdatePostCommand
from src.community.domain.exceptions import (
    NotCommunityMemberError,
    PostNotFoundError,
)
from src.community.domain.repositories import (
    ICategoryRepository,
    IMemberRepository,
    IPostRepository,
)
from src.community.domain.value_objects import CategoryId, PostContent, PostId, PostTitle
from src.identity.domain.value_objects import UserId
from src.shared.infrastructure import event_bus

logger = structlog.get_logger()


class UpdatePostHandler:
    """Handler for updating posts."""

    def __init__(
        self,
        post_repository: IPostRepository,
        category_repository: ICategoryRepository,
        member_repository: IMemberRepository,
    ) -> None:
        """Initialize with dependencies."""
        self._post_repository = post_repository
        self._category_repository = category_repository
        self._member_repository = member_repository

    async def handle(self, command: UpdatePostCommand) -> None:
        """
        Handle post update.

        Args:
            command: The update post command

        Raises:
            PostNotFoundError: If post doesn't exist
            NotCommunityMemberError: If editor is not a member
            NotPostAuthorError: If editor is not author and lacks permission
            PostAlreadyDeletedError: If post is deleted
        """
        logger.info(
            "update_post_attempt",
            post_id=str(command.post_id),
            editor_id=str(command.editor_id),
        )

        post_id = PostId(command.post_id)
        editor_id = UserId(command.editor_id)

        # Get the post
        post = await self._post_repository.get_by_id(post_id)
        if post is None:
            logger.warning("update_post_not_found", post_id=str(post_id))
            raise PostNotFoundError(str(post_id))

        # Get editor's membership
        member = await self._member_repository.get_by_user_and_community(
            editor_id, post.community_id
        )
        if member is None:
            logger.warning("update_post_not_member", editor_id=str(editor_id))
            raise NotCommunityMemberError()

        # Build update parameters
        title = PostTitle(command.title) if command.title is not None else None
        content = PostContent(command.content) if command.content is not None else None
        category_id = CategoryId(command.category_id) if command.category_id is not None else None

        # Edit the post (domain layer checks permissions)
        changed_fields = post.edit(
            editor_id=editor_id,
            editor_role=member.role,
            title=title,
            content=content,
            image_url=command.image_url,
            category_id=category_id,
        )

        # Save if anything changed
        if changed_fields:
            await self._post_repository.save(post)
            await event_bus.publish_all(post.clear_events())
            logger.info("update_post_success", post_id=str(post_id), changed_fields=changed_fields)
        else:
            logger.info("update_post_no_changes", post_id=str(post_id))
