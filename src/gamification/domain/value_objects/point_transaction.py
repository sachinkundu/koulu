"""PointTransaction value object."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID

from src.gamification.domain.value_objects.point_source import PointSource


@dataclass(frozen=True)
class PointTransaction:
    """Represents a single point change (positive or negative)."""

    points: int
    source: PointSource
    source_id: UUID
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
