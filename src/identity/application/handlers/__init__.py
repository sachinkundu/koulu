"""Identity application command handlers."""

from src.identity.application.handlers.complete_profile_handler import (
    CompleteProfileHandler,
)
from src.identity.application.handlers.login_handler import LoginHandler
from src.identity.application.handlers.logout_handler import LogoutHandler
from src.identity.application.handlers.password_reset_handler import (
    RequestPasswordResetHandler,
    ResetPasswordHandler,
)
from src.identity.application.handlers.refresh_token_handler import RefreshTokenHandler
from src.identity.application.handlers.register_user_handler import RegisterUserHandler
from src.identity.application.handlers.update_profile_handler import UpdateProfileHandler
from src.identity.application.handlers.verify_email_handler import (
    ResendVerificationHandler,
    VerifyEmailHandler,
)

__all__ = [
    "CompleteProfileHandler",
    "LoginHandler",
    "LogoutHandler",
    "RefreshTokenHandler",
    "RegisterUserHandler",
    "RequestPasswordResetHandler",
    "ResendVerificationHandler",
    "ResetPasswordHandler",
    "UpdateProfileHandler",
    "VerifyEmailHandler",
]
