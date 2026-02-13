"""Pytest fixtures for Member Directory BDD tests."""

from collections.abc import Callable, Coroutine
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID, uuid4

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.community.infrastructure.persistence.models import (
    CommunityMemberModel,
    CommunityModel,
)
from src.identity.infrastructure.persistence.models import ProfileModel, UserModel
from src.identity.infrastructure.services import Argon2PasswordHasher

# Type aliases
CreateCommunityFactory = Callable[..., Coroutine[Any, Any, CommunityModel]]
CreateMemberWithProfileFactory = Callable[..., Coroutine[Any, Any, tuple[UserModel, CommunityMemberModel]]]


@pytest_asyncio.fixture
async def create_community(db_session: AsyncSession) -> CreateCommunityFactory:
    """Factory fixture to create test communities."""

    async def _create_community(
        name: str = "Test Community",
        slug: str = "test-community",
    ) -> CommunityModel:
        community_id = uuid4()
        community = CommunityModel(
            id=community_id,
            name=name,
            slug=slug,
        )
        db_session.add(community)
        await db_session.commit()
        await db_session.refresh(community)
        return community

    return _create_community


@pytest_asyncio.fixture
async def create_member_with_profile(
    db_session: AsyncSession,
    password_hasher: Argon2PasswordHasher,
) -> CreateMemberWithProfileFactory:
    """Factory fixture to create a user + profile + community membership."""

    async def _create(
        community_id: UUID,
        display_name: str,
        role: str = "MEMBER",
        bio: str | None = None,
        avatar_url: str | None = None,
        joined_days_ago: int = 0,
        password: str = "testpassword123",
    ) -> tuple[UserModel, CommunityMemberModel]:
        user_id = uuid4()
        hashed = password_hasher.hash(password)

        # Create user
        email = f"{display_name.lower().replace(' ', '.')}@test.com"
        user = UserModel(
            id=user_id,
            email=email,
            hashed_password=hashed.value,
            is_verified=True,
            is_active=True,
        )
        db_session.add(user)

        # Create profile
        profile = ProfileModel(
            user_id=user_id,
            display_name=display_name,
            avatar_url=avatar_url,
            bio=bio,
            is_complete=True,
        )
        db_session.add(profile)

        # Create membership with specific join date
        joined_at = datetime.now(UTC) - timedelta(days=joined_days_ago)
        member = CommunityMemberModel(
            community_id=community_id,
            user_id=user_id,
            role=role,
            joined_at=joined_at,
            is_active=True,
        )
        db_session.add(member)

        await db_session.commit()
        await db_session.refresh(user)
        await db_session.refresh(member)

        return user, member

    return _create
