"""CommunityMember entity."""

from dataclasses import dataclass
from datetime import UTC, datetime

from src.community.domain.value_objects import CommunityId, MemberRole
from src.identity.domain.value_objects import UserId


@dataclass
class CommunityMember:
    """
    CommunityMember entity.

    Represents a user's membership in a community with their role.
    Links the Identity context (User) to the Community context.
    """

    id: UserId  # Same as user_id for simplicity
    user_id: UserId
    community_id: CommunityId
    role: MemberRole
    joined_at: datetime = datetime.now(UTC)
    is_active: bool = True

    @classmethod
    def create(
        cls,
        user_id: UserId,
        community_id: CommunityId,
        role: MemberRole = MemberRole.MEMBER,
    ) -> "CommunityMember":
        """
        Factory method to create a new community member.

        Args:
            user_id: The user's ID from Identity context
            community_id: The community they're joining
            role: Initial role (defaults to MEMBER)

        Returns:
            A new CommunityMember instance
        """
        return cls(
            id=user_id,  # Use user_id as primary key
            user_id=user_id,
            community_id=community_id,
            role=role,
        )

    def promote_to_moderator(self) -> None:
        """Promote member to moderator role."""
        self.role = MemberRole.MODERATOR

    def promote_to_admin(self) -> None:
        """Promote member to admin role."""
        self.role = MemberRole.ADMIN

    def demote_to_member(self) -> None:
        """Demote to basic member role."""
        self.role = MemberRole.MEMBER

    def deactivate(self) -> None:
        """Deactivate the membership (soft delete)."""
        self.is_active = False

    def reactivate(self) -> None:
        """Reactivate the membership."""
        self.is_active = True

    def __eq__(self, other: object) -> bool:
        """Members are equal if they have the same user_id and community_id."""
        if not isinstance(other, CommunityMember):
            return NotImplemented
        return self.user_id == other.user_id and self.community_id == other.community_id

    def __hash__(self) -> int:
        """Hash based on user_id and community_id."""
        return hash((self.user_id, self.community_id))
