"""UserVerified domain event."""

from dataclasses import dataclass

from src.identity.domain.value_objects import UserId
from src.shared.domain import DomainEvent


@dataclass(frozen=True)
class UserVerified(DomainEvent):
    """
    Published when a user verifies their email.

    Subscribers:
    - Analytics: track verification
    - Email service: send welcome email
    """

    user_id: UserId
