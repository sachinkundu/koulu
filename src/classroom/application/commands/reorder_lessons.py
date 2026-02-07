"""Reorder lessons command."""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class ReorderLessonsCommand:
    """Command to reorder lessons in a module."""

    module_id: UUID
    lesson_ids: list[UUID]
