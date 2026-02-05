"""Identity domain service interfaces."""

from src.identity.domain.services.avatar_generator import IAvatarGenerator
from src.identity.domain.services.email_service import IEmailService
from src.identity.domain.services.password_hasher import IPasswordHasher
from src.identity.domain.services.token_generator import ITokenGenerator

__all__ = [
    "IAvatarGenerator",
    "IEmailService",
    "IPasswordHasher",
    "ITokenGenerator",
]
