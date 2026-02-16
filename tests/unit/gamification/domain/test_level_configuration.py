"""Tests for LevelConfiguration entity."""

from uuid import uuid4

import pytest

from src.gamification.domain.entities.level_configuration import (
    LevelConfiguration,
    LevelDefinition,
)
from src.gamification.domain.exceptions import InvalidLevelNameError, InvalidThresholdError


def _make_valid_levels() -> list[LevelDefinition]:
    """Create a valid set of 9 level definitions for testing update_levels()."""
    return [
        LevelDefinition(level=1, name="Newbie", threshold=0),
        LevelDefinition(level=2, name="Beginner", threshold=10),
        LevelDefinition(level=3, name="Intermediate", threshold=25),
        LevelDefinition(level=4, name="Advanced", threshold=50),
        LevelDefinition(level=5, name="Expert", threshold=80),
        LevelDefinition(level=6, name="Master", threshold=120),
        LevelDefinition(level=7, name="Grandmaster", threshold=170),
        LevelDefinition(level=8, name="Champion", threshold=230),
        LevelDefinition(level=9, name="Legend", threshold=300),
    ]


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


class TestUpdateLevels:
    """Tests for LevelConfiguration.update_levels()."""

    def test_valid_update_with_all_9_levels(self) -> None:
        config = LevelConfiguration.create_default(community_id=uuid4())
        new_levels = _make_valid_levels()

        config.update_levels(new_levels)

        assert len(config.levels) == 9
        assert config.levels[0].name == "Newbie"
        assert config.levels[0].threshold == 0
        assert config.levels[8].name == "Legend"
        assert config.levels[8].threshold == 300

    def test_name_too_long_rejected(self) -> None:
        config = LevelConfiguration.create_default(community_id=uuid4())
        levels = _make_valid_levels()
        levels[3] = LevelDefinition(level=4, name="A" * 31, threshold=50)

        with pytest.raises(InvalidLevelNameError, match="30 characters"):
            config.update_levels(levels)

    def test_empty_name_rejected(self) -> None:
        config = LevelConfiguration.create_default(community_id=uuid4())
        levels = _make_valid_levels()
        levels[0] = LevelDefinition(level=1, name="", threshold=0)

        with pytest.raises(InvalidLevelNameError, match="required"):
            config.update_levels(levels)

    def test_whitespace_only_name_rejected(self) -> None:
        config = LevelConfiguration.create_default(community_id=uuid4())
        levels = _make_valid_levels()
        levels[0] = LevelDefinition(level=1, name="   ", threshold=0)

        with pytest.raises(InvalidLevelNameError, match="required"):
            config.update_levels(levels)

    def test_duplicate_names_rejected(self) -> None:
        config = LevelConfiguration.create_default(community_id=uuid4())
        levels = _make_valid_levels()
        levels[1] = LevelDefinition(level=2, name="Newbie", threshold=10)

        with pytest.raises(InvalidLevelNameError, match="Duplicate"):
            config.update_levels(levels)

    def test_non_increasing_thresholds_rejected(self) -> None:
        config = LevelConfiguration.create_default(community_id=uuid4())
        levels = _make_valid_levels()
        levels[2] = LevelDefinition(level=3, name="Intermediate", threshold=5)

        with pytest.raises(InvalidThresholdError, match="strictly increasing"):
            config.update_levels(levels)

    def test_equal_thresholds_rejected(self) -> None:
        config = LevelConfiguration.create_default(community_id=uuid4())
        levels = _make_valid_levels()
        levels[2] = LevelDefinition(level=3, name="Intermediate", threshold=10)

        with pytest.raises(InvalidThresholdError, match="strictly increasing"):
            config.update_levels(levels)

    def test_level_1_threshold_not_zero_rejected(self) -> None:
        config = LevelConfiguration.create_default(community_id=uuid4())
        levels = _make_valid_levels()
        levels[0] = LevelDefinition(level=1, name="Newbie", threshold=5)

        with pytest.raises(InvalidThresholdError, match="Level 1 threshold must be 0"):
            config.update_levels(levels)

    def test_wrong_number_of_levels_rejected(self) -> None:
        config = LevelConfiguration.create_default(community_id=uuid4())
        levels = _make_valid_levels()[:5]

        with pytest.raises(InvalidThresholdError, match="Exactly 9 levels required"):
            config.update_levels(levels)

    def test_html_tags_stripped_from_names(self) -> None:
        config = LevelConfiguration.create_default(community_id=uuid4())
        levels = _make_valid_levels()
        levels[0] = LevelDefinition(level=1, name="<b>Newbie</b>", threshold=0)

        config.update_levels(levels)

        assert config.levels[0].name == "Newbie"
        assert "<b>" not in config.levels[0].name

    def test_html_only_name_rejected_after_stripping(self) -> None:
        config = LevelConfiguration.create_default(community_id=uuid4())
        levels = _make_valid_levels()
        levels[0] = LevelDefinition(level=1, name="<b><i></i></b>", threshold=0)

        with pytest.raises(InvalidLevelNameError, match="required"):
            config.update_levels(levels)

    def test_updates_timestamp(self) -> None:
        config = LevelConfiguration.create_default(community_id=uuid4())
        original_updated_at = config.updated_at
        new_levels = _make_valid_levels()

        config.update_levels(new_levels)

        assert config.updated_at >= original_updated_at
