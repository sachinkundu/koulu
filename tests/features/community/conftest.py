"""Pytest fixtures for Community BDD tests."""

from collections.abc import Callable, Coroutine, Generator
from typing import Any
from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.community.infrastructure.persistence.models import (
    CategoryModel,
    CommunityMemberModel,
    CommunityModel,
)
from src.community.infrastructure.services import InMemoryRateLimiter
from src.identity.infrastructure.persistence.models import ProfileModel, UserModel
from src.identity.infrastructure.services import Argon2PasswordHasher

# Type aliases for factory functions
CreateCommunityFactory = Callable[..., Coroutine[Any, Any, CommunityModel]]
CreateCategoryFactory = Callable[..., Coroutine[Any, Any, CategoryModel]]
CreateMemberFactory = Callable[..., Coroutine[Any, Any, CommunityMemberModel]]


@pytest.fixture(autouse=True)
def _reset_rate_limiter() -> Generator[None, None, None]:
    """Reset rate limiter state between tests."""
    InMemoryRateLimiter.reset()
    yield
    InMemoryRateLimiter.reset()


@pytest_asyncio.fixture
async def create_community(db_session: AsyncSession) -> CreateCommunityFactory:
    """Factory fixture to create test communities."""

    async def _create_community(
        name: str = "Koulu Community",
        slug: str = "koulu-community",
        description: str | None = None,
    ) -> CommunityModel:
        community_id = uuid4()
        community = CommunityModel(
            id=community_id,
            name=name,
            slug=slug,
            description=description,
        )
        db_session.add(community)
        await db_session.commit()
        await db_session.refresh(community)
        return community

    return _create_community


@pytest_asyncio.fixture
async def create_category(db_session: AsyncSession) -> CreateCategoryFactory:
    """Factory fixture to create test categories."""

    async def _create_category(
        community_id: UUID,
        name: str,
        slug: str,
        emoji: str | None = None,
    ) -> CategoryModel:
        category_id = uuid4()
        category = CategoryModel(
            id=category_id,
            community_id=community_id,
            name=name,
            slug=slug,
            emoji=emoji,
        )
        db_session.add(category)
        await db_session.commit()
        await db_session.refresh(category)
        return category

    return _create_category


@pytest_asyncio.fixture
async def create_member(db_session: AsyncSession) -> CreateMemberFactory:
    """Factory fixture to create community members."""

    async def _create_member(
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
        await db_session.commit()
        await db_session.refresh(member)
        return member

    return _create_member


@pytest_asyncio.fixture
async def create_community_user(
    db_session: AsyncSession,
    password_hasher: Argon2PasswordHasher,
    create_community: CreateCommunityFactory,
    create_member: CreateMemberFactory,
) -> Callable[..., Coroutine[Any, Any, tuple[UserModel, CommunityModel, CommunityMemberModel]]]:
    """Factory fixture to create a user with community membership."""

    async def _create_community_user(
        email: str,
        role: str = "MEMBER",
        password: str = "testpassword123",
        is_verified: bool = True,
        display_name: str = "Test User",
        community_name: str = "Koulu Community",
        community_id: UUID | None = None,
    ) -> tuple[UserModel, CommunityModel, CommunityMemberModel]:
        """
        Create a user and add them to a community with the specified role.

        Returns:
            Tuple of (user, community, member)
        """
        # Create user
        hashed = password_hasher.hash(password)
        user_id = uuid4()
        user = UserModel(
            id=user_id,
            email=email.lower(),
            hashed_password=hashed.value,
            is_verified=is_verified,
            is_active=True,
        )
        db_session.add(user)

        # Create profile
        profile = ProfileModel(
            user_id=user_id,
            display_name=display_name,
            is_complete=True,
        )
        db_session.add(profile)
        await db_session.commit()
        await db_session.refresh(user)

        # Get or create community
        if community_id is None:
            community = await create_community(name=community_name)
        else:
            from sqlalchemy import select

            result = await db_session.execute(
                select(CommunityModel).where(CommunityModel.id == community_id)
            )
            community = result.scalar_one()

        # Create community membership
        member = await create_member(
            community_id=community.id,
            user_id=user_id,
            role=role,
        )

        return user, community, member

    return _create_community_user
