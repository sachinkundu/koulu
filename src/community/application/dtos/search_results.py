"""Search result DTOs."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class MemberSearchEntry:
    """Member search result entry."""

    user_id: UUID
    display_name: str | None
    username: str | None
    avatar_url: str | None
    role: str
    bio: str | None
    joined_at: datetime


@dataclass
class PostSearchEntry:
    """Post search result entry."""

    id: UUID
    title: str
    body_snippet: str
    author_name: str | None
    author_avatar_url: str | None
    category_name: str | None
    category_emoji: str | None
    created_at: datetime
    like_count: int
    comment_count: int


@dataclass
class SearchResult:
    """Combined search result with both-tab counts."""

    items: list[MemberSearchEntry] | list[PostSearchEntry]
    total_count: int
    member_count: int
    post_count: int
    has_more: bool
