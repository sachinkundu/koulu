"""Pytest fixtures for Gamification BDD tests."""

from collections.abc import Callable, Coroutine, Generator
from typing import Any
from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.community.infrastructure.persistence.models import (
    CategoryModel,
    CommentModel,
    CommunityMemberModel,
    CommunityModel,
    PostModel,
)
from src.community.infrastructure.services import InMemoryRateLimiter
from src.gamification.application.commands.award_points import (
    AwardPointsHandler,
)
from src.gamification.application.commands.deduct_points import (
    DeductPointsHandler,
)
from src.gamification.application.commands.update_level_config import (
    UpdateLevelConfigHandler,
)
from src.gamification.application.queries.get_level_definitions import (
    GetLevelDefinitionsHandler,
)
from src.gamification.application.queries.get_member_level import (
    GetMemberLevelHandler,
)
from src.gamification.infrastructure.persistence.level_config_repository import (
    SqlAlchemyLevelConfigRepository,
)
from src.gamification.infrastructure.persistence.member_points_repository import (
    SqlAlchemyMemberPointsRepository,
)
from src.identity.infrastructure.persistence.models import ProfileModel, UserModel
from src.identity.infrastructure.services import Argon2PasswordHasher


@pytest.fixture(autouse=True)
def _reset_rate_limiter() -> Generator[None, None, None]:
    """Reset rate limiter state between tests."""
    InMemoryRateLimiter.reset()
    yield
    InMemoryRateLimiter.reset()


@pytest_asyncio.fixture
async def mp_repo(db_session: AsyncSession) -> SqlAlchemyMemberPointsRepository:
    """Member points repository backed by test DB session."""
    return SqlAlchemyMemberPointsRepository(db_session)


@pytest_asyncio.fixture
async def lc_repo(db_session: AsyncSession) -> SqlAlchemyLevelConfigRepository:
    """Level config repository backed by test DB session."""
    return SqlAlchemyLevelConfigRepository(db_session)


@pytest_asyncio.fixture
async def award_handler(
    mp_repo: SqlAlchemyMemberPointsRepository,
    lc_repo: SqlAlchemyLevelConfigRepository,
) -> AwardPointsHandler:
    """Award points handler using test DB session."""
    return AwardPointsHandler(member_points_repo=mp_repo, level_config_repo=lc_repo)


@pytest_asyncio.fixture
async def deduct_handler(
    mp_repo: SqlAlchemyMemberPointsRepository,
    lc_repo: SqlAlchemyLevelConfigRepository,
) -> DeductPointsHandler:
    """Deduct points handler using test DB session."""
    return DeductPointsHandler(member_points_repo=mp_repo, level_config_repo=lc_repo)


@pytest_asyncio.fixture
async def level_query_handler(
    mp_repo: SqlAlchemyMemberPointsRepository,
    lc_repo: SqlAlchemyLevelConfigRepository,
) -> GetMemberLevelHandler:
    """Get member level query handler using test DB session."""
    return GetMemberLevelHandler(member_points_repo=mp_repo, level_config_repo=lc_repo)


@pytest_asyncio.fixture
async def level_definitions_handler(
    mp_repo: SqlAlchemyMemberPointsRepository,
    lc_repo: SqlAlchemyLevelConfigRepository,
) -> GetLevelDefinitionsHandler:
    """Get level definitions query handler using test DB session."""
    return GetLevelDefinitionsHandler(member_points_repo=mp_repo, level_config_repo=lc_repo)


@pytest_asyncio.fixture
async def update_level_config_handler(
    mp_repo: SqlAlchemyMemberPointsRepository,
    lc_repo: SqlAlchemyLevelConfigRepository,
) -> UpdateLevelConfigHandler:
    """Update level config command handler using test DB session."""
    return UpdateLevelConfigHandler(member_points_repo=mp_repo, level_config_repo=lc_repo)


@pytest_asyncio.fixture
async def create_community(
    db_session: AsyncSession,
) -> Callable[..., Coroutine[Any, Any, CommunityModel]]:
    """Factory fixture to create test communities."""

    async def _create(
        name: str = "Koulu Community",
        slug: str = "koulu-community",
    ) -> CommunityModel:
        community = CommunityModel(
            id=uuid4(),
            name=name,
            slug=slug,
        )
        db_session.add(community)
        await db_session.flush()
        return community

    return _create


@pytest_asyncio.fixture
async def create_user(
    db_session: AsyncSession,
    password_hasher: Argon2PasswordHasher,
) -> Callable[..., Coroutine[Any, Any, UserModel]]:
    """Factory fixture to create test users."""

    async def _create(
        email: str,
        display_name: str = "Test User",
        password: str = "testpassword123",
    ) -> UserModel:
        user_id = uuid4()
        hashed = password_hasher.hash(password)
        user = UserModel(
            id=user_id,
            email=email.lower(),
            hashed_password=hashed.value,
            is_verified=True,
            is_active=True,
        )
        db_session.add(user)
        profile = ProfileModel(
            user_id=user_id,
            display_name=display_name,
            is_complete=True,
        )
        db_session.add(profile)
        await db_session.flush()
        return user

    return _create


@pytest_asyncio.fixture
async def create_member(
    db_session: AsyncSession,
) -> Callable[..., Coroutine[Any, Any, CommunityMemberModel]]:
    """Factory fixture to create community members."""

    async def _create(
        community_id: UUID,
        user_id: UUID,
        role: str = "MEMBER",
    ) -> CommunityMemberModel:
        member = CommunityMemberModel(
            id=uuid4(),
            community_id=community_id,
            user_id=user_id,
            role=role,
        )
        db_session.add(member)
        await db_session.flush()
        return member

    return _create


@pytest_asyncio.fixture
async def create_category(
    db_session: AsyncSession,
) -> Callable[..., Coroutine[Any, Any, CategoryModel]]:
    """Factory fixture to create test categories."""

    async def _create(
        community_id: UUID,
        name: str = "General",
        slug: str = "general",
    ) -> CategoryModel:
        category = CategoryModel(
            id=uuid4(),
            community_id=community_id,
            name=name,
            slug=slug,
        )
        db_session.add(category)
        await db_session.flush()
        return category

    return _create


@pytest_asyncio.fixture
async def create_post(
    db_session: AsyncSession,
) -> Callable[..., Coroutine[Any, Any, PostModel]]:
    """Factory fixture to create test posts."""

    async def _create(
        community_id: UUID,
        author_id: UUID,
        category_id: UUID,
        title: str = "Test Post",
        content: str = "Test content",
    ) -> PostModel:
        post = PostModel(
            id=uuid4(),
            community_id=community_id,
            author_id=author_id,
            category_id=category_id,
            title=title,
            content=content,
        )
        db_session.add(post)
        await db_session.flush()
        return post

    return _create


@pytest_asyncio.fixture
async def create_comment(
    db_session: AsyncSession,
) -> Callable[..., Coroutine[Any, Any, CommentModel]]:
    """Factory fixture to create test comments."""

    async def _create(
        post_id: UUID,
        author_id: UUID,
        content: str = "Test comment",
    ) -> CommentModel:
        comment = CommentModel(
            id=uuid4(),
            post_id=post_id,
            author_id=author_id,
            content=content,
        )
        db_session.add(comment)
        await db_session.flush()
        return comment

    return _create
