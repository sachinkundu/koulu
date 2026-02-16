"""Award points command and handler."""

from dataclasses import dataclass
from uuid import UUID

import structlog

from src.gamification.domain.entities.level_configuration import LevelConfiguration
from src.gamification.domain.entities.member_points import MemberPoints
from src.gamification.domain.repositories import ILevelConfigRepository, IMemberPointsRepository
from src.gamification.domain.value_objects.point_source import PointSource
from src.shared.infrastructure import event_bus

logger = structlog.get_logger()


@dataclass(frozen=True)
class AwardPointsCommand:
    """Command to award points to a member."""

    community_id: UUID
    user_id: UUID
    source: PointSource
    source_id: UUID


class AwardPointsHandler:
    """Handler for awarding points."""

    def __init__(
        self,
        member_points_repo: IMemberPointsRepository,
        level_config_repo: ILevelConfigRepository,
    ) -> None:
        self._member_points_repo = member_points_repo
        self._level_config_repo = level_config_repo

    async def handle(self, command: AwardPointsCommand) -> None:
        # Get or create level config (lazy init)
        config = await self._level_config_repo.get_by_community(command.community_id)
        if config is None:
            config = LevelConfiguration.create_default(command.community_id)
            await self._level_config_repo.save(config)

        # Get or create member points
        mp = await self._member_points_repo.get_by_community_and_user(
            command.community_id, command.user_id
        )
        if mp is None:
            mp = MemberPoints.create(community_id=command.community_id, user_id=command.user_id)

        # Award points
        mp.award_points(
            source=command.source,
            source_id=command.source_id,
            level_config=config,
        )

        # Persist
        await self._member_points_repo.save(mp)

        # Publish events
        await event_bus.publish_all(mp.clear_events())

        logger.info(
            "points_awarded",
            user_id=str(command.user_id),
            community_id=str(command.community_id),
            source=command.source.source_name,
            points=command.source.points,
            new_total=mp.total_points,
        )
