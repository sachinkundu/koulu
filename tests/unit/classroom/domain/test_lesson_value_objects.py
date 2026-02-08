"""Unit tests for Lesson value objects."""

import pytest

from src.classroom.domain.exceptions import (
    InvalidContentTypeError,
    InvalidVideoUrlError,
    LessonTitleRequiredError,
    LessonTitleTooLongError,
    LessonTitleTooShortError,
    TextContentRequiredError,
    TextContentTooLongError,
    VideoUrlRequiredError,
)
from src.classroom.domain.value_objects import ContentType, LessonTitle, TextContent, VideoUrl


class TestLessonTitle:
    """Tests for LessonTitle value object."""

    def test_valid_title(self) -> None:
        title = LessonTitle("What is Python?")
        assert title.value == "What is Python?"

    def test_min_length_title(self) -> None:
        title = LessonTitle("AB")
        assert title.value == "AB"

    def test_max_length_title(self) -> None:
        title = LessonTitle("x" * 200)
        assert len(title.value) == 200

    def test_strips_html(self) -> None:
        title = LessonTitle("<em>Intro</em>")
        assert title.value == "Intro"

    def test_empty_raises_required(self) -> None:
        with pytest.raises(LessonTitleRequiredError):
            LessonTitle("")

    def test_too_short_raises(self) -> None:
        with pytest.raises(LessonTitleTooShortError):
            LessonTitle("A")

    def test_too_long_raises(self) -> None:
        with pytest.raises(LessonTitleTooLongError):
            LessonTitle("x" * 201)


class TestContentType:
    """Tests for ContentType enum."""

    def test_text_type(self) -> None:
        ct = ContentType.from_string("text")
        assert ct == ContentType.TEXT

    def test_video_type(self) -> None:
        ct = ContentType.from_string("video")
        assert ct == ContentType.VIDEO

    def test_case_insensitive(self) -> None:
        ct = ContentType.from_string("TEXT")
        assert ct == ContentType.TEXT

    def test_invalid_raises(self) -> None:
        with pytest.raises(InvalidContentTypeError):
            ContentType.from_string("pdf")

    def test_empty_raises(self) -> None:
        with pytest.raises(InvalidContentTypeError):
            ContentType.from_string("")

    def test_value_access(self) -> None:
        assert ContentType.TEXT.value == "text"
        assert ContentType.VIDEO.value == "video"


class TestTextContent:
    """Tests for TextContent value object."""

    def test_valid_content(self) -> None:
        tc = TextContent("Python is a great language.")
        assert tc.value == "Python is a great language."

    def test_allows_safe_html(self) -> None:
        tc = TextContent("<p>Hello <strong>World</strong></p>")
        assert "<p>" in tc.value
        assert "<strong>" in tc.value

    def test_strips_script_tags(self) -> None:
        tc = TextContent("<script>alert('xss')</script>Hello")
        assert "script" not in tc.value
        assert "Hello" in tc.value

    def test_max_length(self) -> None:
        tc = TextContent("x" * 50000)
        assert len(tc.value) == 50000

    def test_empty_raises(self) -> None:
        with pytest.raises(TextContentRequiredError):
            TextContent("")

    def test_too_long_raises(self) -> None:
        with pytest.raises(TextContentTooLongError):
            TextContent("x" * 50001)

    def test_whitespace_only_raises(self) -> None:
        with pytest.raises(TextContentRequiredError):
            TextContent("   ")


class TestVideoUrl:
    """Tests for VideoUrl value object."""

    def test_youtube_standard(self) -> None:
        url = VideoUrl("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        assert url.value == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    def test_youtube_short(self) -> None:
        url = VideoUrl("https://youtu.be/dQw4w9WgXcQ")
        assert "youtu.be" in url.value

    def test_youtube_embed(self) -> None:
        url = VideoUrl("https://www.youtube.com/embed/dQw4w9WgXcQ")
        assert "embed" in url.value

    def test_vimeo(self) -> None:
        url = VideoUrl("https://vimeo.com/123456789")
        assert "vimeo.com" in url.value

    def test_vimeo_player(self) -> None:
        url = VideoUrl("https://player.vimeo.com/video/123456789")
        assert "player.vimeo.com" in url.value

    def test_loom(self) -> None:
        url = VideoUrl("https://www.loom.com/share/abc123def456")
        assert "loom.com" in url.value

    def test_loom_embed(self) -> None:
        url = VideoUrl("https://www.loom.com/embed/abc123def456")
        assert "loom.com" in url.value

    def test_empty_raises(self) -> None:
        with pytest.raises(VideoUrlRequiredError):
            VideoUrl("")

    def test_invalid_url_raises(self) -> None:
        with pytest.raises(InvalidVideoUrlError):
            VideoUrl("not-a-url")

    def test_unsupported_platform_raises(self) -> None:
        with pytest.raises(InvalidVideoUrlError):
            VideoUrl("https://www.dailymotion.com/video/x1")

    def test_javascript_protocol_raises(self) -> None:
        with pytest.raises(InvalidVideoUrlError):
            VideoUrl("javascript:alert('xss')")

    def test_strips_whitespace(self) -> None:
        url = VideoUrl("  https://www.youtube.com/watch?v=dQw4w9WgXcQ  ")
        assert url.value == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    def test_http_youtube(self) -> None:
        url = VideoUrl("http://www.youtube.com/watch?v=dQw4w9WgXcQ")
        assert url.value == "http://www.youtube.com/watch?v=dQw4w9WgXcQ"
