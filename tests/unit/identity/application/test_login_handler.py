"""Unit tests for LoginHandler."""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.identity.application.commands.login import LoginCommand
from src.identity.application.handlers.login_handler import LoginHandler
from src.identity.domain.entities.user import User
from src.identity.domain.exceptions import (
    InvalidCredentialsError,
    UserDisabledError,
    UserNotVerifiedError,
)
from src.identity.domain.value_objects import AuthTokens, EmailAddress, HashedPassword, UserId


@pytest.fixture
def mock_user_repository() -> AsyncMock:
    """Create a mock user repository."""
    return AsyncMock()


@pytest.fixture
def mock_password_hasher() -> MagicMock:
    """Create a mock password hasher."""
    return MagicMock()


@pytest.fixture
def mock_token_generator() -> MagicMock:
    """Create a mock token generator."""
    mock = MagicMock()
    mock.generate_auth_tokens.return_value = AuthTokens(
        access_token="access_token",
        refresh_token="refresh_token",
        token_type="bearer",
        expires_at=datetime.now(UTC) + timedelta(minutes=30),
    )
    return mock


@pytest.fixture
def handler(
    mock_user_repository: AsyncMock,
    mock_password_hasher: MagicMock,
    mock_token_generator: MagicMock,
) -> LoginHandler:
    """Create a LoginHandler with mocked dependencies."""
    return LoginHandler(
        user_repository=mock_user_repository,
        password_hasher=mock_password_hasher,
        token_generator=mock_token_generator,
    )


@pytest.fixture
def verified_active_user() -> User:
    """Create a verified, active user for testing."""
    user = User(
        id=UserId(uuid4()),
        email=EmailAddress("user@example.com"),
        hashed_password=HashedPassword("$argon2id$v=19$m=65536,t=3,p=4$hash"),
        is_verified=True,
        is_active=True,
    )
    return user


@pytest.fixture
def unverified_user() -> User:
    """Create an unverified user for testing."""
    user = User(
        id=UserId(uuid4()),
        email=EmailAddress("unverified@example.com"),
        hashed_password=HashedPassword("$argon2id$v=19$m=65536,t=3,p=4$hash"),
        is_verified=False,
        is_active=True,
    )
    return user


@pytest.fixture
def disabled_user() -> User:
    """Create a disabled user for testing."""
    user = User(
        id=UserId(uuid4()),
        email=EmailAddress("disabled@example.com"),
        hashed_password=HashedPassword("$argon2id$v=19$m=65536,t=3,p=4$hash"),
        is_verified=True,
        is_active=False,
    )
    return user


class TestLoginHandlerSuccess:
    """Tests for successful login scenarios."""

    @pytest.mark.asyncio
    async def test_login_with_valid_credentials_returns_tokens(
        self,
        handler: LoginHandler,
        mock_user_repository: AsyncMock,
        mock_password_hasher: MagicMock,
        mock_token_generator: MagicMock,
        verified_active_user: User,
    ) -> None:
        """Valid credentials should return auth tokens."""
        mock_user_repository.get_by_email.return_value = verified_active_user
        mock_password_hasher.verify.return_value = True
        command = LoginCommand(email="user@example.com", password="correctpassword")

        result = await handler.handle(command)

        assert result.access_token == "access_token"
        assert result.refresh_token == "refresh_token"
        mock_token_generator.generate_auth_tokens.assert_called_once()

    @pytest.mark.asyncio
    async def test_login_with_remember_me_passes_flag_to_token_generator(
        self,
        handler: LoginHandler,
        mock_user_repository: AsyncMock,
        mock_password_hasher: MagicMock,
        mock_token_generator: MagicMock,
        verified_active_user: User,
    ) -> None:
        """remember_me flag should be passed to token generator."""
        mock_user_repository.get_by_email.return_value = verified_active_user
        mock_password_hasher.verify.return_value = True
        command = LoginCommand(
            email="user@example.com", password="correctpassword", remember_me=True
        )

        await handler.handle(command)

        mock_token_generator.generate_auth_tokens.assert_called_once_with(
            user_id=verified_active_user.id,
            remember_me=True,
        )

    @pytest.mark.asyncio
    async def test_login_saves_user_after_recording_login(
        self,
        handler: LoginHandler,
        mock_user_repository: AsyncMock,
        mock_password_hasher: MagicMock,
        verified_active_user: User,
    ) -> None:
        """User should be saved after recording login."""
        mock_user_repository.get_by_email.return_value = verified_active_user
        mock_password_hasher.verify.return_value = True
        command = LoginCommand(email="user@example.com", password="correctpassword")

        await handler.handle(command)

        mock_user_repository.save.assert_called_once_with(verified_active_user)


class TestLoginHandlerInvalidEmail:
    """Tests for invalid email format scenarios."""

    @pytest.mark.asyncio
    async def test_login_with_invalid_email_format_raises_invalid_credentials(
        self, handler: LoginHandler
    ) -> None:
        """Invalid email format should raise InvalidCredentialsError (not reveal format error)."""
        command = LoginCommand(email="not-an-email", password="anypassword")

        with pytest.raises(InvalidCredentialsError):
            await handler.handle(command)

    @pytest.mark.asyncio
    async def test_login_with_empty_email_raises_invalid_credentials(
        self, handler: LoginHandler
    ) -> None:
        """Empty email should raise InvalidCredentialsError."""
        command = LoginCommand(email="", password="anypassword")

        with pytest.raises(InvalidCredentialsError):
            await handler.handle(command)


class TestLoginHandlerUserNotFound:
    """Tests for user not found scenarios."""

    @pytest.mark.asyncio
    async def test_login_with_nonexistent_email_raises_invalid_credentials(
        self,
        handler: LoginHandler,
        mock_user_repository: AsyncMock,
    ) -> None:
        """Non-existent email should raise InvalidCredentialsError (same as wrong password)."""
        mock_user_repository.get_by_email.return_value = None
        command = LoginCommand(email="nonexistent@example.com", password="anypassword")

        with pytest.raises(InvalidCredentialsError):
            await handler.handle(command)


class TestLoginHandlerWrongPassword:
    """Tests for wrong password scenarios."""

    @pytest.mark.asyncio
    async def test_login_with_wrong_password_raises_invalid_credentials(
        self,
        handler: LoginHandler,
        mock_user_repository: AsyncMock,
        mock_password_hasher: MagicMock,
        verified_active_user: User,
    ) -> None:
        """Wrong password should raise InvalidCredentialsError."""
        mock_user_repository.get_by_email.return_value = verified_active_user
        mock_password_hasher.verify.return_value = False
        command = LoginCommand(email="user@example.com", password="wrongpassword")

        with pytest.raises(InvalidCredentialsError):
            await handler.handle(command)


class TestLoginHandlerUnverifiedUser:
    """Tests for unverified user scenarios."""

    @pytest.mark.asyncio
    async def test_login_with_unverified_user_raises_not_verified_error(
        self,
        handler: LoginHandler,
        mock_user_repository: AsyncMock,
        mock_password_hasher: MagicMock,
        unverified_user: User,
    ) -> None:
        """Unverified user should raise UserNotVerifiedError (specific error, not generic)."""
        mock_user_repository.get_by_email.return_value = unverified_user
        mock_password_hasher.verify.return_value = True
        command = LoginCommand(email="unverified@example.com", password="correctpassword")

        with pytest.raises(UserNotVerifiedError):
            await handler.handle(command)


class TestLoginHandlerDisabledUser:
    """Tests for disabled user scenarios."""

    @pytest.mark.asyncio
    async def test_login_with_disabled_user_raises_disabled_error(
        self,
        handler: LoginHandler,
        mock_user_repository: AsyncMock,
        mock_password_hasher: MagicMock,
        disabled_user: User,
    ) -> None:
        """Disabled user should raise UserDisabledError."""
        mock_user_repository.get_by_email.return_value = disabled_user
        mock_password_hasher.verify.return_value = True
        command = LoginCommand(email="disabled@example.com", password="correctpassword")

        with pytest.raises(UserDisabledError):
            await handler.handle(command)


class TestLoginHandlerSecurityBehavior:
    """Tests for security-related behavior."""

    @pytest.mark.asyncio
    async def test_same_error_for_nonexistent_and_wrong_password(
        self,
        handler: LoginHandler,
        mock_user_repository: AsyncMock,
        mock_password_hasher: MagicMock,
        verified_active_user: User,
    ) -> None:
        """Both non-existent email and wrong password should raise same error type.

        This prevents email enumeration attacks.
        """
        # Test wrong password
        mock_user_repository.get_by_email.return_value = verified_active_user
        mock_password_hasher.verify.return_value = False
        wrong_password_error = None
        try:
            await handler.handle(LoginCommand(email="user@example.com", password="wrong"))
        except InvalidCredentialsError as e:
            wrong_password_error = e

        # Test non-existent email
        mock_user_repository.get_by_email.return_value = None
        nonexistent_error = None
        try:
            await handler.handle(LoginCommand(email="nonexistent@example.com", password="any"))
        except InvalidCredentialsError as e:
            nonexistent_error = e

        # Both should be InvalidCredentialsError
        assert wrong_password_error is not None
        assert nonexistent_error is not None
        assert type(wrong_password_error) is type(nonexistent_error)
