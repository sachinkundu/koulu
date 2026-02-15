"""Event handlers for Community context events."""

import structlog

from src.community.domain.events import (
    CommentAdded,
    CommentLiked,
    CommentUnliked,
    PostCreated,
    PostLiked,
    PostUnliked,
)
from src.gamification.application.commands.award_points import (
    AwardPointsCommand,
    AwardPointsHandler,
)
from src.gamification.application.commands.deduct_points import (
    DeductPointsCommand,
    DeductPointsHandler,
)
from src.gamification.domain.value_objects.point_source import PointSource

logger = structlog.get_logger()


def _get_award_handler() -> AwardPointsHandler:
    """Get an AwardPointsHandler with a fresh DB session."""
    from src.gamification.interface.api.dependencies import create_award_handler

    return create_award_handler()


def _get_deduct_handler() -> DeductPointsHandler:
    """Get a DeductPointsHandler with a fresh DB session."""
    from src.gamification.interface.api.dependencies import create_deduct_handler

    return create_deduct_handler()


async def handle_post_created(event: PostCreated) -> None:
    """Award 2 points to post author."""
    logger.info("gamification.post_created", post_id=str(event.post_id), author_id=str(event.author_id))
    handler = _get_award_handler()
    await handler.handle(
        AwardPointsCommand(
            community_id=event.community_id.value,
            user_id=event.author_id.value,
            source=PointSource.POST_CREATED,
            source_id=event.post_id.value,
        )
    )


async def handle_post_liked(event: PostLiked) -> None:
    """Award 1 point to post author (not the liker)."""
    logger.info("gamification.post_liked", post_id=str(event.post_id), author_id=str(event.author_id))
    handler = _get_award_handler()
    await handler.handle(
        AwardPointsCommand(
            community_id=event.community_id.value,
            user_id=event.author_id.value,
            source=PointSource.POST_LIKED,
            source_id=event.post_id.value,
        )
    )


async def handle_post_unliked(event: PostUnliked) -> None:
    """Deduct 1 point from post author."""
    logger.info("gamification.post_unliked", post_id=str(event.post_id), author_id=str(event.author_id))
    handler = _get_deduct_handler()
    await handler.handle(
        DeductPointsCommand(
            community_id=event.community_id.value,
            user_id=event.author_id.value,
            source=PointSource.POST_LIKED,
            source_id=event.post_id.value,
        )
    )


async def handle_comment_added(event: CommentAdded) -> None:
    """Award 1 point to comment author."""
    logger.info("gamification.comment_added", comment_id=str(event.comment_id), author_id=str(event.author_id))
    handler = _get_award_handler()
    await handler.handle(
        AwardPointsCommand(
            community_id=event.community_id.value,
            user_id=event.author_id.value,
            source=PointSource.COMMENT_CREATED,
            source_id=event.comment_id.value,
        )
    )


async def handle_comment_liked(event: CommentLiked) -> None:
    """Award 1 point to comment author (not the liker)."""
    logger.info("gamification.comment_liked", comment_id=str(event.comment_id), author_id=str(event.author_id))
    handler = _get_award_handler()
    await handler.handle(
        AwardPointsCommand(
            community_id=event.community_id.value,
            user_id=event.author_id.value,
            source=PointSource.COMMENT_LIKED,
            source_id=event.comment_id.value,
        )
    )


async def handle_comment_unliked(event: CommentUnliked) -> None:
    """Deduct 1 point from comment author."""
    logger.info("gamification.comment_unliked", comment_id=str(event.comment_id), author_id=str(event.author_id))
    handler = _get_deduct_handler()
    await handler.handle(
        DeductPointsCommand(
            community_id=event.community_id.value,
            user_id=event.author_id.value,
            source=PointSource.COMMENT_LIKED,
            source_id=event.comment_id.value,
        )
    )
