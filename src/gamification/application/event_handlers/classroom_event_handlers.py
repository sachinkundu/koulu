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
from src.gamification.infrastructure.persistence.level_config_repository import (
    SqlAlchemyLevelConfigRepository,
)
from src.gamification.infrastructure.persistence.member_points_repository import (
    SqlAlchemyMemberPointsRepository,
)

logger = structlog.get_logger()


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

    from src.identity.interface.api.dependencies import get_database

    db = get_database()
    session = db._session_factory()  # noqa: SLF001
    try:
        mp_repo = SqlAlchemyMemberPointsRepository(session)
        lc_repo = SqlAlchemyLevelConfigRepository(session)
        handler = AwardPointsHandler(member_points_repo=mp_repo, level_config_repo=lc_repo)
        await handler.handle(
            AwardPointsCommand(
                community_id=community_id,
                user_id=event.user_id.value,
                source=PointSource.LESSON_COMPLETED,
                source_id=event.lesson_id.value,
            )
        )
        await session.commit()
    except Exception:
        await session.rollback()
        logger.exception("gamification.lesson_completed_failed")
    finally:
        await session.close()
