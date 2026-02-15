"""MemberPoints aggregate root."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from src.gamification.domain.events.gamification_events import (
    MemberLeveledUp,
    PointsAwarded,
    PointsDeducted,
)
from src.gamification.domain.exceptions import DuplicateLessonCompletionError
from src.gamification.domain.value_objects.point_source import PointSource
from src.gamification.domain.value_objects.point_transaction import PointTransaction
from src.shared.domain.base_entity import BaseEntity

if TYPE_CHECKING:
    from src.gamification.domain.entities.level_configuration import LevelConfiguration


@dataclass
class MemberPoints(BaseEntity[UUID]):
    """
    Aggregate root: a member's point balance and level in a community.

    Invariants:
    - total_points >= 0
    - current_level never decreases (ratchet)
    - Lesson completion points awarded once per lesson
    """

    community_id: UUID = field(default_factory=uuid4)
    user_id: UUID = field(default_factory=uuid4)
    total_points: int = 0
    current_level: int = 1
    transactions: list[PointTransaction] = field(default_factory=list)

    @classmethod
    def create(cls, community_id: UUID, user_id: UUID) -> MemberPoints:
        """Create a new MemberPoints with 0 points at level 1."""
        return cls(
            id=uuid4(),
            community_id=community_id,
            user_id=user_id,
            total_points=0,
            current_level=1,
        )

    def award_points(
        self,
        source: PointSource,
        source_id: UUID,
        level_config: LevelConfiguration,
    ) -> None:
        """Award points from an engagement action."""
        # Lesson deduplication
        if source == PointSource.LESSON_COMPLETED:
            for txn in self.transactions:
                if txn.source == PointSource.LESSON_COMPLETED and txn.source_id == source_id:
                    raise DuplicateLessonCompletionError(str(source_id))

        amount = source.points
        self.total_points += amount

        self.transactions.append(
            PointTransaction(points=amount, source=source, source_id=source_id)
        )

        self.add_event(
            PointsAwarded(
                member_id=self.user_id,
                community_id=self.community_id,
                points=amount,
                new_total=self.total_points,
                source=source.source_name,
            )
        )

        self._recalculate_level(level_config)
        self._update_timestamp()

    def deduct_points(
        self,
        source: PointSource,
        source_id: UUID,
        level_config: LevelConfiguration,  # noqa: ARG002 - kept for API symmetry with award_points
    ) -> None:
        """Deduct points (e.g., unlike). Floor at 0, level never decreases."""
        amount = source.points
        self.total_points = max(0, self.total_points - amount)

        self.transactions.append(
            PointTransaction(points=-amount, source=source, source_id=source_id)
        )

        self.add_event(
            PointsDeducted(
                member_id=self.user_id,
                community_id=self.community_id,
                points=amount,
                new_total=self.total_points,
                source=source.source_name,
            )
        )

        # No level recalculation needed -- ratchet rule means level can't go down
        self._update_timestamp()

    def recalculate_level(self, level_config: LevelConfiguration) -> None:
        """Public recalculation (for admin threshold changes)."""
        self._recalculate_level(level_config)

    def _recalculate_level(self, level_config: LevelConfiguration) -> None:
        """Recalculate level from points -- ratchet: only goes up."""
        calculated_level = level_config.get_level_for_points(self.total_points)
        if calculated_level > self.current_level:
            old_level = self.current_level
            self.current_level = calculated_level
            self.add_event(
                MemberLeveledUp(
                    member_id=self.user_id,
                    community_id=self.community_id,
                    old_level=old_level,
                    new_level=self.current_level,
                    new_level_name=level_config.name_for_level(self.current_level),
                )
            )
