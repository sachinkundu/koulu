"""Community domain repositories."""

from src.community.domain.repositories.category_repository import ICategoryRepository
from src.community.domain.repositories.comment_repository import ICommentRepository
from src.community.domain.repositories.member_repository import IMemberRepository
from src.community.domain.repositories.post_repository import IPostRepository
from src.community.domain.repositories.reaction_repository import IReactionRepository
from src.community.domain.repositories.search_repository import ISearchRepository

__all__ = [
    "ICategoryRepository",
    "ICommentRepository",
    "IMemberRepository",
    "IPostRepository",
    "IReactionRepository",
    "ISearchRepository",
]
