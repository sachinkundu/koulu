"""Community application handlers."""

from src.community.application.handlers.add_comment_handler import AddCommentHandler
from src.community.application.handlers.create_post_handler import CreatePostHandler
from src.community.application.handlers.delete_comment_handler import DeleteCommentHandler
from src.community.application.handlers.delete_post_handler import DeletePostHandler
from src.community.application.handlers.edit_comment_handler import EditCommentHandler
from src.community.application.handlers.get_feed_handler import GetFeedHandler
from src.community.application.handlers.get_post_comments_handler import GetPostCommentsHandler
from src.community.application.handlers.get_post_handler import GetPostHandler
from src.community.application.handlers.like_comment_handler import LikeCommentHandler
from src.community.application.handlers.like_post_handler import LikePostHandler
from src.community.application.handlers.list_categories_handler import ListCategoriesHandler
from src.community.application.handlers.lock_post_handler import LockPostHandler
from src.community.application.handlers.unlike_comment_handler import UnlikeCommentHandler
from src.community.application.handlers.unlike_post_handler import UnlikePostHandler
from src.community.application.handlers.unlock_post_handler import UnlockPostHandler
from src.community.application.handlers.update_post_handler import UpdatePostHandler

__all__ = [
    "AddCommentHandler",
    "CreatePostHandler",
    "DeleteCommentHandler",
    "DeletePostHandler",
    "EditCommentHandler",
    "GetFeedHandler",
    "GetPostCommentsHandler",
    "GetPostHandler",
    "LikeCommentHandler",
    "LikePostHandler",
    "ListCategoriesHandler",
    "LockPostHandler",
    "UnlikeCommentHandler",
    "UnlikePostHandler",
    "UnlockPostHandler",
    "UpdatePostHandler",
]
