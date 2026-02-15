"""FastAPI dependencies for Gamification context."""

from typing import Annotated

from fastapi import Depends

from src.gamification.application.commands.award_points import AwardPointsHandler
from src.gamification.application.commands.deduct_points import DeductPointsHandler
from src.gamification.application.queries.get_member_level import GetMemberLevelHandler
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


MemberPointsRepoDep = Annotated[SqlAlchemyMemberPointsRepository, Depends(get_member_points_repo)]
LevelConfigRepoDep = Annotated[SqlAlchemyLevelConfigRepository, Depends(get_level_config_repo)]


def get_get_member_level_handler(
    mp_repo: MemberPointsRepoDep,
    lc_repo: LevelConfigRepoDep,
) -> GetMemberLevelHandler:
    """Get member level query handler."""
    return GetMemberLevelHandler(member_points_repo=mp_repo, level_config_repo=lc_repo)


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


def create_award_handler() -> AwardPointsHandler:
    """Create AwardPointsHandler with a fresh session (for event handlers)."""
    from src.identity.interface.api.dependencies import get_database

    db = get_database()
    session = db._session_factory()  # noqa: SLF001
    mp_repo = SqlAlchemyMemberPointsRepository(session)
    lc_repo = SqlAlchemyLevelConfigRepository(session)
    return AwardPointsHandler(member_points_repo=mp_repo, level_config_repo=lc_repo)


def create_deduct_handler() -> DeductPointsHandler:
    """Create DeductPointsHandler with a fresh session (for event handlers)."""
    from src.identity.interface.api.dependencies import get_database

    db = get_database()
    session = db._session_factory()  # noqa: SLF001
    mp_repo = SqlAlchemyMemberPointsRepository(session)
    lc_repo = SqlAlchemyLevelConfigRepository(session)
    return DeductPointsHandler(member_points_repo=mp_repo, level_config_repo=lc_repo)
