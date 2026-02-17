"""FastAPI dependencies for Gamification context."""

from typing import Annotated

from fastapi import Depends

from src.gamification.application.commands.award_points import AwardPointsHandler
from src.gamification.application.commands.deduct_points import DeductPointsHandler
from src.gamification.application.commands.set_course_level_requirement import (
    SetCourseLevelRequirementHandler,
)
from src.gamification.application.commands.update_level_config import UpdateLevelConfigHandler
from src.gamification.application.queries.check_course_access import CheckCourseAccessHandler
from src.gamification.application.queries.get_level_definitions import GetLevelDefinitionsHandler
from src.gamification.application.queries.get_member_level import GetMemberLevelHandler
from src.gamification.infrastructure.persistence.course_level_requirement_repository import (
    SqlAlchemyCourseLevelRequirementRepository,
)
from src.gamification.infrastructure.persistence.level_config_repository import (
    SqlAlchemyLevelConfigRepository,
)
from src.gamification.infrastructure.persistence.member_points_repository import (
    SqlAlchemyMemberPointsRepository,
)
from src.identity.interface.api.dependencies import SessionDep


def get_member_points_repo(session: SessionDep) -> SqlAlchemyMemberPointsRepository:
    """Get member points repository."""
    return SqlAlchemyMemberPointsRepository(session)


def get_level_config_repo(session: SessionDep) -> SqlAlchemyLevelConfigRepository:
    """Get level config repository."""
    return SqlAlchemyLevelConfigRepository(session)


def get_course_req_repo(session: SessionDep) -> SqlAlchemyCourseLevelRequirementRepository:
    """Get course level requirement repository."""
    return SqlAlchemyCourseLevelRequirementRepository(session)


MemberPointsRepoDep = Annotated[SqlAlchemyMemberPointsRepository, Depends(get_member_points_repo)]
LevelConfigRepoDep = Annotated[SqlAlchemyLevelConfigRepository, Depends(get_level_config_repo)]
CourseReqRepoDep = Annotated[
    SqlAlchemyCourseLevelRequirementRepository, Depends(get_course_req_repo)
]


def get_get_member_level_handler(
    mp_repo: MemberPointsRepoDep,
    lc_repo: LevelConfigRepoDep,
) -> GetMemberLevelHandler:
    """Get member level query handler."""
    return GetMemberLevelHandler(member_points_repo=mp_repo, level_config_repo=lc_repo)


def get_get_level_definitions_handler(
    mp_repo: MemberPointsRepoDep,
    lc_repo: LevelConfigRepoDep,
) -> GetLevelDefinitionsHandler:
    """Get level definitions query handler."""
    return GetLevelDefinitionsHandler(member_points_repo=mp_repo, level_config_repo=lc_repo)


def get_update_level_config_handler(
    mp_repo: MemberPointsRepoDep,
    lc_repo: LevelConfigRepoDep,
) -> UpdateLevelConfigHandler:
    """Get update level config command handler."""
    return UpdateLevelConfigHandler(member_points_repo=mp_repo, level_config_repo=lc_repo)


def get_check_course_access_handler(
    cr_repo: CourseReqRepoDep,
    mp_repo: MemberPointsRepoDep,
    lc_repo: LevelConfigRepoDep,
) -> CheckCourseAccessHandler:
    """Get check course access query handler."""
    return CheckCourseAccessHandler(
        course_req_repo=cr_repo, member_points_repo=mp_repo, level_config_repo=lc_repo
    )


def get_set_course_level_requirement_handler(
    cr_repo: CourseReqRepoDep,
    mp_repo: MemberPointsRepoDep,
    lc_repo: LevelConfigRepoDep,
) -> SetCourseLevelRequirementHandler:
    """Get set course level requirement command handler."""
    return SetCourseLevelRequirementHandler(
        course_req_repo=cr_repo, member_points_repo=mp_repo, level_config_repo=lc_repo
    )


def get_award_handler(
    mp_repo: MemberPointsRepoDep,
    lc_repo: LevelConfigRepoDep,
) -> AwardPointsHandler:
    """Get award points handler."""
    return AwardPointsHandler(member_points_repo=mp_repo, level_config_repo=lc_repo)


def get_deduct_handler(
    mp_repo: MemberPointsRepoDep,
    lc_repo: LevelConfigRepoDep,
) -> DeductPointsHandler:
    """Get deduct points handler."""
    return DeductPointsHandler(member_points_repo=mp_repo, level_config_repo=lc_repo)
