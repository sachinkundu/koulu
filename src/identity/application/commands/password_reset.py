"""Password reset commands."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RequestPasswordResetCommand:
    """Command to request password reset email."""

    email: str


@dataclass(frozen=True)
class ResetPasswordCommand:
    """Command to reset password with token."""

    token: str
    new_password: str
