"""Logout command handler."""

import structlog

from src.identity.application.commands.logout import LogoutCommand
from src.identity.domain.repositories import IRefreshTokenRepository
from src.identity.domain.services import ITokenGenerator

logger = structlog.get_logger()

# Refresh tokens are valid for 30 days max (remember me)
REFRESH_TOKEN_BLACKLIST_SECONDS = 30 * 24 * 60 * 60


class LogoutHandler:
    """Handler for user logout."""

    def __init__(
        self,
        refresh_token_repository: IRefreshTokenRepository,
        token_generator: ITokenGenerator,
    ) -> None:
        """Initialize with dependencies."""
        self._refresh_token_repository = refresh_token_repository
        self._token_generator = token_generator

    async def handle(self, command: LogoutCommand) -> None:
        """
        Handle user logout.

        Always succeeds (even if token is invalid - security).
        """
        logger.info("logout_attempt")

        # Validate token to get user ID (for logging)
        user_id = self._token_generator.validate_refresh_token(command.refresh_token)

        # Blacklist the refresh token
        await self._refresh_token_repository.blacklist(
            command.refresh_token,
            REFRESH_TOKEN_BLACKLIST_SECONDS,
        )

        if user_id:
            logger.info("logout_success", user_id=str(user_id))
        else:
            logger.info("logout_success", user_id="unknown")
