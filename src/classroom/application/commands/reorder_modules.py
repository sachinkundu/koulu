"""Reorder modules command."""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class ReorderModulesCommand:
    """Command to reorder modules in a course."""

    course_id: UUID
    module_ids: list[UUID]
