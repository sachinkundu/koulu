"""Logout command."""

from dataclasses import dataclass


@dataclass(frozen=True)
class LogoutCommand:
    """Command to log out a user (invalidate refresh token)."""

    refresh_token: str
