"""Get post comments query handler."""

from dataclasses import dataclass

import structlog

from src.community.application.queries import GetPostCommentsQuery
from src.community.domain.entities import Comment
from src.community.domain.repositories import ICommentRepository, IReactionRepository
from src.community.domain.value_objects import PostId

logger = structlog.get_logger()


@dataclass
class CommentWithLikes:
    """Comment with its like count."""

    comment: Comment
    like_count: int


class GetPostCommentsHandler:
    """Handler for getting post comments."""

    def __init__(
        self,
        comment_repository: ICommentRepository,
        reaction_repository: IReactionRepository,
    ) -> None:
        """Initialize with dependencies."""
        self._comment_repository = comment_repository
        self._reaction_repository = reaction_repository

    async def handle(self, query: GetPostCommentsQuery) -> list[CommentWithLikes]:
        """
        Handle getting comments for a post.

        Args:
            query: The get post comments query

        Returns:
            List of comments with their like counts
        """
        logger.info(
            "get_post_comments_attempt",
            post_id=str(query.post_id),
            limit=query.limit,
            offset=query.offset,
        )

        post_id = PostId(query.post_id)

        # Load comments
        comments = await self._comment_repository.list_by_post(
            post_id=post_id,
            limit=query.limit,
            offset=query.offset,
        )

        # Get like counts for each comment
        result = []
        for comment in comments:
            like_count = await self._reaction_repository.count_by_target(
                target_type="comment",
                target_id=comment.id.value,
            )
            result.append(CommentWithLikes(comment=comment, like_count=like_count))

        logger.info("get_post_comments_success", post_id=str(query.post_id), count=len(result))
        return result
