"""Refresh token command."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RefreshTokenCommand:
    """Command to refresh access token using refresh token."""

    refresh_token: str
