"""Pytest fixtures for Identity BDD tests."""

import asyncio
from collections.abc import AsyncGenerator, Callable, Coroutine, Generator
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.config import settings
from src.identity.domain.value_objects import UserId
from src.identity.infrastructure.persistence.models import (
    ProfileModel,
    ResetTokenModel,
    UserModel,
    VerificationTokenModel,
)
from src.identity.infrastructure.services import Argon2PasswordHasher
from src.identity.interface.api.dependencies import get_session
from src.main import app
from src.shared.infrastructure import Base

# Test database URL (use separate test database)
# Use rsplit to replace only the database name at the end, not the username
_base_url, _db_name = settings.database_url.rsplit("/", 1)
TEST_DATABASE_URL = f"{_base_url}/koulu_test"


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_engine() -> AsyncGenerator[AsyncEngine, None]:
    """Create test database engine."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(db_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    session_factory = async_sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test HTTP client with overridden database session."""

    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_session] = override_get_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
def password_hasher() -> Argon2PasswordHasher:
    """Get password hasher."""
    return Argon2PasswordHasher()


@pytest.fixture
def context() -> dict[str, Any]:
    """Shared test context for storing state between steps."""
    return {}


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
