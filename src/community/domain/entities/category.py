"""Category entity."""

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4

from src.community.domain.value_objects import CategoryId, CommunityId


@dataclass
class Category:
    """
    Category entity.

    Represents a category for organizing posts within a community.
    Categories are managed by admins only.
    """

    id: CategoryId
    community_id: CommunityId
    name: str
    slug: str
    emoji: str
    description: str | None = None
    created_at: datetime = datetime.now(UTC)
    updated_at: datetime = datetime.now(UTC)

    @classmethod
    def create(
        cls,
        community_id: CommunityId,
        name: str,
        slug: str,
        emoji: str,
        description: str | None = None,
    ) -> "Category":
        """
        Factory method to create a new category.

        Args:
            community_id: The community this category belongs to
            name: Display name for the category
            slug: URL-friendly slug
            emoji: Emoji icon for the category
            description: Optional description

        Returns:
            A new Category instance
        """
        category_id = CategoryId(value=uuid4())
        return cls(
            id=category_id,
            community_id=community_id,
            name=name,
            slug=slug,
            emoji=emoji,
            description=description,
        )

    def update(
        self,
        name: str | None = None,
        emoji: str | None = None,
        description: str | None = None,
    ) -> None:
        """
        Update category fields.

        Args:
            name: New name (optional)
            emoji: New emoji (optional)
            description: New description (optional)
        """
        if name is not None:
            self.name = name
        if emoji is not None:
            self.emoji = emoji
        if description is not None:
            self.description = description

        self.updated_at = datetime.now(UTC)

    def __eq__(self, other: object) -> bool:
        """Categories are equal if they have the same ID."""
        if not isinstance(other, Category):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash based on category ID."""
        return hash(self.id)
