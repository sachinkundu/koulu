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
from src.gamification.infrastructure.persistence.level_config_repository import (
    SqlAlchemyLevelConfigRepository,
)
from src.gamification.infrastructure.persistence.member_points_repository import (
    SqlAlchemyMemberPointsRepository,
)

logger = structlog.get_logger()


async def _run_award(command: AwardPointsCommand) -> None:
    """Run award handler with a properly managed session."""
    from src.identity.interface.api.dependencies import get_database

    db = get_database()
    session = db._session_factory()  # noqa: SLF001
    try:
        mp_repo = SqlAlchemyMemberPointsRepository(session)
        lc_repo = SqlAlchemyLevelConfigRepository(session)
        handler = AwardPointsHandler(member_points_repo=mp_repo, level_config_repo=lc_repo)
        await handler.handle(command)
        await session.commit()
    except Exception:
        await session.rollback()
        logger.exception("gamification.award_points_failed", command=str(command))
    finally:
        await session.close()


async def _run_deduct(command: DeductPointsCommand) -> None:
    """Run deduct handler with a properly managed session."""
    from src.identity.interface.api.dependencies import get_database

    db = get_database()
    session = db._session_factory()  # noqa: SLF001
    try:
        mp_repo = SqlAlchemyMemberPointsRepository(session)
        lc_repo = SqlAlchemyLevelConfigRepository(session)
        handler = DeductPointsHandler(member_points_repo=mp_repo, level_config_repo=lc_repo)
        await handler.handle(command)
        await session.commit()
    except Exception:
        await session.rollback()
        logger.exception("gamification.deduct_points_failed", command=str(command))
    finally:
        await session.close()


async def handle_post_created(event: PostCreated) -> None:
    """Award 2 points to post author."""
    logger.info(
        "gamification.post_created", post_id=str(event.post_id), author_id=str(event.author_id)
    )
    await _run_award(
        AwardPointsCommand(
            community_id=event.community_id.value,
            user_id=event.author_id.value,
            source=PointSource.POST_CREATED,
            source_id=event.post_id.value,
        )
    )


async def handle_post_liked(event: PostLiked) -> None:
    """Award 1 point to post author (not the liker)."""
    logger.info(
        "gamification.post_liked", post_id=str(event.post_id), author_id=str(event.author_id)
    )
    await _run_award(
        AwardPointsCommand(
            community_id=event.community_id.value,
            user_id=event.author_id.value,
            source=PointSource.POST_LIKED,
            source_id=event.post_id.value,
        )
    )


async def handle_post_unliked(event: PostUnliked) -> None:
    """Deduct 1 point from post author."""
    logger.info(
        "gamification.post_unliked", post_id=str(event.post_id), author_id=str(event.author_id)
    )
    await _run_deduct(
        DeductPointsCommand(
            community_id=event.community_id.value,
            user_id=event.author_id.value,
            source=PointSource.POST_LIKED,
            source_id=event.post_id.value,
        )
    )


async def handle_comment_added(event: CommentAdded) -> None:
    """Award 1 point to comment author."""
    logger.info(
        "gamification.comment_added",
        comment_id=str(event.comment_id),
        author_id=str(event.author_id),
    )
    await _run_award(
        AwardPointsCommand(
            community_id=event.community_id.value,
            user_id=event.author_id.value,
            source=PointSource.COMMENT_CREATED,
            source_id=event.comment_id.value,
        )
    )


async def handle_comment_liked(event: CommentLiked) -> None:
    """Award 1 point to comment author (not the liker)."""
    logger.info(
        "gamification.comment_liked",
        comment_id=str(event.comment_id),
        author_id=str(event.author_id),
    )
    await _run_award(
        AwardPointsCommand(
            community_id=event.community_id.value,
            user_id=event.author_id.value,
            source=PointSource.COMMENT_LIKED,
            source_id=event.comment_id.value,
        )
    )


async def handle_comment_unliked(event: CommentUnliked) -> None:
    """Deduct 1 point from comment author."""
    logger.info(
        "gamification.comment_unliked",
        comment_id=str(event.comment_id),
        author_id=str(event.author_id),
    )
    await _run_deduct(
        DeductPointsCommand(
            community_id=event.community_id.value,
            user_id=event.author_id.value,
            source=PointSource.COMMENT_LIKED,
            source_id=event.comment_id.value,
        )
    )
