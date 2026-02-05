"""Password reset command handlers."""

import structlog

from src.identity.application.commands.password_reset import (
    RequestPasswordResetCommand,
    ResetPasswordCommand,
)
from src.identity.domain.entities import User
from src.identity.domain.exceptions import InvalidTokenError
from src.identity.domain.repositories import (
    IRefreshTokenRepository,
    IResetTokenRepository,
    IUserRepository,
)
from src.identity.domain.services import IEmailService, IPasswordHasher, ITokenGenerator
from src.identity.domain.value_objects import EmailAddress
from src.shared.infrastructure import event_bus

logger = structlog.get_logger()

# Blacklist all tokens for 30 days after password reset
USER_BLACKLIST_SECONDS = 30 * 24 * 60 * 60


class RequestPasswordResetHandler:
    """Handler for password reset request."""

    def __init__(
        self,
        user_repository: IUserRepository,
        reset_token_repository: IResetTokenRepository,
        token_generator: ITokenGenerator,
        email_service: IEmailService,
    ) -> None:
        """Initialize with dependencies."""
        self._user_repository = user_repository
        self._reset_token_repository = reset_token_repository
        self._token_generator = token_generator
        self._email_service = email_service

    async def handle(self, command: RequestPasswordResetCommand) -> None:
        """
        Handle password reset request.

        Always succeeds (no error if email doesn't exist - security).
        """
        logger.info("password_reset_request", email=command.email)

        try:
            email = EmailAddress(command.email)
        except Exception:
            # Invalid email, silently ignore
            return

        # Get user
        user = await self._user_repository.get_by_email(email)
        if user is None:
            # User doesn't exist, silently succeed (security)
            logger.info("password_reset_user_not_found", email=command.email)
            return

        if not user.is_verified or not user.is_active:
            # Not verified or disabled, silently succeed
            logger.info("password_reset_user_inactive", email=command.email)
            return

        # Delete any existing reset tokens
        await self._reset_token_repository.delete_by_user_id(user.id)

        # Generate reset token
        token = self._token_generator.generate_reset_token()
        expires_at = self._token_generator.get_reset_token_expiry()
        await self._reset_token_repository.save(
            user_id=user.id,
            token=token,
            expires_at=expires_at,
        )

        # Send password reset email
        await self._email_service.send_password_reset_email(
            email=str(email),
            token=token,
        )

        # Publish domain events (for analytics, audit, etc.)
        user.request_password_reset()
        await event_bus.publish_all(user.clear_events())

        logger.info("password_reset_request_success", user_id=str(user.id))


class ResetPasswordHandler:
    """Handler for password reset."""

    def __init__(
        self,
        user_repository: IUserRepository,
        reset_token_repository: IResetTokenRepository,
        refresh_token_repository: IRefreshTokenRepository,
        password_hasher: IPasswordHasher,
    ) -> None:
        """Initialize with dependencies."""
        self._user_repository = user_repository
        self._reset_token_repository = reset_token_repository
        self._refresh_token_repository = refresh_token_repository
        self._password_hasher = password_hasher

    async def handle(self, command: ResetPasswordCommand) -> None:
        """
        Handle password reset.

        Raises InvalidTokenError if token invalid/expired/used.
        Raises PasswordTooShortError if password too short.
        """
        logger.info("password_reset_attempt")

        # Validate password strength first
        User.validate_password_strength(command.new_password)

        # Get user ID from token
        user_id = await self._reset_token_repository.get_user_id_by_token(command.token)
        if user_id is None:
            logger.warning("password_reset_invalid_token")
            raise InvalidTokenError()

        # Get user
        user = await self._user_repository.get_by_id(user_id)
        if user is None:
            logger.error("password_reset_user_not_found", user_id=str(user_id))
            raise InvalidTokenError()

        # Hash new password
        hashed_password = self._password_hasher.hash(command.new_password)

        # Reset password
        user.reset_password(hashed_password)
        await self._user_repository.save(user)

        # Mark token as used
        await self._reset_token_repository.mark_as_used(command.token)

        # Blacklist all refresh tokens for this user
        await self._refresh_token_repository.blacklist_all_for_user(user_id, USER_BLACKLIST_SECONDS)

        # Publish domain events
        await event_bus.publish_all(user.clear_events())

        logger.info("password_reset_success", user_id=str(user_id))
