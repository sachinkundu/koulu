"""Refresh token command handler."""

import structlog

from src.identity.application.commands.refresh_token import RefreshTokenCommand
from src.identity.domain.exceptions import InvalidTokenError
from src.identity.domain.repositories import IRefreshTokenRepository, IUserRepository
from src.identity.domain.services import ITokenGenerator
from src.identity.domain.value_objects import AuthTokens

logger = structlog.get_logger()

# Refresh tokens are valid for 30 days max (remember me)
REFRESH_TOKEN_BLACKLIST_SECONDS = 30 * 24 * 60 * 60


class RefreshTokenHandler:
    """Handler for refreshing access tokens."""

    def __init__(
        self,
        user_repository: IUserRepository,
        refresh_token_repository: IRefreshTokenRepository,
        token_generator: ITokenGenerator,
    ) -> None:
        """Initialize with dependencies."""
        self._user_repository = user_repository
        self._refresh_token_repository = refresh_token_repository
        self._token_generator = token_generator

    async def handle(self, command: RefreshTokenCommand) -> AuthTokens:
        """
        Handle token refresh.

        Returns new AuthTokens on success.
        Raises InvalidTokenError if token invalid/expired/blacklisted.
        """
        logger.info("refresh_token_attempt")

        # Check if token is blacklisted
        if await self._refresh_token_repository.is_blacklisted(command.refresh_token):
            logger.warning("refresh_token_blacklisted")
            raise InvalidTokenError()

        # Validate token and get user ID
        user_id = self._token_generator.validate_refresh_token(command.refresh_token)
        if user_id is None:
            logger.warning("refresh_token_invalid")
            raise InvalidTokenError()

        # Check if user's tokens are all blacklisted (password reset)
        if await self._refresh_token_repository.is_user_blacklisted(user_id):
            logger.warning("refresh_token_user_blacklisted", user_id=str(user_id))
            raise InvalidTokenError()

        # Get user to verify they still exist and are active
        user = await self._user_repository.get_by_id(user_id)
        if user is None or not user.is_active:
            logger.warning("refresh_token_user_invalid", user_id=str(user_id))
            raise InvalidTokenError()

        # Blacklist old refresh token (rotation)
        await self._refresh_token_repository.blacklist(
            command.refresh_token,
            REFRESH_TOKEN_BLACKLIST_SECONDS,
        )

        # Generate new tokens
        tokens = self._token_generator.generate_auth_tokens(user_id)

        logger.info("refresh_token_success", user_id=str(user_id))
        return tokens
