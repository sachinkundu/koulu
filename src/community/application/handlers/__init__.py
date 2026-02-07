"""Community application handlers."""

from src.community.application.handlers.create_post_handler import CreatePostHandler
from src.community.application.handlers.delete_post_handler import DeletePostHandler
from src.community.application.handlers.get_post_handler import GetPostHandler
from src.community.application.handlers.update_post_handler import UpdatePostHandler

__all__ = [
    "CreatePostHandler",
    "DeletePostHandler",
    "GetPostHandler",
    "UpdatePostHandler",
]
