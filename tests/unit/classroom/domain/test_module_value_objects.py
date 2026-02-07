"""Unit tests for Module value objects."""

import pytest

from src.classroom.domain.exceptions import (
    ModuleDescriptionTooLongError,
    ModuleTitleRequiredError,
    ModuleTitleTooLongError,
    ModuleTitleTooShortError,
)
from src.classroom.domain.value_objects import ModuleDescription, ModuleTitle


class TestModuleTitle:
    """Tests for ModuleTitle value object."""

    def test_valid_title(self) -> None:
        title = ModuleTitle("Getting Started")
        assert title.value == "Getting Started"

    def test_min_length_title(self) -> None:
        title = ModuleTitle("AB")
        assert title.value == "AB"

    def test_max_length_title(self) -> None:
        title = ModuleTitle("x" * 200)
        assert len(title.value) == 200

    def test_strips_html(self) -> None:
        title = ModuleTitle("<b>Bold Title</b>")
        assert title.value == "Bold Title"

    def test_strips_whitespace(self) -> None:
        title = ModuleTitle("  Some Title  ")
        assert title.value == "Some Title"

    def test_empty_raises_required(self) -> None:
        with pytest.raises(ModuleTitleRequiredError):
            ModuleTitle("")

    def test_whitespace_only_raises_required(self) -> None:
        with pytest.raises(ModuleTitleRequiredError):
            ModuleTitle("   ")

    def test_html_only_raises_required(self) -> None:
        with pytest.raises(ModuleTitleRequiredError):
            ModuleTitle("<br><br>")

    def test_too_short_raises(self) -> None:
        with pytest.raises(ModuleTitleTooShortError):
            ModuleTitle("A")

    def test_too_long_raises(self) -> None:
        with pytest.raises(ModuleTitleTooLongError):
            ModuleTitle("x" * 201)

    def test_equality(self) -> None:
        assert ModuleTitle("Test") == ModuleTitle("Test")

    def test_inequality(self) -> None:
        assert ModuleTitle("Test A") != ModuleTitle("Test B")


class TestModuleDescription:
    """Tests for ModuleDescription value object."""

    def test_valid_description(self) -> None:
        desc = ModuleDescription("Learn the basics of Python")
        assert desc.value == "Learn the basics of Python"

    def test_empty_string_allowed(self) -> None:
        desc = ModuleDescription("")
        assert desc.value == ""

    def test_max_length(self) -> None:
        desc = ModuleDescription("x" * 1000)
        assert len(desc.value) == 1000

    def test_too_long_raises(self) -> None:
        with pytest.raises(ModuleDescriptionTooLongError):
            ModuleDescription("x" * 1001)

    def test_strips_html(self) -> None:
        desc = ModuleDescription("<script>alert('x')</script>Hello")
        assert desc.value == "alert('x')Hello"

    def test_equality(self) -> None:
        assert ModuleDescription("Test") == ModuleDescription("Test")
