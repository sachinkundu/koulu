"""Unit tests for GetProfileHandler."""

from uuid import uuid4

import pytest

from src.identity.application.queries import GetProfileHandler, GetProfileQuery
from src.identity.domain.entities import Profile, User
from src.identity.domain.exceptions import ProfileNotFoundError
from src.identity.domain.repositories import IUserRepository
from src.identity.domain.value_objects import (
    DisplayName,
    EmailAddress,
    HashedPassword,
    UserId,
)


class MockUserRepository(IUserRepository):
    """Mock user repository for testing."""

    def __init__(self, users: dict[UserId, User] | None = None) -> None:
        """Initialize with optional users dict."""
        self._users = users or {}

    async def save(self, user: User) -> None:
        """Save user."""
        self._users[user.id] = user

    async def get_by_id(self, user_id: UserId) -> User | None:
        """Get user by ID."""
        return self._users.get(user_id)

    async def get_by_email(self, email: EmailAddress) -> User | None:
        """Get user by email."""
        for user in self._users.values():
            if user.email == email:
                return user
        return None

    async def exists_by_email(self, email: EmailAddress) -> bool:
        """Check if user exists."""
        return any(user.email == email for user in self._users.values())

    async def delete(self, user_id: UserId) -> None:
        """Delete user."""
        self._users.pop(user_id, None)


@pytest.mark.asyncio
async def test_get_profile_success() -> None:
    """Test getting profile successfully."""
    user_id = UserId(value=uuid4())
    user = User(
        id=user_id,
        email=EmailAddress("test@example.com"),
        hashed_password=HashedPassword("hashed"),
        is_verified=True,
        profile=Profile(
            user_id=user_id,
            display_name=DisplayName("Test User"),
            is_complete=True,
        ),
    )

    repository = MockUserRepository({user_id: user})
    handler = GetProfileHandler(user_repository=repository)

    query = GetProfileQuery(user_id=user_id.value)
    result = await handler.handle(query)

    assert result == user
    assert result.profile is not None
    assert result.profile.display_name == DisplayName("Test User")


@pytest.mark.asyncio
async def test_get_profile_user_not_found() -> None:
    """Test getting profile when user doesn't exist."""
    repository = MockUserRepository()
    handler = GetProfileHandler(user_repository=repository)

    query = GetProfileQuery(user_id=uuid4())

    with pytest.raises(ProfileNotFoundError):
        await handler.handle(query)


@pytest.mark.asyncio
async def test_get_profile_profile_not_found() -> None:
    """Test getting profile when user exists but profile doesn't."""
    user_id = UserId(value=uuid4())
    user = User(
        id=user_id,
        email=EmailAddress("test@example.com"),
        hashed_password=HashedPassword("hashed"),
        is_verified=True,
        profile=None,  # No profile
    )

    repository = MockUserRepository({user_id: user})
    handler = GetProfileHandler(user_repository=repository)

    query = GetProfileQuery(user_id=user_id.value)

    with pytest.raises(ProfileNotFoundError):
        await handler.handle(query)
