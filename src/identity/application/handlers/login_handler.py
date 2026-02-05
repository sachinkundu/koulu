"""Login command handler."""

import structlog

from src.identity.application.commands.login import LoginCommand
from src.identity.domain.exceptions import (
    InvalidCredentialsError,
    UserDisabledError,
    UserNotVerifiedError,
)
from src.identity.domain.repositories import IUserRepository
from src.identity.domain.services import IPasswordHasher, ITokenGenerator
from src.identity.domain.value_objects import AuthTokens, EmailAddress
from src.shared.infrastructure import event_bus

logger = structlog.get_logger()


class LoginHandler:
    """Handler for user login."""

    def __init__(
        self,
        user_repository: IUserRepository,
        password_hasher: IPasswordHasher,
        token_generator: ITokenGenerator,
    ) -> None:
        """Initialize with dependencies."""
        self._user_repository = user_repository
        self._password_hasher = password_hasher
        self._token_generator = token_generator

    async def handle(self, command: LoginCommand) -> AuthTokens:
        """
        Handle user login.

        Returns AuthTokens on success.
        Raises InvalidCredentialsError if email/password wrong.
        Raises UserNotVerifiedError if email not verified.
        Raises UserDisabledError if account disabled.
        """
        logger.info("login_attempt", email=command.email)

        # Validate email format
        try:
            email = EmailAddress(command.email)
        except Exception:
            logger.warning("login_invalid_email", email=command.email)
            raise InvalidCredentialsError() from None

        # Get user
        user = await self._user_repository.get_by_email(email)
        if user is None:
            logger.info("login_user_not_found", email=command.email)
            raise InvalidCredentialsError()

        # Verify password
        if not self._password_hasher.verify(command.password, user.hashed_password):
            logger.warning("login_wrong_password", email=command.email)
            raise InvalidCredentialsError()

        # Check if verified
        if not user.is_verified:
            logger.info("login_not_verified", email=command.email)
            raise UserNotVerifiedError()

        # Check if active
        if not user.is_active:
            logger.info("login_disabled", email=command.email)
            raise UserDisabledError()

        # Record login
        user.record_login()
        await self._user_repository.save(user)

        # Publish domain events
        await event_bus.publish_all(user.clear_events())

        # Generate tokens
        tokens = self._token_generator.generate_auth_tokens(
            user_id=user.id,
            remember_me=command.remember_me,
        )

        logger.info("login_success", user_id=str(user.id))
        return tokens
