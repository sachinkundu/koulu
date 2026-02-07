"""Unit tests for CommentContent value object."""

import pytest

from src.community.domain.exceptions import (
    CommentContentRequiredError,
    CommentContentTooLongError,
)
from src.community.domain.value_objects import CommentContent


class TestCommentContentValidation:
    """Tests for CommentContent validation."""

    def test_valid_content(self) -> None:
        """CommentContent should accept valid content."""
        content = CommentContent("This is a valid comment.")
        assert str(content) == "This is a valid comment."

    def test_empty_content_raises_error(self) -> None:
        """CommentContent should reject empty content."""
        with pytest.raises(CommentContentRequiredError):
            CommentContent("")

    def test_whitespace_only_content_raises_error(self) -> None:
        """CommentContent should reject whitespace-only content."""
        with pytest.raises(CommentContentRequiredError):
            CommentContent("   ")

    def test_content_too_long_raises_error(self) -> None:
        """CommentContent should reject content exceeding 2000 characters."""
        long_content = "a" * 2001
        with pytest.raises(CommentContentTooLongError):
            CommentContent(long_content)

    def test_content_at_max_length_is_valid(self) -> None:
        """CommentContent should accept content at exactly 2000 characters."""
        content = CommentContent("a" * 2000)
        assert len(str(content)) == 2000

    def test_html_tags_are_stripped(self) -> None:
        """CommentContent should strip HTML tags."""
        content = CommentContent("<b>Bold</b> and <i>italic</i>")
        assert str(content) == "Bold and italic"

    def test_script_tags_are_stripped(self) -> None:
        """CommentContent should strip script tags (XSS prevention)."""
        content = CommentContent("<script>alert('xss')</script>Hello")
        assert "script" not in str(content)
        assert "Hello" in str(content)

    def test_deleted_placeholder_is_valid(self) -> None:
        """CommentContent should accept '[deleted]' as valid content."""
        content = CommentContent("[deleted]")
        assert str(content) == "[deleted]"


class TestCommentContentEquality:
    """Tests for CommentContent equality."""

    def test_same_content_is_equal(self) -> None:
        """CommentContent with same value should be equal."""
        c1 = CommentContent("Hello")
        c2 = CommentContent("Hello")
        assert c1 == c2

    def test_different_content_is_not_equal(self) -> None:
        """CommentContent with different values should not be equal."""
        c1 = CommentContent("Hello")
        c2 = CommentContent("World")
        assert c1 != c2
