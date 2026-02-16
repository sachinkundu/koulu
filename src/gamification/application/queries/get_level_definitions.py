"""GetLevelDefinitions query and handler."""

from dataclasses import dataclass
from uuid import UUID

from src.gamification.domain.entities.level_configuration import LevelConfiguration
from src.gamification.domain.repositories import ILevelConfigRepository, IMemberPointsRepository


@dataclass(frozen=True)
class GetLevelDefinitionsQuery:
    community_id: UUID
    requesting_user_id: UUID


@dataclass
class LevelDefinitionResult:
    level: int
    name: str
    threshold: int
    member_percentage: float


@dataclass
class LevelDefinitionsResult:
    levels: list[LevelDefinitionResult]
    current_user_level: int


class GetLevelDefinitionsHandler:
    def __init__(
        self,
        member_points_repo: IMemberPointsRepository,
        level_config_repo: ILevelConfigRepository,
    ) -> None:
        self._member_points_repo = member_points_repo
        self._level_config_repo = level_config_repo

    async def handle(self, query: GetLevelDefinitionsQuery) -> LevelDefinitionsResult:
        # Get or create default level config
        config = await self._level_config_repo.get_by_community(query.community_id)
        if config is None:
            config = LevelConfiguration.create_default(query.community_id)

        # Get all member points for community
        all_members = await self._member_points_repo.list_by_community(query.community_id)

        # Calculate distribution (% at each level)
        total_members = len(all_members)
        level_counts: dict[int, int] = {ld.level: 0 for ld in config.levels}

        for mp in all_members:
            level = mp.current_level
            if level in level_counts:
                level_counts[level] += 1

        # Build results
        level_results: list[LevelDefinitionResult] = []
        for ld in config.levels:
            count = level_counts.get(ld.level, 0)
            percentage = (count / total_members * 100) if total_members > 0 else 0.0
            level_results.append(
                LevelDefinitionResult(
                    level=ld.level,
                    name=ld.name,
                    threshold=ld.threshold,
                    member_percentage=round(percentage, 1),
                )
            )

        # Get requesting user's level
        requesting_mp = await self._member_points_repo.get_by_community_and_user(
            query.community_id, query.requesting_user_id
        )
        current_user_level = requesting_mp.current_level if requesting_mp else 1

        return LevelDefinitionsResult(
            levels=level_results,
            current_user_level=current_user_level,
        )
