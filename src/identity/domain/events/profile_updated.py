"""ProfileUpdated domain event."""

from dataclasses import dataclass

from src.identity.domain.value_objects import UserId
from src.shared.domain import DomainEvent


@dataclass(frozen=True)
class ProfileUpdated(DomainEvent):
    """
    Published when a user updates their profile.

    Contains the list of fields that were changed to allow subscribers
    to react to specific changes.

    Subscribers:
    - Analytics: track which fields users update
    - Cache: invalidate profile caches
    - Notifications (future): notify followers of profile updates
    """

    user_id: UserId
    changed_fields: list[str]
