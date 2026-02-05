"""Identity API layer."""

from src.identity.interface.api.auth_controller import router as auth_router
from src.identity.interface.api.user_controller import router as user_router

__all__ = [
    "auth_router",
    "user_router",
]
