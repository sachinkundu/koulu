"""Refresh token repository interface (blacklist)."""

from abc import ABC, abstractmethod

from src.identity.domain.value_objects import UserId


class IRefreshTokenRepository(ABC):
    """
    Interface for refresh token blacklist.

    Used for token rotation (invalidating old tokens) and
    invalidating all tokens on password reset.

    Implementation should use Redis for performance.
    """

    @abstractmethod
    async def blacklist(self, token: str, expires_in_seconds: int) -> None:
        """
        Add a refresh token to the blacklist.

        Token should be automatically removed after expiry.

        Args:
            token: The token to blacklist
            expires_in_seconds: How long to keep in blacklist
        """
        ...

    @abstractmethod
    async def is_blacklisted(self, token: str) -> bool:
        """
        Check if a token is blacklisted.

        Args:
            token: The token to check

        Returns:
            True if blacklisted, False otherwise
        """
        ...

    @abstractmethod
    async def blacklist_all_for_user(
        self,
        user_id: UserId,
        expires_in_seconds: int,
    ) -> None:
        """
        Blacklist all refresh tokens for a user.

        Used when password is reset to invalidate all sessions.

        Args:
            user_id: The user whose tokens to blacklist
            expires_in_seconds: How long to keep in blacklist
        """
        ...

    @abstractmethod
    async def is_user_blacklisted(self, user_id: UserId) -> bool:
        """
        Check if all tokens for a user are blacklisted.

        Args:
            user_id: The user to check

        Returns:
            True if all tokens blacklisted, False otherwise
        """
        ...
