"""Community API interface layer."""

from src.community.interface.api.comment_controller import (
    comments_router,
    post_comments_router,
)
from src.community.interface.api.post_controller import router as posts_router

__all__ = ["comments_router", "post_comments_router", "posts_router"]
