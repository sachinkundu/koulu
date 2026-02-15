"""Gamification domain events."""

from dataclasses import dataclass
from uuid import UUID

from src.shared.domain.base_event import DomainEvent


@dataclass(frozen=True)
class PointsAwarded(DomainEvent):
    """Published when points are awarded to a member."""

    member_id: UUID
    community_id: UUID
    points: int
    new_total: int
    source: str

    @property
    def event_type(self) -> str:
        return "PointsAwarded"


@dataclass(frozen=True)
class PointsDeducted(DomainEvent):
    """Published when points are deducted from a member."""

    member_id: UUID
    community_id: UUID
    points: int
    new_total: int
    source: str

    @property
    def event_type(self) -> str:
        return "PointsDeducted"


@dataclass(frozen=True)
class MemberLeveledUp(DomainEvent):
    """Published when a member reaches a new level."""

    member_id: UUID
    community_id: UUID
    old_level: int
    new_level: int
    new_level_name: str

    @property
    def event_type(self) -> str:
        return "MemberLeveledUp"
