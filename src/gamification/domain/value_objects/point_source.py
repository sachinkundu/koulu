"""PointSource enum — defines engagement actions and their point values."""

from enum import Enum


class PointSource(Enum):
    """Engagement actions that award points."""

    POST_CREATED = ("post_created", 2)
    COMMENT_CREATED = ("comment_created", 1)
    POST_LIKED = ("post_liked", 1)
    COMMENT_LIKED = ("comment_liked", 1)
    LESSON_COMPLETED = ("lesson_completed", 5)

    def __init__(self, source_name: str, points: int) -> None:
        self.source_name = source_name
        self._points = points

    @property
    def points(self) -> int:
        return self._points
