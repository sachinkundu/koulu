"""Community application commands."""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class CreatePostCommand:
    """Command to create a new post."""

    community_id: UUID
    author_id: UUID
    category_id: UUID | None  # If None, use category by name
    category_name: str | None  # Alternative to category_id
    title: str
    content: str
    image_url: str | None = None


@dataclass(frozen=True)
class UpdatePostCommand:
    """Command to update an existing post."""

    post_id: UUID
    editor_id: UUID
    title: str | None = None
    content: str | None = None
    image_url: str | None = None
    category_id: UUID | None = None


@dataclass(frozen=True)
class DeletePostCommand:
    """Command to delete a post."""

    post_id: UUID
    deleter_id: UUID
