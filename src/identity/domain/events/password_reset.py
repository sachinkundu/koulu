"""PasswordReset domain event."""

from dataclasses import dataclass

from src.identity.domain.value_objects import EmailAddress, UserId
from src.shared.domain import DomainEvent


@dataclass(frozen=True)
class PasswordReset(DomainEvent):
    """
    Published when a user successfully resets their password.

    Subscribers:
    - Email service: sends confirmation email
    - Audit log: record password change
    """

    user_id: UserId
    email: EmailAddress
