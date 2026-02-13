"""Unmark lesson command."""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class UnmarkLessonCommand:
    """Command to un-mark a lesson as complete."""

    user_id: UUID
    lesson_id: UUID
