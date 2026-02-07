"""Community domain repositories."""

from src.community.domain.repositories.category_repository import ICategoryRepository
from src.community.domain.repositories.member_repository import IMemberRepository
from src.community.domain.repositories.post_repository import IPostRepository

__all__ = [
    "ICategoryRepository",
    "IMemberRepository",
    "IPostRepository",
]
