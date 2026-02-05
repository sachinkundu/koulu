"""UserLoggedIn domain event."""

from dataclasses import dataclass

from src.identity.domain.value_objects import UserId
from src.shared.domain import DomainEvent


@dataclass(frozen=True)
class UserLoggedIn(DomainEvent):
    """
    Published when a user successfully logs in.

    Subscribers:
    - Analytics: track login
    - Audit log: record login event
    """

    user_id: UserId
