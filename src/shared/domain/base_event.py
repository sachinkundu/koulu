"""Base domain event class."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4


@dataclass(frozen=True, kw_only=True)
class DomainEvent:
    """
    Base class for all domain events.

    Domain events are:
    - Immutable (frozen=True)
    - Named in past tense (e.g., UserRegistered, OrderPlaced)
    - Contain all data needed by subscribers
    - Timestamped with when they occurred

    Events are published after successful persistence and consumed
    by event handlers for side effects (emails, analytics, cross-context
    communication, etc.).
    """

    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def event_type(self) -> str:
        """Get the event type name (class name)."""
        return self.__class__.__name__
