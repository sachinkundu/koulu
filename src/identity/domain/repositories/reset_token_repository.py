"""Password reset token repository interface."""

from abc import ABC, abstractmethod
from datetime import datetime

from src.identity.domain.value_objects import UserId


class IResetTokenRepository(ABC):
    """
    Interface for password reset token persistence.

    Tokens are single-use with 1-hour expiry.
    """

    @abstractmethod
    async def save(
        self,
        user_id: UserId,
        token: str,
        expires_at: datetime,
    ) -> None:
        """
        Save a reset token.

        If a token already exists for the user, it should be replaced.

        Args:
            user_id: The user this token belongs to
            token: The secure token string
            expires_at: When the token expires
        """
        ...

    @abstractmethod
    async def get_user_id_by_token(self, token: str) -> UserId | None:
        """
        Get the user ID associated with a token.

        Only returns if token is valid, not expired, and not used.

        Args:
            token: The token to look up

        Returns:
            UserId if valid, None if invalid, expired, or already used
        """
        ...

    @abstractmethod
    async def mark_as_used(self, token: str) -> None:
        """
        Mark a token as used (single-use).

        Args:
            token: The token to mark as used
        """
        ...

    @abstractmethod
    async def delete_by_user_id(self, user_id: UserId) -> None:
        """
        Delete all reset tokens for a user.

        Args:
            user_id: The user whose tokens to delete
        """
        ...

    @abstractmethod
    async def delete_expired(self) -> int:
        """
        Delete all expired tokens.

        Returns:
            Number of tokens deleted
        """
        ...
