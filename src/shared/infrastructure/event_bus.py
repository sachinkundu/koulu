"""Simple in-memory event bus for domain events."""

from collections import defaultdict
from collections.abc import Awaitable, Callable
from typing import TypeVar

from src.shared.domain.base_event import DomainEvent

EventType = TypeVar("EventType", bound=DomainEvent)
EventHandler = Callable[[DomainEvent], Awaitable[None]]


class EventBus:
    """
    Simple in-memory event bus for publishing domain events.

    This is a basic implementation suitable for a single-process application.
    For production, consider using a message broker (Redis Pub/Sub, RabbitMQ, etc.).

    Usage:
        event_bus = EventBus()

        # Subscribe to events
        @event_bus.subscribe(UserRegistered)
        async def send_welcome_email(event: UserRegistered) -> None:
            await email_service.send_welcome(event.email)

        # Publish events
        await event_bus.publish(UserRegistered(user_id=user.id, email=user.email))
    """

    def __init__(self) -> None:
        """Initialize the event bus with empty handlers."""
        self._handlers: dict[type[DomainEvent], list[EventHandler]] = defaultdict(list)

    def subscribe(
        self, event_type: type[EventType]
    ) -> Callable[[Callable[[EventType], Awaitable[None]]], Callable[[EventType], Awaitable[None]]]:
        """
        Decorator to subscribe a handler to an event type.

        Args:
            event_type: The type of event to subscribe to

        Returns:
            Decorator function
        """

        def decorator(
            handler: Callable[[EventType], Awaitable[None]],
        ) -> Callable[[EventType], Awaitable[None]]:
            self._handlers[event_type].append(handler)  # type: ignore[arg-type]
            return handler

        return decorator

    def register_handler(self, event_type: type[DomainEvent], handler: EventHandler) -> None:
        """
        Register a handler for an event type.

        Args:
            event_type: The type of event to handle
            handler: The async handler function
        """
        self._handlers[event_type].append(handler)

    async def publish(self, event: DomainEvent) -> None:
        """
        Publish an event to all registered handlers.

        Args:
            event: The domain event to publish
        """
        event_type = type(event)
        handlers = self._handlers.get(event_type, [])

        for handler in handlers:
            await handler(event)

    async def publish_all(self, events: list[DomainEvent]) -> None:
        """
        Publish multiple events.

        Args:
            events: List of domain events to publish
        """
        for event in events:
            await self.publish(event)

    def clear(self) -> None:
        """Clear all registered handlers (useful for testing)."""
        self._handlers.clear()


# Global event bus instance
event_bus = EventBus()
