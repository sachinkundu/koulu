"""Verification token repository interface."""

from abc import ABC, abstractmethod
from datetime import datetime

from src.identity.domain.value_objects import UserId


class IVerificationTokenRepository(ABC):
    """
    Interface for email verification token persistence.

    Tokens are used for email verification (24-hour expiry).
    """

    @abstractmethod
    async def save(
        self,
        user_id: UserId,
        token: str,
        expires_at: datetime,
    ) -> None:
        """
        Save a verification token.

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

        Only returns if token is valid and not expired.

        Args:
            token: The token to look up

        Returns:
            UserId if valid, None if invalid or expired
        """
        ...

    @abstractmethod
    async def delete_by_user_id(self, user_id: UserId) -> None:
        """
        Delete all tokens for a user.

        Args:
            user_id: The user whose tokens to delete
        """
        ...

    @abstractmethod
    async def delete_by_token(self, token: str) -> None:
        """
        Delete a specific token.

        Args:
            token: The token to delete
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
