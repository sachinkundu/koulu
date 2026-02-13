"""Member directory DTOs."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class MemberDirectoryEntry:
    """Flat DTO combining membership + profile data for the directory."""

    user_id: UUID
    display_name: str | None
    avatar_url: str | None
    role: str
    bio: str | None
    joined_at: datetime


@dataclass
class MemberDirectoryResult:
    """Result of a directory listing query with pagination."""

    items: list[MemberDirectoryEntry]
    total_count: int
    cursor: str | None
    has_more: bool
