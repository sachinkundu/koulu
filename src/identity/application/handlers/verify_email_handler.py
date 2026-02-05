"""Verify email command handler."""

import structlog

from src.identity.application.commands.verify_email import (
    ResendVerificationCommand,
    VerifyEmailCommand,
)
from src.identity.domain.exceptions import InvalidTokenError, UserAlreadyVerifiedError
from src.identity.domain.repositories import IUserRepository, IVerificationTokenRepository
from src.identity.domain.services import IEmailService, ITokenGenerator
from src.identity.domain.value_objects import AuthTokens, EmailAddress
from src.shared.infrastructure import event_bus

logger = structlog.get_logger()


class VerifyEmailHandler:
    """Handler for email verification."""

    def __init__(
        self,
        user_repository: IUserRepository,
        verification_token_repository: IVerificationTokenRepository,
        token_generator: ITokenGenerator,
    ) -> None:
        """Initialize with dependencies."""
        self._user_repository = user_repository
        self._verification_token_repository = verification_token_repository
        self._token_generator = token_generator

    async def handle(self, command: VerifyEmailCommand) -> AuthTokens:
        """
        Handle email verification.

        Returns AuthTokens on success.
        Raises InvalidTokenError if token invalid/expired.
        Raises UserAlreadyVerifiedError if already verified.
        """
        logger.info("verify_email_attempt")

        # Get user ID from token
        user_id = await self._verification_token_repository.get_user_id_by_token(command.token)
        if user_id is None:
            logger.warning("verify_email_invalid_token")
            raise InvalidTokenError()

        # Get user
        user = await self._user_repository.get_by_id(user_id)
        if user is None:
            logger.error("verify_email_user_not_found", user_id=str(user_id))
            raise InvalidTokenError()

        # Check if already verified
        if user.is_verified:
            logger.info("verify_email_already_verified", user_id=str(user_id))
            raise UserAlreadyVerifiedError()

        # Verify user
        user.verify_email()

        # Save user
        await self._user_repository.save(user)

        # Delete verification token
        await self._verification_token_repository.delete_by_user_id(user_id)

        # Publish domain events
        await event_bus.publish_all(user.clear_events())

        # Generate auth tokens (user is now logged in)
        tokens = self._token_generator.generate_auth_tokens(user_id)

        logger.info("verify_email_success", user_id=str(user_id))
        return tokens


class ResendVerificationHandler:
    """Handler for resending verification email."""

    def __init__(
        self,
        user_repository: IUserRepository,
        verification_token_repository: IVerificationTokenRepository,
        token_generator: ITokenGenerator,
        email_service: IEmailService,
    ) -> None:
        """Initialize with dependencies."""
        self._user_repository = user_repository
        self._verification_token_repository = verification_token_repository
        self._token_generator = token_generator
        self._email_service = email_service

    async def handle(self, command: ResendVerificationCommand) -> None:
        """
        Handle resend verification email request.

        Always succeeds (no error if email doesn't exist - security).
        """
        logger.info("resend_verification_attempt", email=command.email)

        try:
            email = EmailAddress(command.email)
        except Exception:
            # Invalid email, silently ignore
            return

        # Get user
        user = await self._user_repository.get_by_email(email)
        if user is None:
            # User doesn't exist, silently ignore (security)
            logger.info("resend_verification_user_not_found", email=command.email)
            return

        if user.is_verified:
            # Already verified, silently ignore
            logger.info("resend_verification_already_verified", email=command.email)
            return

        # Delete old token
        await self._verification_token_repository.delete_by_user_id(user.id)

        # Generate new token
        token = self._token_generator.generate_verification_token()
        expires_at = self._token_generator.get_verification_token_expiry()
        await self._verification_token_repository.save(
            user_id=user.id,
            token=token,
            expires_at=expires_at,
        )

        # Send verification email
        await self._email_service.send_verification_email(
            email=str(email),
            token=token,
        )

        logger.info("resend_verification_success", user_id=str(user.id))
