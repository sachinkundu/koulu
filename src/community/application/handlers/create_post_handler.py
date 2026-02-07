"""Create post command handler."""

import structlog

from src.community.application.commands import CreatePostCommand
from src.community.domain.entities import Post
from src.community.domain.exceptions import (
    CategoryNotFoundError,
    NotCommunityMemberError,
)
from src.community.domain.repositories import (
    ICategoryRepository,
    IMemberRepository,
    IPostRepository,
)
from src.community.domain.value_objects import (
    CategoryId,
    CommunityId,
    PostContent,
    PostId,
    PostTitle,
)
from src.identity.domain.value_objects import UserId
from src.shared.infrastructure import event_bus

logger = structlog.get_logger()


class CreatePostHandler:
    """Handler for creating posts."""

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

    async def handle(self, command: CreatePostCommand) -> PostId:
        """
        Handle post creation.

        Args:
            command: The create post command

        Returns:
            The created post's ID

        Raises:
            NotCommunityMemberError: If author is not a member
            CategoryNotFoundError: If category doesn't exist
            PostTitleRequiredError: If title is invalid
            PostContentRequiredError: If content is invalid
            InvalidImageUrlError: If image URL is not HTTPS
        """
        logger.info(
            "create_post_attempt",
            author_id=str(command.author_id),
            community_id=str(command.community_id),
        )

        # Convert to value objects
        community_id = CommunityId(command.community_id)
        author_id = UserId(command.author_id)

        # Check author is a member of the community
        member = await self._member_repository.get_by_user_and_community(author_id, community_id)
        if member is None:
            logger.warning("create_post_not_member", author_id=str(author_id))
            raise NotCommunityMemberError()

        # Resolve category
        if command.category_id is not None:
            category_id = CategoryId(command.category_id)
            category = await self._category_repository.get_by_id(category_id)
        elif command.category_name is not None:
            category = await self._category_repository.get_by_name(
                community_id, command.category_name
            )
        else:
            # Default to first category (should be "General")
            categories = await self._category_repository.list_by_community(community_id)
            category = categories[0] if categories else None

        if category is None:
            logger.warning("create_post_category_not_found", category_name=command.category_name)
            raise CategoryNotFoundError(command.category_name)

        # Validate and create value objects (will raise if invalid)
        title = PostTitle(command.title)
        content = PostContent(command.content)

        # Create post
        post = Post.create(
            community_id=community_id,
            author_id=author_id,
            category_id=category.id,
            title=title,
            content=content,
            image_url=command.image_url,
        )

        # Save post
        await self._post_repository.save(post)

        # Publish domain events
        await event_bus.publish_all(post.clear_events())

        logger.info("create_post_success", post_id=str(post.id))
        return post.id
