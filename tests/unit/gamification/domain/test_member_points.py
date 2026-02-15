"""Tests for MemberPoints aggregate root."""

from uuid import uuid4

import pytest

from src.gamification.domain.entities.level_configuration import LevelConfiguration
from src.gamification.domain.entities.member_points import MemberPoints
from src.gamification.domain.events.gamification_events import (
    MemberLeveledUp,
    PointsAwarded,
    PointsDeducted,
)
from src.gamification.domain.exceptions import DuplicateLessonCompletionError
from src.gamification.domain.value_objects.point_source import PointSource


class TestMemberPointsCreation:
    def test_create_starts_at_level_1_with_0_points(self) -> None:
        mp = MemberPoints.create(community_id=uuid4(), user_id=uuid4())
        assert mp.total_points == 0
        assert mp.current_level == 1

    def test_create_has_no_transactions(self) -> None:
        mp = MemberPoints.create(community_id=uuid4(), user_id=uuid4())
        assert len(mp.transactions) == 0


class TestAwardPoints:
    def test_award_increases_total(self) -> None:
        config = LevelConfiguration.create_default(community_id=uuid4())
        mp = MemberPoints.create(community_id=config.community_id, user_id=uuid4())
        mp.award_points(
            source=PointSource.POST_CREATED,
            source_id=uuid4(),
            level_config=config,
        )
        assert mp.total_points == 2

    def test_award_creates_transaction(self) -> None:
        config = LevelConfiguration.create_default(community_id=uuid4())
        mp = MemberPoints.create(community_id=config.community_id, user_id=uuid4())
        mp.award_points(
            source=PointSource.POST_LIKED,
            source_id=uuid4(),
            level_config=config,
        )
        assert len(mp.transactions) == 1
        assert mp.transactions[0].points == 1

    def test_award_publishes_points_awarded_event(self) -> None:
        config = LevelConfiguration.create_default(community_id=uuid4())
        mp = MemberPoints.create(community_id=config.community_id, user_id=uuid4())
        mp.award_points(
            source=PointSource.POST_CREATED,
            source_id=uuid4(),
            level_config=config,
        )
        events = [e for e in mp.events if isinstance(e, PointsAwarded)]
        assert len(events) == 1
        assert events[0].points == 2
        assert events[0].new_total == 2


class TestLevelUp:
    def test_level_up_when_threshold_reached(self) -> None:
        config = LevelConfiguration.create_default(community_id=uuid4())
        mp = MemberPoints.create(community_id=config.community_id, user_id=uuid4())
        # Award enough to reach level 2 (threshold=10): 2 lessons = 10 points
        for _ in range(2):
            mp.award_points(
                source=PointSource.LESSON_COMPLETED,
                source_id=uuid4(),
                level_config=config,
            )
        assert mp.current_level == 2
        assert mp.total_points == 10

    def test_level_up_publishes_event(self) -> None:
        config = LevelConfiguration.create_default(community_id=uuid4())
        mp = MemberPoints.create(community_id=config.community_id, user_id=uuid4())
        for _ in range(2):
            mp.award_points(
                source=PointSource.LESSON_COMPLETED,
                source_id=uuid4(),
                level_config=config,
            )
        level_events = [e for e in mp.events if isinstance(e, MemberLeveledUp)]
        assert len(level_events) == 1
        assert level_events[0].old_level == 1
        assert level_events[0].new_level == 2

    def test_can_skip_levels(self) -> None:
        config = LevelConfiguration.create_default(community_id=uuid4())
        mp = MemberPoints.create(community_id=config.community_id, user_id=uuid4())
        # Award 10 points (5 posts x 2)
        for _ in range(5):
            mp.award_points(
                source=PointSource.POST_CREATED,
                source_id=uuid4(),
                level_config=config,
            )
        # Award 20 more points (4 lessons x 5)
        for _ in range(4):
            mp.award_points(
                source=PointSource.LESSON_COMPLETED,
                source_id=uuid4(),
                level_config=config,
            )
        # 10 + 20 = 30 points = level 3
        assert mp.total_points == 30
        assert mp.current_level == 3


class TestDeductPoints:
    def test_deduct_decreases_total(self) -> None:
        config = LevelConfiguration.create_default(community_id=uuid4())
        mp = MemberPoints.create(community_id=config.community_id, user_id=uuid4())
        mp.award_points(source=PointSource.POST_CREATED, source_id=uuid4(), level_config=config)
        mp.deduct_points(source=PointSource.POST_LIKED, source_id=uuid4(), level_config=config)
        assert mp.total_points == 1  # 2 - 1

    def test_deduct_cannot_go_below_zero(self) -> None:
        config = LevelConfiguration.create_default(community_id=uuid4())
        mp = MemberPoints.create(community_id=config.community_id, user_id=uuid4())
        mp.deduct_points(source=PointSource.POST_LIKED, source_id=uuid4(), level_config=config)
        assert mp.total_points == 0

    def test_deduct_publishes_points_deducted_event(self) -> None:
        config = LevelConfiguration.create_default(community_id=uuid4())
        mp = MemberPoints.create(community_id=config.community_id, user_id=uuid4())
        mp.award_points(source=PointSource.POST_CREATED, source_id=uuid4(), level_config=config)
        mp.clear_events()  # Clear award event
        mp.deduct_points(source=PointSource.POST_LIKED, source_id=uuid4(), level_config=config)
        events = [e for e in mp.events if isinstance(e, PointsDeducted)]
        assert len(events) == 1


class TestRatchetBehavior:
    def test_level_does_not_decrease_on_deduction(self) -> None:
        config = LevelConfiguration.create_default(community_id=uuid4())
        mp = MemberPoints.create(community_id=config.community_id, user_id=uuid4())
        # Reach level 2 (10 points)
        for _ in range(2):
            mp.award_points(
                source=PointSource.LESSON_COMPLETED,
                source_id=uuid4(),
                level_config=config,
            )
        assert mp.current_level == 2
        # Deduct a point
        mp.deduct_points(source=PointSource.POST_LIKED, source_id=uuid4(), level_config=config)
        assert mp.total_points == 9
        assert mp.current_level == 2  # Ratchet: stays at 2


class TestLessonDeduplication:
    def test_duplicate_lesson_raises(self) -> None:
        config = LevelConfiguration.create_default(community_id=uuid4())
        mp = MemberPoints.create(community_id=config.community_id, user_id=uuid4())
        lesson_id = uuid4()
        mp.award_points(
            source=PointSource.LESSON_COMPLETED,
            source_id=lesson_id,
            level_config=config,
        )
        with pytest.raises(DuplicateLessonCompletionError):
            mp.award_points(
                source=PointSource.LESSON_COMPLETED,
                source_id=lesson_id,
                level_config=config,
            )
        assert mp.total_points == 5  # Only first completion counted
