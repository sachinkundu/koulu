"""Unit tests for Community domain value objects."""

import pytest

from src.community.domain.exceptions import (
    PostContentRequiredError,
    PostContentTooLongError,
    PostTitleRequiredError,
    PostTitleTooLongError,
)
from src.community.domain.value_objects import PostContent, PostTitle


class TestPostTitle:
    """Tests for PostTitle value object."""

    def test_valid_title_creates_instance(self) -> None:
        """Valid title (1-200 chars) should create a PostTitle instance."""
        title = PostTitle("My First Post")
        assert title.value == "My First Post"

    def test_title_is_trimmed(self) -> None:
        """Title should have whitespace trimmed."""
        title = PostTitle("  My Post  ")
        assert title.value == "My Post"

    def test_empty_title_raises_error(self) -> None:
        """Empty title should raise PostTitleRequiredError."""
        with pytest.raises(PostTitleRequiredError):
            PostTitle("")

    def test_whitespace_only_title_raises_error(self) -> None:
        """Whitespace-only title should raise PostTitleRequiredError."""
        with pytest.raises(PostTitleRequiredError):
            PostTitle("   ")

    def test_title_too_long_raises_error(self) -> None:
        """Title over 200 chars should raise PostTitleTooLongError."""
        long_title = "a" * 201
        with pytest.raises(PostTitleTooLongError) as exc_info:
            PostTitle(long_title)
        assert exc_info.value.args[0] == "Title must be 200 characters or less"

    def test_title_at_max_length_is_valid(self) -> None:
        """Title at exactly 200 chars should be valid."""
        title = PostTitle("a" * 200)
        assert len(title.value) == 200

    def test_title_at_min_length_is_valid(self) -> None:
        """Title at exactly 1 char should be valid."""
        title = PostTitle("a")
        assert title.value == "a"

    def test_title_with_html_tags_strips_tags(self) -> None:
        """Title with HTML tags should strip tags for security."""
        title = PostTitle("<script>alert('xss')</script>Hello")
        assert title.value == "alert('xss')Hello"
        assert "<script>" not in title.value
        assert "</script>" not in title.value

    def test_title_with_nested_html_strips_tags(self) -> None:
        """Title with nested HTML tags should strip all tags."""
        title = PostTitle("Welcome to <b>my <i>post</i></b>!")
        assert title.value == "Welcome to my post!"
        assert "<b>" not in title.value
        assert "<i>" not in title.value

    def test_title_with_only_html_tags_raises_error(self) -> None:
        """Title with only HTML tags (no content) should raise error."""
        with pytest.raises(PostTitleRequiredError):
            PostTitle("<b></b>")

    def test_str_returns_value(self) -> None:
        """str() should return the title value."""
        title = PostTitle("My Post")
        assert str(title) == "My Post"

    def test_title_is_immutable(self) -> None:
        """PostTitle should be a frozen dataclass (immutable)."""
        title = PostTitle("My Post")
        with pytest.raises(Exception):  # FrozenInstanceError
            title.value = "Modified"  # type: ignore


class TestPostContent:
    """Tests for PostContent value object."""

    def test_valid_content_creates_instance(self) -> None:
        """Valid content (1-5000 chars) should create a PostContent instance."""
        content = PostContent("This is my post content with details.")
        assert content.value == "This is my post content with details."

    def test_content_is_trimmed(self) -> None:
        """Content should have whitespace trimmed."""
        content = PostContent("  My content  ")
        assert content.value == "My content"

    def test_empty_content_raises_error(self) -> None:
        """Empty content should raise PostContentRequiredError."""
        with pytest.raises(PostContentRequiredError):
            PostContent("")

    def test_whitespace_only_content_raises_error(self) -> None:
        """Whitespace-only content should raise PostContentRequiredError."""
        with pytest.raises(PostContentRequiredError):
            PostContent("   ")

    def test_content_too_long_raises_error(self) -> None:
        """Content over 5000 chars should raise PostContentTooLongError."""
        long_content = "a" * 5001
        with pytest.raises(PostContentTooLongError) as exc_info:
            PostContent(long_content)
        assert exc_info.value.args[0] == "Content must be 5000 characters or less"

    def test_content_at_max_length_is_valid(self) -> None:
        """Content at exactly 5000 chars should be valid."""
        content = PostContent("a" * 5000)
        assert len(content.value) == 5000

    def test_content_at_min_length_is_valid(self) -> None:
        """Content at exactly 1 char should be valid."""
        content = PostContent("a")
        assert content.value == "a"

    def test_content_with_html_tags_strips_tags(self) -> None:
        """Content with HTML tags should strip tags for security."""
        content = PostContent("<script>alert('xss')</script>Hello world")
        assert content.value == "alert('xss')Hello world"
        assert "<script>" not in content.value
        assert "</script>" not in content.value

    def test_content_with_nested_html_strips_tags(self) -> None:
        """Content with nested HTML tags should strip all tags."""
        content = PostContent("This is <b>important <i>information</i></b> for you.")
        assert content.value == "This is important information for you."
        assert "<b>" not in content.value
        assert "<i>" not in content.value

    def test_content_with_only_html_tags_raises_error(self) -> None:
        """Content with only HTML tags (no content) should raise error."""
        with pytest.raises(PostContentRequiredError):
            PostContent("<p></p>")

    def test_str_returns_value(self) -> None:
        """str() should return the content value."""
        content = PostContent("My content")
        assert str(content) == "My content"

    def test_content_is_immutable(self) -> None:
        """PostContent should be a frozen dataclass (immutable)."""
        content = PostContent("My content")
        with pytest.raises(Exception):  # FrozenInstanceError
            content.value = "Modified"  # type: ignore

    def test_content_with_newlines_is_valid(self) -> None:
        """Content with newlines should be preserved."""
        content = PostContent("Line 1\nLine 2\nLine 3")
        assert "Line 1" in content.value
        assert "Line 2" in content.value
        assert "\n" in content.value

    def test_content_with_special_characters_is_valid(self) -> None:
        """Content with special characters should be valid."""
        content = PostContent("Hello! How are you? #coding @user 🚀")
        assert "Hello!" in content.value
        assert "#coding" in content.value
