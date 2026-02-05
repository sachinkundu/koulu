"""Unit tests for VerifyEmailHandler."""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.identity.application.commands.verify_email import VerifyEmailCommand
from src.identity.application.handlers.verify_email_handler import VerifyEmailHandler
from src.identity.domain.entities.user import User
from src.identity.domain.exceptions import InvalidTokenError, UserAlreadyVerifiedError
from src.identity.domain.value_objects import AuthTokens, EmailAddress, HashedPassword, UserId


@pytest.fixture
def mock_user_repository() -> AsyncMock:
    """Create a mock user repository."""
    return AsyncMock()


@pytest.fixture
def mock_verification_token_repository() -> AsyncMock:
    """Create a mock verification token repository."""
    return AsyncMock()


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
    mock_verification_token_repository: AsyncMock,
    mock_token_generator: MagicMock,
) -> VerifyEmailHandler:
    """Create a VerifyEmailHandler with mocked dependencies."""
    return VerifyEmailHandler(
        user_repository=mock_user_repository,
        verification_token_repository=mock_verification_token_repository,
        token_generator=mock_token_generator,
    )


@pytest.fixture
def unverified_user() -> User:
    """Create an unverified user for testing."""
    return User(
        id=UserId(uuid4()),
        email=EmailAddress("user@example.com"),
        hashed_password=HashedPassword("$argon2id$v=19$m=65536,t=3,p=4$hash"),
        is_verified=False,
        is_active=True,
    )


@pytest.fixture
def verified_user() -> User:
    """Create a verified user for testing."""
    return User(
        id=UserId(uuid4()),
        email=EmailAddress("verified@example.com"),
        hashed_password=HashedPassword("$argon2id$v=19$m=65536,t=3,p=4$hash"),
        is_verified=True,
        is_active=True,
    )


class TestVerifyEmailHandlerSuccess:
    """Tests for successful verification scenarios."""

    @pytest.mark.asyncio
    async def test_valid_token_returns_auth_tokens(
        self,
        handler: VerifyEmailHandler,
        mock_user_repository: AsyncMock,
        mock_verification_token_repository: AsyncMock,
        unverified_user: User,
    ) -> None:
        """Valid verification token should return auth tokens."""
        mock_verification_token_repository.get_user_id_by_token.return_value = unverified_user.id
        mock_user_repository.get_by_id.return_value = unverified_user
        command = VerifyEmailCommand(token="valid_token_123")

        result = await handler.handle(command)

        assert result.access_token is not None
        assert result.refresh_token is not None

    @pytest.mark.asyncio
    async def test_verification_marks_user_as_verified(
        self,
        handler: VerifyEmailHandler,
        mock_user_repository: AsyncMock,
        mock_verification_token_repository: AsyncMock,
        unverified_user: User,
    ) -> None:
        """Verification should mark the user as verified."""
        mock_verification_token_repository.get_user_id_by_token.return_value = unverified_user.id
        mock_user_repository.get_by_id.return_value = unverified_user
        command = VerifyEmailCommand(token="valid_token_123")

        await handler.handle(command)

        assert unverified_user.is_verified is True
        mock_user_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_verification_deletes_token(
        self,
        handler: VerifyEmailHandler,
        mock_user_repository: AsyncMock,
        mock_verification_token_repository: AsyncMock,
        unverified_user: User,
    ) -> None:
        """Verification should delete the used token."""
        mock_verification_token_repository.get_user_id_by_token.return_value = unverified_user.id
        mock_user_repository.get_by_id.return_value = unverified_user
        command = VerifyEmailCommand(token="valid_token_123")

        await handler.handle(command)

        mock_verification_token_repository.delete_by_user_id.assert_called_once_with(
            unverified_user.id
        )


class TestVerifyEmailHandlerInvalidToken:
    """Tests for invalid token scenarios."""

    @pytest.mark.asyncio
    async def test_invalid_token_raises_error(
        self,
        handler: VerifyEmailHandler,
        mock_verification_token_repository: AsyncMock,
    ) -> None:
        """Invalid/expired token should raise InvalidTokenError."""
        mock_verification_token_repository.get_user_id_by_token.return_value = None
        command = VerifyEmailCommand(token="invalid_token")

        with pytest.raises(InvalidTokenError):
            await handler.handle(command)

    @pytest.mark.asyncio
    async def test_token_for_deleted_user_raises_error(
        self,
        handler: VerifyEmailHandler,
        mock_user_repository: AsyncMock,
        mock_verification_token_repository: AsyncMock,
    ) -> None:
        """Token for a deleted user should raise InvalidTokenError."""
        user_id = UserId(uuid4())
        mock_verification_token_repository.get_user_id_by_token.return_value = user_id
        mock_user_repository.get_by_id.return_value = None  # User not found
        command = VerifyEmailCommand(token="orphan_token")

        with pytest.raises(InvalidTokenError):
            await handler.handle(command)


class TestVerifyEmailHandlerAlreadyVerified:
    """Tests for already verified user scenarios."""

    @pytest.mark.asyncio
    async def test_already_verified_user_raises_error(
        self,
        handler: VerifyEmailHandler,
        mock_user_repository: AsyncMock,
        mock_verification_token_repository: AsyncMock,
        verified_user: User,
    ) -> None:
        """Verifying an already verified user should raise UserAlreadyVerifiedError."""
        mock_verification_token_repository.get_user_id_by_token.return_value = verified_user.id
        mock_user_repository.get_by_id.return_value = verified_user
        command = VerifyEmailCommand(token="valid_token_123")

        with pytest.raises(UserAlreadyVerifiedError):
            await handler.handle(command)

    @pytest.mark.asyncio
    async def test_already_verified_does_not_save_user(
        self,
        handler: VerifyEmailHandler,
        mock_user_repository: AsyncMock,
        mock_verification_token_repository: AsyncMock,
        verified_user: User,
    ) -> None:
        """Already verified user should not trigger a save."""
        mock_verification_token_repository.get_user_id_by_token.return_value = verified_user.id
        mock_user_repository.get_by_id.return_value = verified_user
        command = VerifyEmailCommand(token="valid_token_123")

        with pytest.raises(UserAlreadyVerifiedError):
            await handler.handle(command)

        mock_user_repository.save.assert_not_called()
