"""MemberRole value object."""

from enum import StrEnum


class MemberRole(StrEnum):
    """
    Community member role enumeration.

    Defines the permission levels for community members:
    - MEMBER: Basic posting and interaction rights
    - MODERATOR: Can delete posts, pin, lock, but not manage categories
    - ADMIN: Full permissions including category management
    """

    MEMBER = "MEMBER"
    MODERATOR = "MODERATOR"
    ADMIN = "ADMIN"

    def can_delete_any_post(self) -> bool:
        """Check if this role can delete any post (not just own)."""
        return self in (MemberRole.MODERATOR, MemberRole.ADMIN)

    def can_pin_posts(self) -> bool:
        """Check if this role can pin posts."""
        return self in (MemberRole.MODERATOR, MemberRole.ADMIN)

    def can_lock_posts(self) -> bool:
        """Check if this role can lock posts."""
        return self in (MemberRole.MODERATOR, MemberRole.ADMIN)

    def can_manage_categories(self) -> bool:
        """Check if this role can create/edit/delete categories."""
        return self == MemberRole.ADMIN
