"""Pytest fixtures for Identity BDD tests."""

from collections.abc import Callable, Coroutine
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID, uuid4

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.identity.domain.value_objects import UserId
from src.identity.infrastructure.persistence.models import (
    ProfileModel,
    ResetTokenModel,
    UserModel,
    VerificationTokenModel,
)
from src.identity.infrastructure.services import Argon2PasswordHasher

# Shared fixtures (db_engine, db_session, client, password_hasher, context)
# are now defined in tests/conftest.py


# Type alias for the create_user factory
CreateUserFactory = Callable[..., Coroutine[Any, Any, UserModel]]


@pytest_asyncio.fixture
async def create_user(
    db_session: AsyncSession, password_hasher: Argon2PasswordHasher
) -> CreateUserFactory:
    """Factory fixture to create test users."""

    async def _create_user(
        email: str,
        password: str = "testpassword123",
        is_verified: bool = False,
        is_active: bool = True,
        display_name: str | None = None,
        bio: str | None = None,
        avatar_url: str | None = None,
        city: str | None = None,
        country: str | None = None,
        twitter_url: str | None = None,
        linkedin_url: str | None = None,
        instagram_url: str | None = None,
        website_url: str | None = None,
        registered_on: datetime | None = None,
    ) -> UserModel:
        hashed = password_hasher.hash(password)
        user_id = uuid4()
        created_at = registered_on or datetime.now(UTC)

        user = UserModel(
            id=user_id,
            email=email.lower(),
            hashed_password=hashed.value,
            is_verified=is_verified,
            is_active=is_active,
            created_at=created_at,
        )
        db_session.add(user)

        # Determine if profile is complete
        is_complete = display_name is not None

        profile = ProfileModel(
            user_id=user_id,
            display_name=display_name,
            bio=bio,
            avatar_url=avatar_url,
            location_city=city,
            location_country=country,
            twitter_url=twitter_url,
            linkedin_url=linkedin_url,
            instagram_url=instagram_url,
            website_url=website_url,
            is_complete=is_complete,
            created_at=created_at,
        )
        db_session.add(profile)

        await db_session.commit()
        await db_session.refresh(user)
        return user

    return _create_user


# Type alias for the create_verification_token factory
CreateVerificationTokenFactory = Callable[..., Coroutine[Any, Any, VerificationTokenModel]]


@pytest_asyncio.fixture
async def create_verification_token(
    db_session: AsyncSession,
) -> CreateVerificationTokenFactory:
    """Factory fixture to create verification tokens."""

    async def _create_token(
        user_id: UserId | UUID,
        token: str | None = None,
        hours_ago: int = 0,
    ) -> VerificationTokenModel:
        if token is None:
            token = f"verify_{uuid4().hex}"

        expires_at = datetime.now(UTC) + timedelta(hours=24 - hours_ago)

        verification = VerificationTokenModel(
            id=uuid4(),
            user_id=user_id.value if isinstance(user_id, UserId) else user_id,
            token=token,
            expires_at=expires_at,
        )
        db_session.add(verification)
        await db_session.commit()
        await db_session.refresh(verification)
        return verification

    return _create_token


# Type alias for the create_reset_token factory
CreateResetTokenFactory = Callable[..., Coroutine[Any, Any, ResetTokenModel]]


@pytest_asyncio.fixture
async def create_reset_token(db_session: AsyncSession) -> CreateResetTokenFactory:
    """Factory fixture to create password reset tokens."""

    async def _create_token(
        user_id: UserId | UUID,
        token: str | None = None,
        hours_ago: int = 0,
        used: bool = False,
    ) -> ResetTokenModel:
        if token is None:
            token = f"reset_{uuid4().hex}"

        expires_at = datetime.now(UTC) + timedelta(hours=1 - hours_ago)

        reset = ResetTokenModel(
            id=uuid4(),
            user_id=user_id.value if isinstance(user_id, UserId) else user_id,
            token=token,
            expires_at=expires_at,
            used_at=datetime.now(UTC) if used else None,
        )
        db_session.add(reset)
        await db_session.commit()
        await db_session.refresh(reset)
        return reset

    return _create_token
