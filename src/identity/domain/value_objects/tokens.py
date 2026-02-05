"""Token-related value objects."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class AuthTokens:
    """
    Authentication tokens returned after successful login.

    Contains:
    - access_token: Short-lived JWT for API authentication (30 min)
    - refresh_token: Long-lived token for getting new access tokens (7-30 days)
    - token_type: Always "bearer"
    - expires_at: When the access token expires
    """

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_at: datetime | None = None

    def __str__(self) -> str:
        """Return masked representation for security."""
        return f"AuthTokens(type={self.token_type}, expires_at={self.expires_at})"

    def __repr__(self) -> str:
        """Return masked representation for security."""
        return self.__str__()


@dataclass(frozen=True)
class VerificationToken:
    """
    Email verification token.

    Attributes:
        token: The secure random token string
        expires_at: When the token expires (24 hours after creation)
    """

    token: str
    expires_at: datetime

    @property
    def is_expired(self) -> bool:
        """Check if the token has expired."""
        return datetime.now(self.expires_at.tzinfo) > self.expires_at


@dataclass(frozen=True)
class ResetToken:
    """
    Password reset token.

    Attributes:
        token: The secure random token string
        expires_at: When the token expires (1 hour after creation)
    """

    token: str
    expires_at: datetime

    @property
    def is_expired(self) -> bool:
        """Check if the token has expired."""
        return datetime.now(self.expires_at.tzinfo) > self.expires_at
