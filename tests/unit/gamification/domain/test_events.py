"""Tests for gamification domain events."""

from uuid import uuid4

from src.gamification.domain.events.gamification_events import (
    MemberLeveledUp,
    PointsAwarded,
    PointsDeducted,
)
from src.shared.domain.base_event import DomainEvent


class TestPointsAwarded:
    def test_is_domain_event(self) -> None:
        event = PointsAwarded(
            member_id=uuid4(),
            community_id=uuid4(),
            points=2,
            new_total=12,
            source="post_created",
        )
        assert isinstance(event, DomainEvent)

    def test_event_type(self) -> None:
        event = PointsAwarded(
            member_id=uuid4(),
            community_id=uuid4(),
            points=1,
            new_total=5,
            source="post_liked",
        )
        assert event.event_type == "PointsAwarded"


class TestPointsDeducted:
    def test_event_type(self) -> None:
        event = PointsDeducted(
            member_id=uuid4(),
            community_id=uuid4(),
            points=1,
            new_total=4,
            source="post_liked",
        )
        assert event.event_type == "PointsDeducted"


class TestMemberLeveledUp:
    def test_event_type(self) -> None:
        event = MemberLeveledUp(
            member_id=uuid4(),
            community_id=uuid4(),
            old_level=1,
            new_level=2,
            new_level_name="Practitioner",
        )
        assert event.event_type == "MemberLeveledUp"
        assert event.old_level == 1
        assert event.new_level == 2
