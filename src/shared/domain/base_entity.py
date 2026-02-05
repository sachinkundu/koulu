"""Base entity class for domain entities."""

from abc import ABC
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Generic, TypeVar
from uuid import UUID, uuid4

from src.shared.domain.base_event import DomainEvent

IdType = TypeVar("IdType")


@dataclass
class BaseEntity(ABC, Generic[IdType]):
    """
    Base class for all domain entities.

    Provides:
    - Identity (id)
    - Timestamps (created_at, updated_at)
    - Domain event collection and publishing
    """

    id: IdType
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    _events: list[DomainEvent] = field(default_factory=list, repr=False, compare=False)

    def add_event(self, event: DomainEvent) -> None:
        """Add a domain event to be published after persistence."""
        self._events.append(event)

    def clear_events(self) -> list[DomainEvent]:
        """Clear and return all pending domain events."""
        events = self._events.copy()
        self._events.clear()
        return events

    @property
    def events(self) -> list[DomainEvent]:
        """Get pending domain events (read-only view)."""
        return self._events.copy()

    def _update_timestamp(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now(UTC)

    def __eq__(self, other: object) -> bool:
        """Entities are equal if they have the same ID."""
        if not isinstance(other, BaseEntity):
            return NotImplemented
        return bool(self.id == other.id)

    def __hash__(self) -> int:
        """Hash based on entity ID."""
        return hash(self.id)


def generate_uuid() -> UUID:
    """Generate a new UUID v4."""
    return uuid4()
