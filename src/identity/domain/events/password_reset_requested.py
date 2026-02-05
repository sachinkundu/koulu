"""PasswordResetRequested domain event."""

from dataclasses import dataclass

from src.identity.domain.value_objects import EmailAddress, UserId
from src.shared.domain import DomainEvent


@dataclass(frozen=True)
class PasswordResetRequested(DomainEvent):
    """
    Published when a user requests a password reset.

    Subscribers:
    - Email service: sends reset link email
    """

    user_id: UserId
    email: EmailAddress
