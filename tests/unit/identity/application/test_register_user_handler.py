"""Unit tests for RegisterUserHandler."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.identity.application.commands.register_user import RegisterUserCommand
from src.identity.application.handlers.register_user_handler import RegisterUserHandler
from src.identity.domain.exceptions import PasswordTooShortError
from src.identity.domain.value_objects import HashedPassword


@pytest.fixture
def mock_user_repository() -> AsyncMock:
    """Create a mock user repository."""
    mock = AsyncMock()
    mock.exists_by_email.return_value = False
    return mock


@pytest.fixture
def mock_verification_token_repository() -> AsyncMock:
    """Create a mock verification token repository."""
    return AsyncMock()


@pytest.fixture
def mock_password_hasher() -> MagicMock:
    """Create a mock password hasher."""
    mock = MagicMock()
    mock.hash.return_value = HashedPassword("$argon2id$v=19$m=65536,t=3,p=4$hash")
    return mock


@pytest.fixture
def mock_token_generator() -> MagicMock:
    """Create a mock token generator."""
    mock = MagicMock()
    mock.generate_verification_token.return_value = "verify_token_123"
    mock.get_verification_token_expiry.return_value = MagicMock()
    return mock


@pytest.fixture
def mock_email_service() -> AsyncMock:
    """Create a mock email service."""
    return AsyncMock()


@pytest.fixture
def handler(
    mock_user_repository: AsyncMock,
    mock_verification_token_repository: AsyncMock,
    mock_password_hasher: MagicMock,
    mock_token_generator: MagicMock,
    mock_email_service: AsyncMock,
) -> RegisterUserHandler:
    """Create a RegisterUserHandler with mocked dependencies."""
    return RegisterUserHandler(
        user_repository=mock_user_repository,
        verification_token_repository=mock_verification_token_repository,
        password_hasher=mock_password_hasher,
        token_generator=mock_token_generator,
        email_service=mock_email_service,
    )


class TestRegisterUserHandlerSuccess:
    """Tests for successful registration scenarios."""

    @pytest.mark.asyncio
    async def test_registration_with_valid_data_returns_user_id(
        self,
        handler: RegisterUserHandler,
    ) -> None:
        """Valid registration should return a user ID."""
        command = RegisterUserCommand(
            email="newuser@example.com",
            password="validpassword123",
        )

        result = await handler.handle(command)

        assert result is not None
        assert result.value is not None  # UUID

    @pytest.mark.asyncio
    async def test_registration_saves_user(
        self,
        handler: RegisterUserHandler,
        mock_user_repository: AsyncMock,
    ) -> None:
        """Registration should save the user to the repository."""
        command = RegisterUserCommand(
            email="newuser@example.com",
            password="validpassword123",
        )

        await handler.handle(command)

        mock_user_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_registration_hashes_password(
        self,
        handler: RegisterUserHandler,
        mock_password_hasher: MagicMock,
    ) -> None:
        """Registration should hash the password."""
        command = RegisterUserCommand(
            email="newuser@example.com",
            password="validpassword123",
        )

        await handler.handle(command)

        mock_password_hasher.hash.assert_called_once_with("validpassword123")

    @pytest.mark.asyncio
    async def test_registration_saves_verification_token(
        self,
        handler: RegisterUserHandler,
        mock_verification_token_repository: AsyncMock,
    ) -> None:
        """Registration should create and save a verification token."""
        command = RegisterUserCommand(
            email="newuser@example.com",
            password="validpassword123",
        )

        await handler.handle(command)

        mock_verification_token_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_registration_sends_verification_email(
        self,
        handler: RegisterUserHandler,
        mock_email_service: AsyncMock,
    ) -> None:
        """Registration should send a verification email."""
        command = RegisterUserCommand(
            email="newuser@example.com",
            password="validpassword123",
        )

        await handler.handle(command)

        mock_email_service.send_verification_email.assert_called_once()
        call_kwargs = mock_email_service.send_verification_email.call_args.kwargs
        assert call_kwargs["email"] == "newuser@example.com"
        assert call_kwargs["token"] == "verify_token_123"


class TestRegisterUserHandlerInvalidEmail:
    """Tests for invalid email scenarios."""

    @pytest.mark.asyncio
    async def test_registration_with_invalid_email_returns_none(
        self,
        handler: RegisterUserHandler,
    ) -> None:
        """Invalid email format should return None (not reveal error)."""
        command = RegisterUserCommand(
            email="not-an-email",
            password="validpassword123",
        )

        result = await handler.handle(command)

        assert result is None

    @pytest.mark.asyncio
    async def test_registration_with_invalid_email_does_not_save_user(
        self,
        handler: RegisterUserHandler,
        mock_user_repository: AsyncMock,
    ) -> None:
        """Invalid email should not attempt to save user."""
        command = RegisterUserCommand(
            email="not-an-email",
            password="validpassword123",
        )

        await handler.handle(command)

        mock_user_repository.save.assert_not_called()


class TestRegisterUserHandlerWeakPassword:
    """Tests for weak password scenarios."""

    @pytest.mark.asyncio
    async def test_registration_with_short_password_raises_error(
        self,
        handler: RegisterUserHandler,
    ) -> None:
        """Password too short should raise PasswordTooShortError."""
        command = RegisterUserCommand(
            email="newuser@example.com",
            password="short",  # Less than 8 chars
        )

        with pytest.raises(PasswordTooShortError):
            await handler.handle(command)


class TestRegisterUserHandlerExistingEmail:
    """Tests for existing email scenarios."""

    @pytest.mark.asyncio
    async def test_registration_with_existing_email_returns_none(
        self,
        handler: RegisterUserHandler,
        mock_user_repository: AsyncMock,
    ) -> None:
        """Existing email should return None (not reveal email exists)."""
        mock_user_repository.exists_by_email.return_value = True
        command = RegisterUserCommand(
            email="existing@example.com",
            password="validpassword123",
        )

        result = await handler.handle(command)

        assert result is None

    @pytest.mark.asyncio
    async def test_registration_with_existing_email_does_not_save_user(
        self,
        handler: RegisterUserHandler,
        mock_user_repository: AsyncMock,
    ) -> None:
        """Existing email should not create a duplicate user."""
        mock_user_repository.exists_by_email.return_value = True
        command = RegisterUserCommand(
            email="existing@example.com",
            password="validpassword123",
        )

        await handler.handle(command)

        mock_user_repository.save.assert_not_called()

    @pytest.mark.asyncio
    async def test_registration_with_existing_email_does_not_send_email(
        self,
        handler: RegisterUserHandler,
        mock_user_repository: AsyncMock,
        mock_email_service: AsyncMock,
    ) -> None:
        """Existing email should not send verification email."""
        mock_user_repository.exists_by_email.return_value = True
        command = RegisterUserCommand(
            email="existing@example.com",
            password="validpassword123",
        )

        await handler.handle(command)

        mock_email_service.send_verification_email.assert_not_called()


class TestRegisterUserHandlerSecurityBehavior:
    """Tests for security-related behavior."""

    @pytest.mark.asyncio
    async def test_same_response_for_invalid_email_and_existing_email(
        self,
        handler: RegisterUserHandler,
        mock_user_repository: AsyncMock,
    ) -> None:
        """Both invalid and existing email should return None (prevent enumeration)."""
        # Test invalid email
        invalid_result = await handler.handle(
            RegisterUserCommand(email="not-an-email", password="validpassword123")
        )

        # Test existing email
        mock_user_repository.exists_by_email.return_value = True
        existing_result = await handler.handle(
            RegisterUserCommand(email="existing@example.com", password="validpassword123")
        )

        # Both should return None (same response, no enumeration)
        assert invalid_result is None
        assert existing_result is None

    @pytest.mark.asyncio
    async def test_email_is_normalized_to_lowercase(
        self,
        handler: RegisterUserHandler,
        mock_user_repository: AsyncMock,
    ) -> None:
        """Email should be stored as lowercase."""
        command = RegisterUserCommand(
            email="NewUser@EXAMPLE.COM",
            password="validpassword123",
        )

        await handler.handle(command)

        # Check that exists_by_email was called with lowercase email
        call_args = mock_user_repository.exists_by_email.call_args
        email_arg = call_args[0][0]
        assert email_arg.value == "newuser@example.com"
