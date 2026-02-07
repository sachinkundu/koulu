"""Unit tests for Classroom value objects."""

import pytest

from src.classroom.domain.exceptions import (
    CourseDescriptionTooLongError,
    CourseTitleRequiredError,
    CourseTitleTooLongError,
    CourseTitleTooShortError,
    InvalidCoverImageUrlError,
)
from src.classroom.domain.value_objects import (
    CourseDescription,
    CourseId,
    CourseTitle,
    CoverImageUrl,
    EstimatedDuration,
)


class TestCourseTitle:
    """Tests for CourseTitle value object."""

    def test_valid_title(self) -> None:
        """Valid title is accepted."""
        title = CourseTitle("Introduction to Python")
        assert title.value == "Introduction to Python"

    def test_min_length_title(self) -> None:
        """Title at minimum length (2) is accepted."""
        title = CourseTitle("AB")
        assert title.value == "AB"

    def test_max_length_title(self) -> None:
        """Title at maximum length (200) is accepted."""
        title = CourseTitle("x" * 200)
        assert len(title.value) == 200

    def test_empty_title_raises(self) -> None:
        """Empty title raises CourseTitleRequiredError."""
        with pytest.raises(CourseTitleRequiredError):
            CourseTitle("")

    def test_whitespace_only_title_raises(self) -> None:
        """Whitespace-only title raises CourseTitleRequiredError."""
        with pytest.raises(CourseTitleRequiredError):
            CourseTitle("   ")

    def test_too_short_title_raises(self) -> None:
        """Single character title raises CourseTitleTooShortError."""
        with pytest.raises(CourseTitleTooShortError):
            CourseTitle("A")

    def test_too_long_title_raises(self) -> None:
        """Title over 200 chars raises CourseTitleTooLongError."""
        with pytest.raises(CourseTitleTooLongError):
            CourseTitle("x" * 201)

    def test_html_stripped(self) -> None:
        """HTML tags are stripped from title."""
        title = CourseTitle("<b>Bold Title</b>")
        assert title.value == "Bold Title"

    def test_str_representation(self) -> None:
        """__str__ returns the value."""
        title = CourseTitle("Test")
        assert str(title) == "Test"

    def test_whitespace_normalized(self) -> None:
        """Leading/trailing whitespace is stripped."""
        title = CourseTitle("  Title  ")
        assert title.value == "Title"


class TestCourseDescription:
    """Tests for CourseDescription value object."""

    def test_valid_description(self) -> None:
        """Valid description is accepted."""
        desc = CourseDescription("Learn Python basics")
        assert desc.value == "Learn Python basics"

    def test_empty_description_is_valid(self) -> None:
        """Empty description is accepted (optional field)."""
        desc = CourseDescription("")
        assert desc.value == ""

    def test_max_length_description(self) -> None:
        """Description at maximum length (2000) is accepted."""
        desc = CourseDescription("x" * 2000)
        assert len(desc.value) == 2000

    def test_too_long_description_raises(self) -> None:
        """Description over 2000 chars raises error."""
        with pytest.raises(CourseDescriptionTooLongError):
            CourseDescription("x" * 2001)

    def test_html_stripped(self) -> None:
        """HTML tags are stripped."""
        desc = CourseDescription("<script>alert('xss')</script>Hello")
        assert "script" not in desc.value
        assert "Hello" in desc.value

    def test_str_representation(self) -> None:
        """__str__ returns the value."""
        desc = CourseDescription("Test desc")
        assert str(desc) == "Test desc"


class TestCoverImageUrl:
    """Tests for CoverImageUrl value object."""

    def test_valid_https_url(self) -> None:
        """Valid HTTPS URL is accepted."""
        url = CoverImageUrl("https://example.com/image.jpg")
        assert url.value == "https://example.com/image.jpg"

    def test_http_url_rejected(self) -> None:
        """HTTP URL raises InvalidCoverImageUrlError."""
        with pytest.raises(InvalidCoverImageUrlError):
            CoverImageUrl("http://example.com/image.jpg")

    def test_invalid_url_rejected(self) -> None:
        """Invalid URL raises error."""
        with pytest.raises(InvalidCoverImageUrlError):
            CoverImageUrl("not-a-url")

    def test_empty_url_rejected(self) -> None:
        """Empty URL raises error."""
        with pytest.raises(InvalidCoverImageUrlError):
            CoverImageUrl("")

    def test_whitespace_stripped(self) -> None:
        """Whitespace is stripped from URL."""
        url = CoverImageUrl("  https://example.com/img.jpg  ")
        assert url.value == "https://example.com/img.jpg"

    def test_str_representation(self) -> None:
        """__str__ returns the value."""
        url = CoverImageUrl("https://example.com/img.jpg")
        assert str(url) == "https://example.com/img.jpg"


class TestEstimatedDuration:
    """Tests for EstimatedDuration value object."""

    def test_valid_duration(self) -> None:
        """Valid duration string is accepted."""
        dur = EstimatedDuration("8 hours")
        assert dur.value == "8 hours"

    def test_whitespace_stripped(self) -> None:
        """Whitespace is stripped."""
        dur = EstimatedDuration("  2 weeks  ")
        assert dur.value == "2 weeks"

    def test_str_representation(self) -> None:
        """__str__ returns the value."""
        dur = EstimatedDuration("3 days")
        assert str(dur) == "3 days"


class TestCourseId:
    """Tests for CourseId value object."""

    def test_str_representation(self) -> None:
        """__str__ returns string representation of UUID."""
        from uuid import uuid4

        uid = uuid4()
        course_id = CourseId(value=uid)
        assert str(course_id) == str(uid)
