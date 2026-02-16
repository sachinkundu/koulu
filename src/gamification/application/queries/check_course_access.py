"""CheckCourseAccess query and handler."""

from dataclasses import dataclass
from uuid import UUID

from src.gamification.domain.entities.level_configuration import LevelConfiguration
from src.gamification.domain.repositories import (
    ICourseLevelRequirementRepository,
    ILevelConfigRepository,
    IMemberPointsRepository,
)


@dataclass(frozen=True)
class CheckCourseAccessQuery:
    community_id: UUID
    course_id: UUID
    user_id: UUID


@dataclass
class CourseAccessResult:
    course_id: UUID
    has_access: bool
    minimum_level: int | None
    minimum_level_name: str | None
    current_level: int


class CheckCourseAccessHandler:
    def __init__(
        self,
        course_req_repo: ICourseLevelRequirementRepository,
        member_points_repo: IMemberPointsRepository,
        level_config_repo: ILevelConfigRepository,
    ) -> None:
        self._course_req_repo = course_req_repo
        self._member_points_repo = member_points_repo
        self._level_config_repo = level_config_repo

    async def handle(self, query: CheckCourseAccessQuery) -> CourseAccessResult:
        # Get member's current level
        mp = await self._member_points_repo.get_by_community_and_user(
            query.community_id, query.user_id
        )
        current_level = mp.current_level if mp else 1

        # Get course level requirement
        req = await self._course_req_repo.get_by_community_and_course(
            query.community_id, query.course_id
        )

        if req is None:
            # No level requirement — accessible to all
            return CourseAccessResult(
                course_id=query.course_id,
                has_access=True,
                minimum_level=None,
                minimum_level_name=None,
                current_level=current_level,
            )

        # Get level config for name lookup
        config = await self._level_config_repo.get_by_community(query.community_id)
        if config is None:
            config = LevelConfiguration.create_default(query.community_id)

        has_access = current_level >= req.minimum_level
        level_name = config.name_for_level(req.minimum_level)

        return CourseAccessResult(
            course_id=query.course_id,
            has_access=has_access,
            minimum_level=req.minimum_level,
            minimum_level_name=level_name,
            current_level=current_level,
        )
