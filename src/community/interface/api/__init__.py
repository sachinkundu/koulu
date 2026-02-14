"""Community API interface layer."""

from src.community.interface.api.category_controller import router as categories_router
from src.community.interface.api.comment_controller import (
    comments_router,
    post_comments_router,
)
from src.community.interface.api.member_controller import router as members_router
from src.community.interface.api.post_controller import router as posts_router
from src.community.interface.api.search_controller import router as search_router

__all__ = [
    "categories_router",
    "comments_router",
    "members_router",
    "post_comments_router",
    "posts_router",
    "search_router",
]
