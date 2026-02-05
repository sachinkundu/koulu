"""UserRegistered domain event."""

from dataclasses import dataclass

from src.identity.domain.value_objects import EmailAddress, UserId
from src.shared.domain import DomainEvent


@dataclass(frozen=True)
class UserRegistered(DomainEvent):
    """
    Published when a new user registers.

    Subscribers:
    - Email service: sends verification email
    """

    user_id: UserId
    email: EmailAddress
