"""Token generator interface."""

from abc import ABC, abstractmethod
from datetime import datetime

from src.identity.domain.value_objects import AuthTokens, UserId


class ITokenGenerator(ABC):
    """
    Interface for generating and validating authentication tokens.

    Implementations should use:
    - JWT for access and refresh tokens (HS256)
    - Secure random tokens for verification and reset
    """

    @abstractmethod
    def generate_auth_tokens(
        self,
        user_id: UserId,
        remember_me: bool = False,
    ) -> AuthTokens:
        """
        Generate access and refresh tokens for a user.

        Args:
            user_id: The user's ID to include in tokens
            remember_me: If True, refresh token lasts 30 days, else 7 days

        Returns:
            AuthTokens with access_token, refresh_token, and expiry
        """
        ...

    @abstractmethod
    def generate_verification_token(self) -> str:
        """
        Generate a secure token for email verification.

        Token is valid for 24 hours.

        Returns:
            A secure random token string
        """
        ...

    @abstractmethod
    def generate_reset_token(self) -> str:
        """
        Generate a secure token for password reset.

        Token is valid for 1 hour.

        Returns:
            A secure random token string
        """
        ...

    @abstractmethod
    def validate_access_token(self, token: str) -> UserId | None:
        """
        Validate an access token and extract user ID.

        Args:
            token: The JWT access token to validate

        Returns:
            UserId if valid, None if invalid or expired
        """
        ...

    @abstractmethod
    def validate_refresh_token(self, token: str) -> UserId | None:
        """
        Validate a refresh token and extract user ID.

        Args:
            token: The JWT refresh token to validate

        Returns:
            UserId if valid, None if invalid or expired
        """
        ...

    @abstractmethod
    def get_verification_token_expiry(self) -> datetime:
        """Get the expiry datetime for a new verification token (24h from now)."""
        ...

    @abstractmethod
    def get_reset_token_expiry(self) -> datetime:
        """Get the expiry datetime for a new reset token (1h from now)."""
        ...
