"""GetMemberLevel query and handler."""

from dataclasses import dataclass
from uuid import UUID

from src.gamification.domain.entities.level_configuration import LevelConfiguration
from src.gamification.domain.repositories import ILevelConfigRepository, IMemberPointsRepository


@dataclass(frozen=True)
class GetMemberLevelQuery:
    community_id: UUID
    user_id: UUID
    requesting_user_id: UUID


@dataclass
class MemberLevelResult:
    user_id: UUID
    level: int
    level_name: str
    total_points: int
    points_to_next_level: int | None
    is_max_level: bool


class GetMemberLevelHandler:
    def __init__(
        self,
        member_points_repo: IMemberPointsRepository,
        level_config_repo: ILevelConfigRepository,
    ) -> None:
        self._member_points_repo = member_points_repo
        self._level_config_repo = level_config_repo

    async def handle(self, query: GetMemberLevelQuery) -> MemberLevelResult:
        config = await self._level_config_repo.get_by_community(query.community_id)
        if config is None:
            config = LevelConfiguration.create_default(query.community_id)

        mp = await self._member_points_repo.get_by_community_and_user(
            query.community_id, query.user_id
        )

        total_points = mp.total_points if mp else 0
        current_level = mp.current_level if mp else 1
        is_max_level = current_level >= 9
        is_own_profile = query.user_id == query.requesting_user_id

        points_to_next: int | None = None
        if is_own_profile and not is_max_level:
            points_to_next = config.points_to_next_level(current_level, total_points)

        return MemberLevelResult(
            user_id=query.user_id,
            level=current_level,
            level_name=config.name_for_level(current_level),
            total_points=total_points,
            points_to_next_level=points_to_next,
            is_max_level=is_max_level,
        )
