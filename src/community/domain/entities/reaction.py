"""Reaction entity."""

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid4

from src.community.domain.value_objects import CommentId, PostId, ReactionId
from src.identity.domain.value_objects import UserId


@dataclass(frozen=True)
class Reaction:
    """
    Reaction entity.

    Represents a "like" on a post or comment.
    Immutable - to unlike, delete the reaction.
    """

    id: ReactionId
    user_id: UserId
    target_type: str  # "post" or "comment"
    target_id: UUID  # PostId.value or CommentId.value
    created_at: datetime

    @classmethod
    def create(
        cls,
        user_id: UserId,
        target_type: str,
        target_id: PostId | CommentId,
    ) -> "Reaction":
        """
        Factory method to create a new reaction.

        Args:
            user_id: The user creating the reaction
            target_type: "post" or "comment"
            target_id: The post or comment being liked

        Returns:
            A new Reaction instance
        """
        return cls(
            id=ReactionId(value=uuid4()),
            user_id=user_id,
            target_type=target_type,
            target_id=target_id.value,
            created_at=datetime.now(UTC),
        )

    def __eq__(self, other: object) -> bool:
        """Reactions are equal if they have the same ID."""
        if not isinstance(other, Reaction):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash based on reaction ID."""
        return hash(self.id)
