"""Tests for LevelConfiguration entity."""

from uuid import uuid4

from src.gamification.domain.entities.level_configuration import LevelConfiguration


class TestLevelConfigurationDefaults:
    """Tests for default level configuration."""

    def test_create_default_has_9_levels(self) -> None:
        config = LevelConfiguration.create_default(community_id=uuid4())
        assert len(config.levels) == 9

    def test_default_level_1_is_student_at_0(self) -> None:
        config = LevelConfiguration.create_default(community_id=uuid4())
        assert config.levels[0].name == "Student"
        assert config.levels[0].threshold == 0

    def test_default_level_9_is_icon_at_360(self) -> None:
        config = LevelConfiguration.create_default(community_id=uuid4())
        assert config.levels[8].name == "Icon"
        assert config.levels[8].threshold == 360


class TestGetLevelForPoints:
    """Tests for level calculation from points."""

    def test_zero_points_is_level_1(self) -> None:
        config = LevelConfiguration.create_default(community_id=uuid4())
        assert config.get_level_for_points(0) == 1

    def test_exactly_at_threshold_is_that_level(self) -> None:
        config = LevelConfiguration.create_default(community_id=uuid4())
        assert config.get_level_for_points(10) == 2

    def test_one_below_threshold_stays_at_lower_level(self) -> None:
        config = LevelConfiguration.create_default(community_id=uuid4())
        assert config.get_level_for_points(9) == 1

    def test_high_points_is_level_9(self) -> None:
        config = LevelConfiguration.create_default(community_id=uuid4())
        assert config.get_level_for_points(500) == 9

    def test_mid_range_points(self) -> None:
        config = LevelConfiguration.create_default(community_id=uuid4())
        assert config.get_level_for_points(45) == 3  # threshold for 3 is 30, for 4 is 60


class TestThresholdForLevel:
    """Tests for getting threshold of a specific level."""

    def test_threshold_for_level_1_is_0(self) -> None:
        config = LevelConfiguration.create_default(community_id=uuid4())
        assert config.threshold_for_level(1) == 0

    def test_threshold_for_level_2_is_10(self) -> None:
        config = LevelConfiguration.create_default(community_id=uuid4())
        assert config.threshold_for_level(2) == 10

    def test_threshold_for_level_9_is_360(self) -> None:
        config = LevelConfiguration.create_default(community_id=uuid4())
        assert config.threshold_for_level(9) == 360


class TestPointsToNextLevel:
    """Tests for points-to-next-level calculation."""

    def test_level_1_with_0_points(self) -> None:
        config = LevelConfiguration.create_default(community_id=uuid4())
        assert config.points_to_next_level(current_level=1, total_points=0) == 10

    def test_level_2_with_15_points(self) -> None:
        config = LevelConfiguration.create_default(community_id=uuid4())
        assert config.points_to_next_level(current_level=2, total_points=15) == 15

    def test_level_9_returns_none(self) -> None:
        config = LevelConfiguration.create_default(community_id=uuid4())
        assert config.points_to_next_level(current_level=9, total_points=400) is None
