"""Set course level requirement command and handler."""

from dataclasses import dataclass
from uuid import UUID

import structlog

from src.gamification.domain.entities.course_level_requirement import CourseLevelRequirement
from src.gamification.domain.repositories import (
    ICourseLevelRequirementRepository,
    ILevelConfigRepository,
    IMemberPointsRepository,
)

logger = structlog.get_logger()


@dataclass(frozen=True)
class SetCourseLevelRequirementCommand:
    """Command to set minimum level requirement for a course."""

    community_id: UUID
    course_id: UUID
    admin_user_id: UUID
    minimum_level: int


class SetCourseLevelRequirementHandler:
    """Handler for setting course level requirements."""

    def __init__(
        self,
        course_req_repo: ICourseLevelRequirementRepository,
        member_points_repo: IMemberPointsRepository,
        level_config_repo: ILevelConfigRepository,
    ) -> None:
        self._course_req_repo = course_req_repo
        self._member_points_repo = member_points_repo
        self._level_config_repo = level_config_repo

    async def handle(self, command: SetCourseLevelRequirementCommand) -> None:
        # Get or create requirement
        req = await self._course_req_repo.get_by_community_and_course(
            command.community_id, command.course_id
        )

        if req is None:
            req = CourseLevelRequirement.create(
                community_id=command.community_id,
                course_id=command.course_id,
                minimum_level=command.minimum_level,
            )
        else:
            req.update_minimum_level(command.minimum_level)

        await self._course_req_repo.save(req)

        logger.info(
            "course_level_requirement_set",
            community_id=str(command.community_id),
            course_id=str(command.course_id),
            minimum_level=command.minimum_level,
            admin_user_id=str(command.admin_user_id),
        )
