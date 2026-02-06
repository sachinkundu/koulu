"""Unit tests for UpdateProfileHandler."""
# mypy: disable-error-code="no-untyped-def"

from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from src.identity.application.commands.update_profile import UpdateProfileCommand
from src.identity.application.handlers.update_profile_handler import UpdateProfileHandler
from src.identity.domain.entities import Profile, User
from src.identity.domain.exceptions import ProfileNotFoundError, UserNotFoundError
from src.identity.domain.value_objects import (
    Bio,
    DisplayName,
    EmailAddress,
    HashedPassword,
    Location,
    UserId,
)


@pytest.fixture
def mock_user_repository() -> AsyncMock:
    """Create a mock user repository."""
    return AsyncMock()


@pytest.fixture
def mock_avatar_generator() -> Mock:
    """Create a mock avatar generator."""
    mock = Mock()
    mock.generate_from_initials.return_value = "https://ui-avatars.com/api/?name=JD"
    return mock


@pytest.fixture
def handler(mock_user_repository: AsyncMock, mock_avatar_generator: Mock) -> UpdateProfileHandler:
    """Create UpdateProfileHandler with mocked dependencies."""
    return UpdateProfileHandler(
        user_repository=mock_user_repository,
        avatar_generator=mock_avatar_generator,
    )


@pytest.fixture
def user_with_profile() -> User:
    """Create a user with a completed profile."""
    user_id = UserId(uuid4())
    user = User(
        id=user_id,
        email=EmailAddress("test@example.com"),
        hashed_password=HashedPassword("hashed"),
        is_verified=True,
        is_active=True,
    )
    user.profile = Profile(
        user_id=user_id,
        display_name=DisplayName("Original Name"),
        avatar_url="https://example.com/avatar.jpg",
        bio=Bio("Original bio"),
        location=Location(city="Austin", country="USA"),
        is_complete=True,
    )
    return user


@pytest.mark.asyncio
async def test_update_display_name_success(
    handler, mock_user_repository, user_with_profile
) -> None:
    """Test successful display name update."""
    # Arrange
    user_id = user_with_profile.id.value
    command = UpdateProfileCommand(
        user_id=user_id,
        display_name="New Name",
    )
    mock_user_repository.get_by_id.return_value = user_with_profile

    # Act
    await handler.handle(command)

    # Assert
    mock_user_repository.save.assert_called_once()
    assert user_with_profile.profile.display_name.value == "New Name"


@pytest.mark.asyncio
async def test_update_bio_success(handler, mock_user_repository, user_with_profile) -> None:
    """Test successful bio update."""
    # Arrange
    user_id = user_with_profile.id.value
    command = UpdateProfileCommand(
        user_id=user_id,
        bio="Updated bio content",
    )
    mock_user_repository.get_by_id.return_value = user_with_profile

    # Act
    await handler.handle(command)

    # Assert
    mock_user_repository.save.assert_called_once()
    assert user_with_profile.profile.bio.value == "Updated bio content"


@pytest.mark.asyncio
async def test_update_location_success(handler, mock_user_repository, user_with_profile) -> None:
    """Test successful location update."""
    # Arrange
    user_id = user_with_profile.id.value
    command = UpdateProfileCommand(
        user_id=user_id,
        city="Seattle",
        country="USA",
    )
    mock_user_repository.get_by_id.return_value = user_with_profile

    # Act
    await handler.handle(command)

    # Assert
    mock_user_repository.save.assert_called_once()
    assert user_with_profile.profile.location.city == "Seattle"
    assert user_with_profile.profile.location.country == "USA"


@pytest.mark.asyncio
async def test_update_social_links_success(
    handler, mock_user_repository, user_with_profile
) -> None:
    """Test successful social links update."""
    # Arrange
    user_id = user_with_profile.id.value
    command = UpdateProfileCommand(
        user_id=user_id,
        twitter_url="https://twitter.com/testuser",
        linkedin_url="https://linkedin.com/in/testuser",
    )
    mock_user_repository.get_by_id.return_value = user_with_profile

    # Act
    await handler.handle(command)

    # Assert
    mock_user_repository.save.assert_called_once()
    assert user_with_profile.profile.social_links.twitter_url == "https://twitter.com/testuser"
    assert user_with_profile.profile.social_links.linkedin_url == "https://linkedin.com/in/testuser"


@pytest.mark.asyncio
async def test_clear_avatar_regenerates_from_initials(
    handler, mock_user_repository, mock_avatar_generator, user_with_profile
) -> None:
    """Test clearing avatar URL regenerates from initials."""
    # Arrange
    user_id = user_with_profile.id.value
    command = UpdateProfileCommand(
        user_id=user_id,
        avatar_url="",  # Empty string triggers regeneration
    )
    mock_user_repository.get_by_id.return_value = user_with_profile

    # Act
    await handler.handle(command)

    # Assert
    mock_avatar_generator.generate_from_initials.assert_called_once()
    mock_user_repository.save.assert_called_once()


@pytest.mark.asyncio
async def test_update_multiple_fields(handler, mock_user_repository, user_with_profile) -> None:
    """Test updating multiple fields at once."""
    # Arrange
    user_id = user_with_profile.id.value
    command = UpdateProfileCommand(
        user_id=user_id,
        display_name="New Name",
        bio="New bio",
        city="London",
        country="UK",
    )
    mock_user_repository.get_by_id.return_value = user_with_profile

    # Act
    await handler.handle(command)

    # Assert
    mock_user_repository.save.assert_called_once()
    assert user_with_profile.profile.display_name.value == "New Name"
    assert user_with_profile.profile.bio.value == "New bio"
    assert user_with_profile.profile.location.city == "London"


@pytest.mark.asyncio
async def test_user_not_found_raises_error(handler, mock_user_repository) -> None:
    """Test that UserNotFoundError is raised when user doesn't exist."""
    # Arrange
    user_id = uuid4()
    command = UpdateProfileCommand(
        user_id=user_id,
        display_name="New Name",
    )
    mock_user_repository.get_by_id.return_value = None

    # Act & Assert
    with pytest.raises(UserNotFoundError):
        await handler.handle(command)


@pytest.mark.asyncio
async def test_profile_not_found_raises_error(handler, mock_user_repository) -> None:
    """Test that ProfileNotFoundError is raised when profile doesn't exist."""
    # Arrange
    user_id = UserId(uuid4())
    user = User(
        id=user_id,
        email=EmailAddress("test@example.com"),
        hashed_password=HashedPassword("hashed"),
        is_verified=True,
        is_active=True,
    )
    # User has no profile
    user.profile = None

    command = UpdateProfileCommand(
        user_id=user_id.value,
        display_name="New Name",
    )
    mock_user_repository.get_by_id.return_value = user

    # Act & Assert
    with pytest.raises(ProfileNotFoundError):
        await handler.handle(command)


@pytest.mark.asyncio
async def test_no_changes_does_not_save(handler, mock_user_repository, user_with_profile) -> None:
    """Test that no changes result in no save operation."""
    # Arrange
    user_id = user_with_profile.id.value
    command = UpdateProfileCommand(
        user_id=user_id,
        # No fields provided - no changes
    )
    mock_user_repository.get_by_id.return_value = user_with_profile

    # Act
    await handler.handle(command)

    # Assert
    mock_user_repository.save.assert_not_called()


@pytest.mark.asyncio
async def test_events_published_on_update(handler, mock_user_repository, user_with_profile) -> None:
    """Test that domain events are published when profile is updated."""
    # Arrange
    user_id = user_with_profile.id.value
    command = UpdateProfileCommand(
        user_id=user_id,
        display_name="New Name",
    )
    mock_user_repository.get_by_id.return_value = user_with_profile

    # Act
    await handler.handle(command)

    # Assert
    # After handle, events should be cleared (published)
    assert len(user_with_profile.clear_events()) == 0
