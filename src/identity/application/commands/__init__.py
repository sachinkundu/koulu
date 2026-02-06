"""Identity application commands."""

from src.identity.application.commands.complete_profile import CompleteProfileCommand
from src.identity.application.commands.login import LoginCommand
from src.identity.application.commands.logout import LogoutCommand
from src.identity.application.commands.password_reset import (
    RequestPasswordResetCommand,
    ResetPasswordCommand,
)
from src.identity.application.commands.refresh_token import RefreshTokenCommand
from src.identity.application.commands.register_user import RegisterUserCommand
from src.identity.application.commands.update_profile import UpdateProfileCommand
from src.identity.application.commands.verify_email import (
    ResendVerificationCommand,
    VerifyEmailCommand,
)

__all__ = [
    "CompleteProfileCommand",
    "LoginCommand",
    "LogoutCommand",
    "RefreshTokenCommand",
    "RegisterUserCommand",
    "RequestPasswordResetCommand",
    "ResendVerificationCommand",
    "ResetPasswordCommand",
    "UpdateProfileCommand",
    "VerifyEmailCommand",
]
