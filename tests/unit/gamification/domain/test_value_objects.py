"""Tests for gamification value objects."""

import pytest

from src.gamification.domain.exceptions import (
    GamificationDomainError,
    InvalidLevelNameError,
    InvalidLevelNumberError,
)
from src.gamification.domain.value_objects.level_name import LevelName
from src.gamification.domain.value_objects.level_number import LevelNumber
from src.gamification.domain.value_objects.point_source import PointSource


class TestPointSource:
    """Tests for PointSource enum."""

    def test_post_created_awards_2_points(self) -> None:
        assert PointSource.POST_CREATED.points == 2

    def test_comment_created_awards_1_point(self) -> None:
        assert PointSource.COMMENT_CREATED.points == 1

    def test_post_liked_awards_1_point(self) -> None:
        assert PointSource.POST_LIKED.points == 1

    def test_comment_liked_awards_1_point(self) -> None:
        assert PointSource.COMMENT_LIKED.points == 1

    def test_lesson_completed_awards_5_points(self) -> None:
        assert PointSource.LESSON_COMPLETED.points == 5


class TestLevelNumber:
    """Tests for LevelNumber value object."""

    def test_valid_level_1(self) -> None:
        level = LevelNumber(1)
        assert level.value == 1

    def test_valid_level_9(self) -> None:
        level = LevelNumber(9)
        assert level.value == 9

    def test_level_0_raises(self) -> None:
        with pytest.raises(InvalidLevelNumberError):
            LevelNumber(0)

    def test_level_10_raises(self) -> None:
        with pytest.raises(InvalidLevelNumberError):
            LevelNumber(10)

    def test_negative_level_raises(self) -> None:
        with pytest.raises(InvalidLevelNumberError):
            LevelNumber(-1)


class TestLevelName:
    """Tests for LevelName value object."""

    def test_valid_name(self) -> None:
        name = LevelName("Student")
        assert name.value == "Student"

    def test_empty_name_raises(self) -> None:
        with pytest.raises(InvalidLevelNameError, match="required"):
            LevelName("")

    def test_name_too_long_raises(self) -> None:
        with pytest.raises(InvalidLevelNameError, match="30 characters"):
            LevelName("A" * 31)

    def test_html_stripped(self) -> None:
        name = LevelName("<script>alert('xss')</script>Beginner")
        assert "<script>" not in name.value
        assert "Beginner" in name.value

    def test_whitespace_only_raises(self) -> None:
        with pytest.raises(InvalidLevelNameError, match="required"):
            LevelName("   ")
