"""Update level configuration command and handler."""

from dataclasses import dataclass
from uuid import UUID

import structlog

from src.gamification.domain.entities.level_configuration import LevelConfiguration, LevelDefinition
from src.gamification.domain.repositories import ILevelConfigRepository, IMemberPointsRepository
from src.shared.infrastructure import event_bus

logger = structlog.get_logger()


@dataclass(frozen=True)
class LevelUpdate:
    """A single level update."""

    level: int
    name: str
    threshold: int


@dataclass(frozen=True)
class UpdateLevelConfigCommand:
    """Command to update level configuration for a community."""

    community_id: UUID
    admin_user_id: UUID
    levels: list[LevelUpdate]


class UpdateLevelConfigHandler:
    """Handler for updating level configuration."""

    def __init__(
        self,
        member_points_repo: IMemberPointsRepository,
        level_config_repo: ILevelConfigRepository,
    ) -> None:
        self._member_points_repo = member_points_repo
        self._level_config_repo = level_config_repo

    async def handle(self, command: UpdateLevelConfigCommand) -> None:
        # Get or create level config
        config = await self._level_config_repo.get_by_community(command.community_id)
        if config is None:
            config = LevelConfiguration.create_default(command.community_id)
            await self._level_config_repo.save(config)

        # Remember old thresholds for comparison
        old_thresholds = {ld.level: ld.threshold for ld in config.levels}

        # Build new LevelDefinitions from command
        new_levels = [
            LevelDefinition(level=lu.level, name=lu.name, threshold=lu.threshold)
            for lu in command.levels
        ]

        # Call config.update_levels() (validates)
        config.update_levels(new_levels)

        # Save config
        await self._level_config_repo.save(config)

        # Check if thresholds changed
        new_thresholds = {ld.level: ld.threshold for ld in config.levels}
        thresholds_changed = old_thresholds != new_thresholds

        if thresholds_changed:
            # Recalculate all member levels
            all_members = await self._member_points_repo.list_by_community(command.community_id)
            for mp in all_members:
                mp.recalculate_level(config)
                await self._member_points_repo.save(mp)
                # Publish any MemberLeveledUp events
                events = mp.clear_events()
                if events:
                    await event_bus.publish_all(events)

        logger.info(
            "level_config_updated",
            community_id=str(command.community_id),
            admin_user_id=str(command.admin_user_id),
            thresholds_changed=thresholds_changed,
        )
