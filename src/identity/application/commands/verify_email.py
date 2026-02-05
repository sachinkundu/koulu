"""Verify email command."""

from dataclasses import dataclass


@dataclass(frozen=True)
class VerifyEmailCommand:
    """Command to verify user email with token."""

    token: str


@dataclass(frozen=True)
class ResendVerificationCommand:
    """Command to resend verification email."""

    email: str
