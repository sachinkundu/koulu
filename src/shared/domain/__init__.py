"""Shared domain components."""

from src.shared.domain.base_entity import BaseEntity, generate_uuid
from src.shared.domain.base_event import DomainEvent
from src.shared.domain.base_value_object import BaseValueObject

__all__ = [
    "BaseEntity",
    "BaseValueObject",
    "DomainEvent",
    "generate_uuid",
]
