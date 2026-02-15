"""Event handlers for Classroom context events."""

import structlog

from src.classroom.domain.events.progress_events import LessonCompleted
from src.gamification.application.commands.award_points import (
    AwardPointsCommand,
    AwardPointsHandler,
)
from src.gamification.domain.value_objects.point_source import PointSource

logger = structlog.get_logger()


def _get_award_handler() -> AwardPointsHandler:
    """Get an AwardPointsHandler with a fresh DB session."""
    from src.gamification.interface.api.dependencies import create_award_handler

    return create_award_handler()


async def _resolve_community_id() -> object:
    """Resolve the community_id for the platform.

    In a single-community Skool clone, courses belong to the one community.
    This queries the first active community as a default resolution.
    """
    from sqlalchemy import select, text

    from src.shared.infrastructure.database import async_session_factory

    async with async_session_factory() as session:
        result = await session.execute(
            select(text("id")).select_from(text("communities")).limit(1)
        )
        row = result.scalar_one_or_none()
        return row


async def handle_lesson_completed(event: LessonCompleted) -> None:
    """Award 5 points to member who completed a lesson."""
    logger.info(
        "gamification.lesson_completed",
        user_id=str(event.user_id),
        course_id=str(event.course_id),
        lesson_id=str(event.lesson_id),
    )
    community_id = await _resolve_community_id()
    if community_id is None:
        logger.warning("gamification.lesson_completed.no_community")
        return

    handler = _get_award_handler()
    await handler.handle(
        AwardPointsCommand(
            community_id=community_id,
            user_id=event.user_id.value,
            source=PointSource.LESSON_COMPLETED,
            source_id=event.lesson_id.value,
        )
    )
