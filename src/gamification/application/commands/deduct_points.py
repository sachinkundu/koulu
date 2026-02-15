"""Deduct points command and handler."""

from dataclasses import dataclass
from uuid import UUID

import structlog

from src.gamification.domain.entities.level_configuration import LevelConfiguration
from src.gamification.domain.repositories import ILevelConfigRepository, IMemberPointsRepository
from src.gamification.domain.value_objects.point_source import PointSource
from src.shared.infrastructure import event_bus

logger = structlog.get_logger()


@dataclass(frozen=True)
class DeductPointsCommand:
    """Command to deduct points from a member."""

    community_id: UUID
    user_id: UUID
    source: PointSource
    source_id: UUID


class DeductPointsHandler:
    """Handler for deducting points."""

    def __init__(
        self,
        member_points_repo: IMemberPointsRepository,
        level_config_repo: ILevelConfigRepository,
    ) -> None:
        self._member_points_repo = member_points_repo
        self._level_config_repo = level_config_repo

    async def handle(self, command: DeductPointsCommand) -> None:
        # Get member points - if not found, nothing to deduct
        mp = await self._member_points_repo.get_by_community_and_user(
            command.community_id, command.user_id
        )
        if mp is None:
            logger.info(
                "deduct_points_skip_no_member",
                user_id=str(command.user_id),
                community_id=str(command.community_id),
            )
            return

        # Get level config
        config = await self._level_config_repo.get_by_community(command.community_id)
        if config is None:
            config = LevelConfiguration.create_default(command.community_id)

        # Deduct points
        mp.deduct_points(
            source=command.source,
            source_id=command.source_id,
            level_config=config,
        )

        # Persist
        await self._member_points_repo.save(mp)

        # Publish events
        await event_bus.publish_all(mp.clear_events())

        logger.info(
            "points_deducted",
            user_id=str(command.user_id),
            community_id=str(command.community_id),
            source=command.source.source_name,
            points=command.source.points,
            new_total=mp.total_points,
        )
