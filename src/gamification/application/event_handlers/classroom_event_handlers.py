"""Event handlers for Classroom context events."""

from uuid import UUID

import structlog
from sqlalchemy import text

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


async def _resolve_community_id() -> UUID | None:
    """Resolve the community_id for the platform.

    In a single-community Skool clone, courses belong to the one community.
    This queries the first active community as a default resolution.
    """
    from src.identity.interface.api.dependencies import get_database

    db = get_database()
    session = db._session_factory()  # noqa: SLF001
    try:
        result = await session.execute(text("SELECT id FROM communities LIMIT 1"))
        row = result.scalar_one_or_none()
        return UUID(str(row)) if row is not None else None
    finally:
        await session.close()


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
