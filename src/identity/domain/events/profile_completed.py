"""ProfileCompleted domain event."""

from dataclasses import dataclass

from src.identity.domain.value_objects import DisplayName, UserId
from src.shared.domain import DomainEvent


@dataclass(frozen=True)
class ProfileCompleted(DomainEvent):
    """
    Published when a user completes their profile.

    Subscribers:
    - Analytics: track profile completion
    """

    user_id: UserId
    display_name: DisplayName
