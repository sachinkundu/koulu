"""Community API interface layer."""

from src.community.interface.api.post_controller import router as posts_router

__all__ = ["posts_router"]
